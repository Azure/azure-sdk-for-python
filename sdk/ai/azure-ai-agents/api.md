```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


namespace azure.ai.agents

    class azure.ai.agents.AgentsClient(AgentsClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def create_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: str, 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def create_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: str, 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                toolset: Optional[ToolSet] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def create_agent(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def create_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def create_thread_and_process_run(
                self, 
                *, 
                agent_id: str = _Unset, 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                polling_interval: int = 1, 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                thread: Optional[AgentThreadCreationOptions] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                toolset: Optional[ToolSet] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create_thread_and_run(
                self, 
                *, 
                agent_id: str, 
                content_type: str = "application/json", 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                thread: Optional[AgentThreadCreationOptions] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create_thread_and_run(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create_thread_and_run(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace
        def delete_agent(
                self, 
                agent_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_auto_function_calls(
                self, 
                tools: Union[Set[Callable[, Any]], FunctionTool, ToolSet], 
                max_retry: int = 10
            ) -> None: ...

        @distributed_trace
        def get_agent(
                self, 
                agent_id: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list_agents(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Agent]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_agent(
                self, 
                agent_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def update_agent(
                self, 
                agent_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                toolset: Optional[ToolSet] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def update_agent(
                self, 
                agent_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        def update_agent(
                self, 
                agent_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...


namespace azure.ai.agents.aio

    class azure.ai.agents.aio.AgentsClient(AgentsClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def create_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: str, 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def create_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: str, 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                toolset: Optional[AsyncToolSet] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def create_agent(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def create_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace_async
        async def create_thread_and_process_run(
                self, 
                *, 
                agent_id: str = _Unset, 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                polling_interval: int = 1, 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                thread: Optional[AgentThreadCreationOptions] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                toolset: Optional[AsyncToolSet] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create_thread_and_run(
                self, 
                *, 
                agent_id: str, 
                content_type: str = "application/json", 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                thread: Optional[AgentThreadCreationOptions] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create_thread_and_run(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create_thread_and_run(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace_async
        async def delete_agent(
                self, 
                agent_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_auto_function_calls(
                self, 
                tools: Union[Set[Callable[, Any]], AsyncFunctionTool, AsyncToolSet], 
                max_retry: int = 10
            ) -> None: ...

        @distributed_trace_async
        async def get_agent(
                self, 
                agent_id: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list_agents(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Agent]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_agent(
                self, 
                agent_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def update_agent(
                self, 
                agent_id: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                name: Optional[str] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                toolset: Optional[AsyncToolSet] = ..., 
                top_p: Optional[float] = ..., 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def update_agent(
                self, 
                agent_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...

        @overload
        async def update_agent(
                self, 
                agent_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Agent: ...


namespace azure.ai.agents.aio.operations

    class azure.ai.agents.aio.operations.FilesOperations(FilesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> FileInfo: ...

        @distributed_trace_async
        async def get_content(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def list(
                self, 
                *, 
                purpose: Optional[Union[str, FilePurpose]] = ..., 
                **kwargs: Any
            ) -> FileListResponse: ...

        @distributed_trace_async
        async def save(
                self, 
                file_id: str, 
                file_name: str, 
                target_dir: Optional[Union[str, Path]] = None
            ) -> None: ...

        @overload
        async def upload(
                self, 
                *, 
                file_path: str, 
                purpose: Union[str, FilePurpose], 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        async def upload(
                self, 
                *, 
                file: FileType, 
                filename: Optional[str] = ..., 
                purpose: Union[str, FilePurpose], 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        async def upload(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        async def upload_and_poll(
                self, 
                body: JSON, 
                *, 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        async def upload_and_poll(
                self, 
                *, 
                file: FileType, 
                filename: Optional[str] = ..., 
                polling_interval: float = 1, 
                purpose: Union[str, FilePurpose], 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        async def upload_and_poll(
                self, 
                *, 
                file_path: str, 
                polling_interval: float = 1, 
                purpose: Union[str, FilePurpose], 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...


    class azure.ai.agents.aio.operations.MessagesOperations(MessagesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                *, 
                attachments: Optional[List[MessageAttachment]] = ..., 
                content: MessageInputContent, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                role: Union[str, MessageRole], 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @distributed_trace_async
        async def delete(
                self, 
                thread_id: str, 
                message_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                thread_id: str, 
                message_id: str, 
                **kwargs: Any
            ) -> ThreadMessage: ...

        async def get_last_message_by_role(
                self, 
                thread_id: str, 
                role: MessageRole, 
                **kwargs
            ) -> Optional[ThreadMessage]: ...

        async def get_last_message_text_by_role(
                self, 
                thread_id: str, 
                role: MessageRole, 
                **kwargs
            ) -> Optional[MessageTextContent]: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ThreadMessage]: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                message_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                message_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                message_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...


    class azure.ai.agents.aio.operations.RunStepsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                thread_id: str, 
                run_id: str, 
                step_id: str, 
                *, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> RunStep: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                before: Optional[str] = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RunStep]: ...


    class azure.ai.agents.aio.operations.RunsOperations(RunsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                thread_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def create(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace_async
        async def create_and_process(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                polling_interval: int = 1, 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                run_handler: Optional[AsyncRunHandler] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                toolset: Optional[AsyncToolSet] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace_async
        async def get(
                self, 
                thread_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ThreadRun]: ...

        @overload
        async def stream(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                event_handler: None = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> AsyncAgentRunStream[AsyncAgentEventHandler]: ...

        @overload
        async def stream(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                event_handler: BaseAsyncAgentEventHandlerT, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> AsyncAgentRunStream[BaseAsyncAgentEventHandlerT]: ...

        @overload
        async def stream(
                self, 
                thread_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: None = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> AsyncAgentRunStream[AsyncAgentEventHandler]: ...

        @overload
        async def stream(
                self, 
                thread_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAsyncAgentEventHandlerT, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> AsyncAgentRunStream[BaseAsyncAgentEventHandlerT]: ...

        @overload
        async def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                tool_approvals: Optional[List[ToolApproval]] = ..., 
                tool_outputs: Optional[List[StructuredToolOutput]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def submit_tool_outputs_stream(
                self, 
                thread_id: str, 
                run_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAsyncAgentEventHandler, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def submit_tool_outputs_stream(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAsyncAgentEventHandler, 
                tool_approvals: Optional[List[ToolApproval]] = ..., 
                tool_outputs: Optional[List[StructuredToolOutput]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...


    class azure.ai.agents.aio.operations.ThreadsOperations(ThreadsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                *, 
                content_type: str = "application/json", 
                messages: Optional[List[ThreadMessageOptions]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @distributed_trace_async
        async def delete(
                self, 
                thread_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                thread_id: str, 
                **kwargs: Any
            ) -> AgentThread: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentThread]: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        async def update(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...


    class azure.ai.agents.aio.operations.VectorStoreFileBatchesOperations(VectorStoreFileBatchesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                file_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                file_ids: Optional[List[str]] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @distributed_trace_async
        async def get(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @distributed_trace
        def list_files(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[Union[str, VectorStoreFileStatusFilter]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VectorStoreFile]: ...


    class azure.ai.agents.aio.operations.VectorStoreFilesOperations(VectorStoreFilesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        async def create(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        async def create_and_poll(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @distributed_trace_async
        async def delete(
                self, 
                vector_store_id: str, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vector_store_id: str, 
                file_id: str, 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @distributed_trace
        def list(
                self, 
                vector_store_id: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[Union[str, VectorStoreFileStatusFilter]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VectorStoreFile]: ...


    class azure.ai.agents.aio.operations.VectorStoresOperations(VectorStoresOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                file_ids: Optional[List[str]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                store_configuration: Optional[VectorStoreConfiguration] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def create_and_poll(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def create_and_poll(
                self, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                file_ids: Optional[List[str]] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def create_and_poll(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @distributed_trace_async
        async def delete(
                self, 
                vector_store_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                vector_store_id: str, 
                **kwargs: Any
            ) -> VectorStore: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VectorStore]: ...

        @overload
        async def modify(
                self, 
                vector_store_id: str, 
                *, 
                content_type: str = "application/json", 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def modify(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        async def modify(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...


namespace azure.ai.agents.models

    def azure.ai.agents.models.get_tool_definitions(tools: List[Tool]) -> List[ToolDefinition]: ...


    def azure.ai.agents.models.get_tool_resources(tools: List[Tool]) -> ToolResources: ...


    class azure.ai.agents.models.AISearchIndexResource(_Model):
        filter: Optional[str]
        index_asset_id: Optional[str]
        index_connection_id: Optional[str]
        index_name: Optional[str]
        query_type: Optional[Union[str, AzureAISearchQueryType]]
        top_k: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                index_asset_id: Optional[str] = ..., 
                index_connection_id: Optional[str] = ..., 
                index_name: Optional[str] = ..., 
                query_type: Optional[Union[str, AzureAISearchQueryType]] = ..., 
                top_k: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ActivityFunctionDefinition(_Model):
        description: Optional[str]
        parameters: ActivityFunctionParameters

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: ActivityFunctionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ActivityFunctionParameters(_Model):
        additional_properties: Optional[bool]
        properties: dict[str, FunctionArgument]
        required: list[str]
        type: Literal["object"]

        @overload
        def __init__(
                self, 
                *, 
                additional_properties: Optional[bool] = ..., 
                properties: dict[str, FunctionArgument], 
                required: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.Agent(_Model):
        created_at: datetime
        description: str
        id: str
        instructions: str
        metadata: dict[str, str]
        model: str
        name: str
        object: Literal["assistant"]
        response_format: Optional[AgentsResponseFormatOption]
        temperature: float
        tool_resources: ToolResources
        tools: list[ToolDefinition]
        top_p: float

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                description: str, 
                id: str, 
                instructions: str, 
                metadata: dict[str, str], 
                model: str, 
                name: str, 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: float, 
                tool_resources: ToolResources, 
                tools: list[ToolDefinition], 
                top_p: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentErrorDetail(_Model):
        code: Optional[str]
        message: Optional[str]
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentEventHandler(BaseAgentEventHandler[Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]]):

        def __init__(self) -> None: ...

        def __next__(self) -> T: ...

        def __next_impl__(self) -> bytes: ...

        def initialize(
                self, 
                response_iterator: Iterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAgentEventHandler[T], bool], Any]
            ) -> None: ...

        def on_done(self) -> Optional[EventFunctionReturnT]: ...

        def on_error(self, data: str) -> Optional[EventFunctionReturnT]: ...

        def on_message_delta(self, delta: MessageDeltaChunk) -> Optional[EventFunctionReturnT]: ...

        def on_run_step(self, step: RunStep) -> Optional[EventFunctionReturnT]: ...

        def on_run_step_delta(self, delta: RunStepDeltaChunk) -> Optional[EventFunctionReturnT]: ...

        def on_thread_message(self, message: ThreadMessage) -> Optional[EventFunctionReturnT]: ...

        def on_thread_run(self, run: ThreadRun) -> Optional[EventFunctionReturnT]: ...

        def on_unhandled_event(
                self, 
                event_type: str, 
                event_data: str
            ) -> Optional[EventFunctionReturnT]: ...

        def set_max_retry(self, max_retry: int) -> None: ...

        def until_done(self) -> None: ...


    class azure.ai.agents.models.AgentRunStream(Generic[BaseAgentEventHandlerT]): implements ContextManager 

        def __init__(
                self, 
                response_iterator: Iterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAgentEventHandlerT, bool], Any], 
                event_handler: BaseAgentEventHandlerT
            ): ...


    class azure.ai.agents.models.AgentStreamEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DONE = "done"
        ERROR = "error"
        THREAD_CREATED = "thread.created"
        THREAD_MESSAGE_COMPLETED = "thread.message.completed"
        THREAD_MESSAGE_CREATED = "thread.message.created"
        THREAD_MESSAGE_DELTA = "thread.message.delta"
        THREAD_MESSAGE_INCOMPLETE = "thread.message.incomplete"
        THREAD_MESSAGE_IN_PROGRESS = "thread.message.in_progress"
        THREAD_RUN_CANCELLED = "thread.run.cancelled"
        THREAD_RUN_CANCELLING = "thread.run.cancelling"
        THREAD_RUN_COMPLETED = "thread.run.completed"
        THREAD_RUN_CREATED = "thread.run.created"
        THREAD_RUN_EXPIRED = "thread.run.expired"
        THREAD_RUN_FAILED = "thread.run.failed"
        THREAD_RUN_INCOMPLETE = "thread.run.incomplete"
        THREAD_RUN_IN_PROGRESS = "thread.run.in_progress"
        THREAD_RUN_QUEUED = "thread.run.queued"
        THREAD_RUN_REQUIRES_ACTION = "thread.run.requires_action"
        THREAD_RUN_STEP_CANCELLED = "thread.run.step.cancelled"
        THREAD_RUN_STEP_COMPLETED = "thread.run.step.completed"
        THREAD_RUN_STEP_CREATED = "thread.run.step.created"
        THREAD_RUN_STEP_DELTA = "thread.run.step.delta"
        THREAD_RUN_STEP_EXPIRED = "thread.run.step.expired"
        THREAD_RUN_STEP_FAILED = "thread.run.step.failed"
        THREAD_RUN_STEP_IN_PROGRESS = "thread.run.step.in_progress"


    class azure.ai.agents.models.AgentThread(_Model):
        created_at: datetime
        id: str
        metadata: dict[str, str]
        object: Literal["thread"]
        tool_resources: ToolResources

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                id: str, 
                metadata: dict[str, str], 
                tool_resources: ToolResources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentThreadCreationOptions(_Model):
        messages: Optional[list[ThreadMessageOptions]]
        metadata: Optional[dict[str, str]]
        tool_resources: Optional[ToolResources]

        @overload
        def __init__(
                self, 
                *, 
                messages: Optional[list[ThreadMessageOptions]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                tool_resources: Optional[ToolResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentV1Error(_Model):
        error: AgentErrorDetail

        @overload
        def __init__(
                self, 
                *, 
                error: AgentErrorDetail
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentsNamedToolChoice(_Model):
        function: Optional[FunctionName]
        type: Union[str, AgentsNamedToolChoiceType]

        @overload
        def __init__(
                self, 
                *, 
                function: Optional[FunctionName] = ..., 
                type: Union[str, AgentsNamedToolChoiceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentsNamedToolChoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AI_SEARCH = "azure_ai_search"
        BING_CUSTOM_SEARCH = "bing_custom_search"
        BING_GROUNDING = "bing_grounding"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CONNECTED_AGENT = "connected_agent"
        DEEP_RESEARCH = "deep_research"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        MCP = "mcp"
        MICROSOFT_FABRIC = "fabric_dataagent"
        SHAREPOINT = "sharepoint_grounding"


    class azure.ai.agents.models.AgentsResponseFormat(_Model):
        type: Optional[Union[str, ResponseFormat]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResponseFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AgentsResponseFormatMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"


    class azure.ai.agents.models.AgentsToolChoiceOptionMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"


    class azure.ai.agents.models.AsyncAgentEventHandler(BaseAsyncAgentEventHandler[Tuple[str, StreamEventData, Optional[EventFunctionReturnT]]]):

        async def __anext__(self) -> T: ...

        async def __anext_impl__(self) -> bytes: ...

        def __init__(self) -> None: ...

        def initialize(
                self, 
                response_iterator: AsyncIterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAsyncAgentEventHandler[T], bool], Awaitable[Any]]
            ): ...

        async def on_done(self) -> Optional[EventFunctionReturnT]: ...

        async def on_error(self, data: str) -> Optional[EventFunctionReturnT]: ...

        async def on_message_delta(self, delta: MessageDeltaChunk) -> Optional[EventFunctionReturnT]: ...

        async def on_run_step(self, step: RunStep) -> Optional[EventFunctionReturnT]: ...

        async def on_run_step_delta(self, delta: RunStepDeltaChunk) -> Optional[EventFunctionReturnT]: ...

        async def on_thread_message(self, message: ThreadMessage) -> Optional[EventFunctionReturnT]: ...

        async def on_thread_run(self, run: ThreadRun) -> Optional[EventFunctionReturnT]: ...

        async def on_unhandled_event(
                self, 
                event_type: str, 
                event_data: str
            ) -> Optional[EventFunctionReturnT]: ...

        def set_max_retry(self, max_retry: int) -> None: ...

        async def until_done(self) -> None: ...


    class azure.ai.agents.models.AsyncAgentRunStream(Generic[BaseAsyncAgentEventHandlerT]): implements AsyncContextManager 

        def __init__(
                self, 
                response_iterator: AsyncIterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAsyncAgentEventHandlerT, bool], Awaitable[Any]], 
                event_handler: BaseAsyncAgentEventHandlerT
            ): ...


    class azure.ai.agents.models.AsyncFunctionTool(BaseFunctionTool):
        property definitions: List[FunctionToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, functions: Set[Callable[, Any]]): ...

        def add_functions(self, extra_functions: Set[Callable[, Any]]) -> None: ...

        async def execute(self, tool_call: RequiredFunctionToolCall) -> Any: ...


    class azure.ai.agents.models.AsyncRunHandler:

        async def submit_function_call_output(
                self, 
                *, 
                run: ThreadRun, 
                tool_call: RequiredFunctionToolCall, 
                tool_call_details: RequiredFunctionToolCallDetails, 
                **kwargs: Any
            ) -> Any: ...

        def submit_mcp_tool_approval(
                self, 
                *, 
                run: ThreadRun, 
                tool_call: RequiredMcpToolCall, 
                **kwargs: Any
            ) -> ToolApproval: ...


    class azure.ai.agents.models.AsyncToolSet(BaseToolSet):
        property definitions: List[ToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self) -> None: ...

        def add(self, tool: Tool): ...

        async def execute_tool_calls(self, tool_calls: List[Any]) -> Any: ...

        def get_definitions_and_resources(self) -> Dict[str, Any]: ...

        @overload
        def get_tool(self, tool_type: Type[McpTool]) -> McpTool: ...

        @overload
        def get_tool(
                self, 
                tool_type: Type[McpTool], 
                *, 
                server_label: str
            ) -> McpTool: ...

        @overload
        def get_tool(self, tool_type: Type[ToolT]) -> ToolT: ...

        @overload
        def remove(self, tool_type: Type[Tool]) -> None: ...

        @overload
        def remove(
                self, 
                tool_type: Type[OpenApiTool], 
                *, 
                name: str
            ) -> None: ...

        @overload
        def remove(
                self, 
                tool_type: Type[McpTool], 
                *, 
                server_label: str
            ) -> None: ...

        def validate_tool_type(self, tool: Tool) -> None: ...


    class azure.ai.agents.models.AzureAISearchQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"
        SIMPLE = "simple"
        VECTOR = "vector"
        VECTOR_SEMANTIC_HYBRID = "vector_semantic_hybrid"
        VECTOR_SIMPLE_HYBRID = "vector_simple_hybrid"


    class azure.ai.agents.models.AzureAISearchTool(Tool[AzureAISearchToolDefinition]):
        property definitions: List[AzureAISearchToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                index_connection_id: str, 
                index_name: str, 
                query_type: AzureAISearchQueryType = AzureAISearchQueryType.SIMPLE, 
                filter: str = "", 
                top_k: int = 5, 
                index_asset_id: Optional[str] = None
            ): ...

        def execute(self, tool_call: Any): ...


    class azure.ai.agents.models.AzureAISearchToolDefinition(ToolDefinition, discriminator='azure_ai_search'):
        type: Literal["azure_ai_search"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AzureAISearchToolResource(_Model):
        index_list: Optional[list[AISearchIndexResource]]

        @overload
        def __init__(
                self, 
                *, 
                index_list: Optional[list[AISearchIndexResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AzureFunctionBinding(_Model):
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


    class azure.ai.agents.models.AzureFunctionDefinition(_Model):
        function: FunctionDefinition
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding

        @overload
        def __init__(
                self, 
                *, 
                function: FunctionDefinition, 
                input_binding: AzureFunctionBinding, 
                output_binding: AzureFunctionBinding
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AzureFunctionStorageQueue(_Model):
        queue_name: str
        storage_service_endpoint: str

        @overload
        def __init__(
                self, 
                *, 
                queue_name: str, 
                storage_service_endpoint: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AzureFunctionTool(Tool[AzureFunctionToolDefinition]):
        property definitions: List[AzureFunctionToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                name: str, 
                description: str, 
                parameters: Dict[str, Any], 
                input_queue: AzureFunctionStorageQueue, 
                output_queue: AzureFunctionStorageQueue
            ) -> None: ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.AzureFunctionToolCallDetails(_Model):
        arguments: Optional[str]
        name: Optional[str]
        output: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[str] = ..., 
                name: Optional[str] = ..., 
                output: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.AzureFunctionToolDefinition(ToolDefinition, discriminator='azure_function'):
        azure_function: AzureFunctionDefinition
        type: Literal["azure_function"]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BaseAgentEventHandler(Iterator[T]):

        def __init__(self) -> None: ...

        def __next__(self) -> T: ...

        def __next_impl__(self) -> bytes: ...

        def initialize(
                self, 
                response_iterator: Iterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAgentEventHandler[T], bool], Any]
            ) -> None: ...

        def until_done(self) -> None: ...


    class azure.ai.agents.models.BaseAsyncAgentEventHandler(AsyncIterator[T]):

        async def __anext__(self) -> T: ...

        async def __anext_impl__(self) -> bytes: ...

        def __init__(self) -> None: ...

        def initialize(
                self, 
                response_iterator: AsyncIterator[bytes], 
                submit_tool_outputs: Callable[[ThreadRun, BaseAsyncAgentEventHandler[T], bool], Awaitable[Any]]
            ): ...

        async def until_done(self) -> None: ...


    class azure.ai.agents.models.BingCustomSearchConfiguration(_Model):
        connection_id: str
        count: Optional[int]
        freshness: Optional[str]
        instance_name: str
        market: Optional[str]
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                instance_name: str, 
                market: Optional[str] = ..., 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BingCustomSearchTool(Tool[BingCustomSearchToolDefinition]):
        property definitions: List[BingCustomSearchToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                connection_id: str, 
                instance_name: str, 
                market: str = "", 
                set_lang: str = "", 
                count: int = 5, 
                freshness: str = ""
            ): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.BingCustomSearchToolDefinition(ToolDefinition, discriminator='bing_custom_search'):
        bing_custom_search: BingCustomSearchToolParameters
        type: Literal["bing_custom_search"]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search: BingCustomSearchToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BingCustomSearchToolParameters(_Model):
        search_configurations: list[BingCustomSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingCustomSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BingGroundingSearchConfiguration(_Model):
        connection_id: str
        count: Optional[int]
        freshness: Optional[str]
        market: Optional[str]
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                market: Optional[str] = ..., 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BingGroundingSearchToolParameters(_Model):
        search_configurations: list[BingGroundingSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingGroundingSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BingGroundingTool(Tool[BingGroundingToolDefinition]):
        property definitions: List[BingGroundingToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                connection_id: str, 
                market: str = "", 
                set_lang: str = "", 
                count: int = 5, 
                freshness: str = ""
            ): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.BingGroundingToolDefinition(ToolDefinition, discriminator='bing_grounding'):
        bing_grounding: BingGroundingSearchToolParameters
        type: Literal["bing_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: BingGroundingSearchToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BrowserAutomationTool(Tool[BrowserAutomationToolDefinition]):
        property definitions: List[BrowserAutomationToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, connection_id: str): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.BrowserAutomationToolCallDetails(_Model):
        input: str
        output: str
        steps: list[BrowserAutomationToolCallStep]

        @overload
        def __init__(
                self, 
                *, 
                input: str, 
                output: str, 
                steps: list[BrowserAutomationToolCallStep]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BrowserAutomationToolCallStep(_Model):
        current_state: str
        last_step_result: str
        next_step: str

        @overload
        def __init__(
                self, 
                *, 
                current_state: str, 
                last_step_result: str, 
                next_step: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BrowserAutomationToolConnectionParameters(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BrowserAutomationToolDefinition(ToolDefinition, discriminator='browser_automation'):
        browser_automation: BrowserAutomationToolParameters
        type: Literal["browser_automation"]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation: BrowserAutomationToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.BrowserAutomationToolParameters(_Model):
        connection: BrowserAutomationToolConnectionParameters

        @overload
        def __init__(
                self, 
                *, 
                connection: BrowserAutomationToolConnectionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ClickAction(ComputerUseAction, discriminator='click'):
        button: Union[str, MouseButton]
        type: Literal["click"]
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                button: Union[str, MouseButton], 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.CodeInterpreterTool(Tool[CodeInterpreterToolDefinition]):
        property definitions: List[CodeInterpreterToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                file_ids: Optional[List[str]] = None, 
                data_sources: Optional[List[VectorStoreDataSource]] = None
            ): ...

        def add_data_source(self, data_source: VectorStoreDataSource) -> None: ...

        def add_file(self, file_id: str) -> None: ...

        def execute(self, tool_call: Any) -> Any: ...

        def remove_data_source(self, asset_identifier: str) -> None: ...

        def remove_file(self, file_id: str) -> None: ...


    class azure.ai.agents.models.CodeInterpreterToolDefinition(ToolDefinition, discriminator='code_interpreter'):
        type: Literal["code_interpreter"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.CodeInterpreterToolResource(_Model):
        data_sources: Optional[list[VectorStoreDataSource]]
        file_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                data_sources: Optional[list[VectorStoreDataSource]] = ..., 
                file_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ComputerScreenshot(_Model):
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


    class azure.ai.agents.models.ComputerToolOutput(StructuredToolOutput, discriminator='computer_call_output'):
        acknowledged_safety_checks: Optional[list[SafetyCheck]]
        output: ComputerScreenshot
        tool_call_id: str
        type: Literal["computer_call_output"]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[SafetyCheck]] = ..., 
                output: ComputerScreenshot, 
                tool_call_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ComputerUseAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ComputerUseEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROWSER = "browser"
        LINUX = "linux"
        MAC = "mac"
        WINDOWS = "windows"


    class azure.ai.agents.models.ComputerUseTool(Tool[ComputerUseToolDefinition]):
        property definitions: List[ComputerUseToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                display_width: int, 
                display_height: int, 
                environment: str
            ): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.ComputerUseToolDefinition(ToolDefinition, discriminator='computer_use_preview'):
        computer_use_preview: ComputerUseToolParameters
        type: Literal["computer_use_preview"]

        @overload
        def __init__(
                self, 
                *, 
                computer_use_preview: ComputerUseToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ComputerUseToolParameters(_Model):
        display_height: int
        display_width: int
        environment: Union[str, ComputerUseEnvironment]

        @overload
        def __init__(
                self, 
                *, 
                display_height: int, 
                display_width: int, 
                environment: Union[str, ComputerUseEnvironment]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ConnectedAgentDetails(_Model):
        description: str
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ConnectedAgentTool(Tool[ConnectedAgentToolDefinition]):
        property definitions: List[ConnectedAgentToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                id: str, 
                name: str, 
                description: str
            ): ...

        def execute(self, tool_call: Any) -> None: ...


    class azure.ai.agents.models.ConnectedAgentToolDefinition(ToolDefinition, discriminator='connected_agent'):
        connected_agent: ConnectedAgentDetails
        type: Literal["connected_agent"]

        @overload
        def __init__(
                self, 
                *, 
                connected_agent: ConnectedAgentDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.CoordinatePoint(_Model):
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


    class azure.ai.agents.models.DeepResearchBingGroundingConnection(_Model):
        connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.DeepResearchDetails(_Model):
        bing_grounding_connections: list[DeepResearchBingGroundingConnection]
        model: str

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding_connections: list[DeepResearchBingGroundingConnection], 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.DeepResearchTool(Tool[DeepResearchToolDefinition]):
        property definitions: List[DeepResearchToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                bing_grounding_connection_id: str, 
                deep_research_model: str
            ): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.DeepResearchToolDefinition(ToolDefinition, discriminator='deep_research'):
        deep_research: DeepResearchDetails
        type: Literal["deep_research"]

        @overload
        def __init__(
                self, 
                *, 
                deep_research: DeepResearchDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.DoneEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DONE = "done"


    class azure.ai.agents.models.DoubleClickAction(ComputerUseAction, discriminator='double_click'):
        type: Literal["double_click"]
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


    class azure.ai.agents.models.DragAction(ComputerUseAction, discriminator='drag'):
        path: list[CoordinatePoint]
        type: Literal["drag"]

        @overload
        def __init__(
                self, 
                *, 
                path: list[CoordinatePoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ErrorEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"


    class azure.ai.agents.models.FabricDataAgentToolParameters(_Model):
        connection_list: Optional[list[ToolConnection]]

        @overload
        def __init__(
                self, 
                *, 
                connection_list: Optional[list[ToolConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FabricTool(ConnectionTool[MicrosoftFabricToolDefinition]):
        property definitions: List[MicrosoftFabricToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, connection_id: str): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.FileInfo(_Model):
        bytes: int
        created_at: datetime
        filename: str
        id: str
        object: Literal["file"]
        purpose: Union[str, FilePurpose]
        status: Optional[Union[str, FileState]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bytes: int, 
                created_at: datetime, 
                filename: str, 
                id: str, 
                purpose: Union[str, FilePurpose], 
                status: Optional[Union[str, FileState]] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileListResponse(_Model):
        data: list[FileInfo]
        object: Literal["list"]

        @overload
        def __init__(
                self, 
                *, 
                data: list[FileInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FilePurpose(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTS = "assistants"
        AGENTS_OUTPUT = "assistants_output"
        VISION = "vision"


    class azure.ai.agents.models.FileSearchRankingOptions(_Model):
        ranker: str
        score_threshold: float

        @overload
        def __init__(
                self, 
                *, 
                ranker: str, 
                score_threshold: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileSearchTool(Tool[FileSearchToolDefinition]):
        property definitions: List[FileSearchToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, vector_store_ids: Optional[List[str]] = None): ...

        def add_vector_store(self, store_id: str) -> None: ...

        def execute(self, tool_call: Any) -> Any: ...

        def remove_vector_store(self, store_id: str) -> None: ...


    class azure.ai.agents.models.FileSearchToolCallContent(_Model):
        text: str
        type: Literal["text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileSearchToolDefinition(ToolDefinition, discriminator='file_search'):
        file_search: Optional[FileSearchToolDefinitionDetails]
        type: Literal["file_search"]

        @overload
        def __init__(
                self, 
                *, 
                file_search: Optional[FileSearchToolDefinitionDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileSearchToolDefinitionDetails(_Model):
        max_num_results: Optional[int]
        ranking_options: Optional[FileSearchRankingOptions]

        @overload
        def __init__(
                self, 
                *, 
                max_num_results: Optional[int] = ..., 
                ranking_options: Optional[FileSearchRankingOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileSearchToolResource(_Model):
        vector_store_ids: Optional[list[str]]
        vector_stores: Optional[list[VectorStoreConfigurations]]

        @overload
        def __init__(
                self, 
                *, 
                vector_store_ids: Optional[list[str]] = ..., 
                vector_stores: Optional[list[VectorStoreConfigurations]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FileState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "deleted"
        DELETING = "deleting"
        ERROR = "error"
        PENDING = "pending"
        PROCESSED = "processed"
        RUNNING = "running"
        UPLOADED = "uploaded"


    class azure.ai.agents.models.FunctionArgument(_Model):
        description: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FunctionDefinition(_Model):
        description: Optional[str]
        name: str
        parameters: Any

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FunctionName(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.FunctionTool(BaseFunctionTool):
        property definitions: List[FunctionToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, functions: Set[Callable[, Any]]): ...

        def add_functions(self, extra_functions: Set[Callable[, Any]]) -> None: ...

        def execute(self, tool_call: RequiredFunctionToolCall) -> Any: ...


    class azure.ai.agents.models.FunctionToolDefinition(ToolDefinition, discriminator='function'):
        function: FunctionDefinition
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                function: FunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ImageDetailLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HIGH = "high"
        LOW = "low"


    class azure.ai.agents.models.IncompleteDetailsReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX_COMPLETION_TOKENS = "max_completion_tokens"
        MAX_PROMPT_TOKENS = "max_prompt_tokens"


    class azure.ai.agents.models.IncompleteRunDetails(_Model):
        reason: Union[str, IncompleteDetailsReason]

        @overload
        def __init__(
                self, 
                *, 
                reason: Union[str, IncompleteDetailsReason]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.KeyPressAction(ComputerUseAction, discriminator='keypress'):
        keys_property: list[str]
        type: Literal["keypress"]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ListSortOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCENDING = "asc"
        DESCENDING = "desc"


    class azure.ai.agents.models.MCPApprovalPerTool(_Model):
        always: Optional[MCPToolList]
        never: Optional[MCPToolList]

        @overload
        def __init__(
                self, 
                *, 
                always: Optional[MCPToolList] = ..., 
                never: Optional[MCPToolList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MCPToolDefinition(ToolDefinition, discriminator='mcp'):
        allowed_tools: Optional[list[str]]
        server_label: str
        server_url: str
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[list[str]] = ..., 
                server_label: str, 
                server_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MCPToolList(_Model):
        tool_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                tool_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MCPToolResource(_Model):
        headers: dict[str, str]
        require_approval: Optional[MCPRequiredApproval]
        server_label: str

        @overload
        def __init__(
                self, 
                *, 
                headers: dict[str, str], 
                require_approval: Optional[MCPRequiredApproval] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.McpTool(Tool[MCPToolDefinition]):
        property allowed_tools: List[str]    # Read-only
        property definitions: List[MCPToolDefinition]    # Read-only
        property headers: Dict[str, str]    # Read-only
        property resources: ToolResources    # Read-only
        property server_label: str    # Read-only
        property server_url: str    # Read-only

        def __init__(
                self, 
                server_label: str, 
                server_url: str, 
                allowed_tools: Optional[List[str]] = None
            ) -> None: ...

        def allow_tool(self, tool_name: str) -> None: ...

        def disallow_tool(self, tool_name: str) -> None: ...

        def execute(self, tool_call: Any) -> None: ...

        def set_approval_mode(self, require_approval: str) -> None: ...

        def update_headers(
                self, 
                key: str, 
                value: str
            ) -> None: ...


    class azure.ai.agents.models.MessageAttachment(MessageAttachmentGenerated):

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                tools: List[FileSearchToolDefinition]
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                tools: List[CodeInterpreterToolDefinition]
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                tools: List[MessageAttachmentToolDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageBlockType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE_FILE = "image_file"
        IMAGE_URL = "image_url"
        TEXT = "text"


    class azure.ai.agents.models.MessageContent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDelta(_Model):
        content: list[MessageDeltaContent]
        role: Union[str, MessageRole]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageDeltaContent], 
                role: Union[str, MessageRole]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaChunk(MessageDeltaChunkGenerated):
        property text: str    # Read-only

        @overload
        def __init__(
                self, 
                *, 
                delta: MessageDelta, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaContent(_Model):
        index: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaImageFileContent(MessageDeltaContent, discriminator='image_file'):
        image_file: Optional[MessageDeltaImageFileContentObject]
        index: int
        type: Literal["image_file"]

        @overload
        def __init__(
                self, 
                *, 
                image_file: Optional[MessageDeltaImageFileContentObject] = ..., 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaImageFileContentObject(_Model):
        file_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextAnnotation(_Model):
        index: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextContent(MessageDeltaContent, discriminator='text'):
        index: int
        text: Optional[MessageDeltaTextContentObject]
        type: Literal["text"]

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                text: Optional[MessageDeltaTextContentObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextContentObject(_Model):
        annotations: Optional[list[MessageDeltaTextAnnotation]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[list[MessageDeltaTextAnnotation]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextFileCitationAnnotation(MessageDeltaTextAnnotation, discriminator='file_citation'):
        end_index: Optional[int]
        file_citation: Optional[MessageDeltaTextFileCitationAnnotationObject]
        index: int
        start_index: Optional[int]
        text: Optional[str]
        type: Literal["file_citation"]

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                file_citation: Optional[MessageDeltaTextFileCitationAnnotationObject] = ..., 
                index: int, 
                start_index: Optional[int] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextFileCitationAnnotationObject(_Model):
        file_id: Optional[str]
        quote: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ..., 
                quote: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextFilePathAnnotation(MessageDeltaTextAnnotation, discriminator='file_path'):
        end_index: Optional[int]
        file_path: Optional[MessageDeltaTextFilePathAnnotationObject]
        index: int
        start_index: Optional[int]
        text: Optional[str]
        type: Literal["file_path"]

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                file_path: Optional[MessageDeltaTextFilePathAnnotationObject] = ..., 
                index: int, 
                start_index: Optional[int] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextFilePathAnnotationObject(_Model):
        file_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextUrlCitationAnnotation(MessageDeltaTextAnnotation, discriminator='url_citation'):
        end_index: Optional[int]
        index: int
        start_index: Optional[int]
        type: Literal["url_citation"]
        url_citation: MessageDeltaTextUrlCitationDetails

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                index: int, 
                start_index: Optional[int] = ..., 
                url_citation: MessageDeltaTextUrlCitationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageDeltaTextUrlCitationDetails(_Model):
        title: Optional[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                title: Optional[str] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageImageFileContent(MessageContent, discriminator='image_file'):
        image_file: MessageImageFileDetails
        type: Literal["image_file"]

        @overload
        def __init__(
                self, 
                *, 
                image_file: MessageImageFileDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageImageFileDetails(_Model):
        file_id: str

        @overload
        def __init__(
                self, 
                *, 
                file_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageImageFileParam(_Model):
        detail: Optional[Union[str, ImageDetailLevel]]
        file_id: str

        @overload
        def __init__(
                self, 
                *, 
                detail: Optional[Union[str, ImageDetailLevel]] = ..., 
                file_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageImageUrlParam(_Model):
        detail: Optional[Union[str, ImageDetailLevel]]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                detail: Optional[Union[str, ImageDetailLevel]] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageIncompleteDetails(_Model):
        reason: Union[str, MessageIncompleteDetailsReason]

        @overload
        def __init__(
                self, 
                *, 
                reason: Union[str, MessageIncompleteDetailsReason]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageIncompleteDetailsReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_FILTER = "content_filter"
        MAX_TOKENS = "max_tokens"
        RUN_CANCELLED = "run_cancelled"
        RUN_EXPIRED = "run_expired"
        RUN_FAILED = "run_failed"


    class azure.ai.agents.models.MessageInputContentBlock(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageInputImageFileBlock(MessageInputContentBlock, discriminator='image_file'):
        image_file: MessageImageFileParam
        type: Literal[MessageBlockType.IMAGE_FILE]

        @overload
        def __init__(
                self, 
                *, 
                image_file: MessageImageFileParam
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageInputImageUrlBlock(MessageInputContentBlock, discriminator='image_url'):
        image_url: MessageImageUrlParam
        type: Literal[MessageBlockType.IMAGE_URL]

        @overload
        def __init__(
                self, 
                *, 
                image_url: MessageImageUrlParam
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageInputTextBlock(MessageInputContentBlock, discriminator='text'):
        text: str
        type: Literal[MessageBlockType.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "assistant"
        USER = "user"


    class azure.ai.agents.models.MessageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.MessageStreamEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THREAD_MESSAGE_COMPLETED = "thread.message.completed"
        THREAD_MESSAGE_CREATED = "thread.message.created"
        THREAD_MESSAGE_DELTA = "thread.message.delta"
        THREAD_MESSAGE_INCOMPLETE = "thread.message.incomplete"
        THREAD_MESSAGE_IN_PROGRESS = "thread.message.in_progress"


    class azure.ai.agents.models.MessageTextAnnotation(_Model):
        text: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                text: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextContent(MessageContent, discriminator='text'):
        text: MessageTextDetails
        type: Literal["text"]

        @overload
        def __init__(
                self, 
                *, 
                text: MessageTextDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextDetails(_Model):
        annotations: list[MessageTextAnnotation]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                annotations: list[MessageTextAnnotation], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextFileCitationAnnotation(MessageTextAnnotation, discriminator='file_citation'):
        end_index: Optional[int]
        file_citation: MessageTextFileCitationDetails
        start_index: Optional[int]
        text: str
        type: Literal["file_citation"]

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                file_citation: MessageTextFileCitationDetails, 
                start_index: Optional[int] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextFileCitationDetails(_Model):
        file_id: str
        quote: str

        @overload
        def __init__(
                self, 
                *, 
                file_id: str, 
                quote: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextFilePathAnnotation(MessageTextAnnotation, discriminator='file_path'):
        end_index: Optional[int]
        file_path: MessageTextFilePathDetails
        start_index: Optional[int]
        text: str
        type: Literal["file_path"]

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                file_path: MessageTextFilePathDetails, 
                start_index: Optional[int] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextFilePathDetails(_Model):
        file_id: str

        @overload
        def __init__(
                self, 
                *, 
                file_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextUrlCitationAnnotation(MessageTextAnnotation, discriminator='url_citation'):
        end_index: Optional[int]
        start_index: Optional[int]
        text: str
        type: Literal["url_citation"]
        url_citation: MessageTextUrlCitationDetails

        @overload
        def __init__(
                self, 
                *, 
                end_index: Optional[int] = ..., 
                start_index: Optional[int] = ..., 
                text: str, 
                url_citation: MessageTextUrlCitationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MessageTextUrlCitationDetails(_Model):
        title: Optional[str]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                title: Optional[str] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MicrosoftFabricToolDefinition(ToolDefinition, discriminator='fabric_dataagent'):
        fabric_dataagent: FabricDataAgentToolParameters
        type: Literal["fabric_dataagent"]

        @overload
        def __init__(
                self, 
                *, 
                fabric_dataagent: FabricDataAgentToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.MouseButton(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACK = "back"
        FORWARD = "forward"
        LEFT = "left"
        RIGHT = "right"
        WHEEL = "wheel"


    class azure.ai.agents.models.MoveAction(ComputerUseAction, discriminator='move'):
        type: Literal["move"]
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


    class azure.ai.agents.models.OpenApiAnonymousAuthDetails(OpenApiAuthDetails, discriminator='anonymous'):
        type: Literal[OpenApiAuthType.ANONYMOUS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiAuthDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "anonymous"
        CONNECTION = "connection"
        MANAGED_IDENTITY = "managed_identity"


    class azure.ai.agents.models.OpenApiConnectionAuthDetails(OpenApiAuthDetails, discriminator='connection'):
        security_scheme: OpenApiConnectionSecurityScheme
        type: Literal[OpenApiAuthType.CONNECTION]

        @overload
        def __init__(
                self, 
                *, 
                security_scheme: OpenApiConnectionSecurityScheme
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiConnectionSecurityScheme(_Model):
        connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiFunctionDefinition(_Model):
        auth: OpenApiAuthDetails
        default_params: Optional[list[str]]
        description: Optional[str]
        functions: Optional[list[FunctionDefinition]]
        name: str
        spec: Any

        @overload
        def __init__(
                self, 
                *, 
                auth: OpenApiAuthDetails, 
                default_params: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                spec: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiManagedAuthDetails(OpenApiAuthDetails, discriminator='managed_identity'):
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


    class azure.ai.agents.models.OpenApiManagedSecurityScheme(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.OpenApiTool(Tool[OpenApiToolDefinition]):
        property definitions: List[OpenApiToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(
                self, 
                name: str, 
                description: Optional[str], 
                spec: Any, 
                auth: OpenApiAuthDetails, 
                default_parameters: Optional[List[str]] = None
            ) -> None: ...

        def add_definition(
                self, 
                name: str, 
                description: Optional[str], 
                spec: Any, 
                auth: Optional[OpenApiAuthDetails] = None, 
                default_parameters: Optional[List[str]] = None
            ) -> None: ...

        def execute(self, tool_call: Any) -> None: ...

        def remove_definition(self, name: str) -> None: ...


    class azure.ai.agents.models.OpenApiToolDefinition(ToolDefinition, discriminator='openapi'):
        openapi: OpenApiFunctionDefinition
        type: Literal["openapi"]

        @overload
        def __init__(
                self, 
                *, 
                openapi: OpenApiFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredComputerUseToolCall(RequiredToolCall, discriminator='computer_use_preview'):
        computer_use_preview: RequiredComputerUseToolCallDetails
        id: str
        type: Literal["computer_use_preview"]

        @overload
        def __init__(
                self, 
                *, 
                computer_use_preview: RequiredComputerUseToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredComputerUseToolCallDetails(_Model):
        action: ComputerUseAction
        pending_safety_checks: list[SafetyCheck]

        @overload
        def __init__(
                self, 
                *, 
                action: ComputerUseAction, 
                pending_safety_checks: list[SafetyCheck]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredFunctionToolCall(RequiredToolCall, discriminator='function'):
        function: RequiredFunctionToolCallDetails
        id: str
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                function: RequiredFunctionToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredFunctionToolCallDetails(_Model):
        arguments: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RequiredMcpToolCall(RequiredToolCall, discriminator='mcp'):
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal["mcp"]

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


    class azure.ai.agents.models.RequiredToolCall(_Model):
        id: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ResponseFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "json_object"
        TEXT = "text"


    class azure.ai.agents.models.ResponseFormatJsonSchema(_Model):
        description: Optional[str]
        name: str
        schema: Any

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                schema: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ResponseFormatJsonSchemaType(_Model):
        json_schema: ResponseFormatJsonSchema
        type: Literal["json_schema"]

        @overload
        def __init__(
                self, 
                *, 
                json_schema: ResponseFormatJsonSchema
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunAdditionalFieldList(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_SEARCH_CONTENTS = "step_details.tool_calls[*].file_search.results[*].content"


    class azure.ai.agents.models.RunCompletionUsage(_Model):
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                completion_tokens: int, 
                prompt_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunError(_Model):
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


    class azure.ai.agents.models.RunHandler:

        def submit_function_call_output(
                self, 
                *, 
                run: ThreadRun, 
                tool_call: RequiredFunctionToolCall, 
                tool_call_details: RequiredFunctionToolCallDetails, 
                **kwargs: Any
            ) -> Any: ...

        def submit_mcp_tool_approval(
                self, 
                *, 
                run: ThreadRun, 
                tool_call: RequiredMcpToolCall, 
                **kwargs: Any
            ) -> ToolApproval: ...


    class azure.ai.agents.models.RunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        COMPLETED = "completed"
        EXPIRED = "expired"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        QUEUED = "queued"
        REQUIRES_ACTION = "requires_action"


    class azure.ai.agents.models.RunStep(_Model):
        agent_id: str
        cancelled_at: datetime
        completed_at: datetime
        created_at: datetime
        expired_at: datetime
        failed_at: datetime
        id: str
        last_error: RunStepError
        metadata: dict[str, str]
        object: Literal["step"]
        run_id: str
        status: Union[str, RunStepStatus]
        step_details: RunStepDetails
        thread_id: str
        type: Union[str, RunStepType]
        usage: Optional[RunStepCompletionUsage]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: str, 
                cancelled_at: datetime, 
                completed_at: datetime, 
                created_at: datetime, 
                expired_at: datetime, 
                failed_at: datetime, 
                id: str, 
                last_error: RunStepError, 
                metadata: dict[str, str], 
                run_id: str, 
                status: Union[str, RunStepStatus], 
                step_details: RunStepDetails, 
                thread_id: str, 
                type: Union[str, RunStepType], 
                usage: Optional[RunStepCompletionUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepActivityDetails(RunStepDetails, discriminator='activities'):
        activities: list[RunStepDetailsActivity]
        type: Literal[RunStepType.ACTIVITIES]

        @overload
        def __init__(
                self, 
                *, 
                activities: list[RunStepDetailsActivity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepAzureAISearchToolCall(RunStepToolCall, discriminator='azure_ai_search'):
        azure_ai_search: dict[str, str]
        id: str
        type: Literal["azure_ai_search"]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: dict[str, str], 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepAzureFunctionToolCall(RunStepToolCall, discriminator='azure_function'):
        azure_function: AzureFunctionToolCallDetails
        id: str
        type: Literal["azure_function"]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepBingCustomSearchToolCall(RunStepToolCall, discriminator='bing_custom_search'):
        bing_custom_search: dict[str, str]
        id: str
        type: Literal["bing_custom_search"]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search: dict[str, str], 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepBingGroundingToolCall(RunStepToolCall, discriminator='bing_grounding'):
        bing_grounding: dict[str, str]
        id: str
        type: Literal["bing_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: dict[str, str], 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepBrowserAutomationToolCall(RunStepToolCall, discriminator='browser_automation'):
        browser_automation: BrowserAutomationToolCallDetails
        id: str
        type: Literal["browser_automation"]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation: BrowserAutomationToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCodeInterpreterImageOutput(RunStepCodeInterpreterToolCallOutput, discriminator='image'):
        image: RunStepCodeInterpreterImageReference
        type: Literal["image"]

        @overload
        def __init__(
                self, 
                *, 
                image: RunStepCodeInterpreterImageReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCodeInterpreterImageReference(_Model):
        file_id: str

        @overload
        def __init__(
                self, 
                *, 
                file_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCodeInterpreterLogOutput(RunStepCodeInterpreterToolCallOutput, discriminator='logs'):
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


    class azure.ai.agents.models.RunStepCodeInterpreterToolCall(RunStepToolCall, discriminator='code_interpreter'):
        code_interpreter: RunStepCodeInterpreterToolCallDetails
        id: str
        type: Literal["code_interpreter"]

        @overload
        def __init__(
                self, 
                *, 
                code_interpreter: RunStepCodeInterpreterToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCodeInterpreterToolCallDetails(_Model):
        input: str
        outputs: list[RunStepCodeInterpreterToolCallOutput]

        @overload
        def __init__(
                self, 
                *, 
                input: str, 
                outputs: list[RunStepCodeInterpreterToolCallOutput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCodeInterpreterToolCallOutput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepCompletionUsage(_Model):
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                completion_tokens: int, 
                prompt_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepComputerUseToolCall(RunStepToolCall, discriminator='computer_use_preview'):
        computer_use_preview: RunStepComputerUseToolCallDetails
        id: str
        type: Literal["computer_use_preview"]

        @overload
        def __init__(
                self, 
                *, 
                computer_use_preview: RunStepComputerUseToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepComputerUseToolCallDetails(_Model):
        acknowledged_safety_checks: Optional[list[SafetyCheck]]
        action: ComputerUseAction
        output: ComputerScreenshot
        pending_safety_checks: list[SafetyCheck]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[SafetyCheck]] = ..., 
                action: ComputerUseAction, 
                output: ComputerScreenshot, 
                pending_safety_checks: list[SafetyCheck]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepConnectedAgent(_Model):
        agent_id: Optional[str]
        arguments: Optional[str]
        name: Optional[str]
        output: Optional[str]
        run_id: Optional[str]
        thread_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                arguments: Optional[str] = ..., 
                name: Optional[str] = ..., 
                output: Optional[str] = ..., 
                run_id: Optional[str] = ..., 
                thread_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepConnectedAgentToolCall(RunStepToolCall, discriminator='connected_agent'):
        connected_agent: RunStepConnectedAgent
        id: str
        type: Literal["connected_agent"]

        @overload
        def __init__(
                self, 
                *, 
                connected_agent: RunStepConnectedAgent, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeepResearchToolCall(RunStepToolCall, discriminator='deep_research'):
        deep_research: RunStepDeepResearchToolCallDetails
        id: str
        type: Literal["deep_research"]

        @overload
        def __init__(
                self, 
                *, 
                deep_research: RunStepDeepResearchToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeepResearchToolCallDetails(_Model):
        input: str
        output: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                input: str, 
                output: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDelta(_Model):
        step_details: Optional[RunStepDeltaDetail]

        @overload
        def __init__(
                self, 
                *, 
                step_details: Optional[RunStepDeltaDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaAzureAISearchToolCall(RunStepDeltaToolCall, discriminator='azure_ai_search'):
        azure_ai_search: dict[str, str]
        id: str
        index: int
        type: Literal["azure_ai_search"]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: dict[str, str], 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaAzureFunctionToolCall(RunStepDeltaToolCall, discriminator='azure_function'):
        azure_function: AzureFunctionToolCallDetails
        id: str
        index: int
        type: Literal["azure_function"]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionToolCallDetails, 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaBingGroundingToolCall(RunStepDeltaToolCall, discriminator='bing_grounding'):
        bing_grounding: dict[str, str]
        id: str
        index: int
        type: Literal["bing_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: dict[str, str], 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaChunk(_Model):
        delta: RunStepDelta
        id: str
        object: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                delta: RunStepDelta, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterDetailItemObject(_Model):
        input: Optional[str]
        outputs: Optional[list[RunStepDeltaCodeInterpreterOutput]]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[str] = ..., 
                outputs: Optional[list[RunStepDeltaCodeInterpreterOutput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterImageOutput(RunStepDeltaCodeInterpreterOutput, discriminator='image'):
        image: Optional[RunStepDeltaCodeInterpreterImageOutputObject]
        index: int
        type: Literal["image"]

        @overload
        def __init__(
                self, 
                *, 
                image: Optional[RunStepDeltaCodeInterpreterImageOutputObject] = ..., 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterImageOutputObject(_Model):
        file_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterLogOutput(RunStepDeltaCodeInterpreterOutput, discriminator='logs'):
        index: int
        logs: Optional[str]
        type: Literal["logs"]

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                logs: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterOutput(_Model):
        index: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCodeInterpreterToolCall(RunStepDeltaToolCall, discriminator='code_interpreter'):
        code_interpreter: Optional[RunStepDeltaCodeInterpreterDetailItemObject]
        id: str
        index: int
        type: Literal["code_interpreter"]

        @overload
        def __init__(
                self, 
                *, 
                code_interpreter: Optional[RunStepDeltaCodeInterpreterDetailItemObject] = ..., 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaComputerUseDetails(_Model):
        acknowledged_safety_checks: Optional[list[SafetyCheck]]
        action: Optional[ComputerUseAction]
        output: Optional[ComputerScreenshot]
        pending_safety_checks: Optional[list[SafetyCheck]]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged_safety_checks: Optional[list[SafetyCheck]] = ..., 
                action: Optional[ComputerUseAction] = ..., 
                output: Optional[ComputerScreenshot] = ..., 
                pending_safety_checks: Optional[list[SafetyCheck]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaComputerUseToolCall(RunStepDeltaToolCall, discriminator='computer_use_preview'):
        computer_use_preview: Optional[RunStepDeltaComputerUseDetails]
        id: str
        index: int
        type: Literal["computer_use_preview"]

        @overload
        def __init__(
                self, 
                *, 
                computer_use_preview: Optional[RunStepDeltaComputerUseDetails] = ..., 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaConnectedAgentToolCall(RunStepDeltaToolCall, discriminator='connected_agent'):
        connected_agent: RunStepConnectedAgent
        id: str
        index: int
        type: Literal["connected_agent"]

        @overload
        def __init__(
                self, 
                *, 
                connected_agent: RunStepConnectedAgent, 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaCustomBingGroundingToolCall(RunStepDeltaToolCall, discriminator='bing_custom_search'):
        bing_custom_search: dict[str, str]
        id: str
        index: int
        type: Literal["bing_custom_search"]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search: dict[str, str], 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaDeepResearchToolCall(RunStepDeltaToolCall, discriminator='deep_research'):
        deep_research: RunStepDeepResearchToolCallDetails
        id: str
        index: int
        type: Literal["deep_research"]

        @overload
        def __init__(
                self, 
                *, 
                deep_research: RunStepDeepResearchToolCallDetails, 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaDetail(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaFileSearchToolCall(RunStepDeltaToolCall, discriminator='file_search'):
        file_search: Optional[RunStepFileSearchToolCallResults]
        id: str
        index: int
        type: Literal["file_search"]

        @overload
        def __init__(
                self, 
                *, 
                file_search: Optional[RunStepFileSearchToolCallResults] = ..., 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaFunction(_Model):
        arguments: Optional[str]
        name: Optional[str]
        output: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[str] = ..., 
                name: Optional[str] = ..., 
                output: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaFunctionToolCall(RunStepDeltaToolCall, discriminator='function'):
        function: Optional[RunStepDeltaFunction]
        id: str
        index: int
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                function: Optional[RunStepDeltaFunction] = ..., 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaMCPObject(RunStepDeltaDetail, discriminator='mcp'):
        tool_calls: Optional[list[RunStepDeltaMcpToolCall]]
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: Optional[list[RunStepDeltaMcpToolCall]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaMcpToolCall(RunStepDeltaToolCall, discriminator='mcp'):
        arguments: str
        id: str
        index: int
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                id: str, 
                index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaMessageCreation(RunStepDeltaDetail, discriminator='message_creation'):
        message_creation: Optional[RunStepDeltaMessageCreationObject]
        type: Literal["message_creation"]

        @overload
        def __init__(
                self, 
                *, 
                message_creation: Optional[RunStepDeltaMessageCreationObject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaMessageCreationObject(_Model):
        message_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaMicrosoftFabricToolCall(RunStepDeltaToolCall, discriminator='fabric_dataagent'):
        id: str
        index: int
        microsoft_fabric: dict[str, str]
        type: Literal["fabric_dataagent"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                index: int, 
                microsoft_fabric: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaOpenAPIObject(RunStepDeltaDetail, discriminator='openapi'):
        tool_calls: Optional[list[RunStepDeltaOpenAPIToolCall]]
        type: Literal["openapi"]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: Optional[list[RunStepDeltaOpenAPIToolCall]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaOpenAPIToolCall(RunStepDeltaToolCall, discriminator='openapi'):
        id: str
        index: int
        open_api: dict[str, str]
        type: Literal["openapi"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                index: int, 
                open_api: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaSharepointToolCall(RunStepDeltaToolCall, discriminator='sharepoint_grounding'):
        id: str
        index: int
        sharepoint_grounding: dict[str, str]
        type: Literal["sharepoint_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                index: int, 
                sharepoint_grounding: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaToolCall(_Model):
        id: str
        index: int
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                index: int, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDeltaToolCallObject(RunStepDeltaDetail, discriminator='tool_calls'):
        tool_calls: Optional[list[RunStepDeltaToolCall]]
        type: Literal["tool_calls"]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: Optional[list[RunStepDeltaToolCall]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepDetailsActivity(_Model):
        id: str
        server_label: str
        tools: dict[str, ActivityFunctionDefinition]
        type: Literal["mcp_list_tools"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                server_label: str, 
                tools: dict[str, ActivityFunctionDefinition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepError(_Model):
        code: Union[str, RunStepErrorCode]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, RunStepErrorCode], 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
        SERVER_ERROR = "server_error"


    class azure.ai.agents.models.RunStepFileSearchToolCall(RunStepToolCall, discriminator='file_search'):
        file_search: RunStepFileSearchToolCallResults
        id: str
        type: Literal["file_search"]

        @overload
        def __init__(
                self, 
                *, 
                file_search: RunStepFileSearchToolCallResults, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepFileSearchToolCallResult(_Model):
        content: Optional[list[FileSearchToolCallContent]]
        file_id: str
        file_name: str
        score: float

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[list[FileSearchToolCallContent]] = ..., 
                file_id: str, 
                file_name: str, 
                score: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepFileSearchToolCallResults(_Model):
        ranking_options: Optional[FileSearchRankingOptions]
        results: list[RunStepFileSearchToolCallResult]

        @overload
        def __init__(
                self, 
                *, 
                ranking_options: Optional[FileSearchRankingOptions] = ..., 
                results: list[RunStepFileSearchToolCallResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepFunctionToolCall(RunStepToolCall, discriminator='function'):
        function: RunStepFunctionToolCallDetails
        id: str
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                function: RunStepFunctionToolCallDetails, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepFunctionToolCallDetails(_Model):
        arguments: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepMcpToolCall(RunStepToolCall, discriminator='mcp'):
        arguments: str
        id: str
        name: str
        output: str
        server_label: Optional[str]
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                id: str, 
                name: str, 
                output: str, 
                server_label: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepMessageCreationDetails(RunStepDetails, discriminator='message_creation'):
        message_creation: RunStepMessageCreationReference
        type: Literal[RunStepType.MESSAGE_CREATION]

        @overload
        def __init__(
                self, 
                *, 
                message_creation: RunStepMessageCreationReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepMessageCreationReference(_Model):
        message_id: str

        @overload
        def __init__(
                self, 
                *, 
                message_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepMicrosoftFabricToolCall(RunStepToolCall, discriminator='fabric_dataagent'):
        id: str
        microsoft_fabric: dict[str, str]
        type: Literal["fabric_dataagent"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                microsoft_fabric: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepOpenAPIToolCall(RunStepToolCall, discriminator='openapi'):
        id: str
        open_api: dict[str, str]
        type: Literal["openapi"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                open_api: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepSharepointToolCall(RunStepToolCall, discriminator='sharepoint_grounding'):
        id: str
        share_point: dict[str, str]
        type: Literal["sharepoint_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                share_point: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        EXPIRED = "expired"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.RunStepStreamEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THREAD_RUN_STEP_CANCELLED = "thread.run.step.cancelled"
        THREAD_RUN_STEP_COMPLETED = "thread.run.step.completed"
        THREAD_RUN_STEP_CREATED = "thread.run.step.created"
        THREAD_RUN_STEP_DELTA = "thread.run.step.delta"
        THREAD_RUN_STEP_EXPIRED = "thread.run.step.expired"
        THREAD_RUN_STEP_FAILED = "thread.run.step.failed"
        THREAD_RUN_STEP_IN_PROGRESS = "thread.run.step.in_progress"


    class azure.ai.agents.models.RunStepToolCall(_Model):
        id: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepToolCallDetails(RunStepDetails, discriminator='tool_calls'):
        tool_calls: list[RunStepToolCall]
        type: Literal[RunStepType.TOOL_CALLS]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: list[RunStepToolCall]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.RunStepType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITIES = "activities"
        MESSAGE_CREATION = "message_creation"
        TOOL_CALLS = "tool_calls"


    class azure.ai.agents.models.RunStreamEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THREAD_RUN_CANCELLED = "thread.run.cancelled"
        THREAD_RUN_CANCELLING = "thread.run.cancelling"
        THREAD_RUN_COMPLETED = "thread.run.completed"
        THREAD_RUN_CREATED = "thread.run.created"
        THREAD_RUN_EXPIRED = "thread.run.expired"
        THREAD_RUN_FAILED = "thread.run.failed"
        THREAD_RUN_INCOMPLETE = "thread.run.incomplete"
        THREAD_RUN_IN_PROGRESS = "thread.run.in_progress"
        THREAD_RUN_QUEUED = "thread.run.queued"
        THREAD_RUN_REQUIRES_ACTION = "thread.run.requires_action"


    class azure.ai.agents.models.SafetyCheck(_Model):
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


    class azure.ai.agents.models.ScreenshotAction(ComputerUseAction, discriminator='screenshot'):
        type: Literal["screenshot"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ScrollAction(ComputerUseAction, discriminator='scroll'):
        scroll_x: int
        scroll_y: int
        type: Literal["scroll"]
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


    class azure.ai.agents.models.SharepointGroundingToolParameters(_Model):
        connection_list: Optional[list[ToolConnection]]

        @overload
        def __init__(
                self, 
                *, 
                connection_list: Optional[list[ToolConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.SharepointTool(ConnectionTool[SharepointToolDefinition]):
        property definitions: List[SharepointToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self, connection_id: str): ...

        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.SharepointToolDefinition(ToolDefinition, discriminator='sharepoint_grounding'):
        sharepoint_grounding: SharepointGroundingToolParameters
        type: Literal["sharepoint_grounding"]

        @overload
        def __init__(
                self, 
                *, 
                sharepoint_grounding: SharepointGroundingToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.StructuredToolOutput(_Model):
        tool_call_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                tool_call_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.SubmitToolApprovalAction(RequiredAction, discriminator='submit_tool_approval'):
        submit_tool_approval: SubmitToolApprovalDetails
        type: Literal["submit_tool_approval"]

        @overload
        def __init__(
                self, 
                *, 
                submit_tool_approval: SubmitToolApprovalDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.SubmitToolApprovalDetails(_Model):
        tool_calls: list[RequiredToolCall]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: list[RequiredToolCall]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.SubmitToolOutputsAction(RequiredAction, discriminator='submit_tool_outputs'):
        submit_tool_outputs: SubmitToolOutputsDetails
        type: Literal["submit_tool_outputs"]

        @overload
        def __init__(
                self, 
                *, 
                submit_tool_outputs: SubmitToolOutputsDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.SubmitToolOutputsDetails(_Model):
        tool_calls: list[RequiredToolCall]

        @overload
        def __init__(
                self, 
                *, 
                tool_calls: list[RequiredToolCall]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ThreadMessage(ThreadMessageGenerated):
        property file_citation_annotations: List[MessageTextFileCitationAnnotation]    # Read-only
        property file_path_annotations: List[MessageTextFilePathAnnotation]    # Read-only
        property image_contents: List[MessageImageFileContent]    # Read-only
        property text_messages: List[MessageTextContent]    # Read-only
        property url_citation_annotations: List[MessageTextUrlCitationAnnotation]    # Read-only

        @overload
        def __init__(
                self, 
                *, 
                agent_id: str, 
                attachments: list[MessageAttachment], 
                completed_at: datetime, 
                content: list[MessageContent], 
                created_at: datetime, 
                id: str, 
                incomplete_at: datetime, 
                incomplete_details: MessageIncompleteDetails, 
                metadata: dict[str, str], 
                role: Union[str, MessageRole], 
                run_id: str, 
                status: Union[str, MessageStatus], 
                thread_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ThreadMessageOptions(_Model):
        attachments: Optional[list[MessageAttachment]]
        content: MessageInputContent
        metadata: Optional[dict[str, str]]
        role: Union[str, MessageRole]

        @overload
        def __init__(
                self, 
                *, 
                attachments: Optional[list[MessageAttachment]] = ..., 
                content: MessageInputContent, 
                metadata: Optional[dict[str, str]] = ..., 
                role: Union[str, MessageRole]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ThreadRun(_Model):
        agent_id: str
        cancelled_at: datetime
        completed_at: datetime
        created_at: datetime
        expires_at: datetime
        failed_at: datetime
        id: str
        incomplete_details: IncompleteRunDetails
        instructions: str
        last_error: RunError
        max_completion_tokens: int
        max_prompt_tokens: int
        metadata: dict[str, str]
        model: str
        object: Literal["run"]
        parallel_tool_calls: bool
        required_action: Optional[RequiredAction]
        response_format: AgentsResponseFormatOption
        started_at: datetime
        status: Union[str, RunStatus]
        temperature: Optional[float]
        thread_id: str
        tool_choice: AgentsToolChoiceOption
        tool_resources: Optional[ToolResources]
        tools: list[ToolDefinition]
        top_p: Optional[float]
        truncation_strategy: TruncationObject
        usage: RunCompletionUsage

        @overload
        def __init__(
                self, 
                *, 
                agent_id: str, 
                cancelled_at: datetime, 
                completed_at: datetime, 
                created_at: datetime, 
                expires_at: datetime, 
                failed_at: datetime, 
                id: str, 
                incomplete_details: IncompleteRunDetails, 
                instructions: str, 
                last_error: RunError, 
                max_completion_tokens: int, 
                max_prompt_tokens: int, 
                metadata: dict[str, str], 
                model: str, 
                parallel_tool_calls: bool, 
                required_action: Optional[RequiredAction] = ..., 
                response_format: AgentsResponseFormatOption, 
                started_at: datetime, 
                status: Union[str, RunStatus], 
                temperature: Optional[float] = ..., 
                thread_id: str, 
                tool_choice: AgentsToolChoiceOption, 
                tool_resources: Optional[ToolResources] = ..., 
                tools: list[ToolDefinition], 
                top_p: Optional[float] = ..., 
                truncation_strategy: TruncationObject, 
                usage: RunCompletionUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ThreadStreamEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THREAD_CREATED = "thread.created"


    class azure.ai.agents.models.Tool(ABC, Generic[ToolDefinitionT]):
        property definitions: List[ToolDefinitionT]    # Read-only
        property resources: ToolResources    # Read-only

        @abstractmethod
        def execute(self, tool_call: Any) -> Any: ...


    class azure.ai.agents.models.ToolApproval(_Model):
        approve: bool
        headers: Optional[dict[str, str]]
        tool_call_id: str

        @overload
        def __init__(
                self, 
                *, 
                approve: bool, 
                headers: Optional[dict[str, str]] = ..., 
                tool_call_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ToolConnection(_Model):
        connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ToolDefinition(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ToolOutput(StructuredToolOutput, discriminator='function_call_output'):
        output: Optional[str]
        tool_call_id: str
        type: Literal["function_call_output"]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[str] = ..., 
                tool_call_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ToolResources(_Model):
        azure_ai_search: Optional[AzureAISearchToolResource]
        code_interpreter: Optional[CodeInterpreterToolResource]
        file_search: Optional[FileSearchToolResource]
        mcp: Optional[list[MCPToolResource]]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: Optional[AzureAISearchToolResource] = ..., 
                code_interpreter: Optional[CodeInterpreterToolResource] = ..., 
                file_search: Optional[FileSearchToolResource] = ..., 
                mcp: Optional[list[MCPToolResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.ToolSet(BaseToolSet):
        property definitions: List[ToolDefinition]    # Read-only
        property resources: ToolResources    # Read-only

        def __init__(self) -> None: ...

        def add(self, tool: Tool): ...

        def execute_tool_calls(self, tool_calls: List[Any]) -> Any: ...

        def get_definitions_and_resources(self) -> Dict[str, Any]: ...

        @overload
        def get_tool(self, tool_type: Type[McpTool]) -> McpTool: ...

        @overload
        def get_tool(
                self, 
                tool_type: Type[McpTool], 
                *, 
                server_label: str
            ) -> McpTool: ...

        @overload
        def get_tool(self, tool_type: Type[ToolT]) -> ToolT: ...

        @overload
        def remove(self, tool_type: Type[Tool]) -> None: ...

        @overload
        def remove(
                self, 
                tool_type: Type[OpenApiTool], 
                *, 
                name: str
            ) -> None: ...

        @overload
        def remove(
                self, 
                tool_type: Type[McpTool], 
                *, 
                server_label: str
            ) -> None: ...

        def validate_tool_type(self, tool: Tool) -> None: ...


    class azure.ai.agents.models.TruncationObject(_Model):
        last_messages: Optional[int]
        type: Union[str, TruncationStrategy]

        @overload
        def __init__(
                self, 
                *, 
                last_messages: Optional[int] = ..., 
                type: Union[str, TruncationStrategy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.TruncationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        LAST_MESSAGES = "last_messages"


    class azure.ai.agents.models.TypeAction(ComputerUseAction, discriminator='type'):
        text: str
        type: Literal["type"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStore(_Model):
        created_at: datetime
        expires_after: Optional[VectorStoreExpirationPolicy]
        expires_at: Optional[datetime]
        file_counts: VectorStoreFileCount
        id: str
        last_active_at: datetime
        metadata: dict[str, str]
        name: str
        object: Literal["vector_store"]
        status: Union[str, VectorStoreStatus]
        usage_bytes: int

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                expires_at: Optional[datetime] = ..., 
                file_counts: VectorStoreFileCount, 
                id: str, 
                last_active_at: datetime, 
                metadata: dict[str, str], 
                name: str, 
                status: Union[str, VectorStoreStatus], 
                usage_bytes: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreAutoChunkingStrategyRequest(VectorStoreChunkingStrategyRequest, discriminator='auto'):
        type: Literal[VectorStoreChunkingStrategyRequestType.AUTO]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreAutoChunkingStrategyResponse(VectorStoreChunkingStrategyResponse, discriminator='other'):
        type: Literal[VectorStoreChunkingStrategyResponseType.OTHER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreChunkingStrategyRequest(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreChunkingStrategyRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        STATIC = "static"


    class azure.ai.agents.models.VectorStoreChunkingStrategyResponse(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreChunkingStrategyResponseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "other"
        STATIC = "static"


    class azure.ai.agents.models.VectorStoreConfiguration(_Model):
        data_sources: list[VectorStoreDataSource]

        @overload
        def __init__(
                self, 
                *, 
                data_sources: list[VectorStoreDataSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreConfigurations(_Model):
        store_configuration: VectorStoreConfiguration
        store_name: str

        @overload
        def __init__(
                self, 
                *, 
                store_configuration: VectorStoreConfiguration, 
                store_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreDataSource(_Model):
        asset_identifier: str
        asset_type: Union[str, VectorStoreDataSourceAssetType]

        @overload
        def __init__(
                self, 
                *, 
                asset_identifier: str, 
                asset_type: Union[str, VectorStoreDataSourceAssetType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreDataSourceAssetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ID_ASSET = "id_asset"
        URI_ASSET = "uri_asset"


    class azure.ai.agents.models.VectorStoreExpirationPolicy(_Model):
        anchor: Union[str, VectorStoreExpirationPolicyAnchor]
        days: int

        @overload
        def __init__(
                self, 
                *, 
                anchor: Union[str, VectorStoreExpirationPolicyAnchor], 
                days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreExpirationPolicyAnchor(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LAST_ACTIVE_AT = "last_active_at"


    class azure.ai.agents.models.VectorStoreFile(_Model):
        chunking_strategy: VectorStoreChunkingStrategyResponse
        created_at: datetime
        id: str
        last_error: VectorStoreFileError
        object: Literal["file"]
        status: Union[str, VectorStoreFileStatus]
        usage_bytes: int
        vector_store_id: str

        @overload
        def __init__(
                self, 
                *, 
                chunking_strategy: VectorStoreChunkingStrategyResponse, 
                created_at: datetime, 
                id: str, 
                last_error: VectorStoreFileError, 
                status: Union[str, VectorStoreFileStatus], 
                usage_bytes: int, 
                vector_store_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreFileBatch(_Model):
        created_at: datetime
        file_counts: VectorStoreFileCount
        id: str
        object: Literal["files_batch"]
        status: Union[str, VectorStoreFileBatchStatus]
        vector_store_id: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                file_counts: VectorStoreFileCount, 
                id: str, 
                status: Union[str, VectorStoreFileBatchStatus], 
                vector_store_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreFileBatchStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.VectorStoreFileCount(_Model):
        cancelled: int
        completed: int
        failed: int
        in_progress: int
        total: int

        @overload
        def __init__(
                self, 
                *, 
                cancelled: int, 
                completed: int, 
                failed: int, 
                in_progress: int, 
                total: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreFileError(_Model):
        code: Union[str, VectorStoreFileErrorCode]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, VectorStoreFileErrorCode], 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreFileErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_FILE = "invalid_file"
        SERVER_ERROR = "server_error"
        UNSUPPORTED_FILE = "unsupported_file"


    class azure.ai.agents.models.VectorStoreFileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.VectorStoreFileStatusFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.VectorStoreStaticChunkingStrategyOptions(_Model):
        chunk_overlap_tokens: int
        max_chunk_size_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                chunk_overlap_tokens: int, 
                max_chunk_size_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreStaticChunkingStrategyRequest(VectorStoreChunkingStrategyRequest, discriminator='static'):
        static: VectorStoreStaticChunkingStrategyOptions
        type: Literal[VectorStoreChunkingStrategyRequestType.STATIC]

        @overload
        def __init__(
                self, 
                *, 
                static: VectorStoreStaticChunkingStrategyOptions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreStaticChunkingStrategyResponse(VectorStoreChunkingStrategyResponse, discriminator='static'):
        static: VectorStoreStaticChunkingStrategyOptions
        type: Literal[VectorStoreChunkingStrategyResponseType.STATIC]

        @overload
        def __init__(
                self, 
                *, 
                static: VectorStoreStaticChunkingStrategyOptions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.agents.models.VectorStoreStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        EXPIRED = "expired"
        IN_PROGRESS = "in_progress"


    class azure.ai.agents.models.WaitAction(ComputerUseAction, discriminator='wait'):
        type: Literal["wait"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.agents.operations

    class azure.ai.agents.operations.FilesOperations(FilesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> FileInfo: ...

        @distributed_trace
        def get_content(
                self, 
                file_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def list(
                self, 
                *, 
                purpose: Optional[Union[str, FilePurpose]] = ..., 
                **kwargs: Any
            ) -> FileListResponse: ...

        @distributed_trace
        def save(
                self, 
                file_id: str, 
                file_name: str, 
                target_dir: Optional[Union[str, Path]] = None
            ) -> None: ...

        @overload
        def upload(
                self, 
                *, 
                file_path: str, 
                purpose: Union[str, FilePurpose], 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        def upload(
                self, 
                *, 
                file: FileType, 
                filename: Optional[str] = ..., 
                purpose: Union[str, FilePurpose], 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        def upload(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        def upload_and_poll(
                self, 
                body: JSON, 
                *, 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        def upload_and_poll(
                self, 
                *, 
                file: FileType, 
                filename: Optional[str] = ..., 
                polling_interval: float = 1, 
                purpose: Union[str, FilePurpose], 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...

        @overload
        def upload_and_poll(
                self, 
                *, 
                file_path: str, 
                polling_interval: float = 1, 
                purpose: Union[str, FilePurpose], 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> FileInfo: ...


    class azure.ai.agents.operations.MessagesOperations(MessagesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                *, 
                attachments: Optional[List[MessageAttachment]] = ..., 
                content: MessageInputContent, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                role: Union[str, MessageRole], 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @distributed_trace
        def delete(
                self, 
                thread_id: str, 
                message_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                thread_id: str, 
                message_id: str, 
                **kwargs: Any
            ) -> ThreadMessage: ...

        def get_last_message_by_role(
                self, 
                thread_id: str, 
                role: MessageRole, 
                **kwargs
            ) -> Optional[ThreadMessage]: ...

        def get_last_message_text_by_role(
                self, 
                thread_id: str, 
                role: MessageRole, 
                **kwargs
            ) -> Optional[MessageTextContent]: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                run_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ThreadMessage]: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                message_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                message_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                message_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadMessage: ...


    class azure.ai.agents.operations.RunStepsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                thread_id: str, 
                run_id: str, 
                step_id: str, 
                *, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> RunStep: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                before: Optional[str] = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RunStep]: ...


    class azure.ai.agents.operations.RunsOperations(RunsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                thread_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def create(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace
        def create_and_process(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                polling_interval: int = 1, 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                run_handler: Optional[RunHandler] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                toolset: Optional[ToolSet] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace
        def get(
                self, 
                thread_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ThreadRun: ...

        @distributed_trace
        def list(
                self, 
                thread_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ThreadRun]: ...

        @overload
        def stream(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                event_handler: None = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> AgentRunStream[AgentEventHandler]: ...

        @overload
        def stream(
                self, 
                thread_id: str, 
                *, 
                additional_instructions: Optional[str] = ..., 
                additional_messages: Optional[List[ThreadMessageOptions]] = ..., 
                agent_id: str, 
                content_type: str = "application/json", 
                event_handler: BaseAgentEventHandlerT, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                instructions: Optional[str] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                max_prompt_tokens: Optional[int] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                response_format: Optional[AgentsResponseFormatOption] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[AgentsToolChoiceOption] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                tools: Optional[List[ToolDefinition]] = ..., 
                top_p: Optional[float] = ..., 
                truncation_strategy: Optional[TruncationObject] = ..., 
                **kwargs: Any
            ) -> AgentRunStream[BaseAgentEventHandlerT]: ...

        @overload
        def stream(
                self, 
                thread_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: None = ..., 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> AgentRunStream[AgentEventHandler]: ...

        @overload
        def stream(
                self, 
                thread_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAgentEventHandlerT, 
                include: Optional[List[Union[str, RunAdditionalFieldList]]] = ..., 
                **kwargs: Any
            ) -> AgentRunStream[BaseAgentEventHandlerT]: ...

        @overload
        def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                event_handler: Optional[AgentEventHandler] = ..., 
                tool_approvals: Optional[List[ToolApproval]] = ..., 
                tool_outputs: Optional[List[StructuredToolOutput]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def submit_tool_outputs(
                self, 
                thread_id: str, 
                run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def submit_tool_outputs_stream(
                self, 
                thread_id: str, 
                run_id: str, 
                body: Union[JSON, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAgentEventHandler, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def submit_tool_outputs_stream(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                event_handler: BaseAgentEventHandler, 
                tool_approvals: Optional[List[ToolApproval]] = ..., 
                tool_outputs: Optional[List[StructuredToolOutput]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                run_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                run_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                run_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ThreadRun: ...


    class azure.ai.agents.operations.ThreadsOperations(ThreadsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                *, 
                content_type: str = "application/json", 
                messages: Optional[List[ThreadMessageOptions]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @distributed_trace
        def delete(
                self, 
                thread_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                thread_id: str, 
                **kwargs: Any
            ) -> AgentThread: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentThread]: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                *, 
                content_type: str = "application/json", 
                metadata: Optional[dict[str, str]] = ..., 
                tool_resources: Optional[ToolResources] = ..., 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...

        @overload
        def update(
                self, 
                thread_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentThread: ...


    class azure.ai.agents.operations.VectorStoreFileBatchesOperations(VectorStoreFileBatchesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                file_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                file_ids: Optional[List[str]] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @distributed_trace
        def get(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                **kwargs: Any
            ) -> VectorStoreFileBatch: ...

        @distributed_trace
        def list_files(
                self, 
                vector_store_id: str, 
                batch_id: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[Union[str, VectorStoreFileStatusFilter]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VectorStoreFile]: ...


    class azure.ai.agents.operations.VectorStoreFilesOperations(VectorStoreFilesOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        def create(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_source: Optional[VectorStoreDataSource] = ..., 
                file_id: Optional[str] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @overload
        def create_and_poll(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @distributed_trace
        def delete(
                self, 
                vector_store_id: str, 
                file_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vector_store_id: str, 
                file_id: str, 
                **kwargs: Any
            ) -> VectorStoreFile: ...

        @distributed_trace
        def list(
                self, 
                vector_store_id: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[Union[str, VectorStoreFileStatusFilter]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VectorStoreFile]: ...


    class azure.ai.agents.operations.VectorStoresOperations(VectorStoresOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                file_ids: Optional[List[str]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                store_configuration: Optional[VectorStoreConfiguration] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def create_and_poll(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def create_and_poll(
                self, 
                *, 
                chunking_strategy: Optional[VectorStoreChunkingStrategyRequest] = ..., 
                content_type: str = "application/json", 
                data_sources: Optional[List[VectorStoreDataSource]] = ..., 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                file_ids: Optional[List[str]] = ..., 
                metadata: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def create_and_poll(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                polling_interval: float = 1, 
                timeout: Optional[float] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @distributed_trace
        def delete(
                self, 
                vector_store_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                vector_store_id: str, 
                **kwargs: Any
            ) -> VectorStore: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, ListSortOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VectorStore]: ...

        @overload
        def modify(
                self, 
                vector_store_id: str, 
                *, 
                content_type: str = "application/json", 
                expires_after: Optional[VectorStoreExpirationPolicy] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def modify(
                self, 
                vector_store_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...

        @overload
        def modify(
                self, 
                vector_store_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VectorStore: ...


namespace azure.ai.agents.telemetry

    def azure.ai.agents.telemetry.trace_function(span_name: Optional[str] = None) -> Callable: ...


    class azure.ai.agents.telemetry.AIAgentsInstrumentor:

        def __init__(self): ...

        def instrument(self, enable_content_recording: Optional[bool] = None) -> None: ...

        def is_content_recording_enabled(self) -> bool: ...

        def is_instrumented(self) -> bool: ...

        def uninstrument(self) -> None: ...


```