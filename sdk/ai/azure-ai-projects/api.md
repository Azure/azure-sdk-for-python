```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


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
        async def create_version(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
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
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

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
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentVersionDetails]: ...


    class azure.ai.projects.aio.operations.BetaAgentsOperations(GeneratedBetaAgentsOperations):

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
                isolation_key: str, 
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
                isolation_key: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                isolation_key: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace_async
        async def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                isolation_key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_session_file(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_session_file(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace_async
        async def get_session_files(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionDirectoryListResponse: ...

        @distributed_trace_async
        async def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

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

        @overload
        async def patch_agent_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpoint] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def patch_agent_details(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def patch_agent_details(
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
                content_or_file_path: bytes | str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResponse: ...


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
                body: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: IO[bytes], 
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
                body: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
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
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

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
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorVersion]: ...

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

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

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


    class azure.ai.projects.aio.operations.BetaOperations(GeneratedBetaOperations):
        agents: BetaAgentsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        red_teams: BetaRedTeamsOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations
        toolboxes: BetaToolboxesOperations

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
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace_async
        async def create_from_package(
                self, 
                body: bytes, 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResponse: ...

        @distributed_trace_async
        async def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkillObject]: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...


    class azure.ai.projects.aio.operations.BetaToolboxesOperations:

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
                tools: List[Tool], 
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


namespace azure.ai.projects.models

    class azure.ai.projects.models.A2APreviewTool(Tool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        project_connection_id: Optional[str]
        type: Literal[ToolType.A2A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                project_connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        agent_endpoint: Optional[AgentEndpoint]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        id: str
        instance_identity: Optional[AgentIdentity]
        name: str
        object: Literal[AgentObjectType.AGENT]
        versions: AgentObjectVersions

        @overload
        def __init__(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpoint] = ..., 
                id: str, 
                name: str, 
                object: Literal[AgentObjectType.AGENT], 
                versions: AgentObjectVersions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpoint(_Model):
        authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]]
        protocols: Optional[list[Union[str, AgentEndpointProtocol]]]
        version_selector: Optional[VersionSelector]

        @overload
        def __init__(
                self, 
                *, 
                authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]] = ..., 
                protocols: Optional[list[Union[str, AgentEndpointProtocol]]] = ..., 
                version_selector: Optional[VersionSelector] = ...
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
        ENTRA = "Entra"


    class azure.ai.projects.models.AgentEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A = "a2a"
        ACTIVITY = "activity"
        INVOCATIONS = "invocations"
        RESPONSES = "responses"


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


    class azure.ai.projects.models.AgentProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVITY_PROTOCOL = "activity_protocol"
        INVOCATIONS = "invocations"
        RESPONSES = "responses"


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


    class azure.ai.projects.models.AgentTaxonomyInput(EvaluationTaxonomyInput, discriminator='agent'):
        risk_categories: list[Union[str, RiskCategory]]
        target: Target
        type: Literal[EvaluationTaxonomyInputType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                risk_categories: list[Union[str, RiskCategory]], 
                target: Target
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


    class azure.ai.projects.models.AzureAIAgentTarget(Target, discriminator='azure_ai_agent'):
        name: str
        tool_descriptions: Optional[list[ToolDescription]]
        type: Literal["azure_ai_agent"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tool_descriptions: Optional[list[ToolDescription]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIAgentTargetParam(TypedDict, total=False):
        key "tool_descriptions": List[ToolDescriptionParam]
        key "version": str
        name: Required[str]
        type: Required[Literal["azure_ai_agent"]]


    class azure.ai.projects.models.AzureAIBenchmarkPreviewEvalRunDataSource(TypedDict, total=False):
        key "input_messages": InputMessagesItemReference
        target: Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        type: Required[Literal["azure_ai_benchmark_preview"]]


    class azure.ai.projects.models.AzureAIDataSourceConfig(TypedDict, total=False):
        scenario: Required[str]
        type: Required[Literal["azure_ai_source"]]


    class azure.ai.projects.models.AzureAIModelTarget(Target, discriminator='azure_ai_model'):
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
        type: Required[Literal["azure_ai_model"]]


    class azure.ai.projects.models.AzureAIResponsesEvalRunDataSource(TypedDict, total=False):
        key "event_configuration_id": str
        key "max_runs_hourly": int
        item_generation_params: Required[ResponseRetrievalItemGenerationParams]
        type: Required[Literal["azure_ai_responses"]]


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
        type: Literal[ToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource
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
        type: Literal[ToolType.AZURE_FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureOpenAIModelConfiguration(TargetConfig, discriminator='AzureOpenAIModel'):
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
        type: Literal[ToolType.BING_GROUNDING]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: BingGroundingSearchToolParameters
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
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: StructuredOutputDefinition
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
        entry_point: list[str]
        runtime: str

        @overload
        def __init__(
                self, 
                *, 
                entry_point: list[str], 
                runtime: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeInterpreterTool(Tool, discriminator='code_interpreter'):
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


    class azure.ai.projects.models.ComparisonFilter(_Model):
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
        type: Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                eval_id: str, 
                max_hourly_runs: Optional[int] = ...
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


    class azure.ai.projects.models.CustomTextFormatParam(CustomToolParamFormat, discriminator='text'):
        type: Literal[CustomToolParamFormatType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParam(Tool, discriminator='custom'):
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


    class azure.ai.projects.models.DeleteSkillResponse(_Model):
        deleted: bool
        name: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str
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


    class azure.ai.projects.models.EntraAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='Entra'):
        isolation_key_source: IsolationKeySource
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]

        @overload
        def __init__(
                self, 
                *, 
                isolation_key_source: IsolationKeySource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraIDCredentials(BaseCredentials, discriminator='AAD'):
        type: Literal[CredentialType.ENTRA_ID]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraIsolationKeySource(IsolationKeySource, discriminator='Entra'):
        kind: Literal[IsolationKeySourceKind.ENTRA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalCsvFileIdSource(TypedDict, total=False):
        id: Required[str]
        type: Required[Literal["file_id"]]


    class azure.ai.projects.models.EvalCsvRunDataSource(TypedDict, total=False):
        source: Required[EvalCsvFileIdSource]
        type: Required[Literal["csv"]]


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
        eval_run: Any
        type: Literal[ScheduleTaskType.EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                eval_id: str, 
                eval_run: Any
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
        OPENAI_GRADERS = "openai_graders"
        PROMPT = "prompt"
        PROMPT_AND_CODE = "prompt_and_code"
        SERVICE = "service"


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
        id: Optional[str]
        metadata: Optional[dict[str, str]]
        modified_at: datetime
        name: str
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
                tags: Optional[dict[str, str]] = ...
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


    class azure.ai.projects.models.FunctionShellToolParam(Tool, discriminator='shell'):
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


    class azure.ai.projects.models.GrammarSyntax1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARK = "lark"
        REGEX = "regex"


    class azure.ai.projects.models.HeaderIsolationKeySource(IsolationKeySource, discriminator='Header'):
        chat_isolation_key: str
        kind: Literal[IsolationKeySourceKind.HEADER]
        user_isolation_key: str

        @overload
        def __init__(
                self, 
                *, 
                chat_isolation_key: str, 
                user_isolation_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        container_protocol_versions: Optional[list[ProtocolVersionRecord]]
        cpu: str
        environment_variables: Optional[dict[str, str]]
        image: Optional[str]
        kind: Literal[AgentKind.HOSTED]
        memory: str
        protocol_versions: Optional[list[ProtocolVersionRecord]]
        rai_config: RaiConfig
        telemetry_config: Optional[TelemetryConfig]
        tools: Optional[list[Tool]]

        @overload
        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                container_configuration: Optional[ContainerConfiguration] = ..., 
                container_protocol_versions: Optional[list[ProtocolVersionRecord]] = ..., 
                cpu: str, 
                environment_variables: Optional[dict[str, str]] = ..., 
                image: Optional[str] = ..., 
                memory: str, 
                protocol_versions: Optional[list[ProtocolVersionRecord]] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                telemetry_config: Optional[TelemetryConfig] = ..., 
                tools: Optional[list[Tool]] = ...
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
        size: Optional[Literal["1024x1024", "1024x1536", "1536x1024", "auto"]]
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
                size: Optional[Literal[1024x1024, 1024x1536, 1536x1024, auto]] = ...
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


    class azure.ai.projects.models.IsolationKeySource(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.IsolationKeySourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTRA = "Entra"
        HEADER = "Header"


    class azure.ai.projects.models.LocalShellToolParam(Tool, discriminator='local_shell'):
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


    class azure.ai.projects.models.MCPTool(Tool, discriminator='mcp'):
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
        user_profile_details: Optional[str]
        user_profile_enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                chat_summary_enabled: bool, 
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


    class azure.ai.projects.models.ModelSamplingConfigParam(TypedDict, total=False):
        key "max_completion_tokens": int
        key "seed": int
        key "temperature": float
        key "top_p": float


    class azure.ai.projects.models.ModelSamplingParams(_Model):
        max_completion_tokens: int
        seed: int
        temperature: float
        top_p: float

        @overload
        def __init__(
                self, 
                *, 
                max_completion_tokens: int, 
                seed: int, 
                temperature: float, 
                top_p: float
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
        type: Literal[ToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                openapi: OpenApiFunctionDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


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


    class azure.ai.projects.models.ProtocolVersionRecord(_Model):
        protocol: Union[str, AgentProtocol]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                protocol: Union[str, AgentProtocol], 
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
        target: TargetConfig

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
                target: TargetConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RedTeamEvalRunDataSource(TypedDict, total=False):
        item_generation_params: Required[Any]
        target: Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        type: Required[Literal["azure_ai_red_team"]]


    class azure.ai.projects.models.ResponseRetrievalItemGenerationParams(TypedDict, total=False):
        key "max_num_turns": int
        data_mapping: Required[Dict[str, str]]
        source: Required[Union[SourceFileContent, SourceFileID]]
        type: Required[Literal["response_retrieval"]]


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


    class azure.ai.projects.models.SessionDirectoryListResponse(_Model):
        entries: list[SessionDirectoryEntry]
        path: str

        @overload
        def __init__(
                self, 
                *, 
                entries: list[SessionDirectoryEntry], 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionFileWriteResponse(_Model):
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


    class azure.ai.projects.models.SkillObject(_Model):
        description: Optional[str]
        has_blob: bool
        metadata: Optional[dict[str, str]]
        name: str
        skill_id: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                has_blob: bool, 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                skill_id: str
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


    class azure.ai.projects.models.Target(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TargetCompletionEvalRunDataSource(TypedDict, total=False):
        input_messages: Required[InputMessagesItemReference]
        source: Required[Union[SourceFileContent, SourceFileID]]
        target: Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        type: Required[Literal["azure_ai_target_completions"]]


    class azure.ai.projects.models.TargetConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
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


    class azure.ai.projects.models.TestingCriterionAzureAIEvaluator(TypedDict, total=False):
        key "data_mapping": Dict[str, str]
        key "evaluator_version": str
        key "initialization_parameters": Dict[str, Any]
        evaluator_name: Required[str]
        name: Required[str]
        type: Required[Literal["azure_ai_evaluator"]]


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


    class azure.ai.projects.models.ToolboxVersionObject(_Model):
        created_at: datetime
        description: Optional[str]
        id: str
        metadata: dict[str, str]
        name: str
        policies: Optional[ToolboxPolicies]
        tools: list[Tool]
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
                tools: list[Tool], 
                version: str
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
        type: Required[Literal["azure_ai_traces_preview"]]


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


    class azure.ai.projects.models.WebSearchTool(Tool, discriminator='web_search'):
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
        description: Optional[str]
        name: Optional[str]
        type: Literal[ToolType.WORK_IQ_PREVIEW]
        work_iq_preview: WorkIQPreviewToolParameters

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                work_iq_preview: WorkIQPreviewToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkIQPreviewToolParameters(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
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
        def create_version(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
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
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace
        def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace
        def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

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
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentVersionDetails]: ...


    class azure.ai.projects.operations.BetaAgentsOperations(GeneratedBetaAgentsOperations):

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
                isolation_key: str, 
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
                isolation_key: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                isolation_key: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace
        def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                isolation_key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_session_file(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_session_file(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace
        def get_session_files(
                self, 
                agent_name: str, 
                agent_session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionDirectoryListResponse: ...

        @distributed_trace
        def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

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

        @overload
        def patch_agent_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpoint] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def patch_agent_details(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def patch_agent_details(
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
                content_or_file_path: bytes | str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResponse: ...


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
                body: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                body: IO[bytes], 
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
                body: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
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
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

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
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorVersion]: ...

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

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

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
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryStoreDetails]: ...

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


    class azure.ai.projects.operations.BetaOperations(GeneratedBetaOperations):
        agents: BetaAgentsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        red_teams: BetaRedTeamsOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations
        toolboxes: BetaToolboxesOperations

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
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace
        def create_from_package(
                self, 
                body: bytes, 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResponse: ...

        @distributed_trace
        def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkillObject]: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                instructions: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillObject: ...


    class azure.ai.projects.operations.BetaToolboxesOperations:

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
                tools: List[Tool], 
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