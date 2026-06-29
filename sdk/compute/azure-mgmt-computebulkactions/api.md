```py
namespace azure.mgmt.computebulkactions

    class azure.mgmt.computebulkactions.ComputeClient: implements ContextManager 
        operations: Operations
        virtual_machine_bulk_operations: VirtualMachineBulkOperationsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.computebulkactions.aio

    class azure.mgmt.computebulkactions.aio.ComputeClient: implements AsyncContextManager 
        operations: Operations
        virtual_machine_bulk_operations: VirtualMachineBulkOperationsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.computebulkactions.aio.operations

    class azure.mgmt.computebulkactions.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.computebulkactions.aio.operations.VirtualMachineBulkOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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


namespace azure.mgmt.computebulkactions.models

    class azure.mgmt.computebulkactions.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computebulkactions.models.CancelOperationsContent(_Model):
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CancelOperationsResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DeadlineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE_BY = "CompleteBy"
        INITIATE_AT = "InitiateAt"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.DeallocateResourceOperationResponse(_Model):
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


    class azure.mgmt.computebulkactions.models.DeleteResourceOperationResponse(_Model):
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


    class azure.mgmt.computebulkactions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computebulkactions.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computebulkactions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteDeallocateContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteDeleteContent(_Model):
        execution_parameters: ExecutionParameters
        force_deletion: Optional[bool]
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                force_deletion: Optional[bool] = ..., 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteHibernateContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteStartContent(_Model):
        execution_parameters: ExecutionParameters
        resources: Resources

        @overload
        def __init__(
                self, 
                *, 
                execution_parameters: ExecutionParameters, 
                resources: Resources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecutionParameters(_Model):
        retry_policy: Optional[RetryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                retry_policy: Optional[RetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.FallbackOperationInfo(_Model):
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


    class azure.mgmt.computebulkactions.models.GetOperationStatusContent(_Model):
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.GetOperationStatusResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.HibernateResourceOperationResponse(_Model):
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


    class azure.mgmt.computebulkactions.models.Operation(_Model):
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


    class azure.mgmt.computebulkactions.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computebulkactions.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        CANCELLED = "Cancelled"
        EXECUTING = "Executing"
        FAILED = "Failed"
        PENDING_EXECUTION = "PendingExecution"
        PENDING_SCHEDULING = "PendingScheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computebulkactions.models.ResourceOperation(_Model):
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


    class azure.mgmt.computebulkactions.models.ResourceOperationDetails(_Model):
        completed_at: Optional[datetime]
        deadline: Optional[datetime]
        deadline_type: Optional[Union[str, DeadlineType]]
        fallback_operation_info: Optional[FallbackOperationInfo]
        op_type: Optional[Union[str, ResourceOperationType]]
        operation_id: str
        resource_id: Optional[str]
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
                resource_operation_error: Optional[ResourceOperationError] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                state: Optional[Union[str, OperationState]] = ..., 
                subscription_id: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ResourceOperationError(_Model):
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


    class azure.mgmt.computebulkactions.models.ResourceOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"
        HIBERNATE = "Hibernate"
        START = "Start"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.Resources(_Model):
        ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.RetryPolicy(_Model):
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


    class azure.mgmt.computebulkactions.models.StartResourceOperationResponse(_Model):
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


namespace azure.mgmt.computebulkactions.operations

    class azure.mgmt.computebulkactions.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.computebulkactions.operations.VirtualMachineBulkOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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
                request_body: JSON, 
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


```