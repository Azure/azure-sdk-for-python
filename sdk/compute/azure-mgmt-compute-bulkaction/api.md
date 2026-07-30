```py
namespace azure.mgmt.compute.bulkaction

    class azure.mgmt.compute.bulkaction.ComputeBulkActionsMgmtClient: implements ContextManager 
        bulk_create_custom: BulkCreateCustomOperations
        launch_bulk_instances_operation: LaunchBulkInstancesOperationOperations
        occurrence_extension: OccurrenceExtensionOperations
        occurrences: OccurrencesOperations
        operations: Operations
        scheduled_action_extension: ScheduledActionExtensionOperations
        scheduled_action_operation_status: ScheduledActionOperationStatusOperations
        scheduled_actions: ScheduledActionsOperations
        virtual_machine_bulk_operations: VirtualMachineBulkOperationsOperations

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


namespace azure.mgmt.compute.bulkaction.aio

    class azure.mgmt.compute.bulkaction.aio.ComputeBulkActionsMgmtClient: implements AsyncContextManager 
        bulk_create_custom: BulkCreateCustomOperations
        launch_bulk_instances_operation: LaunchBulkInstancesOperationOperations
        occurrence_extension: OccurrenceExtensionOperations
        occurrences: OccurrencesOperations
        operations: Operations
        scheduled_action_extension: ScheduledActionExtensionOperations
        scheduled_action_operation_status: ScheduledActionOperationStatusOperations
        scheduled_actions: ScheduledActionsOperations
        virtual_machine_bulk_operations: VirtualMachineBulkOperationsOperations

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


namespace azure.mgmt.compute.bulkaction.aio.operations

    class azure.mgmt.compute.bulkaction.aio.operations.BulkCreateCustomOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name']}, api_versions_list=['2026-07-06-preview'])
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedBulkCreateCustom, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedBulkCreateCustom]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedBulkCreateCustom, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedBulkCreateCustom]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedBulkCreateCustom]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'delete_instances']}, api_versions_list=['2026-07-06-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedBulkCreateCustom: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'async_operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get_async_operation_status(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedBulkCreateCustom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedBulkCreateCustom]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.LaunchBulkInstancesOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name']}, api_versions_list=['2026-07-06-preview'])
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'delete_instances']}, api_versions_list=['2026-07-06-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedLaunchBulkInstancesOperation: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'async_operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get_operation_status(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'filter', 'skiptoken', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.OccurrenceExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_occurrence_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OccurrenceExtensionResource]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.OccurrencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: DelayRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: DelayRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_scheduled_action(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Occurrence]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OccurrenceResource]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.ScheduledActionExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledActionResources]: ...


    class azure.mgmt.compute.bulkaction.aio.operations.ScheduledActionOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.compute.bulkaction.aio.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScheduledAction]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScheduledAction]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScheduledAction]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @overload
        async def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceOperationResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        async def begin_disable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        async def begin_enable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def begin_trigger_manual_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Occurrence]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledActionResource]: ...

        @overload
        async def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...

        @overload
        async def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...

        @overload
        async def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...


    class azure.mgmt.compute.bulkaction.aio.operations.VirtualMachineBulkOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: AcknowledgeBulkOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        async def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: AcknowledgeBulkOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        async def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        async def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: CancelOperationsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: CancelOperationsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteCreateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteCreateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeallocateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeallocateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeleteContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeleteContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: GetOperationStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: GetOperationStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteHibernateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteHibernateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'lookback_in_minutes', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def bulk_list_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                *, 
                lookback_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceOperation]: ...

        @overload
        async def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteReimageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        async def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteReimageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        async def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        async def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteStartContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteStartContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteVdiCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteVdiCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...


namespace azure.mgmt.compute.bulkaction.models

    class azure.mgmt.compute.bulkaction.models.AcceleratorManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        NVIDIA = "Nvidia"
        XILINX = "Xilinx"


    class azure.mgmt.compute.bulkaction.models.AcceleratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FPGA = "FPGA"
        GPU = "GPU"


    class azure.mgmt.compute.bulkaction.models.AcknowledgeBulkOperationErrorsRequest(_Model):
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.AcknowledgeBulkOperationErrorsResponse(_Model):
        acknowledged: list[str]
        not_found: list[str]
        skipped: list[str]

        @overload
        def __init__(
                self, 
                *, 
                acknowledged: list[str], 
                not_found: list[str], 
                skipped: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.compute.bulkaction.models.AdditionalCapabilities(_Model):
        hibernation_enabled: Optional[bool]
        ultra_ssd_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                hibernation_enabled: Optional[bool] = ..., 
                ultra_ssd_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.AdditionalUnattendContent(_Model):
        component_name: Optional[Literal["Microsoft-Windows-Shell-Setup"]]
        content: Optional[str]
        pass_name: Optional[Literal["OobeSystem"]]
        setting_name: Optional[Union[str, SettingNames]]

        @overload
        def __init__(
                self, 
                *, 
                component_name: Optional[Literal[Microsoft-Windows-Shell-Setup]] = ..., 
                content: Optional[str] = ..., 
                pass_name: Optional[Literal[OobeSystem]] = ..., 
                setting_name: Optional[Union[str, SettingNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.AllInstancesDown(_Model):
        all_instances_down_automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                all_instances_down_automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.AllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OPTIMIZED = "CapacityOptimized"
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.compute.bulkaction.models.ApiEntityReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ApiError(_Model):
        code: Optional[str]
        details: Optional[list[ApiErrorBase]]
        innererror: Optional[BulkInstancesInnerError]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ApiErrorBase]] = ..., 
                innererror: Optional[BulkInstancesInnerError] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ApiErrorBase(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ApplicationProfile(_Model):
        gallery_applications: Optional[list[VMGalleryApplication]]

        @overload
        def __init__(
                self, 
                *, 
                gallery_applications: Optional[list[VMGalleryApplication]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ArchitectureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "ARM64"
        X64 = "X64"


    class azure.mgmt.compute.bulkaction.models.BootDiagnostics(_Model):
        enabled: Optional[bool]
        storage_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                storage_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkActionVmExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[dict[str, Any]]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        provision_after_extensions: Optional[list[str]]
        publisher: Optional[str]
        settings: Optional[dict[str, Any]]
        suppress_failures: Optional[bool]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                protected_settings: Optional[dict[str, Any]] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[dict[str, Any]] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomAllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomDistributionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT_BALANCED = "BestEffortBalanced"
        BEST_EFFORT_SINGLE_ZONE = "BestEffortSingleZone"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomOverride(_Model):
        extensions: Optional[list[BulkactionVMExtension]]
        identity: Optional[VirtualMachineIdentity]
        plan: Optional[Plan]
        tags: Optional[dict[str, str]]
        virtual_machine_name: Optional[str]
        virtual_machine_profile: Optional[BulkactionVMProperties]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[list[BulkactionVMExtension]] = ..., 
                identity: Optional[VirtualMachineIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                virtual_machine_name: Optional[str] = ..., 
                virtual_machine_profile: Optional[BulkactionVMProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomOverrideBase(_Model):
        extensions: Optional[list[BulkactionVMExtension]]
        identity: Optional[VirtualMachineIdentity]
        plan: Optional[Plan]
        tags: Optional[dict[str, str]]
        virtual_machine_profile: Optional[BulkactionVMProperties]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[list[BulkactionVMExtension]] = ..., 
                identity: Optional[VirtualMachineIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                virtual_machine_profile: Optional[BulkactionVMProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomOverridesProfile(_Model):
        overrides: Optional[list[BulkCreateCustomOverride]]
        virtual_machine_name_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                overrides: Optional[list[BulkCreateCustomOverride]] = ..., 
                virtual_machine_name_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomPriorityProfile(_Model):
        allocation_strategy: Optional[Union[str, BulkCreateCustomAllocationStrategy]]
        eviction_policy: Optional[Union[str, EvictionPolicy]]
        max_price_per_vm: Optional[float]
        type: Optional[Union[str, PriorityType]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, BulkCreateCustomAllocationStrategy]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                max_price_per_vm: Optional[float] = ..., 
                type: Optional[Union[str, PriorityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomProperties(_Model):
        capacity: int
        capacity_type: Optional[Union[str, CapacityType]]
        compute_profile: ComputeProfile
        created_time: Optional[datetime]
        execution_parameters: Optional[ExecutionParameters]
        overrides_profile: Optional[BulkCreateCustomOverridesProfile]
        priority_profile: BulkCreateCustomPriorityProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        vm_sizes_profile: Optional[list[BulkCreateCustomVmSizeProfile]]
        zone_allocation_policy: Optional[BulkCreateCustomZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                capacity_type: Optional[Union[str, CapacityType]] = ..., 
                compute_profile: ComputeProfile, 
                execution_parameters: Optional[ExecutionParameters] = ..., 
                overrides_profile: Optional[BulkCreateCustomOverridesProfile] = ..., 
                priority_profile: BulkCreateCustomPriorityProfile, 
                vm_sizes_profile: Optional[list[BulkCreateCustomVmSizeProfile]] = ..., 
                zone_allocation_policy: Optional[BulkCreateCustomZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomVmSizeProfile(_Model):
        name: str
        override: Optional[BulkCreateCustomOverrideBase]
        rank: int

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                override: Optional[BulkCreateCustomOverrideBase] = ..., 
                rank: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkCreateCustomZoneAllocationPolicy(_Model):
        distribution_strategy: Optional[Union[str, BulkCreateCustomDistributionStrategy]]
        zone_preferences: Optional[list[ZonePreference]]

        @overload
        def __init__(
                self, 
                *, 
                distribution_strategy: Optional[Union[str, BulkCreateCustomDistributionStrategy]] = ..., 
                zone_preferences: Optional[list[ZonePreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkInstancesInnerError(_Model):
        error_detail: Optional[str]
        exception_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_detail: Optional[str] = ..., 
                exception_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkactionVMExtension(_Model):
        name: str
        properties: BulkActionVmExtensionProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: BulkActionVmExtensionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.BulkactionVMProperties(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        application_profile: Optional[ApplicationProfile]
        capacity_reservation: Optional[CapacityReservationProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        extensions_time_budget: Optional[str]
        hardware_profile: Optional[HardwareProfile]
        license_type: Optional[str]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OSProfile]
        scheduled_events_policy: Optional[ScheduledEventsPolicy]
        scheduled_events_profile: Optional[ScheduledEventsProfile]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[StorageProfile]
        user_data: Optional[str]
        vm_extensions: Optional[list[BulkactionVMExtension]]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                application_profile: Optional[ApplicationProfile] = ..., 
                capacity_reservation: Optional[CapacityReservationProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                extensions_time_budget: Optional[str] = ..., 
                hardware_profile: Optional[HardwareProfile] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                scheduled_events_policy: Optional[ScheduledEventsPolicy] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
                user_data: Optional[str] = ..., 
                vm_extensions: Optional[list[BulkactionVMExtension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CachingTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.compute.bulkaction.models.CancelOccurrenceRequest(_Model):
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CancelOperationsContent(_Model):
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CancelOperationsResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CapacityReservationProfile(_Model):
        capacity_reservation_group: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_group: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CapacityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM = "VM"
        V_CPU = "VCpu"


    class azure.mgmt.compute.bulkaction.models.ComputeProfile(_Model):
        compute_api_version: Optional[str]
        extensions: Optional[list[BulkactionVMExtension]]
        virtual_machine_profile: BulkactionVMProperties

        @overload
        def __init__(
                self, 
                *, 
                compute_api_version: Optional[str] = ..., 
                extensions: Optional[list[BulkactionVMExtension]] = ..., 
                virtual_machine_profile: BulkactionVMProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CpuManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        AMPERE = "Ampere"
        INTEL = "Intel"
        MICROSOFT = "Microsoft"


    class azure.mgmt.compute.bulkaction.models.CreateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.compute.bulkaction.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        detach_option: Optional[Union[str, DiskDetachOptionTypes]]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        lun: int
        managed_disk: Optional[ManagedDiskParametersContent]
        name: Optional[str]
        source_resource: Optional[ApiEntityReference]
        to_be_detached: Optional[bool]
        vhd: Optional[VirtualHardDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                create_option: Union[str, DiskCreateOptionTypes], 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                detach_option: Optional[Union[str, DiskDetachOptionTypes]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                lun: int, 
                managed_disk: Optional[ManagedDiskParametersContent] = ..., 
                name: Optional[str] = ..., 
                source_resource: Optional[ApiEntityReference] = ..., 
                to_be_detached: Optional[bool] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DeadlineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE_BY = "CompleteBy"
        INITIATE_AT = "InitiateAt"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.DeallocateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DelayRequest(_Model):
        delay: datetime
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                delay: datetime, 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DeleteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.compute.bulkaction.models.DeleteResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DiagnosticsProfile(_Model):
        boot_diagnostics: Optional[BootDiagnostics]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnostics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DiffDiskOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"


    class azure.mgmt.compute.bulkaction.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "CacheDisk"
        NVME_DISK = "NvmeDisk"
        RESOURCE_DISK = "ResourceDisk"


    class azure.mgmt.compute.bulkaction.models.DiffDiskSettings(_Model):
        option: Optional[Union[str, DiffDiskOptions]]
        placement: Optional[Union[str, DiffDiskPlacement]]

        @overload
        def __init__(
                self, 
                *, 
                option: Optional[Union[str, DiffDiskOptions]] = ..., 
                placement: Optional[Union[str, DiffDiskPlacement]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DiskControllerTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NV_ME = "NVMe"
        SCSI = "SCSI"


    class azure.mgmt.compute.bulkaction.models.DiskCreateOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "Attach"
        COPY = "Copy"
        EMPTY = "Empty"
        FROM_IMAGE = "FromImage"
        RESTORE = "Restore"


    class azure.mgmt.compute.bulkaction.models.DiskDeleteOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.compute.bulkaction.models.DiskDetachOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE_DETACH = "ForceDetach"


    class azure.mgmt.compute.bulkaction.models.DiskEncryptionSetParametersContent(SubResource):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DiskEncryptionSettings(_Model):
        disk_encryption_key: Optional[KeyVaultSecretReference]
        enabled: Optional[bool]
        key_encryption_key: Optional[KeyVaultKeyReference]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_key: Optional[KeyVaultSecretReference] = ..., 
                enabled: Optional[bool] = ..., 
                key_encryption_key: Optional[KeyVaultKeyReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.DistributionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT_BALANCED = "BestEffortBalanced"
        BEST_EFFORT_SINGLE_ZONE = "BestEffortSingleZone"
        PRIORITIZED = "Prioritized"
        STRICT_BALANCED = "StrictBalanced"


    class azure.mgmt.compute.bulkaction.models.DomainNameLabelScopeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.compute.bulkaction.models.EncryptionIdentity(_Model):
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.compute.bulkaction.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.compute.bulkaction.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.EventGridAndResourceGraph(_Model):
        enable: Optional[bool]
        scheduled_events_api_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                scheduled_events_api_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.EvictionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.compute.bulkaction.models.ExecuteCreateContent(_Model):
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionPayload

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resource_config_parameters: ResourceProvisionPayload
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteDeallocateContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]
        resources_with_context: Optional[ResourcesWithContext]

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ..., 
                resources_with_context: Optional[ResourcesWithContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteDeleteContent(_Model):
        execution_parameters: ExecutionParameters
        force_deletion: Optional[bool]
        resources: Optional[Resources]
        resources_with_context: Optional[ResourcesWithContext]

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                force_deletion: Optional[bool] = ..., 
                resources: Optional[Resources] = ..., 
                resources_with_context: Optional[ResourcesWithContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteHibernateContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]
        resources_with_context: Optional[ResourcesWithContext]

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ..., 
                resources_with_context: Optional[ResourcesWithContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteReimageRequest(_Model):
        execution_parameters: ExecutionParameters
        reimage_parameters: Optional[ReimagePayload]
        resources: Optional[Resources]
        resources_with_context: Optional[ResourcesWithContext]

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                reimage_parameters: Optional[ReimagePayload] = ..., 
                resources: Optional[Resources] = ..., 
                resources_with_context: Optional[ResourcesWithContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteStartContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]
        resources_with_context: Optional[ResourcesWithContext]

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ..., 
                resources_with_context: Optional[ResourcesWithContext] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecuteVdiCreateRequest(_Model):
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionVdiPayload

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resource_config_parameters: ResourceProvisionVdiPayload
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExecutionParameters(_Model):
        optimization_preference: Optional[Union[str, OptimizationPreference]]
        retry_policy: Optional[RetryPolicy]
        verify_vm_agent_health: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                optimization_preference: Optional[Union[str, OptimizationPreference]] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                verify_vm_agent_health: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.compute.bulkaction.models.FallbackOperationInfo(_Model):
        error: Optional[ResourceOperationError]
        last_op_type: Union[str, ResourceOperationType]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ResourceOperationError] = ..., 
                last_op_type: Union[str, ResourceOperationType], 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.FlexProperties(_Model):
        min_capacity: Optional[int]
        os_type: Union[str, OsType]
        priority_profile: PriorityProfile
        vm_size_profiles: list[VmSizeProfile]
        zone_allocation_policy: Optional[ZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                min_capacity: Optional[int] = ..., 
                os_type: Union[str, OsType], 
                priority_profile: PriorityProfile, 
                vm_size_profiles: list[VmSizeProfile], 
                zone_allocation_policy: Optional[ZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.GetOperationStatusContent(_Model):
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.GetOperationStatusResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.HardwareProfile(_Model):
        vm_size: Optional[str]
        vm_size_properties: Optional[VmSizeProperties]

        @overload
        def __init__(
                self, 
                *, 
                vm_size: Optional[str] = ..., 
                vm_size_properties: Optional[VmSizeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.HibernateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.HostEndpointSettings(_Model):
        in_vm_access_control_profile_reference_id: Optional[str]
        mode: Optional[Union[str, Modes]]

        @overload
        def __init__(
                self, 
                *, 
                in_vm_access_control_profile_reference_id: Optional[str] = ..., 
                mode: Optional[Union[str, Modes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.HyperVGeneration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.compute.bulkaction.models.IPVersions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.compute.bulkaction.models.ImageReference(SubResource):
        community_gallery_image_id: Optional[str]
        id: str
        offer: Optional[str]
        publisher: Optional[str]
        shared_gallery_image_id: Optional[str]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                shared_gallery_image_id: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.KeyVaultKeyReference(_Model):
        key_url: str
        source_vault: SubResource

        @overload
        def __init__(
                self, 
                *, 
                key_url: str, 
                source_vault: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.KeyVaultSecretReference(_Model):
        secret_url: str
        source_vault: SubResource

        @overload
        def __init__(
                self, 
                *, 
                secret_url: str, 
                source_vault: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.Language(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EN_US = "en-us"


    class azure.mgmt.compute.bulkaction.models.LaunchBulkInstancesOperationProperties(_Model):
        capacity: int
        capacity_type: Optional[Union[str, CapacityType]]
        compute_profile: ComputeProfile
        created_time: Optional[datetime]
        priority_profile: PriorityProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retry_policy: Optional[RetryPolicy]
        vm_attributes: Optional[VMAttributes]
        vm_sizes_profile: Optional[list[VmSizeProfile]]
        zone_allocation_policy: Optional[ZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                capacity_type: Optional[Union[str, CapacityType]] = ..., 
                compute_profile: ComputeProfile, 
                priority_profile: PriorityProfile, 
                retry_policy: Optional[RetryPolicy] = ..., 
                vm_attributes: Optional[VMAttributes] = ..., 
                vm_sizes_profile: Optional[list[VmSizeProfile]] = ..., 
                zone_allocation_policy: Optional[ZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.LinuxConfiguration(_Model):
        disable_password_authentication: Optional[bool]
        enable_vm_agent_platform_updates: Optional[bool]
        patch_settings: Optional[LinuxPatchSettings]
        provision_vm_agent: Optional[bool]
        ssh: Optional[SshConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                disable_password_authentication: Optional[bool] = ..., 
                enable_vm_agent_platform_updates: Optional[bool] = ..., 
                patch_settings: Optional[LinuxPatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.LinuxPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.bulkaction.models.LinuxPatchSettings(_Model):
        assessment_mode: Optional[Union[str, LinuxPatchAssessmentMode]]
        automatic_by_platform_settings: Optional[LinuxVMGuestPatchAutomaticByPlatformSettings]
        patch_mode: Optional[Union[str, LinuxVMGuestPatchMode]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_mode: Optional[Union[str, LinuxPatchAssessmentMode]] = ..., 
                automatic_by_platform_settings: Optional[LinuxVMGuestPatchAutomaticByPlatformSettings] = ..., 
                patch_mode: Optional[Union[str, LinuxVMGuestPatchMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.LinuxVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.LinuxVMGuestPatchAutomaticByPlatformSettings(_Model):
        bypass_platform_safety_checks_on_user_schedule: Optional[bool]
        reboot_setting: Optional[Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]]

        @overload
        def __init__(
                self, 
                *, 
                bypass_platform_safety_checks_on_user_schedule: Optional[bool] = ..., 
                reboot_setting: Optional[Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.LinuxVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.bulkaction.models.LocalStorageDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        SSD = "SSD"


    class azure.mgmt.compute.bulkaction.models.LocationBasedBulkCreateCustom(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        plan: Optional[Plan]
        properties: Optional[BulkCreateCustomProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[BulkCreateCustomProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.LocationBasedLaunchBulkInstancesOperation(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        plan: Optional[Plan]
        properties: Optional[LaunchBulkInstancesOperationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[LaunchBulkInstancesOperationProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ManagedDiskParametersContent(SubResource):
        disk_encryption_set: Optional[DiskEncryptionSetParametersContent]
        id: str
        security_profile: Optional[VMDiskSecurityProfile]
        storage_account_type: Optional[Union[str, StorageAccountTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParametersContent] = ..., 
                id: Optional[str] = ..., 
                security_profile: Optional[VMDiskSecurityProfile] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.compute.bulkaction.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.compute.bulkaction.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.mgmt.compute.bulkaction.models.Modes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DISABLED = "Disabled"
        ENFORCE = "Enforce"


    class azure.mgmt.compute.bulkaction.models.Month(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        APRIL = "April"
        AUGUST = "August"
        DECEMBER = "December"
        FEBRUARY = "February"
        JANUARY = "January"
        JULY = "July"
        JUNE = "June"
        MARCH = "March"
        MAY = "May"
        NOVEMBER = "November"
        OCTOBER = "October"
        SEPTEMBER = "September"


    class azure.mgmt.compute.bulkaction.models.NetworkApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUM2020_11_01 = "2020-11-01"
        ENUM2022_11_01 = "2022-11-01"


    class azure.mgmt.compute.bulkaction.models.NetworkInterfaceAuxiliaryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCELERATED_CONNECTIONS = "AcceleratedConnections"
        FLOATING = "Floating"
        NONE = "None"


    class azure.mgmt.compute.bulkaction.models.NetworkInterfaceAuxiliarySku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A1 = "A1"
        A2 = "A2"
        A4 = "A4"
        A8 = "A8"
        NONE = "None"


    class azure.mgmt.compute.bulkaction.models.NetworkInterfaceReference(SubResource):
        id: str
        properties: Optional[NetworkInterfaceReferenceProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[NetworkInterfaceReferenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.NetworkInterfaceReferenceProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        primary: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.NetworkProfile(_Model):
        network_api_version: Optional[Union[str, NetworkApiVersion]]
        network_interface_configurations: Optional[list[VirtualMachineNetworkInterfaceConfiguration]]
        network_interfaces: Optional[list[NetworkInterfaceReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_api_version: Optional[Union[str, NetworkApiVersion]] = ..., 
                network_interface_configurations: Optional[list[VirtualMachineNetworkInterfaceConfiguration]] = ..., 
                network_interfaces: Optional[list[NetworkInterfaceReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.NotificationProperties(_Model):
        destination: str
        disabled: Optional[bool]
        language: Union[str, Language]
        type: Union[str, NotificationType]

        @overload
        def __init__(
                self, 
                *, 
                destination: str, 
                disabled: Optional[bool] = ..., 
                language: Union[str, Language], 
                type: Union[str, NotificationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.NotificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "Email"


    class azure.mgmt.compute.bulkaction.models.OSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        diff_disk_settings: Optional[DiffDiskSettings]
        disk_size_gb: Optional[int]
        encryption_settings: Optional[DiskEncryptionSettings]
        image: Optional[VirtualHardDisk]
        managed_disk: Optional[ManagedDiskParametersContent]
        name: Optional[str]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        vhd: Optional[VirtualHardDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                create_option: Union[str, DiskCreateOptionTypes], 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                diff_disk_settings: Optional[DiffDiskSettings] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption_settings: Optional[DiskEncryptionSettings] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                managed_disk: Optional[ManagedDiskParametersContent] = ..., 
                name: Optional[str] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OSImageNotificationProfile(_Model):
        enable: Optional[bool]
        not_before_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                not_before_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OSProfile(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        allow_extension_operations: Optional[bool]
        computer_name: Optional[str]
        custom_data: Optional[str]
        linux_configuration: Optional[LinuxConfiguration]
        require_guest_provision_signal: Optional[bool]
        secrets: Optional[list[VaultSecretGroup]]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                allow_extension_operations: Optional[bool] = ..., 
                computer_name: Optional[str] = ..., 
                custom_data: Optional[str] = ..., 
                linux_configuration: Optional[LinuxConfiguration] = ..., 
                require_guest_provision_signal: Optional[bool] = ..., 
                secrets: Optional[list[VaultSecretGroup]] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OSProfileProvisioningData(_Model):
        admin_password: Optional[str]
        custom_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                custom_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.Occurrence(ProxyResource):
        id: str
        name: str
        properties: Optional[OccurrenceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OccurrenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OccurrenceExtensionProperties(_Model):
        error_details: Optional[ODataV4Format]
        notification_settings: Optional[list[NotificationProperties]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resource_id: str
        scheduled_action_id: str
        scheduled_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[list[NotificationProperties]] = ..., 
                resource_id: str, 
                scheduled_action_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OccurrenceExtensionResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[OccurrenceExtensionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OccurrenceExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OccurrenceProperties(_Model):
        provisioning_state: Optional[Union[str, OccurrenceState]]
        result_summary: OccurrenceResultSummary
        scheduled_time: datetime


    class azure.mgmt.compute.bulkaction.models.OccurrenceResource(_Model):
        error_details: Optional[ODataV4Format]
        id: str
        name: str
        notification_settings: Optional[list[NotificationProperties]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resource_id: str
        scheduled_time: datetime
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[list[NotificationProperties]] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OccurrenceResultSummary(_Model):
        statuses: list[ResourceResultSummary]
        total: int

        @overload
        def __init__(
                self, 
                *, 
                statuses: list[ResourceResultSummary], 
                total: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OccurrenceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        CREATED = "Created"
        FAILED = "Failed"
        RESCHEDULING = "Rescheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.compute.bulkaction.models.Operation(_Model):
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


    class azure.mgmt.compute.bulkaction.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.compute.bulkaction.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        CANCELLED = "Cancelled"
        EXECUTING = "Executing"
        FAILED = "Failed"
        PENDING_EXECUTION = "PendingExecution"
        PENDING_SCHEDULING = "PendingScheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.OptimizationPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        COST = "Cost"
        COST_AVAILABILITY_BALANCED = "CostAvailabilityBalanced"


    class azure.mgmt.compute.bulkaction.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.compute.bulkaction.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.compute.bulkaction.models.PatchSettings(_Model):
        assessment_mode: Optional[Union[str, WindowsPatchAssessmentMode]]
        automatic_by_platform_settings: Optional[WindowsVMGuestPatchAutomaticByPlatformSettings]
        enable_hotpatching: Optional[bool]
        patch_mode: Optional[Union[str, WindowsVMGuestPatchMode]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_mode: Optional[Union[str, WindowsPatchAssessmentMode]] = ..., 
                automatic_by_platform_settings: Optional[WindowsVMGuestPatchAutomaticByPlatformSettings] = ..., 
                enable_hotpatching: Optional[bool] = ..., 
                patch_mode: Optional[Union[str, WindowsVMGuestPatchMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.PriorityProfile(_Model):
        allocation_strategy: Optional[Union[str, AllocationStrategy]]
        eviction_policy: Optional[Union[str, EvictionPolicy]]
        max_price_per_vm: Optional[float]
        type: Optional[Union[str, PriorityType]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, AllocationStrategy]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                max_price_per_vm: Optional[float] = ..., 
                type: Optional[Union[str, PriorityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.PriorityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.compute.bulkaction.models.ProtocolTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.compute.bulkaction.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.ProxyAgentSettings(_Model):
        add_proxy_agent_extension: Optional[bool]
        enabled: Optional[bool]
        imds: Optional[HostEndpointSettings]
        key_incarnation_id: Optional[int]
        mode: Optional[Union[str, Mode]]
        wire_server: Optional[HostEndpointSettings]

        @overload
        def __init__(
                self, 
                *, 
                add_proxy_agent_extension: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                imds: Optional[HostEndpointSettings] = ..., 
                key_incarnation_id: Optional[int] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
                wire_server: Optional[HostEndpointSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.compute.bulkaction.models.PublicIPAddressSku(_Model):
        name: Optional[Union[str, PublicIPAddressSkuName]]
        tier: Optional[Union[str, PublicIPAddressSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, PublicIPAddressSkuName]] = ..., 
                tier: Optional[Union[str, PublicIPAddressSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.PublicIPAddressSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.compute.bulkaction.models.PublicIPAddressSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "Global"
        REGIONAL = "Regional"


    class azure.mgmt.compute.bulkaction.models.PublicIPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.compute.bulkaction.models.RecurringScheduledActionsDeadlineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE_BY = "CompleteBy"
        INITIATE_AT = "InitiateAt"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.RecurringScheduledActionsExecutionParameters(_Model):
        optimization_preference: Optional[Union[str, OptimizationPreference]]
        retry_policy: Optional[RecurringScheduledActionsRetryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                optimization_preference: Optional[Union[str, OptimizationPreference]] = ..., 
                retry_policy: Optional[RecurringScheduledActionsRetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.RecurringScheduledActionsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.RecurringScheduledActionsResourceOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"
        HIBERNATE = "Hibernate"
        START = "Start"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.RecurringScheduledActionsRetryPolicy(_Model):
        on_failure_action: Optional[Union[str, RecurringScheduledActionsResourceOperationType]]
        retry_count: Optional[int]
        retry_window_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                on_failure_action: Optional[Union[str, RecurringScheduledActionsResourceOperationType]] = ..., 
                retry_count: Optional[int] = ..., 
                retry_window_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ReimagePayload(_Model):
        base_profile: Optional[VirtualMachineReimageParameters]
        resource_overrides: Optional[list[ReimageResourceOverride]]

        @overload
        def __init__(
                self, 
                *, 
                base_profile: Optional[VirtualMachineReimageParameters] = ..., 
                resource_overrides: Optional[list[ReimageResourceOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ReimageResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ReimageResourceOverride(_Model):
        profile: VirtualMachineReimageParameters
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                profile: VirtualMachineReimageParameters, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.compute.bulkaction.models.ResourceAttachRequest(_Model):
        resources: list[ScheduledActionResourceInput]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[ScheduledActionResourceInput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceDetachRequest(_Model):
        resources: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.compute.bulkaction.models.ResourceNotificationDetails(_Model):
        resource_context: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_context: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceOperation(_Model):
        error_code: Optional[str]
        error_details: Optional[str]
        operation: Optional[ResourceOperationDetails]
        resource_id: Optional[str]
        virtual_machine_info: Optional[VirtualMachineInfo]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_details: Optional[str] = ..., 
                operation: Optional[ResourceOperationDetails] = ..., 
                resource_id: Optional[str] = ..., 
                virtual_machine_info: Optional[VirtualMachineInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceOperationDetails(_Model):
        completed_at: Optional[datetime]
        deadline: Optional[datetime]
        deadline_type: Optional[Union[str, DeadlineType]]
        fallback_operation_info: Optional[FallbackOperationInfo]
        op_type: Optional[Union[str, ResourceOperationType]]
        operation_id: str
        resource_id: Optional[str]
        resource_notification_details: Optional[ResourceNotificationDetails]
        resource_operation_error: Optional[ResourceOperationError]
        retry_policy: Optional[RetryPolicy]
        state: Optional[Union[str, OperationState]]
        subscription_id: Optional[str]
        timezone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                deadline: Optional[datetime] = ..., 
                deadline_type: Optional[Union[str, DeadlineType]] = ..., 
                fallback_operation_info: Optional[FallbackOperationInfo] = ..., 
                op_type: Optional[Union[str, ResourceOperationType]] = ..., 
                operation_id: str, 
                resource_id: Optional[str] = ..., 
                resource_notification_details: Optional[ResourceNotificationDetails] = ..., 
                resource_operation_error: Optional[ResourceOperationError] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                state: Optional[Union[str, OperationState]] = ..., 
                subscription_id: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceOperationError(_Model):
        error_code: str
        error_details: str

        @overload
        def __init__(
                self, 
                *, 
                error_code: str, 
                error_details: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceOperationResponse(_Model):
        resources_statuses: list[ResourceStatus]
        total_resources: int

        @overload
        def __init__(
                self, 
                *, 
                resources_statuses: list[ResourceStatus], 
                total_resources: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.ResourceOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"
        GET_INSTANCE_VIEW = "GetInstanceView"
        HIBERNATE = "Hibernate"
        START = "Start"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.ResourcePatchRequest(_Model):
        resources: list[ScheduledActionResourceInput]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[ScheduledActionResourceInput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceProvisionPayload(_Model):
        base_profile: Optional[dict[str, Any]]
        resource_count: int
        resource_overrides: Optional[list[dict[str, Any]]]
        resource_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_profile: Optional[dict[str, Any]] = ..., 
                resource_count: int, 
                resource_overrides: Optional[list[dict[str, Any]]] = ..., 
                resource_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceProvisionVdiPayload(_Model):
        base_profile: Optional[dict[str, Any]]
        flex_properties: FlexProperties
        resource_count: int
        resource_overrides: Optional[list[dict[str, Any]]]
        resource_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_profile: Optional[dict[str, Any]] = ..., 
                flex_properties: FlexProperties, 
                resource_count: int, 
                resource_overrides: Optional[list[dict[str, Any]]] = ..., 
                resource_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.ResourceResultSummary(_Model):
        code: str
        count: int
        error_details: Optional[ODataV4Format]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                count: int, 
                error_details: Optional[ODataV4Format] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceStatus(_Model):
        error: Optional[ODataV4Format]
        resource_id: str
        status: Union[str, ResourceOperationStatus]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                resource_id: str, 
                status: Union[str, ResourceOperationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VIRTUAL_MACHINE = "VirtualMachine"
        VIRTUAL_MACHINE_SCALE_SET = "VirtualMachineScaleSet"


    class azure.mgmt.compute.bulkaction.models.ResourceWithContext(_Model):
        resource_context: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_context: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.Resources(_Model):
        ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ResourcesWithContext(_Model):
        resources: list[ResourceWithContext]

        @overload
        def __init__(
                self, 
                *, 
                resources: list[ResourceWithContext]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.RetryPolicy(_Model):
        on_failure_action: Optional[Union[str, ResourceOperationType]]
        retry_count: Optional[int]
        retry_window_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                on_failure_action: Optional[Union[str, ResourceOperationType]] = ..., 
                retry_count: Optional[int] = ..., 
                retry_window_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledAction(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ScheduledActionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ScheduledActionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionProperties(_Model):
        action_type: Union[str, ScheduledActionType]
        disabled: Optional[bool]
        end_time: Optional[datetime]
        notification_settings: list[NotificationProperties]
        provisioning_state: Optional[Union[str, RecurringScheduledActionsProvisioningState]]
        resource_type: Union[str, ResourceType]
        schedule: ScheduledActionsSchedule
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, ScheduledActionType], 
                disabled: Optional[bool] = ..., 
                end_time: Optional[datetime] = ..., 
                notification_settings: list[NotificationProperties], 
                resource_type: Union[str, ResourceType], 
                schedule: ScheduledActionsSchedule, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionResource(_Model):
        id: str
        name: str
        notification_settings: Optional[list[NotificationProperties]]
        resource_id: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[list[NotificationProperties]] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionResourceInput(_Model):
        notification_settings: Optional[list[NotificationProperties]]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[list[NotificationProperties]] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionResources(ExtensionResource):
        id: str
        name: str
        properties: Optional[ScheduledActionsExtensionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledActionsExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        HIBERNATE = "Hibernate"
        START = "Start"


    class azure.mgmt.compute.bulkaction.models.ScheduledActionUpdate(_Model):
        properties: Optional[ScheduledActionUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledActionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionUpdateProperties(_Model):
        action_type: Optional[Union[str, ScheduledActionType]]
        disabled: Optional[bool]
        end_time: Optional[datetime]
        notification_settings: Optional[list[NotificationProperties]]
        resource_type: Optional[Union[str, ResourceType]]
        schedule: Optional[ScheduledActionsScheduleUpdate]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ScheduledActionType]] = ..., 
                disabled: Optional[bool] = ..., 
                end_time: Optional[datetime] = ..., 
                notification_settings: Optional[list[NotificationProperties]] = ..., 
                resource_type: Optional[Union[str, ResourceType]] = ..., 
                schedule: Optional[ScheduledActionsScheduleUpdate] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionsExtensionProperties(_Model):
        action_type: Union[str, ScheduledActionType]
        disabled: Optional[bool]
        end_time: Optional[datetime]
        notification_settings: list[NotificationProperties]
        provisioning_state: Optional[Union[str, RecurringScheduledActionsProvisioningState]]
        resource_notification_settings: Optional[list[NotificationProperties]]
        resource_type: Union[str, ResourceType]
        schedule: ScheduledActionsSchedule
        start_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, ScheduledActionType], 
                disabled: Optional[bool] = ..., 
                end_time: Optional[datetime] = ..., 
                notification_settings: list[NotificationProperties], 
                resource_type: Union[str, ResourceType], 
                schedule: ScheduledActionsSchedule, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionsSchedule(_Model):
        deadline_type: Optional[Union[str, RecurringScheduledActionsDeadlineType]]
        execution_parameters: Optional[RecurringScheduledActionsExecutionParameters]
        requested_days_of_the_month: Optional[list[int]]
        requested_months: Optional[list[Union[str, Month]]]
        requested_week_days: Optional[list[Union[str, WeekDay]]]
        scheduled_time: time
        time_zone: str

        @overload
        def __init__(
                self, 
                *, 
                deadline_type: Optional[Union[str, RecurringScheduledActionsDeadlineType]] = ..., 
                execution_parameters: Optional[RecurringScheduledActionsExecutionParameters] = ..., 
                requested_days_of_the_month: Optional[list[int]] = ..., 
                requested_months: Optional[list[Union[str, Month]]] = ..., 
                requested_week_days: Optional[list[Union[str, WeekDay]]] = ..., 
                scheduled_time: time, 
                time_zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledActionsScheduleUpdate(_Model):
        deadline_type: Optional[Union[str, RecurringScheduledActionsDeadlineType]]
        execution_parameters: Optional[RecurringScheduledActionsExecutionParameters]
        requested_days_of_the_month: Optional[list[int]]
        requested_months: Optional[list[Union[str, Month]]]
        requested_week_days: Optional[list[Union[str, WeekDay]]]
        scheduled_time: Optional[time]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deadline_type: Optional[Union[str, RecurringScheduledActionsDeadlineType]] = ..., 
                execution_parameters: Optional[RecurringScheduledActionsExecutionParameters] = ..., 
                requested_days_of_the_month: Optional[list[int]] = ..., 
                requested_months: Optional[list[Union[str, Month]]] = ..., 
                requested_week_days: Optional[list[Union[str, WeekDay]]] = ..., 
                scheduled_time: Optional[time] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledEventsAdditionalPublishingTargets(_Model):
        event_grid_and_resource_graph: Optional[EventGridAndResourceGraph]

        @overload
        def __init__(
                self, 
                *, 
                event_grid_and_resource_graph: Optional[EventGridAndResourceGraph] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledEventsPolicy(_Model):
        all_instances_down: Optional[AllInstancesDown]
        scheduled_events_additional_publishing_targets: Optional[ScheduledEventsAdditionalPublishingTargets]
        user_initiated_reboot: Optional[UserInitiatedReboot]
        user_initiated_redeploy: Optional[UserInitiatedRedeploy]

        @overload
        def __init__(
                self, 
                *, 
                all_instances_down: Optional[AllInstancesDown] = ..., 
                scheduled_events_additional_publishing_targets: Optional[ScheduledEventsAdditionalPublishingTargets] = ..., 
                user_initiated_reboot: Optional[UserInitiatedReboot] = ..., 
                user_initiated_redeploy: Optional[UserInitiatedRedeploy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ScheduledEventsProfile(_Model):
        os_image_notification_profile: Optional[OSImageNotificationProfile]
        terminate_notification_profile: Optional[TerminateNotificationProfile]

        @overload
        def __init__(
                self, 
                *, 
                os_image_notification_profile: Optional[OSImageNotificationProfile] = ..., 
                terminate_notification_profile: Optional[TerminateNotificationProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.compute.bulkaction.models.SecurityProfile(_Model):
        encryption_at_host: Optional[bool]
        encryption_identity: Optional[EncryptionIdentity]
        proxy_agent_settings: Optional[ProxyAgentSettings]
        security_type: Optional[Union[str, SecurityTypes]]
        uefi_settings: Optional[UefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_host: Optional[bool] = ..., 
                encryption_identity: Optional[EncryptionIdentity] = ..., 
                proxy_agent_settings: Optional[ProxyAgentSettings] = ..., 
                security_type: Optional[Union[str, SecurityTypes]] = ..., 
                uefi_settings: Optional[UefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.compute.bulkaction.models.SettingNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_LOGON = "AutoLogon"
        FIRST_LOGON_COMMANDS = "FirstLogonCommands"


    class azure.mgmt.compute.bulkaction.models.SshConfiguration(_Model):
        public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.SshPublicKey(_Model):
        key_data: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_data: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.StartResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.StorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.compute.bulkaction.models.StorageProfile(_Model):
        data_disks: Optional[list[DataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[OSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[DataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[OSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.SystemData(_Model):
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


    class azure.mgmt.compute.bulkaction.models.TerminateNotificationProfile(_Model):
        enable: Optional[bool]
        not_before_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                not_before_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.TrackedResource(Resource):
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


    class azure.mgmt.compute.bulkaction.models.UefiSettings(_Model):
        secure_boot_enabled: Optional[bool]
        v_tpm_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ..., 
                v_tpm_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.UserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.compute.bulkaction.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.compute.bulkaction.models.UserInitiatedReboot(_Model):
        user_initiated_reboot_automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                user_initiated_reboot_automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.UserInitiatedRedeploy(_Model):
        user_initiated_redeploy_automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                user_initiated_redeploy_automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMAttributeMinMaxDouble(_Model):
        max: Optional[float]
        min: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max: Optional[float] = ..., 
                min: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMAttributeMinMaxInteger(_Model):
        max: Optional[int]
        min: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max: Optional[int] = ..., 
                min: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMAttributeSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"
        REQUIRED = "Required"


    class azure.mgmt.compute.bulkaction.models.VMAttributes(_Model):
        accelerator_count: Optional[VMAttributeMinMaxInteger]
        accelerator_manufacturers: Optional[list[Union[str, AcceleratorManufacturer]]]
        accelerator_support: Optional[Union[str, VMAttributeSupport]]
        accelerator_types: Optional[list[Union[str, AcceleratorType]]]
        allowed_vm_sizes: Optional[list[str]]
        architecture_types: list[Union[str, ArchitectureType]]
        burstable_support: Optional[Union[str, VMAttributeSupport]]
        cpu_manufacturers: Optional[list[Union[str, CpuManufacturer]]]
        data_disk_count: Optional[VMAttributeMinMaxInteger]
        excluded_vm_sizes: Optional[list[str]]
        hyper_v_generations: Optional[list[Union[str, HyperVGeneration]]]
        local_storage_disk_types: Optional[list[Union[str, LocalStorageDiskType]]]
        local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble]
        local_storage_support: Optional[Union[str, VMAttributeSupport]]
        memory_in_gi_b: VMAttributeMinMaxDouble
        memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble]
        network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble]
        network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_support: Optional[Union[str, VMAttributeSupport]]
        v_cpu_count: VMAttributeMinMaxInteger
        vm_categories: Optional[list[Union[str, VMCategory]]]

        @overload
        def __init__(
                self, 
                *, 
                accelerator_count: Optional[VMAttributeMinMaxInteger] = ..., 
                accelerator_manufacturers: Optional[list[Union[str, AcceleratorManufacturer]]] = ..., 
                accelerator_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                accelerator_types: Optional[list[Union[str, AcceleratorType]]] = ..., 
                allowed_vm_sizes: Optional[list[str]] = ..., 
                architecture_types: list[Union[str, ArchitectureType]], 
                burstable_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                cpu_manufacturers: Optional[list[Union[str, CpuManufacturer]]] = ..., 
                data_disk_count: Optional[VMAttributeMinMaxInteger] = ..., 
                excluded_vm_sizes: Optional[list[str]] = ..., 
                hyper_v_generations: Optional[list[Union[str, HyperVGeneration]]] = ..., 
                local_storage_disk_types: Optional[list[Union[str, LocalStorageDiskType]]] = ..., 
                local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble] = ..., 
                local_storage_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                memory_in_gi_b: VMAttributeMinMaxDouble, 
                memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble] = ..., 
                network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble] = ..., 
                network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                v_cpu_count: VMAttributeMinMaxInteger, 
                vm_categories: Optional[list[Union[str, VMCategory]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_OPTIMIZED = "ComputeOptimized"
        FPGA_ACCELERATED = "FpgaAccelerated"
        GENERAL_PURPOSE = "GeneralPurpose"
        GPU_ACCELERATED = "GpuAccelerated"
        HIGH_PERFORMANCE_COMPUTE = "HighPerformanceCompute"
        MEMORY_OPTIMIZED = "MemoryOptimized"
        STORAGE_OPTIMIZED = "StorageOptimized"


    class azure.mgmt.compute.bulkaction.models.VMDiskSecurityProfile(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParametersContent]
        security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParametersContent] = ..., 
                security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMGalleryApplication(_Model):
        configuration_reference: Optional[str]
        enable_automatic_upgrade: Optional[bool]
        order: Optional[int]
        package_reference_id: str
        tags: Optional[str]
        treat_failure_as_deployment_failure: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration_reference: Optional[str] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                order: Optional[int] = ..., 
                package_reference_id: str, 
                tags: Optional[str] = ..., 
                treat_failure_as_deployment_failure: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VMOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        CANCEL_FAILED_STATUS_UNKNOWN = "CancelFailedStatusUnknown"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.bulkaction.models.VaultCertificate(_Model):
        certificate_store: Optional[str]
        certificate_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_store: Optional[str] = ..., 
                certificate_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VaultSecretGroup(_Model):
        source_vault: Optional[SubResource]
        vault_certificates: Optional[list[VaultCertificate]]

        @overload
        def __init__(
                self, 
                *, 
                source_vault: Optional[SubResource] = ..., 
                vault_certificates: Optional[list[VaultCertificate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualHardDisk(_Model):
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachine(_Model):
        error: Optional[ApiError]
        id: str
        name: str
        operation_status: Union[str, VMOperationStatus]
        type: Optional[str]


    class azure.mgmt.compute.bulkaction.models.VirtualMachineIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineInfo(_Model):
        vm_size: Optional[str]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                vm_size: Optional[str] = ..., 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineIpTag(_Model):
        ip_tag_type: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineNetworkInterfaceConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceConfigurationProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineNetworkInterfaceConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineNetworkInterfaceConfigurationProperties(_Model):
        auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]]
        auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]]
        delete_option: Optional[Union[str, DeleteOptions]]
        disable_tcp_state_tracking: Optional[bool]
        dns_settings: Optional[VirtualMachineNetworkInterfaceDnsSettingsConfiguration]
        dscp_configuration: Optional[SubResource]
        enable_accelerated_networking: Optional[bool]
        enable_fpga: Optional[bool]
        enable_ip_forwarding: Optional[bool]
        ip_configurations: list[VirtualMachineNetworkInterfaceIPConfiguration]
        network_security_group: Optional[SubResource]
        primary: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]] = ..., 
                auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]] = ..., 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                disable_tcp_state_tracking: Optional[bool] = ..., 
                dns_settings: Optional[VirtualMachineNetworkInterfaceDnsSettingsConfiguration] = ..., 
                dscp_configuration: Optional[SubResource] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                enable_fpga: Optional[bool] = ..., 
                enable_ip_forwarding: Optional[bool] = ..., 
                ip_configurations: list[VirtualMachineNetworkInterfaceIPConfiguration], 
                network_security_group: Optional[SubResource] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineNetworkInterfaceDnsSettingsConfiguration(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineNetworkInterfaceIPConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineNetworkInterfaceIPConfigurationProperties(_Model):
        application_gateway_backend_address_pools: Optional[list[SubResource]]
        application_security_groups: Optional[list[SubResource]]
        load_balancer_backend_address_pools: Optional[list[SubResource]]
        primary: Optional[bool]
        private_ip_address_version: Optional[Union[str, IPVersions]]
        public_ip_address_configuration: Optional[VirtualMachinePublicIPAddressConfiguration]
        subnet: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[list[SubResource]] = ..., 
                application_security_groups: Optional[list[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[list[SubResource]] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address_version: Optional[Union[str, IPVersions]] = ..., 
                public_ip_address_configuration: Optional[VirtualMachinePublicIPAddressConfiguration] = ..., 
                subnet: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachinePublicIPAddressConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachinePublicIPAddressConfigurationProperties]
        sku: Optional[PublicIPAddressSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachinePublicIPAddressConfigurationProperties] = ..., 
                sku: Optional[PublicIPAddressSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachinePublicIPAddressConfigurationProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        dns_settings: Optional[VirtualMachinePublicIPAddressDnsSettingsConfiguration]
        idle_timeout_in_minutes: Optional[int]
        ip_tags: Optional[list[VirtualMachineIpTag]]
        public_ip_address_version: Optional[Union[str, IPVersions]]
        public_ip_allocation_method: Optional[Union[str, PublicIPAllocationMethod]]
        public_ip_prefix: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                dns_settings: Optional[VirtualMachinePublicIPAddressDnsSettingsConfiguration] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                ip_tags: Optional[list[VirtualMachineIpTag]] = ..., 
                public_ip_address_version: Optional[Union[str, IPVersions]] = ..., 
                public_ip_allocation_method: Optional[Union[str, PublicIPAllocationMethod]] = ..., 
                public_ip_prefix: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachinePublicIPAddressDnsSettingsConfiguration(_Model):
        domain_name_label: str
        domain_name_label_scope: Optional[Union[str, DomainNameLabelScopeTypes]]

        @overload
        def __init__(
                self, 
                *, 
                domain_name_label: str, 
                domain_name_label_scope: Optional[Union[str, DomainNameLabelScopeTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VirtualMachineReimageParameters(_Model):
        exact_version: Optional[str]
        os_profile: Optional[OSProfileProvisioningData]
        temp_disk: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exact_version: Optional[str] = ..., 
                os_profile: Optional[OSProfileProvisioningData] = ..., 
                temp_disk: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VmSizeProfile(_Model):
        name: str
        rank: int

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                rank: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.VmSizeProperties(_Model):
        v_cpus_available: Optional[int]
        v_cpus_per_core: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                v_cpus_available: Optional[int] = ..., 
                v_cpus_per_core: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.compute.bulkaction.models.WinRMConfiguration(_Model):
        listeners: Optional[list[WinRMListener]]

        @overload
        def __init__(
                self, 
                *, 
                listeners: Optional[list[WinRMListener]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.WinRMListener(_Model):
        certificate_url: Optional[str]
        protocol: Optional[Union[str, ProtocolTypes]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_url: Optional[str] = ..., 
                protocol: Optional[Union[str, ProtocolTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.WindowsConfiguration(_Model):
        additional_unattend_content: Optional[list[AdditionalUnattendContent]]
        enable_automatic_updates: Optional[bool]
        patch_settings: Optional[PatchSettings]
        provision_vm_agent: Optional[bool]
        time_zone: Optional[str]
        win_rm: Optional[WinRMConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                additional_unattend_content: Optional[list[AdditionalUnattendContent]] = ..., 
                enable_automatic_updates: Optional[bool] = ..., 
                patch_settings: Optional[PatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                time_zone: Optional[str] = ..., 
                win_rm: Optional[WinRMConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.WindowsPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.bulkaction.models.WindowsVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.bulkaction.models.WindowsVMGuestPatchAutomaticByPlatformSettings(_Model):
        bypass_platform_safety_checks_on_user_schedule: Optional[bool]
        reboot_setting: Optional[Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]]

        @overload
        def __init__(
                self, 
                *, 
                bypass_platform_safety_checks_on_user_schedule: Optional[bool] = ..., 
                reboot_setting: Optional[Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.WindowsVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_OS = "AutomaticByOS"
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        MANUAL = "Manual"


    class azure.mgmt.compute.bulkaction.models.ZoneAllocationPolicy(_Model):
        distribution_strategy: Optional[Union[str, DistributionStrategy]]
        zone_preferences: Optional[list[ZonePreference]]

        @overload
        def __init__(
                self, 
                *, 
                distribution_strategy: Optional[Union[str, DistributionStrategy]] = ..., 
                zone_preferences: Optional[list[ZonePreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.bulkaction.models.ZonePreference(_Model):
        rank: int
        zone: str

        @overload
        def __init__(
                self, 
                *, 
                rank: int, 
                zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.compute.bulkaction.operations

    class azure.mgmt.compute.bulkaction.operations.BulkCreateCustomOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name']}, api_versions_list=['2026-07-06-preview'])
        def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedBulkCreateCustom, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedBulkCreateCustom]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedBulkCreateCustom, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedBulkCreateCustom]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedBulkCreateCustom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'delete_instances']}, api_versions_list=['2026-07-06-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedBulkCreateCustom: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'async_operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get_async_operation_status(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedBulkCreateCustom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedBulkCreateCustom]: ...


    class azure.mgmt.compute.bulkaction.operations.LaunchBulkInstancesOperationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name']}, api_versions_list=['2026-07-06-preview'])
        def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'delete_instances']}, api_versions_list=['2026-07-06-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedLaunchBulkInstancesOperation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'async_operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get_operation_status(
                self, 
                location: str, 
                async_operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'name', 'filter', 'skiptoken', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...


    class azure.mgmt.compute.bulkaction.operations.OccurrenceExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_occurrence_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[OccurrenceExtensionResource]: ...


    class azure.mgmt.compute.bulkaction.operations.OccurrencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: DelayRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: DelayRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_scheduled_action(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Occurrence]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> ItemPaged[OccurrenceResource]: ...


    class azure.mgmt.compute.bulkaction.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.compute.bulkaction.operations.ScheduledActionExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledActionResources]: ...


    class azure.mgmt.compute.bulkaction.operations.ScheduledActionOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.compute.bulkaction.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScheduledAction]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: ScheduledAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScheduledAction]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @overload
        def begin_detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceOperationResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        def begin_disable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name']}, api_versions_list=['2026-07-06-preview'])
        def begin_enable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def begin_trigger_manual_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[Occurrence]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledActionResource]: ...

        @overload
        def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...

        @overload
        def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourcePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...

        @overload
        def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceOperationResponse: ...


    class azure.mgmt.compute.bulkaction.operations.VirtualMachineBulkOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: AcknowledgeBulkOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: AcknowledgeBulkOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        def bulk_acknowledge_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AcknowledgeBulkOperationErrorsResponse: ...

        @overload
        def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: CancelOperationsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: CancelOperationsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def bulk_cancel_operations(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteCreateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteCreateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def bulk_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeallocateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeallocateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def bulk_deallocate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeleteContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteDeleteContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def bulk_delete_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: GetOperationStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: GetOperationStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def bulk_get_operations_status(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteHibernateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteHibernateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def bulk_hibernate_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-06-preview', params_added_on={'2026-07-06-preview': ['api_version', 'subscription_id', 'resource_group_name', 'location', 'lookback_in_minutes', 'accept']}, api_versions_list=['2026-07-06-preview'])
        def bulk_list_operation_errors(
                self, 
                resource_group_name: str, 
                location: str, 
                *, 
                lookback_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceOperation]: ...

        @overload
        def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteReimageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteReimageRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        def bulk_reimage_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ReimageResourceOperationResponse: ...

        @overload
        def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteStartContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteStartContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def bulk_start_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteVdiCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: ExecuteVdiCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def bulk_vdi_flex_create_operation(
                self, 
                resource_group_name: str, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...


namespace azure.mgmt.compute.bulkaction.types

    class azure.mgmt.compute.bulkaction.types.AcknowledgeBulkOperationErrorsRequest(TypedDict, total=False):
        key "operationIds": Required[list[str]]
        operation_ids: list[str]


    class azure.mgmt.compute.bulkaction.types.AdditionalCapabilities(TypedDict, total=False):
        key "hibernationEnabled": bool
        key "ultraSSDEnabled": bool
        hibernation_enabled: bool
        ultra_ssd_enabled: bool


    class azure.mgmt.compute.bulkaction.types.AdditionalUnattendContent(TypedDict, total=False):
        key "componentName": Literal["Microsoft-Windows-Shell-Setup"]
        key "content": str
        key "passName": Literal["OobeSystem"]
        key "settingName": Union[str, SettingNames]
        component_name: Literal[Microsoft-Windows-Shell-Setup]
        content: str
        pass_name: Literal[OobeSystem]
        setting_name: Union[str, SettingNames]


    class azure.mgmt.compute.bulkaction.types.AllInstancesDown(TypedDict, total=False):
        key "automaticallyApprove": bool
        all_instances_down_automatically_approve: bool


    class azure.mgmt.compute.bulkaction.types.ApiEntityReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.compute.bulkaction.types.ApplicationProfile(TypedDict, total=False):
        galleryApplications: list[VMGalleryApplication]
        gallery_applications: list[VMGalleryApplication]


    class azure.mgmt.compute.bulkaction.types.BootDiagnostics(TypedDict, total=False):
        key "enabled": bool
        key "storageUri": str
        enabled: bool
        storage_uri: str


    class azure.mgmt.compute.bulkaction.types.BulkActionVmExtensionProperties(TypedDict, total=False):
        key "autoUpgradeMinorVersion": bool
        key "enableAutomaticUpgrade": bool
        key "forceUpdateTag": str
        key "protectedSettingsFromKeyVault": ForwardRef('KeyVaultSecretReference', module='types')
        key "publisher": str
        key "suppressFailures": bool
        key "type": str
        key "typeHandlerVersion": str
        auto_upgrade_minor_version: bool
        enable_automatic_upgrade: bool
        force_update_tag: str
        protectedSettings: dict[str, Any]
        protected_settings: dict[str, Any]
        protected_settings_from_key_vault: KeyVaultSecretReference
        provisionAfterExtensions: list[str]
        provision_after_extensions: list[str]
        publisher: str
        settings: dict[str, Any]
        suppress_failures: bool
        type: str
        type_handler_version: str


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomOverride(TypedDict, total=False):
        key "identity": ForwardRef('VirtualMachineIdentity', module='types')
        key "plan": ForwardRef('Plan', module='types')
        key "virtualMachineName": str
        key "virtualMachineProfile": ForwardRef('BulkactionVMProperties', module='types')
        extensions: list[BulkactionVMExtension]
        identity: VirtualMachineIdentity
        plan: Plan
        tags: dict[str, str]
        virtual_machine_name: str
        virtual_machine_profile: BulkactionVMProperties


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomOverrideBase(TypedDict, total=False):
        key "identity": ForwardRef('VirtualMachineIdentity', module='types')
        key "plan": ForwardRef('Plan', module='types')
        key "virtualMachineProfile": ForwardRef('BulkactionVMProperties', module='types')
        extensions: list[BulkactionVMExtension]
        identity: VirtualMachineIdentity
        plan: Plan
        tags: dict[str, str]
        virtual_machine_profile: BulkactionVMProperties


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomOverridesProfile(TypedDict, total=False):
        key "virtualMachineNamePrefix": str
        overrides: list[BulkCreateCustomOverride]
        virtual_machine_name_prefix: str


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomPriorityProfile(TypedDict, total=False):
        key "allocationStrategy": Union[str, BulkCreateCustomAllocationStrategy]
        key "evictionPolicy": Union[str, EvictionPolicy]
        key "maxPricePerVM": float
        key "type": Union[str, PriorityType]
        allocation_strategy: Union[str, BulkCreateCustomAllocationStrategy]
        eviction_policy: Union[str, EvictionPolicy]
        max_price_per_vm: float
        type: Union[str, PriorityType]


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomProperties(TypedDict, total=False):
        key "capacity": Required[int]
        key "capacityType": Union[str, CapacityType]
        key "computeProfile": Required[ComputeProfile]
        key "createdTime": str
        key "executionParameters": ForwardRef('ExecutionParameters', module='types')
        key "overridesProfile": ForwardRef('BulkCreateCustomOverridesProfile', module='types')
        key "priorityProfile": Required[BulkCreateCustomPriorityProfile]
        key "provisioningState": Union[str, ProvisioningState]
        key "zoneAllocationPolicy": ForwardRef('BulkCreateCustomZoneAllocationPolicy', module='types')
        capacity: int
        capacity_type: Union[str, CapacityType]
        compute_profile: ComputeProfile
        created_time: str
        execution_parameters: ExecutionParameters
        overrides_profile: BulkCreateCustomOverridesProfile
        priority_profile: BulkCreateCustomPriorityProfile
        provisioning_state: Union[str, ProvisioningState]
        vmSizesProfile: list[BulkCreateCustomVmSizeProfile]
        vm_sizes_profile: list[BulkCreateCustomVmSizeProfile]
        zone_allocation_policy: BulkCreateCustomZoneAllocationPolicy


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomVmSizeProfile(TypedDict, total=False):
        key "name": Required[str]
        key "override": ForwardRef('BulkCreateCustomOverrideBase', module='types')
        key "rank": Required[int]
        name: str
        override: BulkCreateCustomOverrideBase
        rank: int


    class azure.mgmt.compute.bulkaction.types.BulkCreateCustomZoneAllocationPolicy(TypedDict, total=False):
        key "distributionStrategy": Union[str, BulkCreateCustomDistributionStrategy]
        distribution_strategy: Union[str, BulkCreateCustomDistributionStrategy]
        zonePreferences: list[ZonePreference]
        zone_preferences: list[ZonePreference]


    class azure.mgmt.compute.bulkaction.types.BulkactionVMExtension(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[BulkActionVmExtensionProperties]
        name: str
        properties: BulkActionVmExtensionProperties


    class azure.mgmt.compute.bulkaction.types.BulkactionVMProperties(TypedDict, total=False):
        key "additionalCapabilities": ForwardRef('AdditionalCapabilities', module='types')
        key "applicationProfile": ForwardRef('ApplicationProfile', module='types')
        key "capacityReservation": ForwardRef('CapacityReservationProfile', module='types')
        key "diagnosticsProfile": ForwardRef('DiagnosticsProfile', module='types')
        key "extensionsTimeBudget": str
        key "hardwareProfile": ForwardRef('HardwareProfile', module='types')
        key "licenseType": str
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "osProfile": ForwardRef('OSProfile', module='types')
        key "scheduledEventsPolicy": ForwardRef('ScheduledEventsPolicy', module='types')
        key "scheduledEventsProfile": ForwardRef('ScheduledEventsProfile', module='types')
        key "securityProfile": ForwardRef('SecurityProfile', module='types')
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        key "userData": str
        additional_capabilities: AdditionalCapabilities
        application_profile: ApplicationProfile
        capacity_reservation: CapacityReservationProfile
        diagnostics_profile: DiagnosticsProfile
        extensions_time_budget: str
        hardware_profile: HardwareProfile
        license_type: str
        network_profile: NetworkProfile
        os_profile: OSProfile
        scheduled_events_policy: ScheduledEventsPolicy
        scheduled_events_profile: ScheduledEventsProfile
        security_profile: SecurityProfile
        storage_profile: StorageProfile
        user_data: str
        vmExtensions: list[BulkactionVMExtension]
        vm_extensions: list[BulkactionVMExtension]


    class azure.mgmt.compute.bulkaction.types.CancelOccurrenceRequest(TypedDict, total=False):
        key "resourceIds": Required[list[str]]
        resource_ids: list[str]


    class azure.mgmt.compute.bulkaction.types.CancelOperationsContent(TypedDict, total=False):
        key "operationIds": Required[list[str]]
        operation_ids: list[str]


    class azure.mgmt.compute.bulkaction.types.CapacityReservationProfile(TypedDict, total=False):
        key "capacityReservationGroup": ForwardRef('SubResource', module='types')
        capacity_reservation_group: SubResource


    class azure.mgmt.compute.bulkaction.types.ComputeProfile(TypedDict, total=False):
        key "computeApiVersion": str
        key "virtualMachineProfile": Required[BulkactionVMProperties]
        compute_api_version: str
        extensions: list[BulkactionVMExtension]
        virtual_machine_profile: BulkactionVMProperties


    class azure.mgmt.compute.bulkaction.types.DataDisk(TypedDict, total=False):
        key "caching": Union[str, CachingTypes]
        key "createOption": Required[Union[str, DiskCreateOptionTypes]]
        key "deleteOption": Union[str, DiskDeleteOptionTypes]
        key "detachOption": Union[str, DiskDetachOptionTypes]
        key "diskSizeGB": int
        key "image": ForwardRef('VirtualHardDisk', module='types')
        key "lun": Required[int]
        key "managedDisk": ForwardRef('ManagedDiskParametersContent', module='types')
        key "name": str
        key "sourceResource": ForwardRef('ApiEntityReference', module='types')
        key "toBeDetached": bool
        key "vhd": ForwardRef('VirtualHardDisk', module='types')
        key "writeAcceleratorEnabled": bool
        caching: Union[str, CachingTypes]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Union[str, DiskDeleteOptionTypes]
        detach_option: Union[str, DiskDetachOptionTypes]
        disk_size_gb: int
        image: VirtualHardDisk
        lun: int
        managed_disk: ManagedDiskParametersContent
        name: str
        source_resource: ApiEntityReference
        to_be_detached: bool
        vhd: VirtualHardDisk
        write_accelerator_enabled: bool


    class azure.mgmt.compute.bulkaction.types.DelayRequest(TypedDict, total=False):
        key "delay": Required[str]
        key "resourceIds": Required[list[str]]
        delay: str
        resource_ids: list[str]


    class azure.mgmt.compute.bulkaction.types.DiagnosticsProfile(TypedDict, total=False):
        key "bootDiagnostics": ForwardRef('BootDiagnostics', module='types')
        boot_diagnostics: BootDiagnostics


    class azure.mgmt.compute.bulkaction.types.DiffDiskSettings(TypedDict, total=False):
        key "option": Union[str, DiffDiskOptions]
        key "placement": Union[str, DiffDiskPlacement]
        option: Union[str, DiffDiskOptions]
        placement: Union[str, DiffDiskPlacement]


    class azure.mgmt.compute.bulkaction.types.DiskEncryptionSetParametersContent(SubResource):
        key "id": str
        id: str


    class azure.mgmt.compute.bulkaction.types.DiskEncryptionSettings(TypedDict, total=False):
        key "diskEncryptionKey": ForwardRef('KeyVaultSecretReference', module='types')
        key "enabled": bool
        key "keyEncryptionKey": ForwardRef('KeyVaultKeyReference', module='types')
        disk_encryption_key: KeyVaultSecretReference
        enabled: bool
        key_encryption_key: KeyVaultKeyReference


    class azure.mgmt.compute.bulkaction.types.EncryptionIdentity(TypedDict, total=False):
        key "userAssignedIdentityResourceId": str
        user_assigned_identity_resource_id: str


    class azure.mgmt.compute.bulkaction.types.EventGridAndResourceGraph(TypedDict, total=False):
        key "enable": bool
        key "scheduledEventsApiVersion": str
        enable: bool
        scheduled_events_api_version: str


    class azure.mgmt.compute.bulkaction.types.ExecuteCreateContent(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "resourceConfigParameters": Required[ResourceProvisionPayload]
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionPayload


    class azure.mgmt.compute.bulkaction.types.ExecuteDeallocateContent(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "resources": ForwardRef('Resources', module='types')
        key "resourcesWithContext": ForwardRef('ResourcesWithContext', module='types')
        execution_parameters: ExecutionParameters
        resources: Resources
        resources_with_context: ResourcesWithContext


    class azure.mgmt.compute.bulkaction.types.ExecuteDeleteContent(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "forceDeletion": bool
        key "resources": ForwardRef('Resources', module='types')
        key "resourcesWithContext": ForwardRef('ResourcesWithContext', module='types')
        execution_parameters: ExecutionParameters
        force_deletion: bool
        resources: Resources
        resources_with_context: ResourcesWithContext


    class azure.mgmt.compute.bulkaction.types.ExecuteHibernateContent(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "resources": ForwardRef('Resources', module='types')
        key "resourcesWithContext": ForwardRef('ResourcesWithContext', module='types')
        execution_parameters: ExecutionParameters
        resources: Resources
        resources_with_context: ResourcesWithContext


    class azure.mgmt.compute.bulkaction.types.ExecuteReimageRequest(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "reimageParameters": ForwardRef('ReimagePayload', module='types')
        key "resources": ForwardRef('Resources', module='types')
        key "resourcesWithContext": ForwardRef('ResourcesWithContext', module='types')
        execution_parameters: ExecutionParameters
        reimage_parameters: ReimagePayload
        resources: Resources
        resources_with_context: ResourcesWithContext


    class azure.mgmt.compute.bulkaction.types.ExecuteStartContent(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "resources": ForwardRef('Resources', module='types')
        key "resourcesWithContext": ForwardRef('ResourcesWithContext', module='types')
        execution_parameters: ExecutionParameters
        resources: Resources
        resources_with_context: ResourcesWithContext


    class azure.mgmt.compute.bulkaction.types.ExecuteVdiCreateRequest(TypedDict, total=False):
        key "executionParameters": Required[ExecutionParameters]
        key "resourceConfigParameters": Required[ResourceProvisionVdiPayload]
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionVdiPayload


    class azure.mgmt.compute.bulkaction.types.ExecutionParameters(TypedDict, total=False):
        key "optimizationPreference": Union[str, OptimizationPreference]
        key "retryPolicy": ForwardRef('RetryPolicy', module='types')
        key "verifyVmAgentHealth": bool
        optimization_preference: Union[str, OptimizationPreference]
        retry_policy: RetryPolicy
        verify_vm_agent_health: bool


    class azure.mgmt.compute.bulkaction.types.FlexProperties(TypedDict, total=False):
        key "minCapacity": int
        key "osType": Required[Union[str, OsType]]
        key "priorityProfile": Required[PriorityProfile]
        key "vmSizeProfiles": Required[list[VmSizeProfile]]
        key "zoneAllocationPolicy": ForwardRef('ZoneAllocationPolicy', module='types')
        min_capacity: int
        os_type: Union[str, OsType]
        priority_profile: PriorityProfile
        vm_size_profiles: list[VmSizeProfile]
        zone_allocation_policy: ZoneAllocationPolicy


    class azure.mgmt.compute.bulkaction.types.GetOperationStatusContent(TypedDict, total=False):
        key "operationIds": Required[list[str]]
        operation_ids: list[str]


    class azure.mgmt.compute.bulkaction.types.HardwareProfile(TypedDict, total=False):
        key "vmSize": str
        key "vmSizeProperties": ForwardRef('VmSizeProperties', module='types')
        vm_size: str
        vm_size_properties: VmSizeProperties


    class azure.mgmt.compute.bulkaction.types.HostEndpointSettings(TypedDict, total=False):
        key "inVMAccessControlProfileReferenceId": str
        key "mode": Union[str, Modes]
        in_vm_access_control_profile_reference_id: str
        mode: Union[str, Modes]


    class azure.mgmt.compute.bulkaction.types.ImageReference(SubResource):
        key "communityGalleryImageId": str
        key "id": str
        key "offer": str
        key "publisher": str
        key "sharedGalleryImageId": str
        key "sku": str
        key "version": str
        community_gallery_image_id: str
        id: str
        offer: str
        publisher: str
        shared_gallery_image_id: str
        sku: str
        version: str


    class azure.mgmt.compute.bulkaction.types.KeyVaultKeyReference(TypedDict, total=False):
        key "keyUrl": Required[str]
        key "sourceVault": Required[SubResource]
        key_url: str
        source_vault: SubResource


    class azure.mgmt.compute.bulkaction.types.KeyVaultSecretReference(TypedDict, total=False):
        key "secretUrl": Required[str]
        key "sourceVault": Required[SubResource]
        secret_url: str
        source_vault: SubResource


    class azure.mgmt.compute.bulkaction.types.LaunchBulkInstancesOperationProperties(TypedDict, total=False):
        key "capacity": Required[int]
        key "capacityType": Union[str, CapacityType]
        key "computeProfile": Required[ComputeProfile]
        key "createdTime": str
        key "priorityProfile": Required[PriorityProfile]
        key "provisioningState": Union[str, ProvisioningState]
        key "retryPolicy": ForwardRef('RetryPolicy', module='types')
        key "vmAttributes": ForwardRef('VMAttributes', module='types')
        key "zoneAllocationPolicy": ForwardRef('ZoneAllocationPolicy', module='types')
        capacity: int
        capacity_type: Union[str, CapacityType]
        compute_profile: ComputeProfile
        created_time: str
        priority_profile: PriorityProfile
        provisioning_state: Union[str, ProvisioningState]
        retry_policy: RetryPolicy
        vmSizesProfile: list[VmSizeProfile]
        vm_attributes: VMAttributes
        vm_sizes_profile: list[VmSizeProfile]
        zone_allocation_policy: ZoneAllocationPolicy


    class azure.mgmt.compute.bulkaction.types.LinuxConfiguration(TypedDict, total=False):
        key "disablePasswordAuthentication": bool
        key "enableVMAgentPlatformUpdates": bool
        key "patchSettings": ForwardRef('LinuxPatchSettings', module='types')
        key "provisionVMAgent": bool
        key "ssh": ForwardRef('SshConfiguration', module='types')
        disable_password_authentication: bool
        enable_vm_agent_platform_updates: bool
        patch_settings: LinuxPatchSettings
        provision_vm_agent: bool
        ssh: SshConfiguration


    class azure.mgmt.compute.bulkaction.types.LinuxPatchSettings(TypedDict, total=False):
        key "assessmentMode": Union[str, LinuxPatchAssessmentMode]
        key "automaticByPlatformSettings": ForwardRef('LinuxVMGuestPatchAutomaticByPlatformSettings', module='types')
        key "patchMode": Union[str, LinuxVMGuestPatchMode]
        assessment_mode: Union[str, LinuxPatchAssessmentMode]
        automatic_by_platform_settings: LinuxVMGuestPatchAutomaticByPlatformSettings
        patch_mode: Union[str, LinuxVMGuestPatchMode]


    class azure.mgmt.compute.bulkaction.types.LinuxVMGuestPatchAutomaticByPlatformSettings(TypedDict, total=False):
        key "bypassPlatformSafetyChecksOnUserSchedule": bool
        key "rebootSetting": Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]
        bypass_platform_safety_checks_on_user_schedule: bool
        reboot_setting: Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]


    class azure.mgmt.compute.bulkaction.types.LocationBasedBulkCreateCustom(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "plan": ForwardRef('Plan', module='types')
        key "properties": ForwardRef('BulkCreateCustomProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        plan: Plan
        properties: BulkCreateCustomProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.compute.bulkaction.types.LocationBasedLaunchBulkInstancesOperation(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "plan": ForwardRef('Plan', module='types')
        key "properties": ForwardRef('LaunchBulkInstancesOperationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        plan: Plan
        properties: LaunchBulkInstancesOperationProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: list[str]


    class azure.mgmt.compute.bulkaction.types.ManagedDiskParametersContent(SubResource):
        key "diskEncryptionSet": ForwardRef('DiskEncryptionSetParametersContent', module='types')
        key "id": str
        key "securityProfile": ForwardRef('VMDiskSecurityProfile', module='types')
        key "storageAccountType": Union[str, StorageAccountTypes]
        disk_encryption_set: DiskEncryptionSetParametersContent
        id: str
        security_profile: VMDiskSecurityProfile
        storage_account_type: Union[str, StorageAccountTypes]


    class azure.mgmt.compute.bulkaction.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.compute.bulkaction.types.NetworkInterfaceReference(SubResource):
        key "id": str
        key "properties": ForwardRef('NetworkInterfaceReferenceProperties', module='types')
        id: str
        properties: NetworkInterfaceReferenceProperties


    class azure.mgmt.compute.bulkaction.types.NetworkInterfaceReferenceProperties(TypedDict, total=False):
        key "deleteOption": Union[str, DeleteOptions]
        key "primary": bool
        delete_option: Union[str, DeleteOptions]
        primary: bool


    class azure.mgmt.compute.bulkaction.types.NetworkProfile(TypedDict, total=False):
        key "networkApiVersion": Union[str, NetworkApiVersion]
        networkInterfaceConfigurations: list[VirtualMachineNetworkInterfaceConfiguration]
        networkInterfaces: list[NetworkInterfaceReference]
        network_api_version: Union[str, NetworkApiVersion]
        network_interface_configurations: list[VirtualMachineNetworkInterfaceConfiguration]
        network_interfaces: list[NetworkInterfaceReference]


    class azure.mgmt.compute.bulkaction.types.NotificationProperties(TypedDict, total=False):
        key "destination": Required[str]
        key "disabled": bool
        key "language": Required[Union[str, Language]]
        key "type": Required[Union[str, NotificationType]]
        destination: str
        disabled: bool
        language: Union[str, Language]
        type: Union[str, NotificationType]


    class azure.mgmt.compute.bulkaction.types.OSDisk(TypedDict, total=False):
        key "caching": Union[str, CachingTypes]
        key "createOption": Required[Union[str, DiskCreateOptionTypes]]
        key "deleteOption": Union[str, DiskDeleteOptionTypes]
        key "diffDiskSettings": ForwardRef('DiffDiskSettings', module='types')
        key "diskSizeGB": int
        key "encryptionSettings": ForwardRef('DiskEncryptionSettings', module='types')
        key "image": ForwardRef('VirtualHardDisk', module='types')
        key "managedDisk": ForwardRef('ManagedDiskParametersContent', module='types')
        key "name": str
        key "osType": Union[str, OperatingSystemTypes]
        key "vhd": ForwardRef('VirtualHardDisk', module='types')
        key "writeAcceleratorEnabled": bool
        caching: Union[str, CachingTypes]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Union[str, DiskDeleteOptionTypes]
        diff_disk_settings: DiffDiskSettings
        disk_size_gb: int
        encryption_settings: DiskEncryptionSettings
        image: VirtualHardDisk
        managed_disk: ManagedDiskParametersContent
        name: str
        os_type: Union[str, OperatingSystemTypes]
        vhd: VirtualHardDisk
        write_accelerator_enabled: bool


    class azure.mgmt.compute.bulkaction.types.OSImageNotificationProfile(TypedDict, total=False):
        key "enable": bool
        key "notBeforeTimeout": str
        enable: bool
        not_before_timeout: str


    class azure.mgmt.compute.bulkaction.types.OSProfile(TypedDict, total=False):
        key "adminPassword": str
        key "adminUsername": str
        key "allowExtensionOperations": bool
        key "computerName": str
        key "customData": str
        key "linuxConfiguration": ForwardRef('LinuxConfiguration', module='types')
        key "requireGuestProvisionSignal": bool
        key "windowsConfiguration": ForwardRef('WindowsConfiguration', module='types')
        admin_password: str
        admin_username: str
        allow_extension_operations: bool
        computer_name: str
        custom_data: str
        linux_configuration: LinuxConfiguration
        require_guest_provision_signal: bool
        secrets: list[VaultSecretGroup]
        windows_configuration: WindowsConfiguration


    class azure.mgmt.compute.bulkaction.types.OSProfileProvisioningData(TypedDict, total=False):
        key "adminPassword": str
        key "customData": str
        admin_password: str
        custom_data: str


    class azure.mgmt.compute.bulkaction.types.PatchSettings(TypedDict, total=False):
        key "assessmentMode": Union[str, WindowsPatchAssessmentMode]
        key "automaticByPlatformSettings": ForwardRef('WindowsVMGuestPatchAutomaticByPlatformSettings', module='types')
        key "enableHotpatching": bool
        key "patchMode": Union[str, WindowsVMGuestPatchMode]
        assessment_mode: Union[str, WindowsPatchAssessmentMode]
        automatic_by_platform_settings: WindowsVMGuestPatchAutomaticByPlatformSettings
        enable_hotpatching: bool
        patch_mode: Union[str, WindowsVMGuestPatchMode]


    class azure.mgmt.compute.bulkaction.types.Plan(TypedDict, total=False):
        key "name": Required[str]
        key "product": Required[str]
        key "promotionCode": str
        key "publisher": Required[str]
        key "version": str
        name: str
        product: str
        promotion_code: str
        publisher: str
        version: str


    class azure.mgmt.compute.bulkaction.types.PriorityProfile(TypedDict, total=False):
        key "allocationStrategy": Union[str, AllocationStrategy]
        key "evictionPolicy": Union[str, EvictionPolicy]
        key "maxPricePerVM": float
        key "type": Union[str, PriorityType]
        allocation_strategy: Union[str, AllocationStrategy]
        eviction_policy: Union[str, EvictionPolicy]
        max_price_per_vm: float
        type: Union[str, PriorityType]


    class azure.mgmt.compute.bulkaction.types.ProxyAgentSettings(TypedDict, total=False):
        key "addProxyAgentExtension": bool
        key "enabled": bool
        key "imds": ForwardRef('HostEndpointSettings', module='types')
        key "keyIncarnationId": int
        key "mode": Union[str, Mode]
        key "wireServer": ForwardRef('HostEndpointSettings', module='types')
        add_proxy_agent_extension: bool
        enabled: bool
        imds: HostEndpointSettings
        key_incarnation_id: int
        mode: Union[str, Mode]
        wire_server: HostEndpointSettings


    class azure.mgmt.compute.bulkaction.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.compute.bulkaction.types.PublicIPAddressSku(TypedDict, total=False):
        key "name": Union[str, PublicIPAddressSkuName]
        key "tier": Union[str, PublicIPAddressSkuTier]
        name: Union[str, PublicIPAddressSkuName]
        tier: Union[str, PublicIPAddressSkuTier]


    class azure.mgmt.compute.bulkaction.types.RecurringScheduledActionsExecutionParameters(TypedDict, total=False):
        key "optimizationPreference": Union[str, OptimizationPreference]
        key "retryPolicy": ForwardRef('RecurringScheduledActionsRetryPolicy', module='types')
        optimization_preference: Union[str, OptimizationPreference]
        retry_policy: RecurringScheduledActionsRetryPolicy


    class azure.mgmt.compute.bulkaction.types.RecurringScheduledActionsRetryPolicy(TypedDict, total=False):
        key "onFailureAction": Union[str, RecurringScheduledActionsResourceOperationType]
        key "retryCount": int
        key "retryWindowInMinutes": int
        on_failure_action: Union[str, RecurringScheduledActionsResourceOperationType]
        retry_count: int
        retry_window_in_minutes: int


    class azure.mgmt.compute.bulkaction.types.ReimagePayload(TypedDict, total=False):
        key "baseProfile": ForwardRef('VirtualMachineReimageParameters', module='types')
        base_profile: VirtualMachineReimageParameters
        resourceOverrides: list[ReimageResourceOverride]
        resource_overrides: list[ReimageResourceOverride]


    class azure.mgmt.compute.bulkaction.types.ReimageResourceOverride(TypedDict, total=False):
        key "profile": Required[VirtualMachineReimageParameters]
        key "resourceId": Required[str]
        profile: VirtualMachineReimageParameters
        resource_id: str


    class azure.mgmt.compute.bulkaction.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.compute.bulkaction.types.ResourceAttachRequest(TypedDict, total=False):
        key "resources": Required[list[ScheduledActionResourceInput]]
        resources: list[ScheduledActionResourceInput]


    class azure.mgmt.compute.bulkaction.types.ResourceDetachRequest(TypedDict, total=False):
        key "resources": Required[list[str]]
        resources: list[str]


    class azure.mgmt.compute.bulkaction.types.ResourcePatchRequest(TypedDict, total=False):
        key "resources": Required[list[ScheduledActionResourceInput]]
        resources: list[ScheduledActionResourceInput]


    class azure.mgmt.compute.bulkaction.types.ResourceProvisionPayload(TypedDict, total=False):
        key "resourceCount": Required[int]
        key "resourcePrefix": str
        baseProfile: dict[str, Any]
        base_profile: dict[str, Any]
        resourceOverrides: list[dict[str, Any]]
        resource_count: int
        resource_overrides: list[dict[str, Any]]
        resource_prefix: str


    class azure.mgmt.compute.bulkaction.types.ResourceProvisionVdiPayload(TypedDict, total=False):
        key "flexProperties": Required[FlexProperties]
        key "resourceCount": Required[int]
        key "resourcePrefix": str
        baseProfile: dict[str, Any]
        base_profile: dict[str, Any]
        flex_properties: FlexProperties
        resourceOverrides: list[dict[str, Any]]
        resource_count: int
        resource_overrides: list[dict[str, Any]]
        resource_prefix: str


    class azure.mgmt.compute.bulkaction.types.ResourceWithContext(TypedDict, total=False):
        key "resourceContext": Required[str]
        key "resourceId": Required[str]
        resource_context: str
        resource_id: str


    class azure.mgmt.compute.bulkaction.types.Resources(TypedDict, total=False):
        key "ids": Required[list[str]]
        ids: list[str]


    class azure.mgmt.compute.bulkaction.types.ResourcesWithContext(TypedDict, total=False):
        key "resources": Required[list[ResourceWithContext]]
        resources: list[ResourceWithContext]


    class azure.mgmt.compute.bulkaction.types.RetryPolicy(TypedDict, total=False):
        key "onFailureAction": Union[str, ResourceOperationType]
        key "retryCount": int
        key "retryWindowInMinutes": int
        on_failure_action: Union[str, ResourceOperationType]
        retry_count: int
        retry_window_in_minutes: int


    class azure.mgmt.compute.bulkaction.types.ScheduledAction(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ScheduledActionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ScheduledActionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.compute.bulkaction.types.ScheduledActionProperties(TypedDict, total=False):
        key "actionType": Required[Union[str, ScheduledActionType]]
        key "disabled": bool
        key "endTime": str
        key "notificationSettings": Required[list[NotificationProperties]]
        key "provisioningState": Union[str, RecurringScheduledActionsProvisioningState]
        key "resourceType": Required[Union[str, ResourceType]]
        key "schedule": Required[ScheduledActionsSchedule]
        key "startTime": Required[str]
        action_type: Union[str, ScheduledActionType]
        disabled: bool
        end_time: str
        notification_settings: list[NotificationProperties]
        provisioning_state: Union[str, RecurringScheduledActionsProvisioningState]
        resource_type: Union[str, ResourceType]
        schedule: ScheduledActionsSchedule
        start_time: str


    class azure.mgmt.compute.bulkaction.types.ScheduledActionResourceInput(TypedDict, total=False):
        key "resourceId": Required[str]
        notificationSettings: list[NotificationProperties]
        notification_settings: list[NotificationProperties]
        resource_id: str


    class azure.mgmt.compute.bulkaction.types.ScheduledActionUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ScheduledActionUpdateProperties', module='types')
        properties: ScheduledActionUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.compute.bulkaction.types.ScheduledActionUpdateProperties(TypedDict, total=False):
        key "actionType": Union[str, ScheduledActionType]
        key "disabled": bool
        key "endTime": str
        key "resourceType": Union[str, ResourceType]
        key "schedule": ForwardRef('ScheduledActionsScheduleUpdate', module='types')
        key "startTime": str
        action_type: Union[str, ScheduledActionType]
        disabled: bool
        end_time: str
        notificationSettings: list[NotificationProperties]
        notification_settings: list[NotificationProperties]
        resource_type: Union[str, ResourceType]
        schedule: ScheduledActionsScheduleUpdate
        start_time: str


    class azure.mgmt.compute.bulkaction.types.ScheduledActionsSchedule(TypedDict, total=False):
        key "deadlineType": Union[str, RecurringScheduledActionsDeadlineType]
        key "executionParameters": ForwardRef('RecurringScheduledActionsExecutionParameters', module='types')
        key "scheduledTime": Required[str]
        key "timeZone": Required[str]
        deadline_type: Union[str, RecurringScheduledActionsDeadlineType]
        execution_parameters: RecurringScheduledActionsExecutionParameters
        requestedDaysOfTheMonth: list[int]
        requestedMonths: list[Union[str, Month]]
        requestedWeekDays: list[Union[str, WeekDay]]
        requested_days_of_the_month: list[int]
        requested_months: list[Union[str, Month]]
        requested_week_days: list[Union[str, WeekDay]]
        scheduled_time: str
        time_zone: str


    class azure.mgmt.compute.bulkaction.types.ScheduledActionsScheduleUpdate(TypedDict, total=False):
        key "deadlineType": Union[str, RecurringScheduledActionsDeadlineType]
        key "executionParameters": ForwardRef('RecurringScheduledActionsExecutionParameters', module='types')
        key "scheduledTime": str
        key "timeZone": str
        deadline_type: Union[str, RecurringScheduledActionsDeadlineType]
        execution_parameters: RecurringScheduledActionsExecutionParameters
        requestedDaysOfTheMonth: list[int]
        requestedMonths: list[Union[str, Month]]
        requestedWeekDays: list[Union[str, WeekDay]]
        requested_days_of_the_month: list[int]
        requested_months: list[Union[str, Month]]
        requested_week_days: list[Union[str, WeekDay]]
        scheduled_time: str
        time_zone: str


    class azure.mgmt.compute.bulkaction.types.ScheduledEventsAdditionalPublishingTargets(TypedDict, total=False):
        key "eventGridAndResourceGraph": ForwardRef('EventGridAndResourceGraph', module='types')
        event_grid_and_resource_graph: EventGridAndResourceGraph


    class azure.mgmt.compute.bulkaction.types.ScheduledEventsPolicy(TypedDict, total=False):
        key "allInstancesDown": ForwardRef('AllInstancesDown', module='types')
        key "scheduledEventsAdditionalPublishingTargets": ForwardRef('ScheduledEventsAdditionalPublishingTargets', module='types')
        key "userInitiatedReboot": ForwardRef('UserInitiatedReboot', module='types')
        key "userInitiatedRedeploy": ForwardRef('UserInitiatedRedeploy', module='types')
        all_instances_down: AllInstancesDown
        scheduled_events_additional_publishing_targets: ScheduledEventsAdditionalPublishingTargets
        user_initiated_reboot: UserInitiatedReboot
        user_initiated_redeploy: UserInitiatedRedeploy


    class azure.mgmt.compute.bulkaction.types.ScheduledEventsProfile(TypedDict, total=False):
        key "osImageNotificationProfile": ForwardRef('OSImageNotificationProfile', module='types')
        key "terminateNotificationProfile": ForwardRef('TerminateNotificationProfile', module='types')
        os_image_notification_profile: OSImageNotificationProfile
        terminate_notification_profile: TerminateNotificationProfile


    class azure.mgmt.compute.bulkaction.types.SecurityProfile(TypedDict, total=False):
        key "encryptionAtHost": bool
        key "encryptionIdentity": ForwardRef('EncryptionIdentity', module='types')
        key "proxyAgentSettings": ForwardRef('ProxyAgentSettings', module='types')
        key "securityType": Union[str, SecurityTypes]
        key "uefiSettings": ForwardRef('UefiSettings', module='types')
        encryption_at_host: bool
        encryption_identity: EncryptionIdentity
        proxy_agent_settings: ProxyAgentSettings
        security_type: Union[str, SecurityTypes]
        uefi_settings: UefiSettings


    class azure.mgmt.compute.bulkaction.types.SshConfiguration(TypedDict, total=False):
        publicKeys: list[SshPublicKey]
        public_keys: list[SshPublicKey]


    class azure.mgmt.compute.bulkaction.types.SshPublicKey(TypedDict, total=False):
        key "keyData": str
        key "path": str
        key_data: str
        path: str


    class azure.mgmt.compute.bulkaction.types.StorageProfile(TypedDict, total=False):
        key "diskControllerType": Union[str, DiskControllerTypes]
        key "imageReference": ForwardRef('ImageReference', module='types')
        key "osDisk": ForwardRef('OSDisk', module='types')
        dataDisks: list[DataDisk]
        data_disks: list[DataDisk]
        disk_controller_type: Union[str, DiskControllerTypes]
        image_reference: ImageReference
        os_disk: OSDisk


    class azure.mgmt.compute.bulkaction.types.SubResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.compute.bulkaction.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.compute.bulkaction.types.TerminateNotificationProfile(TypedDict, total=False):
        key "enable": bool
        key "notBeforeTimeout": str
        enable: bool
        not_before_timeout: str


    class azure.mgmt.compute.bulkaction.types.TrackedResource(Resource):
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


    class azure.mgmt.compute.bulkaction.types.UefiSettings(TypedDict, total=False):
        key "secureBootEnabled": bool
        key "vTpmEnabled": bool
        secure_boot_enabled: bool
        v_tpm_enabled: bool


    class azure.mgmt.compute.bulkaction.types.UserAssignedIdentitiesValue(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.compute.bulkaction.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.compute.bulkaction.types.UserInitiatedReboot(TypedDict, total=False):
        key "automaticallyApprove": bool
        user_initiated_reboot_automatically_approve: bool


    class azure.mgmt.compute.bulkaction.types.UserInitiatedRedeploy(TypedDict, total=False):
        key "automaticallyApprove": bool
        user_initiated_redeploy_automatically_approve: bool


    class azure.mgmt.compute.bulkaction.types.VMAttributeMinMaxDouble(TypedDict, total=False):
        key "max": float
        key "min": float
        max: float
        min: float


    class azure.mgmt.compute.bulkaction.types.VMAttributeMinMaxInteger(TypedDict, total=False):
        key "max": int
        key "min": int
        max: int
        min: int


    class azure.mgmt.compute.bulkaction.types.VMAttributes(TypedDict, total=False):
        key "acceleratorCount": ForwardRef('VMAttributeMinMaxInteger', module='types')
        key "acceleratorSupport": Union[str, VMAttributeSupport]
        key "architectureTypes": Required[list[Union[str, ArchitectureType]]]
        key "burstableSupport": Union[str, VMAttributeSupport]
        key "dataDiskCount": ForwardRef('VMAttributeMinMaxInteger', module='types')
        key "localStorageInGiB": ForwardRef('VMAttributeMinMaxDouble', module='types')
        key "localStorageSupport": Union[str, VMAttributeSupport]
        key "memoryInGiB": Required[VMAttributeMinMaxDouble]
        key "memoryInGiBPerVCpu": ForwardRef('VMAttributeMinMaxDouble', module='types')
        key "networkBandwidthInMbps": ForwardRef('VMAttributeMinMaxDouble', module='types')
        key "networkInterfaceCount": ForwardRef('VMAttributeMinMaxInteger', module='types')
        key "rdmaNetworkInterfaceCount": ForwardRef('VMAttributeMinMaxInteger', module='types')
        key "rdmaSupport": Union[str, VMAttributeSupport]
        key "vCpuCount": Required[VMAttributeMinMaxInteger]
        acceleratorManufacturers: list[Union[str, AcceleratorManufacturer]]
        acceleratorTypes: list[Union[str, AcceleratorType]]
        accelerator_count: VMAttributeMinMaxInteger
        accelerator_manufacturers: list[Union[str, AcceleratorManufacturer]]
        accelerator_support: Union[str, VMAttributeSupport]
        accelerator_types: list[Union[str, AcceleratorType]]
        allowedVMSizes: list[str]
        allowed_vm_sizes: list[str]
        architecture_types: list[Union[str, ArchitectureType]]
        burstable_support: Union[str, VMAttributeSupport]
        cpuManufacturers: list[Union[str, CpuManufacturer]]
        cpu_manufacturers: list[Union[str, CpuManufacturer]]
        data_disk_count: VMAttributeMinMaxInteger
        excludedVMSizes: list[str]
        excluded_vm_sizes: list[str]
        hyperVGenerations: list[Union[str, HyperVGeneration]]
        hyper_v_generations: list[Union[str, HyperVGeneration]]
        localStorageDiskTypes: list[Union[str, LocalStorageDiskType]]
        local_storage_disk_types: list[Union[str, LocalStorageDiskType]]
        local_storage_in_gi_b: VMAttributeMinMaxDouble
        local_storage_support: Union[str, VMAttributeSupport]
        memory_in_gi_b: VMAttributeMinMaxDouble
        memory_in_gi_b_per_v_cpu: VMAttributeMinMaxDouble
        network_bandwidth_in_mbps: VMAttributeMinMaxDouble
        network_interface_count: VMAttributeMinMaxInteger
        rdma_network_interface_count: VMAttributeMinMaxInteger
        rdma_support: Union[str, VMAttributeSupport]
        v_cpu_count: VMAttributeMinMaxInteger
        vmCategories: list[Union[str, VMCategory]]
        vm_categories: list[Union[str, VMCategory]]


    class azure.mgmt.compute.bulkaction.types.VMDiskSecurityProfile(TypedDict, total=False):
        key "diskEncryptionSet": ForwardRef('DiskEncryptionSetParametersContent', module='types')
        key "securityEncryptionType": Union[str, SecurityEncryptionTypes]
        disk_encryption_set: DiskEncryptionSetParametersContent
        security_encryption_type: Union[str, SecurityEncryptionTypes]


    class azure.mgmt.compute.bulkaction.types.VMGalleryApplication(TypedDict, total=False):
        key "configurationReference": str
        key "enableAutomaticUpgrade": bool
        key "order": int
        key "packageReferenceId": Required[str]
        key "tags": str
        key "treatFailureAsDeploymentFailure": bool
        configuration_reference: str
        enable_automatic_upgrade: bool
        order: int
        package_reference_id: str
        tags: str
        treat_failure_as_deployment_failure: bool


    class azure.mgmt.compute.bulkaction.types.VaultCertificate(TypedDict, total=False):
        key "certificateStore": str
        key "certificateUrl": str
        certificate_store: str
        certificate_url: str


    class azure.mgmt.compute.bulkaction.types.VaultSecretGroup(TypedDict, total=False):
        key "sourceVault": ForwardRef('SubResource', module='types')
        source_vault: SubResource
        vaultCertificates: list[VaultCertificate]
        vault_certificates: list[VaultCertificate]


    class azure.mgmt.compute.bulkaction.types.VirtualHardDisk(TypedDict, total=False):
        key "uri": str
        uri: str


    class azure.mgmt.compute.bulkaction.types.VirtualMachineIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentitiesValue]
        user_assigned_identities: dict[str, UserAssignedIdentitiesValue]


    class azure.mgmt.compute.bulkaction.types.VirtualMachineIpTag(TypedDict, total=False):
        key "ipTagType": str
        key "tag": str
        ip_tag_type: str
        tag: str


    class azure.mgmt.compute.bulkaction.types.VirtualMachineNetworkInterfaceConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('VirtualMachineNetworkInterfaceConfigurationProperties', module='types')
        name: str
        properties: VirtualMachineNetworkInterfaceConfigurationProperties
        tags: dict[str, str]


    class azure.mgmt.compute.bulkaction.types.VirtualMachineNetworkInterfaceConfigurationProperties(TypedDict, total=False):
        key "auxiliaryMode": Union[str, NetworkInterfaceAuxiliaryMode]
        key "auxiliarySku": Union[str, NetworkInterfaceAuxiliarySku]
        key "deleteOption": Union[str, DeleteOptions]
        key "disableTcpStateTracking": bool
        key "dnsSettings": ForwardRef('VirtualMachineNetworkInterfaceDnsSettingsConfiguration', module='types')
        key "dscpConfiguration": ForwardRef('SubResource', module='types')
        key "enableAcceleratedNetworking": bool
        key "enableFpga": bool
        key "enableIPForwarding": bool
        key "ipConfigurations": Required[list[VirtualMachineNetworkInterfaceIPConfiguration]]
        key "networkSecurityGroup": ForwardRef('SubResource', module='types')
        key "primary": bool
        auxiliary_mode: Union[str, NetworkInterfaceAuxiliaryMode]
        auxiliary_sku: Union[str, NetworkInterfaceAuxiliarySku]
        delete_option: Union[str, DeleteOptions]
        disable_tcp_state_tracking: bool
        dns_settings: VirtualMachineNetworkInterfaceDnsSettingsConfiguration
        dscp_configuration: SubResource
        enable_accelerated_networking: bool
        enable_fpga: bool
        enable_ip_forwarding: bool
        ip_configurations: list[VirtualMachineNetworkInterfaceIPConfiguration]
        network_security_group: SubResource
        primary: bool


    class azure.mgmt.compute.bulkaction.types.VirtualMachineNetworkInterfaceDnsSettingsConfiguration(TypedDict, total=False):
        dnsServers: list[str]
        dns_servers: list[str]


    class azure.mgmt.compute.bulkaction.types.VirtualMachineNetworkInterfaceIPConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('VirtualMachineNetworkInterfaceIPConfigurationProperties', module='types')
        name: str
        properties: VirtualMachineNetworkInterfaceIPConfigurationProperties


    class azure.mgmt.compute.bulkaction.types.VirtualMachineNetworkInterfaceIPConfigurationProperties(TypedDict, total=False):
        key "primary": bool
        key "privateIPAddressVersion": Union[str, IPVersions]
        key "publicIPAddressConfiguration": ForwardRef('VirtualMachinePublicIPAddressConfiguration', module='types')
        key "subnet": ForwardRef('SubResource', module='types')
        applicationGatewayBackendAddressPools: list[SubResource]
        applicationSecurityGroups: list[SubResource]
        application_gateway_backend_address_pools: list[SubResource]
        application_security_groups: list[SubResource]
        loadBalancerBackendAddressPools: list[SubResource]
        load_balancer_backend_address_pools: list[SubResource]
        primary: bool
        private_ip_address_version: Union[str, IPVersions]
        public_ip_address_configuration: VirtualMachinePublicIPAddressConfiguration
        subnet: SubResource


    class azure.mgmt.compute.bulkaction.types.VirtualMachinePublicIPAddressConfiguration(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('VirtualMachinePublicIPAddressConfigurationProperties', module='types')
        key "sku": ForwardRef('PublicIPAddressSku', module='types')
        name: str
        properties: VirtualMachinePublicIPAddressConfigurationProperties
        sku: PublicIPAddressSku
        tags: dict[str, str]


    class azure.mgmt.compute.bulkaction.types.VirtualMachinePublicIPAddressConfigurationProperties(TypedDict, total=False):
        key "deleteOption": Union[str, DeleteOptions]
        key "dnsSettings": ForwardRef('VirtualMachinePublicIPAddressDnsSettingsConfiguration', module='types')
        key "idleTimeoutInMinutes": int
        key "publicIPAddressVersion": Union[str, IPVersions]
        key "publicIPAllocationMethod": Union[str, PublicIPAllocationMethod]
        key "publicIPPrefix": ForwardRef('SubResource', module='types')
        delete_option: Union[str, DeleteOptions]
        dns_settings: VirtualMachinePublicIPAddressDnsSettingsConfiguration
        idle_timeout_in_minutes: int
        ipTags: list[VirtualMachineIpTag]
        ip_tags: list[VirtualMachineIpTag]
        public_ip_address_version: Union[str, IPVersions]
        public_ip_allocation_method: Union[str, PublicIPAllocationMethod]
        public_ip_prefix: SubResource


    class azure.mgmt.compute.bulkaction.types.VirtualMachinePublicIPAddressDnsSettingsConfiguration(TypedDict, total=False):
        key "domainNameLabel": Required[str]
        key "domainNameLabelScope": Union[str, DomainNameLabelScopeTypes]
        domain_name_label: str
        domain_name_label_scope: Union[str, DomainNameLabelScopeTypes]


    class azure.mgmt.compute.bulkaction.types.VirtualMachineReimageParameters(TypedDict, total=False):
        key "exactVersion": str
        key "osProfile": ForwardRef('OSProfileProvisioningData', module='types')
        key "tempDisk": bool
        exact_version: str
        os_profile: OSProfileProvisioningData
        temp_disk: bool


    class azure.mgmt.compute.bulkaction.types.VmSizeProfile(TypedDict, total=False):
        key "name": Required[str]
        key "rank": Required[int]
        name: str
        rank: int


    class azure.mgmt.compute.bulkaction.types.VmSizeProperties(TypedDict, total=False):
        key "vCpusAvailable": int
        key "vCpusPerCore": int
        v_cpus_available: int
        v_cpus_per_core: int


    class azure.mgmt.compute.bulkaction.types.WinRMConfiguration(TypedDict, total=False):
        listeners: list[WinRMListener]


    class azure.mgmt.compute.bulkaction.types.WinRMListener(TypedDict, total=False):
        key "certificateUrl": str
        key "protocol": Union[str, ProtocolTypes]
        certificate_url: str
        protocol: Union[str, ProtocolTypes]


    class azure.mgmt.compute.bulkaction.types.WindowsConfiguration(TypedDict, total=False):
        key "enableAutomaticUpdates": bool
        key "patchSettings": ForwardRef('PatchSettings', module='types')
        key "provisionVMAgent": bool
        key "timeZone": str
        key "winRM": ForwardRef('WinRMConfiguration', module='types')
        additionalUnattendContent: list[AdditionalUnattendContent]
        additional_unattend_content: list[AdditionalUnattendContent]
        enable_automatic_updates: bool
        patch_settings: PatchSettings
        provision_vm_agent: bool
        time_zone: str
        win_rm: WinRMConfiguration


    class azure.mgmt.compute.bulkaction.types.WindowsVMGuestPatchAutomaticByPlatformSettings(TypedDict, total=False):
        key "bypassPlatformSafetyChecksOnUserSchedule": bool
        key "rebootSetting": Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]
        bypass_platform_safety_checks_on_user_schedule: bool
        reboot_setting: Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]


    class azure.mgmt.compute.bulkaction.types.ZoneAllocationPolicy(TypedDict, total=False):
        key "distributionStrategy": Union[str, DistributionStrategy]
        distribution_strategy: Union[str, DistributionStrategy]
        zonePreferences: list[ZonePreference]
        zone_preferences: list[ZonePreference]


    class azure.mgmt.compute.bulkaction.types.ZonePreference(TypedDict, total=False):
        key "rank": Required[int]
        key "zone": Required[str]
        rank: int
        zone: str


```