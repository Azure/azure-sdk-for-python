```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.purview.workflow

    class azure.purview.workflow.PurviewWorkflowClient: implements ContextManager 
        approval: ApprovalOperations
        task_status: TaskStatusOperations
        user_requests: UserRequestsOperations
        workflow: WorkflowOperations
        workflow_run: WorkflowRunOperations
        workflow_runs: WorkflowRunsOperations
        workflow_task: WorkflowTaskOperations
        workflow_tasks: WorkflowTasksOperations
        workflows: WorkflowsOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.purview.workflow.aio

    class azure.purview.workflow.aio.PurviewWorkflowClient: implements AsyncContextManager 
        approval: ApprovalOperations
        task_status: TaskStatusOperations
        user_requests: UserRequestsOperations
        workflow: WorkflowOperations
        workflow_run: WorkflowRunOperations
        workflow_runs: WorkflowRunsOperations
        workflow_task: WorkflowTaskOperations
        workflow_tasks: WorkflowTasksOperations
        workflows: WorkflowsOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
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


namespace azure.purview.workflow.aio.operations

    class azure.purview.workflow.aio.operations.ApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def approve(
                self, 
                task_id: str, 
                approval_response_comment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def approve(
                self, 
                task_id: str, 
                approval_response_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def reject(
                self, 
                task_id: str, 
                approval_response_comment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def reject(
                self, 
                task_id: str, 
                approval_response_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.aio.operations.TaskStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def update(
                self, 
                task_id: str, 
                task_update_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                task_id: str, 
                task_update_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.aio.operations.UserRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def submit(
                self, 
                user_requests_payload: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def submit(
                self, 
                user_requests_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.aio.operations.WorkflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_replace(
                self, 
                workflow_id: str, 
                workflow_create_or_update_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def create_or_replace(
                self, 
                workflow_id: str, 
                workflow_create_or_update_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def delete(
                self, 
                workflow_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                workflow_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def validate(
                self, 
                workflow_id: str, 
                workflow_validate_query: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def validate(
                self, 
                workflow_id: str, 
                workflow_validate_query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.aio.operations.WorkflowRunOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                workflow_run_id: str, 
                run_cancel_reply: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def cancel(
                self, 
                workflow_run_id: str, 
                run_cancel_reply: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                workflow_run_id: str, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.aio.operations.WorkflowRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                orderby: Optional[str] = ..., 
                requestors: Optional[List[str]] = ..., 
                run_statuses: Optional[List[str]] = ..., 
                time_window: Optional[str] = ..., 
                view_mode: Optional[str] = ..., 
                workflow_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...


    class azure.purview.workflow.aio.operations.WorkflowTaskOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def reassign(
                self, 
                task_id: str, 
                reassign_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def reassign(
                self, 
                task_id: str, 
                reassign_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.aio.operations.WorkflowTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                assignees: Optional[List[str]] = ..., 
                orderby: Optional[str] = ..., 
                requestors: Optional[List[str]] = ..., 
                task_statuses: Optional[List[str]] = ..., 
                task_types: Optional[List[str]] = ..., 
                time_window: Optional[str] = ..., 
                view_mode: Optional[str] = ..., 
                workflow_ids: Optional[List[str]] = ..., 
                workflow_name_keyword: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...


    class azure.purview.workflow.aio.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[JSON]: ...


namespace azure.purview.workflow.operations

    class azure.purview.workflow.operations.ApprovalOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def approve(
                self, 
                task_id: str, 
                approval_response_comment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def approve(
                self, 
                task_id: str, 
                approval_response_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def reject(
                self, 
                task_id: str, 
                approval_response_comment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def reject(
                self, 
                task_id: str, 
                approval_response_comment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.operations.TaskStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def update(
                self, 
                task_id: str, 
                task_update_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                task_id: str, 
                task_update_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.operations.UserRequestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def submit(
                self, 
                user_requests_payload: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def submit(
                self, 
                user_requests_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.operations.WorkflowOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_replace(
                self, 
                workflow_id: str, 
                workflow_create_or_update_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def create_or_replace(
                self, 
                workflow_id: str, 
                workflow_create_or_update_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def delete(
                self, 
                workflow_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                workflow_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def validate(
                self, 
                workflow_id: str, 
                workflow_validate_query: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def validate(
                self, 
                workflow_id: str, 
                workflow_validate_query: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.operations.WorkflowRunOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def cancel(
                self, 
                workflow_run_id: str, 
                run_cancel_reply: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def cancel(
                self, 
                workflow_run_id: str, 
                run_cancel_reply: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                workflow_run_id: str, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.purview.workflow.operations.WorkflowRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                orderby: Optional[str] = ..., 
                requestors: Optional[List[str]] = ..., 
                run_statuses: Optional[List[str]] = ..., 
                time_window: Optional[str] = ..., 
                view_mode: Optional[str] = ..., 
                workflow_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> Iterable[JSON]: ...


    class azure.purview.workflow.operations.WorkflowTaskOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def reassign(
                self, 
                task_id: str, 
                reassign_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def reassign(
                self, 
                task_id: str, 
                reassign_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.purview.workflow.operations.WorkflowTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                assignees: Optional[List[str]] = ..., 
                orderby: Optional[str] = ..., 
                requestors: Optional[List[str]] = ..., 
                task_statuses: Optional[List[str]] = ..., 
                task_types: Optional[List[str]] = ..., 
                time_window: Optional[str] = ..., 
                view_mode: Optional[str] = ..., 
                workflow_ids: Optional[List[str]] = ..., 
                workflow_name_keyword: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterable[JSON]: ...


    class azure.purview.workflow.operations.WorkflowsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[JSON]: ...


```