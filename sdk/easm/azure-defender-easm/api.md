```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.defender.easm

    class azure.defender.easm.EasmClient: implements ContextManager 
        assets: AssetsOperations
        discovery_groups: DiscoveryGroupsOperations
        discovery_templates: DiscoveryTemplatesOperations
        reports: ReportsOperations
        saved_filters: SavedFiltersOperations
        tasks: TasksOperations

        def __init__(
                self, 
                endpoint: str, 
                resource_group_name: str, 
                subscription_id: str, 
                workspace_name: str, 
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
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.defender.easm.aio

    class azure.defender.easm.aio.EasmClient: implements AsyncContextManager 
        assets: AssetsOperations
        discovery_groups: DiscoveryGroupsOperations
        discovery_templates: DiscoveryTemplatesOperations
        reports: ReportsOperations
        saved_filters: SavedFiltersOperations
        tasks: TasksOperations

        def __init__(
                self, 
                endpoint: str, 
                resource_group_name: str, 
                subscription_id: str, 
                workspace_name: str, 
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
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.defender.easm.aio.operations

    class azure.defender.easm.aio.operations.AssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                asset_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                mark: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @overload
        async def update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def update(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.aio.operations.DiscoveryGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @distributed_trace
        def list_runs(
                self, 
                group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @overload
        async def put(
                self, 
                group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def put(
                self, 
                group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def run(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate(
                self, 
                group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def validate(
                self, 
                group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.aio.operations.DiscoveryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                template_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...


    class azure.defender.easm.aio.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def billable(self, **kwargs: Any) -> JSON: ...

        @overload
        async def snapshot(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def snapshot(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def summary(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def summary(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.aio.operations.SavedFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                filter_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                filter_name: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...

        @overload
        async def put(
                self, 
                filter_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def put(
                self, 
                filter_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> AsyncIterable[JSON]: ...


namespace azure.defender.easm.operations

    class azure.defender.easm.operations.AssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                asset_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                mark: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @overload
        def update(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def update(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.operations.DiscoveryGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @distributed_trace
        def list_runs(
                self, 
                group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @overload
        def put(
                self, 
                group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def put(
                self, 
                group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def run(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate(
                self, 
                group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def validate(
                self, 
                group_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.operations.DiscoveryTemplatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                template_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...


    class azure.defender.easm.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def billable(self, **kwargs: Any) -> JSON: ...

        @overload
        def snapshot(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def snapshot(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def summary(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def summary(
                self, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.operations.SavedFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                filter_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                filter_name: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...

        @overload
        def put(
                self, 
                filter_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def put(
                self, 
                filter_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


    class azure.defender.easm.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def cancel(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get(
                self, 
                task_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skip: int = 0, 
                **kwargs: Any
            ) -> Iterable[JSON]: ...


```