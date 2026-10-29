```py
namespace azure.mgmt.discovery

    class azure.mgmt.discovery.DiscoveryMgmtClient: implements ContextManager 
        bookshelf_private_endpoint_connections: BookshelfPrivateEndpointConnectionsOperations
        bookshelf_private_link_resources: BookshelfPrivateLinkResourcesOperations
        bookshelves: BookshelvesOperations
        chat_model_deployments: ChatModelDeploymentsOperations
        node_pools: NodePoolsOperations
        operations: Operations
        projects: ProjectsOperations
        storage_assets: StorageAssetsOperations
        storage_containers: StorageContainersOperations
        supercomputers: SupercomputersOperations
        tools: ToolsOperations
        workspace_private_endpoint_connections: WorkspacePrivateEndpointConnectionsOperations
        workspace_private_link_resources: WorkspacePrivateLinkResourcesOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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


namespace azure.mgmt.discovery.aio

    class azure.mgmt.discovery.aio.DiscoveryMgmtClient: implements AsyncContextManager 
        bookshelf_private_endpoint_connections: BookshelfPrivateEndpointConnectionsOperations
        bookshelf_private_link_resources: BookshelfPrivateLinkResourcesOperations
        bookshelves: BookshelvesOperations
        chat_model_deployments: ChatModelDeploymentsOperations
        node_pools: NodePoolsOperations
        operations: Operations
        projects: ProjectsOperations
        storage_assets: StorageAssetsOperations
        storage_containers: StorageContainersOperations
        supercomputers: SupercomputersOperations
        tools: ToolsOperations
        workspace_private_endpoint_connections: WorkspacePrivateEndpointConnectionsOperations
        workspace_private_link_resources: WorkspacePrivateLinkResourcesOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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


namespace azure.mgmt.discovery.aio.operations

    class azure.mgmt.discovery.aio.operations.BookshelfPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: BookshelfPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BookshelfPrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: BookshelfPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BookshelfPrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BookshelfPrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> BookshelfPrivateEndpointConnection: ...

        @distributed_trace
        def list_by_bookshelf(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BookshelfPrivateEndpointConnection]: ...


    class azure.mgmt.discovery.aio.operations.BookshelfPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> BookshelfPrivateLinkResource: ...

        @distributed_trace
        def list_by_bookshelf(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BookshelfPrivateLinkResource]: ...


    class azure.mgmt.discovery.aio.operations.BookshelvesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bookshelf]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> Bookshelf: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Bookshelf]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Bookshelf]: ...


    class azure.mgmt.discovery.aio.operations.ChatModelDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChatModelDeployment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                **kwargs: Any
            ) -> ChatModelDeployment: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatModelDeployment]: ...


    class azure.mgmt.discovery.aio.operations.NodePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NodePool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> NodePool: ...

        @distributed_trace
        def list_by_supercomputer(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NodePool]: ...


    class azure.mgmt.discovery.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.discovery.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...


    class azure.mgmt.discovery.aio.operations.StorageAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageAsset]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                **kwargs: Any
            ) -> StorageAsset: ...

        @distributed_trace
        def list_by_storage_container(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageAsset]: ...


    class azure.mgmt.discovery.aio.operations.StorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageContainer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageContainer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StorageContainer]: ...


    class azure.mgmt.discovery.aio.operations.SupercomputersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Supercomputer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> Supercomputer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Supercomputer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Supercomputer]: ...


    class azure.mgmt.discovery.aio.operations.ToolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Tool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                **kwargs: Any
            ) -> Tool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Tool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Tool]: ...


    class azure.mgmt.discovery.aio.operations.WorkspacePrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: WorkspacePrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspacePrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: WorkspacePrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspacePrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspacePrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> WorkspacePrivateEndpointConnection: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspacePrivateEndpointConnection]: ...


    class azure.mgmt.discovery.aio.operations.WorkspacePrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> WorkspacePrivateLinkResource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspacePrivateLinkResource]: ...


    class azure.mgmt.discovery.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workspace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Workspace]: ...


namespace azure.mgmt.discovery.models

    class azure.mgmt.discovery.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.discovery.models.AzureNetAppFilesStore(StorageStore, discriminator='AzureNetAppFiles'):
        kind: Literal[StorageStoreType.AZURE_NET_APP_FILES]
        mount_protocol: Optional[Union[str, NetAppMountProtocol]]
        net_app_volume_id: str

        @overload
        def __init__(
                self, 
                *, 
                mount_protocol: Optional[Union[str, NetAppMountProtocol]] = ..., 
                net_app_volume_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.AzureStorageBlobStore(StorageStore, discriminator='AzureStorageBlob'):
        kind: Literal[StorageStoreType.AZURE_STORAGE_BLOB]
        mount_protocol: Optional[Union[str, BlobStorageMountProtocol]]
        storage_account_id: str

        @overload
        def __init__(
                self, 
                *, 
                mount_protocol: Optional[Union[str, BlobStorageMountProtocol]] = ..., 
                storage_account_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.BlobStorageMountProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOBFUSE_CACHING = "BlobfuseCaching"
        NFS = "NFS"


    class azure.mgmt.discovery.models.Bookshelf(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[BookshelfProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[BookshelfProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.BookshelfKeyVaultProperties(_Model):
        identity_client_id: str
        key_name: str
        key_vault_uri: str
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_client_id: str, 
                key_name: str, 
                key_vault_uri: str, 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.BookshelfPrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.BookshelfPrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.BookshelfProperties(_Model):
        bookshelf_uri: Optional[str]
        customer_managed_keys: Optional[Union[str, CustomerManagedKeys]]
        key_vault_properties: Optional[BookshelfKeyVaultProperties]
        log_analytics_cluster_id: Optional[str]
        managed_on_behalf_of_configuration: Optional[WithMoboBrokerResources]
        managed_resource_group: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        private_endpoint_subnet_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        search_subnet_id: Optional[str]
        workload_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_keys: Optional[Union[str, CustomerManagedKeys]] = ..., 
                key_vault_properties: Optional[BookshelfKeyVaultProperties] = ..., 
                log_analytics_cluster_id: Optional[str] = ..., 
                private_endpoint_subnet_id: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                search_subnet_id: Optional[str] = ..., 
                workload_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ChatModelDeployment(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ChatModelDeploymentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ChatModelDeploymentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ChatModelDeploymentProperties(_Model):
        capacity: Optional[int]
        model_format: str
        model_name: str
        model_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sku_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                model_format: str, 
                model_name: str, 
                model_version: Optional[str] = ..., 
                sku_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.discovery.models.CustomerManagedKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.discovery.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.discovery.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.discovery.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.Identity(_Model):
        client_id: Optional[str]
        id: str
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.KeyVaultProperties(_Model):
        key_name: str
        key_vault_uri: str
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_uri: str, 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.MoboBrokerResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.NetAppMountProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"


    class azure.mgmt.discovery.models.NetworkEgressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOAD_BALANCER = "LoadBalancer"
        NONE = "None"


    class azure.mgmt.discovery.models.NodePool(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[NodePoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NodePoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.NodePoolProperties(_Model):
        image_cache_lower_threshold: Optional[int]
        image_cache_upper_threshold: Optional[int]
        max_node_count: int
        min_node_count: Optional[int]
        os_disk_size_gb: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scale_set_priority: Optional[Union[str, ScaleSetPriority]]
        subnet_id: str
        vm_size: Union[str, VmSize]

        @overload
        def __init__(
                self, 
                *, 
                image_cache_lower_threshold: Optional[int] = ..., 
                image_cache_upper_threshold: Optional[int] = ..., 
                max_node_count: int, 
                min_node_count: Optional[int] = ..., 
                os_disk_size_gb: Optional[int] = ..., 
                scale_set_priority: Optional[Union[str, ScaleSetPriority]] = ..., 
                subnet_id: str, 
                vm_size: Union[str, VmSize]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.discovery.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.discovery.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.discovery.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.discovery.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.discovery.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.Project(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProjectProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ProjectProperties(_Model):
        foundry_project_endpoint: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        settings: Optional[ProjectSettings]
        storage_container_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                settings: Optional[ProjectSettings] = ..., 
                storage_container_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ProjectSettings(_Model):
        behavior_preferences: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                behavior_preferences: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.discovery.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.discovery.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.discovery.models.ScaleSetPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.discovery.models.StorageAsset(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StorageAssetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StorageAssetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.StorageAssetProperties(_Model):
        description: str
        path: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.StorageContainer(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[StorageContainerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[StorageContainerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.StorageContainerProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_store: StorageStore

        @overload
        def __init__(
                self, 
                *, 
                storage_store: StorageStore
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.StorageStore(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.StorageStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_NET_APP_FILES = "AzureNetAppFiles"
        AZURE_STORAGE_BLOB = "AzureStorageBlob"


    class azure.mgmt.discovery.models.Supercomputer(TrackedResource):
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: str
        name: str
        properties: Optional[SupercomputerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[SupercomputerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.SupercomputerIdentities(_Model):
        cluster_identity: Identity
        kubelet_identity: Identity
        workload_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_identity: Identity, 
                kubelet_identity: Identity, 
                workload_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.SupercomputerProperties(_Model):
        customer_managed_keys: Optional[Union[str, CustomerManagedKeys]]
        disk_encryption_set_id: Optional[str]
        identities: SupercomputerIdentities
        log_analytics_cluster_id: Optional[str]
        managed_on_behalf_of_configuration: Optional[WithMoboBrokerResources]
        managed_resource_group: Optional[str]
        management_subnet_id: Optional[str]
        outbound_type: Optional[Union[str, NetworkEgressType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        subnet_id: str
        system_sku: Optional[Union[str, SystemSku]]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_keys: Optional[Union[str, CustomerManagedKeys]] = ..., 
                disk_encryption_set_id: Optional[str] = ..., 
                identities: SupercomputerIdentities, 
                log_analytics_cluster_id: Optional[str] = ..., 
                management_subnet_id: Optional[str] = ..., 
                outbound_type: Optional[Union[str, NetworkEgressType]] = ..., 
                subnet_id: str, 
                system_sku: Optional[Union[str, SystemSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.SystemAssignedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, SystemAssignedServiceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SystemAssignedServiceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.SystemAssignedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.discovery.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.SystemSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_D4_S_V4 = "Standard_D4s_v4"
        STANDARD_D4_S_V5 = "Standard_D4s_v5"
        STANDARD_D4_S_V6 = "Standard_D4s_v6"


    class azure.mgmt.discovery.models.Tool(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ToolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ToolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.ToolProperties(_Model):
        definition_content: dict[str, Any]
        environment_variables: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                definition_content: dict[str, Any], 
                environment_variables: Optional[dict[str, str]] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.discovery.models.VmSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_NC16_AS_T4_V3 = "Standard_NC16as_T4_v3"
        STANDARD_NC24_ADS_A100_V4 = "Standard_NC24ads_A100_v4"
        STANDARD_NC48_ADS_A100_V4 = "Standard_NC48ads_A100_v4"
        STANDARD_NC4_AS_T4_V3 = "Standard_NC4as_T4_v3"
        STANDARD_NC64_AS_T4_V3 = "Standard_NC64as_T4_v3"
        STANDARD_NC8_AS_T4_V3 = "Standard_NC8as_T4_v3"
        STANDARD_NC96_ADS_A100_V4 = "Standard_NC96ads_A100_v4"
        STANDARD_ND40_RS_V2 = "Standard_ND40rs_v2"
        STANDARD_NV12_ADS_A10_V5 = "Standard_NV12ads_A10_v5"
        STANDARD_NV24_ADS_A10_V5 = "Standard_NV24ads_A10_v5"
        STANDARD_NV36_ADMS_A10_V5 = "Standard_NV36adms_A10_v5"
        STANDARD_NV36_ADS_A10_V5 = "Standard_NV36ads_A10_v5"
        STANDARD_NV6_ADS_A10_V5 = "Standard_NV6ads_A10_v5"
        STANDARD_NV72_ADS_A10_V5 = "Standard_NV72ads_A10_v5"


    class azure.mgmt.discovery.models.WithMoboBrokerResources(_Model):
        mobo_broker_resources: Optional[list[MoboBrokerResource]]


    class azure.mgmt.discovery.models.Workspace(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WorkspaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WorkspaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.WorkspacePrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.WorkspacePrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.discovery.models.WorkspaceProperties(_Model):
        agent_subnet_id: Optional[str]
        customer_managed_keys: Optional[Union[str, CustomerManagedKeys]]
        key_vault_properties: Optional[KeyVaultProperties]
        log_analytics_cluster_id: Optional[str]
        managed_on_behalf_of_configuration: Optional[WithMoboBrokerResources]
        managed_resource_group: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        private_endpoint_subnet_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        supercomputer_ids: Optional[list[str]]
        workspace_api_uri: Optional[str]
        workspace_identity: Identity
        workspace_subnet_id: Optional[str]
        workspace_ui_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_subnet_id: Optional[str] = ..., 
                customer_managed_keys: Optional[Union[str, CustomerManagedKeys]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                log_analytics_cluster_id: Optional[str] = ..., 
                private_endpoint_subnet_id: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                supercomputer_ids: Optional[list[str]] = ..., 
                workspace_identity: Identity, 
                workspace_subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.discovery.operations

    class azure.mgmt.discovery.operations.BookshelfPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: BookshelfPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BookshelfPrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: BookshelfPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BookshelfPrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BookshelfPrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> BookshelfPrivateEndpointConnection: ...

        @distributed_trace
        def list_by_bookshelf(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BookshelfPrivateEndpointConnection]: ...


    class azure.mgmt.discovery.operations.BookshelfPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> BookshelfPrivateLinkResource: ...

        @distributed_trace
        def list_by_bookshelf(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BookshelfPrivateLinkResource]: ...


    class azure.mgmt.discovery.operations.BookshelvesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: Bookshelf, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bookshelf]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                bookshelf_name: str, 
                **kwargs: Any
            ) -> Bookshelf: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Bookshelf]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Bookshelf]: ...


    class azure.mgmt.discovery.operations.ChatModelDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: ChatModelDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChatModelDeployment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                chat_model_deployment_name: str, 
                **kwargs: Any
            ) -> ChatModelDeployment: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ChatModelDeployment]: ...


    class azure.mgmt.discovery.operations.NodePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: NodePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NodePool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                node_pool_name: str, 
                **kwargs: Any
            ) -> NodePool: ...

        @distributed_trace
        def list_by_supercomputer(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NodePool]: ...


    class azure.mgmt.discovery.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.discovery.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...


    class azure.mgmt.discovery.operations.StorageAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: StorageAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageAsset]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                storage_asset_name: str, 
                **kwargs: Any
            ) -> StorageAsset: ...

        @distributed_trace
        def list_by_storage_container(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageAsset]: ...


    class azure.mgmt.discovery.operations.StorageContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: StorageContainer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageContainer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_container_name: str, 
                **kwargs: Any
            ) -> StorageContainer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageContainer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StorageContainer]: ...


    class azure.mgmt.discovery.operations.SupercomputersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: Supercomputer, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Supercomputer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                supercomputer_name: str, 
                **kwargs: Any
            ) -> Supercomputer: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Supercomputer]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Supercomputer]: ...


    class azure.mgmt.discovery.operations.ToolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: Tool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Tool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                tool_name: str, 
                **kwargs: Any
            ) -> Tool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Tool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Tool]: ...


    class azure.mgmt.discovery.operations.WorkspacePrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: WorkspacePrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspacePrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: WorkspacePrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspacePrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspacePrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> WorkspacePrivateEndpointConnection: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkspacePrivateEndpointConnection]: ...


    class azure.mgmt.discovery.operations.WorkspacePrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> WorkspacePrivateLinkResource: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkspacePrivateLinkResource]: ...


    class azure.mgmt.discovery.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workspace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Workspace]: ...


namespace azure.mgmt.discovery.types

    class azure.mgmt.discovery.types.AzureNetAppFilesStore(TypedDict, total=False):
        key "kind": Required[Literal[StorageStoreType.AZURE_NET_APP_FILES]]
        key "mountProtocol": Union[str, NetAppMountProtocol]
        key "netAppVolumeId": Required[str]
        kind: Literal[StorageStoreType.AZURE_NET_APP_FILES]
        mount_protocol: Union[str, NetAppMountProtocol]
        net_app_volume_id: str


    class azure.mgmt.discovery.types.AzureStorageBlobStore(TypedDict, total=False):
        key "kind": Required[Literal[StorageStoreType.AZURE_STORAGE_BLOB]]
        key "mountProtocol": Union[str, BlobStorageMountProtocol]
        key "storageAccountId": Required[str]
        kind: Literal[StorageStoreType.AZURE_STORAGE_BLOB]
        mount_protocol: Union[str, BlobStorageMountProtocol]
        storage_account_id: str


    class azure.mgmt.discovery.types.Bookshelf(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('BookshelfProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: BookshelfProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.BookshelfKeyVaultProperties(TypedDict, total=False):
        key "identityClientId": Required[str]
        key "keyName": Required[str]
        key "keyVaultUri": Required[str]
        key "keyVersion": str
        identity_client_id: str
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.discovery.types.BookshelfPrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.types.BookshelfProperties(TypedDict, total=False):
        key "bookshelfUri": str
        key "customerManagedKeys": Union[str, CustomerManagedKeys]
        key "keyVaultProperties": ForwardRef('BookshelfKeyVaultProperties', module='types')
        key "logAnalyticsClusterId": str
        key "managedOnBehalfOfConfiguration": ForwardRef('WithMoboBrokerResources', module='types')
        key "managedResourceGroup": str
        key "privateEndpointSubnetId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "searchSubnetId": str
        bookshelf_uri: str
        customer_managed_keys: Union[str, CustomerManagedKeys]
        key_vault_properties: BookshelfKeyVaultProperties
        log_analytics_cluster_id: str
        managed_on_behalf_of_configuration: WithMoboBrokerResources
        managed_resource_group: str
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        private_endpoint_subnet_id: str
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        search_subnet_id: str
        workloadIdentities: dict[str, UserAssignedIdentity]
        workload_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.discovery.types.ChatModelDeployment(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ChatModelDeploymentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ChatModelDeploymentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.ChatModelDeploymentProperties(TypedDict, total=False):
        key "capacity": int
        key "modelFormat": Required[str]
        key "modelName": Required[str]
        key "modelVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "skuName": str
        capacity: int
        model_format: str
        model_name: str
        model_version: str
        provisioning_state: Union[str, ProvisioningState]
        sku_name: str


    class azure.mgmt.discovery.types.Identity(TypedDict, total=False):
        key "clientId": str
        key "id": Required[str]
        key "principalId": str
        client_id: str
        id: str
        principal_id: str


    class azure.mgmt.discovery.types.KeyVaultProperties(TypedDict, total=False):
        key "keyName": Required[str]
        key "keyVaultUri": Required[str]
        key "keyVersion": str
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.discovery.types.MoboBrokerResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.discovery.types.NodePool(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NodePoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NodePoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.NodePoolProperties(TypedDict, total=False):
        key "imageCacheLowerThreshold": int
        key "imageCacheUpperThreshold": int
        key "maxNodeCount": Required[int]
        key "minNodeCount": int
        key "osDiskSizeGb": int
        key "provisioningState": Union[str, ProvisioningState]
        key "scaleSetPriority": Union[str, ScaleSetPriority]
        key "subnetId": Required[str]
        key "vmSize": Required[Union[str, VmSize]]
        image_cache_lower_threshold: int
        image_cache_upper_threshold: int
        max_node_count: int
        min_node_count: int
        os_disk_size_gb: int
        provisioning_state: Union[str, ProvisioningState]
        scale_set_priority: Union[str, ScaleSetPriority]
        subnet_id: str
        vm_size: Union[str, VmSize]


    class azure.mgmt.discovery.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.discovery.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        group_ids: list[str]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.discovery.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.discovery.types.Project(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ProjectProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.ProjectProperties(TypedDict, total=False):
        key "foundryProjectEndpoint": str
        key "provisioningState": Union[str, ProvisioningState]
        key "settings": ForwardRef('ProjectSettings', module='types')
        foundry_project_endpoint: str
        provisioning_state: Union[str, ProvisioningState]
        settings: ProjectSettings
        storageContainerIds: list[str]
        storage_container_ids: list[str]


    class azure.mgmt.discovery.types.ProjectSettings(TypedDict, total=False):
        key "behaviorPreferences": str
        behavior_preferences: str


    class azure.mgmt.discovery.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.types.StorageAsset(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageAssetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageAssetProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.StorageAssetProperties(TypedDict, total=False):
        key "description": Required[str]
        key "path": str
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        path: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.discovery.types.StorageContainer(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('StorageContainerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: StorageContainerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.StorageContainerProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "storageStore": Required[StorageStore]
        provisioning_state: Union[str, ProvisioningState]
        storage_store: StorageStore


    class azure.mgmt.discovery.types.StorageStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_NET_APP_FILES = "AzureNetAppFiles"
        AZURE_STORAGE_BLOB = "AzureStorageBlob"


    class azure.mgmt.discovery.types.Supercomputer(TrackedResource):
        key "id": str
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SupercomputerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: SystemAssignedServiceIdentity
        location: str
        name: str
        properties: SupercomputerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.SupercomputerIdentities(TypedDict, total=False):
        key "clusterIdentity": Required[Identity]
        key "kubeletIdentity": Required[Identity]
        cluster_identity: Identity
        kubelet_identity: Identity
        workloadIdentities: dict[str, UserAssignedIdentity]
        workload_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.discovery.types.SupercomputerProperties(TypedDict, total=False):
        key "customerManagedKeys": Union[str, CustomerManagedKeys]
        key "diskEncryptionSetId": str
        key "identities": Required[SupercomputerIdentities]
        key "logAnalyticsClusterId": str
        key "managedOnBehalfOfConfiguration": ForwardRef('WithMoboBrokerResources', module='types')
        key "managedResourceGroup": str
        key "managementSubnetId": str
        key "outboundType": Union[str, NetworkEgressType]
        key "provisioningState": Union[str, ProvisioningState]
        key "subnetId": Required[str]
        key "systemSku": Union[str, SystemSku]
        customer_managed_keys: Union[str, CustomerManagedKeys]
        disk_encryption_set_id: str
        identities: SupercomputerIdentities
        log_analytics_cluster_id: str
        managed_on_behalf_of_configuration: WithMoboBrokerResources
        managed_resource_group: str
        management_subnet_id: str
        outbound_type: Union[str, NetworkEgressType]
        provisioning_state: Union[str, ProvisioningState]
        subnet_id: str
        system_sku: Union[str, SystemSku]


    class azure.mgmt.discovery.types.SystemAssignedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, SystemAssignedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, SystemAssignedServiceIdentityType]


    class azure.mgmt.discovery.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.discovery.types.Tool(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ToolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ToolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.ToolProperties(TypedDict, total=False):
        key "definitionContent": Required[dict[str, Any]]
        key "provisioningState": Union[str, ProvisioningState]
        key "version": Required[str]
        definition_content: dict[str, Any]
        environmentVariables: dict[str, str]
        environment_variables: dict[str, str]
        provisioning_state: Union[str, ProvisioningState]
        version: str


    class azure.mgmt.discovery.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.discovery.types.WithMoboBrokerResources(TypedDict, total=False):
        moboBrokerResources: list[MoboBrokerResource]
        mobo_broker_resources: list[MoboBrokerResource]


    class azure.mgmt.discovery.types.Workspace(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: WorkspaceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.discovery.types.WorkspacePrivateEndpointConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.discovery.types.WorkspaceProperties(TypedDict, total=False):
        key "agentSubnetId": str
        key "customerManagedKeys": Union[str, CustomerManagedKeys]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        key "logAnalyticsClusterId": str
        key "managedOnBehalfOfConfiguration": ForwardRef('WithMoboBrokerResources', module='types')
        key "managedResourceGroup": str
        key "privateEndpointSubnetId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "workspaceApiUri": str
        key "workspaceIdentity": Required[Identity]
        key "workspaceSubnetId": str
        key "workspaceUiUri": str
        agent_subnet_id: str
        customer_managed_keys: Union[str, CustomerManagedKeys]
        key_vault_properties: KeyVaultProperties
        log_analytics_cluster_id: str
        managed_on_behalf_of_configuration: WithMoboBrokerResources
        managed_resource_group: str
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        private_endpoint_subnet_id: str
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        supercomputerIds: list[str]
        supercomputer_ids: list[str]
        workspace_api_uri: str
        workspace_identity: Identity
        workspace_subnet_id: str
        workspace_ui_uri: str


```