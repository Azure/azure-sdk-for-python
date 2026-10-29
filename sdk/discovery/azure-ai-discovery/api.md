```py
namespace azure.ai.discovery

    class azure.ai.discovery.BookshelfClient(_GeneratedBookshelfClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                transport: Optional[HttpTransport] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.discovery.WorkspaceClient(_GeneratedWorkspaceClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                transport: Optional[HttpTransport] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.discovery.aio

    class azure.ai.discovery.aio.BookshelfClient(_GeneratedBookshelfClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                transport: Optional[AsyncHttpTransport] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.discovery.aio.WorkspaceClient(_GeneratedWorkspaceClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                transport: Optional[AsyncHttpTransport] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.discovery.aio.operations

    class azure.ai.discovery.aio.operations.ConversationsOperations:

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
                display_name: Optional[str] = ..., 
                investigation_name: Optional[str] = ..., 
                project_name: str, 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        async def create(
                self, 
                body: CreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Conversation: ...

        @distributed_trace_async
        async def delete(
                self, 
                conversation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                conversation_name: str, 
                **kwargs: Any
            ) -> Conversation: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'investigation_name', 'project_name', 'created_since', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        async def list(
                self, 
                *, 
                created_since: Optional[datetime] = ..., 
                investigation_name: Optional[str] = ..., 
                project_name: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedConversation: ...

        @overload
        async def stable_update(
                self, 
                conversation_name: str, 
                resource: Conversation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        async def stable_update(
                self, 
                conversation_name: str, 
                resource: Conversation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        async def stable_update(
                self, 
                conversation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...


    class azure.ai.discovery.aio.operations.InvestigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Investigation]: ...

        @overload
        async def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        async def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        async def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @distributed_trace_async
        async def get(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> Investigation: ...

        @distributed_trace_async
        async def get_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'investigation_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        async def get_discovery_engine_memory(
                self, 
                project_name: str, 
                investigation_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedWorkingMemoryEntry: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'investigation_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        async def get_operation_status(
                self, 
                project_name: str, 
                investigation_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> InvestigationOperationStatus: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'created_since', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        async def list(
                self, 
                project_name: str, 
                *, 
                created_since: Optional[datetime] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedInvestigation: ...

        @distributed_trace_async
        async def start_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @distributed_trace_async
        async def stop_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        async def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        async def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        async def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        async def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: DiscoveryEngineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        async def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: DiscoveryEngineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        async def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...


    class azure.ai.discovery.aio.operations.KnowledgeBasesOperations(_GeneratedKnowledgeBasesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'repeatability_request_id', 'repeatability_first_sent', 'client_request_id', 'accept']}, api_versions_list=['2026-06-01'])
        async def begin_cancel_indexing(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def begin_create_or_update(
                self, 
                knowledge_base_name: str, 
                resource: Union[KnowledgeBase, dict[str, Any], IO[bytes]], 
                **kwargs: Any
            ) -> AsyncLROPoller[KnowledgeBase]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'accept']}, api_versions_list=['2026-06-01'])
        async def begin_delete(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_search(
                self, 
                knowledge_base_name: str, 
                body: SearchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_search(
                self, 
                knowledge_base_name: str, 
                body: SearchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_search(
                self, 
                knowledge_base_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                *, 
                content_type: str = "application/json", 
                node_pool_id: Optional[str] = ..., 
                project_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                body: StartIndexingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'accept']}, api_versions_list=['2026-06-01'])
        async def get(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        async def get_operation_status(
                self, 
                knowledge_base_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> KnowledgeBaseOperationResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[KnowledgeBase]: ...


    class azure.ai.discovery.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: TaskComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: TaskComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: ExecutionHistoryEntry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: ExecutionHistoryEntry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace_async
        async def delete(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def list(
                self, 
                project_name: str, 
                investigation_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Task]: ...

        @overload
        async def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[StartTaskRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[StartTaskRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...


    class azure.ai.discovery.aio.operations.ToolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        async def begin_cancel_run_lro(
                self, 
                project_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RunResult]: ...

        @overload
        async def begin_run(
                self, 
                project_name: str, 
                *, 
                command: Optional[str] = ..., 
                content_type: str = "application/json", 
                environment_variables: Optional[List[RunRequestEnvironmentVariable]] = ..., 
                infra_overrides: Optional[InfraOverrides] = ..., 
                inline_files: Optional[List[InlineFile]] = ..., 
                input_data: Optional[List[InputDataMount]] = ..., 
                node_pool_ids: List[str], 
                output_data: Optional[List[OutputDataMount]] = ..., 
                tool_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RunResult]: ...

        @overload
        async def begin_run(
                self, 
                project_name: str, 
                body: RunRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunResult]: ...

        @overload
        async def begin_run(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunResult]: ...

        @distributed_trace_async
        async def get_compute_usage(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> ComputeUsage: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        async def get_operations(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedOperation: ...

        @distributed_trace_async
        async def get_run_status(
                self, 
                project_name: str, 
                operation_id: str, 
                *, 
                log_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> OperationStatusRunResultError: ...


namespace azure.ai.discovery.models

    class azure.ai.discovery.models.ByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        SYSTEM = "System"
        USER = "User"


    class azure.ai.discovery.models.Citation(_Model):
        end_offset: Optional[int]
        file_name: str
        index: Optional[int]
        start_offset: Optional[int]
        type: Union[str, CitationType]

        @overload
        def __init__(
                self, 
                *, 
                end_offset: Optional[int] = ..., 
                file_name: str, 
                index: Optional[int] = ..., 
                start_offset: Optional[int] = ..., 
                type: Union[str, CitationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.CitationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_CITATION = "file_citation"


    class azure.ai.discovery.models.ComputeUsage(_Model):
        supercomputers: dict[str, SupercomputerUsage]

        @overload
        def __init__(
                self, 
                *, 
                supercomputers: dict[str, SupercomputerUsage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.Conversation(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, ByType]]
        display_name: Optional[str]
        investigation_name: Optional[str]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, ByType]]
        name: str
        project_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, ByType]] = ..., 
                display_name: Optional[str] = ..., 
                investigation_name: Optional[str] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, ByType]] = ..., 
                project_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.DiscoveryEngine(_Model):
        configuration: Optional[dict[str, Any]]
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, ByType]]
        discovery_engine_status: Union[str, DiscoveryEngineStatus]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, ByType]]
        system_prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, Any]] = ..., 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, ByType]] = ..., 
                discovery_engine_status: Union[str, DiscoveryEngineStatus], 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, ByType]] = ..., 
                system_prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.DiscoveryEngineStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.ai.discovery.models.DiscoveryEngineUpdate(_Model):
        configuration: Optional[dict[str, Any]]
        system_prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, Any]] = ..., 
                system_prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.ExecutionHistoryEntry(_Model):
        action: str
        additional_details: Optional[dict[str, Any]]
        created_at: datetime
        created_by: str
        created_by_type: Union[str, ByType]
        response_message_id: Optional[str]
        response_message_text: Optional[str]
        summary: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: str, 
                additional_details: Optional[dict[str, Any]] = ..., 
                created_at: datetime, 
                created_by: str, 
                created_by_type: Union[str, ByType], 
                response_message_id: Optional[str] = ..., 
                response_message_text: Optional[str] = ..., 
                summary: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.IndexingMetrics(_Model):
        documents_failed: int
        documents_processed: int
        documents_total: int
        enrichment_end_time_utc: Optional[datetime]
        enrichment_start_time_utc: Optional[datetime]
        indexing_end_time_utc: Optional[datetime]
        indexing_percentage_complete: int
        indexing_start_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                documents_failed: int, 
                documents_processed: int, 
                documents_total: int, 
                enrichment_end_time_utc: Optional[datetime] = ..., 
                enrichment_start_time_utc: Optional[datetime] = ..., 
                indexing_end_time_utc: Optional[datetime] = ..., 
                indexing_percentage_complete: int, 
                indexing_start_time_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.IndexingOperationResult(_Model):
        metrics: Optional[IndexingMetrics]
        run_id: str

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[IndexingMetrics] = ..., 
                run_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.IndexingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.discovery.models.InfraOverrides(_Model):
        cpu: Optional[str]
        gpu: Optional[str]
        image_uri: Optional[str]
        max_cpu: Optional[str]
        max_gpu: Optional[str]
        max_ram: Optional[str]
        ram: Optional[str]
        replica_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[str] = ..., 
                gpu: Optional[str] = ..., 
                image_uri: Optional[str] = ..., 
                max_cpu: Optional[str] = ..., 
                max_gpu: Optional[str] = ..., 
                max_ram: Optional[str] = ..., 
                ram: Optional[str] = ..., 
                replica_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.InlineFile(_Model):
        encoded_file: str
        mount_path: str

        @overload
        def __init__(
                self, 
                *, 
                encoded_file: str, 
                mount_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.InputDataMount(_Model):
        mount_path: str
        mount_protocol: Optional[Union[str, StorageMountProtocol]]
        storage_uri: str

        @overload
        def __init__(
                self, 
                *, 
                mount_path: str, 
                mount_protocol: Optional[Union[str, StorageMountProtocol]] = ..., 
                storage_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.Investigation(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, ByType]]
        description: Optional[str]
        display_name: Optional[str]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, ByType]]
        name: str
        project_name: str
        status: Optional[Union[str, InvestigationStatus]]
        tags: Optional[list[Tag]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                tags: Optional[list[Tag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.InvestigationOperationStatus(_Model):
        error: Optional[ODataV4Format]
        id: str
        result: Optional[Investigation]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[Investigation] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.InvestigationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        FAILED = "Failed"
        VALIDATED = "Validated"


    class azure.ai.discovery.models.KnowledgeBase(_Model):
        bookshelf_name: str
        copilot_instruction: str
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_api_version: Optional[str]
        created_by_type: Optional[Union[str, ByType]]
        description: str
        error: Optional[ODataV4Format]
        id: Optional[str]
        knowledge_base_url: Optional[str]
        last_indexing_run: Optional[LastIndexingRun]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, ByType]]
        name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, IndexingStatus]]
        storage_asset_references: Optional[list[StorageAssetReference]]
        tags: Optional[list[Tag]]

        @overload
        def __init__(
                self, 
                *, 
                copilot_instruction: str, 
                description: str, 
                storage_asset_references: Optional[list[StorageAssetReference]] = ..., 
                tags: Optional[list[Tag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.KnowledgeBaseIndexingOperationResponse(KnowledgeBaseOperationResponse, discriminator='Indexing'):
        error: ODataV4Format
        id: str
        indexing_result: Optional[IndexingOperationResult]
        operation_type: Literal[KnowledgeBaseOperationType.INDEXING]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                indexing_result: Optional[IndexingOperationResult] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.KnowledgeBaseOperationResponse(_Model):
        error: Optional[ODataV4Format]
        id: str
        operation_type: str
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                operation_type: str, 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.KnowledgeBaseOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL_INDEXING = "CancelIndexing"
        DELETE = "Delete"
        INDEXING = "Indexing"
        SEARCH = "Search"


    class azure.ai.discovery.models.KnowledgeBaseSearchOperationResponse(KnowledgeBaseOperationResponse, discriminator='Search'):
        error: ODataV4Format
        id: str
        operation_type: Literal[KnowledgeBaseOperationType.SEARCH]
        search_result: Optional[SearchResponse]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                search_result: Optional[SearchResponse] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.LastIndexingRun(_Model):
        error: Optional[ODataV4Format]
        indexing_metrics: Optional[IndexingMetrics]
        run_id: Optional[str]
        status: Optional[Union[str, IndexingStatus]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                indexing_metrics: Optional[IndexingMetrics] = ..., 
                run_id: Optional[str] = ..., 
                status: Optional[Union[str, IndexingStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.NodepoolUsage(_Model):
        allocatable_cp_us: str
        allocatable_gp_us: str
        allocatable_memory: str
        reserved_cp_us: str
        reserved_gp_us: str
        reserved_memory: str

        @overload
        def __init__(
                self, 
                *, 
                allocatable_cp_us: str, 
                allocatable_gp_us: str, 
                allocatable_memory: str, 
                reserved_cp_us: str, 
                reserved_gp_us: str, 
                reserved_memory: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.Operation(_Model):
        completed_at: Optional[datetime]
        created_at: datetime
        created_by: Optional[str]
        id: str
        nodepool_id: str
        runtime_details: str
        status: Union[str, RunStatus]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                created_at: datetime, 
                created_by: Optional[str] = ..., 
                id: str, 
                nodepool_id: str, 
                runtime_details: str, 
                status: Union[str, RunStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.discovery.models.OperationStatusRunResultError(_Model):
        error: Optional[ODataV4Format]
        id: str
        result: Optional[RunResult]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[RunResult] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.OutputDataMount(_Model):
        mount_path: str
        mount_protocol: Optional[Union[str, StorageMountProtocol]]
        storage_uri: str

        @overload
        def __init__(
                self, 
                *, 
                mount_path: str, 
                mount_protocol: Optional[Union[str, StorageMountProtocol]] = ..., 
                storage_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.OutputDataUri(_Model):
        mount_path: str
        storage_uri: str

        @overload
        def __init__(
                self, 
                *, 
                mount_path: str, 
                storage_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.PagedConversation(_Model):
        next_link: Optional[str]
        value: list[Conversation]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Conversation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.PagedInvestigation(_Model):
        next_link: Optional[str]
        value: list[Investigation]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Investigation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.PagedOperation(_Model):
        next_link: Optional[str]
        value: list[Operation]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Operation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.PagedWorkingMemoryEntry(_Model):
        next_link: Optional[str]
        value: list[WorkingMemoryEntry]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[WorkingMemoryEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.ai.discovery.models.RepeatabilityResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "accepted"
        REJECTED = "rejected"


    class azure.ai.discovery.models.RunRequestEnvironmentVariable(_Model):
        name: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.RunResult(_Model):
        completed_at: Optional[datetime]
        created_at: Optional[datetime]
        created_by: Optional[str]
        debug_info: str
        output_data: list[OutputDataUri]
        runtime_details: str
        status: Optional[str]
        tool_report: Optional[RunResultToolReport]

        @overload
        def __init__(
                self, 
                *, 
                created_by: Optional[str] = ..., 
                debug_info: str, 
                output_data: list[OutputDataUri], 
                runtime_details: str, 
                status: Optional[str] = ..., 
                tool_report: Optional[RunResultToolReport] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.RunResultToolReport(_Model):
        logs: Optional[str]
        percentage_complete: int
        status_information: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                logs: Optional[str] = ..., 
                percentage_complete: int, 
                status_information: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.RunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.discovery.models.SearchRequest(_Model):
        query: str

        @overload
        def __init__(
                self, 
                *, 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.SearchResponse(_Model):
        search_results: list[SearchResultItem]

        @overload
        def __init__(
                self, 
                *, 
                search_results: list[SearchResultItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.SearchResultItem(_Model):
        citations: Optional[list[Citation]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                citations: Optional[list[Citation]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.StartTaskRequest(_Model):
        assignee: Optional[TaskAssignee]

        @overload
        def __init__(
                self, 
                *, 
                assignee: Optional[TaskAssignee] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.StorageAssetReference(_Model):
        id: str
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.StorageMountProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOBFUSE_CACHING = "BlobfuseCaching"
        NFS = "NFS"


    class azure.ai.discovery.models.SupercomputerUsage(_Model):
        active_jobs: int
        nodepools: dict[str, NodepoolUsage]
        pending_jobs: int

        @overload
        def __init__(
                self, 
                *, 
                active_jobs: int, 
                nodepools: dict[str, NodepoolUsage], 
                pending_jobs: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.Tag(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.Task(_Model):
        assigned_to: Optional[TaskAssignee]
        comments: Optional[list[TaskComment]]
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, ByType]]
        depends_on: Optional[list[str]]
        description: Optional[str]
        execution_history: Optional[list[ExecutionHistoryEntry]]
        investigation_id: Optional[str]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, ByType]]
        name: str
        parent_id: Optional[str]
        priority: Optional[Union[str, TaskPriority]]
        related_to: Optional[list[str]]
        status: Optional[Union[str, TaskStatus]]
        storage_asset_ids: Optional[list[str]]
        task_result: Optional[TaskResult]
        title: Optional[str]
        validation_requirements: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                assigned_to: Optional[TaskAssignee] = ..., 
                comments: Optional[list[TaskComment]] = ..., 
                created_by_type: Optional[Union[str, ByType]] = ..., 
                depends_on: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                investigation_id: Optional[str] = ..., 
                parent_id: Optional[str] = ..., 
                priority: Optional[Union[str, TaskPriority]] = ..., 
                related_to: Optional[list[str]] = ..., 
                status: Optional[Union[str, TaskStatus]] = ..., 
                storage_asset_ids: Optional[list[str]] = ..., 
                task_result: Optional[TaskResult] = ..., 
                title: Optional[str] = ..., 
                validation_requirements: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.TaskAssignee(_Model):
        id: str
        type: Union[str, ByType]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                type: Union[str, ByType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.TaskComment(_Model):
        created_by: str
        created_by_type: Union[str, ByType]
        text: str
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                created_by: str, 
                created_by_type: Union[str, ByType], 
                text: str, 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.TaskPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.ai.discovery.models.TaskResult(_Model):
        storage_asset_ids: Optional[list[str]]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_asset_ids: Optional[list[str]] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.TaskStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        EXECUTING = "Executing"
        EXECUTION_DONE = "ExecutionDone"
        FAILED = "Failed"
        FLAGGED_AI = "FlaggedAi"
        FLAGGED_HUMAN = "FlaggedHuman"
        INCOMPLETE = "Incomplete"
        NEW = "New"
        ON_HOLD = "OnHold"
        REMOVED = "Removed"
        STALE = "Stale"


    class azure.ai.discovery.models.WorkingMemoryEntry(_Model):
        content: str
        created_at: Optional[datetime]
        type: Union[str, WorkingMemoryEntryType]

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                created_at: Optional[datetime] = ..., 
                type: Union[str, WorkingMemoryEntryType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.discovery.models.WorkingMemoryEntryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THOUGHT = "Thought"


namespace azure.ai.discovery.operations

    class azure.ai.discovery.operations.ConversationsOperations:

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
                display_name: Optional[str] = ..., 
                investigation_name: Optional[str] = ..., 
                project_name: str, 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        def create(
                self, 
                body: CreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Conversation: ...

        @distributed_trace
        def delete(
                self, 
                conversation_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                conversation_name: str, 
                **kwargs: Any
            ) -> Conversation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'investigation_name', 'project_name', 'created_since', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        def list(
                self, 
                *, 
                created_since: Optional[datetime] = ..., 
                investigation_name: Optional[str] = ..., 
                project_name: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedConversation: ...

        @overload
        def stable_update(
                self, 
                conversation_name: str, 
                resource: Conversation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        def stable_update(
                self, 
                conversation_name: str, 
                resource: Conversation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...

        @overload
        def stable_update(
                self, 
                conversation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Conversation: ...


    class azure.ai.discovery.operations.InvestigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> LROPoller[Investigation]: ...

        @overload
        def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        def create_or_replace(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Investigation: ...

        @distributed_trace
        def get(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> Investigation: ...

        @distributed_trace
        def get_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'investigation_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        def get_discovery_engine_memory(
                self, 
                project_name: str, 
                investigation_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedWorkingMemoryEntry: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'investigation_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        def get_operation_status(
                self, 
                project_name: str, 
                investigation_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> InvestigationOperationStatus: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'created_since', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        def list(
                self, 
                project_name: str, 
                *, 
                created_since: Optional[datetime] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedInvestigation: ...

        @distributed_trace
        def start_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @distributed_trace
        def stop_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: Investigation, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        def update(
                self, 
                project_name: str, 
                investigation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Investigation: ...

        @overload
        def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: DiscoveryEngineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: DiscoveryEngineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...

        @overload
        def update_discovery_engine(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryEngine: ...


    class azure.ai.discovery.operations.KnowledgeBasesOperations(_GeneratedKnowledgeBasesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'repeatability_request_id', 'repeatability_first_sent', 'client_request_id', 'accept']}, api_versions_list=['2026-06-01'])
        def begin_cancel_indexing(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def begin_create_or_update(
                self, 
                knowledge_base_name: str, 
                resource: Union[KnowledgeBase, dict[str, Any], IO[bytes]], 
                **kwargs: Any
            ) -> LROPoller[KnowledgeBase]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'accept']}, api_versions_list=['2026-06-01'])
        def begin_delete(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_search(
                self, 
                knowledge_base_name: str, 
                body: SearchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_search(
                self, 
                knowledge_base_name: str, 
                body: SearchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_search(
                self, 
                knowledge_base_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                *, 
                content_type: str = "application/json", 
                node_pool_id: Optional[str] = ..., 
                project_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                body: StartIndexingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start_indexing(
                self, 
                knowledge_base_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'accept']}, api_versions_list=['2026-06-01'])
        def get(
                self, 
                knowledge_base_name: str, 
                **kwargs: Any
            ) -> KnowledgeBase: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'knowledge_base_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        def get_operation_status(
                self, 
                knowledge_base_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> KnowledgeBaseOperationResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[KnowledgeBase]: ...


    class azure.ai.discovery.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: TaskComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: TaskComment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def add_comment(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: ExecutionHistoryEntry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: ExecutionHistoryEntry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def add_execution_history(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def create(
                self, 
                project_name: str, 
                investigation_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def delete(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @distributed_trace
        def list(
                self, 
                project_name: str, 
                investigation_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Task]: ...

        @overload
        def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def stable_update(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[StartTaskRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[StartTaskRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def start(
                self, 
                project_name: str, 
                investigation_name: str, 
                task_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Task: ...


    class azure.ai.discovery.operations.ToolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'operation_id', 'accept']}, api_versions_list=['2026-06-01'])
        def begin_cancel_run_lro(
                self, 
                project_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[RunResult]: ...

        @overload
        def begin_run(
                self, 
                project_name: str, 
                *, 
                command: Optional[str] = ..., 
                content_type: str = "application/json", 
                environment_variables: Optional[List[RunRequestEnvironmentVariable]] = ..., 
                infra_overrides: Optional[InfraOverrides] = ..., 
                inline_files: Optional[List[InlineFile]] = ..., 
                input_data: Optional[List[InputDataMount]] = ..., 
                node_pool_ids: List[str], 
                output_data: Optional[List[OutputDataMount]] = ..., 
                tool_id: str, 
                **kwargs: Any
            ) -> LROPoller[RunResult]: ...

        @overload
        def begin_run(
                self, 
                project_name: str, 
                body: RunRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunResult]: ...

        @overload
        def begin_run(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunResult]: ...

        @distributed_trace
        def get_compute_usage(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> ComputeUsage: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-01', params_added_on={'2026-06-01': ['api_version', 'project_name', 'top', 'skip', 'maxpagesize', 'accept']}, api_versions_list=['2026-06-01'])
        def get_operations(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PagedOperation: ...

        @distributed_trace
        def get_run_status(
                self, 
                project_name: str, 
                operation_id: str, 
                *, 
                log_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> OperationStatusRunResultError: ...


namespace azure.ai.discovery.types

    class azure.ai.discovery.types.Conversation(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, ByType]
        key "displayName": str
        key "investigationName": str
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, ByType]
        key "name": Required[str]
        key "projectName": str
        created_at: str
        created_by: str
        created_by_type: Union[str, ByType]
        display_name: str
        investigation_name: str
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, ByType]
        name: str
        project_name: str


    class azure.ai.discovery.types.CreateRequest(TypedDict, total=False):
        key "displayName": str
        key "investigationName": str
        key "projectName": Required[str]
        display_name: str
        investigation_name: str
        project_name: str


    class azure.ai.discovery.types.DiscoveryEngineUpdate(TypedDict, total=False):
        key "systemPrompt": str
        configuration: dict[str, Any]
        system_prompt: str


    class azure.ai.discovery.types.ExecutionHistoryEntry(TypedDict, total=False):
        key "action": Required[str]
        key "createdAt": Required[str]
        key "createdBy": Required[str]
        key "createdByType": Required[Union[str, ByType]]
        key "responseMessageId": str
        key "responseMessageText": str
        key "summary": str
        action: str
        additionalDetails: dict[str, Any]
        additional_details: dict[str, Any]
        created_at: str
        created_by: str
        created_by_type: Union[str, ByType]
        response_message_id: str
        response_message_text: str
        summary: str


    class azure.ai.discovery.types.IndexingMetrics(TypedDict, total=False):
        key "documentsFailed": Required[int]
        key "documentsProcessed": Required[int]
        key "documentsTotal": Required[int]
        key "enrichmentEndTimeUtc": str
        key "enrichmentStartTimeUtc": str
        key "indexingEndTimeUtc": str
        key "indexingPercentageComplete": Required[int]
        key "indexingStartTimeUtc": str
        documents_failed: int
        documents_processed: int
        documents_total: int
        enrichment_end_time_utc: str
        enrichment_start_time_utc: str
        indexing_end_time_utc: str
        indexing_percentage_complete: int
        indexing_start_time_utc: str


    class azure.ai.discovery.types.InfraOverrides(TypedDict, total=False):
        key "cpu": str
        key "gpu": str
        key "imageUri": str
        key "maxCpu": str
        key "maxGpu": str
        key "maxRam": str
        key "ram": str
        key "replicaCount": int
        cpu: str
        gpu: str
        image_uri: str
        max_cpu: str
        max_gpu: str
        max_ram: str
        ram: str
        replica_count: int


    class azure.ai.discovery.types.InlineFile(TypedDict, total=False):
        key "encodedFile": Required[str]
        key "mountPath": Required[str]
        encoded_file: str
        mount_path: str


    class azure.ai.discovery.types.InputDataMount(TypedDict, total=False):
        key "mountPath": Required[str]
        key "mountProtocol": Union[str, StorageMountProtocol]
        key "storageUri": Required[str]
        mount_path: str
        mount_protocol: Union[str, StorageMountProtocol]
        storage_uri: str


    class azure.ai.discovery.types.Investigation(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, ByType]
        key "description": str
        key "displayName": str
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, ByType]
        key "name": Required[str]
        key "projectName": Required[str]
        key "status": Union[str, InvestigationStatus]
        created_at: str
        created_by: str
        created_by_type: Union[str, ByType]
        description: str
        display_name: str
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, ByType]
        name: str
        project_name: str
        status: Union[str, InvestigationStatus]
        tags: list[Tag]


    class azure.ai.discovery.types.KnowledgeBase(TypedDict, total=False):
        key "bookshelfName": Required[str]
        key "copilotInstruction": Required[str]
        key "createdAt": str
        key "createdBy": str
        key "createdByApiVersion": str
        key "createdByType": Union[str, ByType]
        key "description": Required[str]
        key "error": ODataV4Format
        key "id": str
        key "knowledgeBaseUrl": str
        key "lastIndexingRun": ForwardRef('LastIndexingRun', module='types')
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, ByType]
        key "name": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Union[str, IndexingStatus]
        bookshelf_name: str
        copilot_instruction: str
        created_at: str
        created_by: str
        created_by_api_version: str
        created_by_type: Union[str, ByType]
        description: str
        error: ODataV4Format
        id: str
        knowledge_base_url: str
        last_indexing_run: LastIndexingRun
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, ByType]
        name: str
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, IndexingStatus]
        storageAssetReferences: list[StorageAssetReference]
        storage_asset_references: list[StorageAssetReference]
        tags: list[Tag]


    class azure.ai.discovery.types.LastIndexingRun(TypedDict, total=False):
        key "error": ODataV4Format
        key "indexingMetrics": ForwardRef('IndexingMetrics', module='types')
        key "runId": str
        key "status": Union[str, IndexingStatus]
        error: ODataV4Format
        indexing_metrics: IndexingMetrics
        run_id: str
        status: Union[str, IndexingStatus]


    class azure.ai.discovery.types.OutputDataMount(TypedDict, total=False):
        key "mountPath": Required[str]
        key "mountProtocol": Union[str, StorageMountProtocol]
        key "storageUri": Required[str]
        mount_path: str
        mount_protocol: Union[str, StorageMountProtocol]
        storage_uri: str


    class azure.ai.discovery.types.RunRequest(TypedDict, total=False):
        key "command": str
        key "infraOverrides": ForwardRef('InfraOverrides', module='types')
        key "nodePoolIds": Required[list[str]]
        key "toolId": Required[str]
        command: str
        environmentVariables: list[RunRequestEnvironmentVariable]
        environment_variables: list[RunRequestEnvironmentVariable]
        infra_overrides: InfraOverrides
        inlineFiles: list[InlineFile]
        inline_files: list[InlineFile]
        inputData: list[InputDataMount]
        input_data: list[InputDataMount]
        node_pool_ids: list[str]
        outputData: list[OutputDataMount]
        output_data: list[OutputDataMount]
        tool_id: str


    class azure.ai.discovery.types.RunRequestEnvironmentVariable(TypedDict, total=False):
        key "name": Required[str]
        key "value": str
        name: str
        value: str


    class azure.ai.discovery.types.SearchRequest(TypedDict, total=False):
        key "query": Required[str]
        query: str


    class azure.ai.discovery.types.StartIndexingRequest(TypedDict, total=False):
        key "nodePoolId": str
        key "projectId": str
        node_pool_id: str
        project_id: str


    class azure.ai.discovery.types.StartTaskRequest(TypedDict, total=False):
        key "assignee": ForwardRef('TaskAssignee', module='types')
        assignee: TaskAssignee


    class azure.ai.discovery.types.StorageAssetReference(TypedDict, total=False):
        key "id": Required[str]
        key "userAssignedIdentity": str
        id: str
        user_assigned_identity: str


    class azure.ai.discovery.types.Tag(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.ai.discovery.types.Task(TypedDict, total=False):
        key "assignedTo": ForwardRef('TaskAssignee', module='types')
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, ByType]
        key "description": str
        key "investigationId": str
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, ByType]
        key "name": Required[str]
        key "parentId": str
        key "priority": Union[str, TaskPriority]
        key "status": Union[str, TaskStatus]
        key "taskResult": ForwardRef('TaskResult', module='types')
        key "title": str
        assigned_to: TaskAssignee
        comments: list[TaskComment]
        created_at: str
        created_by: str
        created_by_type: Union[str, ByType]
        dependsOn: list[str]
        depends_on: list[str]
        description: str
        executionHistory: list[ExecutionHistoryEntry]
        execution_history: list[ExecutionHistoryEntry]
        investigation_id: str
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, ByType]
        name: str
        parent_id: str
        priority: Union[str, TaskPriority]
        relatedTo: list[str]
        related_to: list[str]
        status: Union[str, TaskStatus]
        storageAssetIds: list[str]
        storage_asset_ids: list[str]
        task_result: TaskResult
        title: str
        validationRequirements: list[str]
        validation_requirements: list[str]


    class azure.ai.discovery.types.TaskAssignee(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Union[str, ByType]]
        id: str
        type: Union[str, ByType]


    class azure.ai.discovery.types.TaskComment(TypedDict, total=False):
        key "createdBy": Required[str]
        key "createdByType": Required[Union[str, ByType]]
        key "text": Required[str]
        key "timestamp": str
        created_by: str
        created_by_type: Union[str, ByType]
        text: str
        timestamp: str


    class azure.ai.discovery.types.TaskResult(TypedDict, total=False):
        key "text": str
        storageAssetIds: list[str]
        storage_asset_ids: list[str]
        text: str


```