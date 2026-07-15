```py
namespace azure.ai.agentserver.responses

    def azure.ai.agentserver.responses.get_conversation_id(request: CreateResponse | ResponseObject) -> Optional[str]: ...


    def azure.ai.agentserver.responses.get_input_expanded(request: CreateResponse) -> list[Item]: ...


    def azure.ai.agentserver.responses.to_output_item(item: Item, response_id: str | None = None) -> OutputItem | None: ...


    class azure.ai.agentserver.responses.CreateResponse(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "background": Optional[bool]
        key "context_management": Optional[list[ContextManagementParam]]
        key "conversation": Optional[ConversationParam]
        key "include": Optional[list[Literal["results", "results", "sources", "image_url", "image_url", "outputs", "encrypted_content", "logprobs", "results"]]]
        key "input": ForwardRef('InputParam', module='types')
        key "instructions": Optional[str]
        key "internal_metadata": ForwardRef('CreateResponseInternalMetadata', module='types')
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[ModerationParam]
        key "parallel_tool_calls": Optional[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "rai_config": str
        key "reasoning": Optional[Reasoning]
        key "resolved_agent_version": ForwardRef('AgentVersionObject', module='types')
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "store": Optional[bool]
        key "stream": Optional[bool]
        key "stream_options": Optional[ResponseStreamOptions]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "user": str
        agent_reference: AgentReference
        background: bool
        context_management: list[ContextManagementParam]
        conversation: ConversationParam
        include: list[IncludeEnum]
        input: InputParam
        instructions: str
        internal_metadata: CreateResponseInternalMetadata
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: ModerationParam
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        rai_config: str
        reasoning: Reasoning
        resolved_agent_version: AgentVersionObject
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        store: bool
        stream: bool
        stream_options: ResponseStreamOptions
        structured_inputs: dict[str, Any]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        user: str


    class azure.ai.agentserver.responses.FoundryApiError(FoundryStorageError):

        def __init__(
                self,
                message: str,
                *,
                response_body: dict[str, Any] | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.FoundryBadRequestError(FoundryStorageError):

        def __init__(
                self,
                message: str,
                *,
                response_body: dict[str, Any] | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.FoundryResourceNotFoundError(FoundryStorageError):

        def __init__(
                self,
                message: str,
                *,
                response_body: dict[str, Any] | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.FoundryStorageError(Exception):

        def __init__(
                self,
                message: str,
                *,
                response_body: dict[str, Any] | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.FoundryStorageProvider: implements AsyncContextManager

        def __init__(
                self,
                credential: AsyncTokenCredential,
                settings: FoundryStorageSettings | None = None,
                get_server_version: Callable[[], str] | None = None
            ) -> None: ...

        async def aclose(self) -> None: ...

        async def create_response(
                self,
                response: ResponseObject,
                input_items: Iterable[OutputItem] | None,
                history_item_ids: Iterable[str] | None,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def delete_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def get_history_item_ids(
                self,
                previous_response_id: str | None,
                conversation_id: str | None,
                limit: int,
                *,
                context: PlatformContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self,
                response_id: str,
                limit: int = 20,
                ascending: bool = False,
                after: str | None = None,
                before: str | None = None,
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self,
                item_ids: Iterable[str],
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> ResponseObject: ...

        async def update_response(
                self,
                response: ResponseObject,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.FoundryStorageSettings:

        def __init__(
                self,
                *,
                storage_base_url: str
            ) -> None: ...

        @classmethod
        def from_endpoint(cls, endpoint: str) -> FoundryStorageSettings: ...

        @classmethod
        def from_env(cls) -> FoundryStorageSettings: ...

        def build_url(
                self,
                path: str,
                **extra_params: str
            ) -> str: ...


    class azure.ai.agentserver.responses.InMemoryResponseProvider(ResponseProviderProtocol, ResponseStreamProviderProtocol):

        def __init__(self) -> None: ...

        async def append_stream_event(
                self,
                response_id: str,
                event: StreamEventRecord,
                *,
                ttl_seconds: int | None = ...
            ) -> bool: ...

        async def create_execution(
                self,
                execution: ResponseExecution,
                *,
                ttl_seconds: int | None = ...
            ) -> None: ...

        async def create_response(
                self,
                response: ResponseObject,
                input_items: Iterable[OutputItem] | None,
                history_item_ids: Iterable[str] | None,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def delete(self, response_id: str) -> bool: ...

        async def delete_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def delete_stream_events(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def get_execution(self, response_id: str) -> ResponseExecution | None: ...

        async def get_history_item_ids(
                self,
                previous_response_id: str | None,
                conversation_id: str | None,
                limit: int,
                *,
                context: PlatformContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self,
                response_id: str,
                limit: int = 20,
                ascending: bool = False,
                after: str | None = None,
                before: str | None = None,
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self,
                item_ids: Iterable[str],
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_replay_events(self, response_id: str) -> list[StreamEventRecord] | None: ...

        async def get_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> ResponseObject: ...

        async def get_stream_events(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> list[ResponseStreamEvent] | None: ...

        async def purge_expired(
                self,
                *,
                now: datetime | None = ...
            ) -> int: ...

        async def save_stream_events(
                self,
                response_id: str,
                events: list[ResponseStreamEvent],
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def set_cancel_requested(
                self,
                response_id: str,
                *,
                ttl_seconds: int | None = ...
            ) -> bool: ...

        async def set_response_snapshot(
                self,
                response_id: str,
                response: ResponseObject,
                *,
                ttl_seconds: int | None = ...
            ) -> bool: ...

        async def transition_execution_status(
                self,
                response_id: str,
                next_status: ResponseStatus,
                *,
                ttl_seconds: int | None = ...
            ) -> bool: ...

        async def update_response(
                self,
                response: ResponseObject,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.PlatformContext:

        def __init__(
                self,
                *,
                call_id: str | None = ...,
                user_id_key: str | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.ResponseContext:

        def __init__(
                self,
                *,
                client_headers: dict[str, str] | None = ...,
                conversation_id: str | None = ...,
                created_at: datetime | None = ...,
                history_limit: int = 100,
                input_items: list[InputParam] | list[OutputItem] | None = ...,
                mode_flags: ResponseModeFlags,
                platform_context: PlatformContext | None = ...,
                prefetched_history_ids: list[str] | None = ...,
                previous_response_id: str | None = ...,
                provider: ResponseProviderProtocol | None = ...,
                query_parameters: dict[str, str] | None = ...,
                request: CreateResponse | None = ...,
                response_id: str
            ) -> None: ...

        async def get_history(self) -> Sequence[OutputItem]: ...

        async def get_input_items(
                self,
                *,
                resolve_references: bool = True
            ) -> Sequence[Item]: ...

        async def get_input_text(
                self,
                *,
                resolve_references: bool = True
            ) -> str: ...


    class azure.ai.agentserver.responses.ResponseEventStream:
        property response: dict[str, Any]    # Read-only

        def __init__(
                self,
                *,
                agent_reference: AgentReference | None = ...,
                model: str | None = ...,
                request: CreateResponse | None = ...,
                response: ResponseObject | None = ...,
                response_id: str | None = ...
            ) -> None: ...

        def add_output_item(self, item_id: str) -> OutputItemBuilder: ...

        def add_output_item_apply_patch_call(self) -> OutputItemBuilder: ...

        def add_output_item_apply_patch_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_code_interpreter_call(self) -> OutputItemCodeInterpreterCallBuilder: ...

        def add_output_item_compaction(self) -> OutputItemBuilder: ...

        def add_output_item_computer_call(self) -> OutputItemBuilder: ...

        def add_output_item_computer_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_custom_tool_call(
                self,
                call_id: str,
                name: str
            ) -> OutputItemCustomToolCallBuilder: ...

        def add_output_item_custom_tool_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_file_search_call(self) -> OutputItemFileSearchCallBuilder: ...

        def add_output_item_function_call(
                self,
                name: str,
                call_id: str
            ) -> OutputItemFunctionCallBuilder: ...

        def add_output_item_function_call_output(self, call_id: str) -> OutputItemFunctionCallOutputBuilder: ...

        def add_output_item_function_shell_call(self) -> OutputItemBuilder: ...

        def add_output_item_function_shell_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_image_gen_call(self) -> OutputItemImageGenCallBuilder: ...

        def add_output_item_local_shell_call(self) -> OutputItemBuilder: ...

        def add_output_item_local_shell_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_approval_request(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_approval_response(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_call(
                self,
                server_label: str,
                name: str,
                *,
                item_id: str | None = ...
            ) -> OutputItemMcpCallBuilder: ...

        def add_output_item_mcp_list_tools(self, server_label: str) -> OutputItemMcpListToolsBuilder: ...

        def add_output_item_message(self) -> OutputItemMessageBuilder: ...

        def add_output_item_reasoning_item(self) -> OutputItemReasoningItemBuilder: ...

        def add_output_item_structured_outputs(self) -> OutputItemBuilder: ...

        def add_output_item_web_search_call(self) -> OutputItemWebSearchCallBuilder: ...

        async def aoutput_item_apply_patch_call(
                self,
                call_id: str,
                operation: ApplyPatchFileOperation,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_apply_patch_call_output(
                self,
                call_id: str,
                *,
                output: str | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_compaction(self, encrypted_content: str) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_computer_call(
                self,
                call_id: str,
                action: ComputerAction,
                *,
                pending_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_computer_call_output(
                self,
                call_id: str,
                output: ComputerScreenshotImage,
                *,
                acknowledged_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_custom_tool_call_output(
                self,
                call_id: str,
                output: str | list[FunctionAndCustomToolCallOutput]
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_call(
                self,
                name: str,
                call_id: str,
                arguments: str | AsyncIterable[str]
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_call_output(
                self,
                call_id: str,
                output: str
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_shell_call(
                self,
                call_id: str,
                action: FunctionShellAction,
                environment: FunctionShellCallEnvironment,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_shell_call_output(
                self,
                call_id: str,
                output: list[FunctionShellCallOutputContent],
                *,
                max_output_length: int | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_image_gen_call(
                self,
                result_base64: str,
                *,
                partials: AsyncIterable[str] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_local_shell_call(
                self,
                call_id: str,
                action: LocalShellExecAction,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_local_shell_call_output(self, output: str) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_mcp_approval_request(
                self,
                server_label: str,
                name: str,
                arguments: str
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_mcp_approval_response(
                self,
                approval_request_id: str,
                approve: bool = False,
                *,
                reason: str | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_message(
                self,
                text: str | AsyncIterable[str],
                *,
                annotations: Sequence[Annotation] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_reasoning_item(self, summary_text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_structured_outputs(self, output: Any) -> AsyncIterator[ResponseStreamEvent]: ...

        def emit_completed(
                self,
                *,
                usage: ResponseUsage | None = ...
            ) -> ResponseCompletedEvent: ...

        def emit_created(
                self,
                *,
                status: str = "in_progress"
            ) -> ResponseCreatedEvent: ...

        def emit_failed(
                self,
                *,
                code: str | ResponseErrorCode = "server_error",
                message: str = "An internal server error occurred.",
                usage: ResponseUsage | None = ...
            ) -> ResponseFailedEvent: ...

        def emit_in_progress(self) -> ResponseInProgressEvent: ...

        def emit_incomplete(
                self,
                *,
                reason: str | None = ...,
                usage: ResponseUsage | None = ...
            ) -> ResponseIncompleteEvent: ...

        def emit_queued(self) -> ResponseQueuedEvent: ...

        def events(self) -> list[ResponseStreamEvent]: ...

        def output_item_apply_patch_call(
                self,
                call_id: str,
                operation: ApplyPatchFileOperation,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_apply_patch_call_output(
                self,
                call_id: str,
                *,
                output: str | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_compaction(self, encrypted_content: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_computer_call(
                self,
                call_id: str,
                action: ComputerAction,
                *,
                pending_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_computer_call_output(
                self,
                call_id: str,
                output: ComputerScreenshotImage,
                *,
                acknowledged_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_custom_tool_call_output(
                self,
                call_id: str,
                output: str | list[FunctionAndCustomToolCallOutput]
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_call(
                self,
                name: str,
                call_id: str,
                arguments: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_call_output(
                self,
                call_id: str,
                output: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_shell_call(
                self,
                call_id: str,
                action: FunctionShellAction,
                environment: FunctionShellCallEnvironment,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_shell_call_output(
                self,
                call_id: str,
                output: list[FunctionShellCallOutputContent],
                *,
                max_output_length: int | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_image_gen_call(self, result_base64: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_local_shell_call(
                self,
                call_id: str,
                action: LocalShellExecAction,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_local_shell_call_output(self, output: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_mcp_approval_request(
                self,
                server_label: str,
                name: str,
                arguments: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_mcp_approval_response(
                self,
                approval_request_id: str,
                approve: bool = False,
                *,
                reason: str | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_message(
                self,
                text: str,
                *,
                annotations: Sequence[Annotation] | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_reasoning_item(self, summary_text: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_structured_outputs(self, output: Any) -> Iterator[ResponseStreamEvent]: ...


    class azure.ai.agentserver.responses.ResponseObject(TypedDict, total=False):
        key "agent_reference": Required[Optional[AgentReference]]
        key "background": Optional[bool]
        key "completed_at": Optional[int]
        key "conversation": Optional[ConversationReference]
        key "created_at": Required[int]
        key "error": Required[Optional[ResponseError]]
        key "id": Required[str]
        key "incomplete_details": Required[Optional[ResponseIncompleteDetails]]
        key "instructions": Required[Optional[Union[str, list[Item]]]]
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[Moderation]
        key "object": Required[Literal["response"]]
        key "output": Required[list[OutputItem]]
        key "output_text": Optional[str]
        key "parallel_tool_calls": Required[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "reasoning": Optional[Reasoning]
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "status": Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "usage": ForwardRef('ResponseUsage', module='types')
        key "user": str
        agent_reference: AgentReference
        background: bool
        completed_at: int
        conversation: ConversationReference
        created_at: int
        error: ResponseError
        id: str
        incomplete_details: ResponseIncompleteDetails
        instructions: Union[str, list[Item]]
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: Moderation
        object: Literal[response]
        output: list[OutputItem]
        output_text: str
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        reasoning: Reasoning
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        status: Literal[completed, failed, in_progress, cancelled, queued, incomplete]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        usage: ResponseUsage
        user: str


    @runtime_checkable
    class azure.ai.agentserver.responses.ResponseProviderProtocol(Protocol):

        async def create_response(
                self,
                response: ResponseObject,
                input_items: Iterable[OutputItem] | None,
                history_item_ids: Iterable[str] | None,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def delete_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def get_history_item_ids(
                self,
                previous_response_id: str | None,
                conversation_id: str | None,
                limit: int,
                *,
                context: PlatformContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self,
                response_id: str,
                limit: int = 20,
                ascending: bool = False,
                after: str | None = None,
                before: str | None = None,
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self,
                item_ids: Iterable[str],
                *,
                context: PlatformContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_response(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> ResponseObject: ...

        async def update_response(
                self,
                response: ResponseObject,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...


    @runtime_checkable
    class azure.ai.agentserver.responses.ResponseStreamProviderProtocol(Protocol):

        async def delete_stream_events(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> None: ...

        async def get_stream_events(
                self,
                response_id: str,
                *,
                context: PlatformContext | None = ...
            ) -> list[ResponseStreamEvent] | None: ...

        async def save_stream_events(
                self,
                response_id: str,
                events: list[ResponseStreamEvent],
                *,
                context: PlatformContext | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.ResponsesAgentServerHost(AgentServerHost):
        property routes: list[BaseRoute]    # Read-only

        def __init__(
                self,
                *,
                options: ResponsesServerOptions | None = ...,
                prefix: str = "",
                store: ResponseProviderProtocol | None = ...,
                **kwargs: Any
            ) -> None: ...

        def response_handler(self, fn: CreateHandlerFn) -> CreateHandlerFn: ...


    class azure.ai.agentserver.responses.ResponsesServerOptions:
        property sse_keep_alive_enabled: bool    # Read-only

        def __init__(
                self,
                *,
                additional_server_version: str | None = ...,
                create_span_hook: CreateSpanHook | None = ...,
                default_fetch_history_count: int = 100,
                default_model: str | None = ...,
                shutdown_grace_period_seconds: int = 10,
                sse_keep_alive_interval_seconds: int | None = ...
            ) -> None: ...

        @classmethod
        def from_env(cls, environ: Mapping[str, str] | None = None) -> ResponsesServerOptions: ...


    class azure.ai.agentserver.responses.TextResponse:

        def __aiter__(self) -> AsyncIterator[ResponseStreamEvent]: ...

        def __init__(
                self,
                context: ResponseContext,
                request: CreateResponse,
                *,
                configure: Callable[[ResponseObject], None] | None = ...,
                text: TextSource
            ) -> None: ...


namespace azure.ai.agentserver.responses.hosting

    class azure.ai.agentserver.responses.hosting.ResponsesAgentServerHost(AgentServerHost):
        property routes: list[BaseRoute]    # Read-only

        def __init__(
                self,
                *,
                options: ResponsesServerOptions | None = ...,
                prefix: str = "",
                store: ResponseProviderProtocol | None = ...,
                **kwargs: Any
            ) -> None: ...

        def response_handler(self, fn: CreateHandlerFn) -> CreateHandlerFn: ...


namespace azure.ai.agentserver.responses.models

    def azure.ai.agentserver.responses.models.get_content_expanded(message: ItemMessage) -> list[MessageContent]: ...


    def azure.ai.agentserver.responses.models.get_conversation_expanded(request: CreateResponse) -> Optional[ConversationParam_2]: ...


    def azure.ai.agentserver.responses.models.get_conversation_id(request: CreateResponse | ResponseObject) -> Optional[str]: ...


    def azure.ai.agentserver.responses.models.get_input_expanded(request: CreateResponse) -> list[Item]: ...


    def azure.ai.agentserver.responses.models.get_tool_choice_expanded(request: CreateResponse) -> Optional[ToolChoiceParam]: ...


    class azure.ai.agentserver.responses.models.A2APreviewTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "project_connection_id": str
        key "type": Required[Literal["a2a_preview"]]
        agent_card_path: str
        base_url: str
        project_connection_id: str
        type: Literal[a2a_preview]


    class azure.ai.agentserver.responses.models.A2AToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["a2a_preview_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[a2a_preview_call]


    class azure.ai.agentserver.responses.models.A2AToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["a2a_preview_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[a2a_preview_call_output]


    class azure.ai.agentserver.responses.models.AISearchIndexResource(TypedDict, total=False):
        key "filter": str
        key "index_asset_id": str
        key "index_name": str
        key "project_connection_id": str
        key "query_type": Literal["simple", "semantic", "vector", "vector_simple_hybrid", "vector_semantic_hybrid"]
        key "top_k": int
        filter: str
        index_asset_id: str
        index_name: str
        project_connection_id: str
        query_type: AzureAISearchQueryType
        top_k: int


    class azure.ai.agentserver.responses.models.AdditionalToolsItemParam(TypedDict, total=False):
        key "id": Optional[str]
        key "role": Required[Literal["developer"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["additional_tools"]]
        id: str
        role: Literal[developer]
        tools: list[Tool]
        type: Literal[additional_tools]


    class azure.ai.agentserver.responses.models.AgentDefinitionOptInKeys(TypedDict):


    class azure.ai.agentserver.responses.models.AgentKind(TypedDict):


    class azure.ai.agentserver.responses.models.AgentObject(TypedDict, total=False):
        key "id": Required[str]
        key "name": Required[str]
        key "object": Required[Literal["agent"]]
        key "versions": Required[AgentObjectVersions]
        id: str
        name: str
        object: Literal[agent]
        versions: AgentObjectVersions


    class azure.ai.agentserver.responses.models.AgentObjectType(TypedDict):


    class azure.ai.agentserver.responses.models.AgentObjectVersions(TypedDict, total=False):
        key "latest": Required[AgentVersionObject]
        latest: AgentVersionObject


    class azure.ai.agentserver.responses.models.AgentProtocol(TypedDict):


    class azure.ai.agentserver.responses.models.AgentReference(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["agent_reference"]]
        key "version": str
        name: str
        type: Literal[agent_reference]
        version: str


    class azure.ai.agentserver.responses.models.AgentVersionObject(TypedDict, total=False):
        key "created_at": Required[int]
        key "definition": Required[AgentDefinition]
        key "description": str
        key "id": Required[str]
        key "metadata": Required[Optional[dict[str, str]]]
        key "name": Required[str]
        key "object": Required[Literal["version"]]
        key "version": Required[str]
        created_at: int
        definition: AgentDefinition
        description: str
        id: str
        metadata: dict[str, str]
        name: str
        object: Literal[version]
        version: str


    class azure.ai.agentserver.responses.models.AnnotationType(TypedDict):


    class azure.ai.agentserver.responses.models.ApiErrorResponse(TypedDict, total=False):
        key "error": Required[Error]
        error: Error


    class azure.ai.agentserver.responses.models.ApplyPatchCallOutputStatus(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchCallOutputStatusParam(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchCallStatus(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchCallStatusParam(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchCreateFileOperation(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal["create_file"]]
        diff: str
        path: str
        type: Literal[create_file]


    class azure.ai.agentserver.responses.models.ApplyPatchCreateFileOperationParam(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal["create_file"]]
        diff: str
        path: str
        type: Literal[create_file]


    class azure.ai.agentserver.responses.models.ApplyPatchDeleteFileOperation(TypedDict, total=False):
        key "path": Required[str]
        key "type": Required[Literal["delete_file"]]
        path: str
        type: Literal[delete_file]


    class azure.ai.agentserver.responses.models.ApplyPatchDeleteFileOperationParam(TypedDict, total=False):
        key "path": Required[str]
        key "type": Required[Literal["delete_file"]]
        path: str
        type: Literal[delete_file]


    class azure.ai.agentserver.responses.models.ApplyPatchFileOperationType(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchOperationParamType(TypedDict):


    class azure.ai.agentserver.responses.models.ApplyPatchToolCallItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "operation": Required[ApplyPatchOperationParam]
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal["apply_patch_call"]]
        call_id: str
        id: str
        operation: ApplyPatchOperationParam
        status: ApplyPatchCallStatusParam
        type: Literal[apply_patch_call]


    class azure.ai.agentserver.responses.models.ApplyPatchToolCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Optional[str]
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal["apply_patch_call_output"]]
        call_id: str
        id: str
        output: str
        status: ApplyPatchCallOutputStatusParam
        type: Literal[apply_patch_call_output]


    class azure.ai.agentserver.responses.models.ApplyPatchToolParam(TypedDict, total=False):
        key "type": Required[Literal["apply_patch"]]
        type: Literal[apply_patch]


    class azure.ai.agentserver.responses.models.ApplyPatchUpdateFileOperation(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal["update_file"]]
        diff: str
        path: str
        type: Literal[update_file]


    class azure.ai.agentserver.responses.models.ApplyPatchUpdateFileOperationParam(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal["update_file"]]
        diff: str
        path: str
        type: Literal[update_file]


    class azure.ai.agentserver.responses.models.ApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.agentserver.responses.models.AutoCodeInterpreterToolParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal["auto"]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        type: Literal[auto]


    class azure.ai.agentserver.responses.models.AzureAISearchQueryType(TypedDict):


    class azure.ai.agentserver.responses.models.AzureAISearchTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "type": Required[Literal["azure_ai_search"]]
        azure_ai_search: AzureAISearchToolResource
        type: Literal[azure_ai_search]


    class azure.ai.agentserver.responses.models.AzureAISearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["azure_ai_search_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[azure_ai_search_call]


    class azure.ai.agentserver.responses.models.AzureAISearchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["azure_ai_search_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[azure_ai_search_call_output]


    class azure.ai.agentserver.responses.models.AzureAISearchToolResource(TypedDict, total=False):
        key "indexes": Required[list[AISearchIndexResource]]
        indexes: list[AISearchIndexResource]


    class azure.ai.agentserver.responses.models.AzureFunctionBinding(TypedDict, total=False):
        key "storage_queue": Required[AzureFunctionStorageQueue]
        key "type": Required[Literal["storage_queue"]]
        storage_queue: AzureFunctionStorageQueue
        type: Literal[storage_queue]


    class azure.ai.agentserver.responses.models.AzureFunctionDefinition(TypedDict, total=False):
        key "function": Required[AzureFunctionDefinitionFunction]
        key "input_binding": Required[AzureFunctionBinding]
        key "output_binding": Required[AzureFunctionBinding]
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding


    class azure.ai.agentserver.responses.models.AzureFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.agentserver.responses.models.AzureFunctionStorageQueue(TypedDict, total=False):
        key "queue_name": Required[str]
        key "queue_service_endpoint": Required[str]
        queue_name: str
        queue_service_endpoint: str


    class azure.ai.agentserver.responses.models.AzureFunctionTool(TypedDict, total=False):
        key "azure_function": Required[AzureFunctionDefinition]
        key "type": Required[Literal["azure_function"]]
        azure_function: AzureFunctionDefinition
        type: Literal[azure_function]


    class azure.ai.agentserver.responses.models.AzureFunctionToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["azure_function_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[azure_function_call]


    class azure.ai.agentserver.responses.models.AzureFunctionToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["azure_function_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[azure_function_call_output]


    class azure.ai.agentserver.responses.models.BingCustomSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "freshness": str
        key "instance_name": Required[str]
        key "market": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        freshness: str
        instance_name: str
        market: str
        project_connection_id: str
        set_lang: str


    class azure.ai.agentserver.responses.models.BingCustomSearchPreviewTool(TypedDict, total=False):
        key "bing_custom_search_preview": Required[BingCustomSearchToolParameters]
        key "type": Required[Literal["bing_custom_search_preview"]]
        bing_custom_search_preview: BingCustomSearchToolParameters
        type: Literal[bing_custom_search_preview]


    class azure.ai.agentserver.responses.models.BingCustomSearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["bing_custom_search_preview_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[bing_custom_search_preview_call]


    class azure.ai.agentserver.responses.models.BingCustomSearchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["bing_custom_search_preview_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[bing_custom_search_preview_call_output]


    class azure.ai.agentserver.responses.models.BingCustomSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingCustomSearchConfiguration]]
        search_configurations: list[BingCustomSearchConfiguration]


    class azure.ai.agentserver.responses.models.BingGroundingSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "freshness": str
        key "market": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        freshness: str
        market: str
        project_connection_id: str
        set_lang: str


    class azure.ai.agentserver.responses.models.BingGroundingSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingGroundingSearchConfiguration]]
        search_configurations: list[BingGroundingSearchConfiguration]


    class azure.ai.agentserver.responses.models.BingGroundingTool(TypedDict, total=False):
        key "bing_grounding": Required[BingGroundingSearchToolParameters]
        key "type": Required[Literal["bing_grounding"]]
        bing_grounding: BingGroundingSearchToolParameters
        type: Literal[bing_grounding]


    class azure.ai.agentserver.responses.models.BingGroundingToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["bing_grounding_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[bing_grounding_call]


    class azure.ai.agentserver.responses.models.BingGroundingToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["bing_grounding_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[bing_grounding_call_output]


    class azure.ai.agentserver.responses.models.BrowserAutomationPreviewTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "type": Required[Literal["browser_automation_preview"]]
        browser_automation_preview: BrowserAutomationToolParameters
        type: Literal[browser_automation_preview]


    class azure.ai.agentserver.responses.models.BrowserAutomationToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["browser_automation_preview_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[browser_automation_preview_call]


    class azure.ai.agentserver.responses.models.BrowserAutomationToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["browser_automation_preview_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[browser_automation_preview_call_output]


    class azure.ai.agentserver.responses.models.BrowserAutomationToolConnectionParameters(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.agentserver.responses.models.BrowserAutomationToolParameters(TypedDict, total=False):
        key "connection": Required[BrowserAutomationToolConnectionParameters]
        connection: BrowserAutomationToolConnectionParameters


    class azure.ai.agentserver.responses.models.CaptureStructuredOutputsTool(TypedDict, total=False):
        key "outputs": Required[StructuredOutputDefinition]
        key "type": Required[Literal["capture_structured_outputs"]]
        outputs: StructuredOutputDefinition
        type: Literal[capture_structured_outputs]


    class azure.ai.agentserver.responses.models.ChatSummaryMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal["chat_summary"]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[chat_summary]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.agentserver.responses.models.ClickButtonType(TypedDict):


    class azure.ai.agentserver.responses.models.ClickParam(TypedDict, total=False):
        key "button": Required[Literal["left", "right", "wheel", "back", "forward"]]
        key "keys": Optional[list[str]]
        key "type": Required[Literal["click"]]
        key "x": Required[int]
        key "y": Required[int]
        button: ClickButtonType
        keys_property: list[str]
        type: Literal[click]
        x: int
        y: int


    class azure.ai.agentserver.responses.models.CodeInterpreterOutputImage(TypedDict, total=False):
        key "type": Required[Literal["image"]]
        key "url": Required[str]
        type: Literal[image]
        url: str


    class azure.ai.agentserver.responses.models.CodeInterpreterOutputLogs(TypedDict, total=False):
        key "logs": Required[str]
        key "type": Required[Literal["logs"]]
        logs: str
        type: Literal[logs]


    class azure.ai.agentserver.responses.models.CodeInterpreterTool(TypedDict, total=False):
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "type": Required[Literal["code_interpreter"]]
        container: Union[str, AutoCodeInterpreterToolParam]
        type: Literal[code_interpreter]


    class azure.ai.agentserver.responses.models.CompactResource(TypedDict, total=False):
        key "created_at": Required[int]
        key "id": Required[str]
        key "object": Required[Literal["compaction"]]
        key "output": Required[list[ItemField]]
        key "usage": Required[ResponseUsage]
        created_at: int
        id: str
        object: Literal[compaction]
        output: list[ItemField]
        usage: ResponseUsage


    class azure.ai.agentserver.responses.models.CompactResponseMethodPublicBody(TypedDict, total=False):
        key "input": Optional[Union[str, list[Item]]]
        key "instructions": Optional[str]
        key "model": Required[Optional[Literal["gpt-4", "gpt-4-mini", "gpt-4-nano", "gpt-4-mini-2026-03-17", "gpt-4-nano-2026-03-17", "gpt-3-chat-latest", "gpt-2", "gpt-2-2025-12-11", "gpt-2-chat-latest", "gpt-2-pro", "gpt-2-pro-2025-12-11", "gpt-1", "gpt-1-2025-11-13", "gpt-1-codex", "gpt-1-mini", "gpt-1-chat-latest", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-2025-08-07", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-5-chat-latest", "gpt-1", "gpt-1-mini", "gpt-1-nano", "gpt-1-2025-04-14", "gpt-1-mini-2025-04-14", "gpt-1-nano-2025-04-14", "o4-mini", "o4-mini-2025-04-16", "o3", "o3-2025-04-16", "o3-mini", "o3-mini-2025-01-31", "o1", "o1-2024-12-17", "o1-preview", "o1-preview-2024-09-12", "o1-mini", "o1-mini-2024-09-12", "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4o-audio-preview", "gpt-4o-audio-preview-2024-10-01", "gpt-4o-audio-preview-2024-12-17", "gpt-4o-audio-preview-2025-06-03", "gpt-4o-mini-audio-preview", "gpt-4o-mini-audio-preview-2024-12-17", "gpt-4o-search-preview", "gpt-4o-mini-search-preview", "gpt-4o-search-preview-2025-03-11", "gpt-4o-mini-search-preview-2025-03-11", "chatgpt-4o-latest", "codex-mini-latest", "gpt-4o-mini", "gpt-4o-mini-2024-07-18", "gpt-4-turbo", "gpt-4-turbo-2024-04-09", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613", "gpt-5-turbo", "gpt-5-turbo-16k", "gpt-5-turbo-0301", "gpt-5-turbo-0613", "gpt-5-turbo-1106", "gpt-5-turbo-0125", "gpt-5-turbo-16k-0613", "o1-pro", "o1-pro-2025-03-19", "o3-pro", "o3-pro-2025-06-10", "o3-deep-research", "o3-deep-research-2025-06-26", "o4-mini-deep-research", "o4-mini-deep-research-2025-06-26", "computer-use-preview", "computer-use-preview-2025-03-11", "gpt-5-codex", "gpt-5-pro", "gpt-5-pro-2025-10-06", "gpt-1-codex-max"]]]
        key "previous_response_id": Optional[str]
        key "prompt_cache_key": Optional[str]
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "service_tier": Optional[Literal["auto", "default", "flex", "priority"]]
        input: Union[str, list[Item]]
        instructions: str
        model: ModelIdsCompaction
        previous_response_id: str
        prompt_cache_key: str
        prompt_cache_retention: PromptCacheRetentionEnum
        service_tier: ServiceTierEnum


    class azure.ai.agentserver.responses.models.CompactionSummaryItemParam(TypedDict, total=False):
        key "encrypted_content": Required[str]
        key "id": Optional[str]
        key "type": Required[Literal["compaction"]]
        encrypted_content: str
        id: str
        type: Literal[compaction]


    class azure.ai.agentserver.responses.models.ComparisonFilter(TypedDict, total=False):
        key "key": Required[str]
        key "type": Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
        key "value": Required[Union[str, float, bool, list[Union[str, float]]]]
        key: str
        type: Literal[eq, ne, gt, gte, lt, lte, in, nin]
        value: Union[str, float, bool, list[Union[str, float]]]


    class azure.ai.agentserver.responses.models.CompoundFilter(TypedDict, total=False):
        key "filters": Required[list[Union[ComparisonFilter, Any]]]
        key "type": Required[Literal["and", "or"]]
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal[and, or]


    class azure.ai.agentserver.responses.models.ComputerActionType(TypedDict):


    class azure.ai.agentserver.responses.models.ComputerCallOutputItemParam(TypedDict, total=False):
        key "acknowledged_safety_checks": Optional[list[ComputerCallSafetyCheckParam]]
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Required[ComputerScreenshotImage]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["computer_call_output"]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        call_id: str
        id: str
        output: ComputerScreenshotImage
        status: FunctionCallItemStatus
        type: Literal[computer_call_output]


    class azure.ai.agentserver.responses.models.ComputerCallSafetyCheckParam(TypedDict, total=False):
        key "code": Optional[str]
        key "id": Required[str]
        key "message": Optional[str]
        code: str
        id: str
        message: str


    class azure.ai.agentserver.responses.models.ComputerEnvironment(TypedDict):


    class azure.ai.agentserver.responses.models.ComputerScreenshotContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Required[Optional[str]]
        key "image_url": Required[Optional[str]]
        key "type": Required[Literal["computer_screenshot"]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[computer_screenshot]


    class azure.ai.agentserver.responses.models.ComputerScreenshotImage(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        key "type": Required[Literal["computer_screenshot"]]
        file_id: str
        image_url: str
        type: Literal[computer_screenshot]


    class azure.ai.agentserver.responses.models.ComputerTool(TypedDict, total=False):
        key "type": Required[Literal["computer"]]
        type: Literal[computer]


    class azure.ai.agentserver.responses.models.ComputerUsePreviewTool(TypedDict, total=False):
        key "display_height": Required[int]
        key "display_width": Required[int]
        key "environment": Required[Literal["windows", "mac", "linux", "ubuntu", "browser"]]
        key "type": Required[Literal["computer_use_preview"]]
        display_height: int
        display_width: int
        environment: ComputerEnvironment
        type: Literal[computer_use_preview]


    class azure.ai.agentserver.responses.models.ContainerAutoParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal["container_auto"]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        skills: list[ContainerSkill]
        type: Literal[container_auto]


    class azure.ai.agentserver.responses.models.ContainerFileCitationBody(TypedDict, total=False):
        key "container_id": Required[str]
        key "end_index": Required[int]
        key "file_id": Required[str]
        key "filename": Required[str]
        key "start_index": Required[int]
        key "type": Required[Literal["container_file_citation"]]
        container_id: str
        end_index: int
        file_id: str
        filename: str
        start_index: int
        type: Literal[container_file_citation]


    class azure.ai.agentserver.responses.models.ContainerMemoryLimit(TypedDict):


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyAllowlistParam(TypedDict, total=False):
        key "allowed_domains": Required[list[str]]
        key "type": Required[Literal["allowlist"]]
        allowed_domains: list[str]
        domain_secrets: list[ContainerNetworkPolicyDomainSecretParam]
        type: Literal[allowlist]


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyDisabledParam(TypedDict, total=False):
        key "type": Required[Literal["disabled"]]
        type: Literal[disabled]


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyDomainSecretParam(TypedDict, total=False):
        key "domain": Required[str]
        key "name": Required[str]
        key "value": Required[str]
        domain: str
        name: str
        value: str


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyParamType(TypedDict):


    class azure.ai.agentserver.responses.models.ContainerReferenceResource(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal["container_reference"]]
        container_id: str
        type: Literal[container_reference]


    class azure.ai.agentserver.responses.models.ContainerSkillType(TypedDict):


    class azure.ai.agentserver.responses.models.ContextManagementParam(TypedDict, total=False):
        key "compact_threshold": Optional[int]
        key "type": Required[str]
        compact_threshold: int
        type: str


    class azure.ai.agentserver.responses.models.ConversationItemList(TypedDict, total=False):
        key "data": Required[list[OutputItem]]
        key "first_id": Required[str]
        key "has_more": Required[bool]
        key "last_id": Required[str]
        key "object": Required[Literal["list"]]
        data: list[OutputItem]
        first_id: str
        has_more: bool
        last_id: str
        object: Literal[list]


    class azure.ai.agentserver.responses.models.ConversationParam_2(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.ai.agentserver.responses.models.ConversationReference(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.ai.agentserver.responses.models.ConversationResource(TypedDict, total=False):
        key "created_at": Required[int]
        key "id": Required[str]
        key "metadata": Required[Metadata]
        key "object": Required[Literal["conversation"]]
        created_at: int
        id: str
        metadata: Metadata
        object: Literal[conversation]


    class azure.ai.agentserver.responses.models.CoordParam(TypedDict, total=False):
        key "x": Required[int]
        key "y": Required[int]
        x: int
        y: int


    class azure.ai.agentserver.responses.models.CreateAgentFromManifestRequest(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "name": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        name: str
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.CreateAgentFromManifestRequest1(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "name": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        name: str
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.CreateAgentRequest(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        key "name": Required[str]
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]
        name: str


    class azure.ai.agentserver.responses.models.CreateAgentRequest1(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        key "name": Required[str]
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]
        name: str


    class azure.ai.agentserver.responses.models.CreateAgentVersionFromManifestRequest(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.CreateAgentVersionFromManifestRequest1(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.CreateAgentVersionRequest(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]


    class azure.ai.agentserver.responses.models.CreateAgentVersionRequest1(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]


    class azure.ai.agentserver.responses.models.CreateConversationBody(TypedDict, total=False):
        key "items": Optional[list[Item]]
        key "metadata": Optional[Metadata]
        items_property: list[Item]
        metadata: Metadata


    class azure.ai.agentserver.responses.models.CreateConversationItemsRequest(TypedDict, total=False):
        key "items": Required[list[Item]]
        items_property: list[Item]


    class azure.ai.agentserver.responses.models.CreateMemoryStoreRequest(TypedDict, total=False):
        key "definition": Required[MemoryStoreDefinition]
        key "description": str
        key "name": Required[str]
        definition: MemoryStoreDefinition
        description: str
        metadata: dict[str, str]
        name: str


    class azure.ai.agentserver.responses.models.CreateResponse(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "background": Optional[bool]
        key "context_management": Optional[list[ContextManagementParam]]
        key "conversation": Optional[ConversationParam]
        key "include": Optional[list[Literal["results", "results", "sources", "image_url", "image_url", "outputs", "encrypted_content", "logprobs", "results"]]]
        key "input": ForwardRef('InputParam', module='types')
        key "instructions": Optional[str]
        key "internal_metadata": ForwardRef('CreateResponseInternalMetadata', module='types')
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[ModerationParam]
        key "parallel_tool_calls": Optional[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "rai_config": str
        key "reasoning": Optional[Reasoning]
        key "resolved_agent_version": ForwardRef('AgentVersionObject', module='types')
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "store": Optional[bool]
        key "stream": Optional[bool]
        key "stream_options": Optional[ResponseStreamOptions]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "user": str
        agent_reference: AgentReference
        background: bool
        context_management: list[ContextManagementParam]
        conversation: ConversationParam
        include: list[IncludeEnum]
        input: InputParam
        instructions: str
        internal_metadata: CreateResponseInternalMetadata
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: ModerationParam
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        rai_config: str
        reasoning: Reasoning
        resolved_agent_version: AgentVersionObject
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        store: bool
        stream: bool
        stream_options: ResponseStreamOptions
        structured_inputs: dict[str, Any]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        user: str


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadata(TypedDict):
        key "application-context": ForwardRef('CreateResponseInternalMetadataApplicationContext', module='types')
        key "defender-for-ai-context": ForwardRef('CreateResponseInternalMetadataDefenderForAiContext', module='types')
        key "response-context": ForwardRef('CreateResponseInternalMetadataResponseContext', module='types')
        key "user-context": ForwardRef('CreateResponseInternalMetadataUserContext', module='types')
        key "web_search": ForwardRef('CreateResponseInternalMetadataWebSearch', module='types')
        application_context: CreateResponseInternalMetadataApplicationContext
        defender_for_ai_context: CreateResponseInternalMetadataDefenderForAiContext
        feature_flags: list[str]
        response_context: CreateResponseInternalMetadataResponseContext
        user_context: CreateResponseInternalMetadataUserContext
        web_search: CreateResponseInternalMetadataWebSearch


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataApplicationContext(TypedDict):
        key "application-id": str
        key "chat-isolation-key": str
        key "creation-date": str
        key "region": str
        key "resource-id": str
        key "subscription-id": str
        key "tenant-id": str
        key "user-isolation-key": str
        application_id: str
        chat_isolation_key: str
        creation_date: str
        region: str
        resource_id: str
        subscription_id: str
        tenant_id: str
        user_isolation_key: str


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataDefenderForAiContext(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataResponseContext(TypedDict):
        key "agent-kind": str
        key "agent-name": str
        key "agent-version": str
        key "agent-version-created-at": str
        key "agent-version-description": str
        key "agent-version-id": str
        key "conversation-id": str
        key "hosted-agent-image": str
        key "max-output-tokens": int
        key "max-tool-calls": int
        key "model": str
        key "parallel-tool-calls": bool
        key "previous-response-id": str
        key "reasoning-effort": str
        key "reasoning-summary": str
        key "temperature": str
        key "top-p": str
        agent_kind: str
        agent_name: str
        agent_version: str
        agent_version_created_at: str
        agent_version_description: str
        agent_version_id: str
        conversation_id: str
        hosted_agent_image: str
        max_output_tokens: int
        max_tool_calls: int
        model: str
        parallel_tool_calls: bool
        previous_response_id: str
        reasoning_effort: str
        reasoning_summary: str
        temperature: str
        tools: list[CreateResponseInternalMetadataResponseContextTool]
        top_p: str


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataResponseContextTool(TypedDict):
        key "tool-name": str
        key "tool-type": str
        tool_name: str
        tool_type: str


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataUserContext(TypedDict):
        key "appid": str
        key "auth-type": str
        key "ms-user-agent": str
        key "oid": str
        key "request-ip": str
        key "tid": str
        key "token-type": str
        key "upn": str
        key "user-agent": str
        appid: str
        auth_type: str
        ms_user_agent: str
        oid: str
        request_ip: str
        tid: str
        token_type: str
        upn: str
        user_agent: str


    class azure.ai.agentserver.responses.models.CreateResponseInternalMetadataWebSearch(TypedDict, total=False):
        key "custom_search_config_id": str
        key "custom_search_resource_id": str
        custom_search_config_id: str
        custom_search_resource_id: str


    class azure.ai.agentserver.responses.models.CustomGrammarFormatParam(TypedDict, total=False):
        key "definition": Required[str]
        key "syntax": Required[Literal["lark", "regex"]]
        key "type": Required[Literal["grammar"]]
        definition: str
        syntax: GrammarSyntax1
        type: Literal[grammar]


    class azure.ai.agentserver.responses.models.CustomTextFormatParam(TypedDict, total=False):
        key "type": Required[Literal["text"]]
        type: Literal[text]


    class azure.ai.agentserver.responses.models.CustomToolCallOutputResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "created_by": str
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["custom_tool_call_output"]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        status: FunctionCallOutputStatusEnum
        type: Literal[custom_tool_call_output]


    class azure.ai.agentserver.responses.models.CustomToolCallResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "created_by": str
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["custom_tool_call"]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        id: str
        input: str
        name: str
        namespace: str
        response_id: str
        status: FunctionCallStatus
        type: Literal[custom_tool_call]


    class azure.ai.agentserver.responses.models.CustomToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": str
        key "format": ForwardRef('CustomToolParamFormat', module='types')
        key "name": Required[str]
        key "type": Required[Literal["custom"]]
        defer_loading: bool
        description: str
        format: CustomToolParamFormat
        name: str
        type: Literal[custom]


    class azure.ai.agentserver.responses.models.CustomToolParamFormatType(TypedDict):


    class azure.ai.agentserver.responses.models.DeleteAgentResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal["deleted"]]
        deleted: bool
        name: str
        object: Literal[deleted]


    class azure.ai.agentserver.responses.models.DeleteAgentVersionResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal["deleted"]]
        key "version": Required[str]
        deleted: bool
        name: str
        object: Literal[deleted]
        version: str


    class azure.ai.agentserver.responses.models.DeleteMemoryStoreResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal["deleted"]]
        deleted: bool
        name: str
        object: Literal[deleted]


    class azure.ai.agentserver.responses.models.DeleteResponseResult(TypedDict, total=False):
        key "deleted": Required[Literal[True]]
        key "id": Required[str]
        key "object": Required[Literal["response"]]
        deleted: Literal[True]
        id: str
        object: Literal[response]


    class azure.ai.agentserver.responses.models.DeleteScopeRequest(TypedDict, total=False):
        key "scope": Required[str]
        scope: str


    class azure.ai.agentserver.responses.models.DeletedConversationResource(TypedDict, total=False):
        key "deleted": Required[bool]
        key "id": Required[str]
        key "object": Required[Literal["deleted"]]
        deleted: bool
        id: str
        object: Literal[deleted]


    class azure.ai.agentserver.responses.models.DetailEnum(TypedDict):


    class azure.ai.agentserver.responses.models.DoubleClickAction(TypedDict, total=False):
        key "keys": Required[Optional[list[str]]]
        key "type": Required[Literal["double_click"]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        type: Literal[double_click]
        x: int
        y: int


    class azure.ai.agentserver.responses.models.DragParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "path": Required[list[CoordParam]]
        key "type": Required[Literal["drag"]]
        keys_property: list[str]
        path: list[CoordParam]
        type: Literal[drag]


    class azure.ai.agentserver.responses.models.EmptyModelParam(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.Error(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": str
        additionalInfo: dict[str, Any]
        additional_info: dict[str, Any]
        code: str
        debugInfo: dict[str, Any]
        debug_info: dict[str, Any]
        details: list[Error]
        message: str
        param: str
        type: str


    class azure.ai.agentserver.responses.models.FabricDataAgentToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["fabric_dataagent_preview_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[fabric_dataagent_preview_call]


    class azure.ai.agentserver.responses.models.FabricDataAgentToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["fabric_dataagent_preview_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[fabric_dataagent_preview_call_output]


    class azure.ai.agentserver.responses.models.FabricDataAgentToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.agentserver.responses.models.FileCitationBody(TypedDict, total=False):
        key "file_id": Required[str]
        key "filename": Required[str]
        key "index": Required[int]
        key "type": Required[Literal["file_citation"]]
        file_id: str
        filename: str
        index: int
        type: Literal[file_citation]


    class azure.ai.agentserver.responses.models.FileInputDetail(TypedDict):


    class azure.ai.agentserver.responses.models.FilePath(TypedDict, total=False):
        key "file_id": Required[str]
        key "index": Required[int]
        key "type": Required[Literal["file_path"]]
        file_id: str
        index: int
        type: Literal[file_path]


    class azure.ai.agentserver.responses.models.FileSearchTool(TypedDict, total=False):
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal["file_search"]]
        key "vector_store_ids": Required[list[str]]
        filters: Filters
        max_num_results: int
        ranking_options: RankingOptions
        type: Literal[file_search]
        vector_store_ids: list[str]


    class azure.ai.agentserver.responses.models.FileSearchToolCallResults(TypedDict, total=False):
        key "attributes": Optional[VectorStoreFileAttributes]
        key "file_id": str
        key "filename": str
        key "score": float
        key "text": str
        attributes: VectorStoreFileAttributes
        file_id: str
        filename: str
        score: float
        text: str


    class azure.ai.agentserver.responses.models.FoundryFeaturesOptInKeys(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionCallItemStatus(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Required[Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]]]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["function_call_output"]]
        call_id: str
        id: str
        output: Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]]
        status: FunctionCallItemStatus
        type: Literal[function_call_output]


    class azure.ai.agentserver.responses.models.FunctionCallOutputStatusEnum(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionCallStatus(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellAction(TypedDict, total=False):
        key "commands": Required[list[str]]
        key "max_output_length": Required[Optional[int]]
        key "timeout_ms": Required[Optional[int]]
        commands: list[str]
        max_output_length: int
        timeout_ms: int


    class azure.ai.agentserver.responses.models.FunctionShellActionParam(TypedDict, total=False):
        key "commands": Required[list[str]]
        key "max_output_length": Optional[int]
        key "timeout_ms": Optional[int]
        commands: list[str]
        max_output_length: int
        timeout_ms: int


    class azure.ai.agentserver.responses.models.FunctionShellCallEnvironmentType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParam(TypedDict, total=False):
        key "action": Required[FunctionShellActionParam]
        key "call_id": Required[str]
        key "environment": Optional[FunctionShellCallItemParamEnvironment]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call"]]
        action: FunctionShellActionParam
        call_id: str
        environment: FunctionShellCallItemParamEnvironment
        id: str
        status: FunctionShellCallItemStatus
        type: Literal[shell_call]


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal["container_reference"]]
        container_id: str
        type: Literal[container_reference]


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal["local"]]
        skills: list[LocalSkillParam]
        type: Literal[local]


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallItemStatus(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputContent(TypedDict, total=False):
        key "created_by": str
        key "outcome": Required[FunctionShellCallOutputOutcome]
        key "stderr": Required[str]
        key "stdout": Required[str]
        created_by: str
        outcome: FunctionShellCallOutputOutcome
        stderr: str
        stdout: str


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputContentParam(TypedDict, total=False):
        key "outcome": Required[FunctionShellCallOutputOutcomeParam]
        key "stderr": Required[str]
        key "stdout": Required[str]
        outcome: FunctionShellCallOutputOutcomeParam
        stderr: str
        stdout: str


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputExitOutcome(TypedDict, total=False):
        key "exit_code": Required[int]
        key "type": Required[Literal["exit"]]
        exit_code: int
        type: Literal[exit]


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputExitOutcomeParam(TypedDict, total=False):
        key "exit_code": Required[int]
        key "type": Required[Literal["exit"]]
        exit_code: int
        type: Literal[exit]


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "max_output_length": Optional[int]
        key "output": Required[list[FunctionShellCallOutputContentParam]]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call_output"]]
        call_id: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContentParam]
        status: FunctionShellCallItemStatus
        type: Literal[shell_call_output]


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcomeParamType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcomeType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputStatusEnum(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputTimeoutOutcome(TypedDict, total=False):
        key "type": Required[Literal["timeout"]]
        type: Literal[timeout]


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputTimeoutOutcomeParam(TypedDict, total=False):
        key "type": Required[Literal["timeout"]]
        type: Literal[timeout]


    class azure.ai.agentserver.responses.models.FunctionShellCallStatus(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionShellToolParam(TypedDict, total=False):
        key "environment": Optional[FunctionShellToolParamEnvironment]
        key "type": Required[Literal["shell"]]
        environment: FunctionShellToolParamEnvironment
        type: Literal[shell]


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal["container_reference"]]
        container_id: str
        type: Literal[container_reference]


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal["local"]]
        skills: list[LocalSkillParam]
        type: Literal[local]


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentType(TypedDict):


    class azure.ai.agentserver.responses.models.FunctionTool(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Required[Optional[dict[str, Any]]]
        key "strict": Required[Optional[bool]]
        key "type": Required[Literal["function"]]
        defer_loading: bool
        description: str
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[function]


    class azure.ai.agentserver.responses.models.FunctionToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Optional[EmptyModelParam]
        key "strict": Optional[bool]
        key "type": Required[Literal["function"]]
        defer_loading: bool
        description: str
        name: str
        parameters: EmptyModelParam
        strict: bool
        type: Literal[function]


    class azure.ai.agentserver.responses.models.GrammarSyntax1(TypedDict):


    class azure.ai.agentserver.responses.models.HostedAgentDefinition(TypedDict, total=False):
        key "container_protocol_versions": Required[list[ProtocolVersionRecord]]
        key "cpu": Required[str]
        key "image": str
        key "kind": Required[Literal["hosted"]]
        key "memory": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        container_protocol_versions: list[ProtocolVersionRecord]
        cpu: str
        environment_variables: dict[str, str]
        image: str
        kind: Literal[hosted]
        memory: str
        rai_config: RaiConfig
        tools: list[Tool]


    class azure.ai.agentserver.responses.models.HybridSearchOptions(TypedDict, total=False):
        key "embedding_weight": Required[float]
        key "text_weight": Required[float]
        embedding_weight: float
        text_weight: float


    class azure.ai.agentserver.responses.models.ImageDetail(TypedDict):


    class azure.ai.agentserver.responses.models.ImageGenActionEnum(TypedDict):


    class azure.ai.agentserver.responses.models.ImageGenTool(TypedDict, total=False):
        key "action": Literal["generate", "edit", "auto"]
        key "background": Literal["transparent", "opaque", "auto"]
        key "input_fidelity": Optional[Literal["high", "low"]]
        key "input_image_mask": ForwardRef('ImageGenToolInputImageMask', module='types')
        key "model": Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]
        key "moderation": Literal["auto", "low"]
        key "output_compression": int
        key "output_format": Literal["png", "webp", "jpeg"]
        key "partial_images": int
        key "quality": Literal["low", "medium", "high", "auto"]
        key "size": Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]
        key "type": Required[Literal["image_generation"]]
        action: ImageGenActionEnum
        background: Literal[transparent, opaque, auto]
        input_fidelity: InputFidelity
        input_image_mask: ImageGenToolInputImageMask
        model: Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]
        moderation: Literal[auto, low]
        output_compression: int
        output_format: Literal[png, webp, jpeg]
        partial_images: int
        quality: Literal[low, medium, high, auto]
        size: Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]
        type: Literal[image_generation]


    class azure.ai.agentserver.responses.models.ImageGenToolInputImageMask(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        file_id: str
        image_url: str


    class azure.ai.agentserver.responses.models.IncludeEnum(TypedDict):


    class azure.ai.agentserver.responses.models.InlineSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "source": Required[InlineSkillSourceParam]
        key "type": Required[Literal["inline"]]
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[inline]


    class azure.ai.agentserver.responses.models.InlineSkillSourceParam(TypedDict, total=False):
        key "data": Required[str]
        key "media_type": Required[Literal["application/zip"]]
        key "type": Required[Literal["base64"]]
        data: str
        media_type: Literal[application/zip]
        type: Literal[base64]


    class azure.ai.agentserver.responses.models.InputFidelity(TypedDict):


    class azure.ai.agentserver.responses.models.InputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.agentserver.responses.models.InputFileContentParam(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": Optional[str]
        key "file_id": Optional[str]
        key "file_url": Optional[str]
        key "filename": Optional[str]
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.agentserver.responses.models.InputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.agentserver.responses.models.InputImageContentParamAutoParam(TypedDict, total=False):
        key "detail": Optional[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: DetailEnum
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.agentserver.responses.models.InputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.agentserver.responses.models.InputTextContentParam(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.agentserver.responses.models.ItemCodeInterpreterToolCall(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal["code_interpreter_call"]]
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[code_interpreter_call]


    class azure.ai.agentserver.responses.models.ItemComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["computer_call"]]
        action: ComputerAction
        actions: list[ComputerAction]
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[computer_call]


    class azure.ai.agentserver.responses.models.ItemCustomToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "type": Required[Literal["custom_tool_call"]]
        call_id: str
        id: str
        input: str
        name: str
        namespace: str
        type: Literal[custom_tool_call]


    class azure.ai.agentserver.responses.models.ItemCustomToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "type": Required[Literal["custom_tool_call_output"]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[custom_tool_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldAdditionalTools(TypedDict, total=False):
        key "id": Required[str]
        key "role": Required[Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["additional_tools"]]
        id: str
        role: MessageRole
        tools: list[Tool]
        type: Literal[additional_tools]


    class azure.ai.agentserver.responses.models.ItemFieldApplyPatchToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "operation": Required[ApplyPatchFileOperation]
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal["apply_patch_call"]]
        call_id: str
        created_by: str
        id: str
        operation: ApplyPatchFileOperation
        status: ApplyPatchCallStatus
        type: Literal[apply_patch_call]


    class azure.ai.agentserver.responses.models.ItemFieldApplyPatchToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "output": Optional[str]
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal["apply_patch_call_output"]]
        call_id: str
        created_by: str
        id: str
        output: str
        status: ApplyPatchCallOutputStatus
        type: Literal[apply_patch_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldCodeInterpreterToolCall(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal["code_interpreter_call"]]
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[code_interpreter_call]


    class azure.ai.agentserver.responses.models.ItemFieldCompactionBody(TypedDict, total=False):
        key "created_by": str
        key "encrypted_content": Required[str]
        key "id": Required[str]
        key "type": Required[Literal["compaction"]]
        created_by: str
        encrypted_content: str
        id: str
        type: Literal[compaction]


    class azure.ai.agentserver.responses.models.ItemFieldComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["computer_call"]]
        action: ComputerAction
        actions: list[ComputerAction]
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[computer_call]


    class azure.ai.agentserver.responses.models.ItemFieldComputerToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[ComputerScreenshotImage]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["computer_call_output"]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        call_id: str
        id: str
        output: ComputerScreenshotImage
        status: Literal[in_progress, completed, incomplete]
        type: Literal[computer_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldCustomToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "type": Required[Literal["custom_tool_call"]]
        call_id: str
        id: str
        input: str
        name: str
        namespace: str
        type: Literal[custom_tool_call]


    class azure.ai.agentserver.responses.models.ItemFieldCustomToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "type": Required[Literal["custom_tool_call_output"]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[custom_tool_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldFileSearchToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["file_search_call"]]
        id: str
        queries: list[str]
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[file_search_call]


    class azure.ai.agentserver.responses.models.ItemFieldFunctionShellCall(TypedDict, total=False):
        key "action": Required[FunctionShellAction]
        key "call_id": Required[str]
        key "created_by": str
        key "environment": Required[Optional[FunctionShellCallEnvironment]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call"]]
        action: FunctionShellAction
        call_id: str
        created_by: str
        environment: FunctionShellCallEnvironment
        id: str
        status: FunctionShellCallStatus
        type: Literal[shell_call]


    class azure.ai.agentserver.responses.models.ItemFieldFunctionShellCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "max_output_length": Required[Optional[int]]
        key "output": Required[list[FunctionShellCallOutputContent]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call_output"]]
        call_id: str
        created_by: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        status: FunctionShellCallOutputStatusEnum
        type: Literal[shell_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldFunctionToolCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call"]]
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call]


    class azure.ai.agentserver.responses.models.ItemFieldFunctionToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call_output"]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldImageGenToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal["image_generation_call"]]
        id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[image_generation_call]


    class azure.ai.agentserver.responses.models.ItemFieldLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "call_id": Required[str]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call"]]
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call]


    class azure.ai.agentserver.responses.models.ItemFieldLocalShellToolCallOutput(TypedDict, total=False):
        key "id": Required[str]
        key "output": Required[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call_output"]]
        id: str
        output: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call_output]


    class azure.ai.agentserver.responses.models.ItemFieldMcpApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal["mcp_approval_request"]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[mcp_approval_request]


    class azure.ai.agentserver.responses.models.ItemFieldMcpApprovalResponseResource(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "type": Required[Literal["mcp_approval_response"]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[mcp_approval_response]


    class azure.ai.agentserver.responses.models.ItemFieldMcpListTools(TypedDict, total=False):
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal["mcp_list_tools"]]
        error: RealtimeMCPError
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[mcp_list_tools]


    class azure.ai.agentserver.responses.models.ItemFieldMcpToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal["mcp_call"]]
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[mcp_call]


    class azure.ai.agentserver.responses.models.ItemFieldMessage(TypedDict, total=False):
        key "content": Required[list[MessageContent]]
        key "id": str
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["message"]]
        content: list[MessageContent]
        id: str
        phase: MessagePhase
        role: MessageRole
        status: MessageStatus
        type: Literal[message]


    class azure.ai.agentserver.responses.models.ItemFieldReasoningItem(TypedDict, total=False):
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal["reasoning"]]
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[reasoning]


    class azure.ai.agentserver.responses.models.ItemFieldToolSearchCall(TypedDict, total=False):
        key "arguments": Required[Any]
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["tool_search_call"]]
        arguments: Any
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallStatus
        type: Literal[tool_search_call]


    class azure.ai.agentserver.responses.models.ItemFieldToolSearchOutput(TypedDict, total=False):
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["tool_search_output"]]
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallOutputStatusEnum
        tools: list[Tool]
        type: Literal[tool_search_output]


    class azure.ai.agentserver.responses.models.ItemFieldType(TypedDict):


    class azure.ai.agentserver.responses.models.ItemFieldWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["web_search_call"]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal[in_progress, searching, completed, failed, incomplete]
        type: Literal[web_search_call]


    class azure.ai.agentserver.responses.models.ItemFileSearchToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["file_search_call"]]
        id: str
        queries: list[str]
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[file_search_call]


    class azure.ai.agentserver.responses.models.ItemFunctionToolCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call"]]
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call]


    class azure.ai.agentserver.responses.models.ItemImageGenToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal["image_generation_call"]]
        id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[image_generation_call]


    class azure.ai.agentserver.responses.models.ItemLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "call_id": Required[str]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call"]]
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call]


    class azure.ai.agentserver.responses.models.ItemLocalShellToolCallOutput(TypedDict, total=False):
        key "id": Required[str]
        key "output": Required[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call_output"]]
        id: str
        output: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call_output]


    class azure.ai.agentserver.responses.models.ItemMcpApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal["mcp_approval_request"]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[mcp_approval_request]


    class azure.ai.agentserver.responses.models.ItemMcpListTools(TypedDict, total=False):
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal["mcp_list_tools"]]
        error: RealtimeMCPError
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[mcp_list_tools]


    class azure.ai.agentserver.responses.models.ItemMcpToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal["mcp_call"]]
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[mcp_call]


    class azure.ai.agentserver.responses.models.ItemMessage(TypedDict, total=False):
        key "content": Required[Union[str, list[MessageContent]]]
        key "id": str
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["message"]]
        content: Union[str, list[MessageContent]]
        id: str
        phase: MessagePhase
        role: MessageRole
        status: MessageStatus
        type: Literal[message]


    class azure.ai.agentserver.responses.models.ItemOutputMessage(TypedDict, total=False):
        key "content": Required[list[OutputMessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[Literal["assistant"]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["output_message"]]
        content: list[OutputMessageContent]
        id: str
        phase: MessagePhase
        role: Literal[assistant]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[output_message]


    class azure.ai.agentserver.responses.models.ItemReasoningItem(TypedDict, total=False):
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal["reasoning"]]
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[reasoning]


    class azure.ai.agentserver.responses.models.ItemReferenceParam(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Literal["item_reference"]]
        id: str
        type: Literal[item_reference]


    class azure.ai.agentserver.responses.models.ItemType(TypedDict):


    class azure.ai.agentserver.responses.models.ItemWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["web_search_call"]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal[in_progress, searching, completed, failed, incomplete]
        type: Literal[web_search_call]


    class azure.ai.agentserver.responses.models.KeyPressAction(TypedDict, total=False):
        key "keys": Required[list[str]]
        key "type": Required[Literal["keypress"]]
        keys_property: list[str]
        type: Literal[keypress]


    class azure.ai.agentserver.responses.models.LocalEnvironmentResource(TypedDict, total=False):
        key "type": Required[Literal["local"]]
        type: Literal[local]


    class azure.ai.agentserver.responses.models.LocalShellExecAction(TypedDict, total=False):
        key "command": Required[list[str]]
        key "env": Required[dict[str, str]]
        key "timeout_ms": Optional[int]
        key "type": Required[Literal["exec"]]
        key "user": Optional[str]
        key "working_directory": Optional[str]
        command: list[str]
        env: dict[str, str]
        timeout_ms: int
        type: Literal[exec]
        user: str
        working_directory: str


    class azure.ai.agentserver.responses.models.LocalShellToolParam(TypedDict, total=False):
        key "type": Required[Literal["local_shell"]]
        type: Literal[local_shell]


    class azure.ai.agentserver.responses.models.LocalSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "path": Required[str]
        description: str
        name: str
        path: str


    class azure.ai.agentserver.responses.models.LogProb(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        key "top_logprobs": Required[list[TopLogProb]]
        bytes: list[int]
        logprob: float
        token: str
        top_logprobs: list[TopLogProb]


    class azure.ai.agentserver.responses.models.MCPApprovalResponse(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Optional[str]
        key "reason": Optional[str]
        key "type": Required[Literal["mcp_approval_response"]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[mcp_approval_response]


    class azure.ai.agentserver.responses.models.MCPListToolsTool(TypedDict, total=False):
        key "annotations": Optional[MCPListToolsToolAnnotations]
        key "description": Optional[str]
        key "input_schema": Required[MCPListToolsToolInputSchema]
        key "name": Required[str]
        annotations: MCPListToolsToolAnnotations
        description: str
        input_schema: MCPListToolsToolInputSchema
        name: str


    class azure.ai.agentserver.responses.models.MCPListToolsToolAnnotations(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.MCPListToolsToolInputSchema(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.MCPTool(TypedDict, total=False):
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "connector_id": Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]
        key "defer_loading": bool
        key "headers": Optional[dict[str, str]]
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "tunnel_id": str
        key "type": Required[Literal["mcp"]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        connector_id: Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams,
        defer_loading: bool
        headers: dict[str, str]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        server_description: str
        server_label: str
        server_url: str
        tunnel_id: str
        type: Literal[mcp]


    class azure.ai.agentserver.responses.models.MCPToolCallStatus(TypedDict):


    class azure.ai.agentserver.responses.models.MCPToolFilter(TypedDict, total=False):
        key "read_only": bool
        read_only: bool
        tool_names: list[str]


    class azure.ai.agentserver.responses.models.MCPToolRequireApproval(TypedDict, total=False):
        key "always": ForwardRef('MCPToolFilter', module='types')
        key "never": ForwardRef('MCPToolFilter', module='types')
        always: MCPToolFilter
        never: MCPToolFilter


    class azure.ai.agentserver.responses.models.MemoryItemKind(TypedDict):


    class azure.ai.agentserver.responses.models.MemoryOperation(TypedDict, total=False):
        key "kind": Required[Literal["create", "update", "delete"]]
        key "memory_item": Required[MemoryItem]
        kind: MemoryOperationKind
        memory_item: MemoryItem


    class azure.ai.agentserver.responses.models.MemoryOperationKind(TypedDict):


    class azure.ai.agentserver.responses.models.MemorySearchItem(TypedDict, total=False):
        key "memory_item": Required[MemoryItem]
        memory_item: MemoryItem


    class azure.ai.agentserver.responses.models.MemorySearchOptions(TypedDict, total=False):
        key "max_memories": int
        max_memories: int


    class azure.ai.agentserver.responses.models.MemorySearchPreviewTool(TypedDict, total=False):
        key "memory_store_name": Required[str]
        key "scope": Required[str]
        key "search_options": ForwardRef('MemorySearchOptions', module='types')
        key "type": Required[Literal["memory_search_preview"]]
        key "update_delay": int
        memory_store_name: str
        scope: str
        search_options: MemorySearchOptions
        type: Literal[memory_search_preview]
        update_delay: int


    class azure.ai.agentserver.responses.models.MemorySearchToolCallItemParam(TypedDict, total=False):
        key "results": Optional[list[MemorySearchItem]]
        key "type": Required[Literal["memory_search_call"]]
        results: list[MemorySearchItem]
        type: Literal[memory_search_call]


    class azure.ai.agentserver.responses.models.MemorySearchToolCallItemResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": str
        key "response_id": str
        key "results": Optional[list[MemorySearchItem]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["memory_search_call"]]
        agent_reference: AgentReference
        id: str
        response_id: str
        results: list[MemorySearchItem]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[memory_search_call]


    class azure.ai.agentserver.responses.models.MemoryStoreDefaultDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal["default"]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[default]
        options: MemoryStoreDefaultOptions


    class azure.ai.agentserver.responses.models.MemoryStoreDefaultOptions(TypedDict, total=False):
        key "chat_summary_enabled": Required[bool]
        key "user_profile_details": str
        key "user_profile_enabled": Required[bool]
        chat_summary_enabled: bool
        user_profile_details: str
        user_profile_enabled: bool


    class azure.ai.agentserver.responses.models.MemoryStoreDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal["default"]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[default]
        options: MemoryStoreDefaultOptions


    class azure.ai.agentserver.responses.models.MemoryStoreDeleteScopeResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal["deleted"]]
        key "scope": Required[str]
        deleted: bool
        name: str
        object: Literal[deleted]
        scope: str


    class azure.ai.agentserver.responses.models.MemoryStoreKind(TypedDict):


    class azure.ai.agentserver.responses.models.MemoryStoreObject(TypedDict, total=False):
        key "created_at": Required[int]
        key "definition": Required[MemoryStoreDefinition]
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        key "object": Required[Literal["memory_store"]]
        key "updated_at": Required[int]
        created_at: int
        definition: MemoryStoreDefinition
        description: str
        id: str
        metadata: dict[str, str]
        name: str
        object: Literal[memory_store]
        updated_at: int


    class azure.ai.agentserver.responses.models.MemoryStoreObjectType(TypedDict):


    class azure.ai.agentserver.responses.models.MemoryStoreOperationUsage(TypedDict, total=False):
        key "embedding_tokens": Required[int]
        key "input_tokens": Required[int]
        key "input_tokens_details": Required[ResponseUsageInputTokensDetails]
        key "output_tokens": Required[int]
        key "output_tokens_details": Required[ResponseUsageOutputTokensDetails]
        key "total_tokens": Required[int]
        embedding_tokens: int
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int


    class azure.ai.agentserver.responses.models.MemoryStoreSearchResponse(TypedDict, total=False):
        key "memories": Required[list[MemorySearchItem]]
        key "search_id": Required[str]
        key "usage": Required[MemoryStoreOperationUsage]
        memories: list[MemorySearchItem]
        search_id: str
        usage: MemoryStoreOperationUsage


    class azure.ai.agentserver.responses.models.MemoryStoreUpdateCompletedResult(TypedDict, total=False):
        key "memory_operations": Required[list[MemoryOperation]]
        key "usage": Required[MemoryStoreOperationUsage]
        memory_operations: list[MemoryOperation]
        usage: MemoryStoreOperationUsage


    class azure.ai.agentserver.responses.models.MemoryStoreUpdateResponse(TypedDict, total=False):
        key "error": ForwardRef('Error', module='types')
        key "result": ForwardRef('MemoryStoreUpdateCompletedResult', module='types')
        key "status": Required[Literal["queued", "in_progress", "completed", "failed", "superseded"]]
        key "superseded_by": str
        key "update_id": Required[str]
        error: Error
        result: MemoryStoreUpdateCompletedResult
        status: MemoryStoreUpdateStatus
        superseded_by: str
        update_id: str


    class azure.ai.agentserver.responses.models.MemoryStoreUpdateStatus(TypedDict):


    class azure.ai.agentserver.responses.models.MessageContentInputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.agentserver.responses.models.MessageContentInputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.agentserver.responses.models.MessageContentInputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.agentserver.responses.models.MessageContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal["output_text"]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[output_text]


    class azure.ai.agentserver.responses.models.MessageContentReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["reasoning_text"]]
        text: str
        type: Literal[reasoning_text]


    class azure.ai.agentserver.responses.models.MessageContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal["refusal"]]
        refusal: str
        type: Literal[refusal]


    class azure.ai.agentserver.responses.models.MessageContentType(TypedDict):


    class azure.ai.agentserver.responses.models.MessagePhase(TypedDict):


    class azure.ai.agentserver.responses.models.MessageRole(TypedDict):


    class azure.ai.agentserver.responses.models.MessageStatus(TypedDict):


    class azure.ai.agentserver.responses.models.Metadata(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.MicrosoftFabricPreviewTool(TypedDict, total=False):
        key "fabric_dataagent_preview": Required[FabricDataAgentToolParameters]
        key "type": Required[Literal["fabric_dataagent_preview"]]
        fabric_dataagent_preview: FabricDataAgentToolParameters
        type: Literal[fabric_dataagent_preview]


    class azure.ai.agentserver.responses.models.ModelIdsCompaction(TypedDict):


    class azure.ai.agentserver.responses.models.Moderation(TypedDict, total=False):
        key "input": Required[ModerationEntry]
        key "output": Required[ModerationEntry]
        input: ModerationEntry
        output: ModerationEntry


    class azure.ai.agentserver.responses.models.ModerationEntryType(TypedDict):


    class azure.ai.agentserver.responses.models.ModerationErrorBody(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        key "type": Required[Literal["error"]]
        code: str
        message: str
        type: Literal[error]


    class azure.ai.agentserver.responses.models.ModerationInputType(TypedDict):


    class azure.ai.agentserver.responses.models.ModerationParam(TypedDict, total=False):
        key "model": Required[str]
        model: str


    class azure.ai.agentserver.responses.models.ModerationResultBody(TypedDict, total=False):
        key "categories": Required[dict[str, bool]]
        key "category_applied_input_types": Required[dict[str, list[Literal["text", "image"]]]]
        key "category_scores": Required[dict[str, float]]
        key "flagged": Required[bool]
        key "model": Required[str]
        key "type": Required[Literal["moderation_result"]]
        categories: dict[str, bool]
        category_applied_input_types: dict[str, list[ModerationInputType]]
        category_scores: dict[str, float]
        flagged: bool
        model: str
        type: Literal[moderation_result]


    class azure.ai.agentserver.responses.models.MoveParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "type": Required[Literal["move"]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        type: Literal[move]
        x: int
        y: int


    class azure.ai.agentserver.responses.models.NamespaceToolParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "tools": Required[list[Union[FunctionToolParam, CustomToolParam]]]
        key "type": Required[Literal["namespace"]]
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[namespace]


    class azure.ai.agentserver.responses.models.OAuthConsentRequestOutputItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "consent_link": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal["oauth_consent_request"]]
        agent_reference: AgentReference
        consent_link: str
        id: str
        response_id: str
        server_label: str
        type: Literal[oauth_consent_request]


    class azure.ai.agentserver.responses.models.OpenApiAnonymousAuthDetails(TypedDict, total=False):
        key "type": Required[Literal["anonymous"]]
        type: Literal[anonymous]


    class azure.ai.agentserver.responses.models.OpenApiAuthType(TypedDict):


    class azure.ai.agentserver.responses.models.OpenApiFunctionDefinition(TypedDict, total=False):
        key "auth": Required[OpenApiAuthDetails]
        key "description": str
        key "name": Required[str]
        key "spec": Required[dict[str, Any]]
        auth: OpenApiAuthDetails
        default_params: list[str]
        description: str
        functions: list[OpenApiFunctionDefinitionFunction]
        name: str
        spec: dict[str, Any]


    class azure.ai.agentserver.responses.models.OpenApiFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.agentserver.responses.models.OpenApiManagedAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiManagedSecurityScheme]
        key "type": Required[Literal["managed_identity"]]
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[managed_identity]


    class azure.ai.agentserver.responses.models.OpenApiManagedSecurityScheme(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.ai.agentserver.responses.models.OpenApiProjectConnectionAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiProjectConnectionSecurityScheme]
        key "type": Required[Literal["project_connection"]]
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[project_connection]


    class azure.ai.agentserver.responses.models.OpenApiProjectConnectionSecurityScheme(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.agentserver.responses.models.OpenApiTool(TypedDict, total=False):
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal["openapi"]]
        openapi: OpenApiFunctionDefinition
        type: Literal[openapi]


    class azure.ai.agentserver.responses.models.OpenApiToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["openapi_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[openapi_call]


    class azure.ai.agentserver.responses.models.OpenApiToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["openapi_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[openapi_call_output]


    class azure.ai.agentserver.responses.models.OutputContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal["output_text"]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[output_text]


    class azure.ai.agentserver.responses.models.OutputContentReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["reasoning_text"]]
        text: str
        type: Literal[reasoning_text]


    class azure.ai.agentserver.responses.models.OutputContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal["refusal"]]
        refusal: str
        type: Literal[refusal]


    class azure.ai.agentserver.responses.models.OutputContentType(TypedDict):


    class azure.ai.agentserver.responses.models.OutputItemAdditionalTools(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "role": Required[Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["additional_tools"]]
        agent_reference: AgentReference
        id: str
        response_id: str
        role: MessageRole
        tools: list[Tool]
        type: Literal[additional_tools]


    class azure.ai.agentserver.responses.models.OutputItemApplyPatchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "operation": Required[ApplyPatchFileOperation]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal["apply_patch_call"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        operation: ApplyPatchFileOperation
        response_id: str
        status: ApplyPatchCallStatus
        type: Literal[apply_patch_call]


    class azure.ai.agentserver.responses.models.OutputItemApplyPatchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal["apply_patch_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: str
        response_id: str
        status: ApplyPatchCallOutputStatus
        type: Literal[apply_patch_call_output]


    class azure.ai.agentserver.responses.models.OutputItemCodeInterpreterToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal["code_interpreter_call"]]
        agent_reference: AgentReference
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        response_id: str
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[code_interpreter_call]


    class azure.ai.agentserver.responses.models.OutputItemCompactionBody(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "encrypted_content": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "type": Required[Literal["compaction"]]
        agent_reference: AgentReference
        encrypted_content: str
        id: str
        response_id: str
        type: Literal[compaction]


    class azure.ai.agentserver.responses.models.OutputItemComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["computer_call"]]
        action: ComputerAction
        actions: list[ComputerAction]
        agent_reference: AgentReference
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[computer_call]


    class azure.ai.agentserver.responses.models.OutputItemComputerToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[ComputerScreenshotImage]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["computer_call_output"]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ComputerScreenshotImage
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[computer_call_output]


    class azure.ai.agentserver.responses.models.OutputItemFileSearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "response_id": str
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["file_search_call"]]
        agent_reference: AgentReference
        id: str
        queries: list[str]
        response_id: str
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[file_search_call]


    class azure.ai.agentserver.responses.models.OutputItemFunctionShellCall(TypedDict, total=False):
        key "action": Required[FunctionShellAction]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "environment": Required[Optional[FunctionShellCallEnvironment]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call"]]
        action: FunctionShellAction
        agent_reference: AgentReference
        call_id: str
        environment: FunctionShellCallEnvironment
        id: str
        response_id: str
        status: FunctionShellCallStatus
        type: Literal[shell_call]


    class azure.ai.agentserver.responses.models.OutputItemFunctionShellCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "max_output_length": Required[Optional[int]]
        key "output": Required[list[FunctionShellCallOutputContent]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["shell_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        response_id: str
        status: FunctionShellCallOutputStatusEnum
        type: Literal[shell_call_output]


    class azure.ai.agentserver.responses.models.OutputItemFunctionToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call]


    class azure.ai.agentserver.responses.models.OutputItemFunctionToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call_output]


    class azure.ai.agentserver.responses.models.OutputItemImageGenToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal["image_generation_call"]]
        agent_reference: AgentReference
        id: str
        response_id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[image_generation_call]


    class azure.ai.agentserver.responses.models.OutputItemLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call"]]
        action: LocalShellExecAction
        agent_reference: AgentReference
        call_id: str
        id: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call]


    class azure.ai.agentserver.responses.models.OutputItemLocalShellToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "output": Required[str]
        key "response_id": str
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["local_shell_call_output"]]
        agent_reference: AgentReference
        id: str
        output: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[local_shell_call_output]


    class azure.ai.agentserver.responses.models.OutputItemMcpApprovalRequest(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal["mcp_approval_request"]]
        agent_reference: AgentReference
        arguments: str
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[mcp_approval_request]


    class azure.ai.agentserver.responses.models.OutputItemMcpApprovalResponseResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "response_id": str
        key "type": Required[Literal["mcp_approval_response"]]
        agent_reference: AgentReference
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        response_id: str
        type: Literal[mcp_approval_response]


    class azure.ai.agentserver.responses.models.OutputItemMcpListTools(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal["mcp_list_tools"]]
        agent_reference: AgentReference
        error: RealtimeMCPError
        id: str
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[mcp_list_tools]


    class azure.ai.agentserver.responses.models.OutputItemMcpToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal["mcp_call"]]
        agent_reference: AgentReference
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        response_id: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[mcp_call]


    class azure.ai.agentserver.responses.models.OutputItemMessage(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "content": Required[list[MessageContent]]
        key "id": str
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "response_id": str
        key "role": Required[Literal["unknown", "user", "assistant", "system", "critic", "discriminator", "developer", "tool"]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["message"]]
        agent_reference: AgentReference
        content: list[MessageContent]
        id: str
        phase: MessagePhase
        response_id: str
        role: MessageRole
        status: MessageStatus
        type: Literal[message]


    class azure.ai.agentserver.responses.models.OutputItemOutputMessage(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "content": Required[list[OutputMessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "response_id": str
        key "role": Required[Literal["assistant"]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["output_message"]]
        agent_reference: AgentReference
        content: list[OutputMessageContent]
        id: str
        phase: MessagePhase
        response_id: str
        role: Literal[assistant]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[output_message]


    class azure.ai.agentserver.responses.models.OutputItemReasoningItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal["reasoning"]]
        agent_reference: AgentReference
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[reasoning]


    class azure.ai.agentserver.responses.models.OutputItemReference(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": str
        key "response_id": str
        key "type": Required[Literal["item_reference"]]
        agent_reference: AgentReference
        id: str
        response_id: str
        type: Literal[item_reference]


    class azure.ai.agentserver.responses.models.OutputItemRemoteToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "label": str
        key "name": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["remote_function_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        label: str
        name: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[remote_function_call]


    class azure.ai.agentserver.responses.models.OutputItemRemoteToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "label": str
        key "name": str
        key "output": Any
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["remote_function_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        label: str
        name: str
        output: Any
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[remote_function_call_output]


    class azure.ai.agentserver.responses.models.OutputItemToolSearchCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[Any]
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["tool_search_call"]]
        agent_reference: AgentReference
        arguments: Any
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        response_id: str
        status: FunctionCallStatus
        type: Literal[tool_search_call]


    class azure.ai.agentserver.responses.models.OutputItemToolSearchOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["tool_search_output"]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        response_id: str
        status: FunctionCallOutputStatusEnum
        tools: list[Tool]
        type: Literal[tool_search_output]


    class azure.ai.agentserver.responses.models.OutputItemType(TypedDict):


    class azure.ai.agentserver.responses.models.OutputItemWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["web_search_call"]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        agent_reference: AgentReference
        id: str
        response_id: str
        status: Literal[in_progress, searching, completed, failed, incomplete]
        type: Literal[web_search_call]


    class azure.ai.agentserver.responses.models.OutputMessageContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal["output_text"]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[output_text]


    class azure.ai.agentserver.responses.models.OutputMessageContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal["refusal"]]
        refusal: str
        type: Literal[refusal]


    class azure.ai.agentserver.responses.models.OutputMessageContentType(TypedDict):


    class azure.ai.agentserver.responses.models.PageOrder(TypedDict):


    class azure.ai.agentserver.responses.models.Prompt(TypedDict, total=False):
        key "id": Required[str]
        key "variables": Optional[ResponsePromptVariables]
        key "version": Optional[str]
        id: str
        variables: ResponsePromptVariables
        version: str


    class azure.ai.agentserver.responses.models.PromptAgentDefinition(TypedDict, total=False):
        key "instructions": Optional[str]
        key "kind": Required[Literal["prompt"]]
        key "model": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "reasoning": Optional[Reasoning]
        key "temperature": Optional[float]
        key "text": ForwardRef('PromptAgentDefinitionTextOptions', module='types')
        key "tool_choice": Union[str, ToolChoiceParam]
        key "top_p": Optional[float]
        instructions: str
        kind: Literal[prompt]
        model: str
        rai_config: RaiConfig
        reasoning: Reasoning
        structured_inputs: dict[str, StructuredInputDefinition]
        temperature: float
        text: PromptAgentDefinitionTextOptions
        tool_choice: Union[str, ToolChoiceParam]
        tools: list[Tool]
        top_p: float


    class azure.ai.agentserver.responses.models.PromptAgentDefinitionTextOptions(TypedDict, total=False):
        key "format": ForwardRef('TextResponseFormatConfiguration', module='types')
        format: TextResponseFormatConfiguration


    class azure.ai.agentserver.responses.models.PromptCacheRetentionEnum(TypedDict):


    class azure.ai.agentserver.responses.models.ProtocolVersionRecord(TypedDict, total=False):
        key "protocol": Required[Literal["activity_protocol", "responses"]]
        key "version": Required[str]
        protocol: AgentProtocol
        version: str


    class azure.ai.agentserver.responses.models.RaiConfig(TypedDict, total=False):
        key "rai_policy_name": Required[str]
        rai_policy_name: str


    class azure.ai.agentserver.responses.models.RankerVersionType(TypedDict):


    class azure.ai.agentserver.responses.models.RankingOptions(TypedDict, total=False):
        key "hybrid_search": ForwardRef('HybridSearchOptions', module='types')
        key "ranker": Literal["auto", "default-2024-11-15"]
        key "score_threshold": float
        hybrid_search: HybridSearchOptions
        ranker: RankerVersionType
        score_threshold: float


    class azure.ai.agentserver.responses.models.RealtimeMCPHTTPError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal["http_error"]]
        code: int
        message: str
        type: Literal[http_error]


    class azure.ai.agentserver.responses.models.RealtimeMCPProtocolError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal["protocol_error"]]
        code: int
        message: str
        type: Literal[protocol_error]


    class azure.ai.agentserver.responses.models.RealtimeMCPToolExecutionError(TypedDict, total=False):
        key "message": Required[str]
        key "type": Required[Literal["tool_execution_error"]]
        message: str
        type: Literal[tool_execution_error]


    class azure.ai.agentserver.responses.models.RealtimeMcpErrorType(TypedDict):


    class azure.ai.agentserver.responses.models.Reasoning(TypedDict, total=False):
        key "context": Optional[Literal["auto", "current_turn", "all_turns"]]
        key "effort": Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh"]]
        key "generate_summary": Optional[Literal["auto", "concise", "detailed"]]
        key "summary": Optional[Literal["auto", "concise", "detailed"]]
        context: Literal[auto, current_turn, all_turns]
        effort: ReasoningEffort
        generate_summary: Literal[auto, concise, detailed]
        summary: Literal[auto, concise, detailed]


    class azure.ai.agentserver.responses.models.ReasoningEffort(TypedDict):


    class azure.ai.agentserver.responses.models.ReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["reasoning_text"]]
        text: str
        type: Literal[reasoning_text]


    class azure.ai.agentserver.responses.models.RemoteTool(TypedDict, total=False):
        key "type": Required[Literal["remote_tool"]]
        tool_arguments: list[RemoteToolArgument]
        type: Literal[remote_tool]


    class azure.ai.agentserver.responses.models.RemoteToolArgument(TypedDict, total=False):
        key "arguments": ForwardRef('RemoteToolArgumentArguments', module='types')
        key "description": str
        key "name": str
        arguments: RemoteToolArgumentArguments
        description: str
        name: str


    class azure.ai.agentserver.responses.models.RemoteToolArgumentArguments(TypedDict, total=False):
        key "connection_id": str
        connection_id: str
        knowledge_sources: list[RemoteToolArgumentArgumentsKnowledgeSource]


    class azure.ai.agentserver.responses.models.RemoteToolArgumentArgumentsKnowledgeSource(TypedDict, total=False):
        key "connection_id": str
        key "index_details": ForwardRef('RemoteToolArgumentArgumentsKnowledgeSourceIndexDetails', module='types')
        key "index_id": str
        connection_id: str
        index_details: RemoteToolArgumentArgumentsKnowledgeSourceIndexDetails
        index_id: str
        query_parameters: dict[str, Any]


    class azure.ai.agentserver.responses.models.RemoteToolArgumentArgumentsKnowledgeSourceIndexDetails(TypedDict, total=False):
        key "index_configuration": ForwardRef('RemoteToolArgumentArgumentsKnowledgeSourceIndexDetailsIndexConfiguration', module='types')
        index_configuration: RemoteToolArgumentArgumentsKnowledgeSourceIndexDetailsIndexConfiguration


    class azure.ai.agentserver.responses.models.RemoteToolArgumentArgumentsKnowledgeSourceIndexDetailsIndexConfiguration(TypedDict, total=False):
        key "index_connection_id": str
        key "index_name": str
        index_connection_id: str
        index_name: str


    class azure.ai.agentserver.responses.models.RemoteToolChoiceParam(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["remote_tool"]]
        name: str
        type: Literal[remote_tool]


    class azure.ai.agentserver.responses.models.ResponseAudioDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseAudioDoneEvent(TypedDict, total=False):
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseAudioTranscriptDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseAudioTranscriptDoneEvent(TypedDict, total=False):
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCodeDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCodeDoneEvent(TypedDict, total=False):
        key "code": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        code: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallInterpretingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["interpreting"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[interpreting]


    class azure.ai.agentserver.responses.models.ResponseCompletedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseContentPartAddedEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[OutputContent]
        key "sequence_number": Required[int]
        key "type": Required[Literal["added"]]
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[added]


    class azure.ai.agentserver.responses.models.ResponseContentPartDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[OutputContent]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseCreatedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["created"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[created]


    class azure.ai.agentserver.responses.models.ResponseCustomToolCallInputDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseCustomToolCallInputDoneEvent(TypedDict, total=False):
        key "input": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        input: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseError(TypedDict, total=False):
        key "code": Required[Literal["server_error", "rate_limit_exceeded", "invalid_prompt", "vector_store_timeout", "invalid_image", "invalid_image_format", "invalid_base64_image", "invalid_image_url", "image_too_large", "image_too_small", "image_parse_error", "image_content_policy_violation", "invalid_image_mode", "image_file_too_large", "unsupported_image_media_type", "empty_image_file", "failed_to_download_image", "image_file_not_found"]]
        key "message": Required[str]
        code: ResponseErrorCode
        message: str


    class azure.ai.agentserver.responses.models.ResponseErrorCode(TypedDict):


    class azure.ai.agentserver.responses.models.ResponseErrorEvent(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Required[Optional[str]]
        key "sequence_number": Required[int]
        key "type": Required[Literal["error"]]
        code: str
        message: str
        param: str
        sequence_number: int
        type: Literal[error]


    class azure.ai.agentserver.responses.models.ResponseFailedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["failed"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[failed]


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallSearchingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["searching"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[searching]


    class azure.ai.agentserver.responses.models.ResponseFormatJsonSchemaSchema(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.ResponseFunctionCallArgumentsDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseFunctionCallArgumentsDoneEvent(TypedDict, total=False):
        key "arguments": Required[str]
        key "item_id": Required[str]
        key "name": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        arguments: str
        item_id: str
        name: str
        output_index: int
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseImageGenCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseImageGenCallGeneratingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["generating"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[generating]


    class azure.ai.agentserver.responses.models.ResponseImageGenCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseImageGenCallPartialImageEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "partial_image_b64": Required[str]
        key "partial_image_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["partial_image"]]
        item_id: str
        output_index: int
        partial_image_b64: str
        partial_image_index: int
        sequence_number: int
        type: Literal[partial_image]


    class azure.ai.agentserver.responses.models.ResponseInProgressEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseIncompleteDetails(TypedDict, total=False):
        key "reason": Literal["max_output_tokens", "content_filter"]
        reason: Literal[max_output_tokens, content_filter]


    class azure.ai.agentserver.responses.models.ResponseIncompleteEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["incomplete"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[incomplete]


    class azure.ai.agentserver.responses.models.ResponseLogProb(TypedDict, total=False):
        key "logprob": Required[float]
        key "token": Required[str]
        logprob: float
        token: str
        top_logprobs: list[ResponseLogProbTopLogprobs]


    class azure.ai.agentserver.responses.models.ResponseLogProbTopLogprobs(TypedDict, total=False):
        key "logprob": float
        key "token": str
        logprob: float
        token: str


    class azure.ai.agentserver.responses.models.ResponseMCPCallArgumentsDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseMCPCallArgumentsDoneEvent(TypedDict, total=False):
        key "arguments": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        arguments: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseMCPCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseMCPCallFailedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["failed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[failed]


    class azure.ai.agentserver.responses.models.ResponseMCPCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsFailedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["failed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[failed]


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseObject(TypedDict, total=False):
        key "agent_reference": Required[Optional[AgentReference]]
        key "background": Optional[bool]
        key "completed_at": Optional[int]
        key "conversation": Optional[ConversationReference]
        key "created_at": Required[int]
        key "error": Required[Optional[ResponseError]]
        key "id": Required[str]
        key "incomplete_details": Required[Optional[ResponseIncompleteDetails]]
        key "instructions": Required[Optional[Union[str, list[Item]]]]
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[Moderation]
        key "object": Required[Literal["response"]]
        key "output": Required[list[OutputItem]]
        key "output_text": Optional[str]
        key "parallel_tool_calls": Required[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "reasoning": Optional[Reasoning]
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "status": Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "usage": ForwardRef('ResponseUsage', module='types')
        key "user": str
        agent_reference: AgentReference
        background: bool
        completed_at: int
        conversation: ConversationReference
        created_at: int
        error: ResponseError
        id: str
        incomplete_details: ResponseIncompleteDetails
        instructions: Union[str, list[Item]]
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: Moderation
        object: Literal[response]
        output: list[OutputItem]
        output_text: str
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        reasoning: Reasoning
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        status: Literal[completed, failed, in_progress, cancelled, queued, incomplete]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        usage: ResponseUsage
        user: str


    class azure.ai.agentserver.responses.models.ResponseObjectType(TypedDict):


    class azure.ai.agentserver.responses.models.ResponseOutputItemAddedEvent(TypedDict, total=False):
        key "item": Required[OutputItem]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["added"]]
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[added]


    class azure.ai.agentserver.responses.models.ResponseOutputItemDoneEvent(TypedDict, total=False):
        key "item": Required[OutputItem]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseOutputTextAnnotationAddedEvent(TypedDict, total=False):
        key "annotation": Required[Annotation]
        key "annotation_index": Required[int]
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["added"]]
        annotation: Annotation
        annotation_index: int
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[added]


    class azure.ai.agentserver.responses.models.ResponsePromptVariables(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.ResponseQueuedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal["queued"]]
        response: ResponseObject
        sequence_number: int
        type: Literal[queued]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartAddedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[ResponseReasoningSummaryPartAddedEventPart]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal["added"]]
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartAddedEventPart
        sequence_number: int
        summary_index: int
        type: Literal[added]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartAddedEventPart(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["summary_text"]]
        text: str
        type: Literal[summary_text]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartDoneEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[ResponseReasoningSummaryPartDoneEventPart]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal["done"]]
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartDoneEventPart
        sequence_number: int
        summary_index: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartDoneEventPart(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["summary_text"]]
        text: str
        type: Literal[summary_text]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryTextDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal["delta"]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryTextDoneEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "text": Required[str]
        key "type": Required[Literal["done"]]
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        text: str
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseReasoningTextDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseReasoningTextDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "text": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        text: str
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseRefusalDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseRefusalDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "refusal": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal["done"]]
        content_index: int
        item_id: str
        output_index: int
        refusal: str
        sequence_number: int
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseStreamEventType(TypedDict):


    class azure.ai.agentserver.responses.models.ResponseStreamOptions(TypedDict, total=False):
        key "include_obfuscation": bool
        include_obfuscation: bool


    class azure.ai.agentserver.responses.models.ResponseTextDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "logprobs": Required[list[ResponseLogProb]]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["delta"]]
        content_index: int
        delta: str
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        type: Literal[delta]


    class azure.ai.agentserver.responses.models.ResponseTextDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "logprobs": Required[list[ResponseLogProb]]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "text": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        text: str
        type: Literal[done]


    class azure.ai.agentserver.responses.models.ResponseTextParam(TypedDict, total=False):
        key "format": ForwardRef('TextResponseFormatConfiguration', module='types')
        key "verbosity": Optional[Literal["low", "medium", "high"]]
        format: TextResponseFormatConfiguration
        verbosity: Literal[low, medium, high]


    class azure.ai.agentserver.responses.models.ResponseUsage(TypedDict, total=False):
        key "input_tokens": Required[int]
        key "input_tokens_details": Required[ResponseUsageInputTokensDetails]
        key "output_tokens": Required[int]
        key "output_tokens_details": Required[ResponseUsageOutputTokensDetails]
        key "total_tokens": Required[int]
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int


    class azure.ai.agentserver.responses.models.ResponseUsageInputTokensDetails(TypedDict, total=False):
        key "cached_tokens": Required[int]
        cached_tokens: int


    class azure.ai.agentserver.responses.models.ResponseUsageOutputTokensDetails(TypedDict, total=False):
        key "reasoning_tokens": Required[int]
        reasoning_tokens: int


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[completed]


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallSearchingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal["searching"]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[searching]


    class azure.ai.agentserver.responses.models.ScreenshotParam(TypedDict, total=False):
        key "type": Required[Literal["screenshot"]]
        type: Literal[screenshot]


    class azure.ai.agentserver.responses.models.ScrollParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "scroll_x": Required[int]
        key "scroll_y": Required[int]
        key "type": Required[Literal["scroll"]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        scroll_x: int
        scroll_y: int
        type: Literal[scroll]
        x: int
        y: int


    class azure.ai.agentserver.responses.models.SearchContentType(TypedDict):


    class azure.ai.agentserver.responses.models.SearchContextSize(TypedDict):


    class azure.ai.agentserver.responses.models.SearchMemoriesRequest(TypedDict, total=False):
        key "options": ForwardRef('MemorySearchOptions', module='types')
        key "previous_search_id": str
        key "scope": Required[str]
        items: list[Item]
        items_property: list[Item]
        options: MemorySearchOptions
        previous_search_id: str
        scope: str


    class azure.ai.agentserver.responses.models.ServiceTierEnum(TypedDict):


    class azure.ai.agentserver.responses.models.SharepointGroundingToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["sharepoint_grounding_preview_call"]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[sharepoint_grounding_preview_call]


    class azure.ai.agentserver.responses.models.SharepointGroundingToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": str
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal["sharepoint_grounding_preview_call_output"]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[sharepoint_grounding_preview_call_output]


    class azure.ai.agentserver.responses.models.SharepointGroundingToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.agentserver.responses.models.SharepointPreviewTool(TypedDict, total=False):
        key "sharepoint_grounding_preview": Required[SharepointGroundingToolParameters]
        key "type": Required[Literal["sharepoint_grounding_preview"]]
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[sharepoint_grounding_preview]


    class azure.ai.agentserver.responses.models.SkillReferenceParam(TypedDict, total=False):
        key "skill_id": Required[str]
        key "type": Required[Literal["skill_reference"]]
        key "version": str
        skill_id: str
        type: Literal[skill_reference]
        version: str


    class azure.ai.agentserver.responses.models.SpecificApplyPatchParam(TypedDict, total=False):
        key "type": Required[Literal["apply_patch"]]
        type: Literal[apply_patch]


    class azure.ai.agentserver.responses.models.SpecificFunctionShellParam(TypedDict, total=False):
        key "type": Required[Literal["shell"]]
        type: Literal[shell]


    class azure.ai.agentserver.responses.models.StructuredInputDefinition(TypedDict, total=False):
        key "default_value": Any
        key "description": str
        key "required": bool
        default_value: Any
        description: str
        required: bool
        schema: dict[str, Any]


    class azure.ai.agentserver.responses.models.StructuredOutputDefinition(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Required[Optional[bool]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool


    class azure.ai.agentserver.responses.models.StructuredOutputsOutputItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": str
        key "output": Required[Any]
        key "response_id": str
        key "type": Required[Literal["structured_outputs"]]
        agent_reference: AgentReference
        id: str
        output: Any
        response_id: str
        type: Literal[structured_outputs]


    class azure.ai.agentserver.responses.models.SummaryTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["summary_text"]]
        text: str
        type: Literal[summary_text]


    class azure.ai.agentserver.responses.models.TextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["text"]]
        text: str
        type: Literal[text]


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationResponseFormatJsonObject(TypedDict, total=False):
        key "type": Required[Literal["json_object"]]
        type: Literal[json_object]


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationResponseFormatText(TypedDict, total=False):
        key "type": Required[Literal["text"]]
        type: Literal[text]


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationType(TypedDict):


    class azure.ai.agentserver.responses.models.TextResponseFormatJsonSchema(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "schema": Required[ResponseFormatJsonSchemaSchema]
        key "strict": Optional[bool]
        key "type": Required[Literal["json_schema"]]
        description: str
        name: str
        schema: ResponseFormatJsonSchemaSchema
        strict: bool
        type: Literal[json_schema]


    class azure.ai.agentserver.responses.models.ToolCallStatus(TypedDict):


    class azure.ai.agentserver.responses.models.ToolChoiceAllowed(TypedDict, total=False):
        key "mode": Required[Literal["auto", "required"]]
        key "tools": Required[list[dict[str, Any]]]
        key "type": Required[Literal["allowed_tools"]]
        mode: Literal[auto, required]
        tools: list[dict[str, Any]]
        type: Literal[allowed_tools]


    class azure.ai.agentserver.responses.models.ToolChoiceCodeInterpreter(TypedDict, total=False):
        key "type": Required[Literal["code_interpreter"]]
        type: Literal[code_interpreter]


    class azure.ai.agentserver.responses.models.ToolChoiceComputer(TypedDict, total=False):
        key "type": Required[Literal["computer"]]
        type: Literal[computer]


    class azure.ai.agentserver.responses.models.ToolChoiceComputerUse(TypedDict, total=False):
        key "type": Required[Literal["computer_use"]]
        type: Literal[computer_use]


    class azure.ai.agentserver.responses.models.ToolChoiceComputerUsePreview(TypedDict, total=False):
        key "type": Required[Literal["computer_use_preview"]]
        type: Literal[computer_use_preview]


    class azure.ai.agentserver.responses.models.ToolChoiceCustom(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["custom"]]
        name: str
        type: Literal[custom]


    class azure.ai.agentserver.responses.models.ToolChoiceFileSearch(TypedDict, total=False):
        key "type": Required[Literal["file_search"]]
        type: Literal[file_search]


    class azure.ai.agentserver.responses.models.ToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["function"]]
        name: str
        type: Literal[function]


    class azure.ai.agentserver.responses.models.ToolChoiceImageGeneration(TypedDict, total=False):
        key "type": Required[Literal["image_generation"]]
        type: Literal[image_generation]


    class azure.ai.agentserver.responses.models.ToolChoiceMCP(TypedDict, total=False):
        key "name": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal["mcp"]]
        name: str
        server_label: str
        type: Literal[mcp]


    class azure.ai.agentserver.responses.models.ToolChoiceOptions(TypedDict):


    class azure.ai.agentserver.responses.models.ToolChoiceParamType(TypedDict):


    class azure.ai.agentserver.responses.models.ToolChoiceWebSearchPreview(TypedDict, total=False):
        key "type": Required[Literal["web_search_preview"]]
        type: Literal[web_search_preview]


    class azure.ai.agentserver.responses.models.ToolChoiceWebSearchPreview20250311(TypedDict, total=False):
        key "type": Required[Literal["web_search_preview_2025_03_11"]]
        type: Literal[web_search_preview_2025_03_11]


    class azure.ai.agentserver.responses.models.ToolProjectConnection(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.agentserver.responses.models.ToolSearchCallItemParam(TypedDict, total=False):
        key "arguments": Required[EmptyModelParam]
        key "call_id": Optional[str]
        key "execution": Literal["server", "client"]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal["tool_search_call"]]
        arguments: EmptyModelParam
        call_id: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallItemStatus
        type: Literal[tool_search_call]


    class azure.ai.agentserver.responses.models.ToolSearchExecutionType(TypedDict):


    class azure.ai.agentserver.responses.models.ToolSearchOutputItemParam(TypedDict, total=False):
        key "call_id": Optional[str]
        key "execution": Literal["server", "client"]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal["tool_search_output"]]
        call_id: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallItemStatus
        tools: list[Tool]
        type: Literal[tool_search_output]


    class azure.ai.agentserver.responses.models.ToolSearchToolParam(TypedDict, total=False):
        key "description": Optional[str]
        key "execution": Literal["server", "client"]
        key "parameters": Optional[EmptyModelParam]
        key "type": Required[Literal["tool_search"]]
        description: str
        execution: ToolSearchExecutionType
        parameters: EmptyModelParam
        type: Literal[tool_search]


    class azure.ai.agentserver.responses.models.ToolType(TypedDict):


    class azure.ai.agentserver.responses.models.TopLogProb(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        bytes: list[int]
        logprob: float
        token: str


    class azure.ai.agentserver.responses.models.TypeParam(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["type"]]
        text: str
        type: Literal[type]


    class azure.ai.agentserver.responses.models.UpdateAgentFromManifestRequest(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.UpdateAgentFromManifestRequest1(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.agentserver.responses.models.UpdateAgentRequest(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]


    class azure.ai.agentserver.responses.models.UpdateAgentRequest1(TypedDict, total=False):
        key "definition": Required[AgentDefinition]
        key "description": str
        definition: AgentDefinition
        description: str
        metadata: dict[str, str]


    class azure.ai.agentserver.responses.models.UpdateConversationRequest(TypedDict, total=False):
        key "metadata": Required[Optional[Metadata]]
        metadata: Metadata


    class azure.ai.agentserver.responses.models.UpdateMemoriesRequest(TypedDict, total=False):
        key "previous_update_id": str
        key "scope": Required[str]
        key "update_delay": int
        items: list[Item]
        items_property: list[Item]
        previous_update_id: str
        scope: str
        update_delay: int


    class azure.ai.agentserver.responses.models.UpdateMemoryStoreRequest(TypedDict, total=False):
        key "description": str
        description: str
        metadata: dict[str, str]


    class azure.ai.agentserver.responses.models.UrlCitationBody(TypedDict, total=False):
        key "end_index": Required[int]
        key "start_index": Required[int]
        key "title": Required[str]
        key "type": Required[Literal["url_citation"]]
        key "url": Required[str]
        end_index: int
        start_index: int
        title: str
        type: Literal[url_citation]
        url: str


    class azure.ai.agentserver.responses.models.UserProfileMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal["user_profile"]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[user_profile]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.agentserver.responses.models.VectorStoreFileAttributes(TypedDict, total=False):


    class azure.ai.agentserver.responses.models.WaitParam(TypedDict, total=False):
        key "type": Required[Literal["wait"]]
        type: Literal[wait]


    class azure.ai.agentserver.responses.models.WebSearchActionFind(TypedDict, total=False):
        key "pattern": Required[str]
        key "type": Required[Literal["find_in_page"]]
        key "url": Required[str]
        pattern: str
        type: Literal[find_in_page]
        url: str


    class azure.ai.agentserver.responses.models.WebSearchActionOpenPage(TypedDict, total=False):
        key "type": Required[Literal["open_page"]]
        key "url": Optional[str]
        type: Literal[open_page]
        url: str


    class azure.ai.agentserver.responses.models.WebSearchActionSearch(TypedDict, total=False):
        key "query": str
        key "type": Required[Literal["search"]]
        queries: list[str]
        query: str
        sources: list[WebSearchActionSearchSources]
        type: Literal[search]


    class azure.ai.agentserver.responses.models.WebSearchActionSearchSources(TypedDict, total=False):
        key "type": Required[Literal["url"]]
        key "url": Required[str]
        type: Literal[url]
        url: str


    class azure.ai.agentserver.responses.models.WebSearchApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.agentserver.responses.models.WebSearchConfiguration(TypedDict, total=False):
        key "instance_name": Required[str]
        key "project_connection_id": Required[str]
        instance_name: str
        project_connection_id: str


    class azure.ai.agentserver.responses.models.WebSearchPreviewTool(TypedDict, total=False):
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal["web_search_preview"]]
        key "user_location": Optional[ApproximateLocation]
        search_content_types: list[Literal["text", "image"]]
        search_context_size: SearchContextSize
        type: Literal[web_search_preview]
        user_location: ApproximateLocation


    class azure.ai.agentserver.responses.models.WebSearchTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "filters": Optional[WebSearchToolFilters]
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal["web_search"]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        filters: WebSearchToolFilters
        search_context_size: Literal[low, medium, high]
        type: Literal[web_search]
        user_location: WebSearchApproximateLocation


    class azure.ai.agentserver.responses.models.WebSearchToolFilters(TypedDict, total=False):
        key "allowed_domains": Optional[list[str]]
        allowed_domains: list[str]


    class azure.ai.agentserver.responses.models.WorkflowActionOutputItem(TypedDict, total=False):
        key "action_id": Required[str]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": str
        key "kind": Required[str]
        key "parent_action_id": str
        key "previous_action_id": str
        key "response_id": str
        key "status": Required[Literal["completed", "failed", "in_progress", "cancelled"]]
        key "type": Required[Literal["workflow_action"]]
        action_id: str
        agent_reference: AgentReference
        id: str
        kind: str
        parent_action_id: str
        previous_action_id: str
        response_id: str
        status: Literal[completed, failed, in_progress, cancelled]
        type: Literal[workflow_action]


    class azure.ai.agentserver.responses.models.WorkflowAgentDefinition(TypedDict, total=False):
        key "kind": Required[Literal["workflow"]]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "workflow": str
        kind: Literal[workflow]
        rai_config: RaiConfig
        workflow: str


namespace azure.ai.agentserver.responses.models.errors

    class azure.ai.agentserver.responses.models.errors.ApiErrorResponse(TypedDict, total=False):
        key "error": Required[Error]
        error: Error


    class azure.ai.agentserver.responses.models.errors.Error(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": str
        additionalInfo: dict[str, Any]
        additional_info: dict[str, Any]
        code: str
        debugInfo: dict[str, Any]
        debug_info: dict[str, Any]
        details: list[Error]
        message: str
        param: str
        type: str


    class azure.ai.agentserver.responses.models.errors.RequestValidationError(ValueError):

        def __init__(
                self,
                message: str,
                *,
                code: str = "invalid_request_error",
                debug_info: dict[str, Any] | None = ...,
                details: list[dict[str, str]] | None = ...,
                error_type: str = "invalid_request_error",
                param: str | None = ...
            ) -> None: ...

        def to_api_error_response(self) -> ApiErrorResponse: ...

        def to_error(self) -> Error: ...


namespace azure.ai.agentserver.responses.models.runtime

    def azure.ai.agentserver.responses.models.runtime.build_cancelled_response(
            response_id: str,
            agent_reference: AgentReference | dict[str, Any],
            model: str | None,
            created_at: datetime | None = None
        ) -> dict[str, Any]: ...


    def azure.ai.agentserver.responses.models.runtime.build_failed_response(
            response_id: str,
            agent_reference: AgentReference | dict[str, Any],
            model: str | None,
            created_at: datetime | None = None,
            error_message: str = "An internal server error occurred.",
            error_code: str = "server_error"
        ) -> dict[str, Any]: ...


    class azure.ai.agentserver.responses.models.runtime.AgentReference(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["agent_reference"]]
        key "version": str
        name: str
        type: Literal[agent_reference]
        version: str


    class azure.ai.agentserver.responses.models.runtime.ResponseExecution:
        property agent_reference: AgentReference | dict[str, Any]    # Read-only
        property is_terminal: bool    # Read-only
        property model: str | None    # Read-only
        property replay_enabled: bool    # Read-only
        property visible_via_get: bool    # Read-only

        def __init__(
                self,
                *,
                agent_session_id: str | None = ...,
                cancel_requested: bool = False,
                cancel_signal: Event | None = ...,
                client_disconnected: bool = False,
                completed_at: datetime | None = ...,
                conversation_id: str | None = ...,
                created_at: datetime | None = ...,
                execution_task: Task[Any] | None = ...,
                initial_agent_reference: AgentReference | dict[str, Any] | None = ...,
                initial_model: str | None = ...,
                input_items: list[OutputItem] | None = ...,
                mode_flags: ResponseModeFlags,
                previous_response_id: str | None = ...,
                response: dict[str, Any] | None = ...,
                response_context: ResponseContext | None = ...,
                response_created_seen: bool = False,
                response_id: str,
                status: ResponseStatus = "in_progress",
                subject: _ResponseEventSubject | None = ...,
                updated_at: datetime | None = ...,
                user_id_key: str | None = ...
            ) -> None: ...

        def apply_event(
                self,
                normalized: ResponseStreamEvent,
                all_events: list[ResponseStreamEvent]
            ) -> None: ...

        def set_response_snapshot(self, response: dict[str, Any]) -> None: ...

        def transition_to(self, next_status: ResponseStatus) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseModeFlags:

        def __init__(
                self,
                *,
                background: bool,
                store: bool,
                stream: bool
            ) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseStreamEventType(TypedDict):


    class azure.ai.agentserver.responses.models.runtime.StreamEventRecord:
        property terminal: bool    # Read-only

        def __init__(
                self,
                *,
                emitted_at: datetime | None = ...,
                event_type: str,
                payload: Mapping[str, Any],
                sequence_number: int
            ) -> None: ...

        @classmethod
        def from_event(
                cls,
                event: ResponseStreamEvent,
                payload: Mapping[str, Any]
            ) -> StreamEventRecord: ...


    class azure.ai.agentserver.responses.models.runtime.StreamReplayState:
        property terminal_event_seen: bool    # Read-only

        def __init__(
                self,
                *,
                events: list[StreamEventRecord] | None = ...,
                response_id: str
            ) -> None: ...

        def append(self, event: StreamEventRecord) -> None: ...


namespace azure.ai.agentserver.responses.streaming

    class azure.ai.agentserver.responses.streaming.OutputItemBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self, item: OutputItem) -> ResponseOutputItemAddedEvent: ...

        def emit_done(self, item: OutputItem) -> ResponseOutputItemDoneEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemCodeInterpreterCallBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        async def acode(self, code_text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def code(self, code_text: str) -> Iterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_code_delta(self, delta: str) -> ResponseCodeInterpreterCallCodeDeltaEvent: ...

        def emit_code_done(self, code: str) -> ResponseCodeInterpreterCallCodeDoneEvent: ...

        def emit_completed(self) -> ResponseCodeInterpreterCallCompletedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def emit_in_progress(self) -> ResponseCodeInterpreterCallInProgressEvent: ...

        def emit_interpreting(self) -> ResponseCodeInterpreterCallInterpretingEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemCustomToolCallBuilder(BaseOutputItemBuilder):
        property call_id: str    # Read-only
        property item_id: str    # Read-only
        property name: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str,
                call_id: str,
                name: str
            ) -> None: ...

        async def ainput(self, input_text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def emit_input_delta(self, delta: str) -> ResponseCustomToolCallInputDeltaEvent: ...

        def emit_input_done(self, input_text: str) -> ResponseCustomToolCallInputDoneEvent: ...

        def input(self, input_text: str) -> Iterator[ResponseStreamEvent]: ...


    class azure.ai.agentserver.responses.streaming.OutputItemFileSearchCallBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_completed(self) -> ResponseFileSearchCallCompletedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def emit_in_progress(self) -> ResponseFileSearchCallInProgressEvent: ...

        def emit_searching(self) -> ResponseFileSearchCallSearchingEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemFunctionCallBuilder(BaseOutputItemBuilder):
        property call_id: str    # Read-only
        property item_id: str    # Read-only
        property name: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str,
                name: str,
                call_id: str
            ) -> None: ...

        async def aarguments(self, args: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def arguments(self, args: str) -> Iterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_arguments_delta(self, delta: str) -> ResponseFunctionCallArgumentsDeltaEvent: ...

        def emit_arguments_done(self, arguments: str) -> ResponseFunctionCallArgumentsDoneEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemFunctionCallOutputBuilder(BaseOutputItemBuilder):
        property call_id: str    # Read-only
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str,
                call_id: str
            ) -> None: ...

        def emit_added(self, output: str | list[InputTextContentParam | InputImageContentParamAutoParam | InputFileContentParam] | None = None) -> ResponseOutputItemAddedEvent: ...

        def emit_done(self, output: str | list[InputTextContentParam | InputImageContentParamAutoParam | InputFileContentParam] | None = None) -> ResponseOutputItemDoneEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemImageGenCallBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_completed(self) -> ResponseImageGenCallCompletedEvent: ...

        def emit_done(self, result: str) -> ResponseOutputItemDoneEvent: ...

        def emit_generating(self) -> ResponseImageGenCallGeneratingEvent: ...

        def emit_in_progress(self) -> ResponseImageGenCallInProgressEvent: ...

        def emit_partial_image(self, partial_image_b64: str) -> ResponseImageGenCallPartialImageEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemMcpCallBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property name: str    # Read-only
        property output_index: int    # Read-only
        property server_label: str    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str,
                server_label: str,
                name: str
            ) -> None: ...

        async def aarguments(self, args: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def arguments(self, args: str) -> Iterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_arguments_delta(self, delta: str) -> ResponseMCPCallArgumentsDeltaEvent: ...

        def emit_arguments_done(self, arguments: str) -> ResponseMCPCallArgumentsDoneEvent: ...

        def emit_completed(self) -> ResponseMCPCallCompletedEvent: ...

        def emit_done(
                self,
                *,
                error: dict[str, Any] | None = ...,
                output: str | None = ...
            ) -> ResponseOutputItemDoneEvent: ...

        def emit_failed(self) -> ResponseMCPCallFailedEvent: ...

        def emit_in_progress(self) -> ResponseMCPCallInProgressEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemMcpListToolsBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only
        property server_label: str    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str,
                server_label: str
            ) -> None: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_completed(self) -> ResponseMCPListToolsCompletedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def emit_failed(self) -> ResponseMCPListToolsFailedEvent: ...

        def emit_in_progress(self) -> ResponseMCPListToolsInProgressEvent: ...


    class azure.ai.agentserver.responses.streaming.OutputItemMessageBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def add_refusal_content(self) -> RefusalContentBuilder: ...

        def add_text_content(self) -> TextContentBuilder: ...

        async def arefusal_content(self, text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        async def atext_content(self, text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def refusal_content(self, text: str) -> Iterator[ResponseStreamEvent]: ...

        def text_content(self, text: str) -> Iterator[ResponseStreamEvent]: ...


    class azure.ai.agentserver.responses.streaming.OutputItemReasoningItemBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def add_summary_part(self) -> ReasoningSummaryPartBuilder: ...

        async def asummary_part(self, text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def summary_part(self, text: str) -> Iterator[ResponseStreamEvent]: ...


    class azure.ai.agentserver.responses.streaming.OutputItemWebSearchCallBuilder(BaseOutputItemBuilder):
        property item_id: str    # Read-only
        property output_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseOutputItemAddedEvent: ...

        def emit_completed(self) -> ResponseWebSearchCallCompletedEvent: ...

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

        def emit_in_progress(self) -> ResponseWebSearchCallInProgressEvent: ...

        def emit_searching(self) -> ResponseWebSearchCallSearchingEvent: ...


    class azure.ai.agentserver.responses.streaming.ReasoningSummaryPartBuilder:
        property final_text: str | None    # Read-only
        property summary_index: int    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                summary_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseReasoningSummaryPartAddedEvent: ...

        def emit_done(self) -> ResponseReasoningSummaryPartDoneEvent: ...

        def emit_text_delta(self, text: str) -> ResponseReasoningSummaryTextDeltaEvent: ...

        def emit_text_done(self, final_text: str) -> ResponseReasoningSummaryTextDoneEvent: ...


    class azure.ai.agentserver.responses.streaming.RefusalContentBuilder:
        property content_index: int    # Read-only
        property final_refusal: str | None    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                content_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseContentPartAddedEvent: ...

        def emit_delta(self, text: str) -> ResponseRefusalDeltaEvent: ...

        def emit_done(self) -> ResponseContentPartDoneEvent: ...

        def emit_refusal_done(self, final_refusal: str) -> ResponseRefusalDoneEvent: ...


    class azure.ai.agentserver.responses.streaming.ResponseEventStream:
        property response: dict[str, Any]    # Read-only

        def __init__(
                self,
                *,
                agent_reference: AgentReference | None = ...,
                model: str | None = ...,
                request: CreateResponse | None = ...,
                response: ResponseObject | None = ...,
                response_id: str | None = ...
            ) -> None: ...

        def add_output_item(self, item_id: str) -> OutputItemBuilder: ...

        def add_output_item_apply_patch_call(self) -> OutputItemBuilder: ...

        def add_output_item_apply_patch_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_code_interpreter_call(self) -> OutputItemCodeInterpreterCallBuilder: ...

        def add_output_item_compaction(self) -> OutputItemBuilder: ...

        def add_output_item_computer_call(self) -> OutputItemBuilder: ...

        def add_output_item_computer_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_custom_tool_call(
                self,
                call_id: str,
                name: str
            ) -> OutputItemCustomToolCallBuilder: ...

        def add_output_item_custom_tool_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_file_search_call(self) -> OutputItemFileSearchCallBuilder: ...

        def add_output_item_function_call(
                self,
                name: str,
                call_id: str
            ) -> OutputItemFunctionCallBuilder: ...

        def add_output_item_function_call_output(self, call_id: str) -> OutputItemFunctionCallOutputBuilder: ...

        def add_output_item_function_shell_call(self) -> OutputItemBuilder: ...

        def add_output_item_function_shell_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_image_gen_call(self) -> OutputItemImageGenCallBuilder: ...

        def add_output_item_local_shell_call(self) -> OutputItemBuilder: ...

        def add_output_item_local_shell_call_output(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_approval_request(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_approval_response(self) -> OutputItemBuilder: ...

        def add_output_item_mcp_call(
                self,
                server_label: str,
                name: str,
                *,
                item_id: str | None = ...
            ) -> OutputItemMcpCallBuilder: ...

        def add_output_item_mcp_list_tools(self, server_label: str) -> OutputItemMcpListToolsBuilder: ...

        def add_output_item_message(self) -> OutputItemMessageBuilder: ...

        def add_output_item_reasoning_item(self) -> OutputItemReasoningItemBuilder: ...

        def add_output_item_structured_outputs(self) -> OutputItemBuilder: ...

        def add_output_item_web_search_call(self) -> OutputItemWebSearchCallBuilder: ...

        async def aoutput_item_apply_patch_call(
                self,
                call_id: str,
                operation: ApplyPatchFileOperation,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_apply_patch_call_output(
                self,
                call_id: str,
                *,
                output: str | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_compaction(self, encrypted_content: str) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_computer_call(
                self,
                call_id: str,
                action: ComputerAction,
                *,
                pending_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_computer_call_output(
                self,
                call_id: str,
                output: ComputerScreenshotImage,
                *,
                acknowledged_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_custom_tool_call_output(
                self,
                call_id: str,
                output: str | list[FunctionAndCustomToolCallOutput]
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_call(
                self,
                name: str,
                call_id: str,
                arguments: str | AsyncIterable[str]
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_call_output(
                self,
                call_id: str,
                output: str
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_shell_call(
                self,
                call_id: str,
                action: FunctionShellAction,
                environment: FunctionShellCallEnvironment,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_function_shell_call_output(
                self,
                call_id: str,
                output: list[FunctionShellCallOutputContent],
                *,
                max_output_length: int | None = ...,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_image_gen_call(
                self,
                result_base64: str,
                *,
                partials: AsyncIterable[str] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_local_shell_call(
                self,
                call_id: str,
                action: LocalShellExecAction,
                *,
                status: str = "completed"
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_local_shell_call_output(self, output: str) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_mcp_approval_request(
                self,
                server_label: str,
                name: str,
                arguments: str
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_mcp_approval_response(
                self,
                approval_request_id: str,
                approve: bool = False,
                *,
                reason: str | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_message(
                self,
                text: str | AsyncIterable[str],
                *,
                annotations: Sequence[Annotation] | None = ...
            ) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_reasoning_item(self, summary_text: str | AsyncIterable[str]) -> AsyncIterator[ResponseStreamEvent]: ...

        async def aoutput_item_structured_outputs(self, output: Any) -> AsyncIterator[ResponseStreamEvent]: ...

        def emit_completed(
                self,
                *,
                usage: ResponseUsage | None = ...
            ) -> ResponseCompletedEvent: ...

        def emit_created(
                self,
                *,
                status: str = "in_progress"
            ) -> ResponseCreatedEvent: ...

        def emit_failed(
                self,
                *,
                code: str | ResponseErrorCode = "server_error",
                message: str = "An internal server error occurred.",
                usage: ResponseUsage | None = ...
            ) -> ResponseFailedEvent: ...

        def emit_in_progress(self) -> ResponseInProgressEvent: ...

        def emit_incomplete(
                self,
                *,
                reason: str | None = ...,
                usage: ResponseUsage | None = ...
            ) -> ResponseIncompleteEvent: ...

        def emit_queued(self) -> ResponseQueuedEvent: ...

        def events(self) -> list[ResponseStreamEvent]: ...

        def output_item_apply_patch_call(
                self,
                call_id: str,
                operation: ApplyPatchFileOperation,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_apply_patch_call_output(
                self,
                call_id: str,
                *,
                output: str | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_compaction(self, encrypted_content: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_computer_call(
                self,
                call_id: str,
                action: ComputerAction,
                *,
                pending_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_computer_call_output(
                self,
                call_id: str,
                output: ComputerScreenshotImage,
                *,
                acknowledged_safety_checks: list[ComputerCallSafetyCheckParam] | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_custom_tool_call_output(
                self,
                call_id: str,
                output: str | list[FunctionAndCustomToolCallOutput]
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_call(
                self,
                name: str,
                call_id: str,
                arguments: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_call_output(
                self,
                call_id: str,
                output: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_shell_call(
                self,
                call_id: str,
                action: FunctionShellAction,
                environment: FunctionShellCallEnvironment,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_function_shell_call_output(
                self,
                call_id: str,
                output: list[FunctionShellCallOutputContent],
                *,
                max_output_length: int | None = ...,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_image_gen_call(self, result_base64: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_local_shell_call(
                self,
                call_id: str,
                action: LocalShellExecAction,
                *,
                status: str = "completed"
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_local_shell_call_output(self, output: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_mcp_approval_request(
                self,
                server_label: str,
                name: str,
                arguments: str
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_mcp_approval_response(
                self,
                approval_request_id: str,
                approve: bool = False,
                *,
                reason: str | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_message(
                self,
                text: str,
                *,
                annotations: Sequence[Annotation] | None = ...
            ) -> Iterator[ResponseStreamEvent]: ...

        def output_item_reasoning_item(self, summary_text: str) -> Iterator[ResponseStreamEvent]: ...

        def output_item_structured_outputs(self, output: Any) -> Iterator[ResponseStreamEvent]: ...


    class azure.ai.agentserver.responses.streaming.TextContentBuilder:
        property content_index: int    # Read-only
        property final_text: str | None    # Read-only

        def __init__(
                self,
                stream: ResponseEventStream,
                output_index: int,
                content_index: int,
                item_id: str
            ) -> None: ...

        def emit_added(self) -> ResponseContentPartAddedEvent: ...

        def emit_annotation_added(self, annotation: Annotation) -> ResponseOutputTextAnnotationAddedEvent: ...

        def emit_delta(self, text: str) -> ResponseTextDeltaEvent: ...

        def emit_done(self) -> ResponseContentPartDoneEvent: ...

        def emit_text_done(self, final_text: str | None = None) -> ResponseTextDoneEvent: ...


```