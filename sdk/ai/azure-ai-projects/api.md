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

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
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
        agents: AgentsOperations
        beta: BetaOperations
        connections: ConnectionsOperations
        datasets: DatasetsOperations
        deployments: DeploymentsOperations
        evaluation_rules: EvaluationRulesOperations
        indexes: IndexesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
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


namespace azure.ai.projects.aio.operations

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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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

        @distributed_trace_async
        async def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.aio.operations.BetaAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        async def create_optimization_job(
                self, 
                job: OptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        async def create_optimization_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        async def create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

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
            ) -> OptimizationJob: ...

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
            ) -> AsyncItemPaged[OptimizationJobListItem]: ...


    class azure.ai.projects.aio.operations.BetaDatasetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
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
                taxonomy: JSON, 
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
                taxonomy: JSON, 
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

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        async def create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
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
                evaluator_version: JSON, 
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
                credential_request: JSON, 
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
                pending_upload_request: JSON, 
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
                evaluator_version: JSON, 
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
                insight: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                credential_request: JSON, 
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
                model_version: JSON, 
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
                pending_upload_request: JSON, 
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
                model_version_update: JSON, 
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
                red_team: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                schedule: JSON, 
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
                body: JSON, 
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
                content: JSON, 
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
                body: JSON, 
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
                dataset_version: JSON, 
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
                pending_upload_request: JSON, 
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
                index: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                principal_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "external"
        HOSTED = "hosted"
        PROMPT = "prompt"
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
        type: Literal[ToolType.APPLY_PATCH]

        @overload
        def __init__(self) -> None: ...

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
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeInterpreterToolboxTool(ToolboxTool, discriminator='code_interpreter'):
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
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
        defer_loading: Optional[bool]
        description: Optional[str]
        format: Optional[CustomToolParamFormat]
        name: str
        type: Literal[ToolType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
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
        id: Optional[str]
        metadata: Optional[dict[str, str]]
        modified_at: datetime
        name: str
        supported_evaluation_levels: Optional[list[Union[str, EvaluationLevel]]]
        tags: Optional[dict[str, str]]
        version: str

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
        description: Optional[str]
        environment: Optional[FunctionShellToolParamEnvironment]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.SHELL]

        @overload
        def __init__(
                self, 
                *, 
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
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionToolParam(_Model):
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        parameters: Optional[EmptyModelParam]
        strict: Optional[bool]
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[EmptyModelParam] = ..., 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.ai.projects.models.MCPTool(Tool, discriminator='mcp'):
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
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
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
                tool_configs: Optional[dict[str, ToolConfig]] = ...
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
        type: Literal[ToolboxToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
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
                tool_configs: Optional[dict[str, ToolConfig]] = ...
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


    class azure.ai.projects.models.OptimizationAgentIdentifier(_Model):
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


    class azure.ai.projects.models.OptimizationCandidate(_Model):
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


    class azure.ai.projects.models.OptimizationDatasetCriterion(_Model):
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


    class azure.ai.projects.models.OptimizationDatasetInput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationDatasetInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.ai.projects.models.OptimizationDatasetItem(_Model):
        criteria: Optional[list[OptimizationDatasetCriterion]]
        desired_num_turns: Optional[int]
        ground_truth: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                criteria: Optional[list[OptimizationDatasetCriterion]] = ..., 
                desired_num_turns: Optional[int] = ..., 
                ground_truth: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationEvaluatorRef(_Model):
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


    class azure.ai.projects.models.OptimizationInlineDatasetInput(OptimizationDatasetInput, discriminator='inline'):
        dataset_items: list[OptimizationDatasetItem]
        type: Literal[OptimizationDatasetInputType.INLINE]

        @overload
        def __init__(
                self, 
                *, 
                dataset_items: list[OptimizationDatasetItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        id: str
        inputs: Optional[OptimizationJobInputs]
        progress: Optional[OptimizationJobProgress]
        result: Optional[OptimizationJobResult]
        status: Union[str, JobStatus]
        updated_at: datetime
        warnings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[OptimizationJobInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationJobInputs(_Model):
        agent: OptimizationAgentIdentifier
        evaluators: list[OptimizationEvaluatorRef]
        options: Optional[OptimizationOptions]
        train_dataset: OptimizationDatasetInput
        validation_dataset: Optional[OptimizationDatasetInput]

        @overload
        def __init__(
                self, 
                *, 
                agent: OptimizationAgentIdentifier, 
                evaluators: list[OptimizationEvaluatorRef], 
                options: Optional[OptimizationOptions] = ..., 
                train_dataset: OptimizationDatasetInput, 
                validation_dataset: Optional[OptimizationDatasetInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationJobListItem(_Model):
        agent: Optional[OptimizationAgentIdentifier]
        created_at: datetime
        error: Optional[ApiError]
        id: str
        progress: Optional[OptimizationJobProgress]
        status: Union[str, JobStatus]
        updated_at: datetime


    class azure.ai.projects.models.OptimizationJobProgress(_Model):
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


    class azure.ai.projects.models.OptimizationJobResult(_Model):
        baseline: Optional[str]
        best: Optional[str]
        candidates: Optional[list[OptimizationCandidate]]

        @overload
        def __init__(
                self, 
                *, 
                baseline: Optional[str] = ..., 
                best: Optional[str] = ..., 
                candidates: Optional[list[OptimizationCandidate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationOptions(_Model):
        eval_model: Optional[str]
        evaluation_level: Optional[Union[str, EvaluationLevel]]
        max_candidates: Optional[int]
        optimization_config: Optional[dict[str, Any]]
        optimization_model: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                eval_model: Optional[str] = ..., 
                evaluation_level: Optional[Union[str, EvaluationLevel]] = ..., 
                max_candidates: Optional[int] = ..., 
                optimization_config: Optional[dict[str, Any]] = ..., 
                optimization_model: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OptimizationReferenceDatasetInput(OptimizationDatasetInput, discriminator='reference'):
        name: str
        type: Literal[OptimizationDatasetInputType.REFERENCE]
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


    class azure.ai.projects.models.Reasoning(_Model):
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
        cached_tokens: int

        @overload
        def __init__(
                self, 
                *, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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

        @distributed_trace
        def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.operations.BetaAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        def create_optimization_job(
                self, 
                job: OptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        def create_optimization_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

        @overload
        def create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> OptimizationJob: ...

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
            ) -> OptimizationJob: ...

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
            ) -> ItemPaged[OptimizationJobListItem]: ...


    class azure.ai.projects.operations.BetaDatasetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
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
                taxonomy: JSON, 
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
                taxonomy: JSON, 
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

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        def create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
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
                evaluator_version: JSON, 
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
                credential_request: JSON, 
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
                pending_upload_request: JSON, 
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
                evaluator_version: JSON, 
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
                insight: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                credential_request: JSON, 
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
                model_version: JSON, 
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
                pending_upload_request: JSON, 
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
                model_version_update: JSON, 
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
                red_team: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                schedule: JSON, 
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
                body: JSON, 
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
                content: JSON, 
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
                body: JSON, 
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
                dataset_version: JSON, 
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
                pending_upload_request: JSON, 
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
                index: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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


```