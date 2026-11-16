```py
namespace azure.mgmt.durabletask

    class azure.mgmt.durabletask.DurableTaskMgmtClient: implements ContextManager 
        detectors: DetectorsOperations
        failover_instances: FailoverInstancesOperations
        operations: Operations
        retention_policies: RetentionPoliciesOperations
        schedulers: SchedulersOperations
        task_hubs: TaskHubsOperations
        task_queues: TaskQueuesOperations
        transparent_data_encryptions: TransparentDataEncryptionsOperations

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


namespace azure.mgmt.durabletask.aio

    class azure.mgmt.durabletask.aio.DurableTaskMgmtClient: implements AsyncContextManager 
        detectors: DetectorsOperations
        failover_instances: FailoverInstancesOperations
        operations: Operations
        retention_policies: RetentionPoliciesOperations
        schedulers: SchedulersOperations
        task_hubs: TaskHubsOperations
        task_queues: TaskQueuesOperations
        transparent_data_encryptions: TransparentDataEncryptionsOperations

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


namespace azure.mgmt.durabletask.aio.operations

    class azure.mgmt.durabletask.aio.operations.DetectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'detector_id', 'accept']}, api_versions_list=['2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                detector_id: str, 
                **kwargs: Any
            ) -> Detector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Detector]: ...


    class azure.mgmt.durabletask.aio.operations.FailoverInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: FailoverInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverInstance]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: FailoverInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverInstance]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverInstance]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        async def begin_failover(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverInstance]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        async def begin_force_failover_allow_data_loss(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[FailoverInstance]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> FailoverInstance: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FailoverInstance]: ...


    class azure.mgmt.durabletask.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.durabletask.aio.operations.RetentionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RetentionPolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> RetentionPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RetentionPolicy]: ...


    class azure.mgmt.durabletask.aio.operations.SchedulersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        async def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Scheduler]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> Scheduler: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        async def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        async def get_private_link(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> SchedulerPrivateLinkResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Scheduler]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Scheduler]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_private_links(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchedulerPrivateLinkResource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        async def restart(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.durabletask.aio.operations.TaskHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskHub]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> TaskHub: ...

        @distributed_trace
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TaskHub]: ...


    class azure.mgmt.durabletask.aio.operations.TaskQueuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: TaskQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: TaskQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'task_queue_name']}, api_versions_list=['2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: TaskQueueUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: TaskQueueUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TaskQueue]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'task_queue_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                **kwargs: Any
            ) -> TaskQueue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_task_hub(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TaskQueue]: ...


    class azure.mgmt.durabletask.aio.operations.TransparentDataEncryptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransparentDataEncryption]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransparentDataEncryption]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[TransparentDataEncryption]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[TransparentDataEncryption]: ...


namespace azure.mgmt.durabletask.models

    class azure.mgmt.durabletask.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.durabletask.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.durabletask.models.Detector(ProxyResource):
        id: str
        name: str
        properties: Optional[DetectorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DetectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.DetectorDataset(_Model):
        rendering_properties: Optional[DetectorRenderingProperties]
        table: Optional[DetectorTable]


    class azure.mgmt.durabletask.models.DetectorMetadata(_Model):
        analysis_types: Optional[list[str]]
        author: Optional[str]
        category: Optional[str]
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        score: Optional[float]
        support_topic_list: Optional[list[str]]
        type: Optional[Union[str, DetectorType]]


    class azure.mgmt.durabletask.models.DetectorProperties(_Model):
        dataset: Optional[list[DetectorDataset]]
        metadata: Optional[DetectorMetadata]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[DetectorStatus]


    class azure.mgmt.durabletask.models.DetectorRenderingProperties(_Model):
        description: Optional[str]
        title: Optional[str]
        type: Optional[Union[int, DetectorRenderingType]]


    class azure.mgmt.durabletask.models.DetectorRenderingType(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_SUMMARY = 5
        DYNAMIC_INSIGHT = 8
        EMAIL_SNIPPET = 6
        INSIGHT = 7
        MARKDOWN = 9
        PIE_CHART = 4
        TABLE = 1
        TIME_SERIES_GRAPH = 2
        TIME_SERIES_PER_INSTANCE_GRAPH = 3


    class azure.mgmt.durabletask.models.DetectorStatus(_Model):
        message: Optional[str]
        status_id: Optional[Union[int, DetectorStatusId]]


    class azure.mgmt.durabletask.models.DetectorStatusId(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = 0
        INFO = 2
        NONE = 4
        SUCCESS = 3
        WARNING = 1


    class azure.mgmt.durabletask.models.DetectorTable(_Model):
        columns: Optional[list[DetectorTableColumn]]
        rows: Optional[list[list[Any]]]
        table_name: Optional[str]


    class azure.mgmt.durabletask.models.DetectorTableColumn(_Model):
        column_name: Optional[str]
        column_type: Optional[str]
        data_type: Optional[str]


    class azure.mgmt.durabletask.models.DetectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYSIS = "Analysis"
        CATEGORY_OVERVIEW = "CategoryOverview"
        DETECTOR = "Detector"


    class azure.mgmt.durabletask.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.durabletask.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.durabletask.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.FailoverInstance(ProxyResource):
        id: str
        name: str
        properties: Optional[FailoverInstanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FailoverInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.FailoverInstanceProperties(_Model):
        failover_state: Optional[Union[str, FailoverState]]
        partner_scheduler_location: Optional[str]
        partner_scheduler_resource_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication_role: Optional[Union[str, ReplicationRole]]

        @overload
        def __init__(
                self, 
                *, 
                partner_scheduler_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.FailoverState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.durabletask.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.durabletask.models.Operation(_Model):
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


    class azure.mgmt.durabletask.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.durabletask.models.OptionalPropertiesUpdateableProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.durabletask.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.durabletask.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.durabletask.models.PrivateEndpointConnectionUpdate(_Model):
        properties: Optional[OptionalPropertiesUpdateableProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OptionalPropertiesUpdateableProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.durabletask.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.durabletask.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.durabletask.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.durabletask.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.durabletask.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.durabletask.models.PurgeableOrchestrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        TERMINATED = "Terminated"


    class azure.mgmt.durabletask.models.RedundancyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        ZONE = "Zone"


    class azure.mgmt.durabletask.models.ReplicationRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.durabletask.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.durabletask.models.RetentionPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[RetentionPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RetentionPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.RetentionPolicyDetails(_Model):
        orchestration_state: Optional[Union[str, PurgeableOrchestrationState]]
        retention_period_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                orchestration_state: Optional[Union[str, PurgeableOrchestrationState]] = ..., 
                retention_period_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.RetentionPolicyProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retention_policies: Optional[list[RetentionPolicyDetails]]

        @overload
        def __init__(
                self, 
                *, 
                retention_policies: Optional[list[RetentionPolicyDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.Scheduler(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[SchedulerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[SchedulerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerPrivateLinkResource(Resource):
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


    class azure.mgmt.durabletask.models.SchedulerProperties(_Model):
        endpoint: Optional[str]
        ip_allowlist: list[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        sku: SchedulerSku

        @overload
        def __init__(
                self, 
                *, 
                ip_allowlist: list[str], 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: SchedulerSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerPropertiesUpdate(_Model):
        endpoint: Optional[str]
        ip_allowlist: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        sku: Optional[SchedulerSkuUpdate]

        @overload
        def __init__(
                self, 
                *, 
                ip_allowlist: Optional[list[str]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[SchedulerSkuUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerSku(_Model):
        capacity: Optional[int]
        name: Union[str, SchedulerSkuName]
        redundancy_state: Optional[Union[str, RedundancyState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SchedulerSkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSUMPTION = "Consumption"
        DEDICATED = "Dedicated"


    class azure.mgmt.durabletask.models.SchedulerSkuUpdate(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, SchedulerSkuName]]
        redundancy_state: Optional[Union[str, RedundancyState]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, SchedulerSkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SchedulerUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[SchedulerPropertiesUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[SchedulerPropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.SystemData(_Model):
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


    class azure.mgmt.durabletask.models.TaskHub(ProxyResource):
        id: str
        name: str
        properties: Optional[TaskHubProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TaskHubProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskHubProperties(_Model):
        capabilities: Optional[list[str]]
        dashboard_url: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskQueue(ProxyResource):
        id: str
        name: str
        properties: Optional[TaskQueueProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TaskQueueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskQueueProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        throughput: Optional[TaskQueueThroughput]

        @overload
        def __init__(
                self, 
                *, 
                throughput: Optional[TaskQueueThroughput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskQueueThroughput(_Model):
        actions_per_second: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                actions_per_second: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TaskQueueUpdate(_Model):
        properties: Optional[TaskQueueProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TaskQueueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TrackedResource(Resource):
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


    class azure.mgmt.durabletask.models.TransparentDataEncryption(ProxyResource):
        id: str
        name: str
        properties: Optional[TransparentDataEncryptionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TransparentDataEncryptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.TransparentDataEncryptionKeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED = "CustomerManaged"
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.durabletask.models.TransparentDataEncryptionProperties(_Model):
        auto_rotation_enabled: Optional[bool]
        key_source: Union[str, TransparentDataEncryptionKeySource]
        key_vault_key_uri: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                auto_rotation_enabled: Optional[bool] = ..., 
                key_source: Union[str, TransparentDataEncryptionKeySource], 
                key_vault_key_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.durabletask.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.durabletask.operations

    class azure.mgmt.durabletask.operations.DetectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'detector_id', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                detector_id: str, 
                **kwargs: Any
            ) -> Detector: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Detector]: ...


    class azure.mgmt.durabletask.operations.FailoverInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: FailoverInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverInstance]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: FailoverInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverInstance]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailoverInstance]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def begin_failover(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[FailoverInstance]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def begin_force_failover_allow_data_loss(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[FailoverInstance]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> FailoverInstance: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FailoverInstance]: ...


    class azure.mgmt.durabletask.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.durabletask.operations.RetentionPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: RetentionPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RetentionPolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> RetentionPolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-01-preview', params_added_on={'2025-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2025-04-01-preview', '2025-11-01', '2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RetentionPolicy]: ...


    class azure.mgmt.durabletask.operations.SchedulersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: Scheduler, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def begin_delete_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: SchedulerUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Scheduler]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> Scheduler: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def get_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def get_private_link(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> SchedulerPrivateLinkResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Scheduler]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Scheduler]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-02-01', params_added_on={'2026-02-01': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-02-01', '2026-05-01-preview', '2026-07-01-preview'])
        def list_private_links(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchedulerPrivateLinkResource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        def restart(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.durabletask.operations.TaskHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: TaskHub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskHub]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> TaskHub: ...

        @distributed_trace
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TaskHub]: ...


    class azure.mgmt.durabletask.operations.TaskQueuesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: TaskQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: TaskQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'task_queue_name']}, api_versions_list=['2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: TaskQueueUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: TaskQueueUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TaskQueue]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'task_queue_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                task_queue_name: str, 
                **kwargs: Any
            ) -> TaskQueue: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-01-preview', params_added_on={'2026-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'task_hub_name', 'accept']}, api_versions_list=['2026-07-01-preview'])
        def list_by_task_hub(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                task_hub_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TaskQueue]: ...


    class azure.mgmt.durabletask.operations.TransparentDataEncryptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransparentDataEncryption]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: TransparentDataEncryption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransparentDataEncryption]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[TransparentDataEncryption]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> TransparentDataEncryption: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduler_name', 'accept']}, api_versions_list=['2026-05-01-preview', '2026-07-01-preview'])
        def list_by_scheduler(
                self, 
                resource_group_name: str, 
                scheduler_name: str, 
                **kwargs: Any
            ) -> ItemPaged[TransparentDataEncryption]: ...


namespace azure.mgmt.durabletask.types

    class azure.mgmt.durabletask.types.FailoverInstance(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FailoverInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FailoverInstanceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.FailoverInstanceProperties(TypedDict, total=False):
        key "failoverState": Union[str, FailoverState]
        key "partnerSchedulerLocation": str
        key "partnerSchedulerResourceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "replicationRole": Union[str, ReplicationRole]
        failoverState: Union[str, FailoverState]
        partnerSchedulerLocation: str
        partnerSchedulerResourceId: str
        provisioningState: Union[str, ProvisioningState]
        replicationRole: Union[str, ReplicationRole]


    class azure.mgmt.durabletask.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.durabletask.types.OptionalPropertiesUpdateableProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState


    class azure.mgmt.durabletask.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.durabletask.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.durabletask.types.PrivateEndpointConnectionUpdate(TypedDict, total=False):
        key "properties": ForwardRef('OptionalPropertiesUpdateableProperties', module='types')
        properties: OptionalPropertiesUpdateableProperties


    class azure.mgmt.durabletask.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.durabletask.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.RetentionPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RetentionPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RetentionPolicyProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.RetentionPolicyDetails(TypedDict, total=False):
        key "orchestrationState": Union[str, PurgeableOrchestrationState]
        key "retentionPeriodInDays": Required[int]
        orchestrationState: Union[str, PurgeableOrchestrationState]
        retentionPeriodInDays: int


    class azure.mgmt.durabletask.types.RetentionPolicyProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioningState: Union[str, ProvisioningState]
        retentionPolicies: list[RetentionPolicyDetails]


    class azure.mgmt.durabletask.types.Scheduler(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SchedulerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SchedulerProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.durabletask.types.SchedulerProperties(TypedDict, total=False):
        key "endpoint": str
        key "ipAllowlist": Required[list[str]]
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "sku": Required[SchedulerSku]
        endpoint: str
        ipAllowlist: list[str]
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, ProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        sku: SchedulerSku


    class azure.mgmt.durabletask.types.SchedulerPropertiesUpdate(TypedDict, total=False):
        key "endpoint": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "sku": ForwardRef('SchedulerSkuUpdate', module='types')
        endpoint: str
        ipAllowlist: list[str]
        provisioningState: Union[str, ProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        sku: SchedulerSkuUpdate


    class azure.mgmt.durabletask.types.SchedulerSku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[Union[str, SchedulerSkuName]]
        key "redundancyState": Union[str, RedundancyState]
        capacity: int
        name: Union[str, SchedulerSkuName]
        redundancyState: Union[str, RedundancyState]


    class azure.mgmt.durabletask.types.SchedulerSkuUpdate(TypedDict, total=False):
        key "capacity": int
        key "name": Union[str, SchedulerSkuName]
        key "redundancyState": Union[str, RedundancyState]
        capacity: int
        name: Union[str, SchedulerSkuName]
        redundancyState: Union[str, RedundancyState]


    class azure.mgmt.durabletask.types.SchedulerUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('SchedulerPropertiesUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: SchedulerPropertiesUpdate
        tags: dict[str, str]


    class azure.mgmt.durabletask.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.durabletask.types.TaskHub(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TaskHubProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TaskHubProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.TaskHubProperties(TypedDict, total=False):
        key "dashboardUrl": str
        key "provisioningState": Union[str, ProvisioningState]
        capabilities: list[str]
        dashboardUrl: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.durabletask.types.TaskQueue(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TaskQueueProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TaskQueueProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.TaskQueueProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "throughput": ForwardRef('TaskQueueThroughput', module='types')
        provisioningState: Union[str, ProvisioningState]
        throughput: TaskQueueThroughput


    class azure.mgmt.durabletask.types.TaskQueueThroughput(TypedDict, total=False):
        key "actionsPerSecond": int
        actionsPerSecond: int


    class azure.mgmt.durabletask.types.TaskQueueUpdate(TypedDict, total=False):
        key "properties": ForwardRef('TaskQueueProperties', module='types')
        properties: TaskQueueProperties


    class azure.mgmt.durabletask.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.durabletask.types.TransparentDataEncryption(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TransparentDataEncryptionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TransparentDataEncryptionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.durabletask.types.TransparentDataEncryptionProperties(TypedDict, total=False):
        key "autoRotationEnabled": bool
        key "keySource": Required[Union[str, TransparentDataEncryptionKeySource]]
        key "keyVaultKeyUri": str
        key "provisioningState": Union[str, ProvisioningState]
        autoRotationEnabled: bool
        keySource: Union[str, TransparentDataEncryptionKeySource]
        keyVaultKeyUri: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.durabletask.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```