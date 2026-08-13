```py
namespace azure.ai.projects

    class azure.ai.projects.AIProjectClient(AIProjectClientGenerated): implements ContextManager 
        agents: AgentsOperations
        beta: BetaOperations
        connections: ConnectionsOperations
        datasets: DatasetsOperations
        deployments: DeploymentsOperations
        evaluation_rules: EvaluationRulesOperations
        indexes: IndexesOperations
        toolboxes: ToolboxesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_openai_client(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> OpenAI: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.projects.aio

    class azure.ai.projects.aio.AIProjectClient(AIProjectClientGenerated): implements AsyncContextManager 
        property realtime: AsyncRealtime    # Read-only
        agents: AgentsOperations
        beta: BetaOperations
        connections: ConnectionsOperations
        datasets: DatasetsOperations
        deployments: DeploymentsOperations
        evaluation_rules: EvaluationRulesOperations
        indexes: IndexesOperations
        toolboxes: ToolboxesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace
        def get_openai_client(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncOpenAI: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.projects.aio.AsyncRealtime:

        def __init__(self, client: AIProjectClient) -> None: ...

        def connect(
                self, 
                *, 
                agent_name: str, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                api_version: Optional[str] = ..., 
                connection_url: Optional[str] = ..., 
                credential_scopes: Optional[List[str]] = ..., 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: str = _VOICE_AGENT_FEATURE_HEADER, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncRealtimeConnectionManager: ...


    class azure.ai.projects.aio.AsyncRealtimeConnection: implements AsyncContextManager 
        property closed: bool    # Read-only

        def __aiter__(self) -> AsyncIterator[ServerEvent]: ...

        def __init__(
                self, 
                connection: ClientWebSocketResponse, 
                session: ClientSession
            ) -> None: ...

        def __repr__(self) -> str: ...

        async def close(
                self, 
                *, 
                code: int = 1000, 
                reason: str = ""
            ) -> None: ...

        async def recv(self) -> ServerEvent: ...

        async def send(self, event: ClientEvent) -> None: ...


    class azure.ai.projects.aio.AsyncRealtimeConnectionManager: implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                api_version: str, 
                connection_url: Optional[str] = ..., 
                credential: AsyncTokenCredential, 
                credential_scopes: List[str], 
                endpoint: str, 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: str, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def enter(self) -> AsyncRealtimeConnection: ...


namespace azure.ai.projects.aio.operations

    class azure.ai.projects.aio.operations.AgentEndpointConversationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace_async
        async def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceResponse]: ...

        @distributed_trace
        def list_agent_conversations(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversation]: ...


    class azure.ai.projects.aio.operations.AgentsOperations(GeneratedAgentsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                version_indicator: VersionIndicator, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                body: CreateSessionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace_async
        async def create_version_from_code(
                self, 
                agent_name: str, 
                *, 
                code: IO[bytes], 
                code_zip_sha256: Optional[str] = ..., 
                definition: HostedAgentDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                manifest_id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                parameter_values: dict[str, Any], 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: CreateAgentVersionFromManifestRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace_async
        async def delete(
                self, 
                agent_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace_async
        async def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace_async
        async def disable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_code(
                self, 
                agent_name: str, 
                *, 
                agent_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def download_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def enable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                kind: Union[str, AgentKind], 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def generate_agent(
                self, 
                body: GenerateAgentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def generate_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace_async
        async def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace_async
        async def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

        @distributed_trace_async
        async def get_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                kind: Optional[Union[str, AgentKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentDetails]: ...

        @distributed_trace
        def list_session_files(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                path: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SessionDirectoryEntry]: ...

        @distributed_trace
        def list_sessions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentSessionResource]: ...

        @distributed_trace
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentVersionDetails]: ...

        @distributed_trace_async
        async def stop_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                body: PatchAgentObjectRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...

        @overload
        async def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: IO[bytes], 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.aio.operations.BetaAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentOptimizationJobResult]: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentOptimizationJobResult]: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentOptimizationJobResult]: ...

        @distributed_trace_async
        async def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace_async
        async def delete_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def list_optimization_jobs(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentOptimizationJobListItem]: ...


    class azure.ai.projects.aio.operations.BetaDatasetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DataGenerationJobResult]: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DataGenerationJobResult]: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[DataGenerationJobResult]: ...

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace_async
        async def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataGenerationJob]: ...


    class azure.ai.projects.aio.operations.BetaEvaluationTaxonomiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                input_name: Optional[str] = ..., 
                input_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluationTaxonomy]: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...


    class azure.ai.projects.aio.operations.BetaEvaluatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluatorVersion]: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluatorVersion]: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[EvaluatorVersion]: ...

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace_async
        async def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace_async
        async def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorVersion]: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorGenerationJob]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorVersion]: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...


    class azure.ai.projects.aio.operations.BetaInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def generate(
                self, 
                insight: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace_async
        async def get(
                self, 
                insight_id: str, 
                *, 
                include_coordinates: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                include_coordinates: Optional[bool] = ..., 
                run_id: Optional[str] = ..., 
                type: Optional[Union[str, InsightType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Insight]: ...


    class azure.ai.projects.aio.operations.BetaMemoryStoresOperations(GenerateBetaMemoryStoresOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                previous_update_id: Optional[str] = ..., 
                scope: str, 
                update_delay: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def create(
                self, 
                *, 
                content_type: str = "application/json", 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create(
                self, 
                body: CreateMemoryStoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                kind: Union[str, MemoryItemKind], 
                scope: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                body: CreateMemoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

        @distributed_trace_async
        async def delete_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> DeleteMemoryResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                body: DeleteScopeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @distributed_trace_async
        async def get_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryStoreDetails]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: ListMemoriesRequest, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                options: Optional[MemorySearchOptions] = ..., 
                previous_search_id: Optional[str] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: UpdateMemoryStoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: UpdateMemoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...


    class azure.ai.projects.aio.operations.BetaModelsOperations(BetaModelsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[True] = True, 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def create(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[False], 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ModelVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelVersion]: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...


    class azure.ai.projects.aio.operations.BetaOperations(GeneratedBetaOperations):
        agents: BetaAgentsOperations
        datasets: BetaDatasetsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        models: BetaModelsOperations
        red_teams: BetaRedTeamsOperations
        routines: BetaRoutinesOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.aio.operations.BetaRedTeamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        async def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        async def create(
                self, 
                red_team: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[RedTeam]: ...


    class azure.ai.projects.aio.operations.BetaRoutinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                *, 
                action: Optional[RoutineAction] = ..., 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                body: CreateOrUpdateRoutineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace_async
        async def delete(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                *, 
                content_type: str = "application/json", 
                payload: Optional[RoutineDispatchPayload] = ..., 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                body: DispatchRoutineAsyncRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @distributed_trace_async
        async def enable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace_async
        async def get(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Routine]: ...

        @distributed_trace
        def list_runs(
                self, 
                routine_name: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoutineRun]: ...


    class azure.ai.projects.aio.operations.BetaSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def get_run(
                self, 
                schedule_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScheduleRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Schedule]: ...

        @distributed_trace
        def list_runs(
                self, 
                schedule_id: str, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduleRun]: ...


    class azure.ai.projects.aio.operations.BetaSkillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default: Optional[bool] = ..., 
                inline_content: Optional[SkillInlineContent] = ..., 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: CreateSkillVersionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResult: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DeleteSkillVersionResult: ...

        @distributed_trace_async
        async def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def download_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkillDetails]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkillVersion]: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: UpdateSkillRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...


    class azure.ai.projects.aio.operations.ConnectionsOperations(ConnectionsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace_async
        async def get_default(
                self, 
                connection_type: Union[str, ConnectionType], 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                *, 
                connection_type: Optional[Union[str, ConnectionType]] = ..., 
                default_connection: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Connection]: ...


    class azure.ai.projects.aio.operations.DatasetsOperations(DatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace_async
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DatasetVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatasetVersion]: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @distributed_trace_async
        async def upload_file(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_path: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FileDatasetVersion: ...

        @distributed_trace_async
        async def upload_folder(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_pattern: Optional[Pattern] = ..., 
                folder: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FolderDatasetVersion: ...


    class azure.ai.projects.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                deployment_type: Optional[Union[str, DeploymentType]] = ..., 
                model_name: Optional[str] = ..., 
                model_publisher: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...


    class azure.ai.projects.aio.operations.EvaluationRulesOperations(GeneratedEvaluationRulesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: EvaluationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def list(
                self, 
                *, 
                action_type: Optional[Union[str, EvaluationRuleActionType]] = ..., 
                agent_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluationRule]: ...


    class azure.ai.projects.aio.operations.IndexesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Index]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Index]: ...


    class azure.ai.projects.aio.operations.TelemetryOperations:

        def __init__(self, outer_instance: AIProjectClient) -> None: ...

        @distributed_trace_async
        async def get_application_insights_connection_string(self) -> str: ...


    class azure.ai.projects.aio.operations.ToolboxesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[List[ToolboxSkill]] = ..., 
                tools: List[ToolboxTool], 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                body: CreateToolboxVersionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ToolboxObject]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ToolboxVersionObject]: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: UpdateToolboxRequest1, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...


    class azure.ai.projects.aio.operations.VoiceAgentWebSocketOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def connect_voice_agent(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                store: Optional[bool] = ..., 
                structured_inputs: Optional[str] = ..., 
                websocket_subprotocol: Optional[Union[str, VoiceAgentWebSocketSubprotocol]] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.projects.models

    class azure.ai.projects.models.A2APreviewTool(Tool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        type: Literal[ToolType.A2A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.A2APreviewToolboxTool(ToolboxTool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        description: str
        name: str
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.A2A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.A2AProtocolConfiguration(_Model):


    class azure.ai.projects.models.AISearchIndexResource(_Model):
        filter: Optional[str]
        index_asset_id: Optional[str]
        index_name: Optional[str]
        project_connection_id: Optional[str]
        query_type: Optional[Union[str, AzureAISearchQueryType]]
        top_k: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                index_asset_id: Optional[str] = ..., 
                index_name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                query_type: Optional[Union[str, AzureAISearchQueryType]] = ..., 
                top_k: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ActivityProtocolConfiguration(_Model):
        enable_m365_public_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_m365_public_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentBlueprintReference(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentBlueprintReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_AGENT_IDENTITY_BLUEPRINT = "ManagedAgentIdentityBlueprint"


    class azure.ai.projects.models.AgentCard(_Model):
        description: Optional[str]
        skills: list[AgentCardSkill]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                skills: list[AgentCardSkill], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentCardSkill(_Model):
        description: Optional[str]
        examples: Optional[list[str]]
        id: str
        name: str
        tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                examples: Optional[list[str]] = ..., 
                id: str, 
                name: str, 
                tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentClusterInsightRequest(InsightRequest, discriminator='AgentClusterInsight'):
        agent_name: str
        model_configuration: Optional[InsightModelConfiguration]
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                model_configuration: Optional[InsightModelConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentClusterInsightResult(InsightResult, discriminator='AgentClusterInsight'):
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                cluster_insight: ClusterInsightResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDataGenerationJobSource(DataGenerationJobSource, discriminator='agent'):
        agent_name: str
        agent_version: Optional[str]
        description: str
        type: Literal[DataGenerationJobSourceType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDefinition(_Model):
        kind: str
        rai_config: Optional[RaiConfig]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDetails(_Model):
        agent_card: Optional[AgentCard]
        agent_endpoint: Optional[AgentEndpointConfig]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        id: str
        instance_identity: Optional[AgentIdentity]
        name: str
        object: Literal[AgentObjectType.AGENT]
        state: Union[str, AgentState]
        state_source: Optional[Union[str, AgentStateSource]]
        versions: AgentObjectVersions

        @overload
        def __init__(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                id: str, 
                name: str, 
                object: Literal[AgentObjectType.AGENT], 
                versions: AgentObjectVersions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpointAuthorizationScheme(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpointAuthorizationSchemeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT_SERVICE = "BotService"
        BOT_SERVICE_RBAC = "BotServiceRbac"
        BOT_SERVICE_TENANT = "BotServiceTenant"
        ENTRA = "Entra"


    class azure.ai.projects.models.AgentEndpointConfig(_Model):
        authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]]
        protocol_configuration: Optional[ProtocolConfiguration]
        version_selector: Optional[VersionSelector]

        @overload
        def __init__(
                self, 
                *, 
                authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]] = ..., 
                protocol_configuration: Optional[ProtocolConfiguration] = ..., 
                version_selector: Optional[VersionSelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A = "a2a"
        ACTIVITY = "activity"
        INVOCATIONS = "invocations"
        INVOCATIONS_WS = "invocations_ws"
        MCP = "mcp"
        RESPONSES = "responses"
        VOICE = "voice"


    class azure.ai.projects.models.AgentEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='agent'):
        agent_name: str
        agent_version: Optional[str]
        description: Optional[str]
        type: Literal[EvaluatorGenerationJobSourceType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentIdentity(_Model):
        client_id: str
        principal_id: str
        status: Optional[Union[str, AgentIdentityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                principal_id: str, 
                status: Optional[Union[str, AgentIdentityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentIdentityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DISABLED = "disabled"


    class azure.ai.projects.models.AgentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "external"
        HOSTED = "hosted"
        PROMPT = "prompt"
        VOICE = "voice"
        WORKFLOW = "workflow"


    class azure.ai.projects.models.AgentObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        AGENT_CONTAINER = "agent.container"
        AGENT_DELETED = "agent.deleted"
        AGENT_VERSION = "agent.version"
        AGENT_VERSION_DELETED = "agent.version.deleted"


    class azure.ai.projects.models.AgentObjectVersions(_Model):
        latest: AgentVersionDetails

        @overload
        def __init__(
                self, 
                *, 
                latest: AgentVersionDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationCandidate(_Model):
        avg_score: float
        avg_tokens: float
        candidate_id: Optional[str]
        eval_id: Optional[str]
        eval_run_id: Optional[str]
        mutations: Optional[dict[str, Any]]
        name: str
        promotion: Optional[PromotionInfo]

        @overload
        def __init__(
                self, 
                *, 
                avg_score: float, 
                avg_tokens: float, 
                candidate_id: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                eval_run_id: Optional[str] = ..., 
                mutations: Optional[dict[str, Any]] = ..., 
                name: str, 
                promotion: Optional[PromotionInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetCriterion(_Model):
        instruction: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                instruction: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetInput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.ai.projects.models.AgentOptimizationDatasetItem(_Model):
        criteria: Optional[list[AgentOptimizationDatasetCriterion]]
        desired_num_turns: Optional[int]
        ground_truth: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                criteria: Optional[list[AgentOptimizationDatasetCriterion]] = ..., 
                desired_num_turns: Optional[int] = ..., 
                ground_truth: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationEvaluatorRef(_Model):
        name: str
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


    class azure.ai.projects.models.AgentOptimizationInlineDatasetInput(AgentOptimizationDatasetInput, discriminator='inline'):
        dataset_items: list[AgentOptimizationDatasetItem]
        type: Literal[AgentOptimizationDatasetInputType.INLINE]

        @overload
        def __init__(
                self, 
                *, 
                dataset_items: list[AgentOptimizationDatasetItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        id: str
        inputs: Optional[AgentOptimizationJobInputs]
        progress: Optional[AgentOptimizationJobProgress]
        result: Optional[AgentOptimizationJobResult]
        status: Union[str, JobStatus]
        updated_at: datetime
        warnings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[AgentOptimizationJobInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobInputs(_Model):
        agent: OptimizedAgentIdentifier
        evaluators: list[AgentOptimizationEvaluatorRef]
        options: Optional[AgentOptimizationOptions]
        train_dataset: AgentOptimizationDatasetInput
        validation_dataset: Optional[AgentOptimizationDatasetInput]

        @overload
        def __init__(
                self, 
                *, 
                agent: OptimizedAgentIdentifier, 
                evaluators: list[AgentOptimizationEvaluatorRef], 
                options: Optional[AgentOptimizationOptions] = ..., 
                train_dataset: AgentOptimizationDatasetInput, 
                validation_dataset: Optional[AgentOptimizationDatasetInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobListItem(_Model):
        agent: Optional[OptimizedAgentIdentifier]
        created_at: datetime
        error: Optional[ApiError]
        id: str
        progress: Optional[AgentOptimizationJobProgress]
        status: Union[str, JobStatus]
        updated_at: datetime


    class azure.ai.projects.models.AgentOptimizationJobProgress(_Model):
        best_score: float
        candidates_completed: int
        elapsed_seconds: float

        @overload
        def __init__(
                self, 
                *, 
                best_score: float, 
                candidates_completed: int, 
                elapsed_seconds: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobResult(_Model):
        baseline: Optional[str]
        best: Optional[str]
        candidates: Optional[list[AgentOptimizationCandidate]]

        @overload
        def __init__(
                self, 
                *, 
                baseline: Optional[str] = ..., 
                best: Optional[str] = ..., 
                candidates: Optional[list[AgentOptimizationCandidate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationOptions(_Model):
        eval_model: Optional[str]
        evaluation_level: Optional[Union[str, EvaluationLevel]]
        max_candidates: Optional[int]
        max_stalls: Optional[int]
        optimization_config: Optional[dict[str, Any]]
        optimization_model: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                eval_model: Optional[str] = ..., 
                evaluation_level: Optional[Union[str, EvaluationLevel]] = ..., 
                max_candidates: Optional[int] = ..., 
                max_stalls: Optional[int] = ..., 
                optimization_config: Optional[dict[str, Any]] = ..., 
                optimization_model: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationReferenceDatasetInput(AgentOptimizationDatasetInput, discriminator='reference'):
        name: str
        type: Literal[AgentOptimizationDatasetInputType.REFERENCE]
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


    class azure.ai.projects.models.AgentSessionResource(_Model):
        agent_session_id: str
        created_at: datetime
        expires_at: datetime
        last_accessed_at: datetime
        status: Union[str, AgentSessionStatus]
        version_indicator: VersionIndicator

        @overload
        def __init__(
                self, 
                *, 
                agent_session_id: str, 
                status: Union[str, AgentSessionStatus], 
                version_indicator: VersionIndicator
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentSessionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETED = "deleted"
        DELETING = "deleting"
        EXPIRED = "expired"
        FAILED = "failed"
        IDLE = "idle"
        UPDATING = "updating"


    class azure.ai.projects.models.AgentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.ai.projects.models.AgentStateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_BLUEPRINT = "agent_blueprint"
        AGENT_INSTANCE_IDENTITY = "agent_instance_identity"


    class azure.ai.projects.models.AgentTaxonomyInput(EvaluationTaxonomyInput, discriminator='agent'):
        risk_categories: list[Union[str, RiskCategory]]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                risk_categories: list[Union[str, RiskCategory]], 
                target: EvaluationTarget
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentVersionDetails(_Model):
        agent_guid: Optional[str]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        created_at: datetime
        definition: AgentDefinition
        description: Optional[str]
        draft: Optional[bool]
        id: str
        instance_identity: Optional[AgentIdentity]
        metadata: dict[str, str]
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION]
        status: Optional[Union[str, AgentVersionStatus]]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                id: str, 
                metadata: dict[str, str], 
                name: str, 
                object: Literal[AgentObjectType.AGENT_VERSION], 
                status: Optional[Union[str, AgentVersionStatus]] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETED = "deleted"
        DELETING = "deleting"
        FAILED = "failed"


    class azure.ai.projects.models.AgenticIdentityPreviewCredentials(BaseCredentials, discriminator='AgenticIdentityToken_Preview'):
        type: Literal[CredentialType.AGENTIC_IDENTITY_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiError(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[ApiError]]
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
                details: Optional[list[ApiError]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiErrorResponse(_Model):
        error: ApiError

        @overload
        def __init__(
                self, 
                *, 
                error: ApiError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiKeyCredentials(BaseCredentials, discriminator='ApiKey'):
        api_key: Optional[str]
        type: Literal[CredentialType.API_KEY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApplyPatchToolParam(Tool, discriminator='apply_patch'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        type: Literal[ToolType.APPLY_PATCH]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApproximateLocation(_Model):
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


    class azure.ai.projects.models.ArtifactProfile(_Model):
        category: Union[str, FoundryModelArtifactProfileCategory]
        signals: Optional[list[Union[str, FoundryModelArtifactProfileSignal]]]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, FoundryModelArtifactProfileCategory], 
                signals: Optional[list[Union[str, FoundryModelArtifactProfileSignal]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AsyncUpdateMemoriesLROPoller(AsyncLROPoller[MemoryStoreUpdateCompletedResult]):
        property superseded_by: Optional[str]    # Read-only
        property update_id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[MemoryStoreUpdateCompletedResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...


    class azure.ai.projects.models.AttackStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSI_ATTACK = "ansi_attack"
        ASCII_ART = "ascii_art"
        ASCII_SMUGGLER = "ascii_smuggler"
        ATBASH = "atbash"
        BASE64 = "base64"
        BASELINE = "baseline"
        BINARY = "binary"
        CAESAR = "caesar"
        CHARACTER_SPACE = "character_space"
        CHARACTER_SWAP = "character_swap"
        CRESCENDO = "crescendo"
        DIACRITIC = "diacritic"
        DIFFICULT = "difficult"
        EASY = "easy"
        FLIP = "flip"
        INDIRECT_JAILBREAK = "indirect_jailbreak"
        JAILBREAK = "jailbreak"
        LEETSPEAK = "leetspeak"
        MODERATE = "moderate"
        MORSE = "morse"
        MULTI_TURN = "multi_turn"
        ROT13 = "rot13"
        STRING_JOIN = "string_join"
        SUFFIX_APPEND = "suffix_append"
        TENSE = "tense"
        UNICODE_CONFUSABLE = "unicode_confusable"
        UNICODE_SUBSTITUTION = "unicode_substitution"
        URL = "url"


    class azure.ai.projects.models.AutoCodeInterpreterToolParam(_Model):
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


    class azure.ai.projects.models.AzureAIAgentTarget(EvaluationTarget, discriminator='azure_ai_agent'):
        name: str
        tool_descriptions: Optional[list[ToolDescription]]
        tools: Optional[list[Tool]]
        type: Literal["azure_ai_agent"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tool_descriptions: Optional[list[ToolDescription]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIAgentTargetParam(TypedDict, total=False):
        key "name": Required[str]
        key "tool_descriptions": List[ToolDescriptionParam]
        key "type": Required[Literal["azure_ai_agent"]]
        key "version": str


    class azure.ai.projects.models.AzureAIBenchmarkPreviewEvalRunDataSource(TypedDict, total=False):
        key "input_messages": InputMessagesItemReference
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_benchmark_preview"]]


    class azure.ai.projects.models.AzureAIDataSourceConfig(TypedDict, total=False):
        key "scenario": Required[str]
        key "type": Required[Literal["azure_ai_source"]]


    class azure.ai.projects.models.AzureAIModelTarget(EvaluationTarget, discriminator='azure_ai_model'):
        model: Optional[str]
        sampling_params: Optional[ModelSamplingParams]
        type: Literal["azure_ai_model"]

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[str] = ..., 
                sampling_params: Optional[ModelSamplingParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIModelTargetParam(TypedDict, total=False):
        key "model": str
        key "sampling_params": ModelSamplingConfigParam
        key "type": Required[Literal["azure_ai_model"]]


    class azure.ai.projects.models.AzureAIResponsesEvalRunDataSource(TypedDict, total=False):
        key "event_configuration_id": str
        key "item_generation_params": Required[ResponseRetrievalItemGenerationParams]
        key "max_runs_hourly": int
        key "type": Required[Literal["azure_ai_responses"]]


    class azure.ai.projects.models.AzureAISearchIndex(Index, discriminator='AzureSearch'):
        connection_name: str
        description: str
        field_mapping: Optional[FieldMapping]
        id: str
        index_name: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.AZURE_SEARCH]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                description: Optional[str] = ..., 
                field_mapping: Optional[FieldMapping] = ..., 
                index_name: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"
        SIMPLE = "simple"
        VECTOR = "vector"
        VECTOR_SEMANTIC_HYBRID = "vector_semantic_hybrid"
        VECTOR_SIMPLE_HYBRID = "vector_simple_hybrid"


    class azure.ai.projects.models.AzureAISearchTool(Tool, discriminator='azure_ai_search'):
        azure_ai_search: AzureAISearchToolResource
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchToolResource(_Model):
        indexes: list[AISearchIndexResource]

        @overload
        def __init__(
                self, 
                *, 
                indexes: list[AISearchIndexResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchToolboxTool(ToolboxTool, discriminator='azure_ai_search'):
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionBinding(_Model):
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


    class azure.ai.projects.models.AzureFunctionDefinition(_Model):
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


    class azure.ai.projects.models.AzureFunctionDefinitionFunction(_Model):
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


    class azure.ai.projects.models.AzureFunctionStorageQueue(_Model):
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


    class azure.ai.projects.models.AzureFunctionTool(Tool, discriminator='azure_function'):
        azure_function: AzureFunctionDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.AZURE_FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureOpenAIModelConfiguration(RedTeamTargetConfig, discriminator='AzureOpenAIModel'):
        model_deployment_name: str
        type: Literal["AzureOpenAIModel"]

        @overload
        def __init__(
                self, 
                *, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BaseCredentials(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchConfiguration(_Model):
        count: Optional[int]
        freshness: Optional[str]
        instance_name: str
        market: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                instance_name: str, 
                market: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchPreviewTool(Tool, discriminator='bing_custom_search_preview'):
        bing_custom_search_preview: BingCustomSearchToolParameters
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search_preview: BingCustomSearchToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchToolParameters(_Model):
        search_configurations: list[BingCustomSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingCustomSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingSearchConfiguration(_Model):
        count: Optional[int]
        freshness: Optional[str]
        market: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                market: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingSearchToolParameters(_Model):
        search_configurations: list[BingGroundingSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingGroundingSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingTool(Tool, discriminator='bing_grounding'):
        bing_grounding: BingGroundingSearchToolParameters
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.BING_GROUNDING]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: BingGroundingSearchToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BlobReference(_Model):
        blob_uri: str
        credential: BlobReferenceSasCredential
        storage_account_arm_id: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str, 
                credential: BlobReferenceSasCredential, 
                storage_account_arm_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BlobReferenceSasCredential(_Model):
        sas_uri: str
        type: Literal["SAS"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.BotServiceAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotService'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BotServiceRbacAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceRbac'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BotServiceTenantAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceTenant'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationPreviewTool(Tool, discriminator='browser_automation_preview'):
        browser_automation_preview: BrowserAutomationToolParameters
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation_preview: BrowserAutomationToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationPreviewToolboxTool(ToolboxTool, discriminator='browser_automation_preview'):
        browser_automation_preview: BrowserAutomationToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.BROWSER_AUTOMATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation_preview: BrowserAutomationToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationToolConnectionParameters(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationToolParameters(_Model):
        connection: BrowserAutomationToolConnectionParameters

        @overload
        def __init__(
                self, 
                *, 
                connection: BrowserAutomationToolConnectionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CallableToolAllowedCaller(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "direct"
        PROGRAMMATIC = "programmatic"


    class azure.ai.projects.models.CaptureStructuredOutputsTool(Tool, discriminator='capture_structured_outputs'):
        description: Optional[str]
        name: Optional[str]
        outputs: StructuredOutputDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: StructuredOutputDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ChartCoordinate(_Model):
        size: int
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                size: int, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ChatSummaryMemoryItem(MemoryItem, discriminator='chat_summary'):
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


    class azure.ai.projects.models.ClusterInsightResult(_Model):
        clusters: list[InsightCluster]
        coordinates: Optional[dict[str, ChartCoordinate]]
        summary: InsightSummary

        @overload
        def __init__(
                self, 
                *, 
                clusters: list[InsightCluster], 
                coordinates: Optional[dict[str, ChartCoordinate]] = ..., 
                summary: InsightSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ClusterTokenUsage(_Model):
        input_token_usage: int
        output_token_usage: int
        total_token_usage: int

        @overload
        def __init__(
                self, 
                *, 
                input_token_usage: int, 
                output_token_usage: int, 
                total_token_usage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='code'):
        blob_uri: Optional[str]
        code_text: Optional[str]
        data_schema: dict[str, any]
        entry_point: Optional[str]
        image_tag: Optional[str]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.CODE]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                code_text: Optional[str] = ..., 
                data_schema: Optional[dict[str, Any]] = ..., 
                entry_point: Optional[str] = ..., 
                image_tag: Optional[str] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeConfiguration(_Model):
        content_hash: Optional[str]
        dependency_resolution: Union[str, CodeDependencyResolution]
        entry_point: list[str]
        runtime: str

        @overload
        def __init__(
                self, 
                *, 
                dependency_resolution: Union[str, CodeDependencyResolution], 
                entry_point: list[str], 
                runtime: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeDependencyResolution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUNDLED = "bundled"
        REMOTE_BUILD = "remote_build"


    class azure.ai.projects.models.CodeInterpreterTool(Tool, discriminator='code_interpreter'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeInterpreterToolboxTool(ToolboxTool, discriminator='code_interpreter'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ComparisonFilter(_Model):
        key: str
        type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]
        value: Union[str, float, bool, list[Union[str, float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"], 
                value: Union[str, float, bool, list[Union[str, float]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CompoundFilter(_Model):
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


    class azure.ai.projects.models.ComputerEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROWSER = "browser"
        LINUX = "linux"
        MAC = "mac"
        UBUNTU = "ubuntu"
        WINDOWS = "windows"


    class azure.ai.projects.models.ComputerTool(Tool, discriminator='computer'):
        type: Literal[ToolType.COMPUTER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ComputerUsePreviewTool(Tool, discriminator='computer_use_preview'):
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


    class azure.ai.projects.models.Connection(_Model):
        credentials: BaseCredentials
        id: str
        is_default: bool
        metadata: dict[str, str]
        name: str
        target: str
        type: Union[str, ConnectionType]


    class azure.ai.projects.models.ConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "ApiKey"
        APPLICATION_CONFIGURATION = "AppConfig"
        APPLICATION_INSIGHTS = "AppInsights"
        AZURE_AI_SEARCH = "CognitiveSearch"
        AZURE_BLOB_STORAGE = "AzureBlob"
        AZURE_OPEN_AI = "AzureOpenAI"
        AZURE_STORAGE_ACCOUNT = "AzureStorageAccount"
        COSMOS_DB = "CosmosDB"
        CUSTOM = "CustomKeys"
        REMOTE_TOOL = "RemoteTool_Preview"


    class azure.ai.projects.models.ContainerAutoParam(FunctionShellToolParamEnvironment, discriminator='container_auto'):
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


    class azure.ai.projects.models.ContainerConfiguration(_Model):
        image: str

        @overload
        def __init__(
                self, 
                *, 
                image: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerMemoryLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMORY_16GB = "16g"
        MEMORY_1GB = "1g"
        MEMORY_4GB = "4g"
        MEMORY_64GB = "64g"


    class azure.ai.projects.models.ContainerNetworkPolicyAllowlistParam(ContainerNetworkPolicyParam, discriminator='allowlist'):
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


    class azure.ai.projects.models.ContainerNetworkPolicyDisabledParam(ContainerNetworkPolicyParam, discriminator='disabled'):
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyDomainSecretParam(_Model):
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


    class azure.ai.projects.models.ContainerNetworkPolicyParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWLIST = "allowlist"
        DISABLED = "disabled"


    class azure.ai.projects.models.ContainerSkill(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerSkillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        SKILL_REFERENCE = "skill_reference"


    class azure.ai.projects.models.ContinuousEvaluationRuleAction(EvaluationRuleAction, discriminator='continuousEvaluation'):
        eval_id: str
        max_hourly_runs: Optional[int]
        sampling_rate: Optional[float]
        type: Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                eval_id: str, 
                max_hourly_runs: Optional[int] = ..., 
                sampling_rate: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CosmosDBIndex(Index, discriminator='CosmosDBNoSqlVectorStore'):
        connection_name: str
        container_name: str
        database_name: str
        description: str
        embedding_configuration: EmbeddingConfiguration
        field_mapping: FieldMapping
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.COSMOS_DB]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                container_name: str, 
                database_name: str, 
                description: Optional[str] = ..., 
                embedding_configuration: EmbeddingConfiguration, 
                field_mapping: FieldMapping, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateAsyncResponse(_Model):
        location: Optional[str]
        operation_result: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                operation_result: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateSkillVersionFromFilesBody(_Model):
        default: Optional[bool]
        files: list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[bool] = ..., 
                files: list[FileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTranscriptionResponseJsonUsage(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTranscriptionResponseJsonUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DURATION = "duration"
        TOKENS = "tokens"


    class azure.ai.projects.models.CredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC_IDENTITY_PREVIEW = "AgenticIdentityToken_Preview"
        API_KEY = "ApiKey"
        CUSTOM = "CustomKeys"
        ENTRA_ID = "AAD"
        NONE = "None"
        SAS = "SAS"


    class azure.ai.projects.models.CronTrigger(Trigger, discriminator='Cron'):
        end_time: Optional[datetime]
        expression: str
        start_time: Optional[datetime]
        time_zone: Optional[str]
        type: Literal[TriggerType.CRON]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expression: str, 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomCredential(CustomCredentialGenerated, discriminator='CustomKeys'):
        credential_keys: Dict[str, str]
        type: Union[str, CredentialType]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.CustomGrammarFormatParam(CustomToolParamFormat, discriminator='grammar'):
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


    class azure.ai.projects.models.CustomRoutineTrigger(RoutineTrigger, discriminator='custom'):
        event_name: Optional[str]
        parameters: dict[str, Any]
        provider: str
        type: Literal[RoutineTriggerType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                event_name: Optional[str] = ..., 
                parameters: dict[str, Any], 
                provider: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomTextFormatParam(CustomToolParamFormat, discriminator='text'):
        type: Literal[CustomToolParamFormatType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParam(Tool, discriminator='custom'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        format: Optional[CustomToolParamFormat]
        name: str
        type: Literal[ToolType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                format: Optional[CustomToolParamFormat] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParamFormat(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParamFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAMMAR = "grammar"
        TEXT = "text"


    class azure.ai.projects.models.DailyRecurrenceSchedule(RecurrenceSchedule, discriminator='Daily'):
        hours: list[int]
        type: Literal[RecurrenceType.DAILY]

        @overload
        def __init__(
                self, 
                *, 
                hours: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        finished_at: Optional[datetime]
        id: str
        inputs: Optional[DataGenerationJobInputs]
        result: Optional[DataGenerationJobResult]
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[DataGenerationJobInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobInputs(_Model):
        name: str
        options: DataGenerationJobOptions
        output_options: Optional[DataGenerationJobOutputOptions]
        scenario: Union[str, DataGenerationJobScenario]
        sources: list[DataGenerationJobSource]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                options: DataGenerationJobOptions, 
                output_options: Optional[DataGenerationJobOutputOptions] = ..., 
                scenario: Union[str, DataGenerationJobScenario], 
                sources: list[DataGenerationJobSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOptions(_Model):
        max_samples: int
        model_options: Optional[DataGenerationModelOptions]
        train_split: Optional[float]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutputOptions(_Model):
        description: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATASET = "dataset"
        FILE = "file"


    class azure.ai.projects.models.DataGenerationJobResult(_Model):
        generated_samples: int
        outputs: Optional[list[DataGenerationJobOutput]]
        token_usage: Optional[DataGenerationTokenUsage]

        @overload
        def __init__(
                self, 
                *, 
                generated_samples: int, 
                outputs: Optional[list[DataGenerationJobOutput]] = ..., 
                token_usage: Optional[DataGenerationTokenUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobScenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION = "evaluation"
        REINFORCEMENT_FINETUNING = "reinforcement_finetuning"
        SUPERVISED_FINETUNING = "supervised_finetuning"


    class azure.ai.projects.models.DataGenerationJobSource(_Model):
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


    class azure.ai.projects.models.DataGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        FILE = "file"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.models.DataGenerationJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMPLE_QNA = "simple_qna"
        TASK_GENERATION = "task_generation"
        TOOL_USE = "tool_use"
        TRACES = "traces"


    class azure.ai.projects.models.DataGenerationModelOptions(_Model):
        model: str

        @overload
        def __init__(
                self, 
                *, 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationTokenUsage(_Model):
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int


    class azure.ai.projects.models.DatasetCredential(_Model):
        blob_reference: BlobReference

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetDataGenerationJobOutput(DataGenerationJobOutput, discriminator='dataset'):
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Literal[DataGenerationJobOutputType.DATASET]
        version: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='dataset'):
        description: Optional[str]
        name: str
        type: Literal[EvaluatorGenerationJobSourceType.DATASET]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetReference(_Model):
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.ai.projects.models.DatasetVersion(_Model):
        connection_name: Optional[str]
        data_uri: str
        description: Optional[str]
        id: Optional[str]
        is_reference: Optional[bool]
        name: str
        tags: Optional[dict[str, str]]
        type: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.ai.projects.models.DeleteAgentResponse(_Model):
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[AgentObjectType.AGENT_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteAgentVersionResponse(_Model):
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION_DELETED]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[AgentObjectType.AGENT_VERSION_DELETED], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteMemoryResult(_Model):
        deleted: bool
        memory_id: str
        object: Literal[MemoryStoreObjectType.MEMORY_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                memory_id: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteMemoryStoreResult(_Model):
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteSkillResult(_Model):
        deleted: bool
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteSkillVersionResult(_Model):
        deleted: bool
        id: str
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: str, 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Deployment(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODEL_DEPLOYMENT = "ModelDeployment"


    class azure.ai.projects.models.Dimension(_Model):
        always_applicable: Optional[bool]
        description: str
        id: str
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                always_applicable: Optional[bool] = ..., 
                description: str, 
                id: str, 
                weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DispatchRoutineResult(_Model):
        action_correlation_id: Optional[str]
        dispatch_id: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_correlation_id: Optional[str] = ..., 
                dispatch_id: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EmbeddingConfiguration(_Model):
        embedding_field: str
        model_deployment_name: str

        @overload
        def __init__(
                self, 
                *, 
                embedding_field: str, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EmptyModelParam(_Model):


    class azure.ai.projects.models.EndpointBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='endpoint'):
        connection_name: str
        data_schema: dict[str, any]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.ENDPOINT]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='Entra'):
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraIDCredentials(BaseCredentials, discriminator='AAD'):
        type: Literal[CredentialType.ENTRA_ID]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalCsvFileIdSource(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Literal["file_id"]]


    class azure.ai.projects.models.EvalCsvRunDataSource(TypedDict, total=False):
        key "source": Required[EvalCsvFileIdSource]
        key "type": Required[Literal["csv"]]


    class azure.ai.projects.models.EvalResult(_Model):
        name: str
        passed: bool
        score: float
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                passed: bool, 
                score: float, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultCompareItem(_Model):
        delta_estimate: float
        p_value: float
        treatment_effect: Union[str, TreatmentEffectType]
        treatment_run_id: str
        treatment_run_summary: EvalRunResultSummary

        @overload
        def __init__(
                self, 
                *, 
                delta_estimate: float, 
                p_value: float, 
                treatment_effect: Union[str, TreatmentEffectType], 
                treatment_run_id: str, 
                treatment_run_summary: EvalRunResultSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultComparison(_Model):
        baseline_run_summary: EvalRunResultSummary
        compare_items: list[EvalRunResultCompareItem]
        evaluator: str
        metric: str
        testing_criteria: str

        @overload
        def __init__(
                self, 
                *, 
                baseline_run_summary: EvalRunResultSummary, 
                compare_items: list[EvalRunResultCompareItem], 
                evaluator: str, 
                metric: str, 
                testing_criteria: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultSummary(_Model):
        average: float
        run_id: str
        sample_count: int
        standard_deviation: float

        @overload
        def __init__(
                self, 
                *, 
                average: float, 
                run_id: str, 
                sample_count: int, 
                standard_deviation: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationComparisonInsightRequest(InsightRequest, discriminator='EvaluationComparison'):
        baseline_run_id: str
        eval_id: str
        treatment_run_ids: list[str]
        type: Literal[InsightType.EVALUATION_COMPARISON]

        @overload
        def __init__(
                self, 
                *, 
                baseline_run_id: str, 
                eval_id: str, 
                treatment_run_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationComparisonInsightResult(InsightResult, discriminator='EvaluationComparison'):
        comparisons: list[EvalRunResultComparison]
        method: str
        type: Literal[InsightType.EVALUATION_COMPARISON]

        @overload
        def __init__(
                self, 
                *, 
                comparisons: list[EvalRunResultComparison], 
                method: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "conversation"
        TURN = "turn"


    class azure.ai.projects.models.EvaluationResultSample(InsightSample, discriminator='EvaluationResultSample'):
        correlation_info: dict[str, any]
        evaluation_result: EvalResult
        features: dict[str, any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]

        @overload
        def __init__(
                self, 
                *, 
                correlation_info: dict[str, Any], 
                evaluation_result: EvalResult, 
                features: dict[str, Any], 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRule(_Model):
        action: EvaluationRuleAction
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        event_type: Union[str, EvaluationRuleEventType]
        filter: Optional[EvaluationRuleFilter]
        id: str
        system_data: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                action: EvaluationRuleAction, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: bool, 
                event_type: Union[str, EvaluationRuleEventType], 
                filter: Optional[EvaluationRuleFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRuleAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS_EVALUATION = "continuousEvaluation"
        HUMAN_EVALUATION_PREVIEW = "humanEvaluationPreview"


    class azure.ai.projects.models.EvaluationRuleEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "manual"
        RESPONSE_COMPLETED = "responseCompleted"


    class azure.ai.projects.models.EvaluationRuleFilter(_Model):
        agent_name: str

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRunClusterInsightRequest(InsightRequest, discriminator='EvaluationRunClusterInsight'):
        eval_id: str
        model_configuration: Optional[InsightModelConfiguration]
        run_ids: list[str]
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                eval_id: str, 
                model_configuration: Optional[InsightModelConfiguration] = ..., 
                run_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRunClusterInsightResult(InsightResult, discriminator='EvaluationRunClusterInsight'):
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                cluster_insight: ClusterInsightResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationScheduleTask(ScheduleTask, discriminator='Evaluation'):
        configuration: dict[str, str]
        eval_id: str
        eval_run: dict[str, Any]
        type: Literal[ScheduleTaskType.EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                eval_id: str, 
                eval_run: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTarget(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomy(_Model):
        description: Optional[str]
        id: Optional[str]
        name: str
        properties: Optional[dict[str, str]]
        tags: Optional[dict[str, str]]
        taxonomy_categories: Optional[list[TaxonomyCategory]]
        taxonomy_input: EvaluationTaxonomyInput
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                taxonomy_categories: Optional[list[TaxonomyCategory]] = ..., 
                taxonomy_input: EvaluationTaxonomyInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomyInput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomyInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        POLICY = "policy"


    class azure.ai.projects.models.EvaluatorCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTS = "agents"
        QUALITY = "quality"
        SAFETY = "safety"


    class azure.ai.projects.models.EvaluatorCredentialRequest(_Model):
        blob_uri: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorDefinition(_Model):
        data_schema: Optional[dict[str, Any]]
        init_parameters: Optional[dict[str, Any]]
        metrics: Optional[dict[str, EvaluatorMetric]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE = "code"
        ENDPOINT = "endpoint"
        OPENAI_GRADERS = "openai_graders"
        PROMPT = "prompt"
        PROMPT_AND_CODE = "prompt_and_code"
        RUBRIC = "rubric"
        SERVICE = "service"


    class azure.ai.projects.models.EvaluatorGenerationArtifacts(_Model):
        dataset: DatasetReference
        kinds: list[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset: DatasetReference, 
                kinds: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationInputs(_Model):
        evaluator_description: Optional[str]
        evaluator_display_name: Optional[str]
        evaluator_name: str
        model: str
        sources: list[EvaluatorGenerationJobSource]

        @overload
        def __init__(
                self, 
                *, 
                evaluator_description: Optional[str] = ..., 
                evaluator_display_name: Optional[str] = ..., 
                evaluator_name: str, 
                model: str, 
                sources: list[EvaluatorGenerationJobSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        finished_at: Optional[datetime]
        id: str
        input_quality_warnings: Optional[list[RubricGenerationInputQualityWarning]]
        inputs: Optional[EvaluatorGenerationInputs]
        result: Optional[EvaluatorVersion]
        status: Union[str, JobStatus]
        usage: Optional[EvaluatorGenerationTokenUsage]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[EvaluatorGenerationInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJobSource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        DATASET = "dataset"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.models.EvaluatorGenerationTokenUsage(_Model):
        input_tokens: int
        output_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                input_tokens: int, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorMetric(_Model):
        desirable_direction: Optional[Union[str, EvaluatorMetricDirection]]
        is_primary: Optional[bool]
        max_value: Optional[float]
        min_value: Optional[float]
        threshold: Optional[float]
        type: Optional[Union[str, EvaluatorMetricType]]

        @overload
        def __init__(
                self, 
                *, 
                desirable_direction: Optional[Union[str, EvaluatorMetricDirection]] = ..., 
                is_primary: Optional[bool] = ..., 
                max_value: Optional[float] = ..., 
                min_value: Optional[float] = ..., 
                threshold: Optional[float] = ..., 
                type: Optional[Union[str, EvaluatorMetricType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorMetricDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECREASE = "decrease"
        INCREASE = "increase"
        NEUTRAL = "neutral"


    class azure.ai.projects.models.EvaluatorMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        CONTINUOUS = "continuous"
        ORDINAL = "ordinal"


    class azure.ai.projects.models.EvaluatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "builtin"
        CUSTOM = "custom"


    class azure.ai.projects.models.EvaluatorVersion(_Model):
        categories: list[Union[str, EvaluatorCategory]]
        created_at: datetime
        created_by: str
        definition: EvaluatorDefinition
        description: Optional[str]
        display_name: Optional[str]
        evaluator_type: Union[str, EvaluatorType]
        generation_artifacts: Optional[EvaluatorGenerationArtifacts]
        generation_job_id: Optional[str]
        id: Optional[str]
        metadata: Optional[dict[str, str]]
        modified_at: datetime
        name: str
        supported_evaluation_levels: Optional[list[Union[str, EvaluationLevel]]]
        tags: Optional[dict[str, str]]
        version: str
        warnings: Optional[list[Union[str, GenerationWarningType]]]

        @overload
        def __init__(
                self, 
                *, 
                categories: list[Union[str, EvaluatorCategory]], 
                definition: EvaluatorDefinition, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluator_type: Union[str, EvaluatorType], 
                metadata: Optional[dict[str, str]] = ..., 
                supported_evaluation_levels: Optional[list[Union[str, EvaluationLevel]]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ExternalAgentDefinition(AgentDefinition, discriminator='external'):
        kind: Literal[AgentKind.EXTERNAL]
        otel_agent_id: Optional[str]
        rai_config: RaiConfig

        @overload
        def __init__(
                self, 
                *, 
                otel_agent_id: Optional[str] = ..., 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricDataAgentToolParameters(_Model):
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricIQPreviewTool(Tool, discriminator='fabric_iq_preview'):
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        server_url: Optional[str]
        type: Literal[ToolType.FABRIC_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ..., 
                server_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricIQPreviewToolboxTool(ToolboxTool, discriminator='fabric_iq_preview'):
        description: str
        name: str
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        server_url: Optional[str]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FABRIC_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ..., 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FieldMapping(_Model):
        content_fields: list[str]
        filepath_field: Optional[str]
        metadata_fields: Optional[list[str]]
        title_field: Optional[str]
        url_field: Optional[str]
        vector_fields: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                content_fields: list[str], 
                filepath_field: Optional[str] = ..., 
                metadata_fields: Optional[list[str]] = ..., 
                title_field: Optional[str] = ..., 
                url_field: Optional[str] = ..., 
                vector_fields: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDataGenerationJobOutput(DataGenerationJobOutput, discriminator='file'):
        filename: str
        id: str
        type: Literal[DataGenerationJobOutputType.FILE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDataGenerationJobSource(DataGenerationJobSource, discriminator='file'):
        description: str
        id: str
        type: Literal[DataGenerationJobSourceType.FILE]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDatasetVersion(DatasetVersion, discriminator='uri_file'):
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FILE]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileSearchTool(Tool, discriminator='file_search'):
        description: Optional[str]
        filters: Optional[Filters]
        max_num_results: Optional[int]
        name: Optional[str]
        ranking_options: Optional[RankingOptions]
        tool_configs: Optional[dict[str, ToolConfig]]
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
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                vector_store_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileSearchToolboxTool(ToolboxTool, discriminator='file_search'):
        description: str
        filters: Optional[Filters]
        max_num_results: Optional[int]
        name: str
        ranking_options: Optional[RankingOptions]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FILE_SEARCH]
        vector_store_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                filters: Optional[Filters] = ..., 
                max_num_results: Optional[int] = ..., 
                name: Optional[str] = ..., 
                ranking_options: Optional[RankingOptions] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                vector_store_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FixedRatioVersionSelectionRule(VersionSelectionRule, discriminator='FixedRatio'):
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str, 
                traffic_percentage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FolderDatasetVersion(DatasetVersion, discriminator='uri_folder'):
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FOLDER]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FoundryModelArtifactProfileCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_ONLY = "DataOnly"
        RUNTIME_DEPENDENT = "RuntimeDependent"
        UNKNOWN = "Unknown"


    class azure.ai.projects.models.FoundryModelArtifactProfileSignal(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_PYTHON_CODE = "CustomPythonCode"
        DYNAMIC_OPS = "DynamicOps"
        NATIVE_BINARY = "NativeBinary"
        PICKLE_DESERIALIZATION = "PickleDeserialization"
        UNKNOWN_FORMAT = "UnknownFormat"


    class azure.ai.projects.models.FoundryModelSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_UPLOAD = "LocalUpload"
        TRAINING_JOB = "TrainingJob"


    class azure.ai.projects.models.FoundryModelWarning(_Model):
        code: Optional[Union[str, FoundryModelWarningCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, FoundryModelWarningCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FoundryModelWarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNTIME_DEPENDENT_ARTIFACT = "RuntimeDependentArtifact"
        UNCLASSIFIED_ARTIFACT = "UnclassifiedArtifact"


    class azure.ai.projects.models.FoundryModelWeightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAFT_MODEL = "DraftModel"
        FULL_WEIGHT = "FullWeight"
        LO_RA = "LoRA"


    class azure.ai.projects.models.FunctionShellToolParam(Tool, discriminator='shell'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        description: Optional[str]
        environment: Optional[FunctionShellToolParamEnvironment]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.SHELL]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                description: Optional[str] = ..., 
                environment: Optional[FunctionShellToolParamEnvironment] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentContainerReferenceParam(FunctionShellToolParamEnvironment, discriminator='container_reference'):
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


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentLocalEnvironmentParam(FunctionShellToolParamEnvironment, discriminator='local'):
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


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_AUTO = "container_auto"
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.projects.models.FunctionTool(Tool, discriminator='function'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        output_schema: Optional[dict[str, Any]]
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                output_schema: Optional[dict[str, Any]] = ..., 
                parameters: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionToolParam(_Model):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        output_schema: Optional[dict[str, Any]]
        parameters: Optional[EmptyModelParam]
        strict: Optional[bool]
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                output_schema: Optional[dict[str, Any]] = ..., 
                parameters: Optional[EmptyModelParam] = ..., 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.GenerationWarningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INPUT_QUALITY = "input_quality"


    class azure.ai.projects.models.GitHubIssueEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSED = "closed"
        OPENED = "opened"


    class azure.ai.projects.models.GitHubIssueRoutineTrigger(RoutineTrigger, discriminator='github_issue'):
        connection_id: str
        issue_event: Union[str, GitHubIssueEvent]
        owner: str
        repository: str
        type: Literal[RoutineTriggerType.GITHUB_ISSUE]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                issue_event: Union[str, GitHubIssueEvent], 
                owner: str, 
                repository: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.GrammarSyntax1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARK = "lark"
        REGEX = "regex"


    class azure.ai.projects.models.HeaderTelemetryEndpointAuth(TelemetryEndpointAuth, discriminator='header'):
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]

        @overload
        def __init__(
                self, 
                *, 
                header_name: str, 
                secret_id: str, 
                secret_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HostedAgentDefinition(AgentDefinition, discriminator='hosted'):
        code_configuration: Optional[CodeConfiguration]
        container_configuration: Optional[ContainerConfiguration]
        cpu: str
        environment_variables: Optional[dict[str, str]]
        kind: Literal[AgentKind.HOSTED]
        memory: str
        protocol_versions: Optional[list[ProtocolVersionRecord]]
        rai_config: RaiConfig
        telemetry_config: Optional[TelemetryConfig]

        @overload
        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                container_configuration: Optional[ContainerConfiguration] = ..., 
                cpu: str, 
                environment_variables: Optional[dict[str, str]] = ..., 
                memory: str, 
                protocol_versions: Optional[list[ProtocolVersionRecord]] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                telemetry_config: Optional[TelemetryConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HourlyRecurrenceSchedule(RecurrenceSchedule, discriminator='Hourly'):
        type: Literal[RecurrenceType.HOURLY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HumanEvaluationPreviewRuleAction(EvaluationRuleAction, discriminator='humanEvaluationPreview'):
        template_id: str
        type: Literal[EvaluationRuleActionType.HUMAN_EVALUATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                template_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HybridSearchOptions(_Model):
        embedding_weight: float
        text_weight: float

        @overload
        def __init__(
                self, 
                *, 
                embedding_weight: float, 
                text_weight: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ImageGenAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        EDIT = "edit"
        GENERATE = "generate"


    class azure.ai.projects.models.ImageGenTool(Tool, discriminator='image_generation'):
        action: Optional[Union[str, ImageGenAction]]
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
        size: Optional[Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.IMAGE_GENERATION]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ImageGenAction]] = ..., 
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
                size: Optional[Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ImageGenToolInputImageMask(_Model):
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


    class azure.ai.projects.models.Index(_Model):
        description: Optional[str]
        id: Optional[str]
        name: str
        tags: Optional[dict[str, str]]
        type: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.IndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEARCH = "AzureSearch"
        COSMOS_DB = "CosmosDBNoSqlVectorStore"
        MANAGED_AZURE_SEARCH = "ManagedAzureSearch"


    class azure.ai.projects.models.InlineSkillParam(ContainerSkill, discriminator='inline'):
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


    class azure.ai.projects.models.InlineSkillSourceParam(_Model):
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


    class azure.ai.projects.models.InputFidelity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"


    class azure.ai.projects.models.Insight(_Model):
        display_name: str
        insight_id: str
        metadata: InsightsMetadata
        request: InsightRequest
        result: Optional[InsightResult]
        state: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                request: InsightRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightCluster(_Model):
        description: str
        id: str
        label: str
        samples: Optional[list[InsightSample]]
        sub_clusters: Optional[list[InsightCluster]]
        suggestion: str
        suggestion_title: str
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                label: str, 
                samples: Optional[list[InsightSample]] = ..., 
                sub_clusters: Optional[list[InsightCluster]] = ..., 
                suggestion: str, 
                suggestion_title: str, 
                weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightModelConfiguration(_Model):
        model_deployment_name: str

        @overload
        def __init__(
                self, 
                *, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightRequest(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightResult(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightSample(_Model):
        correlation_info: dict[str, Any]
        features: dict[str, Any]
        id: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                correlation_info: dict[str, Any], 
                features: dict[str, Any], 
                id: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightScheduleTask(ScheduleTask, discriminator='Insight'):
        configuration: dict[str, str]
        insight: Insight
        type: Literal[ScheduleTaskType.INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                insight: Insight
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightSummary(_Model):
        method: str
        sample_count: int
        unique_cluster_count: int
        unique_subcluster_count: int
        usage: ClusterTokenUsage

        @overload
        def __init__(
                self, 
                *, 
                method: str, 
                sample_count: int, 
                unique_cluster_count: int, 
                unique_subcluster_count: int, 
                usage: ClusterTokenUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_CLUSTER_INSIGHT = "AgentClusterInsight"
        EVALUATION_COMPARISON = "EvaluationComparison"
        EVALUATION_RUN_CLUSTER_INSIGHT = "EvaluationRunClusterInsight"


    class azure.ai.projects.models.InsightsMetadata(_Model):
        completed_at: Optional[datetime]
        created_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                created_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvocationsProtocolConfiguration(_Model):


    class azure.ai.projects.models.InvocationsWsProtocolConfiguration(_Model):


    class azure.ai.projects.models.InvokeAgentInvocationsApiDispatchPayload(RoutineDispatchPayload, discriminator='invoke_agent_invocations_api'):
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_INVOCATIONS_API]

        @overload
        def __init__(
                self, 
                *, 
                input: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentInvocationsApiRoutineAction(RoutineAction, discriminator='invoke_agent_invocations_api'):
        agent_endpoint_id: Optional[str]
        agent_name: Optional[str]
        input: Optional[Any]
        session_id: Optional[str]
        type: Literal[RoutineActionType.INVOKE_AGENT_INVOCATIONS_API]

        @overload
        def __init__(
                self, 
                *, 
                agent_endpoint_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                input: Optional[Any] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentResponsesApiDispatchPayload(RoutineDispatchPayload, discriminator='invoke_agent_responses_api'):
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_RESPONSES_API]

        @overload
        def __init__(
                self, 
                *, 
                input: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentResponsesApiRoutineAction(RoutineAction, discriminator='invoke_agent_responses_api'):
        agent_endpoint_id: Optional[str]
        agent_name: Optional[str]
        conversation: Optional[str]
        input: Optional[Any]
        type: Literal[RoutineActionType.INVOKE_AGENT_RESPONSES_API]

        @overload
        def __init__(
                self, 
                *, 
                agent_endpoint_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                conversation: Optional[str] = ..., 
                input: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        QUEUED = "queued"
        SUCCEEDED = "succeeded"


    class azure.ai.projects.models.LlmGeneratedVoiceGreetingConfig(VoiceGreetingConfig, discriminator='llm_generated'):
        prompt: str
        tool_choice: Optional[VoiceAgentToolChoice]
        type: Literal["llm_generated"]

        @overload
        def __init__(
                self, 
                *, 
                prompt: str, 
                tool_choice: Optional[VoiceAgentToolChoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.LocalShellToolParam(Tool, discriminator='local_shell'):
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.LOCAL_SHELL]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.LocalSkillParam(_Model):
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


    class azure.ai.projects.models.LogProbProperties(_Model):
        bytes: list[int]
        logprob: float
        token: str

        @overload
        def __init__(
                self, 
                *, 
                bytes: list[int], 
                logprob: float, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.LoraConfig(_Model):
        alpha: Optional[int]
        dropout: Optional[float]
        rank: Optional[int]
        target_modules: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alpha: Optional[int] = ..., 
                dropout: Optional[float] = ..., 
                rank: Optional[int] = ..., 
                target_modules: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MCPListToolsTool(_Model):
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


    class azure.ai.projects.models.MCPListToolsToolAnnotations(_Model):


    class azure.ai.projects.models.MCPListToolsToolInputSchema(_Model):


    class azure.ai.projects.models.MCPTool(Tool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        connector_id: Optional[Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]]
        defer_loading: Optional[bool]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        tunnel_id: Optional[str]
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                connector_id: Optional[Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams, connector_outlookcalendar, connector_outlookemail, connector_sharepoint]] = ..., 
                defer_loading: Optional[bool] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                tunnel_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MCPToolFilter(_Model):
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


    class azure.ai.projects.models.MCPToolRequireApproval(_Model):
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


    class azure.ai.projects.models.MCPToolboxTool(ToolboxTool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        connector_id: Optional[Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]]
        defer_loading: Optional[bool]
        description: str
        headers: Optional[dict[str, str]]
        name: str
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: dict[str, ToolConfig]
        tunnel_id: Optional[str]
        type: Literal[ToolboxToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                connector_id: Optional[Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams, connector_outlookcalendar, connector_outlookemail, connector_sharepoint]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                tunnel_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ManagedAgentIdentityBlueprintReference(AgentBlueprintReference, discriminator='ManagedAgentIdentityBlueprint'):
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]

        @overload
        def __init__(
                self, 
                *, 
                blueprint_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ManagedAzureAISearchIndex(Index, discriminator='ManagedAzureSearch'):
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.MANAGED_AZURE_SEARCH]
        vector_store_id: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                vector_store_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.McpProtocolConfiguration(_Model):


    class azure.ai.projects.models.MemoryItem(_Model):
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


    class azure.ai.projects.models.MemoryItemKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT_SUMMARY = "chat_summary"
        PROCEDURAL = "procedural"
        USER_PROFILE = "user_profile"


    class azure.ai.projects.models.MemoryOperation(_Model):
        kind: Union[str, MemoryOperationKind]
        memory_item: MemoryItem

        @overload
        def __init__(
                self, 
                *, 
                kind: Union[str, MemoryOperationKind], 
                memory_item: MemoryItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "create"
        DELETE = "delete"
        UPDATE = "update"


    class azure.ai.projects.models.MemorySearchItem(_Model):
        memory_item: MemoryItem

        @overload
        def __init__(
                self, 
                *, 
                memory_item: MemoryItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemorySearchOptions(_Model):
        max_memories: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_memories: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemorySearchPreviewTool(Tool, discriminator='memory_search_preview'):
        memory_store_name: str
        scope: str
        search_options: Optional[MemorySearchOptions]
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                memory_store_name: str, 
                scope: str, 
                search_options: Optional[MemorySearchOptions] = ..., 
                update_delay: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefaultDefinition(MemoryStoreDefinition, discriminator='default'):
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: Optional[MemoryStoreDefaultOptions]

        @overload
        def __init__(
                self, 
                *, 
                chat_model: str, 
                embedding_model: str, 
                options: Optional[MemoryStoreDefaultOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefaultOptions(_Model):
        chat_summary_enabled: bool
        default_ttl_seconds: Optional[timedelta]
        procedural_memory_enabled: Optional[bool]
        user_profile_details: Optional[str]
        user_profile_enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                chat_summary_enabled: bool, 
                default_ttl_seconds: Optional[timedelta] = ..., 
                procedural_memory_enabled: Optional[bool] = ..., 
                user_profile_details: Optional[str] = ..., 
                user_profile_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefinition(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDeleteScopeResult(_Model):
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_SCOPE_DELETED]
        scope: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE_SCOPE_DELETED], 
                scope: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDetails(_Model):
        created_at: datetime
        definition: MemoryStoreDefinition
        description: Optional[str]
        id: str
        metadata: Optional[dict[str, str]]
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE]
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE], 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.ai.projects.models.MemoryStoreObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMORY_DELETED = "memory_store.item.deleted"
        MEMORY_STORE = "memory_store"
        MEMORY_STORE_DELETED = "memory_store.deleted"
        MEMORY_STORE_SCOPE_DELETED = "memory_store.scope.deleted"


    class azure.ai.projects.models.MemoryStoreOperationUsage(_Model):
        embedding_tokens: int
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                embedding_tokens: int, 
                input_tokens: int, 
                input_tokens_details: ResponseUsageInputTokensDetails, 
                output_tokens: int, 
                output_tokens_details: ResponseUsageOutputTokensDetails, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreSearchResult(_Model):
        memories: list[MemorySearchItem]
        search_id: str
        usage: MemoryStoreOperationUsage

        @overload
        def __init__(
                self, 
                *, 
                memories: list[MemorySearchItem], 
                search_id: str, 
                usage: MemoryStoreOperationUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateCompletedResult(_Model):
        memory_operations: list[MemoryOperation]
        usage: MemoryStoreOperationUsage

        @overload
        def __init__(
                self, 
                *, 
                memory_operations: list[MemoryOperation], 
                usage: MemoryStoreOperationUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateResult(_Model):
        error: Optional[ApiError]
        result: Optional[MemoryStoreUpdateCompletedResult]
        status: Union[str, MemoryStoreUpdateStatus]
        superseded_by: Optional[str]
        update_id: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ApiError] = ..., 
                result: Optional[MemoryStoreUpdateCompletedResult] = ..., 
                status: Union[str, MemoryStoreUpdateStatus], 
                superseded_by: Optional[str] = ..., 
                update_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        QUEUED = "queued"
        SUPERSEDED = "superseded"


    class azure.ai.projects.models.Metadata(_Model):


    class azure.ai.projects.models.MicrosoftFabricPreviewTool(Tool, discriminator='fabric_dataagent_preview'):
        fabric_dataagent_preview: FabricDataAgentToolParameters
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                fabric_dataagent_preview: FabricDataAgentToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelCredentialRequest(_Model):
        blob_uri: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelDeployment(Deployment, discriminator='ModelDeployment'):
        capabilities: dict[str, str]
        connection_name: Optional[str]
        model_name: str
        model_publisher: str
        model_version: str
        name: str
        sku: ModelDeploymentSku
        type: Literal[DeploymentType.MODEL_DEPLOYMENT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelDeploymentSku(_Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: str

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                family: str, 
                name: str, 
                size: str, 
                tier: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelPendingUploadRequest(_Model):
        connection_name: Optional[str]
        pending_upload_id: Optional[str]
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelPendingUploadResponse(_Model):
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference, 
                pending_upload_id: str, 
                pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelSamplingConfigParam(TypedDict, total=False):
        key "max_completion_tokens": int
        key "seed": int
        key "temperature": float
        key "top_p": float


    class azure.ai.projects.models.ModelSamplingParams(_Model):
        max_completion_tokens: Optional[int]
        seed: Optional[int]
        temperature: Optional[float]
        top_p: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max_completion_tokens: Optional[int] = ..., 
                seed: Optional[int] = ..., 
                temperature: Optional[float] = ..., 
                top_p: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelSourceData(_Model):
        job_id: Optional[str]
        source_type: Optional[Union[str, FoundryModelSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                source_type: Optional[Union[str, FoundryModelSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelVersion(_Model):
        artifact_profile: Optional[ArtifactProfile]
        base_model: Optional[str]
        blob_uri: str
        description: Optional[str]
        id: Optional[str]
        lora_config: Optional[LoraConfig]
        name: str
        source: Optional[ModelSourceData]
        tags: Optional[dict[str, str]]
        version: str
        warnings: Optional[list[FoundryModelWarning]]
        weight_type: Optional[Union[str, FoundryModelWeightType]]

        @overload
        def __init__(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                blob_uri: str, 
                description: Optional[str] = ..., 
                lora_config: Optional[LoraConfig] = ..., 
                source: Optional[ModelSourceData] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                weight_type: Optional[Union[str, FoundryModelWeightType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MonthlyRecurrenceSchedule(RecurrenceSchedule, discriminator='Monthly'):
        days_of_month: list[int]
        type: Literal[RecurrenceType.MONTHLY]

        @overload
        def __init__(
                self, 
                *, 
                days_of_month: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.NamespaceToolParam(Tool, discriminator='namespace'):
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[ToolType.NAMESPACE]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                tools: list[Union[FunctionToolParam, CustomToolParam]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.NoAuthenticationCredentials(BaseCredentials, discriminator='None'):
        type: Literal[CredentialType.NONE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OmitPropertiesRealtimeResponse(_Model):
        conversation_id: Optional[str]
        id: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        object: Optional[Literal["response"]]
        output_modalities: Optional[list[Literal["text", "audio"]]]
        status: Optional[Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]]
        status_details: Optional[RealtimeResponseStatusDetails]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                object: Optional[Literal[response]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OmitPropertiesRealtimeResponse1(_Model):
        conversation_id: Optional[str]
        id: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[Metadata]
        object: Optional[Literal["response"]]
        output_modalities: Optional[list[Literal["text", "audio"]]]
        status: Optional[Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]]
        status_details: Optional[RealtimeResponseStatusDetails]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                object: Optional[Literal[response]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OneTimeTrigger(Trigger, discriminator='OneTime'):
        time_zone: Optional[str]
        trigger_at: datetime
        type: Literal[TriggerType.ONE_TIME]

        @overload
        def __init__(
                self, 
                *, 
                time_zone: Optional[str] = ..., 
                trigger_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAnonymousAuthDetails(OpenApiAuthDetails, discriminator='anonymous'):
        type: Literal[OpenApiAuthType.ANONYMOUS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAuthDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "anonymous"
        MANAGED_IDENTITY = "managed_identity"
        PROJECT_CONNECTION = "project_connection"


    class azure.ai.projects.models.OpenApiFunctionDefinition(_Model):
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


    class azure.ai.projects.models.OpenApiFunctionDefinitionFunction(_Model):
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


    class azure.ai.projects.models.OpenApiManagedAuthDetails(OpenApiAuthDetails, discriminator='managed_identity'):
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


    class azure.ai.projects.models.OpenApiManagedSecurityScheme(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiProjectConnectionAuthDetails(OpenApiAuthDetails, discriminator='project_connection'):
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


    class azure.ai.projects.models.OpenApiProjectConnectionSecurityScheme(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiTool(Tool, discriminator='openapi'):
        openapi: OpenApiFunctionDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                openapi: OpenApiFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiToolboxTool(ToolboxTool, discriminator='openapi'):
        description: str
        name: str
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                openapi: OpenApiFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.projects.models.OptimizedAgentIdentifier(_Model):
        agent_name: str
        agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OtlpTelemetryEndpoint(TelemetryEndpoint, discriminator='OTLP'):
        auth: TelemetryEndpointAuth
        data: Union[list[str, TelemetryDataKind]]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: Union[str, TelemetryTransportProtocol]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[TelemetryEndpointAuth] = ..., 
                data: list[Union[str, TelemetryDataKind]], 
                endpoint: str, 
                protocol: Union[str, TelemetryTransportProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PageOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.ai.projects.models.PendingUploadRequest(_Model):
        connection_name: Optional[str]
        pending_upload_id: Optional[str]
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PendingUploadResponse(_Model):
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference, 
                pending_upload_id: str, 
                pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PendingUploadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_REFERENCE = "BlobReference"
        NONE = "None"
        TEMPORARY_BLOB_REFERENCE = "TemporaryBlobReference"


    class azure.ai.projects.models.PickPropertiesVoiceAudioConfig(_Model):
        output: Optional[VoiceAudioOutputConfig]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceAudioOutputConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProceduralMemoryItem(MemoryItem, discriminator='procedural'):
        content: str
        kind: Literal[MemoryItemKind.PROCEDURAL]
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


    class azure.ai.projects.models.ProgrammaticToolCallingParam(Tool, discriminator='programmatic_tool_calling'):
        type: Literal[ToolType.PROGRAMMATIC_TOOL_CALLING]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromotionInfo(_Model):
        agent_name: str
        agent_version: str
        promoted_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: str, 
                promoted_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptAgentDefinition(AgentDefinition, discriminator='prompt'):
        instructions: Optional[str]
        kind: Literal[AgentKind.PROMPT]
        model: str
        rai_config: RaiConfig
        reasoning: Optional[Reasoning]
        structured_inputs: Optional[dict[str, StructuredInputDefinition]]
        temperature: Optional[float]
        text: Optional[PromptAgentDefinitionTextOptions]
        tool_choice: Optional[Union[str, ToolChoiceParam]]
        tools: Optional[list[Tool]]
        top_p: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                model: str, 
                rai_config: Optional[RaiConfig] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                structured_inputs: Optional[dict[str, StructuredInputDefinition]] = ..., 
                temperature: Optional[float] = ..., 
                text: Optional[PromptAgentDefinitionTextOptions] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_p: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptAgentDefinitionTextOptions(_Model):
        format: Optional[TextResponseFormat]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[TextResponseFormat] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='prompt'):
        data_schema: dict[str, any]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        prompt_text: str
        type: Literal[EvaluatorDefinitionType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                prompt_text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptDataGenerationJobSource(DataGenerationJobSource, discriminator='prompt'):
        description: str
        prompt: str
        type: Literal[DataGenerationJobSourceType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                prompt: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='prompt'):
        description: Optional[str]
        prompt: str
        type: Literal[EvaluatorGenerationJobSourceType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                prompt: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProtocolConfiguration(_Model):
        a2a: Optional[A2AProtocolConfiguration]
        activity: Optional[ActivityProtocolConfiguration]
        invocations: Optional[InvocationsProtocolConfiguration]
        invocations_ws: Optional[InvocationsWsProtocolConfiguration]
        mcp: Optional[McpProtocolConfiguration]
        responses: Optional[ResponsesProtocolConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                a2a: Optional[A2AProtocolConfiguration] = ..., 
                activity: Optional[ActivityProtocolConfiguration] = ..., 
                invocations: Optional[InvocationsProtocolConfiguration] = ..., 
                invocations_ws: Optional[InvocationsWsProtocolConfiguration] = ..., 
                mcp: Optional[McpProtocolConfiguration] = ..., 
                responses: Optional[ResponsesProtocolConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProtocolVersionRecord(_Model):
        protocol: Union[str, AgentEndpointProtocol]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                protocol: Union[str, AgentEndpointProtocol], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RaiConfig(_Model):
        rai_policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                rai_policy_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RankerVersionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        DEFAULT_2024_11_15 = "default-2024-11-15"


    class azure.ai.projects.models.RankingOptions(_Model):
        hybrid_search: Optional[HybridSearchOptions]
        ranker: Optional[Union[str, RankerVersionType]]
        score_threshold: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_search: Optional[HybridSearchOptions] = ..., 
                ranker: Optional[Union[str, RankerVersionType]] = ..., 
                score_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormats(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcm(RealtimeAudioFormats, discriminator='audio/pcm'):
        rate: Optional[Literal[24000]]
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCM]

        @overload
        def __init__(
                self, 
                *, 
                rate: Optional[Literal[24000]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcma(RealtimeAudioFormats, discriminator='audio/pcma'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcmu(RealtimeAudioFormats, discriminator='audio/pcmu'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMU]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO_PCM = "audio/pcm"
        AUDIO_PCMA = "audio/pcma"
        AUDIO_PCMU = "audio/pcmu"


    class azure.ai.projects.models.RealtimeClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATE = "conversation.item.create"
        CONVERSATION_ITEM_DELETE = "conversation.item.delete"
        CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
        CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
        INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
        INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
        INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
        OUTPUT_AUDIO_BUFFER_CLEAR = "output_audio_buffer.clear"
        RESPONSE_CANCEL = "response.cancel"
        RESPONSE_CREATE = "response.create"
        SESSION_UPDATE = "session.update"


    class azure.ai.projects.models.RealtimeConversationItem(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemFunctionCall(RealtimeConversationItem, discriminator='function_call'):
        arguments: str
        call_id: Optional[str]
        id: Optional[str]
        name: str
        object: Optional[Literal["item"]]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemFunctionCallOutput(RealtimeConversationItem, discriminator='function_call_output'):
        call_id: str
        id: Optional[str]
        object: Optional[Literal["item"]]
        output: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str, 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessage(_Model):
        role: str

        @overload
        def __init__(
                self, 
                *, 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageAssistant(RealtimeConversationItemMessage, discriminator='assistant'):
        content: list[RealtimeConversationItemMessageAssistantContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageAssistantContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageAssistantContent(_Model):
        audio: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["output_text", "output_audio"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[output_text, output_audio]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageSystem(RealtimeConversationItemMessage, discriminator='system'):
        content: list[RealtimeConversationItemMessageSystemContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageSystemContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageSystemContent(_Model):
        text: Optional[str]
        type: Optional[Literal["input_text"]]

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[str] = ..., 
                type: Optional[Literal[input_text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.projects.models.RealtimeConversationItemMessageUser(RealtimeConversationItemMessage, discriminator='user'):
        content: list[RealtimeConversationItemMessageUserContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageUserContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageUserContent(_Model):
        audio: Optional[str]
        detail: Optional[Literal["auto", "low", "high"]]
        image_url: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["input_text", "input_audio", "input_image"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                detail: Optional[Literal[auto, low, high]] = ..., 
                image_url: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[input_text, input_audio, input_image]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"


    class azure.ai.projects.models.RealtimeFunctionTool(_Model):
        description: Optional[str]
        name: Optional[str]
        parameters: Optional[RealtimeFunctionToolParameters]
        type: Optional[Literal["function"]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[RealtimeFunctionToolParameters] = ..., 
                type: Optional[Literal[function]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeFunctionToolParameters(_Model):


    class azure.ai.projects.models.RealtimeMCPApprovalRequest(RealtimeConversationItem, discriminator='mcp_approval_request'):
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]

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


    class azure.ai.projects.models.RealtimeMCPApprovalResponse(RealtimeConversationItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: str
        reason: Optional[str]
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]

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


    class azure.ai.projects.models.RealtimeMCPError(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPHTTPError(RealtimeMCPError, discriminator='http_error'):
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.HTTP_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                code: int, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPListTools(RealtimeConversationItem, discriminator='mcp_list_tools'):
        id: Optional[str]
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPProtocolError(RealtimeMCPError, discriminator='protocol_error'):
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                code: int, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPToolCall(RealtimeConversationItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[RealtimeMCPError]
        id: str
        name: str
        output: Optional[str]
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[RealtimeMCPError] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPToolExecutionError(RealtimeMCPError, discriminator='tool_execution_error'):
        message: str
        type: Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMcpErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP_ERROR = "http_error"
        PROTOCOL_ERROR = "protocol_error"
        TOOL_EXECUTION_ERROR = "tool_execution_error"


    class azure.ai.projects.models.RealtimeReasoning(_Model):
        effort: Optional[Union[str, RealtimeReasoningEffort]]

        @overload
        def __init__(
                self, 
                *, 
                effort: Optional[Union[str, RealtimeReasoningEffort]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        XHIGH = "xhigh"


    class azure.ai.projects.models.RealtimeResponseStatusDetails(_Model):
        error: Optional[RealtimeResponseStatusDetailsError]
        reason: Optional[Literal["turn_detected", "client_cancelled", "max_output_tokens", "content_filter"]]
        type: Optional[Literal["completed", "cancelled", "failed", "incomplete"]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[RealtimeResponseStatusDetailsError] = ..., 
                reason: Optional[Literal[turn_detected, client_cancelled, max_output_tokens, content_filter]] = ..., 
                type: Optional[Literal[completed, cancelled, failed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeResponseStatusDetailsError(_Model):
        code: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeResponseUsage(_Model):
        input_token_details: Optional[RealtimeResponseUsageInputTokenDetails]
        input_tokens: Optional[int]
        output_token_details: Optional[RealtimeResponseUsageOutputTokenDetails]
        output_tokens: Optional[int]
        total_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                input_token_details: Optional[RealtimeResponseUsageInputTokenDetails] = ..., 
                input_tokens: Optional[int] = ..., 
                output_token_details: Optional[RealtimeResponseUsageOutputTokenDetails] = ..., 
                output_tokens: Optional[int] = ..., 
                total_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeResponseUsageInputTokenDetails(_Model):
        audio_tokens: Optional[int]
        cached_tokens: Optional[int]
        cached_tokens_details: Optional[RealtimeResponseUsageInputTokenDetailsCachedTokensDetails]
        image_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                cached_tokens: Optional[int] = ..., 
                cached_tokens_details: Optional[RealtimeResponseUsageInputTokenDetailsCachedTokensDetails] = ..., 
                image_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeResponseUsageInputTokenDetailsCachedTokensDetails(_Model):
        audio_tokens: Optional[int]
        image_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                image_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeResponseUsageOutputTokenDetails(_Model):
        audio_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEvent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionFailedError(_Model):
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


    class azure.ai.projects.models.RealtimeServerEventError(_Model):
        error: RealtimeServerEventErrorError
        event_id: str
        type: Literal["error"]

        @overload
        def __init__(
                self, 
                *, 
                error: RealtimeServerEventErrorError, 
                event_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventErrorError(_Model):
        code: Optional[str]
        event_id: Optional[str]
        message: str
        param: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventRateLimitsUpdatedRateLimits(_Model):
        limit: Optional[int]
        name: Optional[Literal["requests", "tokens"]]
        remaining: Optional[int]
        reset_seconds: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                name: Optional[Literal[requests, tokens]] = ..., 
                remaining: Optional[int] = ..., 
                reset_seconds: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartAdded(RealtimeServerEvent, discriminator='response.content_part.added'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                part: RealtimeServerEventResponseContentPartAddedPart, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartAddedPart(_Model):
        audio: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["audio", "text"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[audio, text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_CREATED = "conversation.created"
        CONVERSATION_ITEM_ADDED = "conversation.item.added"
        CONVERSATION_ITEM_CREATED = "conversation.item.created"
        CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
        CONVERSATION_ITEM_DONE = "conversation.item.done"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT = "conversation.item.input_audio_transcription.segment"
        CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
        CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
        ERROR = "error"
        INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
        INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
        INPUT_AUDIO_BUFFER_DTMF_EVENT_RECEIVED = "input_audio_buffer.dtmf_event_received"
        INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
        INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
        INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED = "input_audio_buffer.timeout_triggered"
        MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
        MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
        MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
        OUTPUT_AUDIO_BUFFER_CLEARED = "output_audio_buffer.cleared"
        OUTPUT_AUDIO_BUFFER_STARTED = "output_audio_buffer.started"
        OUTPUT_AUDIO_BUFFER_STOPPED = "output_audio_buffer.stopped"
        RATE_LIMITS_UPDATED = "rate_limits.updated"
        RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
        RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
        RESPONSE_CREATED = "response.created"
        RESPONSE_DONE = "response.done"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
        RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
        RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
        RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
        RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
        RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
        RESPONSE_OUTPUT_AUDIO_DELTA = "response.output_audio.delta"
        RESPONSE_OUTPUT_AUDIO_DONE = "response.output_audio.done"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA = "response.output_audio_transcript.delta"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE = "response.output_audio_transcript.done"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        SESSION_CREATED = "session.created"
        SESSION_UPDATED = "session.updated"


    class azure.ai.projects.models.Reasoning(_Model):
        context: Optional[Literal["auto", "current_turn", "all_turns"]]
        effort: Optional[Union[str, ReasoningEffort]]
        generate_summary: Optional[Literal["auto", "concise", "detailed"]]
        mode: Optional[Union[str, ReasoningModeEnum]]
        summary: Optional[Literal["auto", "concise", "detailed"]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[Literal[auto, current_turn, all_turns]] = ..., 
                effort: Optional[Union[str, ReasoningEffort]] = ..., 
                generate_summary: Optional[Literal[auto, concise, detailed]] = ..., 
                mode: Optional[Union[str, ReasoningModeEnum]] = ..., 
                summary: Optional[Literal[auto, concise, detailed]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MAX = "max"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        NONE = "none"
        XHIGH = "xhigh"


    class azure.ai.projects.models.ReasoningModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRO = "pro"
        STANDARD = "standard"


    class azure.ai.projects.models.RecurrenceSchedule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RecurrenceTrigger(Trigger, discriminator='Recurrence'):
        end_time: Optional[datetime]
        interval: int
        schedule: RecurrenceSchedule
        start_time: Optional[datetime]
        time_zone: Optional[str]
        type: Literal[TriggerType.RECURRENCE]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                interval: int, 
                schedule: RecurrenceSchedule, 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.ai.projects.models.RedTeam(_Model):
        application_scenario: Optional[str]
        attack_strategies: Optional[list[Union[str, AttackStrategy]]]
        display_name: Optional[str]
        name: str
        num_turns: Optional[int]
        properties: Optional[dict[str, str]]
        risk_categories: Optional[list[Union[str, RiskCategory]]]
        simulation_only: Optional[bool]
        status: Optional[str]
        tags: Optional[dict[str, str]]
        target: RedTeamTargetConfig

        @overload
        def __init__(
                self, 
                *, 
                application_scenario: Optional[str] = ..., 
                attack_strategies: Optional[list[Union[str, AttackStrategy]]] = ..., 
                display_name: Optional[str] = ..., 
                num_turns: Optional[int] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                risk_categories: Optional[list[Union[str, RiskCategory]]] = ..., 
                simulation_only: Optional[bool] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target: RedTeamTargetConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RedTeamEvalRunDataSource(TypedDict, total=False):
        key "item_generation_params": Required[Any]
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_red_team"]]


    class azure.ai.projects.models.RedTeamTargetConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ReminderPreviewToolboxTool(ToolboxTool, discriminator='reminder_preview'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.REMINDER_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponseRetrievalItemGenerationParams(TypedDict, total=False):
        key "data_mapping": Required[Dict[str, str]]
        key "max_num_turns": int
        key "source": Required[Union[SourceFileContent, SourceFileID]]
        key "type": Required[Literal["response_retrieval"]]


    class azure.ai.projects.models.ResponseUsageInputTokensDetails(_Model):
        cache_write_tokens: int
        cached_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                cache_write_tokens: int, 
                cached_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponseUsageOutputTokensDetails(_Model):
        reasoning_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                reasoning_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponsesProtocolConfiguration(_Model):


    class azure.ai.projects.models.RiskCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_VULNERABILITY = "CodeVulnerability"
        HATE_UNFAIRNESS = "HateUnfairness"
        PROHIBITED_ACTIONS = "ProhibitedActions"
        PROTECTED_MATERIAL = "ProtectedMaterial"
        SELF_HARM = "SelfHarm"
        SENSITIVE_DATA_LEAKAGE = "SensitiveDataLeakage"
        SEXUAL = "Sexual"
        TASK_ADHERENCE = "TaskAdherence"
        UNGROUNDED_ATTRIBUTES = "UngroundedAttributes"
        VIOLENCE = "Violence"


    class azure.ai.projects.models.Routine(_Model):
        action: Optional[RoutineAction]
        created_at: Optional[datetime]
        description: Optional[str]
        enabled: bool
        name: Optional[str]
        triggers: Optional[dict[str, RoutineTrigger]]
        updated_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[RoutineAction] = ..., 
                created_at: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                enabled: bool, 
                name: Optional[str] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                updated_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.models.RoutineAttemptSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_FIRE = "event_fire"
        MANUAL_DISPATCH = "manual_dispatch"
        QUEUED_DISPATCH = "queued_dispatch"
        SCHEDULE_DELIVERY = "schedule_delivery"
        TIMER_DELIVERY = "timer_delivery"


    class azure.ai.projects.models.RoutineDispatchPayload(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineDispatchPayloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.models.RoutineRun(_Model):
        action_correlation_id: Optional[str]
        action_type: Optional[Union[str, RoutineActionType]]
        agent_endpoint_id: Optional[str]
        agent_id: Optional[str]
        attempt_source: Optional[Union[str, RoutineAttemptSource]]
        conversation_id: Optional[str]
        dispatch_id: Optional[str]
        ended_at: Optional[datetime]
        error_message: Optional[str]
        error_status_code: Optional[int]
        error_type: Optional[str]
        id: str
        phase: Optional[Union[str, RoutineRunPhase]]
        response_id: Optional[str]
        scheduled_fire_at: Optional[datetime]
        session_id: Optional[str]
        started_at: Optional[datetime]
        status: Optional[RoutineRunStatus]
        task_id: Optional[str]
        trigger_event_payload: Optional[dict[str, Any]]
        trigger_name: Optional[str]
        trigger_type: Optional[Union[str, RoutineTriggerType]]
        triggered_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action_correlation_id: Optional[str] = ..., 
                action_type: Optional[Union[str, RoutineActionType]] = ..., 
                agent_endpoint_id: Optional[str] = ..., 
                agent_id: Optional[str] = ..., 
                attempt_source: Optional[Union[str, RoutineAttemptSource]] = ..., 
                conversation_id: Optional[str] = ..., 
                dispatch_id: Optional[str] = ..., 
                ended_at: Optional[datetime] = ..., 
                error_message: Optional[str] = ..., 
                error_status_code: Optional[int] = ..., 
                error_type: Optional[str] = ..., 
                phase: Optional[Union[str, RoutineRunPhase]] = ..., 
                response_id: Optional[str] = ..., 
                scheduled_fire_at: Optional[datetime] = ..., 
                session_id: Optional[str] = ..., 
                started_at: Optional[datetime] = ..., 
                status: Optional[RoutineRunStatus] = ..., 
                task_id: Optional[str] = ..., 
                trigger_event_payload: Optional[dict[str, Any]] = ..., 
                trigger_name: Optional[str] = ..., 
                trigger_type: Optional[Union[str, RoutineTriggerType]] = ..., 
                triggered_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineRunPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        DISPATCHING = "dispatching"
        FAILED = "failed"
        QUEUED = "queued"


    class azure.ai.projects.models.RoutineTrigger(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        GITHUB_ISSUE = "github_issue"
        SCHEDULE = "schedule"
        TIMER = "timer"


    class azure.ai.projects.models.RubricBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='rubric'):
        data_schema: dict[str, any]
        dimensions: list[Dimension]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        pass_threshold: Optional[float]
        type: Literal[EvaluatorDefinitionType.RUBRIC]

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                dimensions: list[Dimension], 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                pass_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RubricGenerationInputQualityWarning(_Model):
        code: Union[str, RubricGenerationInputQualityWarningCode]
        message: str
        severity: Union[str, RubricGenerationInputQualityWarningSeverity]
        source: Union[str, RubricGenerationInputQualityWarningSource]
        source_index: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, RubricGenerationInputQualityWarningCode], 
                message: str, 
                severity: Union[str, RubricGenerationInputQualityWarningSeverity], 
                source: Union[str, RubricGenerationInputQualityWarningSource], 
                source_index: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RubricGenerationInputQualityWarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMPTY_AGENT_INSTRUCTIONS = "empty_agent_instructions"
        EMPTY_DATASET_CONTENT = "empty_dataset_content"
        EMPTY_PROMPT = "empty_prompt"
        INSUFFICIENT_TOTAL_INPUT = "insufficient_total_input"
        LOW_TRACE_COUNT = "low_trace_count"
        SHORT_AGENT_INSTRUCTIONS = "short_agent_instructions"
        SHORT_DATASET_CONTENT = "short_dataset_content"
        SHORT_PROMPT = "short_prompt"


    class azure.ai.projects.models.RubricGenerationInputQualityWarningSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WARNING = "warning"


    class azure.ai.projects.models.RubricGenerationInputQualityWarningSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        AGGREGATE = "aggregate"
        DATASET = "dataset"
        PROMPT = "prompt"


    class azure.ai.projects.models.SASCredentials(BaseCredentials, discriminator='SAS'):
        sas_token: Optional[str]
        type: Literal[CredentialType.SAS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SampleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION_RESULT_SAMPLE = "EvaluationResultSample"


    class azure.ai.projects.models.Schedule(_Model):
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        properties: Optional[dict[str, str]]
        provisioning_status: Optional[Union[str, ScheduleProvisioningStatus]]
        schedule_id: str
        system_data: dict[str, str]
        tags: Optional[dict[str, str]]
        task: ScheduleTask
        trigger: Trigger

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: bool, 
                properties: Optional[dict[str, str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                task: ScheduleTask, 
                trigger: Trigger
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.ai.projects.models.ScheduleRoutineTrigger(RoutineTrigger, discriminator='schedule'):
        cron_expression: str
        time_zone: str
        type: Literal[RoutineTriggerType.SCHEDULE]

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: str, 
                time_zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleRun(_Model):
        error: Optional[str]
        properties: dict[str, str]
        run_id: str
        schedule_id: str
        success: bool
        trigger_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                schedule_id: str, 
                trigger_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleTask(_Model):
        configuration: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleTaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION = "Evaluation"
        INSIGHT = "Insight"


    class azure.ai.projects.models.SearchContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        TEXT = "text"


    class azure.ai.projects.models.SearchContextSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.projects.models.SessionDirectoryEntry(_Model):
        is_directory: bool
        modified_time: datetime
        name: str
        size: int

        @overload
        def __init__(
                self, 
                *, 
                is_directory: bool, 
                modified_time: datetime, 
                name: str, 
                size: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionFileWriteResult(_Model):
        bytes_written: int
        path: str

        @overload
        def __init__(
                self, 
                *, 
                bytes_written: int, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionLogEvent(_Model):
        data: str
        event: Union[str, SessionLogEventType]

        @overload
        def __init__(
                self, 
                *, 
                data: str, 
                event: Union[str, SessionLogEventType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionLogEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG = "log"


    class azure.ai.projects.models.SharepointGroundingToolParameters(_Model):
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SharepointPreviewTool(Tool, discriminator='sharepoint_grounding_preview'):
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                sharepoint_grounding_preview: SharepointGroundingToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SimpleQnADataGenerationJobOptions(DataGenerationJobOptions, discriminator='simple_qna'):
        max_samples: int
        model_options: DataGenerationModelOptions
        question_types: Optional[list[Union[str, SimpleQnAFineTuningQuestionType]]]
        train_split: float
        type: Literal[DataGenerationJobType.SIMPLE_QNA]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                question_types: Optional[list[Union[str, SimpleQnAFineTuningQuestionType]]] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SimpleQnAFineTuningQuestionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LONG_ANSWER = "long_answer"
        SHORT_ANSWER = "short_answer"


    class azure.ai.projects.models.SkillDetails(_Model):
        created_at: datetime
        default_version: str
        description: str
        id: str
        latest_version: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                default_version: str, 
                description: str, 
                id: str, 
                latest_version: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillInlineContent(_Model):
        allowed_tools: Optional[list[str]]
        compatibility: Optional[str]
        description: str
        instructions: str
        license: Optional[str]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[list[str]] = ..., 
                compatibility: Optional[str] = ..., 
                description: str, 
                instructions: str, 
                license: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillReferenceParam(ContainerSkill, discriminator='skill_reference'):
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


    class azure.ai.projects.models.SkillVersion(_Model):
        created_at: datetime
        description: str
        id: str
        name: str
        skill_id: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                description: str, 
                id: str, 
                name: str, 
                skill_id: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificApplyPatchParam(ToolChoiceParam, discriminator='apply_patch'):
        type: Literal[ToolChoiceParamType.APPLY_PATCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificFunctionShellParam(ToolChoiceParam, discriminator='shell'):
        type: Literal[ToolChoiceParamType.SHELL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificProgrammaticToolCallingParam(ToolChoiceParam, discriminator='programmatic_tool_calling'):
        type: Literal[ToolChoiceParamType.PROGRAMMATIC_TOOL_CALLING]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.StructuredInputDefinition(_Model):
        default_value: Optional[Any]
        description: Optional[str]
        required: Optional[bool]
        schema: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[Any] = ..., 
                description: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                schema: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.StructuredOutputDefinition(_Model):
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


    class azure.ai.projects.models.TargetCompletionEvalRunDataSource(TypedDict, total=False):
        key "input_messages": Required[InputMessagesItemReference]
        key "source": Required[Union[SourceFileContent, SourceFileID]]
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_target_completions"]]


    class azure.ai.projects.models.TaskGenerationDataGenerationJobOptions(DataGenerationJobOptions, discriminator='task_generation'):
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TASK_GENERATION]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TaxonomyCategory(_Model):
        description: Optional[str]
        id: str
        name: str
        properties: Optional[dict[str, str]]
        risk_category: Union[str, RiskCategory]
        sub_categories: list[TaxonomySubCategory]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: str, 
                name: str, 
                properties: Optional[dict[str, str]] = ..., 
                risk_category: Union[str, RiskCategory], 
                sub_categories: list[TaxonomySubCategory]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TaxonomySubCategory(_Model):
        description: Optional[str]
        enabled: bool
        id: str
        name: str
        properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled: bool, 
                id: str, 
                name: str, 
                properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryConfig(_Model):
        endpoints: list[TelemetryEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: list[TelemetryEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryDataKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_OTEL = "ContainerOtel"
        CONTAINER_STDOUT_STDERR = "ContainerStdoutStderr"
        METRICS = "Metrics"


    class azure.ai.projects.models.TelemetryEndpoint(_Model):
        auth: Optional[TelemetryEndpointAuth]
        data: list[Union[str, TelemetryDataKind]]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[TelemetryEndpointAuth] = ..., 
                data: list[Union[str, TelemetryDataKind]], 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryEndpointAuth(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryEndpointAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEADER = "header"


    class azure.ai.projects.models.TelemetryEndpointKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTLP = "OTLP"


    class azure.ai.projects.models.TelemetryTransportProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRPC = "Grpc"
        HTTP = "Http"


    class azure.ai.projects.models.TemplateVoiceGreetingConfig(VoiceGreetingConfig, discriminator='template'):
        text: str
        type: Literal["template"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TestingCriterionAzureAIEvaluator(TypedDict, total=False):
        key "data_mapping": Dict[str, str]
        key "evaluator_name": Required[str]
        key "evaluator_version": str
        key "initialization_parameters": Dict[str, Any]
        key "name": Required[str]
        key "type": Required[Literal["azure_ai_evaluator"]]


    class azure.ai.projects.models.TextResponseFormat(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "json_object"
        JSON_SCHEMA = "json_schema"
        TEXT = "text"


    class azure.ai.projects.models.TextResponseFormatJsonObject(TextResponseFormat, discriminator='json_object'):
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatJsonSchema(TextResponseFormat, discriminator='json_schema'):
        description: Optional[str]
        name: str
        schema: dict[str, Any]
        strict: Optional[bool]
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                schema: dict[str, Any], 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatText(TextResponseFormat, discriminator='text'):
        type: Literal[TextResponseFormatConfigurationType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TimerRoutineTrigger(RoutineTrigger, discriminator='timer'):
        at: Optional[datetime]
        type: Literal[RoutineTriggerType.TIMER]

        @overload
        def __init__(
                self, 
                *, 
                at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Tool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceAllowed(ToolChoiceParam, discriminator='allowed_tools'):
        mode: Literal["auto", "required"]
        tools: list[dict[str, Any]]
        type: Literal[ToolChoiceParamType.ALLOWED_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                mode: Literal["auto", "required"], 
                tools: list[dict[str, Any]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceCodeInterpreter(ToolChoiceParam, discriminator='code_interpreter'):
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputer(ToolChoiceParam, discriminator='computer'):
        type: Literal[ToolChoiceParamType.COMPUTER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputerUse(ToolChoiceParam, discriminator='computer_use'):
        type: Literal[ToolChoiceParamType.COMPUTER_USE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputerUsePreview(ToolChoiceParam, discriminator='computer_use_preview'):
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceCustom(ToolChoiceParam, discriminator='custom'):
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


    class azure.ai.projects.models.ToolChoiceFileSearch(ToolChoiceParam, discriminator='file_search'):
        type: Literal[ToolChoiceParamType.FILE_SEARCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceFunction(ToolChoiceParam, discriminator='function'):
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


    class azure.ai.projects.models.ToolChoiceImageGeneration(ToolChoiceParam, discriminator='image_generation'):
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceMCP(ToolChoiceParam, discriminator='mcp'):
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


    class azure.ai.projects.models.ToolChoiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.projects.models.ToolChoiceParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_TOOLS = "allowed_tools"
        APPLY_PATCH = "apply_patch"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE = "computer_use"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        MCP = "mcp"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHELL = "shell"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WEB_SEARCH_PREVIEW_2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.projects.models.ToolChoiceWebSearchPreview(ToolChoiceParam, discriminator='web_search_preview'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceWebSearchPreview20250311(ToolChoiceParam, discriminator='web_search_preview_2025_03_11'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW_2025_03_11]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolConfig(_Model):
        additional_search_text: Optional[str]
        pin: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                additional_search_text: Optional[str] = ..., 
                pin: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolDescription(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolDescriptionParam(TypedDict, total=False):
        key "description": str
        key "name": str


    class azure.ai.projects.models.ToolProjectConnection(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolSearchExecutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = "client"
        SERVER = "server"


    class azure.ai.projects.models.ToolSearchToolParam(Tool, discriminator='tool_search'):
        description: Optional[str]
        execution: Optional[Union[str, ToolSearchExecutionType]]
        parameters: Optional[EmptyModelParam]
        type: Literal[ToolType.TOOL_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                execution: Optional[Union[str, ToolSearchExecutionType]] = ..., 
                parameters: Optional[EmptyModelParam] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolSearchToolboxTool(ToolboxTool, discriminator='toolbox_search'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        APPLY_PATCH = "apply_patch"
        AZURE_AI_SEARCH = "azure_ai_search"
        AZURE_FUNCTION = "azure_function"
        BING_CUSTOM_SEARCH_PREVIEW = "bing_custom_search_preview"
        BING_GROUNDING = "bing_grounding"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CAPTURE_STRUCTURED_OUTPUTS = "capture_structured_outputs"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FABRIC_DATAAGENT_PREVIEW = "fabric_dataagent_preview"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        LOCAL_SHELL = "local_shell"
        MCP = "mcp"
        MEMORY_SEARCH_PREVIEW = "memory_search_preview"
        NAMESPACE = "namespace"
        OPENAPI = "openapi"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.models.ToolUseFineTuningDataGenerationJobOptions(DataGenerationJobOptions, discriminator='tool_use'):
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TOOL_USE]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxObject(_Model):
        default_version: str
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                default_version: str, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxPolicies(_Model):
        rai_config: Optional[RaiConfig]

        @overload
        def __init__(
                self, 
                *, 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSearchPreviewToolboxTool(ToolboxTool, discriminator='toolbox_search_preview'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSkill(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSkillReference(ToolboxSkill, discriminator='skill_reference'):
        name: str
        type: Literal["skill_reference"]
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


    class azure.ai.projects.models.ToolboxTool(_Model):
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        AZURE_AI_SEARCH = "azure_ai_search"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CODE_INTERPRETER = "code_interpreter"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        MCP = "mcp"
        OPENAPI = "openapi"
        REMINDER_PREVIEW = "reminder_preview"
        TOOLBOX_SEARCH = "toolbox_search"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        WEB_SEARCH = "web_search"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.models.ToolboxVersionObject(_Model):
        created_at: datetime
        description: Optional[str]
        id: str
        metadata: dict[str, str]
        name: str
        policies: Optional[ToolboxPolicies]
        skills: Optional[list[ToolboxSkill]]
        tools: list[ToolboxTool]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                description: Optional[str] = ..., 
                id: str, 
                metadata: dict[str, str], 
                name: str, 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[list[ToolboxSkill]] = ..., 
                tools: list[ToolboxTool], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesDataGenerationJobOptions(DataGenerationJobOptions, discriminator='traces'):
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesDataGenerationJobSource(DataGenerationJobSource, discriminator='traces'):
        agent_id: Optional[str]
        agent_name: Optional[str]
        agent_version: Optional[str]
        description: str
        end_time: Optional[datetime]
        start_time: datetime
        type: Literal[DataGenerationJobSourceType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='traces'):
        agent_id: Optional[str]
        agent_name: Optional[str]
        agent_version: Optional[str]
        description: Optional[str]
        end_time: Optional[datetime]
        start_time: datetime
        type: Literal[EvaluatorGenerationJobSourceType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesPreviewEvalRunDataSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "end_time": datetime
        key "ingestion_delay_seconds": int
        key "lookback_hours": int
        key "max_traces": int
        key "trace_ids": List[str]
        key "type": Required[Literal["azure_ai_traces_preview"]]


    class azure.ai.projects.models.TranscriptTextUsageDuration(CreateTranscriptionResponseJsonUsage, discriminator='duration'):
        seconds: timedelta
        type: Literal[CreateTranscriptionResponseJsonUsageType.DURATION]

        @overload
        def __init__(
                self, 
                *, 
                seconds: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TranscriptTextUsageTokens(CreateTranscriptionResponseJsonUsage, discriminator='tokens'):
        input_token_details: Optional[TranscriptTextUsageTokensInputTokenDetails]
        input_tokens: int
        output_tokens: int
        total_tokens: int
        type: Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]

        @overload
        def __init__(
                self, 
                *, 
                input_token_details: Optional[TranscriptTextUsageTokensInputTokenDetails] = ..., 
                input_tokens: int, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TranscriptTextUsageTokensInputTokenDetails(_Model):
        audio_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TreatmentEffectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGED = "Changed"
        DEGRADED = "Degraded"
        IMPROVED = "Improved"
        INCONCLUSIVE = "Inconclusive"
        TOO_FEW_SAMPLES = "TooFewSamples"


    class azure.ai.projects.models.Trigger(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRON = "Cron"
        ONE_TIME = "OneTime"
        RECURRENCE = "Recurrence"


    class azure.ai.projects.models.UpdateMemoriesLROPoller(LROPoller[MemoryStoreUpdateCompletedResult]):
        property superseded_by: Optional[str]    # Read-only
        property update_id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[MemoryStoreUpdateCompletedResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...


    class azure.ai.projects.models.UpdateModelVersionRequest(_Model):
        description: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UpdateToolboxRequest(_Model):
        default_version: str

        @overload
        def __init__(
                self, 
                *, 
                default_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UserProfileMemoryItem(MemoryItem, discriminator='user_profile'):
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


    class azure.ai.projects.models.VersionIndicator(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionIndicatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VERSION_REF = "version_ref"


    class azure.ai.projects.models.VersionRefIndicator(VersionIndicator, discriminator='version_ref'):
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionSelectionRule(_Model):
        agent_version: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionSelector(_Model):
        version_selection_rules: list[VersionSelectionRule]

        @overload
        def __init__(
                self, 
                *, 
                version_selection_rules: list[VersionSelectionRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionSelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.ai.projects.models.VoiceAgentAnimationConfig(_Model):
        model_name: Optional[str]
        outputs: Optional[list[Union[str, VoiceAgentAnimationOutputType]]]

        @overload
        def __init__(
                self, 
                *, 
                model_name: Optional[str] = ..., 
                outputs: Optional[list[Union[str, VoiceAgentAnimationOutputType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAnimationOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLENDSHAPES = "blendshapes"
        VISEME_ID = "viseme_id"


    class azure.ai.projects.models.VoiceAgentAvatarIceServer(_Model):
        credential: Optional[str]
        urls: list[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[str] = ..., 
                urls: list[str], 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarScene(_Model):
        amplitude: Optional[float]
        position_x: Optional[float]
        position_y: Optional[float]
        rotation_x: Optional[float]
        rotation_y: Optional[float]
        rotation_z: Optional[float]
        zoom: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                amplitude: Optional[float] = ..., 
                position_x: Optional[float] = ..., 
                position_y: Optional[float] = ..., 
                rotation_x: Optional[float] = ..., 
                rotation_y: Optional[float] = ..., 
                rotation_z: Optional[float] = ..., 
                zoom: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarVideoBackground(_Model):
        color: Optional[str]
        image_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                color: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarVideoCrop(_Model):
        bottom_right: list[int]
        top_left: list[int]

        @overload
        def __init__(
                self, 
                *, 
                bottom_right: list[int], 
                top_left: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarVideoParams(_Model):
        background: Optional[VoiceAgentAvatarVideoBackground]
        bitrate: Optional[int]
        codec: Optional[Literal["h264"]]
        crop: Optional[VoiceAgentAvatarVideoCrop]
        gop_size: Optional[int]
        resolution: Optional[VoiceAgentAvatarVideoResolution]

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[VoiceAgentAvatarVideoBackground] = ..., 
                bitrate: Optional[int] = ..., 
                codec: Optional[Literal[h264]] = ..., 
                crop: Optional[VoiceAgentAvatarVideoCrop] = ..., 
                gop_size: Optional[int] = ..., 
                resolution: Optional[VoiceAgentAvatarVideoResolution] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarVideoResolution(_Model):
        height: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                height: int, 
                width: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventConversationItemCreate(_Model):
        event_id: Optional[str]
        item: VoiceAgentCreateConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: VoiceAgentCreateConversationItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventConversationItemDelete(_Model):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventConversationItemRetrieve(_Model):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventConversationItemTruncate(_Model):
        audio_end_ms: int
        content_index: int
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventInputAudioBufferAppend(_Model):
        audio: str
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventInputAudioBufferClear(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventInputAudioBufferCommit(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventOutputAudioBufferClear(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventResponseCancel(_Model):
        event_id: Optional[str]
        response_id: Optional[str]
        type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventResponseCreate(_Model):
        event_id: Optional[str]
        response: Optional[VoiceAgentResponseCreateParams]
        type: Literal[RealtimeClientEventType.RESPONSE_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response: Optional[VoiceAgentResponseCreateParams] = ..., 
                type: Literal[RealtimeClientEventType.RESPONSE_CREATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventSessionAvatarConnect(_Model):
        client_sdp: str
        event_id: Optional[str]
        type: Literal["connect"]

        @overload
        def __init__(
                self, 
                *, 
                client_sdp: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventSessionUpdate(_Model):
        event_id: Optional[str]
        session: VoiceAgentSessionUpdateConfig
        type: Literal[RealtimeClientEventType.SESSION_UPDATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: VoiceAgentSessionUpdateConfig, 
                type: Literal[RealtimeClientEventType.SESSION_UPDATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentDefinition(AgentDefinition, discriminator='voice'):
        audio: Optional[VoiceAudioConfig]
        avatar: Optional[VoiceAvatarConfig]
        greeting: Optional[VoiceGreetingConfig]
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        kind: Literal[AgentKind.VOICE]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        model: str
        model_type: Union[str, VoiceModelType]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        rai_config: RaiConfig
        store: Optional[bool]
        structured_inputs: Optional[dict[str, StructuredInputDefinition]]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceAudioConfig] = ..., 
                avatar: Optional[VoiceAvatarConfig] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                model: str, 
                model_type: Union[str, VoiceModelType], 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                store: Optional[bool] = ..., 
                structured_inputs: Optional[dict[str, StructuredInputDefinition]] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentEchoCancellation(_Model):
        channels: Optional[int]
        reference_source: Optional[Union[str, VoiceAgentEchoCancellationReferenceSource]]
        type: Literal["server_echo_cancellation"]

        @overload
        def __init__(
                self, 
                *, 
                channels: Optional[int] = ..., 
                reference_source: Optional[Union[str, VoiceAgentEchoCancellationReferenceSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentEchoCancellationReferenceSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = "client"
        SERVER = "server"


    class azure.ai.projects.models.VoiceAgentFunctionTool(VoiceAgentTool, discriminator='function'):
        description: Optional[str]
        name: str
        parameters: Optional[RealtimeFunctionToolParameters]
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[RealtimeFunctionToolParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentInterimResponseConfig(_Model):
        latency_threshold_ms: Optional[int]
        triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentInterimResponseTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATENCY = "latency"
        TOOL = "tool"


    class azure.ai.projects.models.VoiceAgentLlmInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='llm_interim_response'):
        instructions: Optional[str]
        latency_threshold_ms: int
        max_completion_tokens: Optional[int]
        model: Optional[str]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["llm_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                latency_threshold_ms: Optional[int] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                model: Optional[str] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentMcpTool(VoiceAgentTool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        defer_loading: Optional[bool]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                defer_loading: Optional[bool] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentRealtimeResponse(OmitPropertiesRealtimeResponse1):
        audio: Optional[VoiceResponseAudio]
        conversation_id: str
        id: str
        max_output_tokens: Union[int, str]
        metadata: Metadata
        object: str
        output: Optional[list[VoiceAgentResponseItem]]
        output_modalities: Union[list[str, str]]
        status: Union[str, str, str, str, str]
        status_details: RealtimeResponseStatusDetails
        usage: RealtimeResponseUsage

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceResponseAudio] = ..., 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                object: Optional[Literal[response]] = ..., 
                output: Optional[list[VoiceAgentResponseItem]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentResponseCreateParams(_Model):
        audio: Optional[PickPropertiesVoiceAudioConfig]
        conversation: Optional[Union[Literal["auto"], Literal["none"], str]]
        input: Optional[list[RealtimeConversationItem]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[Metadata]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        pre_generated_assistant_message: Optional[RealtimeConversationItemMessageAssistant]
        reasoning: Optional[RealtimeReasoning]
        tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]]
        tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[PickPropertiesVoiceAudioConfig] = ..., 
                conversation: Optional[Union[Literal[auto], Literal[none], str]] = ..., 
                input: Optional[list[RealtimeConversationItem]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                pre_generated_assistant_message: Optional[RealtimeConversationItemMessageAssistant] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]] = ..., 
                tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentResponseEventContentPart(_Model):
        audio: Optional[str]
        format: Optional[VoiceAudioFormat]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["audio", "text"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[audio, text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSemanticVadTurnDetection(VoiceTurnDetection, discriminator='semantic_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        eagerness: Optional[Literal["low", "medium", "high", "auto"]]
        interrupt_response: Optional[bool]
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                eagerness: Optional[Literal[low, medium, high, auto]] = ..., 
                interrupt_response: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemAdded(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemCreated(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemDeleted(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemDone(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted(_Model):
        content_index: int
        event_id: str
        item_id: str
        logprobs: Optional[list[LogProbProperties]]
        phrases: Optional[list[VoiceAgentTranscriptionPhrase]]
        transcript: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]
        usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                logprobs: Optional[list[LogProbProperties]] = ..., 
                phrases: Optional[list[VoiceAgentTranscriptionPhrase]] = ..., 
                transcript: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED], 
                usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionDelta(_Model):
        content_index: Optional[int]
        delta: Optional[str]
        event_id: str
        item_id: str
        logprobs: Optional[list[LogProbProperties]]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: Optional[int] = ..., 
                delta: Optional[str] = ..., 
                event_id: str, 
                item_id: str, 
                logprobs: Optional[list[LogProbProperties]] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionFailed(_Model):
        content_index: int
        error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionSegment(_Model):
        content_index: int
        end: float
        event_id: str
        id: str
        item_id: str
        speaker: str
        start: float
        text: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                end: float, 
                event_id: str, 
                id: str, 
                item_id: str, 
                speaker: str, 
                start: float, 
                text: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemRetrieved(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventConversationItemTruncated(_Model):
        audio_end_ms: int
        content_index: int
        event_id: str
        item: Optional[RealtimeConversationItemMessageAssistant]
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: str, 
                item: Optional[RealtimeConversationItemMessageAssistant] = ..., 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventInputAudioBufferCleared(_Model):
        event_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventInputAudioBufferCommitted(_Model):
        event_id: str
        item_id: str
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventInputAudioBufferSpeechStarted(_Model):
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]

        @overload
        def __init__(
                self, 
                *, 
                audio_start_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventInputAudioBufferSpeechStopped(_Model):
        audio_end_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventInputAudioBufferTimeoutTriggered(_Model):
        audio_end_ms: int
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                audio_start_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventMcpListToolsCompleted(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventMcpListToolsFailed(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventMcpListToolsInProgress(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventOutputAudioBufferCleared(_Model):
        event_id: str
        response_id: str
        type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventRateLimitsUpdated(_Model):
        event_id: str
        rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
        type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits], 
                type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationBlendshapesDelta(_Model):
        content_index: int
        event_id: str
        frame_index: int
        frames: list[list[float]]
        item_id: str
        output_index: int
        response_id: str
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                frame_index: int, 
                frames: list[list[float]], 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationBlendshapesDone(_Model):
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationVisemeDelta(_Model):
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["delta"]
        viseme_id: int

        @overload
        def __init__(
                self, 
                *, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                viseme_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationVisemeDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioDelta(_Model):
        content_index: int
        delta: bytes
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: bytes, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTimestampDelta(_Model):
        audio_duration_ms: int
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal["word"]
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                audio_duration_ms: int, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTimestampDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTranscriptDelta(_Model):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTranscriptDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        transcript: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                transcript: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseContentPartDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: VoiceAgentResponseEventContentPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                part: VoiceAgentResponseEventContentPart, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseCreated(_Model):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse, 
                type: Literal[RealtimeServerEventType.RESPONSE_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseDone(_Model):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse, 
                type: Literal[RealtimeServerEventType.RESPONSE_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseFunctionCallArgumentsDelta(_Model):
        call_id: str
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseFunctionCallArgumentsDone(_Model):
        arguments: str
        call_id: str
        event_id: str
        item_id: str
        name: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                event_id: str, 
                item_id: str, 
                name: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseMcpCallArgumentsDelta(_Model):
        delta: str
        event_id: str
        item_id: str
        obfuscation: Optional[str]
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                obfuscation: Optional[str] = ..., 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseMcpCallArgumentsDone(_Model):
        arguments: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseMcpCallCompleted(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseMcpCallFailed(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseMcpCallInProgress(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseOutputItemAdded(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseOutputItemDone(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseTextDelta(_Model):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseTextDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseVideoDelta(_Model):
        codec: str
        delta: str
        event_id: str
        output_index: int
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                codec: str, 
                delta: str, 
                event_id: str, 
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarConnecting(_Model):
        event_id: str
        server_sdp: str
        type: Literal["connecting"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                server_sdp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarSwitchToIdle(_Model):
        event_id: str
        turn_id: Optional[str]
        type: Literal["switch_to_idle"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking(_Model):
        event_id: str
        turn_id: Optional[str]
        type: Literal["switch_to_speaking"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionCreated(_Model):
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig, 
                type: Literal[RealtimeServerEventType.SESSION_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionUpdated(_Model):
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig, 
                type: Literal[RealtimeServerEventType.SESSION_UPDATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventWarning(_Model):
        event_id: str
        type: Literal["warning"]
        warning: VoiceAgentServerEventWarningDetails

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                warning: VoiceAgentServerEventWarningDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventWarningDetails(_Model):
        code: Optional[str]
        message: str
        param: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionAvatarConfig(VoiceAvatarConfig):
        character: str
        customized: bool
        ice_servers: Optional[list[VoiceAgentAvatarIceServer]]
        model: str
        output_audit_audio: bool
        output_protocol: Union[str, VoiceAvatarOutputProtocol]
        scene: VoiceAgentAvatarScene
        style: str
        type: Union[str, VoiceAvatarType]
        video: VoiceAgentAvatarVideoParams

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: Optional[bool] = ..., 
                ice_servers: Optional[list[VoiceAgentAvatarIceServer]] = ..., 
                model: Optional[str] = ..., 
                output_audit_audio: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, VoiceAvatarOutputProtocol]] = ..., 
                scene: Optional[VoiceAgentAvatarScene] = ..., 
                style: Optional[str] = ..., 
                type: Union[str, VoiceAvatarType], 
                video: Optional[VoiceAgentAvatarVideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionIncludeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_SEARCH_CALL_RESULTS = "file_search_call.results"
        INPUT_AUDIO_TRANSCRIPTION_LOGPROBS = "item.input_audio_transcription.logprobs"
        INPUT_AUDIO_TRANSCRIPTION_PHRASES = "item.input_audio_transcription.phrases"


    class azure.ai.projects.models.VoiceAgentSessionResponseConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAudioConfig]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        expires_at: Optional[datetime]
        greeting: Optional[VoiceGreetingConfig]
        id: str
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        model: str
        object: Literal["session"]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]
        type: Literal["realtime"]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAudioConfig] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                expires_at: Optional[datetime] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                id: str, 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                model: str, 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionUpdateConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAudioConfig]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        greeting: Optional[VoiceGreetingConfig]
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]
        type: Literal["realtime"]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAudioConfig] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentStaticInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='static_interim_response'):
        latency_threshold_ms: int
        texts: Optional[list[str]]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["static_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                texts: Optional[list[str]] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentToolResponseScheduling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERRUPT = "interrupt"
        SILENT = "silent"
        SKIP_IF_BUSY = "skip_if_busy"
        WHEN_IDLE = "when_idle"


    class azure.ai.projects.models.VoiceAgentTranscriptionPhrase(_Model):
        confidence: Optional[float]
        duration_milliseconds: int
        locale: Optional[str]
        offset_milliseconds: int
        text: str
        words: Optional[list[VoiceAgentTranscriptionWord]]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                duration_milliseconds: int, 
                locale: Optional[str] = ..., 
                offset_milliseconds: int, 
                text: str, 
                words: Optional[list[VoiceAgentTranscriptionWord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTranscriptionWord(_Model):
        duration_milliseconds: int
        offset_milliseconds: int
        text: str

        @overload
        def __init__(
                self, 
                *, 
                duration_milliseconds: int, 
                offset_milliseconds: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentWebSocketSubprotocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REALTIME = "realtime"


    class azure.ai.projects.models.VoiceAssistantMessageItem(VoiceMessageItem, discriminator='assistant'):
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageAssistantContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAudioCodec(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM16 = "pcm16"
        PCMA = "pcma"
        PCMU = "pcmu"


    class azure.ai.projects.models.VoiceAudioConfig(_Model):
        input: Optional[VoiceAudioInputConfig]
        output: Optional[VoiceAudioOutputConfig]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[VoiceAudioInputConfig] = ..., 
                output: Optional[VoiceAudioOutputConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAudioContainerFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAV = "wav"


    class azure.ai.projects.models.VoiceAudioFormat(_Model):
        rate: Optional[int]
        type: Union[str, VoiceAudioFormatType]

        @overload
        def __init__(
                self, 
                *, 
                rate: Optional[int] = ..., 
                type: Union[str, VoiceAudioFormatType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAudioFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM = "audio/pcm"
        PCMA = "audio/pcma"
        PCMU = "audio/pcmu"


    class azure.ai.projects.models.VoiceAudioInputConfig(_Model):
        echo_cancellation: Optional[VoiceAgentEchoCancellation]
        format: Optional[VoiceAudioFormat]
        noise_reduction: Optional[VoiceNoiseReduction]
        transcription: Optional[VoiceInputTranscription]
        turn_detection: Optional[VoiceAgentTurnDetection]

        @overload
        def __init__(
                self, 
                *, 
                echo_cancellation: Optional[VoiceAgentEchoCancellation] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                noise_reduction: Optional[VoiceNoiseReduction] = ..., 
                transcription: Optional[VoiceInputTranscription] = ..., 
                turn_detection: Optional[VoiceAgentTurnDetection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAudioOutputConfig(_Model):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        custom_voice_endpoint_id: Optional[str]
        format: Optional[VoiceAudioFormat]
        output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]]
        personal_voice_model: Optional[str]
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        speed: Optional[float]
        style: Optional[str]
        voice: Optional[str]
        voice_locale: Optional[str]
        voice_temperature: Optional[float]
        voice_type: Optional[str]
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                custom_voice_endpoint_id: Optional[str] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]] = ..., 
                personal_voice_model: Optional[str] = ..., 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                speed: Optional[float] = ..., 
                style: Optional[str] = ..., 
                voice: Optional[str] = ..., 
                voice_locale: Optional[str] = ..., 
                voice_temperature: Optional[float] = ..., 
                voice_type: Optional[str] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAudioRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        USER = "user"


    class azure.ai.projects.models.VoiceAudioTimestampType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORD = "word"


    class azure.ai.projects.models.VoiceAvatarConfig(_Model):
        character: str
        customized: Optional[bool]
        model: Optional[str]
        output_audit_audio: Optional[bool]
        output_protocol: Optional[Union[str, VoiceAvatarOutputProtocol]]
        scene: Optional[VoiceAgentAvatarScene]
        style: Optional[str]
        type: Union[str, VoiceAvatarType]
        video: Optional[VoiceAgentAvatarVideoParams]

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: Optional[bool] = ..., 
                model: Optional[str] = ..., 
                output_audit_audio: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, VoiceAvatarOutputProtocol]] = ..., 
                scene: Optional[VoiceAgentAvatarScene] = ..., 
                style: Optional[str] = ..., 
                type: Union[str, VoiceAvatarType], 
                video: Optional[VoiceAgentAvatarVideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAvatarOutputProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"
        WEBSOCKET_BINARY = "websocket-binary"


    class azure.ai.projects.models.VoiceAvatarType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHOTO_AVATAR = "photo_avatar"
        VIDEO_AVATAR = "video_avatar"


    class azure.ai.projects.models.VoiceAzureSemanticVadEnTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad_en'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAzureSemanticVadMultilingualTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad_multilingual'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAzureSemanticVadTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceConversation(_Model):
        completed_at: Optional[datetime]
        created_at: datetime
        id: str
        last_error: Optional[ApiError]
        metadata: Optional[dict[str, str]]
        object: Literal["conversation"]
        status: Union[str, VoiceConversationStatus]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                created_at: datetime, 
                id: str, 
                last_error: Optional[ApiError] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                status: Union[str, VoiceConversationStatus], 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceConversationItem(_Model):
        created_at: Optional[datetime]
        response_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                response_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.projects.models.VoiceConversationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.projects.models.VoiceEndOfUtteranceDetection(_Model):
        model: Union[str, VoiceEndOfUtteranceDetectionModel]
        threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]]
        timeout_ms: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                model: Union[str, VoiceEndOfUtteranceDetectionModel], 
                threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]] = ..., 
                timeout_ms: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceEndOfUtteranceDetectionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_DETECTION_V1 = "semantic_detection_v1"
        SEMANTIC_DETECTION_V1_EN = "semantic_detection_v1_en"
        SEMANTIC_DETECTION_V1_MULTILINGUAL = "semantic_detection_v1_multilingual"
        SMART_END_OF_TURN_DETECTION = "smart_end_of_turn_detection"


    class azure.ai.projects.models.VoiceEndOfUtteranceThresholdLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.projects.models.VoiceFunctionCallItem(VoiceConversationItem, discriminator='function_call'):
        arguments: str
        call_id: Optional[str]
        created_at: datetime
        id: Optional[str]
        name: str
        object: Optional[Literal["item"]]
        response_id: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: Optional[str] = ..., 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceFunctionCallOutputItem(VoiceConversationItem, discriminator='function_call_output'):
        call_id: str
        created_at: datetime
        id: Optional[str]
        name: Optional[str]
        object: Optional[Literal["item"]]
        output: str
        response_id: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceGreetingConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceInputTranscription(_Model):
        custom_speech: Optional[dict[str, str]]
        delay: Optional[Literal["minimal", "low", "medium", "high", "xhigh"]]
        language: Optional[str]
        model: Union[str, VoiceInputTranscriptionModel]
        phrase_list: Optional[list[str]]
        prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_speech: Optional[dict[str, str]] = ..., 
                delay: Optional[Literal[minimal, low, medium, high, xhigh]] = ..., 
                language: Optional[str] = ..., 
                model: Union[str, VoiceInputTranscriptionModel], 
                phrase_list: Optional[list[str]] = ..., 
                prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceInputTranscriptionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SPEECH = "azure-speech"
        GPT4_O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
        GPT4_O_TRANSCRIBE = "gpt-4o-transcribe"
        GPT4_O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"
        GPT_LIVE_TRANSCRIBE = "gpt-live-transcribe"
        GPT_REALTIME_WHISPER = "gpt-realtime-whisper"
        GPT_TRANSCRIBE = "gpt-transcribe"
        MAI_TRANSCRIBE = "mai-transcribe"
        WHISPER1 = "whisper-1"


    class azure.ai.projects.models.VoiceItemAudioResponse(_Model):
        blob_uri: Optional[str]
        channels: Optional[int]
        codec: Optional[Union[str, VoiceAudioCodec]]
        conversation_id: str
        duration_ms: Optional[timedelta]
        format: Optional[Union[str, VoiceAudioContainerFormat]]
        item_id: str
        role: Optional[Union[str, VoiceAudioRole]]
        sample_rate: Optional[int]
        start_offset_ms: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                channels: Optional[int] = ..., 
                codec: Optional[Union[str, VoiceAudioCodec]] = ..., 
                conversation_id: str, 
                duration_ms: Optional[timedelta] = ..., 
                format: Optional[Union[str, VoiceAudioContainerFormat]] = ..., 
                item_id: str, 
                role: Optional[Union[str, VoiceAudioRole]] = ..., 
                sample_rate: Optional[int] = ..., 
                start_offset_ms: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceMcpApprovalRequestItem(VoiceConversationItem, discriminator='mcp_approval_request'):
        arguments: str
        created_at: datetime
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceMcpApprovalResponseItem(VoiceConversationItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        created_at: datetime
        id: str
        reason: Optional[str]
        response_id: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                reason: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceMcpCallItem(VoiceConversationItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        created_at: datetime
        error: Optional[RealtimeMCPError]
        id: str
        name: str
        output: Optional[str]
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                created_at: Optional[datetime] = ..., 
                error: Optional[RealtimeMCPError] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceMcpListToolsItem(VoiceConversationItem, discriminator='mcp_list_tools'):
        created_at: datetime
        id: Optional[str]
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[VoiceConversationItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceMessageItem(VoiceConversationItem, discriminator='message'):
        created_at: datetime
        response_id: str
        role: str
        type: Literal[VoiceConversationItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                response_id: Optional[str] = ..., 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "managed"
        SELF_DEPLOYED = "self_deployed"


    class azure.ai.projects.models.VoiceNoiseReduction(_Model):
        type: Union[str, VoiceNoiseReductionType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, VoiceNoiseReductionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceNoiseReductionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEEP_NOISE_SUPPRESSION = "azure_deep_noise_suppression"
        FAR_FIELD = "far_field"
        NEAR_FIELD = "near_field"


    class azure.ai.projects.models.VoiceOutputModality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANIMATION = "animation"
        AUDIO = "audio"
        AVATAR = "avatar"
        TEXT = "text"


    class azure.ai.projects.models.VoiceRecordingChannelLayout(_Model):
        left: Literal["user"]
        right: Literal["agent"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.VoiceRecordingResponse(_Model):
        blob_uri: Optional[str]
        channel_layout: VoiceRecordingChannelLayout
        channels: int
        conversation_id: str
        duration_ms: timedelta
        format: Union[str, VoiceAudioContainerFormat]
        sample_rate: int

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                channel_layout: VoiceRecordingChannelLayout, 
                channels: int, 
                conversation_id: str, 
                duration_ms: timedelta, 
                format: Union[str, VoiceAudioContainerFormat], 
                sample_rate: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponse(OmitPropertiesRealtimeResponse):
        audio: Optional[VoiceResponseAudio]
        completed_at: Optional[datetime]
        conversation_id: str
        created_at: Optional[datetime]
        id: str
        max_output_tokens: Union[int, str]
        metadata: Optional[dict[str, str]]
        object: str
        output: Optional[list[VoiceConversationItem]]
        output_modalities: Union[list[str, str]]
        status: Union[str, str, str, str, str]
        status_details: RealtimeResponseStatusDetails
        temperature: Optional[float]
        usage: RealtimeResponseUsage

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceResponseAudio] = ..., 
                completed_at: Optional[datetime] = ..., 
                conversation_id: str, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                object: Optional[Literal[response]] = ..., 
                output: Optional[list[VoiceConversationItem]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                temperature: Optional[float] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponseAudio(_Model):
        output: Optional[VoiceResponseAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceResponseAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponseAudioOutput(_Model):
        format: Optional[RealtimeAudioFormats]
        voice: Optional[str]
        voice_locale: Optional[str]
        voice_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[RealtimeAudioFormats] = ..., 
                voice: Optional[str] = ..., 
                voice_locale: Optional[str] = ..., 
                voice_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceServerVadTurnDetection(VoiceTurnDetection, discriminator='server_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[int] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceSystemMessageItem(VoiceMessageItem, discriminator='system'):
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageSystemContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceSystemTool(VoiceAgentTool, discriminator='system'):
        description: Optional[str]
        name: Union[str, VoiceSystemToolName]
        type: Literal["system"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Union[str, VoiceSystemToolName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceSystemToolName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        END_CONVERSATION = "end_conversation"


    class azure.ai.projects.models.VoiceToolboxTool(VoiceAgentTool, discriminator='toolbox'):
        response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]]
        toolbox_name: str
        toolbox_version: str
        type: Literal["toolbox"]

        @overload
        def __init__(
                self, 
                *, 
                response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]] = ..., 
                toolbox_name: str, 
                toolbox_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceTurnDetection(_Model):
        auto_truncate: Optional[bool]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.projects.models.VoiceUserMessageItem(VoiceMessageItem, discriminator='user'):
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageUserContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchApproximateLocation(_Model):
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


    class azure.ai.projects.models.WebSearchConfiguration(_Model):
        instance_name: str
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                instance_name: str, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchPreviewTool(Tool, discriminator='web_search_preview'):
        search_content_types: Optional[list[Union[str, SearchContentType]]]
        search_context_size: Optional[Union[str, SearchContextSize]]
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: Optional[ApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                search_content_types: Optional[list[Union[str, SearchContentType]]] = ..., 
                search_context_size: Optional[Union[str, SearchContextSize]] = ..., 
                user_location: Optional[ApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchTool(Tool, discriminator='web_search'):
        custom_search_configuration: Optional[WebSearchConfiguration]
        description: Optional[str]
        filters: Optional[WebSearchToolFilters]
        name: Optional[str]
        search_context_size: Optional[Literal["low", "medium", "high"]]
        tool_configs: Optional[dict[str, ToolConfig]]
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
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                user_location: Optional[WebSearchApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchToolFilters(_Model):
        allowed_domains: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchToolboxTool(ToolboxTool, discriminator='web_search'):
        custom_search_configuration: Optional[WebSearchConfiguration]
        description: str
        filters: Optional[WebSearchToolFilters]
        name: str
        search_context_size: Optional[Literal["low", "medium", "high"]]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WEB_SEARCH]
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
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                user_location: Optional[WebSearchApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WeeklyRecurrenceSchedule(RecurrenceSchedule, discriminator='Weekly'):
        days_of_week: list[Union[str, DayOfWeek]]
        type: Literal[RecurrenceType.WEEKLY]

        @overload
        def __init__(
                self, 
                *, 
                days_of_week: list[Union[str, DayOfWeek]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkIQPreviewTool(Tool, discriminator='work_iq_preview'):
        project_connection_id: str
        type: Literal[ToolType.WORK_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkIQPreviewToolboxTool(ToolboxTool, discriminator='work_iq_preview'):
        description: str
        name: str
        project_connection_id: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WORK_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkflowAgentDefinition(AgentDefinition, discriminator='workflow'):
        kind: Literal[AgentKind.WORKFLOW]
        rai_config: RaiConfig
        workflow: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rai_config: Optional[RaiConfig] = ..., 
                workflow: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.projects.operations

    class azure.ai.projects.operations.AgentEndpointConversationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace
        def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace
        def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace
        def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace
        def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceResponse]: ...

        @distributed_trace
        def list_agent_conversations(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversation]: ...


    class azure.ai.projects.operations.AgentsOperations(GeneratedAgentsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                version_indicator: VersionIndicator, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                body: CreateSessionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def create_version_from_code(
                self, 
                agent_name: str, 
                *, 
                code: IO[bytes], 
                code_zip_sha256: Optional[str] = ..., 
                definition: HostedAgentDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                manifest_id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                parameter_values: dict[str, Any], 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: CreateAgentVersionFromManifestRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def delete(
                self, 
                agent_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace
        def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace
        def disable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_code(
                self, 
                agent_name: str, 
                *, 
                agent_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def download_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def enable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_agent(
                self, 
                *, 
                content_type: str = "application/json", 
                kind: Union[str, AgentKind], 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def generate_agent(
                self, 
                body: GenerateAgentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def generate_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace
        def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace
        def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace
        def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

        @distributed_trace
        def get_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                kind: Optional[Union[str, AgentKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentDetails]: ...

        @distributed_trace
        def list_session_files(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                path: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SessionDirectoryEntry]: ...

        @distributed_trace
        def list_sessions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentSessionResource]: ...

        @distributed_trace
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentVersionDetails]: ...

        @distributed_trace
        def stop_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                body: PatchAgentObjectRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...

        @overload
        def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: IO[bytes], 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.operations.BetaAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentOptimizationJobResult]: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentOptimizationJobResult]: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[AgentOptimizationJobResult]: ...

        @distributed_trace
        def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def delete_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def list_optimization_jobs(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentOptimizationJobListItem]: ...


    class azure.ai.projects.operations.BetaDatasetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[DataGenerationJobResult]: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[DataGenerationJobResult]: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[DataGenerationJobResult]: ...

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataGenerationJob]: ...


    class azure.ai.projects.operations.BetaEvaluationTaxonomiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                input_name: Optional[str] = ..., 
                input_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluationTaxonomy]: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...


    class azure.ai.projects.operations.BetaEvaluatorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[EvaluatorVersion]: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[EvaluatorVersion]: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[EvaluatorVersion]: ...

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorVersion]: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorGenerationJob]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorVersion]: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...


    class azure.ai.projects.operations.BetaInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def generate(
                self, 
                insight: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def get(
                self, 
                insight_id: str, 
                *, 
                include_coordinates: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                include_coordinates: Optional[bool] = ..., 
                run_id: Optional[str] = ..., 
                type: Optional[Union[str, InsightType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Insight]: ...


    class azure.ai.projects.operations.BetaMemoryStoresOperations(GenerateBetaMemoryStoresOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                previous_update_id: Optional[str] = ..., 
                scope: str, 
                update_delay: Optional[int] = ..., 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def create(
                self, 
                *, 
                content_type: str = "application/json", 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create(
                self, 
                body: CreateMemoryStoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                kind: Union[str, MemoryItemKind], 
                scope: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                body: CreateMemoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

        @distributed_trace
        def delete_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> DeleteMemoryResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                body: DeleteScopeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @distributed_trace
        def get_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryStoreDetails]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: ListMemoriesRequest, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                options: Optional[MemorySearchOptions] = ..., 
                previous_search_id: Optional[str] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: UpdateMemoryStoreRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: UpdateMemoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...


    class azure.ai.projects.operations.BetaModelsOperations(BetaModelsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                *, 
                azcopy_path: Optional[str] = ..., 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[True] = True, 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def create(
                self, 
                *, 
                azcopy_path: Optional[str] = ..., 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[False], 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ModelVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelVersion]: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...


    class azure.ai.projects.operations.BetaOperations(GeneratedBetaOperations):
        agents: BetaAgentsOperations
        datasets: BetaDatasetsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        models: BetaModelsOperations
        red_teams: BetaRedTeamsOperations
        routines: BetaRoutinesOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.operations.BetaRedTeamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        def create(
                self, 
                red_team: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[RedTeam]: ...


    class azure.ai.projects.operations.BetaRoutinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                *, 
                action: Optional[RoutineAction] = ..., 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                body: CreateOrUpdateRoutineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def delete(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                *, 
                content_type: str = "application/json", 
                payload: Optional[RoutineDispatchPayload] = ..., 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                body: DispatchRoutineAsyncRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @distributed_trace
        def enable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def get(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Routine]: ...

        @distributed_trace
        def list_runs(
                self, 
                routine_name: str, 
                *, 
                before: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoutineRun]: ...


    class azure.ai.projects.operations.BetaSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def get_run(
                self, 
                schedule_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScheduleRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Schedule]: ...

        @distributed_trace
        def list_runs(
                self, 
                schedule_id: str, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScheduleRun]: ...


    class azure.ai.projects.operations.BetaSkillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default: Optional[bool] = ..., 
                inline_content: Optional[SkillInlineContent] = ..., 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create(
                self, 
                name: str, 
                body: CreateSkillVersionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResult: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DeleteSkillVersionResult: ...

        @distributed_trace
        def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def download_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkillDetails]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkillVersion]: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: UpdateSkillRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...


    class azure.ai.projects.operations.ConnectionsOperations(ConnectionsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def get_default(
                self, 
                connection_type: Union[str, ConnectionType], 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                *, 
                connection_type: Optional[Union[str, ConnectionType]] = ..., 
                default_connection: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Connection]: ...


    class azure.ai.projects.operations.DatasetsOperations(DatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DatasetVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatasetVersion]: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @distributed_trace
        def upload_file(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_path: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FileDatasetVersion: ...

        @distributed_trace
        def upload_folder(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_pattern: Optional[Pattern] = ..., 
                folder: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FolderDatasetVersion: ...


    class azure.ai.projects.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                deployment_type: Optional[Union[str, DeploymentType]] = ..., 
                model_name: Optional[str] = ..., 
                model_publisher: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...


    class azure.ai.projects.operations.EvaluationRulesOperations(GeneratedEvaluationRulesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: EvaluationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def list(
                self, 
                *, 
                action_type: Optional[Union[str, EvaluationRuleActionType]] = ..., 
                agent_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluationRule]: ...


    class azure.ai.projects.operations.IndexesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Index]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[Index]: ...


    class azure.ai.projects.operations.TelemetryOperations:

        def __init__(self, outer_instance: AIProjectClient) -> None: ...

        @distributed_trace
        def get_application_insights_connection_string(self) -> str: ...


    class azure.ai.projects.operations.ToolboxesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_version(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[List[ToolboxSkill]] = ..., 
                tools: List[ToolboxTool], 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        def create_version(
                self, 
                name: str, 
                body: CreateToolboxVersionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        def create_version(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ToolboxObject]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ToolboxVersionObject]: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: UpdateToolboxRequest1, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...


    class azure.ai.projects.operations.VoiceAgentWebSocketOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def connect_voice_agent(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                store: Optional[bool] = ..., 
                structured_inputs: Optional[str] = ..., 
                websocket_subprotocol: Optional[Union[str, VoiceAgentWebSocketSubprotocol]] = ..., 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.projects.telemetry

    def azure.ai.projects.telemetry.trace_function(span_name: Optional[str] = None) -> Callable: ...


    class azure.ai.projects.telemetry.AIProjectInstrumentor:

        def __init__(self) -> None: ...

        def instrument(
                self, 
                enable_content_recording: Optional[bool] = None, 
                enable_trace_context_propagation: Optional[bool] = None, 
                enable_baggage_propagation: Optional[bool] = None
            ) -> None: ...

        def is_content_recording_enabled(self) -> bool: ...

        def is_instrumented(self) -> bool: ...

        def uninstrument(self) -> None: ...


namespace azure.ai.projects.types

    class azure.ai.projects.types.A2APreviewTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "project_connection_id": str
        key "send_credentials_for_agent_card": bool
        key "type": Required[Literal[ToolType.A2A_PREVIEW]]
        agent_card_path: str
        base_url: str
        project_connection_id: str
        send_credentials_for_agent_card: bool
        type: Literal[ToolType.A2A_PREVIEW]


    class azure.ai.projects.types.A2APreviewToolboxTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "description": str
        key "name": str
        key "project_connection_id": str
        key "send_credentials_for_agent_card": bool
        key "type": Required[Literal[ToolboxToolType.A2A_PREVIEW]]
        agent_card_path: str
        base_url: str
        description: str
        name: str
        project_connection_id: str
        send_credentials_for_agent_card: bool
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.A2A_PREVIEW]


    class azure.ai.projects.types.A2AProtocolConfiguration(TypedDict, total=False):


    class azure.ai.projects.types.AISearchIndexResource(TypedDict, total=False):
        key "filter": str
        key "index_asset_id": str
        key "index_name": str
        key "project_connection_id": str
        key "query_type": Union[str, AzureAISearchQueryType]
        key "top_k": int
        filter: str
        index_asset_id: str
        index_name: str
        project_connection_id: str
        query_type: Union[str, AzureAISearchQueryType]
        top_k: int


    class azure.ai.projects.types.ActivityProtocolConfiguration(TypedDict, total=False):
        key "enable_m365_public_endpoint": bool
        enable_m365_public_endpoint: bool


    class azure.ai.projects.types.AgentBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.projects.types.AgentBlueprintReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_AGENT_IDENTITY_BLUEPRINT = "ManagedAgentIdentityBlueprint"


    class azure.ai.projects.types.AgentCard(TypedDict, total=False):
        key "description": str
        key "skills": Required[list[AgentCardSkill]]
        key "version": Required[str]
        description: str
        skills: list[AgentCardSkill]
        version: str


    class azure.ai.projects.types.AgentCardSkill(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        description: str
        examples: list[str]
        id: str
        name: str
        tags: list[str]


    class azure.ai.projects.types.AgentClusterInsightRequest(TypedDict, total=False):
        key "agentName": Required[str]
        key "modelConfiguration": ForwardRef('InsightModelConfiguration', module='types')
        key "type": Required[Literal[InsightType.AGENT_CLUSTER_INSIGHT]]
        agentName: str
        modelConfiguration: InsightModelConfiguration
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]


    class azure.ai.projects.types.AgentClusterInsightResult(TypedDict, total=False):
        key "clusterInsight": Required[ClusterInsightResult]
        key "type": Required[Literal[InsightType.AGENT_CLUSTER_INSIGHT]]
        clusterInsight: ClusterInsightResult
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]


    class azure.ai.projects.types.AgentDataGenerationJobSource(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        key "description": str
        key "type": Required[Literal[DataGenerationJobSourceType.AGENT]]
        agent_name: str
        agent_version: str
        description: str
        type: Literal[DataGenerationJobSourceType.AGENT]


    class azure.ai.projects.types.AgentEndpointAuthorizationSchemeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT_SERVICE = "BotService"
        BOT_SERVICE_RBAC = "BotServiceRbac"
        BOT_SERVICE_TENANT = "BotServiceTenant"
        ENTRA = "Entra"


    class azure.ai.projects.types.AgentEndpointConfig(TypedDict, total=False):
        key "protocol_configuration": ForwardRef('ProtocolConfiguration', module='types')
        key "version_selector": ForwardRef('VersionSelector', module='types')
        authorization_schemes: list[AgentEndpointAuthorizationScheme]
        protocol_configuration: ProtocolConfiguration
        version_selector: VersionSelector


    class azure.ai.projects.types.AgentEvaluatorGenerationJobSource(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        key "description": str
        key "type": Required[Literal[EvaluatorGenerationJobSourceType.AGENT]]
        agent_name: str
        agent_version: str
        description: str
        type: Literal[EvaluatorGenerationJobSourceType.AGENT]


    class azure.ai.projects.types.AgentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "external"
        HOSTED = "hosted"
        PROMPT = "prompt"
        VOICE = "voice"
        WORKFLOW = "workflow"


    class azure.ai.projects.types.AgentOptimizationCandidate(TypedDict, total=False):
        key "avg_score": Required[float]
        key "avg_tokens": Required[float]
        key "candidate_id": str
        key "eval_id": str
        key "eval_run_id": str
        key "name": Required[str]
        key "promotion": ForwardRef('PromotionInfo', module='types')
        avg_score: float
        avg_tokens: float
        candidate_id: str
        eval_id: str
        eval_run_id: str
        mutations: dict[str, Any]
        name: str
        promotion: PromotionInfo


    class azure.ai.projects.types.AgentOptimizationDatasetCriterion(TypedDict, total=False):
        key "instruction": Required[str]
        key "name": Required[str]
        instruction: str
        name: str


    class azure.ai.projects.types.AgentOptimizationDatasetInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.ai.projects.types.AgentOptimizationDatasetItem(TypedDict, total=False):
        key "desired_num_turns": int
        key "ground_truth": str
        key "query": str
        criteria: list[AgentOptimizationDatasetCriterion]
        desired_num_turns: int
        ground_truth: str
        query: str


    class azure.ai.projects.types.AgentOptimizationEvaluatorRef(TypedDict, total=False):
        key "name": Required[str]
        key "version": str
        name: str
        version: str


    class azure.ai.projects.types.AgentOptimizationInlineDatasetInput(TypedDict, total=False):
        key "items": Required[list[AgentOptimizationDatasetItem]]
        key "type": Required[Literal[AgentOptimizationDatasetInputType.INLINE]]
        items: list[AgentOptimizationDatasetItem]
        type: Literal[AgentOptimizationDatasetInputType.INLINE]


    class azure.ai.projects.types.AgentOptimizationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "id": Required[str]
        key "inputs": ForwardRef('AgentOptimizationJobInputs', module='types')
        key "progress": ForwardRef('AgentOptimizationJobProgress', module='types')
        key "result": ForwardRef('AgentOptimizationJobResult', module='types')
        key "status": Required[Union[str, JobStatus]]
        key "updated_at": Required[int]
        created_at: int
        error: ApiError
        id: str
        inputs: AgentOptimizationJobInputs
        progress: AgentOptimizationJobProgress
        result: AgentOptimizationJobResult
        status: Union[str, JobStatus]
        updated_at: int
        warnings: list[str]


    class azure.ai.projects.types.AgentOptimizationJobInputs(TypedDict, total=False):
        key "agent": Required[OptimizedAgentIdentifier]
        key "evaluators": Required[list[AgentOptimizationEvaluatorRef]]
        key "options": ForwardRef('AgentOptimizationOptions', module='types')
        key "train_dataset": Required[AgentOptimizationDatasetInput]
        key "validation_dataset": ForwardRef('AgentOptimizationDatasetInput', module='types')
        agent: OptimizedAgentIdentifier
        evaluators: list[AgentOptimizationEvaluatorRef]
        options: AgentOptimizationOptions
        train_dataset: AgentOptimizationDatasetInput
        validation_dataset: AgentOptimizationDatasetInput


    class azure.ai.projects.types.AgentOptimizationJobProgress(TypedDict, total=False):
        key "best_score": Required[float]
        key "candidates_completed": Required[int]
        key "elapsed_seconds": Required[float]
        best_score: float
        candidates_completed: int
        elapsed_seconds: float


    class azure.ai.projects.types.AgentOptimizationJobResult(TypedDict, total=False):
        key "baseline": str
        key "best": str
        baseline: str
        best: str
        candidates: list[AgentOptimizationCandidate]


    class azure.ai.projects.types.AgentOptimizationOptions(TypedDict, total=False):
        key "eval_model": str
        key "evaluation_level": Union[str, EvaluationLevel]
        key "max_candidates": int
        key "max_stalls": int
        key "optimization_model": str
        eval_model: str
        evaluation_level: Union[str, EvaluationLevel]
        max_candidates: int
        max_stalls: int
        optimization_config: dict[str, Any]
        optimization_model: str


    class azure.ai.projects.types.AgentOptimizationReferenceDatasetInput(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[AgentOptimizationDatasetInputType.REFERENCE]]
        key "version": str
        name: str
        type: Literal[AgentOptimizationDatasetInputType.REFERENCE]
        version: str


    class azure.ai.projects.types.AgentTaxonomyInput(TypedDict, total=False):
        key "riskCategories": Required[list[Union[str, RiskCategory]]]
        key "target": Required[EvaluationTarget]
        key "type": Required[Literal[EvaluationTaxonomyInputType.AGENT]]
        riskCategories: list[Union[str, RiskCategory]]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]


    class azure.ai.projects.types.ApiError(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": str
        additionalInfo: dict[str, Any]
        code: str
        debugInfo: dict[str, Any]
        details: list[ApiError]
        message: str
        param: str
        type: str


    class azure.ai.projects.types.ApplyPatchToolParam(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "type": Required[Literal[ToolType.APPLY_PATCH]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        type: Literal[ToolType.APPLY_PATCH]


    class azure.ai.projects.types.ApproximateLocation(TypedDict, total=False):
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


    class azure.ai.projects.types.ArtifactProfile(TypedDict, total=False):
        key "category": Required[Union[str, FoundryModelArtifactProfileCategory]]
        category: Union[str, FoundryModelArtifactProfileCategory]
        signals: list[Union[str, FoundryModelArtifactProfileSignal]]


    class azure.ai.projects.types.AutoCodeInterpreterToolParam(TypedDict, total=False):
        key "memory_limit": Optional[Union[str, ContainerMemoryLimit]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal["auto"]]
        file_ids: list[str]
        memory_limit: Union[str, ContainerMemoryLimit]
        network_policy: ContainerNetworkPolicyParam
        type: Literal[auto]


    class azure.ai.projects.types.AzureAIAgentTarget(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["azure_ai_agent"]]
        key "version": str
        name: str
        tool_descriptions: list[ToolDescription]
        tools: list[Tool]
        type: Literal[azure_ai_agent]
        version: str


    class azure.ai.projects.types.AzureAIModelTarget(TypedDict, total=False):
        key "model": str
        key "sampling_params": ForwardRef('ModelSamplingParams', module='types')
        key "type": Required[Literal["azure_ai_model"]]
        model: str
        sampling_params: ModelSamplingParams
        type: Literal[azure_ai_model]


    class azure.ai.projects.types.AzureAISearchIndex(TypedDict, total=False):
        key "connectionName": Required[str]
        key "description": str
        key "fieldMapping": ForwardRef('FieldMapping', module='types')
        key "id": str
        key "indexName": Required[str]
        key "name": Required[str]
        key "type": Required[Literal[IndexType.AZURE_SEARCH]]
        key "version": Required[str]
        connectionName: str
        description: str
        fieldMapping: FieldMapping
        id: str
        indexName: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.AZURE_SEARCH]
        version: str


    class azure.ai.projects.types.AzureAISearchTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolType.AZURE_AI_SEARCH]]
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.AZURE_AI_SEARCH]


    class azure.ai.projects.types.AzureAISearchToolResource(TypedDict, total=False):
        key "indexes": Required[list[AISearchIndexResource]]
        indexes: list[AISearchIndexResource]


    class azure.ai.projects.types.AzureAISearchToolboxTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.AZURE_AI_SEARCH]]
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.AZURE_AI_SEARCH]


    class azure.ai.projects.types.AzureFunctionBinding(TypedDict, total=False):
        key "storage_queue": Required[AzureFunctionStorageQueue]
        key "type": Required[Literal["storage_queue"]]
        storage_queue: AzureFunctionStorageQueue
        type: Literal[storage_queue]


    class azure.ai.projects.types.AzureFunctionDefinition(TypedDict, total=False):
        key "function": Required[AzureFunctionDefinitionFunction]
        key "input_binding": Required[AzureFunctionBinding]
        key "output_binding": Required[AzureFunctionBinding]
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding


    class azure.ai.projects.types.AzureFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.projects.types.AzureFunctionStorageQueue(TypedDict, total=False):
        key "queue_name": Required[str]
        key "queue_service_endpoint": Required[str]
        queue_name: str
        queue_service_endpoint: str


    class azure.ai.projects.types.AzureFunctionTool(TypedDict, total=False):
        key "azure_function": Required[AzureFunctionDefinition]
        key "type": Required[Literal[ToolType.AZURE_FUNCTION]]
        azure_function: AzureFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.AZURE_FUNCTION]


    class azure.ai.projects.types.AzureOpenAIModelConfiguration(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        key "type": Required[Literal["AzureOpenAIModel"]]
        modelDeploymentName: str
        type: Literal[AzureOpenAIModel]


    class azure.ai.projects.types.BingCustomSearchConfiguration(TypedDict, total=False):
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


    class azure.ai.projects.types.BingCustomSearchPreviewTool(TypedDict, total=False):
        key "bing_custom_search_preview": Required[BingCustomSearchToolParameters]
        key "type": Required[Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]]
        bing_custom_search_preview: BingCustomSearchToolParameters
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]


    class azure.ai.projects.types.BingCustomSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingCustomSearchConfiguration]]
        search_configurations: list[BingCustomSearchConfiguration]


    class azure.ai.projects.types.BingGroundingSearchConfiguration(TypedDict, total=False):
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


    class azure.ai.projects.types.BingGroundingSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingGroundingSearchConfiguration]]
        search_configurations: list[BingGroundingSearchConfiguration]


    class azure.ai.projects.types.BingGroundingTool(TypedDict, total=False):
        key "bing_grounding": Required[BingGroundingSearchToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolType.BING_GROUNDING]]
        bing_grounding: BingGroundingSearchToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.BING_GROUNDING]


    class azure.ai.projects.types.BotServiceAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]


    class azure.ai.projects.types.BotServiceRbacAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]


    class azure.ai.projects.types.BotServiceTenantAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]


    class azure.ai.projects.types.BrowserAutomationPreviewTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "type": Required[Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]]
        browser_automation_preview: BrowserAutomationToolParameters
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]


    class azure.ai.projects.types.BrowserAutomationPreviewToolboxTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.BROWSER_AUTOMATION_PREVIEW]]
        browser_automation_preview: BrowserAutomationToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.BROWSER_AUTOMATION_PREVIEW]


    class azure.ai.projects.types.BrowserAutomationToolConnectionParameters(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.projects.types.BrowserAutomationToolParameters(TypedDict, total=False):
        key "connection": Required[BrowserAutomationToolConnectionParameters]
        connection: BrowserAutomationToolConnectionParameters


    class azure.ai.projects.types.CaptureStructuredOutputsTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "outputs": Required[StructuredOutputDefinition]
        key "type": Required[Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]]
        description: str
        name: str
        outputs: StructuredOutputDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]


    class azure.ai.projects.types.ChartCoordinate(TypedDict, total=False):
        key "size": Required[int]
        key "x": Required[int]
        key "y": Required[int]
        size: int
        x: int
        y: int


    class azure.ai.projects.types.ClusterInsightResult(TypedDict, total=False):
        key "clusters": Required[list[InsightCluster]]
        key "summary": Required[InsightSummary]
        clusters: list[InsightCluster]
        coordinates: dict[str, ChartCoordinate]
        summary: InsightSummary


    class azure.ai.projects.types.ClusterTokenUsage(TypedDict, total=False):
        key "inputTokenUsage": Required[int]
        key "outputTokenUsage": Required[int]
        key "totalTokenUsage": Required[int]
        inputTokenUsage: int
        outputTokenUsage: int
        totalTokenUsage: int


    class azure.ai.projects.types.CodeBasedEvaluatorDefinition(TypedDict, total=False):
        key "blob_uri": str
        key "code_text": str
        key "entry_point": str
        key "image_tag": str
        key "type": Required[Literal[EvaluatorDefinitionType.CODE]]
        blob_uri: str
        code_text: str
        data_schema: dict[str, Any]
        entry_point: str
        image_tag: str
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.CODE]


    class azure.ai.projects.types.CodeConfiguration(TypedDict, total=False):
        key "content_hash": str
        key "dependency_resolution": Required[Union[str, CodeDependencyResolution]]
        key "entry_point": Required[list[str]]
        key "runtime": Required[str]
        content_hash: str
        dependency_resolution: Union[str, CodeDependencyResolution]
        entry_point: list[str]
        runtime: str


    class azure.ai.projects.types.CodeInterpreterTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolType.CODE_INTERPRETER]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        container: Union[str, AutoCodeInterpreterToolParam]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.CODE_INTERPRETER]


    class azure.ai.projects.types.CodeInterpreterToolboxTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.CODE_INTERPRETER]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        container: Union[str, AutoCodeInterpreterToolParam]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.CODE_INTERPRETER]


    class azure.ai.projects.types.ComparisonFilter(TypedDict, total=False):
        key "key": Required[str]
        key "type": Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
        key "value": Required[Union[str, float, bool, list[Union[str, float]]]]
        key: str
        type: Literal[eq, ne, gt, gte, lt, lte, in, nin]
        value: Union[str, float, bool, list[Union[str, float]]]


    class azure.ai.projects.types.CompoundFilter(TypedDict, total=False):
        key "filters": Required[list[Union[ComparisonFilter, Any]]]
        key "type": Required[Literal["and", "or"]]
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal[and, or]


    class azure.ai.projects.types.ComputerTool(TypedDict, total=False):
        key "type": Required[Literal[ToolType.COMPUTER]]
        type: Literal[ToolType.COMPUTER]


    class azure.ai.projects.types.ComputerUsePreviewTool(TypedDict, total=False):
        key "display_height": Required[int]
        key "display_width": Required[int]
        key "environment": Required[Union[str, ComputerEnvironment]]
        key "type": Required[Literal[ToolType.COMPUTER_USE_PREVIEW]]
        display_height: int
        display_width: int
        environment: Union[str, ComputerEnvironment]
        type: Literal[ToolType.COMPUTER_USE_PREVIEW]


    class azure.ai.projects.types.ContainerAutoParam(TypedDict, total=False):
        key "memory_limit": Optional[Union[str, ContainerMemoryLimit]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]]
        file_ids: list[str]
        memory_limit: Union[str, ContainerMemoryLimit]
        network_policy: ContainerNetworkPolicyParam
        skills: list[ContainerSkill]
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]


    class azure.ai.projects.types.ContainerConfiguration(TypedDict, total=False):
        key "image": Required[str]
        image: str


    class azure.ai.projects.types.ContainerNetworkPolicyAllowlistParam(TypedDict, total=False):
        key "allowed_domains": Required[list[str]]
        key "type": Required[Literal[ContainerNetworkPolicyParamType.ALLOWLIST]]
        allowed_domains: list[str]
        domain_secrets: list[ContainerNetworkPolicyDomainSecretParam]
        type: Literal[ContainerNetworkPolicyParamType.ALLOWLIST]


    class azure.ai.projects.types.ContainerNetworkPolicyDisabledParam(TypedDict, total=False):
        key "type": Required[Literal[ContainerNetworkPolicyParamType.DISABLED]]
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]


    class azure.ai.projects.types.ContainerNetworkPolicyDomainSecretParam(TypedDict, total=False):
        key "domain": Required[str]
        key "name": Required[str]
        key "value": Required[str]
        domain: str
        name: str
        value: str


    class azure.ai.projects.types.ContainerNetworkPolicyParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWLIST = "allowlist"
        DISABLED = "disabled"


    class azure.ai.projects.types.ContainerSkillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        SKILL_REFERENCE = "skill_reference"


    class azure.ai.projects.types.ContinuousEvaluationRuleAction(TypedDict, total=False):
        key "evalId": Required[str]
        key "maxHourlyRuns": int
        key "samplingRate": float
        key "type": Required[Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]]
        evalId: str
        maxHourlyRuns: int
        samplingRate: float
        type: Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]


    class azure.ai.projects.types.CosmosDBIndex(TypedDict, total=False):
        key "connectionName": Required[str]
        key "containerName": Required[str]
        key "databaseName": Required[str]
        key "description": str
        key "embeddingConfiguration": Required[EmbeddingConfiguration]
        key "fieldMapping": Required[FieldMapping]
        key "id": str
        key "name": Required[str]
        key "type": Required[Literal[IndexType.COSMOS_DB]]
        key "version": Required[str]
        connectionName: str
        containerName: str
        databaseName: str
        description: str
        embeddingConfiguration: EmbeddingConfiguration
        fieldMapping: FieldMapping
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.COSMOS_DB]
        version: str


    class azure.ai.projects.types.CreateAgentVersionFromManifestRequest(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.projects.types.CreateAgentVersionRequest(TypedDict, total=False):
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "definition": Required[AgentDefinition]
        key "description": str
        key "draft": bool
        blueprint_reference: AgentBlueprintReference
        definition: AgentDefinition
        description: str
        draft: bool
        metadata: dict[str, str]


    class azure.ai.projects.types.CreateMemoryRequest(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Union[str, MemoryItemKind]]
        key "scope": Required[str]
        content: str
        kind: Union[str, MemoryItemKind]
        scope: str


    class azure.ai.projects.types.CreateMemoryStoreRequest(TypedDict, total=False):
        key "definition": Required[MemoryStoreDefinition]
        key "description": str
        key "name": Required[str]
        definition: MemoryStoreDefinition
        description: str
        metadata: dict[str, str]
        name: str


    class azure.ai.projects.types.CreateOrUpdateRoutineRequest(TypedDict, total=False):
        key "action": ForwardRef('RoutineAction', module='types')
        key "description": str
        key "enabled": bool
        action: RoutineAction
        description: str
        enabled: bool
        triggers: dict[str, RoutineTrigger]


    class azure.ai.projects.types.CreateSessionRequest(TypedDict, total=False):
        key "agent_session_id": str
        key "version_indicator": Required[VersionIndicator]
        agent_session_id: str
        version_indicator: VersionIndicator


    class azure.ai.projects.types.CreateSkillVersionFromFilesBody(TypedDict, total=False):
        key "default": bool
        key "files": Required[list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]]
        default: bool
        files: list[FileType]


    class azure.ai.projects.types.CreateSkillVersionRequest(TypedDict, total=False):
        key "default": bool
        key "inline_content": ForwardRef('SkillInlineContent', module='types')
        default: bool
        inline_content: SkillInlineContent


    class azure.ai.projects.types.CreateToolboxVersionRequest(TypedDict, total=False):
        key "description": str
        key "policies": ForwardRef('ToolboxPolicies', module='types')
        key "tools": Required[list[ToolboxTool]]
        description: str
        metadata: dict[str, str]
        policies: ToolboxPolicies
        skills: list[ToolboxSkill]
        tools: list[ToolboxTool]


    class azure.ai.projects.types.CreateTranscriptionResponseJsonUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DURATION = "duration"
        TOKENS = "tokens"


    class azure.ai.projects.types.CronTrigger(TypedDict, total=False):
        key "endTime": str
        key "expression": Required[str]
        key "startTime": str
        key "timeZone": str
        key "type": Required[Literal[TriggerType.CRON]]
        endTime: str
        expression: str
        startTime: str
        timeZone: str
        type: Literal[TriggerType.CRON]


    class azure.ai.projects.types.CustomGrammarFormatParam(TypedDict, total=False):
        key "definition": Required[str]
        key "syntax": Required[Union[str, GrammarSyntax1]]
        key "type": Required[Literal[CustomToolParamFormatType.GRAMMAR]]
        definition: str
        syntax: Union[str, GrammarSyntax1]
        type: Literal[CustomToolParamFormatType.GRAMMAR]


    class azure.ai.projects.types.CustomRoutineTrigger(TypedDict, total=False):
        key "event_name": str
        key "parameters": Required[dict[str, Any]]
        key "provider": Required[str]
        key "type": Required[Literal[RoutineTriggerType.CUSTOM]]
        event_name: str
        parameters: dict[str, Any]
        provider: str
        type: Literal[RoutineTriggerType.CUSTOM]


    class azure.ai.projects.types.CustomTextFormatParam(TypedDict, total=False):
        key "type": Required[Literal[CustomToolParamFormatType.TEXT]]
        type: Literal[CustomToolParamFormatType.TEXT]


    class azure.ai.projects.types.CustomToolParam(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "defer_loading": bool
        key "description": str
        key "format": ForwardRef('CustomToolParamFormat', module='types')
        key "name": Required[str]
        key "type": Required[Literal[ToolType.CUSTOM]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        defer_loading: bool
        description: str
        format: CustomToolParamFormat
        name: str
        type: Literal[ToolType.CUSTOM]


    class azure.ai.projects.types.CustomToolParamFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAMMAR = "grammar"
        TEXT = "text"


    class azure.ai.projects.types.DailyRecurrenceSchedule(TypedDict, total=False):
        key "hours": Required[list[int]]
        key "type": Required[Literal[RecurrenceType.DAILY]]
        hours: list[int]
        type: Literal[RecurrenceType.DAILY]


    class azure.ai.projects.types.DataGenerationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "finished_at": int
        key "id": Required[str]
        key "inputs": ForwardRef('DataGenerationJobInputs', module='types')
        key "result": ForwardRef('DataGenerationJobResult', module='types')
        key "status": Required[Union[str, JobStatus]]
        created_at: int
        error: ApiError
        finished_at: int
        id: str
        inputs: DataGenerationJobInputs
        result: DataGenerationJobResult
        status: Union[str, JobStatus]


    class azure.ai.projects.types.DataGenerationJobInputs(TypedDict, total=False):
        key "name": Required[str]
        key "options": Required[DataGenerationJobOptions]
        key "output_options": ForwardRef('DataGenerationJobOutputOptions', module='types')
        key "scenario": Required[Union[str, DataGenerationJobScenario]]
        key "sources": Required[list[DataGenerationJobSource]]
        name: str
        options: DataGenerationJobOptions
        output_options: DataGenerationJobOutputOptions
        scenario: Union[str, DataGenerationJobScenario]
        sources: list[DataGenerationJobSource]


    class azure.ai.projects.types.DataGenerationJobOutputOptions(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str
        tags: dict[str, str]


    class azure.ai.projects.types.DataGenerationJobOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATASET = "dataset"
        FILE = "file"


    class azure.ai.projects.types.DataGenerationJobResult(TypedDict, total=False):
        key "generated_samples": Required[int]
        key "token_usage": ForwardRef('DataGenerationTokenUsage', module='types')
        generated_samples: int
        outputs: list[DataGenerationJobOutput]
        token_usage: DataGenerationTokenUsage


    class azure.ai.projects.types.DataGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        FILE = "file"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.types.DataGenerationJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMPLE_QNA = "simple_qna"
        TASK_GENERATION = "task_generation"
        TOOL_USE = "tool_use"
        TRACES = "traces"


    class azure.ai.projects.types.DataGenerationModelOptions(TypedDict, total=False):
        key "model": Required[str]
        model: str


    class azure.ai.projects.types.DataGenerationTokenUsage(TypedDict, total=False):
        key "completion_tokens": Required[int]
        key "prompt_tokens": Required[int]
        key "total_tokens": Required[int]
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int


    class azure.ai.projects.types.DatasetDataGenerationJobOutput(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": str
        key "type": Required[Literal[DataGenerationJobOutputType.DATASET]]
        key "version": str
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[DataGenerationJobOutputType.DATASET]
        version: str


    class azure.ai.projects.types.DatasetEvaluatorGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "type": Required[Literal[EvaluatorGenerationJobSourceType.DATASET]]
        key "version": str
        description: str
        name: str
        type: Literal[EvaluatorGenerationJobSourceType.DATASET]
        version: str


    class azure.ai.projects.types.DatasetReference(TypedDict, total=False):
        key "name": Required[str]
        key "version": Required[str]
        name: str
        version: str


    class azure.ai.projects.types.DatasetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.ai.projects.types.DeleteScopeRequest(TypedDict, total=False):
        key "scope": Required[str]
        scope: str


    class azure.ai.projects.types.Dimension(TypedDict, total=False):
        key "always_applicable": bool
        key "description": Required[str]
        key "id": Required[str]
        key "weight": Required[int]
        always_applicable: bool
        description: str
        id: str
        weight: int


    class azure.ai.projects.types.DispatchRoutineAsyncRequest(TypedDict, total=False):
        key "payload": ForwardRef('RoutineDispatchPayload', module='types')
        payload: RoutineDispatchPayload


    class azure.ai.projects.types.EmbeddingConfiguration(TypedDict, total=False):
        key "embeddingField": Required[str]
        key "modelDeploymentName": Required[str]
        embeddingField: str
        modelDeploymentName: str


    class azure.ai.projects.types.EmptyModelParam(TypedDict, total=False):


    class azure.ai.projects.types.EndpointBasedEvaluatorDefinition(TypedDict, total=False):
        key "connection_name": Required[str]
        key "type": Required[Literal[EvaluatorDefinitionType.ENDPOINT]]
        connection_name: str
        data_schema: dict[str, Any]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.ENDPOINT]


    class azure.ai.projects.types.EntraAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.ENTRA]]
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]


    class azure.ai.projects.types.EvalResult(TypedDict, total=False):
        key "name": Required[str]
        key "passed": Required[bool]
        key "score": Required[float]
        key "type": Required[str]
        name: str
        passed: bool
        score: float
        type: str


    class azure.ai.projects.types.EvalRunResultCompareItem(TypedDict, total=False):
        key "deltaEstimate": Required[float]
        key "pValue": Required[float]
        key "treatmentEffect": Required[Union[str, TreatmentEffectType]]
        key "treatmentRunId": Required[str]
        key "treatmentRunSummary": Required[EvalRunResultSummary]
        deltaEstimate: float
        pValue: float
        treatmentEffect: Union[str, TreatmentEffectType]
        treatmentRunId: str
        treatmentRunSummary: EvalRunResultSummary


    class azure.ai.projects.types.EvalRunResultComparison(TypedDict, total=False):
        key "baselineRunSummary": Required[EvalRunResultSummary]
        key "compareItems": Required[list[EvalRunResultCompareItem]]
        key "evaluator": Required[str]
        key "metric": Required[str]
        key "testingCriteria": Required[str]
        baselineRunSummary: EvalRunResultSummary
        compareItems: list[EvalRunResultCompareItem]
        evaluator: str
        metric: str
        testingCriteria: str


    class azure.ai.projects.types.EvalRunResultSummary(TypedDict, total=False):
        key "average": Required[float]
        key "runId": Required[str]
        key "sampleCount": Required[int]
        key "standardDeviation": Required[float]
        average: float
        runId: str
        sampleCount: int
        standardDeviation: float


    class azure.ai.projects.types.EvaluationComparisonInsightRequest(TypedDict, total=False):
        key "baselineRunId": Required[str]
        key "evalId": Required[str]
        key "treatmentRunIds": Required[list[str]]
        key "type": Required[Literal[InsightType.EVALUATION_COMPARISON]]
        baselineRunId: str
        evalId: str
        treatmentRunIds: list[str]
        type: Literal[InsightType.EVALUATION_COMPARISON]


    class azure.ai.projects.types.EvaluationComparisonInsightResult(TypedDict, total=False):
        key "comparisons": Required[list[EvalRunResultComparison]]
        key "method": Required[str]
        key "type": Required[Literal[InsightType.EVALUATION_COMPARISON]]
        comparisons: list[EvalRunResultComparison]
        method: str
        type: Literal[InsightType.EVALUATION_COMPARISON]


    class azure.ai.projects.types.EvaluationResultSample(TypedDict, total=False):
        key "correlationInfo": Required[dict[str, Any]]
        key "evaluationResult": Required[EvalResult]
        key "features": Required[dict[str, Any]]
        key "id": Required[str]
        key "type": Required[Literal[SampleType.EVALUATION_RESULT_SAMPLE]]
        correlationInfo: dict[str, Any]
        evaluationResult: EvalResult
        features: dict[str, Any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]


    class azure.ai.projects.types.EvaluationRule(TypedDict, total=False):
        key "action": Required[EvaluationRuleAction]
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "eventType": Required[Union[str, EvaluationRuleEventType]]
        key "filter": ForwardRef('EvaluationRuleFilter', module='types')
        key "id": Required[str]
        key "systemData": Required[dict[str, str]]
        action: EvaluationRuleAction
        description: str
        displayName: str
        enabled: bool
        eventType: Union[str, EvaluationRuleEventType]
        filter: EvaluationRuleFilter
        id: str
        systemData: dict[str, str]


    class azure.ai.projects.types.EvaluationRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS_EVALUATION = "continuousEvaluation"
        HUMAN_EVALUATION_PREVIEW = "humanEvaluationPreview"


    class azure.ai.projects.types.EvaluationRuleFilter(TypedDict, total=False):
        key "agentName": Required[str]
        agentName: str


    class azure.ai.projects.types.EvaluationRunClusterInsightRequest(TypedDict, total=False):
        key "evalId": Required[str]
        key "modelConfiguration": ForwardRef('InsightModelConfiguration', module='types')
        key "runIds": Required[list[str]]
        key "type": Required[Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]]
        evalId: str
        modelConfiguration: InsightModelConfiguration
        runIds: list[str]
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]


    class azure.ai.projects.types.EvaluationRunClusterInsightResult(TypedDict, total=False):
        key "clusterInsight": Required[ClusterInsightResult]
        key "type": Required[Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]]
        clusterInsight: ClusterInsightResult
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]


    class azure.ai.projects.types.EvaluationScheduleTask(TypedDict, total=False):
        key "evalId": Required[str]
        key "evalRun": Required[dict[str, Any]]
        key "type": Required[Literal[ScheduleTaskType.EVALUATION]]
        configuration: dict[str, str]
        evalId: str
        evalRun: dict[str, Any]
        type: Literal[ScheduleTaskType.EVALUATION]


    class azure.ai.projects.types.EvaluationTaxonomy(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": Required[str]
        key "taxonomyInput": Required[EvaluationTaxonomyInput]
        key "version": Required[str]
        description: str
        id: str
        name: str
        properties: dict[str, str]
        tags: dict[str, str]
        taxonomyCategories: list[TaxonomyCategory]
        taxonomyInput: EvaluationTaxonomyInput
        version: str


    class azure.ai.projects.types.EvaluationTaxonomyInput(TypedDict, total=False):
        key "riskCategories": Required[list[Union[str, RiskCategory]]]
        key "target": Required[EvaluationTarget]
        key "type": Required[Literal[EvaluationTaxonomyInputType.AGENT]]
        riskCategories: list[Union[str, RiskCategory]]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]


    class azure.ai.projects.types.EvaluationTaxonomyInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        POLICY = "policy"


    class azure.ai.projects.types.EvaluatorCredentialRequest(TypedDict, total=False):
        key "blob_uri": Required[str]
        blob_uri: str


    class azure.ai.projects.types.EvaluatorDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE = "code"
        ENDPOINT = "endpoint"
        OPENAI_GRADERS = "openai_graders"
        PROMPT = "prompt"
        PROMPT_AND_CODE = "prompt_and_code"
        RUBRIC = "rubric"
        SERVICE = "service"


    class azure.ai.projects.types.EvaluatorGenerationArtifacts(TypedDict, total=False):
        key "dataset": Required[DatasetReference]
        key "kinds": Required[list[str]]
        dataset: DatasetReference
        kinds: list[str]


    class azure.ai.projects.types.EvaluatorGenerationInputs(TypedDict, total=False):
        key "evaluator_description": str
        key "evaluator_display_name": str
        key "evaluator_name": Required[str]
        key "model": Required[str]
        key "sources": Required[list[EvaluatorGenerationJobSource]]
        evaluator_description: str
        evaluator_display_name: str
        evaluator_name: str
        model: str
        sources: list[EvaluatorGenerationJobSource]


    class azure.ai.projects.types.EvaluatorGenerationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "finished_at": int
        key "id": Required[str]
        key "inputs": ForwardRef('EvaluatorGenerationInputs', module='types')
        key "result": ForwardRef('EvaluatorVersion', module='types')
        key "status": Required[Union[str, JobStatus]]
        key "usage": ForwardRef('EvaluatorGenerationTokenUsage', module='types')
        created_at: int
        error: ApiError
        finished_at: int
        id: str
        input_quality_warnings: list[RubricGenerationInputQualityWarning]
        inputs: EvaluatorGenerationInputs
        result: EvaluatorVersion
        status: Union[str, JobStatus]
        usage: EvaluatorGenerationTokenUsage


    class azure.ai.projects.types.EvaluatorGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        DATASET = "dataset"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.types.EvaluatorGenerationTokenUsage(TypedDict, total=False):
        key "input_tokens": Required[int]
        key "output_tokens": Required[int]
        key "total_tokens": Required[int]
        input_tokens: int
        output_tokens: int
        total_tokens: int


    class azure.ai.projects.types.EvaluatorMetric(TypedDict, total=False):
        key "desirable_direction": Union[str, EvaluatorMetricDirection]
        key "is_primary": bool
        key "max_value": float
        key "min_value": float
        key "threshold": float
        key "type": Union[str, EvaluatorMetricType]
        desirable_direction: Union[str, EvaluatorMetricDirection]
        is_primary: bool
        max_value: float
        min_value: float
        threshold: float
        type: Union[str, EvaluatorMetricType]


    class azure.ai.projects.types.EvaluatorVersion(TypedDict, total=False):
        key "categories": Required[list[Union[str, EvaluatorCategory]]]
        key "created_at": Required[str]
        key "created_by": Required[str]
        key "definition": Required[EvaluatorDefinition]
        key "description": str
        key "display_name": str
        key "evaluator_type": Required[Union[str, EvaluatorType]]
        key "generation_artifacts": ForwardRef('EvaluatorGenerationArtifacts', module='types')
        key "generation_job_id": str
        key "id": str
        key "modified_at": Required[str]
        key "name": Required[str]
        key "version": Required[str]
        categories: list[Union[str, EvaluatorCategory]]
        created_at: str
        created_by: str
        definition: EvaluatorDefinition
        description: str
        display_name: str
        evaluator_type: Union[str, EvaluatorType]
        generation_artifacts: EvaluatorGenerationArtifacts
        generation_job_id: str
        id: str
        metadata: dict[str, str]
        modified_at: str
        name: str
        supported_evaluation_levels: list[Union[str, EvaluationLevel]]
        tags: dict[str, str]
        version: str
        warnings: list[Union[str, GenerationWarningType]]


    class azure.ai.projects.types.ExternalAgentDefinition(TypedDict, total=False):
        key "kind": Required[Literal[AgentKind.EXTERNAL]]
        key "otel_agent_id": str
        key "rai_config": ForwardRef('RaiConfig', module='types')
        kind: Literal[AgentKind.EXTERNAL]
        otel_agent_id: str
        rai_config: RaiConfig


    class azure.ai.projects.types.FabricDataAgentToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.projects.types.FabricIQPreviewTool(TypedDict, total=False):
        key "project_connection_id": Required[str]
        key "require_approval": Optional[Union[MCPToolRequireApproval, str]]
        key "server_label": str
        key "server_url": str
        key "type": Required[Literal[ToolType.FABRIC_IQ_PREVIEW]]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, str]
        server_label: str
        server_url: str
        type: Literal[ToolType.FABRIC_IQ_PREVIEW]


    class azure.ai.projects.types.FabricIQPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        key "require_approval": Optional[Union[MCPToolRequireApproval, str]]
        key "server_label": str
        key "server_url": str
        key "type": Required[Literal[ToolboxToolType.FABRIC_IQ_PREVIEW]]
        description: str
        name: str
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, str]
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FABRIC_IQ_PREVIEW]


    class azure.ai.projects.types.FieldMapping(TypedDict, total=False):
        key "contentFields": Required[list[str]]
        key "filepathField": str
        key "titleField": str
        key "urlField": str
        contentFields: list[str]
        filepathField: str
        metadataFields: list[str]
        titleField: str
        urlField: str
        vectorFields: list[str]


    class azure.ai.projects.types.FileDataGenerationJobOutput(TypedDict, total=False):
        key "filename": Required[str]
        key "id": Required[str]
        key "type": Required[Literal[DataGenerationJobOutputType.FILE]]
        filename: str
        id: str
        type: Literal[DataGenerationJobOutputType.FILE]


    class azure.ai.projects.types.FileDataGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "type": Required[Literal[DataGenerationJobSourceType.FILE]]
        description: str
        id: str
        type: Literal[DataGenerationJobSourceType.FILE]


    class azure.ai.projects.types.FileDatasetVersion(TypedDict, total=False):
        key "connectionName": str
        key "dataUri": Required[str]
        key "description": str
        key "id": str
        key "isReference": bool
        key "name": Required[str]
        key "type": Required[Literal[DatasetType.URI_FILE]]
        key "version": Required[str]
        connectionName: str
        dataUri: str
        description: str
        id: str
        isReference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FILE]
        version: str


    class azure.ai.projects.types.FileSearchTool(TypedDict, total=False):
        key "description": str
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "name": str
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal[ToolType.FILE_SEARCH]]
        key "vector_store_ids": Required[list[str]]
        description: str
        filters: Filters
        max_num_results: int
        name: str
        ranking_options: RankingOptions
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.FILE_SEARCH]
        vector_store_ids: list[str]


    class azure.ai.projects.types.FileSearchToolboxTool(TypedDict, total=False):
        key "description": str
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "name": str
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal[ToolboxToolType.FILE_SEARCH]]
        description: str
        filters: Filters
        max_num_results: int
        name: str
        ranking_options: RankingOptions
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FILE_SEARCH]
        vector_store_ids: list[str]


    class azure.ai.projects.types.FixedRatioVersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[VersionSelectorType.FIXED_RATIO]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.projects.types.FolderDatasetVersion(TypedDict, total=False):
        key "connectionName": str
        key "dataUri": Required[str]
        key "description": str
        key "id": str
        key "isReference": bool
        key "name": Required[str]
        key "type": Required[Literal[DatasetType.URI_FOLDER]]
        key "version": Required[str]
        connectionName: str
        dataUri: str
        description: str
        id: str
        isReference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FOLDER]
        version: str


    class azure.ai.projects.types.FoundryModelWarning(TypedDict, total=False):
        key "code": Union[str, FoundryModelWarningCode]
        key "message": str
        code: Union[str, FoundryModelWarningCode]
        message: str


    class azure.ai.projects.types.FunctionShellToolParam(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "description": str
        key "environment": Optional[FunctionShellToolParamEnvironment]
        key "name": str
        key "type": Required[Literal[ToolType.SHELL]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        description: str
        environment: FunctionShellToolParamEnvironment
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.SHELL]


    class azure.ai.projects.types.FunctionShellToolParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]]
        container_id: str
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]


    class azure.ai.projects.types.FunctionShellToolParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal[FunctionShellToolParamEnvironmentType.LOCAL]]
        skills: list[LocalSkillParam]
        type: Literal[FunctionShellToolParamEnvironmentType.LOCAL]


    class azure.ai.projects.types.FunctionShellToolParamEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_AUTO = "container_auto"
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.projects.types.FunctionTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "output_schema": Optional[dict[str, Any]]
        key "parameters": Required[Optional[dict[str, Any]]]
        key "strict": Required[Optional[bool]]
        key "type": Required[Literal[ToolType.FUNCTION]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        defer_loading: bool
        description: str
        name: str
        output_schema: dict[str, Any]
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]


    class azure.ai.projects.types.FunctionToolParam(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "output_schema": Optional[dict[str, Any]]
        key "parameters": Optional[EmptyModelParam]
        key "strict": Optional[bool]
        key "type": Required[Literal["function"]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        defer_loading: bool
        description: str
        name: str
        output_schema: dict[str, Any]
        parameters: EmptyModelParam
        strict: bool
        type: Literal[function]


    class azure.ai.projects.types.GenerateAgentRequest(TypedDict, total=False):
        key "kind": Required[Union[str, AgentKind]]
        kind: Union[str, AgentKind]


    class azure.ai.projects.types.GitHubIssueRoutineTrigger(TypedDict, total=False):
        key "connection_id": Required[str]
        key "issue_event": Required[Union[str, GitHubIssueEvent]]
        key "owner": Required[str]
        key "repository": Required[str]
        key "type": Required[Literal[RoutineTriggerType.GITHUB_ISSUE]]
        connection_id: str
        issue_event: Union[str, GitHubIssueEvent]
        owner: str
        repository: str
        type: Literal[RoutineTriggerType.GITHUB_ISSUE]


    class azure.ai.projects.types.HeaderTelemetryEndpointAuth(TypedDict, total=False):
        key "header_name": Required[str]
        key "secret_id": Required[str]
        key "secret_key": Required[str]
        key "type": Required[Literal[TelemetryEndpointAuthType.HEADER]]
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]


    class azure.ai.projects.types.HostedAgentDefinition(TypedDict, total=False):
        key "code_configuration": ForwardRef('CodeConfiguration', module='types')
        key "container_configuration": ForwardRef('ContainerConfiguration', module='types')
        key "cpu": Required[str]
        key "kind": Required[Literal[AgentKind.HOSTED]]
        key "memory": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "telemetry_config": ForwardRef('TelemetryConfig', module='types')
        code_configuration: CodeConfiguration
        container_configuration: ContainerConfiguration
        cpu: str
        environment_variables: dict[str, str]
        kind: Literal[AgentKind.HOSTED]
        memory: str
        protocol_versions: list[ProtocolVersionRecord]
        rai_config: RaiConfig
        telemetry_config: TelemetryConfig


    class azure.ai.projects.types.HourlyRecurrenceSchedule(TypedDict, total=False):
        key "type": Required[Literal[RecurrenceType.HOURLY]]
        type: Literal[RecurrenceType.HOURLY]


    class azure.ai.projects.types.HumanEvaluationPreviewRuleAction(TypedDict, total=False):
        key "templateId": Required[str]
        key "type": Required[Literal[EvaluationRuleActionType.HUMAN_EVALUATION_PREVIEW]]
        templateId: str
        type: Literal[EvaluationRuleActionType.HUMAN_EVALUATION_PREVIEW]


    class azure.ai.projects.types.HybridSearchOptions(TypedDict, total=False):
        key "embedding_weight": Required[float]
        key "text_weight": Required[float]
        embedding_weight: float
        text_weight: float


    class azure.ai.projects.types.ImageGenTool(TypedDict, total=False):
        key "action": Union[str, ImageGenAction]
        key "background": Literal["transparent", "opaque", "auto"]
        key "description": str
        key "input_fidelity": Optional[Union[str, InputFidelity]]
        key "input_image_mask": ForwardRef('ImageGenToolInputImageMask', module='types')
        key "model": Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]
        key "moderation": Literal["auto", "low"]
        key "name": str
        key "output_compression": int
        key "output_format": Literal["png", "webp", "jpeg"]
        key "partial_images": int
        key "quality": Literal["low", "medium", "high", "auto"]
        key "size": Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]
        key "type": Required[Literal[ToolType.IMAGE_GENERATION]]
        action: Union[str, ImageGenAction]
        background: Literal[transparent, opaque, auto]
        description: str
        input_fidelity: Union[str, InputFidelity]
        input_image_mask: ImageGenToolInputImageMask
        model: Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]
        moderation: Literal[auto, low]
        name: str
        output_compression: int
        output_format: Literal[png, webp, jpeg]
        partial_images: int
        quality: Literal[low, medium, high, auto]
        size: Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.IMAGE_GENERATION]


    class azure.ai.projects.types.ImageGenToolInputImageMask(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        file_id: str
        image_url: str


    class azure.ai.projects.types.IndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEARCH = "AzureSearch"
        COSMOS_DB = "CosmosDBNoSqlVectorStore"
        MANAGED_AZURE_SEARCH = "ManagedAzureSearch"


    class azure.ai.projects.types.InlineSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "source": Required[InlineSkillSourceParam]
        key "type": Required[Literal[ContainerSkillType.INLINE]]
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[ContainerSkillType.INLINE]


    class azure.ai.projects.types.InlineSkillSourceParam(TypedDict, total=False):
        key "data": Required[str]
        key "media_type": Required[Literal["application/zip"]]
        key "type": Required[Literal["base64"]]
        data: str
        media_type: Literal[application/zip]
        type: Literal[base64]


    class azure.ai.projects.types.Insight(TypedDict, total=False):
        key "displayName": Required[str]
        key "id": Required[str]
        key "metadata": Required[InsightsMetadata]
        key "request": Required[InsightRequest]
        key "result": ForwardRef('InsightResult', module='types')
        key "state": Required[Union[str, OperationState]]
        displayName: str
        id: str
        metadata: InsightsMetadata
        request: InsightRequest
        result: InsightResult
        state: Union[str, OperationState]


    class azure.ai.projects.types.InsightCluster(TypedDict, total=False):
        key "description": Required[str]
        key "id": Required[str]
        key "label": Required[str]
        key "suggestion": Required[str]
        key "suggestionTitle": Required[str]
        key "weight": Required[int]
        description: str
        id: str
        label: str
        samples: list[InsightSample]
        subClusters: list[InsightCluster]
        suggestion: str
        suggestionTitle: str
        weight: int


    class azure.ai.projects.types.InsightModelConfiguration(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        modelDeploymentName: str


    class azure.ai.projects.types.InsightSample(TypedDict, total=False):
        key "correlationInfo": Required[dict[str, Any]]
        key "evaluationResult": Required[EvalResult]
        key "features": Required[dict[str, Any]]
        key "id": Required[str]
        key "type": Required[Literal[SampleType.EVALUATION_RESULT_SAMPLE]]
        correlationInfo: dict[str, Any]
        evaluationResult: EvalResult
        features: dict[str, Any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]


    class azure.ai.projects.types.InsightScheduleTask(TypedDict, total=False):
        key "insight": Required[Insight]
        key "type": Required[Literal[ScheduleTaskType.INSIGHT]]
        configuration: dict[str, str]
        insight: Insight
        type: Literal[ScheduleTaskType.INSIGHT]


    class azure.ai.projects.types.InsightSummary(TypedDict, total=False):
        key "method": Required[str]
        key "sampleCount": Required[int]
        key "uniqueClusterCount": Required[int]
        key "uniqueSubclusterCount": Required[int]
        key "usage": Required[ClusterTokenUsage]
        method: str
        sampleCount: int
        uniqueClusterCount: int
        uniqueSubclusterCount: int
        usage: ClusterTokenUsage


    class azure.ai.projects.types.InsightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_CLUSTER_INSIGHT = "AgentClusterInsight"
        EVALUATION_COMPARISON = "EvaluationComparison"
        EVALUATION_RUN_CLUSTER_INSIGHT = "EvaluationRunClusterInsight"


    class azure.ai.projects.types.InsightsMetadata(TypedDict, total=False):
        key "completedAt": str
        key "createdAt": Required[str]
        completedAt: str
        createdAt: str


    class azure.ai.projects.types.InvocationsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.projects.types.InvocationsWsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.projects.types.InvokeAgentInvocationsApiDispatchPayload(TypedDict, total=False):
        key "input": Required[Any]
        key "type": Required[Literal[RoutineDispatchPayloadType.INVOKE_AGENT_INVOCATIONS_API]]
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_INVOCATIONS_API]


    class azure.ai.projects.types.InvokeAgentInvocationsApiRoutineAction(TypedDict, total=False):
        key "agent_endpoint_id": str
        key "agent_name": str
        key "input": Any
        key "session_id": str
        key "type": Required[Literal[RoutineActionType.INVOKE_AGENT_INVOCATIONS_API]]
        agent_endpoint_id: str
        agent_name: str
        input: Any
        session_id: str
        type: Literal[RoutineActionType.INVOKE_AGENT_INVOCATIONS_API]


    class azure.ai.projects.types.InvokeAgentResponsesApiDispatchPayload(TypedDict, total=False):
        key "input": Required[Any]
        key "type": Required[Literal[RoutineDispatchPayloadType.INVOKE_AGENT_RESPONSES_API]]
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_RESPONSES_API]


    class azure.ai.projects.types.InvokeAgentResponsesApiRoutineAction(TypedDict, total=False):
        key "agent_endpoint_id": str
        key "agent_name": str
        key "conversation": str
        key "input": Any
        key "type": Required[Literal[RoutineActionType.INVOKE_AGENT_RESPONSES_API]]
        agent_endpoint_id: str
        agent_name: str
        conversation: str
        input: Any
        type: Literal[RoutineActionType.INVOKE_AGENT_RESPONSES_API]


    class azure.ai.projects.types.ListMemoriesRequest(TypedDict, total=False):
        key "scope": Required[str]
        scope: str


    class azure.ai.projects.types.LlmGeneratedVoiceGreetingConfig(TypedDict, total=False):
        key "prompt": Required[str]
        key "tool_choice": ForwardRef('VoiceAgentToolChoice', module='types')
        key "type": Required[Literal["llm_generated"]]
        prompt: str
        tool_choice: VoiceAgentToolChoice
        type: Literal[llm_generated]


    class azure.ai.projects.types.LocalShellToolParam(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolType.LOCAL_SHELL]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.LOCAL_SHELL]


    class azure.ai.projects.types.LocalSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "path": Required[str]
        description: str
        name: str
        path: str


    class azure.ai.projects.types.LogProbProperties(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        bytes: list[int]
        logprob: float
        token: str


    class azure.ai.projects.types.LoraConfig(TypedDict, total=False):
        key "alpha": int
        key "dropout": float
        key "rank": int
        alpha: int
        dropout: float
        rank: int
        targetModules: list[str]


    class azure.ai.projects.types.MCPListToolsTool(TypedDict, total=False):
        key "annotations": Optional[MCPListToolsToolAnnotations]
        key "description": Optional[str]
        key "input_schema": Required[MCPListToolsToolInputSchema]
        key "name": Required[str]
        annotations: MCPListToolsToolAnnotations
        description: str
        input_schema: MCPListToolsToolInputSchema
        name: str


    class azure.ai.projects.types.MCPListToolsToolAnnotations(TypedDict, total=False):


    class azure.ai.projects.types.MCPListToolsToolInputSchema(TypedDict, total=False):


    class azure.ai.projects.types.MCPTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
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
        key "type": Required[Literal[ToolType.MCP]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
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
        tool_configs: dict[str, ToolConfig]
        tunnel_id: str
        type: Literal[ToolType.MCP]


    class azure.ai.projects.types.MCPToolFilter(TypedDict, total=False):
        key "read_only": bool
        read_only: bool
        tool_names: list[str]


    class azure.ai.projects.types.MCPToolRequireApproval(TypedDict, total=False):
        key "always": ForwardRef('MCPToolFilter', module='types')
        key "never": ForwardRef('MCPToolFilter', module='types')
        always: MCPToolFilter
        never: MCPToolFilter


    class azure.ai.projects.types.MCPToolboxTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "connector_id": Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]
        key "defer_loading": bool
        key "description": str
        key "headers": Optional[dict[str, str]]
        key "name": str
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "tunnel_id": str
        key "type": Required[Literal[ToolboxToolType.MCP]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        connector_id: Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams,
        defer_loading: bool
        description: str
        headers: dict[str, str]
        name: str
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        tunnel_id: str
        type: Literal[ToolboxToolType.MCP]


    class azure.ai.projects.types.ManagedAgentIdentityBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.projects.types.ManagedAzureAISearchIndex(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": Required[str]
        key "type": Required[Literal[IndexType.MANAGED_AZURE_SEARCH]]
        key "vectorStoreId": Required[str]
        key "version": Required[str]
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.MANAGED_AZURE_SEARCH]
        vectorStoreId: str
        version: str


    class azure.ai.projects.types.McpProtocolConfiguration(TypedDict, total=False):


    class azure.ai.projects.types.MemorySearchOptions(TypedDict, total=False):
        key "max_memories": int
        max_memories: int


    class azure.ai.projects.types.MemorySearchPreviewTool(TypedDict, total=False):
        key "memory_store_name": Required[str]
        key "scope": Required[str]
        key "search_options": ForwardRef('MemorySearchOptions', module='types')
        key "type": Required[Literal[ToolType.MEMORY_SEARCH_PREVIEW]]
        key "update_delay": int
        memory_store_name: str
        scope: str
        search_options: MemorySearchOptions
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: int


    class azure.ai.projects.types.MemoryStoreDefaultDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal[MemoryStoreKind.DEFAULT]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: MemoryStoreDefaultOptions


    class azure.ai.projects.types.MemoryStoreDefaultOptions(TypedDict, total=False):
        key "chat_summary_enabled": Required[bool]
        key "default_ttl_seconds": str
        key "procedural_memory_enabled": bool
        key "user_profile_details": str
        key "user_profile_enabled": Required[bool]
        chat_summary_enabled: bool
        default_ttl_seconds: str
        procedural_memory_enabled: bool
        user_profile_details: str
        user_profile_enabled: bool


    class azure.ai.projects.types.MemoryStoreDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal[MemoryStoreKind.DEFAULT]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: MemoryStoreDefaultOptions


    class azure.ai.projects.types.MemoryStoreKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.ai.projects.types.Metadata(TypedDict, total=False):


    class azure.ai.projects.types.MicrosoftFabricPreviewTool(TypedDict, total=False):
        key "fabric_dataagent_preview": Required[FabricDataAgentToolParameters]
        key "type": Required[Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]]
        fabric_dataagent_preview: FabricDataAgentToolParameters
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]


    class azure.ai.projects.types.ModelCredentialRequest(TypedDict, total=False):
        key "blobUri": Required[str]
        blobUri: str


    class azure.ai.projects.types.ModelPendingUploadRequest(TypedDict, total=False):
        key "connectionName": str
        key "pendingUploadId": str
        key "pendingUploadType": Required[Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]]
        connectionName: str
        pendingUploadId: str
        pendingUploadType: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]


    class azure.ai.projects.types.ModelSamplingParams(TypedDict, total=False):
        key "max_completion_tokens": int
        key "seed": int
        key "temperature": float
        key "top_p": float
        max_completion_tokens: int
        seed: int
        temperature: float
        top_p: float


    class azure.ai.projects.types.ModelSourceData(TypedDict, total=False):
        key "jobId": str
        key "sourceType": Union[str, FoundryModelSourceType]
        jobId: str
        sourceType: Union[str, FoundryModelSourceType]


    class azure.ai.projects.types.ModelVersion(TypedDict, total=False):
        key "artifactProfile": ForwardRef('ArtifactProfile', module='types')
        key "baseModel": str
        key "blobUri": Required[str]
        key "description": str
        key "id": str
        key "loraConfig": ForwardRef('LoraConfig', module='types')
        key "name": Required[str]
        key "source": ForwardRef('ModelSourceData', module='types')
        key "version": Required[str]
        key "weightType": Union[str, FoundryModelWeightType]
        artifactProfile: ArtifactProfile
        baseModel: str
        blobUri: str
        description: str
        id: str
        loraConfig: LoraConfig
        name: str
        source: ModelSourceData
        tags: dict[str, str]
        version: str
        warnings: list[FoundryModelWarning]
        weightType: Union[str, FoundryModelWeightType]


    class azure.ai.projects.types.MonthlyRecurrenceSchedule(TypedDict, total=False):
        key "daysOfMonth": Required[list[int]]
        key "type": Required[Literal[RecurrenceType.MONTHLY]]
        daysOfMonth: list[int]
        type: Literal[RecurrenceType.MONTHLY]


    class azure.ai.projects.types.NamespaceToolParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "tools": Required[list[Union[FunctionToolParam, CustomToolParam]]]
        key "type": Required[Literal[ToolType.NAMESPACE]]
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[ToolType.NAMESPACE]


    class azure.ai.projects.types.OmitPropertiesRealtimeResponse1(TypedDict, total=False):
        key "conversation_id": str
        key "id": str
        key "max_output_tokens": Union[int, Literal["inf"]]
        key "metadata": Optional[Metadata]
        key "object": Literal["response"]
        key "status": Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]
        key "status_details": ForwardRef('RealtimeResponseStatusDetails', module='types')
        key "usage": ForwardRef('RealtimeResponseUsage', module='types')
        conversation_id: str
        id: str
        max_output_tokens: Union[int, Literal[inf]]
        metadata: Metadata
        object: Literal[response]
        output_modalities: list[Literal["text", "audio"]]
        status: Literal[completed, cancelled, failed, incomplete, in_progress]
        status_details: RealtimeResponseStatusDetails
        usage: RealtimeResponseUsage


    class azure.ai.projects.types.OneTimeTrigger(TypedDict, total=False):
        key "timeZone": str
        key "triggerAt": Required[str]
        key "type": Required[Literal[TriggerType.ONE_TIME]]
        timeZone: str
        triggerAt: str
        type: Literal[TriggerType.ONE_TIME]


    class azure.ai.projects.types.OpenApiAnonymousAuthDetails(TypedDict, total=False):
        key "type": Required[Literal[OpenApiAuthType.ANONYMOUS]]
        type: Literal[OpenApiAuthType.ANONYMOUS]


    class azure.ai.projects.types.OpenApiAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "anonymous"
        MANAGED_IDENTITY = "managed_identity"
        PROJECT_CONNECTION = "project_connection"


    class azure.ai.projects.types.OpenApiFunctionDefinition(TypedDict, total=False):
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


    class azure.ai.projects.types.OpenApiFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.projects.types.OpenApiManagedAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiManagedSecurityScheme]
        key "type": Required[Literal[OpenApiAuthType.MANAGED_IDENTITY]]
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[OpenApiAuthType.MANAGED_IDENTITY]


    class azure.ai.projects.types.OpenApiManagedSecurityScheme(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.ai.projects.types.OpenApiProjectConnectionAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiProjectConnectionSecurityScheme]
        key "type": Required[Literal[OpenApiAuthType.PROJECT_CONNECTION]]
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[OpenApiAuthType.PROJECT_CONNECTION]


    class azure.ai.projects.types.OpenApiProjectConnectionSecurityScheme(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.projects.types.OpenApiTool(TypedDict, total=False):
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal[ToolType.OPENAPI]]
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.OPENAPI]


    class azure.ai.projects.types.OpenApiToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal[ToolboxToolType.OPENAPI]]
        description: str
        name: str
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.OPENAPI]


    class azure.ai.projects.types.OptimizedAgentIdentifier(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        agent_name: str
        agent_version: str


    class azure.ai.projects.types.OtlpTelemetryEndpoint(TypedDict, total=False):
        key "auth": ForwardRef('TelemetryEndpointAuth', module='types')
        key "data": Required[list[Union[str, TelemetryDataKind]]]
        key "endpoint": Required[str]
        key "kind": Required[Literal[TelemetryEndpointKind.OTLP]]
        key "protocol": Required[Union[str, TelemetryTransportProtocol]]
        auth: TelemetryEndpointAuth
        data: list[Union[str, TelemetryDataKind]]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: Union[str, TelemetryTransportProtocol]


    class azure.ai.projects.types.PatchAgentObjectRequest(TypedDict, total=False):
        key "agent_card": ForwardRef('AgentCard', module='types')
        key "agent_endpoint": ForwardRef('AgentEndpointConfig', module='types')
        agent_card: AgentCard
        agent_endpoint: AgentEndpointConfig


    class azure.ai.projects.types.PendingUploadRequest(TypedDict, total=False):
        key "connectionName": str
        key "pendingUploadId": str
        key "pendingUploadType": Required[Literal[PendingUploadType.BLOB_REFERENCE]]
        connectionName: str
        pendingUploadId: str
        pendingUploadType: Literal[PendingUploadType.BLOB_REFERENCE]


    class azure.ai.projects.types.PendingUploadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_REFERENCE = "BlobReference"
        NONE = "None"
        TEMPORARY_BLOB_REFERENCE = "TemporaryBlobReference"


    class azure.ai.projects.types.PickPropertiesVoiceAudioConfig(TypedDict, total=False):
        key "output": ForwardRef('VoiceAudioOutputConfig', module='types')
        output: VoiceAudioOutputConfig


    class azure.ai.projects.types.ProgrammaticToolCallingParam(TypedDict, total=False):
        key "type": Required[Literal[ToolType.PROGRAMMATIC_TOOL_CALLING]]
        type: Literal[ToolType.PROGRAMMATIC_TOOL_CALLING]


    class azure.ai.projects.types.PromotionInfo(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": Required[str]
        key "promoted_at": Required[int]
        agent_name: str
        agent_version: str
        promoted_at: int


    class azure.ai.projects.types.PromptAgentDefinition(TypedDict, total=False):
        key "instructions": Optional[str]
        key "kind": Required[Literal[AgentKind.PROMPT]]
        key "model": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "reasoning": Optional[Reasoning]
        key "temperature": Optional[float]
        key "text": ForwardRef('PromptAgentDefinitionTextOptions', module='types')
        key "tool_choice": Union[str, ToolChoiceParam]
        key "top_p": Optional[float]
        instructions: str
        kind: Literal[AgentKind.PROMPT]
        model: str
        rai_config: RaiConfig
        reasoning: Reasoning
        structured_inputs: dict[str, StructuredInputDefinition]
        temperature: float
        text: PromptAgentDefinitionTextOptions
        tool_choice: Union[str, ToolChoiceParam]
        tools: list[Tool]
        top_p: float


    class azure.ai.projects.types.PromptAgentDefinitionTextOptions(TypedDict, total=False):
        key "format": ForwardRef('TextResponseFormat', module='types')
        format: TextResponseFormat


    class azure.ai.projects.types.PromptBasedEvaluatorDefinition(TypedDict, total=False):
        key "prompt_text": Required[str]
        key "type": Required[Literal[EvaluatorDefinitionType.PROMPT]]
        data_schema: dict[str, Any]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        prompt_text: str
        type: Literal[EvaluatorDefinitionType.PROMPT]


    class azure.ai.projects.types.PromptDataGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "prompt": Required[str]
        key "type": Required[Literal[DataGenerationJobSourceType.PROMPT]]
        description: str
        prompt: str
        type: Literal[DataGenerationJobSourceType.PROMPT]


    class azure.ai.projects.types.PromptEvaluatorGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "prompt": Required[str]
        key "type": Required[Literal[EvaluatorGenerationJobSourceType.PROMPT]]
        description: str
        prompt: str
        type: Literal[EvaluatorGenerationJobSourceType.PROMPT]


    class azure.ai.projects.types.ProtocolConfiguration(TypedDict, total=False):
        key "a2a": ForwardRef('A2AProtocolConfiguration', module='types')
        key "activity": ForwardRef('ActivityProtocolConfiguration', module='types')
        key "invocations": ForwardRef('InvocationsProtocolConfiguration', module='types')
        key "invocations_ws": ForwardRef('InvocationsWsProtocolConfiguration', module='types')
        key "mcp": ForwardRef('McpProtocolConfiguration', module='types')
        key "responses": ForwardRef('ResponsesProtocolConfiguration', module='types')
        a2a: A2AProtocolConfiguration
        activity: ActivityProtocolConfiguration
        invocations: InvocationsProtocolConfiguration
        invocations_ws: InvocationsWsProtocolConfiguration
        mcp: McpProtocolConfiguration
        responses: ResponsesProtocolConfiguration


    class azure.ai.projects.types.ProtocolVersionRecord(TypedDict, total=False):
        key "protocol": Required[Union[str, AgentEndpointProtocol]]
        key "version": Required[str]
        protocol: Union[str, AgentEndpointProtocol]
        version: str


    class azure.ai.projects.types.RaiConfig(TypedDict, total=False):
        key "rai_policy_name": Required[str]
        rai_policy_name: str


    class azure.ai.projects.types.RankingOptions(TypedDict, total=False):
        key "hybrid_search": ForwardRef('HybridSearchOptions', module='types')
        key "ranker": Union[str, RankerVersionType]
        key "score_threshold": float
        hybrid_search: HybridSearchOptions
        ranker: Union[str, RankerVersionType]
        score_threshold: float


    class azure.ai.projects.types.RealtimeAudioFormatsAudioPcm(TypedDict, total=False):
        key "rate": Literal[24000]
        key "type": Required[Literal[RealtimeAudioFormatsType.AUDIO_PCM]]
        rate: Literal[24000]
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCM]


    class azure.ai.projects.types.RealtimeAudioFormatsAudioPcma(TypedDict, total=False):
        key "type": Required[Literal[RealtimeAudioFormatsType.AUDIO_PCMA]]
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMA]


    class azure.ai.projects.types.RealtimeAudioFormatsAudioPcmu(TypedDict, total=False):
        key "type": Required[Literal[RealtimeAudioFormatsType.AUDIO_PCMU]]
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMU]


    class azure.ai.projects.types.RealtimeAudioFormatsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO_PCM = "audio/pcm"
        AUDIO_PCMA = "audio/pcma"
        AUDIO_PCMU = "audio/pcmu"


    class azure.ai.projects.types.RealtimeClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATE = "conversation.item.create"
        CONVERSATION_ITEM_DELETE = "conversation.item.delete"
        CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
        CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
        INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
        INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
        INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
        OUTPUT_AUDIO_BUFFER_CLEAR = "output_audio_buffer.clear"
        RESPONSE_CANCEL = "response.cancel"
        RESPONSE_CREATE = "response.create"
        SESSION_UPDATE = "session.update"


    class azure.ai.projects.types.RealtimeConversationItemFunctionCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": str
        key "id": str
        key "name": Required[str]
        key "object": Literal["item"]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[RealtimeConversationItemType.FUNCTION_CALL]]
        arguments: str
        call_id: str
        id: str
        name: str
        object: Literal[item]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL]


    class azure.ai.projects.types.RealtimeConversationItemFunctionCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "object": Literal["item"]
        key "output": Required[str]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]]
        call_id: str
        id: str
        object: Literal[item]
        output: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.projects.types.RealtimeConversationItemMessageAssistant(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageAssistantContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.ASSISTANT]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageAssistantContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.projects.types.RealtimeConversationItemMessageAssistantContent(TypedDict, total=False):
        key "audio": str
        key "text": str
        key "transcript": str
        key "type": Literal["output_text", "output_audio"]
        audio: str
        text: str
        transcript: str
        type: Literal[output_text, output_audio]


    class azure.ai.projects.types.RealtimeConversationItemMessageSystem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageSystemContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.SYSTEM]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageSystemContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.projects.types.RealtimeConversationItemMessageSystemContent(TypedDict, total=False):
        key "text": str
        key "type": Literal["input_text"]
        text: str
        type: Literal[input_text]


    class azure.ai.projects.types.RealtimeConversationItemMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.projects.types.RealtimeConversationItemMessageUser(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageUserContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.USER]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageUserContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.projects.types.RealtimeConversationItemMessageUserContent(TypedDict, total=False):
        key "audio": str
        key "detail": Literal["auto", "low", "high"]
        key "image_url": str
        key "text": str
        key "transcript": str
        key "type": Literal["input_text", "input_audio", "input_image"]
        audio: str
        detail: Literal[auto, low, high]
        image_url: str
        text: str
        transcript: str
        type: Literal[input_text, input_audio, input_image]


    class azure.ai.projects.types.RealtimeConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"


    class azure.ai.projects.types.RealtimeFunctionTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "parameters": ForwardRef('RealtimeFunctionToolParameters', module='types')
        key "type": Literal["function"]
        description: str
        name: str
        parameters: RealtimeFunctionToolParameters
        type: Literal[function]


    class azure.ai.projects.types.RealtimeFunctionToolParameters(TypedDict, total=False):


    class azure.ai.projects.types.RealtimeMCPApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.projects.types.RealtimeMCPApprovalResponse(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.projects.types.RealtimeMCPHTTPError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.HTTP_ERROR]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.HTTP_ERROR]


    class azure.ai.projects.types.RealtimeMCPListTools(TypedDict, total=False):
        key "id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]]
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]


    class azure.ai.projects.types.RealtimeMCPProtocolError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]


    class azure.ai.projects.types.RealtimeMCPToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_CALL]]
        approval_request_id: str
        arguments: str
        error: RealtimeMCPError
        id: str
        name: str
        output: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_CALL]


    class azure.ai.projects.types.RealtimeMCPToolExecutionError(TypedDict, total=False):
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]]
        message: str
        type: Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]


    class azure.ai.projects.types.RealtimeMcpErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP_ERROR = "http_error"
        PROTOCOL_ERROR = "protocol_error"
        TOOL_EXECUTION_ERROR = "tool_execution_error"


    class azure.ai.projects.types.RealtimeReasoning(TypedDict, total=False):
        key "effort": Union[str, RealtimeReasoningEffort]
        effort: Union[str, RealtimeReasoningEffort]


    class azure.ai.projects.types.RealtimeResponseStatusDetails(TypedDict, total=False):
        key "error": ForwardRef('RealtimeResponseStatusDetailsError', module='types')
        key "reason": Literal["turn_detected", "client_cancelled", "max_output_tokens", "content_filter"]
        key "type": Literal["completed", "cancelled", "failed", "incomplete"]
        error: RealtimeResponseStatusDetailsError
        reason: Literal[turn_detected, client_cancelled, max_output_tokens, content_filter]
        type: Literal[completed, cancelled, failed, incomplete]


    class azure.ai.projects.types.RealtimeResponseStatusDetailsError(TypedDict, total=False):
        key "code": str
        key "type": str
        code: str
        type: str


    class azure.ai.projects.types.RealtimeResponseUsage(TypedDict, total=False):
        key "input_token_details": ForwardRef('RealtimeResponseUsageInputTokenDetails', module='types')
        key "input_tokens": int
        key "output_token_details": ForwardRef('RealtimeResponseUsageOutputTokenDetails', module='types')
        key "output_tokens": int
        key "total_tokens": int
        input_token_details: RealtimeResponseUsageInputTokenDetails
        input_tokens: int
        output_token_details: RealtimeResponseUsageOutputTokenDetails
        output_tokens: int
        total_tokens: int


    class azure.ai.projects.types.RealtimeResponseUsageInputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "cached_tokens": int
        key "cached_tokens_details": ForwardRef('RealtimeResponseUsageInputTokenDetailsCachedTokensDetails', module='types')
        key "image_tokens": int
        key "text_tokens": int
        audio_tokens: int
        cached_tokens: int
        cached_tokens_details: RealtimeResponseUsageInputTokenDetailsCachedTokensDetails
        image_tokens: int
        text_tokens: int


    class azure.ai.projects.types.RealtimeResponseUsageInputTokenDetailsCachedTokensDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "image_tokens": int
        key "text_tokens": int
        audio_tokens: int
        image_tokens: int
        text_tokens: int


    class azure.ai.projects.types.RealtimeResponseUsageOutputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "text_tokens": int
        audio_tokens: int
        text_tokens: int


    class azure.ai.projects.types.RealtimeServerEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[RealtimeServerEventResponseContentPartAddedPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]


    class azure.ai.projects.types.RealtimeServerEventConversationItemInputAudioTranscriptionFailedError(TypedDict, total=False):
        key "code": str
        key "message": str
        key "param": str
        key "type": str
        code: str
        message: str
        param: str
        type: str


    class azure.ai.projects.types.RealtimeServerEventError(TypedDict, total=False):
        key "error": Required[RealtimeServerEventErrorError]
        key "event_id": Required[str]
        key "type": Required[Literal["error"]]
        error: RealtimeServerEventErrorError
        event_id: str
        type: Literal[error]


    class azure.ai.projects.types.RealtimeServerEventErrorError(TypedDict, total=False):
        key "code": Optional[str]
        key "event_id": Optional[str]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": Required[str]
        code: str
        event_id: str
        message: str
        param: str
        type: str


    class azure.ai.projects.types.RealtimeServerEventRateLimitsUpdatedRateLimits(TypedDict, total=False):
        key "limit": int
        key "name": Literal["requests", "tokens"]
        key "remaining": int
        key "reset_seconds": float
        limit: int
        name: Literal[requests, tokens]
        remaining: int
        reset_seconds: float


    class azure.ai.projects.types.RealtimeServerEventResponseContentPartAdded(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[RealtimeServerEventResponseContentPartAddedPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]


    class azure.ai.projects.types.RealtimeServerEventResponseContentPartAddedPart(TypedDict, total=False):
        key "audio": str
        key "text": str
        key "transcript": str
        key "type": Literal["audio", "text"]
        audio: str
        text: str
        transcript: str
        type: Literal[audio, text]


    class azure.ai.projects.types.RealtimeServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_CREATED = "conversation.created"
        CONVERSATION_ITEM_ADDED = "conversation.item.added"
        CONVERSATION_ITEM_CREATED = "conversation.item.created"
        CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
        CONVERSATION_ITEM_DONE = "conversation.item.done"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT = "conversation.item.input_audio_transcription.segment"
        CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
        CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
        ERROR = "error"
        INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
        INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
        INPUT_AUDIO_BUFFER_DTMF_EVENT_RECEIVED = "input_audio_buffer.dtmf_event_received"
        INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
        INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
        INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED = "input_audio_buffer.timeout_triggered"
        MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
        MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
        MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
        OUTPUT_AUDIO_BUFFER_CLEARED = "output_audio_buffer.cleared"
        OUTPUT_AUDIO_BUFFER_STARTED = "output_audio_buffer.started"
        OUTPUT_AUDIO_BUFFER_STOPPED = "output_audio_buffer.stopped"
        RATE_LIMITS_UPDATED = "rate_limits.updated"
        RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
        RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
        RESPONSE_CREATED = "response.created"
        RESPONSE_DONE = "response.done"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
        RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
        RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
        RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
        RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
        RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
        RESPONSE_OUTPUT_AUDIO_DELTA = "response.output_audio.delta"
        RESPONSE_OUTPUT_AUDIO_DONE = "response.output_audio.done"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA = "response.output_audio_transcript.delta"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE = "response.output_audio_transcript.done"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        SESSION_CREATED = "session.created"
        SESSION_UPDATED = "session.updated"


    class azure.ai.projects.types.Reasoning(TypedDict, total=False):
        key "context": Optional[Literal["auto", "current_turn", "all_turns"]]
        key "effort": Optional[Union[str, ReasoningEffort]]
        key "generate_summary": Optional[Literal["auto", "concise", "detailed"]]
        key "mode": Union[str, ReasoningModeEnum]
        key "summary": Optional[Literal["auto", "concise", "detailed"]]
        context: Literal[auto, current_turn, all_turns]
        effort: Union[str, ReasoningEffort]
        generate_summary: Literal[auto, concise, detailed]
        mode: Union[str, ReasoningModeEnum]
        summary: Literal[auto, concise, detailed]


    class azure.ai.projects.types.RecurrenceTrigger(TypedDict, total=False):
        key "endTime": str
        key "interval": Required[int]
        key "schedule": Required[RecurrenceSchedule]
        key "startTime": str
        key "timeZone": str
        key "type": Required[Literal[TriggerType.RECURRENCE]]
        endTime: str
        interval: int
        schedule: RecurrenceSchedule
        startTime: str
        timeZone: str
        type: Literal[TriggerType.RECURRENCE]


    class azure.ai.projects.types.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.ai.projects.types.RedTeam(TypedDict, total=False):
        key "applicationScenario": str
        key "displayName": str
        key "id": Required[str]
        key "numTurns": int
        key "simulationOnly": bool
        key "status": str
        key "target": Required[RedTeamTargetConfig]
        applicationScenario: str
        attackStrategies: list[Union[str, AttackStrategy]]
        displayName: str
        id: str
        numTurns: int
        properties: dict[str, str]
        riskCategories: list[Union[str, RiskCategory]]
        simulationOnly: bool
        status: str
        tags: dict[str, str]
        target: RedTeamTargetConfig


    class azure.ai.projects.types.RedTeamTargetConfig(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        key "type": Required[Literal["AzureOpenAIModel"]]
        modelDeploymentName: str
        type: Literal[AzureOpenAIModel]


    class azure.ai.projects.types.ReminderPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.REMINDER_PREVIEW]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.REMINDER_PREVIEW]


    class azure.ai.projects.types.ResponsesProtocolConfiguration(TypedDict, total=False):


    class azure.ai.projects.types.RoutineActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.types.RoutineDispatchPayloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.types.RoutineTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        GITHUB_ISSUE = "github_issue"
        SCHEDULE = "schedule"
        TIMER = "timer"


    class azure.ai.projects.types.RubricBasedEvaluatorDefinition(TypedDict, total=False):
        key "dimensions": Required[list[Dimension]]
        key "pass_threshold": float
        key "type": Required[Literal[EvaluatorDefinitionType.RUBRIC]]
        data_schema: dict[str, Any]
        dimensions: list[Dimension]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        pass_threshold: float
        type: Literal[EvaluatorDefinitionType.RUBRIC]


    class azure.ai.projects.types.RubricGenerationInputQualityWarning(TypedDict, total=False):
        key "code": Required[Union[str, RubricGenerationInputQualityWarningCode]]
        key "message": Required[str]
        key "severity": Required[Union[str, RubricGenerationInputQualityWarningSeverity]]
        key "source": Required[Union[str, RubricGenerationInputQualityWarningSource]]
        key "source_index": int
        code: Union[str, RubricGenerationInputQualityWarningCode]
        message: str
        severity: Union[str, RubricGenerationInputQualityWarningSeverity]
        source: Union[str, RubricGenerationInputQualityWarningSource]
        source_index: int


    class azure.ai.projects.types.SampleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION_RESULT_SAMPLE = "EvaluationResultSample"


    class azure.ai.projects.types.Schedule(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "id": Required[str]
        key "provisioningStatus": Union[str, ScheduleProvisioningStatus]
        key "systemData": Required[dict[str, str]]
        key "task": Required[ScheduleTask]
        key "trigger": Required[Trigger]
        description: str
        displayName: str
        enabled: bool
        id: str
        properties: dict[str, str]
        provisioningStatus: Union[str, ScheduleProvisioningStatus]
        systemData: dict[str, str]
        tags: dict[str, str]
        task: ScheduleTask
        trigger: Trigger


    class azure.ai.projects.types.ScheduleRoutineTrigger(TypedDict, total=False):
        key "cron_expression": Required[str]
        key "time_zone": Required[str]
        key "type": Required[Literal[RoutineTriggerType.SCHEDULE]]
        cron_expression: str
        time_zone: str
        type: Literal[RoutineTriggerType.SCHEDULE]


    class azure.ai.projects.types.ScheduleTaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION = "Evaluation"
        INSIGHT = "Insight"


    class azure.ai.projects.types.SearchMemoriesRequest(TypedDict, total=False):
        key "options": ForwardRef('MemorySearchOptions', module='types')
        key "previous_search_id": str
        key "scope": Required[str]
        items: list[dict[str, Any]]
        options: MemorySearchOptions
        previous_search_id: str
        scope: str


    class azure.ai.projects.types.SharepointGroundingToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.projects.types.SharepointPreviewTool(TypedDict, total=False):
        key "sharepoint_grounding_preview": Required[SharepointGroundingToolParameters]
        key "type": Required[Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]]
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]


    class azure.ai.projects.types.SimpleQnADataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[DataGenerationJobType.SIMPLE_QNA]]
        max_samples: int
        model_options: DataGenerationModelOptions
        question_types: list[Union[str, SimpleQnAFineTuningQuestionType]]
        train_split: float
        type: Literal[DataGenerationJobType.SIMPLE_QNA]


    class azure.ai.projects.types.SkillInlineContent(TypedDict, total=False):
        key "compatibility": str
        key "description": Required[str]
        key "instructions": Required[str]
        key "license": str
        allowed_tools: list[str]
        compatibility: str
        description: str
        instructions: str
        license: str
        metadata: dict[str, str]


    class azure.ai.projects.types.SkillReferenceParam(TypedDict, total=False):
        key "skill_id": Required[str]
        key "type": Required[Literal[ContainerSkillType.SKILL_REFERENCE]]
        key "version": str
        skill_id: str
        type: Literal[ContainerSkillType.SKILL_REFERENCE]
        version: str


    class azure.ai.projects.types.SpecificApplyPatchParam(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.APPLY_PATCH]]
        type: Literal[ToolChoiceParamType.APPLY_PATCH]


    class azure.ai.projects.types.SpecificFunctionShellParam(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.SHELL]]
        type: Literal[ToolChoiceParamType.SHELL]


    class azure.ai.projects.types.SpecificProgrammaticToolCallingParam(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.PROGRAMMATIC_TOOL_CALLING]]
        type: Literal[ToolChoiceParamType.PROGRAMMATIC_TOOL_CALLING]


    class azure.ai.projects.types.StructuredInputDefinition(TypedDict, total=False):
        key "default_value": Any
        key "description": str
        key "required": bool
        default_value: Any
        description: str
        required: bool
        schema: dict[str, Any]


    class azure.ai.projects.types.StructuredOutputDefinition(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Required[Optional[bool]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool


    class azure.ai.projects.types.TaskGenerationDataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[DataGenerationJobType.TASK_GENERATION]]
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TASK_GENERATION]


    class azure.ai.projects.types.TaxonomyCategory(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        key "riskCategory": Required[Union[str, RiskCategory]]
        key "subCategories": Required[list[TaxonomySubCategory]]
        description: str
        id: str
        name: str
        properties: dict[str, str]
        riskCategory: Union[str, RiskCategory]
        subCategories: list[TaxonomySubCategory]


    class azure.ai.projects.types.TaxonomySubCategory(TypedDict, total=False):
        key "description": str
        key "enabled": Required[bool]
        key "id": Required[str]
        key "name": Required[str]
        description: str
        enabled: bool
        id: str
        name: str
        properties: dict[str, str]


    class azure.ai.projects.types.TelemetryConfig(TypedDict, total=False):
        key "endpoints": Required[list[TelemetryEndpoint]]
        endpoints: list[TelemetryEndpoint]


    class azure.ai.projects.types.TelemetryEndpoint(TypedDict, total=False):
        key "auth": ForwardRef('TelemetryEndpointAuth', module='types')
        key "data": Required[list[Union[str, TelemetryDataKind]]]
        key "endpoint": Required[str]
        key "kind": Required[Literal[TelemetryEndpointKind.OTLP]]
        key "protocol": Required[Union[str, TelemetryTransportProtocol]]
        auth: TelemetryEndpointAuth
        data: list[Union[str, TelemetryDataKind]]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: Union[str, TelemetryTransportProtocol]


    class azure.ai.projects.types.TelemetryEndpointAuth(TypedDict, total=False):
        key "header_name": Required[str]
        key "secret_id": Required[str]
        key "secret_key": Required[str]
        key "type": Required[Literal[TelemetryEndpointAuthType.HEADER]]
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]


    class azure.ai.projects.types.TelemetryEndpointAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEADER = "header"


    class azure.ai.projects.types.TelemetryEndpointKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTLP = "OTLP"


    class azure.ai.projects.types.TemplateVoiceGreetingConfig(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["template"]]
        text: str
        type: Literal[template]


    class azure.ai.projects.types.TextResponseFormatConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "json_object"
        JSON_SCHEMA = "json_schema"
        TEXT = "text"


    class azure.ai.projects.types.TextResponseFormatJsonObject(TypedDict, total=False):
        key "type": Required[Literal[TextResponseFormatConfigurationType.JSON_OBJECT]]
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]


    class azure.ai.projects.types.TextResponseFormatJsonSchema(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Optional[bool]
        key "type": Required[Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]


    class azure.ai.projects.types.TextResponseFormatText(TypedDict, total=False):
        key "type": Required[Literal[TextResponseFormatConfigurationType.TEXT]]
        type: Literal[TextResponseFormatConfigurationType.TEXT]


    class azure.ai.projects.types.TimerRoutineTrigger(TypedDict, total=False):
        key "at": int
        key "type": Required[Literal[RoutineTriggerType.TIMER]]
        at: int
        type: Literal[RoutineTriggerType.TIMER]


    class azure.ai.projects.types.ToolChoiceAllowed(TypedDict, total=False):
        key "mode": Required[Literal["auto", "required"]]
        key "tools": Required[list[dict[str, Any]]]
        key "type": Required[Literal[ToolChoiceParamType.ALLOWED_TOOLS]]
        mode: Literal[auto, required]
        tools: list[dict[str, Any]]
        type: Literal[ToolChoiceParamType.ALLOWED_TOOLS]


    class azure.ai.projects.types.ToolChoiceCodeInterpreter(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.CODE_INTERPRETER]]
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]


    class azure.ai.projects.types.ToolChoiceComputer(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.COMPUTER]]
        type: Literal[ToolChoiceParamType.COMPUTER]


    class azure.ai.projects.types.ToolChoiceComputerUse(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.COMPUTER_USE]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE]


    class azure.ai.projects.types.ToolChoiceComputerUsePreview(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]


    class azure.ai.projects.types.ToolChoiceCustom(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.CUSTOM]]
        name: str
        type: Literal[ToolChoiceParamType.CUSTOM]


    class azure.ai.projects.types.ToolChoiceFileSearch(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.FILE_SEARCH]]
        type: Literal[ToolChoiceParamType.FILE_SEARCH]


    class azure.ai.projects.types.ToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.FUNCTION]]
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]


    class azure.ai.projects.types.ToolChoiceImageGeneration(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.IMAGE_GENERATION]]
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]


    class azure.ai.projects.types.ToolChoiceMCP(TypedDict, total=False):
        key "name": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.MCP]]
        name: str
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]


    class azure.ai.projects.types.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_TOOLS = "allowed_tools"
        APPLY_PATCH = "apply_patch"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE = "computer_use"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        MCP = "mcp"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHELL = "shell"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WEB_SEARCH_PREVIEW_2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.projects.types.ToolChoiceWebSearchPreview(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]


    class azure.ai.projects.types.ToolChoiceWebSearchPreview20250311(TypedDict, total=False):
        key "type": Required[Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW_2025_03_11]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW_2025_03_11]


    class azure.ai.projects.types.ToolConfig(TypedDict, total=False):
        key "additional_search_text": str
        key "pin": bool
        additional_search_text: str
        pin: bool


    class azure.ai.projects.types.ToolDescription(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.ai.projects.types.ToolProjectConnection(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.projects.types.ToolSearchToolParam(TypedDict, total=False):
        key "description": Optional[str]
        key "execution": Union[str, ToolSearchExecutionType]
        key "parameters": Optional[EmptyModelParam]
        key "type": Required[Literal[ToolType.TOOL_SEARCH]]
        description: str
        execution: Union[str, ToolSearchExecutionType]
        parameters: EmptyModelParam
        type: Literal[ToolType.TOOL_SEARCH]


    class azure.ai.projects.types.ToolSearchToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.TOOLBOX_SEARCH]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH]


    class azure.ai.projects.types.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        APPLY_PATCH = "apply_patch"
        AZURE_AI_SEARCH = "azure_ai_search"
        AZURE_FUNCTION = "azure_function"
        BING_CUSTOM_SEARCH_PREVIEW = "bing_custom_search_preview"
        BING_GROUNDING = "bing_grounding"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CAPTURE_STRUCTURED_OUTPUTS = "capture_structured_outputs"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FABRIC_DATAAGENT_PREVIEW = "fabric_dataagent_preview"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        LOCAL_SHELL = "local_shell"
        MCP = "mcp"
        MEMORY_SEARCH_PREVIEW = "memory_search_preview"
        NAMESPACE = "namespace"
        OPENAPI = "openapi"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.types.ToolUseFineTuningDataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[DataGenerationJobType.TOOL_USE]]
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TOOL_USE]


    class azure.ai.projects.types.ToolboxPolicies(TypedDict, total=False):
        key "rai_config": ForwardRef('RaiConfig', module='types')
        rai_config: RaiConfig


    class azure.ai.projects.types.ToolboxSearchPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[ToolboxToolType.TOOLBOX_SEARCH_PREVIEW]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH_PREVIEW]


    class azure.ai.projects.types.ToolboxSkill(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["skill_reference"]]
        key "version": str
        name: str
        type: Literal[skill_reference]
        version: str


    class azure.ai.projects.types.ToolboxSkillReference(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["skill_reference"]]
        key "version": str
        name: str
        type: Literal[skill_reference]
        version: str


    class azure.ai.projects.types.ToolboxToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        AZURE_AI_SEARCH = "azure_ai_search"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CODE_INTERPRETER = "code_interpreter"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        MCP = "mcp"
        OPENAPI = "openapi"
        REMINDER_PREVIEW = "reminder_preview"
        TOOLBOX_SEARCH = "toolbox_search"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        WEB_SEARCH = "web_search"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.types.TracesDataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[DataGenerationJobType.TRACES]]
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TRACES]


    class azure.ai.projects.types.TracesDataGenerationJobSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "agent_version": str
        key "description": str
        key "end_time": int
        key "start_time": Required[int]
        key "type": Required[Literal[DataGenerationJobSourceType.TRACES]]
        agent_id: str
        agent_name: str
        agent_version: str
        description: str
        end_time: int
        start_time: int
        type: Literal[DataGenerationJobSourceType.TRACES]


    class azure.ai.projects.types.TracesEvaluatorGenerationJobSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "agent_version": str
        key "description": str
        key "end_time": int
        key "start_time": Required[int]
        key "type": Required[Literal[EvaluatorGenerationJobSourceType.TRACES]]
        agent_id: str
        agent_name: str
        agent_version: str
        description: str
        end_time: int
        start_time: int
        type: Literal[EvaluatorGenerationJobSourceType.TRACES]


    class azure.ai.projects.types.TranscriptTextUsageDuration(TypedDict, total=False):
        key "seconds": Required[str]
        key "type": Required[Literal[CreateTranscriptionResponseJsonUsageType.DURATION]]
        seconds: str
        type: Literal[CreateTranscriptionResponseJsonUsageType.DURATION]


    class azure.ai.projects.types.TranscriptTextUsageTokens(TypedDict, total=False):
        key "input_token_details": ForwardRef('TranscriptTextUsageTokensInputTokenDetails', module='types')
        key "input_tokens": Required[int]
        key "output_tokens": Required[int]
        key "total_tokens": Required[int]
        key "type": Required[Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]]
        input_token_details: TranscriptTextUsageTokensInputTokenDetails
        input_tokens: int
        output_tokens: int
        total_tokens: int
        type: Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]


    class azure.ai.projects.types.TranscriptTextUsageTokensInputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "text_tokens": int
        audio_tokens: int
        text_tokens: int


    class azure.ai.projects.types.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRON = "Cron"
        ONE_TIME = "OneTime"
        RECURRENCE = "Recurrence"


    class azure.ai.projects.types.UpdateMemoriesRequest(TypedDict, total=False):
        key "previous_update_id": str
        key "scope": Required[str]
        key "update_delay": int
        items: list[dict[str, Any]]
        previous_update_id: str
        scope: str
        update_delay: int


    class azure.ai.projects.types.UpdateMemoryRequest(TypedDict, total=False):
        key "content": Required[str]
        content: str


    class azure.ai.projects.types.UpdateMemoryStoreRequest(TypedDict, total=False):
        key "description": str
        description: str
        metadata: dict[str, str]


    class azure.ai.projects.types.UpdateModelVersionRequest(TypedDict, total=False):
        key "description": str
        description: str
        tags: dict[str, str]


    class azure.ai.projects.types.UpdateSkillRequest(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.projects.types.UpdateToolboxRequest(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.projects.types.UpdateToolboxRequest1(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.projects.types.VersionIndicator(TypedDict, total=False):
        key "agent_version": Required[str]
        key "type": Required[Literal[VersionIndicatorType.VERSION_REF]]
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]


    class azure.ai.projects.types.VersionIndicatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VERSION_REF = "version_ref"


    class azure.ai.projects.types.VersionRefIndicator(TypedDict, total=False):
        key "agent_version": Required[str]
        key "type": Required[Literal[VersionIndicatorType.VERSION_REF]]
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]


    class azure.ai.projects.types.VersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[VersionSelectorType.FIXED_RATIO]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.projects.types.VersionSelector(TypedDict, total=False):
        key "version_selection_rules": Required[list[VersionSelectionRule]]
        version_selection_rules: list[VersionSelectionRule]


    class azure.ai.projects.types.VersionSelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.ai.projects.types.VoiceAgentAnimationConfig(TypedDict, total=False):
        key "model_name": str
        model_name: str
        outputs: list[Union[str, VoiceAgentAnimationOutputType]]


    class azure.ai.projects.types.VoiceAgentAvatarIceServer(TypedDict, total=False):
        key "credential": Optional[str]
        key "urls": Required[list[str]]
        key "username": Optional[str]
        credential: str
        urls: list[str]
        username: str


    class azure.ai.projects.types.VoiceAgentAvatarScene(TypedDict, total=False):
        key "amplitude": float
        key "position_x": float
        key "position_y": float
        key "rotation_x": float
        key "rotation_y": float
        key "rotation_z": float
        key "zoom": float
        amplitude: float
        position_x: float
        position_y: float
        rotation_x: float
        rotation_y: float
        rotation_z: float
        zoom: float


    class azure.ai.projects.types.VoiceAgentAvatarVideoBackground(TypedDict, total=False):
        key "color": str
        key "image_url": str
        color: str
        image_url: str


    class azure.ai.projects.types.VoiceAgentAvatarVideoCrop(TypedDict, total=False):
        key "bottom_right": Required[list[int]]
        key "top_left": Required[list[int]]
        bottom_right: list[int]
        top_left: list[int]


    class azure.ai.projects.types.VoiceAgentAvatarVideoParams(TypedDict, total=False):
        key "background": ForwardRef('VoiceAgentAvatarVideoBackground', module='types')
        key "bitrate": int
        key "codec": Literal["h264"]
        key "crop": ForwardRef('VoiceAgentAvatarVideoCrop', module='types')
        key "gop_size": int
        key "resolution": ForwardRef('VoiceAgentAvatarVideoResolution', module='types')
        background: VoiceAgentAvatarVideoBackground
        bitrate: int
        codec: Literal[h264]
        crop: VoiceAgentAvatarVideoCrop
        gop_size: int
        resolution: VoiceAgentAvatarVideoResolution


    class azure.ai.projects.types.VoiceAgentAvatarVideoResolution(TypedDict, total=False):
        key "height": Required[int]
        key "width": Required[int]
        height: int
        width: int


    class azure.ai.projects.types.VoiceAgentClientEventConversationItemCreate(TypedDict, total=False):
        key "event_id": str
        key "item": Required[VoiceAgentCreateConversationItem]
        key "previous_item_id": str
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]]
        event_id: str
        item: VoiceAgentCreateConversationItem
        previous_item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]


    class azure.ai.projects.types.VoiceAgentClientEventConversationItemDelete(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]]
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]


    class azure.ai.projects.types.VoiceAgentClientEventConversationItemRetrieve(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]]
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]


    class azure.ai.projects.types.VoiceAgentClientEventConversationItemTruncate(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]]
        audio_end_ms: int
        content_index: int
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]


    class azure.ai.projects.types.VoiceAgentClientEventInputAudioBufferAppend(TypedDict, total=False):
        key "audio": Required[str]
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]]
        audio: str
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]


    class azure.ai.projects.types.VoiceAgentClientEventInputAudioBufferClear(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]]
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]


    class azure.ai.projects.types.VoiceAgentClientEventInputAudioBufferCommit(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]]
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]


    class azure.ai.projects.types.VoiceAgentClientEventOutputAudioBufferClear(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]]
        event_id: str
        type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]


    class azure.ai.projects.types.VoiceAgentClientEventResponseCancel(TypedDict, total=False):
        key "event_id": str
        key "response_id": str
        key "type": Required[Literal[RealtimeClientEventType.RESPONSE_CANCEL]]
        event_id: str
        response_id: str
        type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]


    class azure.ai.projects.types.VoiceAgentClientEventResponseCreate(TypedDict, total=False):
        key "event_id": str
        key "response": ForwardRef('VoiceAgentResponseCreateParams', module='types')
        key "type": Required[Literal[RealtimeClientEventType.RESPONSE_CREATE]]
        event_id: str
        response: VoiceAgentResponseCreateParams
        type: Literal[RealtimeClientEventType.RESPONSE_CREATE]


    class azure.ai.projects.types.VoiceAgentClientEventSessionAvatarConnect(TypedDict, total=False):
        key "client_sdp": Required[str]
        key "event_id": str
        key "type": Required[Literal["connect"]]
        client_sdp: str
        event_id: str
        type: Literal[connect]


    class azure.ai.projects.types.VoiceAgentClientEventSessionUpdate(TypedDict, total=False):
        key "event_id": str
        key "session": Required[VoiceAgentSessionUpdateConfig]
        key "type": Required[Literal[RealtimeClientEventType.SESSION_UPDATE]]
        event_id: str
        session: VoiceAgentSessionUpdateConfig
        type: Literal[RealtimeClientEventType.SESSION_UPDATE]


    class azure.ai.projects.types.VoiceAgentDefinition(TypedDict, total=False):
        key "audio": ForwardRef('VoiceAudioConfig', module='types')
        key "avatar": ForwardRef('VoiceAvatarConfig', module='types')
        key "greeting": ForwardRef('VoiceGreetingConfig', module='types')
        key "instructions": str
        key "interim_response": ForwardRef('VoiceAgentInterimResponse', module='types')
        key "kind": Required[Literal[AgentKind.VOICE]]
        key "max_output_tokens": ForwardRef('VoiceAgentMaxOutputTokens', module='types')
        key "model": Required[str]
        key "model_type": Required[Union[str, VoiceModelType]]
        key "parallel_tool_calls": bool
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "store": bool
        key "tool_choice": ForwardRef('VoiceAgentToolChoice', module='types')
        audio: VoiceAudioConfig
        avatar: VoiceAvatarConfig
        greeting: VoiceGreetingConfig
        include: list[Union[str, VoiceAgentSessionIncludeOption]]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        kind: Literal[AgentKind.VOICE]
        max_output_tokens: VoiceAgentMaxOutputTokens
        model: str
        model_type: Union[str, VoiceModelType]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        rai_config: RaiConfig
        store: bool
        structured_inputs: dict[str, StructuredInputDefinition]
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentTool]


    class azure.ai.projects.types.VoiceAgentEchoCancellation(TypedDict, total=False):
        key "channels": int
        key "reference_source": Union[str, VoiceAgentEchoCancellationReferenceSource]
        key "type": Required[Literal["server_echo_cancellation"]]
        channels: int
        reference_source: Union[str, VoiceAgentEchoCancellationReferenceSource]
        type: Literal[server_echo_cancellation]


    class azure.ai.projects.types.VoiceAgentFunctionTool(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": ForwardRef('RealtimeFunctionToolParameters', module='types')
        key "type": Required[Literal["function"]]
        description: str
        name: str
        parameters: RealtimeFunctionToolParameters
        type: Literal[function]


    class azure.ai.projects.types.VoiceAgentLlmInterimResponseConfig(TypedDict, total=False):
        key "instructions": str
        key "latency_threshold_ms": int
        key "max_completion_tokens": int
        key "model": str
        key "type": Required[Literal["llm_interim_response"]]
        instructions: str
        latency_threshold_ms: int
        max_completion_tokens: int
        model: str
        triggers: list[Union[str, VoiceAgentInterimResponseTrigger]]
        type: Literal[llm_interim_response]


    class azure.ai.projects.types.VoiceAgentMcpTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "defer_loading": bool
        key "headers": Optional[dict[str, str]]
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "response_scheduling": Union[str, VoiceAgentToolResponseScheduling]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "type": Required[Literal["mcp"]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        defer_loading: bool
        headers: dict[str, str]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        response_scheduling: Union[str, VoiceAgentToolResponseScheduling]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[mcp]


    class azure.ai.projects.types.VoiceAgentRealtimeResponse(OmitPropertiesRealtimeResponse1):
        key "audio": ForwardRef('VoiceResponseAudio', module='types')
        key "conversation_id": str
        key "id": str
        key "max_output_tokens": Union[int, Literal["inf"]]
        key "metadata": Optional[Metadata]
        key "object": Literal["response"]
        key "status": Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]
        key "status_details": ForwardRef('RealtimeResponseStatusDetails', module='types')
        key "usage": ForwardRef('RealtimeResponseUsage', module='types')
        audio: VoiceResponseAudio
        conversation_id: str
        id: str
        max_output_tokens: Union[int, Literal[inf]]
        metadata: Metadata
        object: Literal[response]
        output: list[VoiceAgentResponseItem]
        output_modalities: list[Literal["text", "audio"]]
        status: Literal[completed, cancelled, failed, incomplete, in_progress]
        status_details: RealtimeResponseStatusDetails
        usage: RealtimeResponseUsage


    class azure.ai.projects.types.VoiceAgentResponseCreateParams(TypedDict, total=False):
        key "audio": ForwardRef('PickPropertiesVoiceAudioConfig', module='types')
        key "conversation": Union[Literal["auto"], Literal["none"], str]
        key "instructions": str
        key "interim_response": Optional[VoiceAgentInterimResponse]
        key "max_output_tokens": Union[int, Literal["inf"]]
        key "metadata": Optional[Metadata]
        key "parallel_tool_calls": bool
        key "pre_generated_assistant_message": Optional[RealtimeConversationItemMessageAssistant]
        key "reasoning": ForwardRef('RealtimeReasoning', module='types')
        key "tool_choice": Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]
        audio: PickPropertiesVoiceAudioConfig
        conversation: Union[Literal[auto], Literal[none], str]
        input: list[RealtimeConversationItem]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: Union[int, Literal[inf]]
        metadata: Metadata
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        pre_generated_assistant_message: RealtimeConversationItemMessageAssistant
        reasoning: RealtimeReasoning
        tool_choice: Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]
        tools: list[Union[RealtimeFunctionTool, MCPTool]]


    class azure.ai.projects.types.VoiceAgentResponseEventContentPart(TypedDict, total=False):
        key "audio": str
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "text": str
        key "transcript": str
        key "type": Literal["audio", "text"]
        audio: str
        format: VoiceAudioFormat
        text: str
        transcript: str
        type: Literal[audio, text]


    class azure.ai.projects.types.VoiceAgentSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "eagerness": Literal["low", "medium", "high", "auto"]
        key "interrupt_response": bool
        key "type": Required[Literal[VoiceTurnDetectionType.SEMANTIC_VAD]]
        auto_truncate: bool
        create_response: bool
        eagerness: Literal[low, medium, high, auto]
        interrupt_response: bool
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemAdded(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemDeleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "logprobs": Optional[list[LogProbProperties]]
        key "phrases": Optional[list[VoiceAgentTranscriptionPhrase]]
        key "transcript": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]]
        key "usage": Required[Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]]
        content_index: int
        event_id: str
        item_id: str
        logprobs: list[LogProbProperties]
        phrases: list[VoiceAgentTranscriptionPhrase]
        transcript: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]
        usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionDelta(TypedDict, total=False):
        key "content_index": int
        key "delta": str
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "logprobs": Optional[list[LogProbProperties]]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        logprobs: list[LogProbProperties]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionFailed(TypedDict, total=False):
        key "content_index": Required[int]
        key "error": Required[RealtimeServerEventConversationItemInputAudioTranscriptionFailedError]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]]
        content_index: int
        error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionSegment(TypedDict, total=False):
        key "content_index": Required[int]
        key "end": Required[float]
        key "event_id": Required[str]
        key "id": Required[str]
        key "item_id": Required[str]
        key "speaker": Required[str]
        key "start": Required[float]
        key "text": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]]
        content_index: int
        end: float
        event_id: str
        id: str
        item_id: str
        speaker: str
        start: float
        text: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemRetrieved(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]]
        event_id: str
        item: VoiceAgentResponseItem
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]


    class azure.ai.projects.types.VoiceAgentServerEventConversationItemTruncated(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item": ForwardRef('RealtimeConversationItemMessageAssistant', module='types')
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]]
        audio_end_ms: int
        content_index: int
        event_id: str
        item: RealtimeConversationItemMessageAssistant
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]


    class azure.ai.projects.types.VoiceAgentServerEventInputAudioBufferCleared(TypedDict, total=False):
        key "event_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]]
        event_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]


    class azure.ai.projects.types.VoiceAgentServerEventInputAudioBufferCommitted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]]
        event_id: str
        item_id: str
        previous_item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]


    class azure.ai.projects.types.VoiceAgentServerEventInputAudioBufferSpeechStarted(TypedDict, total=False):
        key "audio_start_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]]
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]


    class azure.ai.projects.types.VoiceAgentServerEventInputAudioBufferSpeechStopped(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]]
        audio_end_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]


    class azure.ai.projects.types.VoiceAgentServerEventInputAudioBufferTimeoutTriggered(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "audio_start_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]]
        audio_end_ms: int
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]


    class azure.ai.projects.types.VoiceAgentServerEventMcpListToolsCompleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]


    class azure.ai.projects.types.VoiceAgentServerEventMcpListToolsFailed(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]


    class azure.ai.projects.types.VoiceAgentServerEventMcpListToolsInProgress(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]


    class azure.ai.projects.types.VoiceAgentServerEventOutputAudioBufferCleared(TypedDict, total=False):
        key "event_id": Required[str]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]]
        event_id: str
        response_id: str
        type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]


    class azure.ai.projects.types.VoiceAgentServerEventRateLimitsUpdated(TypedDict, total=False):
        key "event_id": Required[str]
        key "rate_limits": Required[list[RealtimeServerEventRateLimitsUpdatedRateLimits]]
        key "type": Required[Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]]
        event_id: str
        rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
        type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAnimationBlendshapesDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "frame_index": Required[int]
        key "frames": Required[list[list[float]]]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["delta"]]
        content_index: int
        event_id: str
        frame_index: int
        frames: list[list[float]]
        item_id: str
        output_index: int
        response_id: str
        type: Literal[delta]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAnimationBlendshapesDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAnimationVisemeDelta(TypedDict, total=False):
        key "audio_offset_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["delta"]]
        key "viseme_id": Required[int]
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[delta]
        viseme_id: int


    class azure.ai.projects.types.VoiceAgentServerEventResponseAnimationVisemeDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioTimestampDelta(TypedDict, total=False):
        key "audio_duration_ms": Required[int]
        key "audio_offset_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "text": Required[str]
        key "timestamp_type": Required[Literal["word"]]
        key "type": Required[Literal["delta"]]
        audio_duration_ms: int
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal[word]
        type: Literal[delta]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioTimestampDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioTranscriptDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventResponseAudioTranscriptDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "transcript": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        transcript: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseContentPartDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[VoiceAgentResponseEventContentPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: VoiceAgentResponseEventContentPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "response": Required[VoiceAgentRealtimeResponse]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CREATED]]
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_CREATED]


    class azure.ai.projects.types.VoiceAgentServerEventResponseDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "response": Required[VoiceAgentRealtimeResponse]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_DONE]]
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseFunctionCallArgumentsDelta(TypedDict, total=False):
        key "call_id": Required[str]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]]
        call_id: str
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventResponseFunctionCallArgumentsDone(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "name": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]]
        arguments: str
        call_id: str
        event_id: str
        item_id: str
        name: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseMcpCallArgumentsDelta(TypedDict, total=False):
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "obfuscation": Optional[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]]
        delta: str
        event_id: str
        item_id: str
        obfuscation: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventResponseMcpCallArgumentsDone(TypedDict, total=False):
        key "arguments": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]]
        arguments: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseMcpCallCompleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]


    class azure.ai.projects.types.VoiceAgentServerEventResponseMcpCallFailed(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]


    class azure.ai.projects.types.VoiceAgentServerEventResponseMcpCallInProgress(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]


    class azure.ai.projects.types.VoiceAgentServerEventResponseOutputItemAdded(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]]
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]


    class azure.ai.projects.types.VoiceAgentServerEventResponseOutputItemDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]]
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseTextDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]


    class azure.ai.projects.types.VoiceAgentServerEventResponseTextDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "text": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]


    class azure.ai.projects.types.VoiceAgentServerEventResponseVideoDelta(TypedDict, total=False):
        key "codec": Required[str]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal["delta"]]
        codec: str
        delta: str
        event_id: str
        output_index: int
        type: Literal[delta]


    class azure.ai.projects.types.VoiceAgentServerEventSessionAvatarConnecting(TypedDict, total=False):
        key "event_id": Required[str]
        key "server_sdp": Required[str]
        key "type": Required[Literal["connecting"]]
        event_id: str
        server_sdp: str
        type: Literal[connecting]


    class azure.ai.projects.types.VoiceAgentServerEventSessionAvatarSwitchToIdle(TypedDict, total=False):
        key "event_id": Required[str]
        key "turn_id": str
        key "type": Required[Literal["switch_to_idle"]]
        event_id: str
        turn_id: str
        type: Literal[switch_to_idle]


    class azure.ai.projects.types.VoiceAgentServerEventSessionAvatarSwitchToSpeaking(TypedDict, total=False):
        key "event_id": Required[str]
        key "turn_id": str
        key "type": Required[Literal["switch_to_speaking"]]
        event_id: str
        turn_id: str
        type: Literal[switch_to_speaking]


    class azure.ai.projects.types.VoiceAgentServerEventSessionCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "session": Required[VoiceAgentSessionResponseConfig]
        key "type": Required[Literal[RealtimeServerEventType.SESSION_CREATED]]
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_CREATED]


    class azure.ai.projects.types.VoiceAgentServerEventSessionUpdated(TypedDict, total=False):
        key "event_id": Required[str]
        key "session": Required[VoiceAgentSessionResponseConfig]
        key "type": Required[Literal[RealtimeServerEventType.SESSION_UPDATED]]
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_UPDATED]


    class azure.ai.projects.types.VoiceAgentServerEventWarning(TypedDict, total=False):
        key "event_id": Required[str]
        key "type": Required[Literal["warning"]]
        key "warning": Required[VoiceAgentServerEventWarningDetails]
        event_id: str
        type: Literal[warning]
        warning: VoiceAgentServerEventWarningDetails


    class azure.ai.projects.types.VoiceAgentServerEventWarningDetails(TypedDict, total=False):
        key "code": str
        key "message": Required[str]
        key "param": str
        code: str
        message: str
        param: str


    class azure.ai.projects.types.VoiceAgentSessionAvatarConfig(VoiceAvatarConfig):
        key "character": Required[str]
        key "customized": bool
        key "ice_servers": Optional[list[VoiceAgentAvatarIceServer]]
        key "model": str
        key "output_audit_audio": bool
        key "output_protocol": Union[str, VoiceAvatarOutputProtocol]
        key "scene": ForwardRef('VoiceAgentAvatarScene', module='types')
        key "style": str
        key "type": Required[Union[str, VoiceAvatarType]]
        key "video": ForwardRef('VoiceAgentAvatarVideoParams', module='types')
        character: str
        customized: bool
        ice_servers: list[VoiceAgentAvatarIceServer]
        model: str
        output_audit_audio: bool
        output_protocol: Union[str, VoiceAvatarOutputProtocol]
        scene: VoiceAgentAvatarScene
        style: str
        type: Union[str, VoiceAvatarType]
        video: VoiceAgentAvatarVideoParams


    class azure.ai.projects.types.VoiceAgentSessionResponseConfig(TypedDict, total=False):
        key "animation": ForwardRef('VoiceAgentAnimationConfig', module='types')
        key "audio": ForwardRef('VoiceAudioConfig', module='types')
        key "avatar": ForwardRef('VoiceAgentSessionAvatarConfig', module='types')
        key "expires_at": Optional[int]
        key "greeting": ForwardRef('VoiceGreetingConfig', module='types')
        key "id": Required[str]
        key "instructions": str
        key "interim_response": ForwardRef('VoiceAgentInterimResponse', module='types')
        key "max_output_tokens": ForwardRef('VoiceAgentMaxOutputTokens', module='types')
        key "model": Required[str]
        key "object": Required[Literal["session"]]
        key "parallel_tool_calls": bool
        key "reasoning": ForwardRef('RealtimeReasoning', module='types')
        key "temperature": float
        key "tool_choice": ForwardRef('VoiceAgentToolChoice', module='types')
        key "type": Required[Literal["realtime"]]
        animation: VoiceAgentAnimationConfig
        audio: VoiceAudioConfig
        avatar: VoiceAgentSessionAvatarConfig
        expires_at: int
        greeting: VoiceGreetingConfig
        id: str
        include: list[Union[str, VoiceAgentSessionIncludeOption]]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: VoiceAgentMaxOutputTokens
        metadata: dict[str, str]
        model: str
        object: Literal[session]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        reasoning: RealtimeReasoning
        temperature: float
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentTool]
        type: Literal[realtime]


    class azure.ai.projects.types.VoiceAgentSessionUpdateConfig(TypedDict, total=False):
        key "animation": ForwardRef('VoiceAgentAnimationConfig', module='types')
        key "audio": ForwardRef('VoiceAudioConfig', module='types')
        key "avatar": ForwardRef('VoiceAgentSessionAvatarConfig', module='types')
        key "greeting": ForwardRef('VoiceGreetingConfig', module='types')
        key "instructions": str
        key "interim_response": ForwardRef('VoiceAgentInterimResponse', module='types')
        key "max_output_tokens": ForwardRef('VoiceAgentMaxOutputTokens', module='types')
        key "parallel_tool_calls": bool
        key "reasoning": ForwardRef('RealtimeReasoning', module='types')
        key "temperature": float
        key "tool_choice": ForwardRef('VoiceAgentToolChoice', module='types')
        key "type": Required[Literal["realtime"]]
        animation: VoiceAgentAnimationConfig
        audio: VoiceAudioConfig
        avatar: VoiceAgentSessionAvatarConfig
        greeting: VoiceGreetingConfig
        include: list[Union[str, VoiceAgentSessionIncludeOption]]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: VoiceAgentMaxOutputTokens
        metadata: dict[str, str]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        reasoning: RealtimeReasoning
        temperature: float
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentTool]
        type: Literal[realtime]


    class azure.ai.projects.types.VoiceAgentStaticInterimResponseConfig(TypedDict, total=False):
        key "latency_threshold_ms": int
        key "type": Required[Literal["static_interim_response"]]
        latency_threshold_ms: int
        texts: list[str]
        triggers: list[Union[str, VoiceAgentInterimResponseTrigger]]
        type: Literal[static_interim_response]


    class azure.ai.projects.types.VoiceAgentTranscriptionPhrase(TypedDict, total=False):
        key "confidence": Optional[float]
        key "duration_milliseconds": Required[int]
        key "locale": Optional[str]
        key "offset_milliseconds": Required[int]
        key "text": Required[str]
        key "words": Optional[list[VoiceAgentTranscriptionWord]]
        confidence: float
        duration_milliseconds: int
        locale: str
        offset_milliseconds: int
        text: str
        words: list[VoiceAgentTranscriptionWord]


    class azure.ai.projects.types.VoiceAgentTranscriptionWord(TypedDict, total=False):
        key "duration_milliseconds": Required[int]
        key "offset_milliseconds": Required[int]
        key "text": Required[str]
        duration_milliseconds: int
        offset_milliseconds: int
        text: str


    class azure.ai.projects.types.VoiceAssistantMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageAssistantContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.ASSISTANT]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


    class azure.ai.projects.types.VoiceAudioConfig(TypedDict, total=False):
        key "input": ForwardRef('VoiceAudioInputConfig', module='types')
        key "output": ForwardRef('VoiceAudioOutputConfig', module='types')
        input: VoiceAudioInputConfig
        output: VoiceAudioOutputConfig


    class azure.ai.projects.types.VoiceAudioFormat(TypedDict, total=False):
        key "rate": int
        key "type": Required[Union[str, VoiceAudioFormatType]]
        rate: int
        type: Union[str, VoiceAudioFormatType]


    class azure.ai.projects.types.VoiceAudioInputConfig(TypedDict, total=False):
        key "echo_cancellation": Optional[VoiceAgentEchoCancellation]
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "noise_reduction": Optional[VoiceNoiseReduction]
        key "transcription": Optional[VoiceInputTranscription]
        key "turn_detection": Optional[VoiceAgentTurnDetection]
        echo_cancellation: VoiceAgentEchoCancellation
        format: VoiceAudioFormat
        noise_reduction: VoiceNoiseReduction
        transcription: VoiceInputTranscription
        turn_detection: VoiceAgentTurnDetection


    class azure.ai.projects.types.VoiceAudioOutputConfig(TypedDict, total=False):
        key "custom_lexicon_url": str
        key "custom_text_normalization_url": str
        key "custom_voice_endpoint_id": str
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "personal_voice_model": str
        key "pitch": str
        key "speed": float
        key "style": str
        key "voice": str
        key "voice_locale": str
        key "voice_temperature": float
        key "voice_type": str
        key "volume": str
        custom_lexicon_url: str
        custom_text_normalization_url: str
        custom_voice_endpoint_id: str
        format: VoiceAudioFormat
        output_audio_timestamp_types: list[Union[str, VoiceAudioTimestampType]]
        personal_voice_model: str
        pitch: str
        prefer_locales: list[str]
        speed: float
        style: str
        voice: str
        voice_locale: str
        voice_temperature: float
        voice_type: str
        volume: str


    class azure.ai.projects.types.VoiceAvatarConfig(TypedDict, total=False):
        key "character": Required[str]
        key "customized": bool
        key "model": str
        key "output_audit_audio": bool
        key "output_protocol": Union[str, VoiceAvatarOutputProtocol]
        key "scene": ForwardRef('VoiceAgentAvatarScene', module='types')
        key "style": str
        key "type": Required[Union[str, VoiceAvatarType]]
        key "video": ForwardRef('VoiceAgentAvatarVideoParams', module='types')
        character: str
        customized: bool
        model: str
        output_audit_audio: bool
        output_protocol: Union[str, VoiceAvatarOutputProtocol]
        scene: VoiceAgentAvatarScene
        style: str
        type: Union[str, VoiceAvatarType]
        video: VoiceAgentAvatarVideoParams


    class azure.ai.projects.types.VoiceAzureSemanticVadEnTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceEndOfUtteranceDetection]
        key "idle_timeout_ms": str
        key "interrupt_response": bool
        key "prefix_padding_ms": str
        key "remove_filler_words": bool
        key "silence_duration_ms": str
        key "speech_duration_ms": str
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        idle_timeout_ms: str
        interrupt_response: bool
        prefix_padding_ms: str
        remove_filler_words: bool
        silence_duration_ms: str
        speech_duration_ms: str
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]


    class azure.ai.projects.types.VoiceAzureSemanticVadMultilingualTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceEndOfUtteranceDetection]
        key "idle_timeout_ms": str
        key "interrupt_response": bool
        key "prefix_padding_ms": str
        key "remove_filler_words": bool
        key "silence_duration_ms": str
        key "speech_duration_ms": str
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        idle_timeout_ms: str
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: str
        remove_filler_words: bool
        silence_duration_ms: str
        speech_duration_ms: str
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]


    class azure.ai.projects.types.VoiceAzureSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceEndOfUtteranceDetection]
        key "idle_timeout_ms": str
        key "interrupt_response": bool
        key "prefix_padding_ms": str
        key "remove_filler_words": bool
        key "silence_duration_ms": str
        key "speech_duration_ms": str
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        idle_timeout_ms: str
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: str
        remove_filler_words: bool
        silence_duration_ms: str
        speech_duration_ms: str
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]


    class azure.ai.projects.types.VoiceConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.projects.types.VoiceEndOfUtteranceDetection(TypedDict, total=False):
        key "model": Required[Union[str, VoiceEndOfUtteranceDetectionModel]]
        key "threshold_level": Union[str, VoiceEndOfUtteranceThresholdLevel]
        key "timeout_ms": str
        model: Union[str, VoiceEndOfUtteranceDetectionModel]
        threshold_level: Union[str, VoiceEndOfUtteranceThresholdLevel]
        timeout_ms: str


    class azure.ai.projects.types.VoiceFunctionCallItem(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": str
        key "created_at": int
        key "id": str
        key "name": Required[str]
        key "object": Literal["item"]
        key "response_id": str
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.FUNCTION_CALL]]
        arguments: str
        call_id: str
        created_at: int
        id: str
        name: str
        object: Literal[item]
        response_id: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL]


    class azure.ai.projects.types.VoiceFunctionCallOutputItem(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_at": int
        key "id": str
        key "name": str
        key "object": Literal["item"]
        key "output": Required[str]
        key "response_id": str
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]]
        call_id: str
        created_at: int
        id: str
        name: str
        object: Literal[item]
        output: str
        response_id: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.projects.types.VoiceInputTranscription(TypedDict, total=False):
        key "delay": Literal["minimal", "low", "medium", "high", "xhigh"]
        key "language": str
        key "model": Required[Union[str, VoiceInputTranscriptionModel]]
        key "prompt": str
        custom_speech: dict[str, str]
        delay: Literal[minimal, low, medium, high, xhigh]
        language: str
        model: Union[str, VoiceInputTranscriptionModel]
        phrase_list: list[str]
        prompt: str


    class azure.ai.projects.types.VoiceMcpApprovalRequestItem(TypedDict, total=False):
        key "arguments": Required[str]
        key "created_at": int
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]]
        arguments: str
        created_at: int
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.projects.types.VoiceMcpApprovalResponseItem(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "created_at": int
        key "id": Required[str]
        key "reason": Optional[str]
        key "response_id": str
        key "type": Required[Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]]
        approval_request_id: str
        approve: bool
        created_at: int
        id: str
        reason: str
        response_id: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.projects.types.VoiceMcpCallItem(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "created_at": int
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[VoiceConversationItemType.MCP_CALL]]
        approval_request_id: str
        arguments: str
        created_at: int
        error: RealtimeMCPError
        id: str
        name: str
        output: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_CALL]


    class azure.ai.projects.types.VoiceMcpListToolsItem(TypedDict, total=False):
        key "created_at": int
        key "id": str
        key "response_id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[VoiceConversationItemType.MCP_LIST_TOOLS]]
        created_at: int
        id: str
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[VoiceConversationItemType.MCP_LIST_TOOLS]


    class azure.ai.projects.types.VoiceNoiseReduction(TypedDict, total=False):
        key "type": Required[Union[str, VoiceNoiseReductionType]]
        type: Union[str, VoiceNoiseReductionType]


    class azure.ai.projects.types.VoiceResponseAudio(TypedDict, total=False):
        key "output": ForwardRef('VoiceResponseAudioOutput', module='types')
        output: VoiceResponseAudioOutput


    class azure.ai.projects.types.VoiceResponseAudioOutput(TypedDict, total=False):
        key "format": ForwardRef('RealtimeAudioFormats', module='types')
        key "voice": str
        key "voice_locale": str
        key "voice_type": str
        format: RealtimeAudioFormats
        voice: str
        voice_locale: str
        voice_type: str


    class azure.ai.projects.types.VoiceServerVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceEndOfUtteranceDetection]
        key "idle_timeout_ms": Optional[int]
        key "interrupt_response": bool
        key "prefix_padding_ms": int
        key "silence_duration_ms": int
        key "speech_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.SERVER_VAD]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        idle_timeout_ms: int
        interrupt_response: bool
        prefix_padding_ms: int
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]


    class azure.ai.projects.types.VoiceSystemMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageSystemContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.SYSTEM]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


    class azure.ai.projects.types.VoiceSystemTool(TypedDict, total=False):
        key "description": str
        key "name": Required[Union[str, VoiceSystemToolName]]
        key "type": Required[Literal["system"]]
        description: str
        name: Union[str, VoiceSystemToolName]
        type: Literal[system]


    class azure.ai.projects.types.VoiceToolboxTool(TypedDict, total=False):
        key "response_scheduling": Union[str, VoiceAgentToolResponseScheduling]
        key "toolbox_name": Required[str]
        key "toolbox_version": Required[str]
        key "type": Required[Literal["toolbox"]]
        response_scheduling: Union[str, VoiceAgentToolResponseScheduling]
        toolbox_name: str
        toolbox_version: str
        type: Literal[toolbox]


    class azure.ai.projects.types.VoiceTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.projects.types.VoiceUserMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageUserContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.USER]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


    class azure.ai.projects.types.WebSearchApproximateLocation(TypedDict, total=False):
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


    class azure.ai.projects.types.WebSearchConfiguration(TypedDict, total=False):
        key "instance_name": Required[str]
        key "project_connection_id": Required[str]
        instance_name: str
        project_connection_id: str


    class azure.ai.projects.types.WebSearchPreviewTool(TypedDict, total=False):
        key "search_context_size": Union[str, SearchContextSize]
        key "type": Required[Literal[ToolType.WEB_SEARCH_PREVIEW]]
        key "user_location": Optional[ApproximateLocation]
        search_content_types: list[Union[str, SearchContentType]]
        search_context_size: Union[str, SearchContextSize]
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: ApproximateLocation


    class azure.ai.projects.types.WebSearchTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "description": str
        key "filters": Optional[WebSearchToolFilters]
        key "name": str
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[ToolType.WEB_SEARCH]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        description: str
        filters: WebSearchToolFilters
        name: str
        search_context_size: Literal[low, medium, high]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.WEB_SEARCH]
        user_location: WebSearchApproximateLocation


    class azure.ai.projects.types.WebSearchToolFilters(TypedDict, total=False):
        key "allowed_domains": Optional[list[str]]
        allowed_domains: list[str]


    class azure.ai.projects.types.WebSearchToolboxTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "description": str
        key "filters": Optional[WebSearchToolFilters]
        key "name": str
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[ToolboxToolType.WEB_SEARCH]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        description: str
        filters: WebSearchToolFilters
        name: str
        search_context_size: Literal[low, medium, high]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WEB_SEARCH]
        user_location: WebSearchApproximateLocation


    class azure.ai.projects.types.WeeklyRecurrenceSchedule(TypedDict, total=False):
        key "daysOfWeek": Required[list[Union[str, DayOfWeek]]]
        key "type": Required[Literal[RecurrenceType.WEEKLY]]
        daysOfWeek: list[Union[str, DayOfWeek]]
        type: Literal[RecurrenceType.WEEKLY]


    class azure.ai.projects.types.WorkIQPreviewTool(TypedDict, total=False):
        key "project_connection_id": Required[str]
        key "type": Required[Literal[ToolType.WORK_IQ_PREVIEW]]
        project_connection_id: str
        type: Literal[ToolType.WORK_IQ_PREVIEW]


    class azure.ai.projects.types.WorkIQPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        key "type": Required[Literal[ToolboxToolType.WORK_IQ_PREVIEW]]
        description: str
        name: str
        project_connection_id: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WORK_IQ_PREVIEW]


    class azure.ai.projects.types.WorkflowAgentDefinition(TypedDict, total=False):
        key "kind": Required[Literal[AgentKind.WORKFLOW]]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "workflow": str
        kind: Literal[AgentKind.WORKFLOW]
        rai_config: RaiConfig
        workflow: str


```