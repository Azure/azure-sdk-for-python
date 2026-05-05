```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


namespace azure.ai.agentserver.responses

    def azure.ai.agentserver.responses.get_conversation_id(request: CreateResponse | ResponseObject) -> Optional[str]: ...


    def azure.ai.agentserver.responses.get_input_expanded(request: CreateResponse) -> list[Item]: ...


    def azure.ai.agentserver.responses.to_output_item(item: Item, response_id: str | None = None) -> OutputItem | None: ...


    class azure.ai.agentserver.responses.CreateResponse(CreateResponseGenerated):
        prompt_cache_key: Optional[str]
        safety_identifier: Optional[str]
        temperature: Optional[float]
        top_p: Optional[float]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                background: Optional[bool] = ..., 
                context_management: Optional[list[ContextManagementParam]] = ..., 
                conversation: Optional[ConversationParam] = ..., 
                include: Optional[list[Union[str, IncludeEnum]]] = ..., 
                input: Optional[InputParam] = ..., 
                instructions: Optional[str] = ..., 
                max_output_tokens: Optional[int] = ..., 
                max_tool_calls: Optional[int] = ..., 
                metadata: Optional[Metadata] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                previous_response_id: Optional[str] = ..., 
                prompt: Optional[Prompt] = ..., 
                prompt_cache_key: Optional[str] = ..., 
                prompt_cache_retention: Optional[Literal[in-memory, 24h]] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                safety_identifier: Optional[str] = ..., 
                service_tier: Optional[Literal[auto, default, flex, scale, priority]] = ..., 
                store: Optional[bool] = ..., 
                stream: Optional[bool] = ..., 
                stream_options: Optional[ResponseStreamOptions] = ..., 
                structured_inputs: Optional[dict[str, Any]] = ..., 
                temperature: Optional[int] = ..., 
                text: Optional[ResponseTextParam] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_logprobs: Optional[int] = ..., 
                top_p: Optional[int] = ..., 
                truncation: Optional[Literal[auto, disabled]] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def delete_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def get_history_item_ids(
                self, 
                previous_response_id: str | None, 
                conversation_id: str | None, 
                limit: int, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self, 
                response_id: str, 
                limit: int = 20, 
                ascending: bool = False, 
                after: str | None = None, 
                before: str | None = None, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self, 
                item_ids: Iterable[str], 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> ResponseObject: ...

        async def update_response(
                self, 
                response: ResponseObject, 
                *, 
                isolation: IsolationContext | None = ...
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
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def delete(self, response_id: str) -> bool: ...

        async def delete_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def delete_stream_events(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def get_execution(self, response_id: str) -> ResponseExecution | None: ...

        async def get_history_item_ids(
                self, 
                previous_response_id: str | None, 
                conversation_id: str | None, 
                limit: int, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self, 
                response_id: str, 
                limit: int = 20, 
                ascending: bool = False, 
                after: str | None = None, 
                before: str | None = None, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self, 
                item_ids: Iterable[str], 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_replay_events(self, response_id: str) -> list[StreamEventRecord] | None: ...

        async def get_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> ResponseObject: ...

        async def get_stream_events(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
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
                isolation: IsolationContext | None = ...
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
                isolation: IsolationContext | None = ...
            ) -> None: ...


    class azure.ai.agentserver.responses.IsolationContext:

        def __init__(
                self, 
                *, 
                chat_key: str | None = ..., 
                user_key: str | None = ...
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
                isolation: IsolationContext | None = ..., 
                mode_flags: ResponseModeFlags, 
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
        property response: ResponseObject    # Read-only

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
                name: str
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


    class azure.ai.agentserver.responses.ResponseObject(ResponseObjectGenerated):
        output: list[OutputItem]
        prompt_cache_key: Optional[str]
        safety_identifier: Optional[str]
        temperature: Optional[float]
        top_p: Optional[float]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: AgentReference, 
                background: Optional[bool] = ..., 
                completed_at: Optional[datetime] = ..., 
                conversation: Optional[ConversationReference] = ..., 
                created_at: datetime, 
                error: ResponseErrorInfo, 
                id: str, 
                incomplete_details: ResponseIncompleteDetails, 
                instructions: Union[str, list[Item]], 
                max_output_tokens: Optional[int] = ..., 
                max_tool_calls: Optional[int] = ..., 
                metadata: Optional[Metadata] = ..., 
                model: Optional[str] = ..., 
                output: list[OutputItem], 
                output_text: Optional[str] = ..., 
                parallel_tool_calls: bool, 
                previous_response_id: Optional[str] = ..., 
                prompt: Optional[Prompt] = ..., 
                prompt_cache_key: Optional[str] = ..., 
                prompt_cache_retention: Optional[Literal[in-memory, 24h]] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                safety_identifier: Optional[str] = ..., 
                service_tier: Optional[Literal[auto, default, flex, scale, priority]] = ..., 
                status: Optional[Literal[completed, failed, in_progress, cancelled, queued, incomplete]] = ..., 
                temperature: Optional[int] = ..., 
                text: Optional[ResponseTextParam] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_logprobs: Optional[int] = ..., 
                top_p: Optional[int] = ..., 
                truncation: Optional[Literal[auto, disabled]] = ..., 
                usage: Optional[ResponseUsage] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    @runtime_checkable
    class azure.ai.agentserver.responses.ResponseProviderProtocol(Protocol):

        async def create_response(
                self, 
                response: ResponseObject, 
                input_items: Iterable[OutputItem] | None, 
                history_item_ids: Iterable[str] | None, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def delete_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def get_history_item_ids(
                self, 
                previous_response_id: str | None, 
                conversation_id: str | None, 
                limit: int, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[str]: ...

        async def get_input_items(
                self, 
                response_id: str, 
                limit: int = 20, 
                ascending: bool = False, 
                after: str | None = None, 
                before: str | None = None, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem]: ...

        async def get_items(
                self, 
                item_ids: Iterable[str], 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[OutputItem | None]: ...

        async def get_response(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> ResponseObject: ...

        async def update_response(
                self, 
                response: ResponseObject, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...


    @runtime_checkable
    class azure.ai.agentserver.responses.ResponseStreamProviderProtocol(Protocol):

        async def delete_stream_events(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> None: ...

        async def get_stream_events(
                self, 
                response_id: str, 
                *, 
                isolation: IsolationContext | None = ...
            ) -> list[ResponseStreamEvent] | None: ...

        async def save_stream_events(
                self, 
                response_id: str, 
                events: list[ResponseStreamEvent], 
                *, 
                isolation: IsolationContext | None = ...
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


    class azure.ai.agentserver.responses.models.A2APreviewTool(Tool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        description: Optional[str]
        name: Optional[str]
        project_connection_id: Optional[str]
        type: Literal[ToolType.A2_A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.A2AToolCall(OutputItem, discriminator='a2a_preview_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.A2_A_PREVIEW_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.A2AToolCallOutput(OutputItem, discriminator='a2a_preview_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.A2_A_PREVIEW_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                name: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AISearchIndexResource(_Model):
        description: Optional[str]
        filter: Optional[str]
        index_asset_id: Optional[str]
        index_name: Optional[str]
        name: Optional[str]
        project_connection_id: Optional[str]
        query_type: Optional[Union[str, AzureAISearchQueryType]]
        top_k: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                index_asset_id: Optional[str] = ..., 
                index_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                query_type: Optional[Union[str, AzureAISearchQueryType]] = ..., 
                top_k: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AgentReference(_Model):
        name: str
        type: Literal["agent_reference"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.Annotation(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AnnotationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_FILE_CITATION = "container_file_citation"
        FILE_CITATION = "file_citation"
        FILE_PATH = "file_path"
        URL_CITATION = "url_citation"


    class azure.ai.agentserver.responses.models.ApiErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchCallOutputStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"


    class azure.ai.agentserver.responses.models.ApplyPatchCallOutputStatusParam(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"


    class azure.ai.agentserver.responses.models.ApplyPatchCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.ApplyPatchCallStatusParam(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.ApplyPatchCreateFileOperation(ApplyPatchFileOperation, discriminator='create_file'):
        diff: str
        path: str
        type: Literal[ApplyPatchFileOperationType.CREATE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                diff: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchCreateFileOperationParam(ApplyPatchOperationParam, discriminator='create_file'):
        diff: str
        path: str
        type: Literal[ApplyPatchOperationParamType.CREATE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                diff: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchDeleteFileOperation(ApplyPatchFileOperation, discriminator='delete_file'):
        path: str
        type: Literal[ApplyPatchFileOperationType.DELETE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchDeleteFileOperationParam(ApplyPatchOperationParam, discriminator='delete_file'):
        path: str
        type: Literal[ApplyPatchOperationParamType.DELETE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchFileOperation(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchFileOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_FILE = "create_file"
        DELETE_FILE = "delete_file"
        UPDATE_FILE = "update_file"


    class azure.ai.agentserver.responses.models.ApplyPatchOperationParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchOperationParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_FILE = "create_file"
        DELETE_FILE = "delete_file"
        UPDATE_FILE = "update_file"


    class azure.ai.agentserver.responses.models.ApplyPatchToolCallItemParam(Item, discriminator='apply_patch_call'):
        call_id: str
        id: Optional[str]
        operation: ApplyPatchOperationParam
        status: Union[str, ApplyPatchCallStatusParam]
        type: Literal[ItemType.APPLY_PATCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                operation: ApplyPatchOperationParam, 
                status: Union[str, ApplyPatchCallStatusParam]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchToolCallOutputItemParam(Item, discriminator='apply_patch_call_output'):
        call_id: str
        id: Optional[str]
        output: Optional[str]
        status: Union[str, ApplyPatchCallOutputStatusParam]
        type: Literal[ItemType.APPLY_PATCH_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Optional[str] = ..., 
                status: Union[str, ApplyPatchCallOutputStatusParam]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchToolParam(Tool, discriminator='apply_patch'):
        type: Literal[ToolType.APPLY_PATCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchUpdateFileOperation(ApplyPatchFileOperation, discriminator='update_file'):
        diff: str
        path: str
        type: Literal[ApplyPatchFileOperationType.UPDATE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                diff: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApplyPatchUpdateFileOperationParam(ApplyPatchOperationParam, discriminator='update_file'):
        diff: str
        path: str
        type: Literal[ApplyPatchOperationParamType.UPDATE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                diff: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ApproximateLocation(_Model):
        city: Optional[str]
        country: Optional[str]
        region: Optional[str]
        timezone: Optional[str]
        type: Literal["approximate"]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                region: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AutoCodeInterpreterToolParam(_Model):
        file_ids: Optional[list[str]]
        memory_limit: Optional[Union[str, ContainerMemoryLimit]]
        network_policy: Optional[ContainerNetworkPolicyParam]
        type: Literal["auto"]

        @overload
        def __init__(
                self, 
                *, 
                file_ids: Optional[list[str]] = ..., 
                memory_limit: Optional[Union[str, ContainerMemoryLimit]] = ..., 
                network_policy: Optional[ContainerNetworkPolicyParam] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureAISearchQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"
        SIMPLE = "simple"
        VECTOR = "vector"
        VECTOR_SEMANTIC_HYBRID = "vector_semantic_hybrid"
        VECTOR_SIMPLE_HYBRID = "vector_simple_hybrid"


    class azure.ai.agentserver.responses.models.AzureAISearchTool(Tool, discriminator='azure_ai_search'):
        azure_ai_search: AzureAISearchToolResource
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureAISearchToolCall(OutputItem, discriminator='azure_ai_search_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.AZURE_AI_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureAISearchToolCallOutput(OutputItem, discriminator='azure_ai_search_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.AZURE_AI_SEARCH_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureAISearchToolResource(_Model):
        description: Optional[str]
        indexes: list[AISearchIndexResource]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                indexes: list[AISearchIndexResource], 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionBinding(_Model):
        storage_queue: AzureFunctionStorageQueue
        type: Literal["storage_queue"]

        @overload
        def __init__(
                self, 
                *, 
                storage_queue: AzureFunctionStorageQueue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionDefinition(_Model):
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding

        @overload
        def __init__(
                self, 
                *, 
                function: AzureFunctionDefinitionFunction, 
                input_binding: AzureFunctionBinding, 
                output_binding: AzureFunctionBinding
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionDefinitionFunction(_Model):
        description: Optional[str]
        name: str
        parameters: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionStorageQueue(_Model):
        queue_name: str
        queue_service_endpoint: str

        @overload
        def __init__(
                self, 
                *, 
                queue_name: str, 
                queue_service_endpoint: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionTool(Tool, discriminator='azure_function'):
        azure_function: AzureFunctionDefinition
        type: Literal[ToolType.AZURE_FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionToolCall(OutputItem, discriminator='azure_function_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.AZURE_FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.AzureFunctionToolCallOutput(OutputItem, discriminator='azure_function_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.AZURE_FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                name: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingCustomSearchConfiguration(_Model):
        count: Optional[int]
        description: Optional[str]
        freshness: Optional[str]
        instance_name: str
        market: Optional[str]
        name: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                freshness: Optional[str] = ..., 
                instance_name: str, 
                market: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingCustomSearchPreviewTool(Tool, discriminator='bing_custom_search_preview'):
        bing_custom_search_preview: BingCustomSearchToolParameters
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search_preview: BingCustomSearchToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingCustomSearchToolCall(OutputItem, discriminator='bing_custom_search_preview_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BING_CUSTOM_SEARCH_PREVIEW_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingCustomSearchToolCallOutput(OutputItem, discriminator='bing_custom_search_preview_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BING_CUSTOM_SEARCH_PREVIEW_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingCustomSearchToolParameters(_Model):
        description: Optional[str]
        name: Optional[str]
        search_configurations: list[BingCustomSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                search_configurations: list[BingCustomSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingGroundingSearchConfiguration(_Model):
        count: Optional[int]
        description: Optional[str]
        freshness: Optional[str]
        market: Optional[str]
        name: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                description: Optional[str] = ..., 
                freshness: Optional[str] = ..., 
                market: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingGroundingSearchToolParameters(_Model):
        description: Optional[str]
        name: Optional[str]
        search_configurations: list[BingGroundingSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                search_configurations: list[BingGroundingSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingGroundingTool(Tool, discriminator='bing_grounding'):
        bing_grounding: BingGroundingSearchToolParameters
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.BING_GROUNDING]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: BingGroundingSearchToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingGroundingToolCall(OutputItem, discriminator='bing_grounding_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BING_GROUNDING_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BingGroundingToolCallOutput(OutputItem, discriminator='bing_grounding_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BING_GROUNDING_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BrowserAutomationPreviewTool(Tool, discriminator='browser_automation_preview'):
        browser_automation_preview: BrowserAutomationToolParameters
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation_preview: BrowserAutomationToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BrowserAutomationToolCall(OutputItem, discriminator='browser_automation_preview_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BROWSER_AUTOMATION_PREVIEW_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BrowserAutomationToolCallOutput(OutputItem, discriminator='browser_automation_preview_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.BROWSER_AUTOMATION_PREVIEW_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BrowserAutomationToolConnectionParameters(_Model):
        description: Optional[str]
        name: Optional[str]
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.BrowserAutomationToolParameters(_Model):
        connection: BrowserAutomationToolConnectionParameters
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection: BrowserAutomationToolConnectionParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CaptureStructuredOutputsTool(Tool, discriminator='capture_structured_outputs'):
        outputs: StructuredOutputDefinition
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]

        @overload
        def __init__(
                self, 
                *, 
                outputs: StructuredOutputDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ChatSummaryMemoryItem(MemoryItem, discriminator='chat_summary'):
        content: str
        kind: Literal[MemoryItemKind.CHAT_SUMMARY]
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ClickButtonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACK = "back"
        FORWARD = "forward"
        LEFT = "left"
        RIGHT = "right"
        WHEEL = "wheel"


    class azure.ai.agentserver.responses.models.ClickParam(ComputerAction, discriminator='click'):
        button: Union[str, ClickButtonType]
        type: Literal[ComputerActionType.CLICK]
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                button: Union[str, ClickButtonType], 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CodeInterpreterOutputImage(_Model):
        type: Literal["image"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CodeInterpreterOutputLogs(_Model):
        logs: str
        type: Literal["logs"]

        @overload
        def __init__(
                self, 
                *, 
                logs: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CodeInterpreterTool(Tool, discriminator='code_interpreter'):
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CompactResource(_Model):
        created_at: datetime
        id: str
        object: Literal["compaction"]
        output: list[ItemField]
        usage: ResponseUsage

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                id: str, 
                output: list[ItemField], 
                usage: ResponseUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CompactionSummaryItemParam(Item, discriminator='compaction'):
        encrypted_content: str
        id: Optional[str]
        type: Literal[ItemType.COMPACTION]

        @overload
        def __init__(
                self, 
                *, 
                encrypted_content: str, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComparisonFilter(_Model):
        key: str
        type: Literal["eq", "ne", "gt", "gte", "lt", "lte"]
        value: Union[str, int, bool, list[Union[str, int]]]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                type: Literal["eq", "ne", "gt", "gte", "lt", "lte"], 
                value: Union[str, int, bool, list[Union[str, int]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CompoundFilter(_Model):
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal["and", "or"]

        @overload
        def __init__(
                self, 
                *, 
                filters: list[Union[ComparisonFilter, Any]], 
                type: Literal["and", "or"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLICK = "click"
        DOUBLE_CLICK = "double_click"
        DRAG = "drag"
        KEYPRESS = "keypress"
        MOVE = "move"
        SCREENSHOT = "screenshot"
        SCROLL = "scroll"
        TYPE = "type"
        WAIT = "wait"


    class azure.ai.agentserver.responses.models.ComputerCallOutputItemParam(Item, discriminator='computer_call_output'):
        acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]]
        call_id: str
        id: Optional[str]
        output: ComputerScreenshotImage
        status: Optional[Union[str, FunctionCallItemStatus]]
        type: Literal[ItemType.COMPUTER_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                output: ComputerScreenshotImage, 
                status: Optional[Union[str, FunctionCallItemStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerCallSafetyCheckParam(_Model):
        code: Optional[str]
        id: str
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                id: str, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROWSER = "browser"
        LINUX = "linux"
        MAC = "mac"
        UBUNTU = "ubuntu"
        WINDOWS = "windows"


    class azure.ai.agentserver.responses.models.ComputerScreenshotContent(MessageContent, discriminator='computer_screenshot'):
        file_id: str
        image_url: str
        type: Literal[MessageContentType.COMPUTER_SCREENSHOT]

        @overload
        def __init__(
                self, 
                *, 
                file_id: str, 
                image_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerScreenshotImage(_Model):
        file_id: Optional[str]
        image_url: Optional[str]
        type: Literal["computer_screenshot"]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ComputerUsePreviewTool(Tool, discriminator='computer_use_preview'):
        display_height: int
        display_width: int
        environment: Union[str, ComputerEnvironment]
        type: Literal[ToolType.COMPUTER_USE_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                display_height: int, 
                display_width: int, 
                environment: Union[str, ComputerEnvironment]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerAutoParam(FunctionShellToolParamEnvironment, discriminator='container_auto'):
        file_ids: Optional[list[str]]
        memory_limit: Optional[Union[str, ContainerMemoryLimit]]
        network_policy: Optional[ContainerNetworkPolicyParam]
        skills: Optional[list[ContainerSkill]]
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]

        @overload
        def __init__(
                self, 
                *, 
                file_ids: Optional[list[str]] = ..., 
                memory_limit: Optional[Union[str, ContainerMemoryLimit]] = ..., 
                network_policy: Optional[ContainerNetworkPolicyParam] = ..., 
                skills: Optional[list[ContainerSkill]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerFileCitationBody(Annotation, discriminator='container_file_citation'):
        container_id: str
        end_index: int
        file_id: str
        filename: str
        start_index: int
        type: Literal[AnnotationType.CONTAINER_FILE_CITATION]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str, 
                end_index: int, 
                file_id: str, 
                filename: str, 
                start_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerMemoryLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUM_16_G = "16g"
        ENUM_1_G = "1g"
        ENUM_4_G = "4g"
        ENUM_64_G = "64g"


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyAllowlistParam(ContainerNetworkPolicyParam, discriminator='allowlist'):
        allowed_domains: list[str]
        domain_secrets: Optional[list[ContainerNetworkPolicyDomainSecretParam]]
        type: Literal[ContainerNetworkPolicyParamType.ALLOWLIST]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: list[str], 
                domain_secrets: Optional[list[ContainerNetworkPolicyDomainSecretParam]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyDisabledParam(ContainerNetworkPolicyParam, discriminator='disabled'):
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyDomainSecretParam(_Model):
        domain: str
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                domain: str, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerNetworkPolicyParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWLIST = "allowlist"
        DISABLED = "disabled"


    class azure.ai.agentserver.responses.models.ContainerReferenceResource(FunctionShellCallEnvironment, discriminator='container_reference'):
        container_id: str
        type: Literal[FunctionShellCallEnvironmentType.CONTAINER_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerSkill(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ContainerSkillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        SKILL_REFERENCE = "skill_reference"


    class azure.ai.agentserver.responses.models.ContextManagementParam(_Model):
        compact_threshold: Optional[int]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                compact_threshold: Optional[int] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ConversationParam_2(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ConversationReference(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CoordParam(_Model):
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CreateResponse(CreateResponseGenerated):
        prompt_cache_key: Optional[str]
        safety_identifier: Optional[str]
        temperature: Optional[float]
        top_p: Optional[float]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                background: Optional[bool] = ..., 
                context_management: Optional[list[ContextManagementParam]] = ..., 
                conversation: Optional[ConversationParam] = ..., 
                include: Optional[list[Union[str, IncludeEnum]]] = ..., 
                input: Optional[InputParam] = ..., 
                instructions: Optional[str] = ..., 
                max_output_tokens: Optional[int] = ..., 
                max_tool_calls: Optional[int] = ..., 
                metadata: Optional[Metadata] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                previous_response_id: Optional[str] = ..., 
                prompt: Optional[Prompt] = ..., 
                prompt_cache_key: Optional[str] = ..., 
                prompt_cache_retention: Optional[Literal[in-memory, 24h]] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                safety_identifier: Optional[str] = ..., 
                service_tier: Optional[Literal[auto, default, flex, scale, priority]] = ..., 
                store: Optional[bool] = ..., 
                stream: Optional[bool] = ..., 
                stream_options: Optional[ResponseStreamOptions] = ..., 
                structured_inputs: Optional[dict[str, Any]] = ..., 
                temperature: Optional[int] = ..., 
                text: Optional[ResponseTextParam] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_logprobs: Optional[int] = ..., 
                top_p: Optional[int] = ..., 
                truncation: Optional[Literal[auto, disabled]] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CustomGrammarFormatParam(CustomToolParamFormat, discriminator='grammar'):
        definition: str
        syntax: Union[str, GrammarSyntax1]
        type: Literal[CustomToolParamFormatType.GRAMMAR]

        @overload
        def __init__(
                self, 
                *, 
                definition: str, 
                syntax: Union[str, GrammarSyntax1]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CustomTextFormatParam(CustomToolParamFormat, discriminator='text'):
        type: Literal[CustomToolParamFormatType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CustomToolParam(Tool, discriminator='custom'):
        description: Optional[str]
        format: Optional[CustomToolParamFormat]
        name: str
        type: Literal[ToolType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                format: Optional[CustomToolParamFormat] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CustomToolParamFormat(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.CustomToolParamFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAMMAR = "grammar"
        TEXT = "text"


    class azure.ai.agentserver.responses.models.DeleteResponseResult(_Model):
        deleted: Literal[True]
        id: str
        object: Literal["response"]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.DetailEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HIGH = "high"
        LOW = "low"


    class azure.ai.agentserver.responses.models.DoubleClickAction(ComputerAction, discriminator='double_click'):
        type: Literal[ComputerActionType.DOUBLE_CLICK]
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.DragParam(ComputerAction, discriminator='drag'):
        path: list[CoordParam]
        type: Literal[ComputerActionType.DRAG]

        @overload
        def __init__(
                self, 
                *, 
                path: list[CoordParam]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.Error(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[Error]]
        message: str
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[dict[str, Any]] = ..., 
                code: str, 
                debug_info: Optional[dict[str, Any]] = ..., 
                details: Optional[list[Error]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FabricDataAgentToolCall(OutputItem, discriminator='fabric_dataagent_preview_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.FABRIC_DATAAGENT_PREVIEW_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FabricDataAgentToolCallOutput(OutputItem, discriminator='fabric_dataagent_preview_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.FABRIC_DATAAGENT_PREVIEW_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FabricDataAgentToolParameters(_Model):
        description: Optional[str]
        name: Optional[str]
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FileCitationBody(Annotation, discriminator='file_citation'):
        file_id: str
        filename: str
        index: int
        type: Literal[AnnotationType.FILE_CITATION]

        @overload
        def __init__(
                self, 
                *, 
                file_id: str, 
                filename: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FilePath(Annotation, discriminator='file_path'):
        file_id: str
        index: int
        type: Literal[AnnotationType.FILE_PATH]

        @overload
        def __init__(
                self, 
                *, 
                file_id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FileSearchTool(Tool, discriminator='file_search'):
        description: Optional[str]
        filters: Optional[Filters]
        max_num_results: Optional[int]
        name: Optional[str]
        ranking_options: Optional[RankingOptions]
        type: Literal[ToolType.FILE_SEARCH]
        vector_store_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                filters: Optional[Filters] = ..., 
                max_num_results: Optional[int] = ..., 
                name: Optional[str] = ..., 
                ranking_options: Optional[RankingOptions] = ..., 
                vector_store_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FileSearchToolCallResults(_Model):
        attributes: Optional[VectorStoreFileAttributes]
        file_id: Optional[str]
        filename: Optional[str]
        score: Optional[float]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[VectorStoreFileAttributes] = ..., 
                file_id: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                score: Optional[float] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputFileContent(FunctionAndCustomToolCallOutput, discriminator='input_file'):
        file_data: Optional[str]
        file_id: Optional[str]
        file_url: Optional[str]
        filename: Optional[str]
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_FILE]

        @overload
        def __init__(
                self, 
                *, 
                file_data: Optional[str] = ..., 
                file_id: Optional[str] = ..., 
                file_url: Optional[str] = ..., 
                filename: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputImageContent(FunctionAndCustomToolCallOutput, discriminator='input_image'):
        detail: Union[str, ImageDetail]
        file_id: Optional[str]
        image_url: Optional[str]
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_IMAGE]

        @overload
        def __init__(
                self, 
                *, 
                detail: Union[str, ImageDetail], 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputInputTextContent(FunctionAndCustomToolCallOutput, discriminator='input_text'):
        text: str
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionAndCustomToolCallOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INPUT_FILE = "input_file"
        INPUT_IMAGE = "input_image"
        INPUT_TEXT = "input_text"


    class azure.ai.agentserver.responses.models.FunctionCallItemStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.FunctionCallOutputItemParam(Item, discriminator='function_call_output'):
        call_id: str
        id: Optional[str]
        output: Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]]
        status: Optional[Union[str, FunctionCallItemStatus]]
        type: Literal[ItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]], 
                status: Optional[Union[str, FunctionCallItemStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellAction(_Model):
        commands: list[str]
        max_output_length: int
        timeout_ms: int

        @overload
        def __init__(
                self, 
                *, 
                commands: list[str], 
                max_output_length: int, 
                timeout_ms: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellActionParam(_Model):
        commands: list[str]
        max_output_length: Optional[int]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                commands: list[str], 
                max_output_length: Optional[int] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParam(Item, discriminator='shell_call'):
        action: FunctionShellActionParam
        call_id: str
        environment: Optional[FunctionShellCallItemParamEnvironment]
        id: Optional[str]
        status: Optional[Union[str, FunctionShellCallItemStatus]]
        type: Literal[ItemType.SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: FunctionShellActionParam, 
                call_id: str, 
                environment: Optional[FunctionShellCallItemParamEnvironment] = ..., 
                id: Optional[str] = ..., 
                status: Optional[Union[str, FunctionShellCallItemStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentContainerReferenceParam(FunctionShellCallItemParamEnvironment, discriminator='container_reference'):
        container_id: str
        type: Literal[FunctionShellCallItemParamEnvironmentType.CONTAINER_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentLocalEnvironmentParam(FunctionShellCallItemParamEnvironment, discriminator='local'):
        skills: Optional[list[LocalSkillParam]]
        type: Literal[FunctionShellCallItemParamEnvironmentType.LOCAL]

        @overload
        def __init__(
                self, 
                *, 
                skills: Optional[list[LocalSkillParam]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallItemParamEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.agentserver.responses.models.FunctionShellCallItemStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputContent(_Model):
        created_by: Optional[str]
        outcome: FunctionShellCallOutputOutcome
        stderr: str
        stdout: str

        @overload
        def __init__(
                self, 
                *, 
                created_by: Optional[str] = ..., 
                outcome: FunctionShellCallOutputOutcome, 
                stderr: str, 
                stdout: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputContentParam(_Model):
        outcome: FunctionShellCallOutputOutcomeParam
        stderr: str
        stdout: str

        @overload
        def __init__(
                self, 
                *, 
                outcome: FunctionShellCallOutputOutcomeParam, 
                stderr: str, 
                stdout: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputExitOutcome(FunctionShellCallOutputOutcome, discriminator='exit'):
        exit_code: int
        type: Literal[FunctionShellCallOutputOutcomeType.EXIT]

        @overload
        def __init__(
                self, 
                *, 
                exit_code: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputExitOutcomeParam(FunctionShellCallOutputOutcomeParam, discriminator='exit'):
        exit_code: int
        type: Literal[FunctionShellCallOutputOutcomeParamType.EXIT]

        @overload
        def __init__(
                self, 
                *, 
                exit_code: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputItemParam(Item, discriminator='shell_call_output'):
        call_id: str
        id: Optional[str]
        max_output_length: Optional[int]
        output: list[FunctionShellCallOutputContentParam]
        status: Optional[Union[str, FunctionShellCallItemStatus]]
        type: Literal[ItemType.SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                max_output_length: Optional[int] = ..., 
                output: list[FunctionShellCallOutputContentParam], 
                status: Optional[Union[str, FunctionShellCallItemStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcome(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcomeParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcomeParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXIT = "exit"
        TIMEOUT = "timeout"


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputOutcomeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXIT = "exit"
        TIMEOUT = "timeout"


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputTimeoutOutcome(FunctionShellCallOutputOutcome, discriminator='timeout'):
        type: Literal[FunctionShellCallOutputOutcomeType.TIMEOUT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellCallOutputTimeoutOutcomeParam(FunctionShellCallOutputOutcomeParam, discriminator='timeout'):
        type: Literal[FunctionShellCallOutputOutcomeParamType.TIMEOUT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellToolParam(Tool, discriminator='shell'):
        description: Optional[str]
        environment: Optional[FunctionShellToolParamEnvironment]
        name: Optional[str]
        type: Literal[ToolType.SHELL]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                environment: Optional[FunctionShellToolParamEnvironment] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentContainerReferenceParam(FunctionShellToolParamEnvironment, discriminator='container_reference'):
        container_id: str
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentLocalEnvironmentParam(FunctionShellToolParamEnvironment, discriminator='local'):
        skills: Optional[list[LocalSkillParam]]
        type: Literal[FunctionShellToolParamEnvironmentType.LOCAL]

        @overload
        def __init__(
                self, 
                *, 
                skills: Optional[list[LocalSkillParam]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionShellToolParamEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_AUTO = "container_auto"
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.agentserver.responses.models.FunctionTool(Tool, discriminator='function'):
        description: Optional[str]
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionToolCallOutput(ItemField, discriminator='function_call_output'):
        call_id: str
        id: Optional[str]
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemFieldType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[FunctionAndCustomToolCallOutput]], 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.FunctionToolCallOutputResource(OutputItem, discriminator='function_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: Optional[str]
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[OutputItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[FunctionAndCustomToolCallOutput]], 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.GrammarSyntax1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARK = "lark"
        REGEX = "regex"


    class azure.ai.agentserver.responses.models.HybridSearchOptions(_Model):
        embedding_weight: int
        text_weight: int

        @overload
        def __init__(
                self, 
                *, 
                embedding_weight: int, 
                text_weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ImageDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HIGH = "high"
        LOW = "low"


    class azure.ai.agentserver.responses.models.ImageGenActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        EDIT = "edit"
        GENERATE = "generate"


    class azure.ai.agentserver.responses.models.ImageGenTool(Tool, discriminator='image_generation'):
        action: Optional[Union[str, ImageGenActionEnum]]
        background: Optional[Literal["transparent", "opaque", "auto"]]
        description: Optional[str]
        input_fidelity: Optional[Union[str, InputFidelity]]
        input_image_mask: Optional[ImageGenToolInputImageMask]
        model: Optional[Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]]
        moderation: Optional[Literal["auto", "low"]]
        name: Optional[str]
        output_compression: Optional[int]
        output_format: Optional[Literal["png", "webp", "jpeg"]]
        partial_images: Optional[int]
        quality: Optional[Literal["low", "medium", "high", "auto"]]
        size: Optional[Literal["1024x1024", "1024x1536", "1536x1024", "auto"]]
        type: Literal[ToolType.IMAGE_GENERATION]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ImageGenActionEnum]] = ..., 
                background: Optional[Literal[transparent, opaque, auto]] = ..., 
                description: Optional[str] = ..., 
                input_fidelity: Optional[Union[str, InputFidelity]] = ..., 
                input_image_mask: Optional[ImageGenToolInputImageMask] = ..., 
                model: Optional[Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]] = ..., 
                moderation: Optional[Literal[auto, low]] = ..., 
                name: Optional[str] = ..., 
                output_compression: Optional[int] = ..., 
                output_format: Optional[Literal[png, webp, jpeg]] = ..., 
                partial_images: Optional[int] = ..., 
                quality: Optional[Literal[low, medium, high, auto]] = ..., 
                size: Optional[Literal[1024x1024, 1024x1536, 1536x1024, auto]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ImageGenToolInputImageMask(_Model):
        file_id: Optional[str]
        image_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.IncludeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_INTERPRETER_CALL_OUTPUTS = "code_interpreter_call.outputs"
        COMPUTER_CALL_OUTPUT_OUTPUT_IMAGE_URL = "computer_call_output.output.image_url"
        FILE_SEARCH_CALL_RESULTS = "file_search_call.results"
        MEMORY_SEARCH_CALL_RESULTS = "memory_search_call.results"
        MESSAGE_INPUT_IMAGE_IMAGE_URL = "message.input_image.image_url"
        MESSAGE_OUTPUT_TEXT_LOGPROBS = "message.output_text.logprobs"
        REASONING_ENCRYPTED_CONTENT = "reasoning.encrypted_content"
        WEB_SEARCH_CALL_ACTION_SOURCES = "web_search_call.action.sources"
        WEB_SEARCH_CALL_RESULTS = "web_search_call.results"


    class azure.ai.agentserver.responses.models.InlineSkillParam(ContainerSkill, discriminator='inline'):
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[ContainerSkillType.INLINE]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                source: InlineSkillSourceParam
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InlineSkillSourceParam(_Model):
        data: str
        media_type: Literal["application/zip"]
        type: Literal["base64"]

        @overload
        def __init__(
                self, 
                *, 
                data: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputFidelity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"


    class azure.ai.agentserver.responses.models.InputFileContent(_Model):
        file_data: Optional[str]
        file_id: Optional[str]
        file_url: Optional[str]
        filename: Optional[str]
        type: Literal["input_file"]

        @overload
        def __init__(
                self, 
                *, 
                file_data: Optional[str] = ..., 
                file_id: Optional[str] = ..., 
                file_url: Optional[str] = ..., 
                filename: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputFileContentParam(_Model):
        file_data: Optional[str]
        file_id: Optional[str]
        file_url: Optional[str]
        filename: Optional[str]
        type: Literal["input_file"]

        @overload
        def __init__(
                self, 
                *, 
                file_data: Optional[str] = ..., 
                file_id: Optional[str] = ..., 
                file_url: Optional[str] = ..., 
                filename: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputImageContent(_Model):
        detail: Union[str, ImageDetail]
        file_id: Optional[str]
        image_url: Optional[str]
        type: Literal["input_image"]

        @overload
        def __init__(
                self, 
                *, 
                detail: Union[str, ImageDetail], 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputImageContentParamAutoParam(_Model):
        detail: Optional[Union[str, DetailEnum]]
        file_id: Optional[str]
        image_url: Optional[str]
        type: Literal["input_image"]

        @overload
        def __init__(
                self, 
                *, 
                detail: Optional[Union[str, DetailEnum]] = ..., 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputTextContent(_Model):
        text: str
        type: Literal["input_text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.InputTextContentParam(_Model):
        text: str
        type: Literal["input_text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.Item(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemCodeInterpreterToolCall(Item, discriminator='code_interpreter_call'):
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
        type: Literal[ItemType.CODE_INTERPRETER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                container_id: str, 
                id: str, 
                outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]], 
                status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemComputerToolCall(Item, discriminator='computer_call'):
        action: ComputerAction
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[ItemType.COMPUTER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: ComputerAction, 
                call_id: str, 
                id: str, 
                pending_safety_checks: list[ComputerCallSafetyCheckParam], 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemCustomToolCall(Item, discriminator='custom_tool_call'):
        call_id: str
        id: Optional[str]
        input: str
        name: str
        type: Literal[ItemType.CUSTOM_TOOL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                input: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemCustomToolCallOutput(Item, discriminator='custom_tool_call_output'):
        call_id: str
        id: Optional[str]
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[ItemType.CUSTOM_TOOL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[FunctionAndCustomToolCallOutput]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemField(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldApplyPatchToolCall(ItemField, discriminator='apply_patch_call'):
        call_id: str
        created_by: Optional[str]
        id: str
        operation: ApplyPatchFileOperation
        status: Union[str, ApplyPatchCallStatus]
        type: Literal[ItemFieldType.APPLY_PATCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                created_by: Optional[str] = ..., 
                id: str, 
                operation: ApplyPatchFileOperation, 
                status: Union[str, ApplyPatchCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldApplyPatchToolCallOutput(ItemField, discriminator='apply_patch_call_output'):
        call_id: str
        created_by: Optional[str]
        id: str
        output: Optional[str]
        status: Union[str, ApplyPatchCallOutputStatus]
        type: Literal[ItemFieldType.APPLY_PATCH_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                created_by: Optional[str] = ..., 
                id: str, 
                output: Optional[str] = ..., 
                status: Union[str, ApplyPatchCallOutputStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldCodeInterpreterToolCall(ItemField, discriminator='code_interpreter_call'):
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
        type: Literal[ItemFieldType.CODE_INTERPRETER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                container_id: str, 
                id: str, 
                outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]], 
                status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldCompactionBody(ItemField, discriminator='compaction'):
        created_by: Optional[str]
        encrypted_content: str
        id: str
        type: Literal[ItemFieldType.COMPACTION]

        @overload
        def __init__(
                self, 
                *, 
                created_by: Optional[str] = ..., 
                encrypted_content: str, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldComputerToolCall(ItemField, discriminator='computer_call'):
        action: ComputerAction
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[ItemFieldType.COMPUTER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: ComputerAction, 
                call_id: str, 
                id: str, 
                pending_safety_checks: list[ComputerCallSafetyCheckParam], 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldComputerToolCallOutputResource(ItemField, discriminator='computer_call_output'):
        acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]]
        call_id: str
        id: Optional[str]
        output: ComputerScreenshotImage
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemFieldType.COMPUTER_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                output: ComputerScreenshotImage, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldCustomToolCall(ItemField, discriminator='custom_tool_call'):
        call_id: str
        id: Optional[str]
        input: str
        name: str
        type: Literal[ItemFieldType.CUSTOM_TOOL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                input: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldCustomToolCallOutput(ItemField, discriminator='custom_tool_call_output'):
        call_id: str
        id: Optional[str]
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[ItemFieldType.CUSTOM_TOOL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[FunctionAndCustomToolCallOutput]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldFileSearchToolCall(ItemField, discriminator='file_search_call'):
        id: str
        queries: list[str]
        results: Optional[list[FileSearchToolCallResults]]
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
        type: Literal[ItemFieldType.FILE_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                queries: list[str], 
                results: Optional[list[FileSearchToolCallResults]] = ..., 
                status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldFunctionShellCall(ItemField, discriminator='shell_call'):
        action: FunctionShellAction
        call_id: str
        created_by: Optional[str]
        environment: FunctionShellCallEnvironment
        id: str
        status: Union[str, LocalShellCallStatus]
        type: Literal[ItemFieldType.SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: FunctionShellAction, 
                call_id: str, 
                created_by: Optional[str] = ..., 
                environment: FunctionShellCallEnvironment, 
                id: str, 
                status: Union[str, LocalShellCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldFunctionShellCallOutput(ItemField, discriminator='shell_call_output'):
        call_id: str
        created_by: Optional[str]
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        status: Union[str, LocalShellCallOutputStatusEnum]
        type: Literal[ItemFieldType.SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                created_by: Optional[str] = ..., 
                id: str, 
                max_output_length: int, 
                output: list[FunctionShellCallOutputContent], 
                status: Union[str, LocalShellCallOutputStatusEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldFunctionToolCall(ItemField, discriminator='function_call'):
        arguments: str
        call_id: str
        id: Optional[str]
        name: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemFieldType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldImageGenToolCall(ItemField, discriminator='image_generation_call'):
        id: str
        result: str
        status: Literal["in_progress", "completed", "generating", "failed"]
        type: Literal[ItemFieldType.IMAGE_GENERATION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                result: str, 
                status: Literal["in_progress", "completed", "generating", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldLocalShellToolCall(ItemField, discriminator='local_shell_call'):
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[ItemFieldType.LOCAL_SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: LocalShellExecAction, 
                call_id: str, 
                id: str, 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldLocalShellToolCallOutput(ItemField, discriminator='local_shell_call_output'):
        id: str
        output: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemFieldType.LOCAL_SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                output: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldMcpApprovalRequest(ItemField, discriminator='mcp_approval_request'):
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[ItemFieldType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                id: str, 
                name: str, 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldMcpApprovalResponseResource(ItemField, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: str
        reason: Optional[str]
        type: Literal[ItemFieldType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                id: str, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldMcpListTools(ItemField, discriminator='mcp_list_tools'):
        error: Optional[str]
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[ItemFieldType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                id: str, 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldMcpToolCall(ItemField, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[dict[str, Any]]
        id: str
        name: str
        output: Optional[str]
        server_label: str
        status: Optional[Union[str, MCPToolCallStatus]]
        type: Literal[ItemFieldType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[dict[str, Any]] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                server_label: str, 
                status: Optional[Union[str, MCPToolCallStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldMessage(ItemField, discriminator='message'):
        content: list[MessageContent]
        id: str
        role: Union[str, MessageRole]
        status: Union[str, MessageStatus]
        type: Literal[ItemFieldType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageContent], 
                id: str, 
                role: Union[str, MessageRole], 
                status: Union[str, MessageStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldReasoningItem(ItemField, discriminator='reasoning'):
        content: Optional[list[ReasoningTextContent]]
        encrypted_content: Optional[str]
        id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        summary: list[SummaryTextContent]
        type: Literal[ItemFieldType.REASONING]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[list[ReasoningTextContent]] = ..., 
                encrypted_content: Optional[str] = ..., 
                id: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ..., 
                summary: list[SummaryTextContent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFieldType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_PATCH_CALL = "apply_patch_call"
        APPLY_PATCH_CALL_OUTPUT = "apply_patch_call_output"
        CODE_INTERPRETER_CALL = "code_interpreter_call"
        COMPACTION = "compaction"
        COMPUTER_CALL = "computer_call"
        COMPUTER_CALL_OUTPUT = "computer_call_output"
        CUSTOM_TOOL_CALL = "custom_tool_call"
        CUSTOM_TOOL_CALL_OUTPUT = "custom_tool_call_output"
        FILE_SEARCH_CALL = "file_search_call"
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        IMAGE_GENERATION_CALL = "image_generation_call"
        LOCAL_SHELL_CALL = "local_shell_call"
        LOCAL_SHELL_CALL_OUTPUT = "local_shell_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"
        REASONING = "reasoning"
        SHELL_CALL = "shell_call"
        SHELL_CALL_OUTPUT = "shell_call_output"
        WEB_SEARCH_CALL = "web_search_call"


    class azure.ai.agentserver.responses.models.ItemFieldWebSearchToolCall(ItemField, discriminator='web_search_call'):
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal["in_progress", "searching", "completed", "failed"]
        type: Literal[ItemFieldType.WEB_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind], 
                id: str, 
                status: Literal["in_progress", "searching", "completed", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFileSearchToolCall(Item, discriminator='file_search_call'):
        id: str
        queries: list[str]
        results: Optional[list[FileSearchToolCallResults]]
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
        type: Literal[ItemType.FILE_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                queries: list[str], 
                results: Optional[list[FileSearchToolCallResults]] = ..., 
                status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemFunctionToolCall(Item, discriminator='function_call'):
        arguments: str
        call_id: str
        id: Optional[str]
        name: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemImageGenToolCall(Item, discriminator='image_generation_call'):
        id: str
        result: str
        status: Literal["in_progress", "completed", "generating", "failed"]
        type: Literal[ItemType.IMAGE_GENERATION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                result: str, 
                status: Literal["in_progress", "completed", "generating", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemLocalShellToolCall(Item, discriminator='local_shell_call'):
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[ItemType.LOCAL_SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: LocalShellExecAction, 
                call_id: str, 
                id: str, 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemLocalShellToolCallOutput(Item, discriminator='local_shell_call_output'):
        id: str
        output: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[ItemType.LOCAL_SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                output: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemMcpApprovalRequest(Item, discriminator='mcp_approval_request'):
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[ItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                id: str, 
                name: str, 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemMcpListTools(Item, discriminator='mcp_list_tools'):
        error: Optional[str]
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[ItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[str] = ..., 
                id: str, 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemMcpToolCall(Item, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[dict[str, Any]]
        id: str
        name: str
        output: Optional[str]
        server_label: str
        status: Optional[Union[str, MCPToolCallStatus]]
        type: Literal[ItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[dict[str, Any]] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                server_label: str, 
                status: Optional[Union[str, MCPToolCallStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemMessage(Item, discriminator='message'):
        content: Union[str, list[MessageContent]]
        role: Union[str, MessageRole]
        type: Literal[ItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: Union[str, list[MessageContent]], 
                role: Union[str, MessageRole]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemOutputMessage(Item, discriminator='output_message'):
        content: list[OutputMessageContent]
        id: str
        role: Literal["assistant"]
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[ItemType.OUTPUT_MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[OutputMessageContent], 
                id: str, 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemReasoningItem(Item, discriminator='reasoning'):
        content: Optional[list[ReasoningTextContent]]
        encrypted_content: Optional[str]
        id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        summary: list[SummaryTextContent]
        type: Literal[ItemType.REASONING]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[list[ReasoningTextContent]] = ..., 
                encrypted_content: Optional[str] = ..., 
                id: str, 
                status: Optional[Literal[in_progress, completed, incomplete]] = ..., 
                summary: list[SummaryTextContent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemReferenceParam(Item, discriminator='item_reference'):
        id: str
        type: Literal[ItemType.ITEM_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A_PREVIEW_CALL = "a2a_preview_call"
        A2_A_PREVIEW_CALL_OUTPUT = "a2a_preview_call_output"
        APPLY_PATCH_CALL = "apply_patch_call"
        APPLY_PATCH_CALL_OUTPUT = "apply_patch_call_output"
        AZURE_AI_SEARCH_CALL = "azure_ai_search_call"
        AZURE_AI_SEARCH_CALL_OUTPUT = "azure_ai_search_call_output"
        AZURE_FUNCTION_CALL = "azure_function_call"
        AZURE_FUNCTION_CALL_OUTPUT = "azure_function_call_output"
        BING_CUSTOM_SEARCH_PREVIEW_CALL = "bing_custom_search_preview_call"
        BING_CUSTOM_SEARCH_PREVIEW_CALL_OUTPUT = "bing_custom_search_preview_call_output"
        BING_GROUNDING_CALL = "bing_grounding_call"
        BING_GROUNDING_CALL_OUTPUT = "bing_grounding_call_output"
        BROWSER_AUTOMATION_PREVIEW_CALL = "browser_automation_preview_call"
        BROWSER_AUTOMATION_PREVIEW_CALL_OUTPUT = "browser_automation_preview_call_output"
        CODE_INTERPRETER_CALL = "code_interpreter_call"
        COMPACTION = "compaction"
        COMPUTER_CALL = "computer_call"
        COMPUTER_CALL_OUTPUT = "computer_call_output"
        CUSTOM_TOOL_CALL = "custom_tool_call"
        CUSTOM_TOOL_CALL_OUTPUT = "custom_tool_call_output"
        FABRIC_DATAAGENT_PREVIEW_CALL = "fabric_dataagent_preview_call"
        FABRIC_DATAAGENT_PREVIEW_CALL_OUTPUT = "fabric_dataagent_preview_call_output"
        FILE_SEARCH_CALL = "file_search_call"
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        IMAGE_GENERATION_CALL = "image_generation_call"
        ITEM_REFERENCE = "item_reference"
        LOCAL_SHELL_CALL = "local_shell_call"
        LOCAL_SHELL_CALL_OUTPUT = "local_shell_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MEMORY_SEARCH_CALL = "memory_search_call"
        MESSAGE = "message"
        OAUTH_CONSENT_REQUEST = "oauth_consent_request"
        OPENAPI_CALL = "openapi_call"
        OPENAPI_CALL_OUTPUT = "openapi_call_output"
        OUTPUT_MESSAGE = "output_message"
        REASONING = "reasoning"
        SHAREPOINT_GROUNDING_PREVIEW_CALL = "sharepoint_grounding_preview_call"
        SHAREPOINT_GROUNDING_PREVIEW_CALL_OUTPUT = "sharepoint_grounding_preview_call_output"
        SHELL_CALL = "shell_call"
        SHELL_CALL_OUTPUT = "shell_call_output"
        STRUCTURED_OUTPUTS = "structured_outputs"
        WEB_SEARCH_CALL = "web_search_call"
        WORKFLOW_ACTION = "workflow_action"


    class azure.ai.agentserver.responses.models.ItemWebSearchToolCall(Item, discriminator='web_search_call'):
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal["in_progress", "searching", "completed", "failed"]
        type: Literal[ItemType.WEB_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind], 
                id: str, 
                status: Literal["in_progress", "searching", "completed", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.KeyPressAction(ComputerAction, discriminator='keypress'):
        keys_property: list[str]
        type: Literal[ComputerActionType.KEYPRESS]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.LocalEnvironmentResource(FunctionShellCallEnvironment, discriminator='local'):
        type: Literal[FunctionShellCallEnvironmentType.LOCAL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.LocalShellCallOutputStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.LocalShellCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.LocalShellExecAction(_Model):
        command: list[str]
        env: dict[str, str]
        timeout_ms: Optional[int]
        type: Literal["exec"]
        user: Optional[str]
        working_directory: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                command: list[str], 
                env: dict[str, str], 
                timeout_ms: Optional[int] = ..., 
                user: Optional[str] = ..., 
                working_directory: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.LocalShellToolParam(Tool, discriminator='local_shell'):
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.LOCAL_SHELL]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.LocalSkillParam(_Model):
        description: str
        name: str
        path: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.LogProb(_Model):
        bytes: list[int]
        logprob: int
        token: str
        top_logprobs: list[TopLogProb]

        @overload
        def __init__(
                self, 
                *, 
                bytes: list[int], 
                logprob: int, 
                token: str, 
                top_logprobs: list[TopLogProb]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MCPApprovalResponse(Item, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: Optional[str]
        reason: Optional[str]
        type: Literal[ItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                id: Optional[str] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MCPListToolsTool(_Model):
        annotations: Optional[MCPListToolsToolAnnotations]
        description: Optional[str]
        input_schema: MCPListToolsToolInputSchema
        name: str

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[MCPListToolsToolAnnotations] = ..., 
                description: Optional[str] = ..., 
                input_schema: MCPListToolsToolInputSchema, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MCPListToolsToolAnnotations(_Model):


    class azure.ai.agentserver.responses.models.MCPListToolsToolInputSchema(_Model):


    class azure.ai.agentserver.responses.models.MCPTool(Tool, discriminator='mcp'):
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        connector_id: Optional[Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                connector_id: Optional[Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams, connector_outlookcalendar, connector_outlookemail, connector_sharepoint]] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MCPToolCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALLING = "calling"
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.MCPToolFilter(_Model):
        read_only: Optional[bool]
        tool_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                read_only: Optional[bool] = ..., 
                tool_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MCPToolRequireApproval(_Model):
        always: Optional[MCPToolFilter]
        never: Optional[MCPToolFilter]

        @overload
        def __init__(
                self, 
                *, 
                always: Optional[MCPToolFilter] = ..., 
                never: Optional[MCPToolFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemoryItem(_Model):
        content: str
        kind: str
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                kind: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemoryItemKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT_SUMMARY = "chat_summary"
        USER_PROFILE = "user_profile"


    class azure.ai.agentserver.responses.models.MemorySearchItem(_Model):
        memory_item: MemoryItem

        @overload
        def __init__(
                self, 
                *, 
                memory_item: MemoryItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemorySearchOptions(_Model):
        max_memories: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_memories: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemorySearchPreviewTool(Tool, discriminator='memory_search_preview'):
        description: Optional[str]
        memory_store_name: str
        name: Optional[str]
        scope: str
        search_options: Optional[MemorySearchOptions]
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                memory_store_name: str, 
                name: Optional[str] = ..., 
                scope: str, 
                search_options: Optional[MemorySearchOptions] = ..., 
                update_delay: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemorySearchToolCallItemParam(Item, discriminator='memory_search_call'):
        results: Optional[list[MemorySearchItem]]
        type: Literal[ItemType.MEMORY_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                results: Optional[list[MemorySearchItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MemorySearchToolCallItemResource(OutputItem, discriminator='memory_search_call'):
        agent_reference: AgentReference
        id: str
        response_id: str
        results: Optional[list[MemorySearchItem]]
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
        type: Literal[OutputItemType.MEMORY_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                response_id: Optional[str] = ..., 
                results: Optional[list[MemorySearchItem]] = ..., 
                status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentInputFileContent(MessageContent, discriminator='input_file'):
        file_data: Optional[str]
        file_id: Optional[str]
        file_url: Optional[str]
        filename: Optional[str]
        type: Literal[MessageContentType.INPUT_FILE]

        @overload
        def __init__(
                self, 
                *, 
                file_data: Optional[str] = ..., 
                file_id: Optional[str] = ..., 
                file_url: Optional[str] = ..., 
                filename: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentInputImageContent(MessageContent, discriminator='input_image'):
        detail: Union[str, ImageDetail]
        file_id: Optional[str]
        image_url: Optional[str]
        type: Literal[MessageContentType.INPUT_IMAGE]

        @overload
        def __init__(
                self, 
                *, 
                detail: Union[str, ImageDetail], 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentInputTextContent(MessageContent, discriminator='input_text'):
        text: str
        type: Literal[MessageContentType.INPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentOutputTextContent(MessageContent, discriminator='output_text'):
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[MessageContentType.OUTPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                annotations: list[Annotation], 
                logprobs: list[LogProb], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentReasoningTextContent(MessageContent, discriminator='reasoning_text'):
        text: str
        type: Literal[MessageContentType.REASONING_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentRefusalContent(MessageContent, discriminator='refusal'):
        refusal: str
        type: Literal[MessageContentType.REFUSAL]

        @overload
        def __init__(
                self, 
                *, 
                refusal: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.MessageContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTER_SCREENSHOT = "computer_screenshot"
        INPUT_FILE = "input_file"
        INPUT_IMAGE = "input_image"
        INPUT_TEXT = "input_text"
        OUTPUT_TEXT = "output_text"
        REASONING_TEXT = "reasoning_text"
        REFUSAL = "refusal"
        SUMMARY_TEXT = "summary_text"
        TEXT = "text"


    class azure.ai.agentserver.responses.models.MessageRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        CRITIC = "critic"
        DEVELOPER = "developer"
        DISCRIMINATOR = "discriminator"
        SYSTEM = "system"
        TOOL = "tool"
        UNKNOWN = "unknown"
        USER = "user"


    class azure.ai.agentserver.responses.models.MessageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.Metadata(_Model):


    class azure.ai.agentserver.responses.models.MicrosoftFabricPreviewTool(Tool, discriminator='fabric_dataagent_preview'):
        description: Optional[str]
        fabric_dataagent_preview: FabricDataAgentToolParameters
        name: Optional[str]
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                fabric_dataagent_preview: FabricDataAgentToolParameters, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ModelIdsCompaction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHATGPT4_O_LATEST = "chatgpt-4o-latest"
        CODEX_MINI_LATEST = "codex-mini-latest"
        COMPUTER_USE_PREVIEW = "computer-use-preview"
        COMPUTER_USE_PREVIEW2025_03_11 = "computer-use-preview-2025-03-11"
        GPT3_5_TURBO = "gpt-3.5-turbo"
        GPT3_5_TURBO0125 = "gpt-3.5-turbo-0125"
        GPT3_5_TURBO0301 = "gpt-3.5-turbo-0301"
        GPT3_5_TURBO0613 = "gpt-3.5-turbo-0613"
        GPT3_5_TURBO1106 = "gpt-3.5-turbo-1106"
        GPT3_5_TURBO16_K = "gpt-3.5-turbo-16k"
        GPT3_5_TURBO16_K0613 = "gpt-3.5-turbo-16k-0613"
        GPT4 = "gpt-4"
        GPT4_0125_PREVIEW = "gpt-4-0125-preview"
        GPT4_0314 = "gpt-4-0314"
        GPT4_0613 = "gpt-4-0613"
        GPT4_1 = "gpt-4.1"
        GPT4_1106_PREVIEW = "gpt-4-1106-preview"
        GPT4_1_2025_04_14 = "gpt-4.1-2025-04-14"
        GPT4_1_MINI = "gpt-4.1-mini"
        GPT4_1_MINI2025_04_14 = "gpt-4.1-mini-2025-04-14"
        GPT4_1_NANO = "gpt-4.1-nano"
        GPT4_1_NANO2025_04_14 = "gpt-4.1-nano-2025-04-14"
        GPT4_32_K = "gpt-4-32k"
        GPT4_32_K0314 = "gpt-4-32k-0314"
        GPT4_32_K0613 = "gpt-4-32k-0613"
        GPT4_O = "gpt-4o"
        GPT4_O2024_05_13 = "gpt-4o-2024-05-13"
        GPT4_O2024_08_06 = "gpt-4o-2024-08-06"
        GPT4_O2024_11_20 = "gpt-4o-2024-11-20"
        GPT4_O_AUDIO_PREVIEW = "gpt-4o-audio-preview"
        GPT4_O_AUDIO_PREVIEW2024_10_01 = "gpt-4o-audio-preview-2024-10-01"
        GPT4_O_AUDIO_PREVIEW2024_12_17 = "gpt-4o-audio-preview-2024-12-17"
        GPT4_O_AUDIO_PREVIEW2025_06_03 = "gpt-4o-audio-preview-2025-06-03"
        GPT4_O_MINI = "gpt-4o-mini"
        GPT4_O_MINI2024_07_18 = "gpt-4o-mini-2024-07-18"
        GPT4_O_MINI_AUDIO_PREVIEW = "gpt-4o-mini-audio-preview"
        GPT4_O_MINI_AUDIO_PREVIEW2024_12_17 = "gpt-4o-mini-audio-preview-2024-12-17"
        GPT4_O_MINI_SEARCH_PREVIEW = "gpt-4o-mini-search-preview"
        GPT4_O_MINI_SEARCH_PREVIEW2025_03_11 = "gpt-4o-mini-search-preview-2025-03-11"
        GPT4_O_SEARCH_PREVIEW = "gpt-4o-search-preview"
        GPT4_O_SEARCH_PREVIEW2025_03_11 = "gpt-4o-search-preview-2025-03-11"
        GPT4_TURBO = "gpt-4-turbo"
        GPT4_TURBO2024_04_09 = "gpt-4-turbo-2024-04-09"
        GPT4_TURBO_PREVIEW = "gpt-4-turbo-preview"
        GPT4_VISION_PREVIEW = "gpt-4-vision-preview"
        GPT5 = "gpt-5"
        GPT5_1 = "gpt-5.1"
        GPT5_1_2025_11_13 = "gpt-5.1-2025-11-13"
        GPT5_1_CHAT_LATEST = "gpt-5.1-chat-latest"
        GPT5_1_CODEX = "gpt-5.1-codex"
        GPT5_1_CODEX_MAX = "gpt-5.1-codex-max"
        GPT5_1_MINI = "gpt-5.1-mini"
        GPT5_2 = "gpt-5.2"
        GPT5_2025_08_07 = "gpt-5-2025-08-07"
        GPT5_2_2025_12_11 = "gpt-5.2-2025-12-11"
        GPT5_2_CHAT_LATEST = "gpt-5.2-chat-latest"
        GPT5_2_PRO = "gpt-5.2-pro"
        GPT5_2_PRO2025_12_11 = "gpt-5.2-pro-2025-12-11"
        GPT5_CHAT_LATEST = "gpt-5-chat-latest"
        GPT5_CODEX = "gpt-5-codex"
        GPT5_MINI = "gpt-5-mini"
        GPT5_MINI2025_08_07 = "gpt-5-mini-2025-08-07"
        GPT5_NANO = "gpt-5-nano"
        GPT5_NANO2025_08_07 = "gpt-5-nano-2025-08-07"
        GPT5_PRO = "gpt-5-pro"
        GPT5_PRO2025_10_06 = "gpt-5-pro-2025-10-06"
        O1 = "o1"
        O1_2024_12_17 = "o1-2024-12-17"
        O1_MINI = "o1-mini"
        O1_MINI2024_09_12 = "o1-mini-2024-09-12"
        O1_PREVIEW = "o1-preview"
        O1_PREVIEW2024_09_12 = "o1-preview-2024-09-12"
        O1_PRO = "o1-pro"
        O1_PRO2025_03_19 = "o1-pro-2025-03-19"
        O3 = "o3"
        O3_2025_04_16 = "o3-2025-04-16"
        O3_DEEP_RESEARCH = "o3-deep-research"
        O3_DEEP_RESEARCH2025_06_26 = "o3-deep-research-2025-06-26"
        O3_MINI = "o3-mini"
        O3_MINI2025_01_31 = "o3-mini-2025-01-31"
        O3_PRO = "o3-pro"
        O3_PRO2025_06_10 = "o3-pro-2025-06-10"
        O4_MINI = "o4-mini"
        O4_MINI2025_04_16 = "o4-mini-2025-04-16"
        O4_MINI_DEEP_RESEARCH = "o4-mini-deep-research"
        O4_MINI_DEEP_RESEARCH2025_06_26 = "o4-mini-deep-research-2025-06-26"


    class azure.ai.agentserver.responses.models.MoveParam(ComputerAction, discriminator='move'):
        type: Literal[ComputerActionType.MOVE]
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OAuthConsentRequestOutputItem(OutputItem, discriminator='oauth_consent_request'):
        agent_reference: AgentReference
        consent_link: str
        id: str
        response_id: str
        server_label: str
        type: Literal[OutputItemType.OAUTH_CONSENT_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                consent_link: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiAnonymousAuthDetails(OpenApiAuthDetails, discriminator='anonymous'):
        type: Literal[OpenApiAuthType.ANONYMOUS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiAuthDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "anonymous"
        MANAGED_IDENTITY = "managed_identity"
        PROJECT_CONNECTION = "project_connection"


    class azure.ai.agentserver.responses.models.OpenApiFunctionDefinition(_Model):
        auth: OpenApiAuthDetails
        default_params: Optional[list[str]]
        description: Optional[str]
        functions: Optional[list[OpenApiFunctionDefinitionFunction]]
        name: str
        spec: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                auth: OpenApiAuthDetails, 
                default_params: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                spec: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiFunctionDefinitionFunction(_Model):
        description: Optional[str]
        name: str
        parameters: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiManagedAuthDetails(OpenApiAuthDetails, discriminator='managed_identity'):
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[OpenApiAuthType.MANAGED_IDENTITY]

        @overload
        def __init__(
                self, 
                *, 
                security_scheme: OpenApiManagedSecurityScheme
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiManagedSecurityScheme(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiProjectConnectionAuthDetails(OpenApiAuthDetails, discriminator='project_connection'):
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[OpenApiAuthType.PROJECT_CONNECTION]

        @overload
        def __init__(
                self, 
                *, 
                security_scheme: OpenApiProjectConnectionSecurityScheme
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiProjectConnectionSecurityScheme(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiTool(Tool, discriminator='openapi'):
        openapi: OpenApiFunctionDefinition
        type: Literal[ToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                openapi: OpenApiFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiToolCall(OutputItem, discriminator='openapi_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.OPENAPI_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OpenApiToolCallOutput(OutputItem, discriminator='openapi_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.OPENAPI_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                name: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputContent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputContentOutputTextContent(OutputContent, discriminator='output_text'):
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[OutputContentType.OUTPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                annotations: list[Annotation], 
                logprobs: list[LogProb], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputContentReasoningTextContent(OutputContent, discriminator='reasoning_text'):
        text: str
        type: Literal[OutputContentType.REASONING_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputContentRefusalContent(OutputContent, discriminator='refusal'):
        refusal: str
        type: Literal[OutputContentType.REFUSAL]

        @overload
        def __init__(
                self, 
                *, 
                refusal: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OUTPUT_TEXT = "output_text"
        REASONING_TEXT = "reasoning_text"
        REFUSAL = "refusal"


    class azure.ai.agentserver.responses.models.OutputItem(_Model):
        agent_reference: Optional[AgentReference]
        response_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                response_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemApplyPatchToolCall(OutputItem, discriminator='apply_patch_call'):
        agent_reference: AgentReference
        call_id: str
        id: str
        operation: ApplyPatchFileOperation
        response_id: str
        status: Union[str, ApplyPatchCallStatus]
        type: Literal[OutputItemType.APPLY_PATCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                operation: ApplyPatchFileOperation, 
                response_id: Optional[str] = ..., 
                status: Union[str, ApplyPatchCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemApplyPatchToolCallOutput(OutputItem, discriminator='apply_patch_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[str]
        response_id: str
        status: Union[str, ApplyPatchCallOutputStatus]
        type: Literal[OutputItemType.APPLY_PATCH_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ApplyPatchCallOutputStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemCodeInterpreterToolCall(OutputItem, discriminator='code_interpreter_call'):
        agent_reference: AgentReference
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        response_id: str
        status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
        type: Literal[OutputItemType.CODE_INTERPRETER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                code: str, 
                container_id: str, 
                id: str, 
                outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]], 
                response_id: Optional[str] = ..., 
                status: Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemCompactionBody(OutputItem, discriminator='compaction'):
        agent_reference: AgentReference
        encrypted_content: str
        id: str
        response_id: str
        type: Literal[OutputItemType.COMPACTION]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                encrypted_content: str, 
                id: str, 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemComputerToolCall(OutputItem, discriminator='computer_call'):
        action: ComputerAction
        agent_reference: AgentReference
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        response_id: str
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[OutputItemType.COMPUTER_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: ComputerAction, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                pending_safety_checks: list[ComputerCallSafetyCheckParam], 
                response_id: Optional[str] = ..., 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemComputerToolCallOutputResource(OutputItem, discriminator='computer_call_output'):
        acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]]
        agent_reference: AgentReference
        call_id: str
        id: Optional[str]
        output: ComputerScreenshotImage
        response_id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[OutputItemType.COMPUTER_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[ComputerCallSafetyCheckParam]] = ..., 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                output: ComputerScreenshotImage, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemCustomToolCall(OutputItem, discriminator='custom_tool_call'):
        agent_reference: AgentReference
        call_id: str
        id: Optional[str]
        input: str
        name: str
        response_id: str
        type: Literal[OutputItemType.CUSTOM_TOOL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                input: str, 
                name: str, 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemCustomToolCallOutput(OutputItem, discriminator='custom_tool_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: Optional[str]
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        type: Literal[OutputItemType.CUSTOM_TOOL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: Optional[str] = ..., 
                output: Union[str, list[FunctionAndCustomToolCallOutput]], 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemFileSearchToolCall(OutputItem, discriminator='file_search_call'):
        agent_reference: AgentReference
        id: str
        queries: list[str]
        response_id: str
        results: Optional[list[FileSearchToolCallResults]]
        status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
        type: Literal[OutputItemType.FILE_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                queries: list[str], 
                response_id: Optional[str] = ..., 
                results: Optional[list[FileSearchToolCallResults]] = ..., 
                status: Literal["in_progress", "searching", "completed", "incomplete", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemFunctionShellCall(OutputItem, discriminator='shell_call'):
        action: FunctionShellAction
        agent_reference: AgentReference
        call_id: str
        environment: FunctionShellCallEnvironment
        id: str
        response_id: str
        status: Union[str, LocalShellCallStatus]
        type: Literal[OutputItemType.SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: FunctionShellAction, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                environment: FunctionShellCallEnvironment, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, LocalShellCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemFunctionShellCallOutput(OutputItem, discriminator='shell_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        response_id: str
        status: Union[str, LocalShellCallOutputStatusEnum]
        type: Literal[OutputItemType.SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                max_output_length: int, 
                output: list[FunctionShellCallOutputContent], 
                response_id: Optional[str] = ..., 
                status: Union[str, LocalShellCallOutputStatusEnum]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemFunctionToolCall(OutputItem, discriminator='function_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: Optional[str]
        name: str
        response_id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[OutputItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: str, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemImageGenToolCall(OutputItem, discriminator='image_generation_call'):
        agent_reference: AgentReference
        id: str
        response_id: str
        result: str
        status: Literal["in_progress", "completed", "generating", "failed"]
        type: Literal[OutputItemType.IMAGE_GENERATION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                response_id: Optional[str] = ..., 
                result: str, 
                status: Literal["in_progress", "completed", "generating", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemLocalShellToolCall(OutputItem, discriminator='local_shell_call'):
        action: LocalShellExecAction
        agent_reference: AgentReference
        call_id: str
        id: str
        response_id: str
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[OutputItemType.LOCAL_SHELL_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: LocalShellExecAction, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemLocalShellToolCallOutput(OutputItem, discriminator='local_shell_call_output'):
        agent_reference: AgentReference
        id: str
        output: str
        response_id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        type: Literal[OutputItemType.LOCAL_SHELL_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                output: str, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[in_progress, completed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemMcpApprovalRequest(OutputItem, discriminator='mcp_approval_request'):
        agent_reference: AgentReference
        arguments: str
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[OutputItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemMcpApprovalResponseResource(OutputItem, discriminator='mcp_approval_response'):
        agent_reference: AgentReference
        approval_request_id: str
        approve: bool
        id: str
        reason: Optional[str]
        response_id: str
        type: Literal[OutputItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                approval_request_id: str, 
                approve: bool, 
                id: str, 
                reason: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemMcpListTools(OutputItem, discriminator='mcp_list_tools'):
        agent_reference: AgentReference
        error: Optional[str]
        id: str
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[OutputItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                error: Optional[str] = ..., 
                id: str, 
                response_id: Optional[str] = ..., 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemMcpToolCall(OutputItem, discriminator='mcp_call'):
        agent_reference: AgentReference
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[dict[str, Any]]
        id: str
        name: str
        output: Optional[str]
        response_id: str
        server_label: str
        status: Optional[Union[str, MCPToolCallStatus]]
        type: Literal[OutputItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[dict[str, Any]] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                server_label: str, 
                status: Optional[Union[str, MCPToolCallStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemMessage(OutputItem, discriminator='message'):
        agent_reference: AgentReference
        content: list[MessageContent]
        id: str
        response_id: str
        role: Union[str, MessageRole]
        status: Union[str, MessageStatus]
        type: Literal[OutputItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                content: list[MessageContent], 
                id: str, 
                response_id: Optional[str] = ..., 
                role: Union[str, MessageRole], 
                status: Union[str, MessageStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemOutputMessage(OutputItem, discriminator='output_message'):
        agent_reference: AgentReference
        content: list[OutputMessageContent]
        id: str
        response_id: str
        role: Literal["assistant"]
        status: Literal["in_progress", "completed", "incomplete"]
        type: Literal[OutputItemType.OUTPUT_MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                content: list[OutputMessageContent], 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Literal["in_progress", "completed", "incomplete"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemReasoningItem(OutputItem, discriminator='reasoning'):
        agent_reference: AgentReference
        content: Optional[list[ReasoningTextContent]]
        encrypted_content: Optional[str]
        id: str
        response_id: str
        status: Optional[Literal["in_progress", "completed", "incomplete"]]
        summary: list[SummaryTextContent]
        type: Literal[OutputItemType.REASONING]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                content: Optional[list[ReasoningTextContent]] = ..., 
                encrypted_content: Optional[str] = ..., 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[in_progress, completed, incomplete]] = ..., 
                summary: list[SummaryTextContent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A_PREVIEW_CALL = "a2a_preview_call"
        A2_A_PREVIEW_CALL_OUTPUT = "a2a_preview_call_output"
        APPLY_PATCH_CALL = "apply_patch_call"
        APPLY_PATCH_CALL_OUTPUT = "apply_patch_call_output"
        AZURE_AI_SEARCH_CALL = "azure_ai_search_call"
        AZURE_AI_SEARCH_CALL_OUTPUT = "azure_ai_search_call_output"
        AZURE_FUNCTION_CALL = "azure_function_call"
        AZURE_FUNCTION_CALL_OUTPUT = "azure_function_call_output"
        BING_CUSTOM_SEARCH_PREVIEW_CALL = "bing_custom_search_preview_call"
        BING_CUSTOM_SEARCH_PREVIEW_CALL_OUTPUT = "bing_custom_search_preview_call_output"
        BING_GROUNDING_CALL = "bing_grounding_call"
        BING_GROUNDING_CALL_OUTPUT = "bing_grounding_call_output"
        BROWSER_AUTOMATION_PREVIEW_CALL = "browser_automation_preview_call"
        BROWSER_AUTOMATION_PREVIEW_CALL_OUTPUT = "browser_automation_preview_call_output"
        CODE_INTERPRETER_CALL = "code_interpreter_call"
        COMPACTION = "compaction"
        COMPUTER_CALL = "computer_call"
        COMPUTER_CALL_OUTPUT = "computer_call_output"
        CUSTOM_TOOL_CALL = "custom_tool_call"
        CUSTOM_TOOL_CALL_OUTPUT = "custom_tool_call_output"
        FABRIC_DATAAGENT_PREVIEW_CALL = "fabric_dataagent_preview_call"
        FABRIC_DATAAGENT_PREVIEW_CALL_OUTPUT = "fabric_dataagent_preview_call_output"
        FILE_SEARCH_CALL = "file_search_call"
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        IMAGE_GENERATION_CALL = "image_generation_call"
        LOCAL_SHELL_CALL = "local_shell_call"
        LOCAL_SHELL_CALL_OUTPUT = "local_shell_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MEMORY_SEARCH_CALL = "memory_search_call"
        MESSAGE = "message"
        OAUTH_CONSENT_REQUEST = "oauth_consent_request"
        OPENAPI_CALL = "openapi_call"
        OPENAPI_CALL_OUTPUT = "openapi_call_output"
        OUTPUT_MESSAGE = "output_message"
        REASONING = "reasoning"
        SHAREPOINT_GROUNDING_PREVIEW_CALL = "sharepoint_grounding_preview_call"
        SHAREPOINT_GROUNDING_PREVIEW_CALL_OUTPUT = "sharepoint_grounding_preview_call_output"
        SHELL_CALL = "shell_call"
        SHELL_CALL_OUTPUT = "shell_call_output"
        STRUCTURED_OUTPUTS = "structured_outputs"
        WEB_SEARCH_CALL = "web_search_call"
        WORKFLOW_ACTION = "workflow_action"


    class azure.ai.agentserver.responses.models.OutputItemWebSearchToolCall(OutputItem, discriminator='web_search_call'):
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        agent_reference: AgentReference
        id: str
        response_id: str
        status: Literal["in_progress", "searching", "completed", "failed"]
        type: Literal[OutputItemType.WEB_SEARCH_CALL]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind], 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Literal["in_progress", "searching", "completed", "failed"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputMessageContent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputMessageContentOutputTextContent(OutputMessageContent, discriminator='output_text'):
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[OutputMessageContentType.OUTPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                annotations: list[Annotation], 
                logprobs: list[LogProb], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputMessageContentRefusalContent(OutputMessageContent, discriminator='refusal'):
        refusal: str
        type: Literal[OutputMessageContentType.REFUSAL]

        @overload
        def __init__(
                self, 
                *, 
                refusal: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.OutputMessageContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OUTPUT_TEXT = "output_text"
        REFUSAL = "refusal"


    class azure.ai.agentserver.responses.models.PageOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.ai.agentserver.responses.models.Prompt(_Model):
        id: str
        variables: Optional[ResponsePromptVariables]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                variables: Optional[ResponsePromptVariables] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.RankerVersionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        DEFAULT2024_11_15 = "default-2024-11-15"


    class azure.ai.agentserver.responses.models.RankingOptions(_Model):
        hybrid_search: Optional[HybridSearchOptions]
        ranker: Optional[Union[str, RankerVersionType]]
        score_threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_search: Optional[HybridSearchOptions] = ..., 
                ranker: Optional[Union[str, RankerVersionType]] = ..., 
                score_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.Reasoning(_Model):
        effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh"]]
        generate_summary: Optional[Literal["auto", "concise", "detailed"]]
        summary: Optional[Literal["auto", "concise", "detailed"]]

        @overload
        def __init__(
                self, 
                *, 
                effort: Optional[Literal[none, minimal, low, medium, high, xhigh]] = ..., 
                generate_summary: Optional[Literal[auto, concise, detailed]] = ..., 
                summary: Optional[Literal[auto, concise, detailed]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ReasoningTextContent(_Model):
        text: str
        type: Literal["reasoning_text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseAudioDeltaEvent(ResponseStreamEvent, discriminator='response.audio.delta'):
        delta: bytes
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: bytes, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseAudioDoneEvent(ResponseStreamEvent, discriminator='response.audio.done'):
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_DONE]

        @overload
        def __init__(
                self, 
                *, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseAudioTranscriptDeltaEvent(ResponseStreamEvent, discriminator='response.audio.transcript.delta'):
        delta: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseAudioTranscriptDoneEvent(ResponseStreamEvent, discriminator='response.audio.transcript.done'):
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCodeDeltaEvent(ResponseStreamEvent, discriminator='response.code_interpreter_call_code.delta'):
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCodeDoneEvent(ResponseStreamEvent, discriminator='response.code_interpreter_call_code.done'):
        code: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallCompletedEvent(ResponseStreamEvent, discriminator='response.code_interpreter_call.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallInProgressEvent(ResponseStreamEvent, discriminator='response.code_interpreter_call.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCodeInterpreterCallInterpretingEvent(ResponseStreamEvent, discriminator='response.code_interpreter_call.interpreting'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCompletedEvent(ResponseStreamEvent, discriminator='response.completed'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseContentPartAddedEvent(ResponseStreamEvent, discriminator='response.content_part.added'):
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CONTENT_PART_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                item_id: str, 
                output_index: int, 
                part: OutputContent, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseContentPartDoneEvent(ResponseStreamEvent, discriminator='response.content_part.done'):
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CONTENT_PART_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                item_id: str, 
                output_index: int, 
                part: OutputContent, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCreatedEvent(ResponseStreamEvent, discriminator='response.created'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCustomToolCallInputDeltaEvent(ResponseStreamEvent, discriminator='response.custom_tool_call_input.delta'):
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseCustomToolCallInputDoneEvent(ResponseStreamEvent, discriminator='response.custom_tool_call_input.done'):
        input: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                input: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMPTY_IMAGE_FILE = "empty_image_file"
        FAILED_TO_DOWNLOAD_IMAGE = "failed_to_download_image"
        IMAGE_CONTENT_POLICY_VIOLATION = "image_content_policy_violation"
        IMAGE_FILE_NOT_FOUND = "image_file_not_found"
        IMAGE_FILE_TOO_LARGE = "image_file_too_large"
        IMAGE_PARSE_ERROR = "image_parse_error"
        IMAGE_TOO_LARGE = "image_too_large"
        IMAGE_TOO_SMALL = "image_too_small"
        INVALID_BASE64_IMAGE = "invalid_base64_image"
        INVALID_IMAGE = "invalid_image"
        INVALID_IMAGE_FORMAT = "invalid_image_format"
        INVALID_IMAGE_MODE = "invalid_image_mode"
        INVALID_IMAGE_URL = "invalid_image_url"
        INVALID_PROMPT = "invalid_prompt"
        RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
        SERVER_ERROR = "server_error"
        UNSUPPORTED_IMAGE_MEDIA_TYPE = "unsupported_image_media_type"
        VECTOR_STORE_TIMEOUT = "vector_store_timeout"


    class azure.ai.agentserver.responses.models.ResponseErrorEvent(ResponseStreamEvent, discriminator='error'):
        code: str
        message: str
        param: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.ERROR]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                param: str, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseErrorInfo(_Model):
        code: Union[str, ResponseErrorCode]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, ResponseErrorCode], 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFailedEvent(ResponseStreamEvent, discriminator='response.failed'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallCompletedEvent(ResponseStreamEvent, discriminator='response.file_search_call.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallInProgressEvent(ResponseStreamEvent, discriminator='response.file_search_call.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFileSearchCallSearchingEvent(ResponseStreamEvent, discriminator='response.file_search_call.searching'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_SEARCHING]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFormatJsonSchemaSchema(_Model):


    class azure.ai.agentserver.responses.models.ResponseFunctionCallArgumentsDeltaEvent(ResponseStreamEvent, discriminator='response.function_call_arguments.delta'):
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseFunctionCallArgumentsDoneEvent(ResponseStreamEvent, discriminator='response.function_call_arguments.done'):
        arguments: str
        item_id: str
        name: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                item_id: str, 
                name: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseImageGenCallCompletedEvent(ResponseStreamEvent, discriminator='response.image_generation_call.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseImageGenCallGeneratingEvent(ResponseStreamEvent, discriminator='response.image_generation_call.generating'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_GENERATING]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseImageGenCallInProgressEvent(ResponseStreamEvent, discriminator='response.image_generation_call.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseImageGenCallPartialImageEvent(ResponseStreamEvent, discriminator='response.image_generation_call.partial_image'):
        item_id: str
        output_index: int
        partial_image_b64: str
        partial_image_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                partial_image_b64: str, 
                partial_image_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseInProgressEvent(ResponseStreamEvent, discriminator='response.in_progress'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseIncompleteDetails(_Model):
        reason: Optional[Literal["max_output_tokens", "content_filter"]]

        @overload
        def __init__(
                self, 
                *, 
                reason: Optional[Literal[max_output_tokens, content_filter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseIncompleteEvent(ResponseStreamEvent, discriminator='response.incomplete'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_INCOMPLETE]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_FILTER = "content_filter"
        MAX_OUTPUT_TOKENS = "max_output_tokens"


    class azure.ai.agentserver.responses.models.ResponseLogProb(_Model):
        logprob: int
        token: str
        top_logprobs: Optional[list[ResponseLogProbTopLogprobs]]

        @overload
        def __init__(
                self, 
                *, 
                logprob: int, 
                token: str, 
                top_logprobs: Optional[list[ResponseLogProbTopLogprobs]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseLogProbTopLogprobs(_Model):
        logprob: Optional[int]
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logprob: Optional[int] = ..., 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPCallArgumentsDeltaEvent(ResponseStreamEvent, discriminator='response.mcp_call_arguments.delta'):
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPCallArgumentsDoneEvent(ResponseStreamEvent, discriminator='response.mcp_call_arguments.done'):
        arguments: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPCallCompletedEvent(ResponseStreamEvent, discriminator='response.mcp_call.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPCallFailedEvent(ResponseStreamEvent, discriminator='response.mcp_call.failed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPCallInProgressEvent(ResponseStreamEvent, discriminator='response.mcp_call.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsCompletedEvent(ResponseStreamEvent, discriminator='response.mcp_list_tools.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsFailedEvent(ResponseStreamEvent, discriminator='response.mcp_list_tools.failed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseMCPListToolsInProgressEvent(ResponseStreamEvent, discriminator='response.mcp_list_tools.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseObject(ResponseObjectGenerated):
        output: list[OutputItem]
        prompt_cache_key: Optional[str]
        safety_identifier: Optional[str]
        temperature: Optional[float]
        top_p: Optional[float]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: AgentReference, 
                background: Optional[bool] = ..., 
                completed_at: Optional[datetime] = ..., 
                conversation: Optional[ConversationReference] = ..., 
                created_at: datetime, 
                error: ResponseErrorInfo, 
                id: str, 
                incomplete_details: ResponseIncompleteDetails, 
                instructions: Union[str, list[Item]], 
                max_output_tokens: Optional[int] = ..., 
                max_tool_calls: Optional[int] = ..., 
                metadata: Optional[Metadata] = ..., 
                model: Optional[str] = ..., 
                output: list[OutputItem], 
                output_text: Optional[str] = ..., 
                parallel_tool_calls: bool, 
                previous_response_id: Optional[str] = ..., 
                prompt: Optional[Prompt] = ..., 
                prompt_cache_key: Optional[str] = ..., 
                prompt_cache_retention: Optional[Literal[in-memory, 24h]] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                safety_identifier: Optional[str] = ..., 
                service_tier: Optional[Literal[auto, default, flex, scale, priority]] = ..., 
                status: Optional[Literal[completed, failed, in_progress, cancelled, queued, incomplete]] = ..., 
                temperature: Optional[int] = ..., 
                text: Optional[ResponseTextParam] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_logprobs: Optional[int] = ..., 
                top_p: Optional[int] = ..., 
                truncation: Optional[Literal[auto, disabled]] = ..., 
                usage: Optional[ResponseUsage] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseOutputItemAddedEvent(ResponseStreamEvent, discriminator='response.output_item.added'):
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                item: OutputItem, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseOutputItemDoneEvent(ResponseStreamEvent, discriminator='response.output_item.done'):
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                item: OutputItem, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseOutputTextAnnotationAddedEvent(ResponseStreamEvent, discriminator='response.output_text.annotation.added'):
        annotation: Annotation
        annotation_index: int
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                annotation: Annotation, 
                annotation_index: int, 
                content_index: int, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponsePromptVariables(_Model):


    class azure.ai.agentserver.responses.models.ResponseQueuedEvent(ResponseStreamEvent, discriminator='response.queued'):
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_QUEUED]

        @overload
        def __init__(
                self, 
                *, 
                response: ResponseObject, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartAddedEvent(ResponseStreamEvent, discriminator='response.reasoning_summary_part.added'):
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartAddedEventPart
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                part: ResponseReasoningSummaryPartAddedEventPart, 
                sequence_number: int, 
                summary_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartAddedEventPart(_Model):
        text: str
        type: Literal["summary_text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartDoneEvent(ResponseStreamEvent, discriminator='response.reasoning_summary_part.done'):
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartDoneEventPart
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_DONE]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                part: ResponseReasoningSummaryPartDoneEventPart, 
                sequence_number: int, 
                summary_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryPartDoneEventPart(_Model):
        text: str
        type: Literal["summary_text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryTextDeltaEvent(ResponseStreamEvent, discriminator='response.reasoning_summary_text.delta'):
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int, 
                summary_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningSummaryTextDoneEvent(ResponseStreamEvent, discriminator='response.reasoning_summary_text.done'):
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int, 
                summary_index: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningTextDeltaEvent(ResponseStreamEvent, discriminator='response.reasoning_text.delta'):
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseReasoningTextDoneEvent(ResponseStreamEvent, discriminator='response.reasoning_text.done'):
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                item_id: str, 
                output_index: int, 
                sequence_number: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseRefusalDeltaEvent(ResponseStreamEvent, discriminator='response.refusal.delta'):
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REFUSAL_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseRefusalDoneEvent(ResponseStreamEvent, discriminator='response.refusal.done'):
        content_index: int
        item_id: str
        output_index: int
        refusal: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REFUSAL_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                item_id: str, 
                output_index: int, 
                refusal: str, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseStreamEvent(_Model):
        sequence_number: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                sequence_number: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseStreamEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        RESPONSE_AUDIO_DELTA = "response.audio.delta"
        RESPONSE_AUDIO_DONE = "response.audio.done"
        RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio.transcript.delta"
        RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio.transcript.done"
        RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA = "response.code_interpreter_call_code.delta"
        RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE = "response.code_interpreter_call_code.done"
        RESPONSE_CODE_INTERPRETER_CALL_COMPLETED = "response.code_interpreter_call.completed"
        RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING = "response.code_interpreter_call.interpreting"
        RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS = "response.code_interpreter_call.in_progress"
        RESPONSE_COMPLETED = "response.completed"
        RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
        RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
        RESPONSE_CREATED = "response.created"
        RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA = "response.custom_tool_call_input.delta"
        RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE = "response.custom_tool_call_input.done"
        RESPONSE_FAILED = "response.failed"
        RESPONSE_FILE_SEARCH_CALL_COMPLETED = "response.file_search_call.completed"
        RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS = "response.file_search_call.in_progress"
        RESPONSE_FILE_SEARCH_CALL_SEARCHING = "response.file_search_call.searching"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
        RESPONSE_IMAGE_GENERATION_CALL_COMPLETED = "response.image_generation_call.completed"
        RESPONSE_IMAGE_GENERATION_CALL_GENERATING = "response.image_generation_call.generating"
        RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS = "response.image_generation_call.in_progress"
        RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE = "response.image_generation_call.partial_image"
        RESPONSE_INCOMPLETE = "response.incomplete"
        RESPONSE_IN_PROGRESS = "response.in_progress"
        RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
        RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
        RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
        RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
        RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
        RESPONSE_MCP_LIST_TOOLS_COMPLETED = "response.mcp_list_tools.completed"
        RESPONSE_MCP_LIST_TOOLS_FAILED = "response.mcp_list_tools.failed"
        RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS = "response.mcp_list_tools.in_progress"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED = "response.output_text.annotation.added"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        RESPONSE_QUEUED = "response.queued"
        RESPONSE_REASONING_SUMMARY_PART_ADDED = "response.reasoning_summary_part.added"
        RESPONSE_REASONING_SUMMARY_PART_DONE = "response.reasoning_summary_part.done"
        RESPONSE_REASONING_SUMMARY_TEXT_DELTA = "response.reasoning_summary_text.delta"
        RESPONSE_REASONING_SUMMARY_TEXT_DONE = "response.reasoning_summary_text.done"
        RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
        RESPONSE_REASONING_TEXT_DONE = "response.reasoning_text.done"
        RESPONSE_REFUSAL_DELTA = "response.refusal.delta"
        RESPONSE_REFUSAL_DONE = "response.refusal.done"
        RESPONSE_WEB_SEARCH_CALL_COMPLETED = "response.web_search_call.completed"
        RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS = "response.web_search_call.in_progress"
        RESPONSE_WEB_SEARCH_CALL_SEARCHING = "response.web_search_call.searching"


    class azure.ai.agentserver.responses.models.ResponseStreamOptions(_Model):
        include_obfuscation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                include_obfuscation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseTextDeltaEvent(ResponseStreamEvent, discriminator='response.output_text.delta'):
        content_index: int
        delta: str
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                item_id: str, 
                logprobs: list[ResponseLogProb], 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseTextDoneEvent(ResponseStreamEvent, discriminator='response.output_text.done'):
        content_index: int
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                item_id: str, 
                logprobs: list[ResponseLogProb], 
                output_index: int, 
                sequence_number: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseTextParam(_Model):
        format: Optional[TextResponseFormatConfiguration]
        verbosity: Optional[Literal["low", "medium", "high"]]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[TextResponseFormatConfiguration] = ..., 
                verbosity: Optional[Literal[low, medium, high]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseUsage(_Model):
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                input_tokens: int, 
                input_tokens_details: ResponseUsageInputTokensDetails, 
                output_tokens: int, 
                output_tokens_details: ResponseUsageOutputTokensDetails, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseUsageInputTokensDetails(_Model):
        cached_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                cached_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseUsageOutputTokensDetails(_Model):
        reasoning_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                reasoning_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallCompletedEvent(ResponseStreamEvent, discriminator='response.web_search_call.completed'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallInProgressEvent(ResponseStreamEvent, discriminator='response.web_search_call.in_progress'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ResponseWebSearchCallSearchingEvent(ResponseStreamEvent, discriminator='response.web_search_call.searching'):
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_SEARCHING]

        @overload
        def __init__(
                self, 
                *, 
                item_id: str, 
                output_index: int, 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ScreenshotParam(ComputerAction, discriminator='screenshot'):
        type: Literal[ComputerActionType.SCREENSHOT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ScrollParam(ComputerAction, discriminator='scroll'):
        scroll_x: int
        scroll_y: int
        type: Literal[ComputerActionType.SCROLL]
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                scroll_x: int, 
                scroll_y: int, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SearchContextSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.agentserver.responses.models.SharepointGroundingToolCall(OutputItem, discriminator='sharepoint_grounding_preview_call'):
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.SHAREPOINT_GROUNDING_PREVIEW_CALL]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                arguments: str, 
                call_id: str, 
                id: str, 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SharepointGroundingToolCallOutput(OutputItem, discriminator='sharepoint_grounding_preview_call_output'):
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Optional[ToolCallOutputContent]
        response_id: str
        status: Union[str, ToolCallStatus]
        type: Literal[OutputItemType.SHAREPOINT_GROUNDING_PREVIEW_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                call_id: str, 
                id: str, 
                output: Optional[ToolCallOutputContent] = ..., 
                response_id: Optional[str] = ..., 
                status: Union[str, ToolCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SharepointGroundingToolParameters(_Model):
        description: Optional[str]
        name: Optional[str]
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SharepointPreviewTool(Tool, discriminator='sharepoint_grounding_preview'):
        description: Optional[str]
        name: Optional[str]
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                sharepoint_grounding_preview: SharepointGroundingToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SkillReferenceParam(ContainerSkill, discriminator='skill_reference'):
        skill_id: str
        type: Literal[ContainerSkillType.SKILL_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                skill_id: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SpecificApplyPatchParam(ToolChoiceParam, discriminator='apply_patch'):
        type: Literal[ToolChoiceParamType.APPLY_PATCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SpecificFunctionShellParam(ToolChoiceParam, discriminator='shell'):
        type: Literal[ToolChoiceParamType.SHELL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.StructuredOutputDefinition(_Model):
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                schema: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.StructuredOutputsOutputItem(OutputItem, discriminator='structured_outputs'):
        agent_reference: AgentReference
        id: str
        output: Any
        response_id: str
        type: Literal[OutputItemType.STRUCTURED_OUTPUTS]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                output: Any, 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.SummaryTextContent(MessageContent, discriminator='summary_text'):
        text: str
        type: Literal[MessageContentType.SUMMARY_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TextContent(MessageContent, discriminator='text'):
        text: str
        type: Literal[MessageContentType.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TextResponseFormatConfiguration(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationResponseFormatJsonObject(TextResponseFormatConfiguration, discriminator='json_object'):
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationResponseFormatText(TextResponseFormatConfiguration, discriminator='text'):
        type: Literal[TextResponseFormatConfigurationType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TextResponseFormatConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "json_object"
        JSON_SCHEMA = "json_schema"
        TEXT = "text"


    class azure.ai.agentserver.responses.models.TextResponseFormatJsonSchema(TextResponseFormatConfiguration, discriminator='json_schema'):
        description: Optional[str]
        name: str
        schema: ResponseFormatJsonSchemaSchema
        strict: Optional[bool]
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                schema: ResponseFormatJsonSchemaSchema, 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.Tool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agentserver.responses.models.ToolChoiceAllowed(ToolChoiceAllowedGenerated):
        tools: list[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Literal["auto", "required"], 
                tools: list[dict[str, Any]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceCodeInterpreter(ToolChoiceParam, discriminator='code_interpreter'):
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceComputerUsePreview(ToolChoiceParam, discriminator='computer_use_preview'):
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceCustom(ToolChoiceParam, discriminator='custom'):
        name: str
        type: Literal[ToolChoiceParamType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceFileSearch(ToolChoiceParam, discriminator='file_search'):
        type: Literal[ToolChoiceParamType.FILE_SEARCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceFunction(ToolChoiceParam, discriminator='function'):
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceImageGeneration(ToolChoiceParam, discriminator='image_generation'):
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceMCP(ToolChoiceParam, discriminator='mcp'):
        name: Optional[str]
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.agentserver.responses.models.ToolChoiceParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_TOOLS = "allowed_tools"
        APPLY_PATCH = "apply_patch"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        MCP = "mcp"
        SHELL = "shell"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WEB_SEARCH_PREVIEW2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.agentserver.responses.models.ToolChoiceWebSearchPreview(ToolChoiceParam, discriminator='web_search_preview'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolChoiceWebSearchPreview20250311(ToolChoiceParam, discriminator='web_search_preview_2025_03_11'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW2025_03_11]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolProjectConnection(_Model):
        description: Optional[str]
        name: Optional[str]
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A_PREVIEW = "a2a_preview"
        APPLY_PATCH = "apply_patch"
        AZURE_AI_SEARCH = "azure_ai_search"
        AZURE_FUNCTION = "azure_function"
        BING_CUSTOM_SEARCH_PREVIEW = "bing_custom_search_preview"
        BING_GROUNDING = "bing_grounding"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CAPTURE_STRUCTURED_OUTPUTS = "capture_structured_outputs"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FABRIC_DATAAGENT_PREVIEW = "fabric_dataagent_preview"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        LOCAL_SHELL = "local_shell"
        MCP = "mcp"
        MEMORY_SEARCH_PREVIEW = "memory_search_preview"
        OPENAPI = "openapi"
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.agentserver.responses.models.TopLogProb(_Model):
        bytes: list[int]
        logprob: int
        token: str

        @overload
        def __init__(
                self, 
                *, 
                bytes: list[int], 
                logprob: int, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.TypeParam(ComputerAction, discriminator='type'):
        text: str
        type: Literal[ComputerActionType.TYPE]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.UrlCitationBody(Annotation, discriminator='url_citation'):
        end_index: int
        start_index: int
        title: str
        type: Literal[AnnotationType.URL_CITATION]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                end_index: int, 
                start_index: int, 
                title: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.UserProfileMemoryItem(MemoryItem, discriminator='user_profile'):
        content: str
        kind: Literal[MemoryItemKind.USER_PROFILE]
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.VectorStoreFileAttributes(_Model):


    class azure.ai.agentserver.responses.models.WaitParam(ComputerAction, discriminator='wait'):
        type: Literal[ComputerActionType.WAIT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchActionFind(_Model):
        pattern: str
        type: Literal["find_in_page"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                pattern: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchActionOpenPage(_Model):
        type: Literal["open_page"]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchActionSearch(_Model):
        queries: Optional[list[str]]
        query: str
        sources: Optional[list[WebSearchActionSearchSources]]
        type: Literal["search"]

        @overload
        def __init__(
                self, 
                *, 
                queries: Optional[list[str]] = ..., 
                query: str, 
                sources: Optional[list[WebSearchActionSearchSources]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchActionSearchSources(_Model):
        type: Literal["url"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchApproximateLocation(_Model):
        city: Optional[str]
        country: Optional[str]
        region: Optional[str]
        timezone: Optional[str]
        type: Literal["approximate"]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                region: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchConfiguration(_Model):
        description: Optional[str]
        instance_name: str
        name: Optional[str]
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                instance_name: str, 
                name: Optional[str] = ..., 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchPreviewTool(Tool, discriminator='web_search_preview'):
        search_context_size: Optional[Union[str, SearchContextSize]]
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: Optional[ApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                search_context_size: Optional[Union[str, SearchContextSize]] = ..., 
                user_location: Optional[ApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchTool(Tool, discriminator='web_search'):
        custom_search_configuration: Optional[WebSearchConfiguration]
        description: Optional[str]
        filters: Optional[WebSearchToolFilters]
        name: Optional[str]
        search_context_size: Optional[Literal["low", "medium", "high"]]
        type: Literal[ToolType.WEB_SEARCH]
        user_location: Optional[WebSearchApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                custom_search_configuration: Optional[WebSearchConfiguration] = ..., 
                description: Optional[str] = ..., 
                filters: Optional[WebSearchToolFilters] = ..., 
                name: Optional[str] = ..., 
                search_context_size: Optional[Literal[low, medium, high]] = ..., 
                user_location: Optional[WebSearchApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WebSearchToolFilters(_Model):
        allowed_domains: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WorkIQPreviewTool(Tool, discriminator='work_iq_preview'):
        type: Literal[ToolType.WORK_IQ_PREVIEW]
        work_iq_preview: WorkIQPreviewToolParameters

        @overload
        def __init__(
                self, 
                *, 
                work_iq_preview: WorkIQPreviewToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WorkIQPreviewToolParameters(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.WorkflowActionOutputItem(OutputItem, discriminator='workflow_action'):
        action_id: str
        agent_reference: AgentReference
        id: str
        kind: str
        parent_action_id: Optional[str]
        previous_action_id: Optional[str]
        response_id: str
        status: Literal["completed", "failed", "in_progress", "cancelled"]
        type: Literal[OutputItemType.WORKFLOW_ACTION]

        @overload
        def __init__(
                self, 
                *, 
                action_id: str, 
                agent_reference: Optional[AgentReference] = ..., 
                id: str, 
                kind: str, 
                parent_action_id: Optional[str] = ..., 
                previous_action_id: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                status: Literal["completed", "failed", "in_progress", "cancelled"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.agentserver.responses.models.errors

    class azure.ai.agentserver.responses.models.errors.ApiErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.errors.Error(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[Error]]
        message: str
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[dict[str, Any]] = ..., 
                code: str, 
                debug_info: Optional[dict[str, Any]] = ..., 
                details: Optional[list[Error]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        ) -> ResponseObject: ...


    def azure.ai.agentserver.responses.models.runtime.build_failed_response(
            response_id: str, 
            agent_reference: AgentReference | dict[str, Any], 
            model: str | None, 
            created_at: datetime | None = None, 
            error_message: str = "An internal server error occurred.", 
            error_code: str = "server_error"
        ) -> ResponseObject: ...


    class azure.ai.agentserver.responses.models.runtime.AgentReference(_Model):
        name: str
        type: Literal["agent_reference"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.OutputItem(_Model):
        agent_reference: Optional[AgentReference]
        response_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: Optional[AgentReference] = ..., 
                response_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
                chat_isolation_key: str | None = ..., 
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
                response: ResponseObject | None = ..., 
                response_context: ResponseContext | None = ..., 
                response_created_seen: bool = False, 
                response_id: str, 
                status: ResponseStatus = "in_progress", 
                subject: _ResponseEventSubject | None = ..., 
                updated_at: datetime | None = ...
            ) -> None: ...

        def apply_event(
                self, 
                normalized: ResponseStreamEvent, 
                all_events: list[ResponseStreamEvent]
            ) -> None: ...

        def set_response_snapshot(self, response: ResponseObject) -> None: ...

        def transition_to(self, next_status: ResponseStatus) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseModeFlags:

        def __init__(
                self, 
                *, 
                background: bool, 
                store: bool, 
                stream: bool
            ) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseObject(ResponseObjectGenerated):
        output: list[OutputItem]
        prompt_cache_key: Optional[str]
        safety_identifier: Optional[str]
        temperature: Optional[float]
        top_p: Optional[float]
        user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_reference: AgentReference, 
                background: Optional[bool] = ..., 
                completed_at: Optional[datetime] = ..., 
                conversation: Optional[ConversationReference] = ..., 
                created_at: datetime, 
                error: ResponseErrorInfo, 
                id: str, 
                incomplete_details: ResponseIncompleteDetails, 
                instructions: Union[str, list[Item]], 
                max_output_tokens: Optional[int] = ..., 
                max_tool_calls: Optional[int] = ..., 
                metadata: Optional[Metadata] = ..., 
                model: Optional[str] = ..., 
                output: list[OutputItem], 
                output_text: Optional[str] = ..., 
                parallel_tool_calls: bool, 
                previous_response_id: Optional[str] = ..., 
                prompt: Optional[Prompt] = ..., 
                prompt_cache_key: Optional[str] = ..., 
                prompt_cache_retention: Optional[Literal[in-memory, 24h]] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                safety_identifier: Optional[str] = ..., 
                service_tier: Optional[Literal[auto, default, flex, scale, priority]] = ..., 
                status: Optional[Literal[completed, failed, in_progress, cancelled, queued, incomplete]] = ..., 
                temperature: Optional[int] = ..., 
                text: Optional[ResponseTextParam] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_logprobs: Optional[int] = ..., 
                top_p: Optional[int] = ..., 
                truncation: Optional[Literal[auto, disabled]] = ..., 
                usage: Optional[ResponseUsage] = ..., 
                user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseStreamEvent(_Model):
        sequence_number: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                sequence_number: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agentserver.responses.models.runtime.ResponseStreamEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        RESPONSE_AUDIO_DELTA = "response.audio.delta"
        RESPONSE_AUDIO_DONE = "response.audio.done"
        RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio.transcript.delta"
        RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio.transcript.done"
        RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA = "response.code_interpreter_call_code.delta"
        RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE = "response.code_interpreter_call_code.done"
        RESPONSE_CODE_INTERPRETER_CALL_COMPLETED = "response.code_interpreter_call.completed"
        RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING = "response.code_interpreter_call.interpreting"
        RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS = "response.code_interpreter_call.in_progress"
        RESPONSE_COMPLETED = "response.completed"
        RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
        RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
        RESPONSE_CREATED = "response.created"
        RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA = "response.custom_tool_call_input.delta"
        RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE = "response.custom_tool_call_input.done"
        RESPONSE_FAILED = "response.failed"
        RESPONSE_FILE_SEARCH_CALL_COMPLETED = "response.file_search_call.completed"
        RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS = "response.file_search_call.in_progress"
        RESPONSE_FILE_SEARCH_CALL_SEARCHING = "response.file_search_call.searching"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
        RESPONSE_IMAGE_GENERATION_CALL_COMPLETED = "response.image_generation_call.completed"
        RESPONSE_IMAGE_GENERATION_CALL_GENERATING = "response.image_generation_call.generating"
        RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS = "response.image_generation_call.in_progress"
        RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE = "response.image_generation_call.partial_image"
        RESPONSE_INCOMPLETE = "response.incomplete"
        RESPONSE_IN_PROGRESS = "response.in_progress"
        RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
        RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
        RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
        RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
        RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
        RESPONSE_MCP_LIST_TOOLS_COMPLETED = "response.mcp_list_tools.completed"
        RESPONSE_MCP_LIST_TOOLS_FAILED = "response.mcp_list_tools.failed"
        RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS = "response.mcp_list_tools.in_progress"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED = "response.output_text.annotation.added"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        RESPONSE_QUEUED = "response.queued"
        RESPONSE_REASONING_SUMMARY_PART_ADDED = "response.reasoning_summary_part.added"
        RESPONSE_REASONING_SUMMARY_PART_DONE = "response.reasoning_summary_part.done"
        RESPONSE_REASONING_SUMMARY_TEXT_DELTA = "response.reasoning_summary_text.delta"
        RESPONSE_REASONING_SUMMARY_TEXT_DONE = "response.reasoning_summary_text.done"
        RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
        RESPONSE_REASONING_TEXT_DONE = "response.reasoning_text.done"
        RESPONSE_REFUSAL_DELTA = "response.refusal.delta"
        RESPONSE_REFUSAL_DONE = "response.refusal.done"
        RESPONSE_WEB_SEARCH_CALL_COMPLETED = "response.web_search_call.completed"
        RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS = "response.web_search_call.in_progress"
        RESPONSE_WEB_SEARCH_CALL_SEARCHING = "response.web_search_call.searching"


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
        def from_generated(
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

        def emit_done(self) -> ResponseOutputItemDoneEvent: ...

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
        property response: ResponseObject    # Read-only

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
                name: str
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