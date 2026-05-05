```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.computeschedule

    class azure.mgmt.computeschedule.ComputeScheduleMgmtClient: implements ContextManager 
        occurrence_extension: OccurrenceExtensionOperations
        occurrences: OccurrencesOperations
        operations: Operations
        scheduled_action_extension: ScheduledActionExtensionOperations
        scheduled_actions: ScheduledActionsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.computeschedule.aio

    class azure.mgmt.computeschedule.aio.ComputeScheduleMgmtClient: implements AsyncContextManager 
        occurrence_extension: OccurrenceExtensionOperations
        occurrences: OccurrencesOperations
        operations: Operations
        scheduled_action_extension: ScheduledActionExtensionOperations
        scheduled_actions: ScheduledActionsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.computeschedule.aio.operations

    class azure.mgmt.computeschedule.aio.operations.OccurrenceExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_occurrence_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OccurrenceExtensionResource]: ...


    class azure.mgmt.computeschedule.aio.operations.OccurrencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> AsyncLROPoller[RecurringActionsResourceOperationResult]: ...

        @overload
        async def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RecurringActionsResourceOperationResult]: ...

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
            ) -> AsyncLROPoller[RecurringActionsResourceOperationResult]: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_scheduled_action(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Occurrence]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OccurrenceResource]: ...


    class azure.mgmt.computeschedule.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.computeschedule.aio.operations.ScheduledActionExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledActionResources]: ...


    class azure.mgmt.computeschedule.aio.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def disable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def enable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
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
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        async def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        async def trigger_manual_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: CancelOperationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: ExecuteCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: ExecuteDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: ExecuteDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: ExecuteHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: ExecuteStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: GetOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        async def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        async def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: GetOperationStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: SubmitDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: SubmitHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: SubmitStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...


namespace azure.mgmt.computeschedule.models

    class azure.mgmt.computeschedule.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computeschedule.models.CancelOccurrenceRequest(_Model):
        resource_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.CancelOperationsRequest(_Model):
        correlationid: str
        operation_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                operation_ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.CancelOperationsResponse(_Model):
        results: List[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: List[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.CreateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[List[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[List[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computeschedule.models.DeadlineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE_BY = "CompleteBy"
        INITIATE_AT = "InitiateAt"
        UNKNOWN = "Unknown"


    class azure.mgmt.computeschedule.models.DeallocateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[List[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[List[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.DelayRequest(_Model):
        delay: datetime
        resource_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                delay: datetime, 
                resource_ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.DeleteResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[List[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[List[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computeschedule.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computeschedule.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecuteCreateRequest(_Model):
        correlationid: Optional[str]
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionPayload

        @overload
        def __init__(
                self, 
                *, 
                correlationid: Optional[str] = ..., 
                execution_parameters: ExecutionParameters, 
                resource_config_parameters: ResourceProvisionPayload
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecuteDeallocateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecuteDeleteRequest(_Model):
        correlationid: Optional[str]
        execution_parameters: ExecutionParameters
        force_deletion: Optional[bool]
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                correlationid: Optional[str] = ..., 
                execution_parameters: ExecutionParameters, 
                force_deletion: Optional[bool] = ..., 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecuteHibernateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecuteStartRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExecutionParameters(_Model):
        optimization_preference: Optional[Union[str, OptimizationPreference]]
        retry_policy: Optional[RetryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                optimization_preference: Optional[Union[str, OptimizationPreference]] = ..., 
                retry_policy: Optional[RetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computeschedule.models.GetOperationErrorsRequest(_Model):
        operation_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.GetOperationErrorsResponse(_Model):
        results: List[OperationErrorsResult]

        @overload
        def __init__(
                self, 
                *, 
                results: List[OperationErrorsResult]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.GetOperationStatusRequest(_Model):
        correlationid: str
        operation_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                operation_ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.GetOperationStatusResponse(_Model):
        results: List[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: List[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.HibernateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[List[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[List[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.Language(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EN_US = "en-us"


    class azure.mgmt.computeschedule.models.Month(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.computeschedule.models.NotificationProperties(_Model):
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


    class azure.mgmt.computeschedule.models.NotificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL = "Email"


    class azure.mgmt.computeschedule.models.Occurrence(ProxyResource):
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


    class azure.mgmt.computeschedule.models.OccurrenceExtensionProperties(_Model):
        error_details: Optional[ODataV4Format]
        notification_settings: Optional[List[NotificationProperties]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resource_id: str
        scheduled_action_id: str
        scheduled_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[List[NotificationProperties]] = ..., 
                resource_id: str, 
                scheduled_action_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.OccurrenceExtensionResource(ExtensionResource):
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


    class azure.mgmt.computeschedule.models.OccurrenceProperties(_Model):
        provisioning_state: Optional[Union[str, OccurrenceState]]
        result_summary: OccurrenceResultSummary
        scheduled_time: datetime


    class azure.mgmt.computeschedule.models.OccurrenceResource(_Model):
        error_details: Optional[ODataV4Format]
        id: str
        name: str
        notification_settings: Optional[List[NotificationProperties]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resource_id: str
        scheduled_time: datetime
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[List[NotificationProperties]] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.OccurrenceResultSummary(_Model):
        statuses: List[ResourceResultSummary]
        total: int

        @overload
        def __init__(
                self, 
                *, 
                statuses: List[ResourceResultSummary], 
                total: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.OccurrenceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        CREATED = "Created"
        FAILED = "Failed"
        RESCHEDULING = "Rescheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computeschedule.models.Operation(_Model):
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


    class azure.mgmt.computeschedule.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computeschedule.models.OperationErrorDetails(_Model):
        azure_operation_name: Optional[str]
        crp_operation_id: Optional[str]
        error_code: str
        error_details: str
        time_stamp: Optional[datetime]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                azure_operation_name: Optional[str] = ..., 
                crp_operation_id: Optional[str] = ..., 
                error_code: str, 
                error_details: str, 
                time_stamp: Optional[datetime] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.OperationErrorsResult(_Model):
        activation_time: Optional[datetime]
        completed_at: Optional[datetime]
        creation_time: Optional[datetime]
        operation_errors: Optional[List[OperationErrorDetails]]
        operation_id: Optional[str]
        request_error_code: Optional[str]
        request_error_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                activation_time: Optional[datetime] = ..., 
                completed_at: Optional[datetime] = ..., 
                creation_time: Optional[datetime] = ..., 
                operation_errors: Optional[List[OperationErrorDetails]] = ..., 
                operation_id: Optional[str] = ..., 
                request_error_code: Optional[str] = ..., 
                request_error_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        CANCELLED = "Cancelled"
        EXECUTING = "Executing"
        FAILED = "Failed"
        PENDING_EXECUTION = "PendingExecution"
        PENDING_SCHEDULING = "PendingScheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.computeschedule.models.OptimizationPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        COST = "Cost"
        COST_AVAILABILITY_BALANCED = "CostAvailabilityBalanced"


    class azure.mgmt.computeschedule.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computeschedule.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computeschedule.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computeschedule.models.RecurringActionsResourceOperationResult(_Model):
        resources_statuses: List[ResourceStatus]
        total_resources: int

        @overload
        def __init__(
                self, 
                *, 
                resources_statuses: List[ResourceStatus], 
                total_resources: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computeschedule.models.ResourceAttachRequest(_Model):
        resources: List[ScheduledActionResource]

        @overload
        def __init__(
                self, 
                *, 
                resources: List[ScheduledActionResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceDetachRequest(_Model):
        resources: List[str]

        @overload
        def __init__(
                self, 
                *, 
                resources: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceOperation(_Model):
        error_code: Optional[str]
        error_details: Optional[str]
        operation: Optional[ResourceOperationDetails]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_details: Optional[str] = ..., 
                operation: Optional[ResourceOperationDetails] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceOperationDetails(_Model):
        completed_at: Optional[datetime]
        deadline: Optional[datetime]
        deadline_type: Optional[Union[str, DeadlineType]]
        op_type: Optional[Union[str, ResourceOperationType]]
        operation_id: str
        resource_id: Optional[str]
        resource_operation_error: Optional[ResourceOperationError]
        retry_policy: Optional[RetryPolicy]
        state: Optional[Union[str, OperationState]]
        subscription_id: Optional[str]
        time_zone: Optional[str]
        timezone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                deadline: Optional[datetime] = ..., 
                deadline_type: Optional[Union[str, DeadlineType]] = ..., 
                op_type: Optional[Union[str, ResourceOperationType]] = ..., 
                operation_id: str, 
                resource_id: Optional[str] = ..., 
                resource_operation_error: Optional[ResourceOperationError] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                state: Optional[Union[str, OperationState]] = ..., 
                subscription_id: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceOperationError(_Model):
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


    class azure.mgmt.computeschedule.models.ResourceOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computeschedule.models.ResourceOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        HIBERNATE = "Hibernate"
        START = "Start"
        UNKNOWN = "Unknown"


    class azure.mgmt.computeschedule.models.ResourcePatchRequest(_Model):
        resources: List[ScheduledActionResource]

        @overload
        def __init__(
                self, 
                *, 
                resources: List[ScheduledActionResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceProvisionPayload(_Model):
        base_profile: Optional[Dict[str, Any]]
        resource_count: int
        resource_overrides: Optional[List[Dict[str, Any]]]
        resource_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_profile: Optional[Dict[str, Any]] = ..., 
                resource_count: int, 
                resource_overrides: Optional[List[Dict[str, Any]]] = ..., 
                resource_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computeschedule.models.ResourceResultSummary(_Model):
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


    class azure.mgmt.computeschedule.models.ResourceStatus(_Model):
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


    class azure.mgmt.computeschedule.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VIRTUAL_MACHINE = "VirtualMachine"
        VIRTUAL_MACHINE_SCALE_SET = "VirtualMachineScaleSet"


    class azure.mgmt.computeschedule.models.Resources(_Model):
        ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                ids: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.RetryPolicy(_Model):
        retry_count: Optional[int]
        retry_window_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                retry_count: Optional[int] = ..., 
                retry_window_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.Schedule(_Model):
        dead_line: Optional[datetime]
        deadline: Optional[datetime]
        deadline_type: Union[str, DeadlineType]
        time_zone: Optional[str]
        timezone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dead_line: Optional[datetime] = ..., 
                deadline: Optional[datetime] = ..., 
                deadline_type: Union[str, DeadlineType], 
                time_zone: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledAction(TrackedResource):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionProperties(_Model):
        action_type: Union[str, ScheduledActionType]
        disabled: Optional[bool]
        end_time: Optional[datetime]
        notification_settings: List[NotificationProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
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
                notification_settings: List[NotificationProperties], 
                resource_type: Union[str, ResourceType], 
                schedule: ScheduledActionsSchedule, 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionResource(_Model):
        id: str
        name: str
        notification_settings: Optional[List[NotificationProperties]]
        resource_id: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                notification_settings: Optional[List[NotificationProperties]] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionResources(ExtensionResource):
        id: str
        name: str
        properties: Optional[ScheduledActionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledActionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        HIBERNATE = "Hibernate"
        START = "Start"


    class azure.mgmt.computeschedule.models.ScheduledActionUpdate(_Model):
        properties: Optional[ScheduledActionUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduledActionUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionUpdateProperties(_Model):
        action_type: Optional[Union[str, ScheduledActionType]]
        disabled: Optional[bool]
        end_time: Optional[datetime]
        notification_settings: Optional[List[NotificationProperties]]
        resource_type: Optional[Union[str, ResourceType]]
        schedule: Optional[ScheduledActionsSchedule]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ScheduledActionType]] = ..., 
                disabled: Optional[bool] = ..., 
                end_time: Optional[datetime] = ..., 
                notification_settings: Optional[List[NotificationProperties]] = ..., 
                resource_type: Optional[Union[str, ResourceType]] = ..., 
                schedule: Optional[ScheduledActionsSchedule] = ..., 
                start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.ScheduledActionsSchedule(_Model):
        deadline_type: Optional[Union[str, DeadlineType]]
        execution_parameters: Optional[ExecutionParameters]
        requested_days_of_the_month: List[int]
        requested_months: List[Union[str, Month]]
        requested_week_days: List[Union[str, WeekDay]]
        scheduled_time: time
        time_zone: str

        @overload
        def __init__(
                self, 
                *, 
                deadline_type: Optional[Union[str, DeadlineType]] = ..., 
                execution_parameters: Optional[ExecutionParameters] = ..., 
                requested_days_of_the_month: List[int], 
                requested_months: List[Union[str, Month]], 
                requested_week_days: List[Union[str, WeekDay]], 
                scheduled_time: time, 
                time_zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.StartResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[List[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[List[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.SubmitDeallocateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources
        schedule: Schedule

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources, 
                schedule: Schedule
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.SubmitHibernateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources
        schedule: Schedule

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources, 
                schedule: Schedule
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.SubmitStartRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Resources
        schedule: Schedule

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Resources, 
                schedule: Schedule
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.SystemData(_Model):
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


    class azure.mgmt.computeschedule.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computeschedule.models.WeekDay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


namespace azure.mgmt.computeschedule.operations

    class azure.mgmt.computeschedule.operations.OccurrenceExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_occurrence_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[OccurrenceExtensionResource]: ...


    class azure.mgmt.computeschedule.operations.OccurrencesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> LROPoller[RecurringActionsResourceOperationResult]: ...

        @overload
        def begin_delay(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RecurringActionsResourceOperationResult]: ...

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
            ) -> LROPoller[RecurringActionsResourceOperationResult]: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def cancel(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_scheduled_action(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Occurrence]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'occurrence_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                occurrence_id: str, 
                **kwargs: Any
            ) -> ItemPaged[OccurrenceResource]: ...


    class azure.mgmt.computeschedule.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.computeschedule.operations.ScheduledActionExtensionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'resource_uri', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_vms(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledActionResources]: ...


    class azure.mgmt.computeschedule.operations.ScheduledActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceAttachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def attach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: CancelOccurrenceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def cancel_next_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: ResourceDetachRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def detach_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def disable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def enable(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ScheduledAction]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
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
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @overload
        def patch_resources(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RecurringActionsResourceOperationResult: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-04-15-preview', params_added_on={'2025-04-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'scheduled_action_name', 'accept']}, api_versions_list=['2025-04-15-preview'])
        def trigger_manual_occurrence(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                **kwargs: Any
            ) -> Occurrence: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: ScheduledActionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scheduled_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledAction: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: CancelOperationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: ExecuteCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: ExecuteDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: ExecuteDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: ExecuteHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: ExecuteStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: GetOperationErrorsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        def virtual_machines_get_operation_errors(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationErrorsResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: GetOperationStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: SubmitDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_deallocate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: SubmitHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_hibernate(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: SubmitStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_submit_start(
                self, 
                locationparameter: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...


```