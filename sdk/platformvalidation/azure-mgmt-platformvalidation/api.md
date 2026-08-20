```py
namespace azure.mgmt.platformvalidation

    class azure.mgmt.platformvalidation.PlatformValidationClient: implements ContextManager 
        cloud_validations: CloudValidationsOperations
        execution_plan_runs: ExecutionPlanRunsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        validation_execution_plans: ValidationExecutionPlansOperations
        validation_test_categories: ValidationTestCategoriesOperations
        validation_test_runs: ValidationTestRunsOperations
        validation_test_versions: ValidationTestVersionsOperations
        validation_tests: ValidationTestsOperations

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


namespace azure.mgmt.platformvalidation.aio

    class azure.mgmt.platformvalidation.aio.PlatformValidationClient: implements AsyncContextManager 
        cloud_validations: CloudValidationsOperations
        execution_plan_runs: ExecutionPlanRunsOperations
        operation_status: OperationStatusOperations
        operations: Operations
        validation_execution_plans: ValidationExecutionPlansOperations
        validation_test_categories: ValidationTestCategoriesOperations
        validation_test_runs: ValidationTestRunsOperations
        validation_test_versions: ValidationTestVersionsOperations
        validation_tests: ValidationTestsOperations

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


namespace azure.mgmt.platformvalidation.aio.operations

    class azure.mgmt.platformvalidation.aio.operations.CloudValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: CloudValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: CloudValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: CloudValidationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: CloudValidationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudValidation]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                **kwargs: Any
            ) -> CloudValidation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudValidation]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudValidation]: ...


    class azure.mgmt.platformvalidation.aio.operations.ExecutionPlanRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: ExecutionPlanRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExecutionPlanRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: ExecutionPlanRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExecutionPlanRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExecutionPlanRun]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> ExecutionPlanRun: ...

        @distributed_trace
        def list_by_execution_plan(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExecutionPlanRun]: ...


    class azure.mgmt.platformvalidation.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.platformvalidation.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.platformvalidation.aio.operations.ValidationExecutionPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: ValidationExecutionPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: ValidationExecutionPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: ValidationExecutionPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: ValidationExecutionPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationExecutionPlan]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                **kwargs: Any
            ) -> ValidationExecutionPlan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidationExecutionPlan]: ...


    class azure.mgmt.platformvalidation.aio.operations.ValidationTestCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                validation_test_category_name: str, 
                **kwargs: Any
            ) -> ValidationTestCategory: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidationTestCategory]: ...


    class azure.mgmt.platformvalidation.aio.operations.ValidationTestRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: ValidationTestRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationTestRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: ValidationTestRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationTestRun]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidationTestRun]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                **kwargs: Any
            ) -> ValidationTestRun: ...

        @distributed_trace
        def list_by_execution_plan_run(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidationTestRun]: ...


    class azure.mgmt.platformvalidation.aio.operations.ValidationTestVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                validation_test_name: str, 
                version: str, 
                **kwargs: Any
            ) -> ValidationTestVersion: ...

        @distributed_trace
        def list(
                self, 
                validation_test_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidationTestVersion]: ...


    class azure.mgmt.platformvalidation.aio.operations.ValidationTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                validation_test_name: str, 
                **kwargs: Any
            ) -> ValidationTest: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidationTest]: ...


namespace azure.mgmt.platformvalidation.models

    class azure.mgmt.platformvalidation.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.platformvalidation.models.CatalogAudience(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"
        PUBLIC = "Public"


    @dataclass(frozen=True)
    class azure.mgmt.platformvalidation.models.CertificationPackageReference:
        additional_properties: Mapping[str, Any]
        architecture_type: str
        os_type: str
        recommended_vm_sizes: Sequence[str]
        storage_profile: StorageProfile
        vm_generation_type: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                os_type: str,
                vm_generation_type: str,
                architecture_type: str,
                recommended_vm_sizes: Sequence[str],
                storage_profile: StorageProfile,
                additional_properties: Mapping[str, Any]
            ) -> None: ...

        def __post_init__(self) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    class azure.mgmt.platformvalidation.models.CloudValidation(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CloudValidationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CloudValidationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.CloudValidationOverallState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.platformvalidation.models.CloudValidationProperties(_Model):
        description: Optional[str]
        error: Optional[ErrorDetail]
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        overall_state: Optional[Union[str, CloudValidationOverallState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                overall_state: Optional[Union[str, CloudValidationOverallState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.CloudValidationUpdate(_Model):
        properties: Optional[CloudValidationUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudValidationUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.CloudValidationUpdateProperties(_Model):
        description: Optional[str]
        overall_state: Optional[Union[str, CloudValidationOverallState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                overall_state: Optional[Union[str, CloudValidationOverallState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    @dataclass(frozen=True)
    class azure.mgmt.platformvalidation.models.DiskImage:
        source_vhd_uri: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(source_vhd_uri: str) -> None: ...

        def __post_init__(self) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    class azure.mgmt.platformvalidation.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.platformvalidation.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.platformvalidation.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    @dataclass(frozen=True)
    class azure.mgmt.platformvalidation.models.ExecutionPlanConfiguration:
        API_VERSION: ClassVar[str] = microsoft.validate/executionPlan.v0
        KIND: ClassVar[str] = ExecutionPlan
        certification_package_reference: CertificationPackageReference
        name: str
        steps: Sequence[ValidationStep]

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                name: str,
                certification_package_reference: CertificationPackageReference,
                steps: Sequence[ValidationStep]
            ) -> None: ...

        def __post_init__(self) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...

        def to_json(self) -> str: ...


    class azure.mgmt.platformvalidation.models.ExecutionPlanRun(ProxyResource):
        id: str
        name: str
        properties: Optional[ExecutionPlanRunProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExecutionPlanRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ExecutionPlanRunProperties(_Model):
        completed_at: Optional[datetime]
        description: Optional[str]
        error: Optional[ErrorDetail]
        plan_configuration_snapshot: Optional[str]
        provisioning_state: Optional[Union[str, ExecutionPlanRunProvisioningState]]
        reported_at: Optional[datetime]
        started_at: Optional[datetime]
        status: Optional[Union[str, ExecutionPlanRunStatus]]
        test_run_ids: Optional[list[str]]
        test_run_summary: Optional[TestRunSummary]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ExecutionPlanRunProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        PROCESSING = "Processing"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        WAITING = "Waiting"


    class azure.mgmt.platformvalidation.models.ExecutionPlanRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        QUEUED = "Queued"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.platformvalidation.models.ManagedOnBehalfOfConfiguration(_Model):
        mobo_broker_resources: Optional[list[MoboBrokerResource]]


    class azure.mgmt.platformvalidation.models.MoboBrokerResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.Operation(_Model):
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


    class azure.mgmt.platformvalidation.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.platformvalidation.models.OperationStatusResult(_Model):
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


    class azure.mgmt.platformvalidation.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.platformvalidation.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLING = "Disabling"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.platformvalidation.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.platformvalidation.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.platformvalidation.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    @dataclass(frozen=True)
    class azure.mgmt.platformvalidation.models.StorageProfile:
        data_disk_images: Sequence[DiskImage]
        os_disk_image: DiskImage

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(os_disk_image: DiskImage, data_disk_images: Sequence[DiskImage]) -> None: ...

        def __post_init__(self) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...


    class azure.mgmt.platformvalidation.models.SystemData(_Model):
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


    class azure.mgmt.platformvalidation.models.TestRunOverallResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PARTIALLY_PASSED = "PartiallyPassed"
        PASSED = "Passed"


    class azure.mgmt.platformvalidation.models.TestRunSummary(_Model):
        failed_tests: Optional[int]
        message: Optional[str]
        overall_result: Optional[Union[str, TestRunOverallResult]]
        passed_tests: Optional[int]
        skipped_tests: Optional[int]
        total_tests: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_tests: Optional[int] = ..., 
                message: Optional[str] = ..., 
                overall_result: Optional[Union[str, TestRunOverallResult]] = ..., 
                passed_tests: Optional[int] = ..., 
                skipped_tests: Optional[int] = ..., 
                total_tests: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.TrackedResource(Resource):
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


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlan(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ValidationExecutionPlanProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ValidationExecutionPlanProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlanOverallState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlanProperties(_Model):
        description: Optional[str]
        error: Optional[ErrorDetail]
        overall_state: Optional[Union[str, ValidationExecutionPlanOverallState]]
        plan_configuration_json: Optional[str]
        plan_configuration_uri: Optional[str]
        provisioning_state: Optional[Union[str, ValidationExecutionPlanProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                overall_state: Optional[Union[str, ValidationExecutionPlanOverallState]] = ..., 
                plan_configuration_json: Optional[str] = ..., 
                plan_configuration_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlanProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlanUpdate(_Model):
        properties: Optional[ValidationExecutionPlanUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationExecutionPlanUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationExecutionPlanUpdateProperties(_Model):
        description: Optional[str]
        overall_state: Optional[Union[str, ValidationExecutionPlanOverallState]]
        plan_configuration_json: Optional[str]
        plan_configuration_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                overall_state: Optional[Union[str, ValidationExecutionPlanOverallState]] = ..., 
                plan_configuration_json: Optional[str] = ..., 
                plan_configuration_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    @dataclass(frozen=True)
    class azure.mgmt.platformvalidation.models.ValidationStep:
        inputs: Optional[Mapping[str, Any]]
        name: str
        test_ref: str

        def __delattr__() -> None: ...

        def __eq__() -> None: ...

        def __hash__() -> None: ...

        def __init__(
                name: str,
                test_ref: str,
                inputs: Optional[Mapping[str, Any]]
            ) -> None: ...

        def __post_init__(self) -> None: ...

        def __repr__() -> None: ...

        def __setattr__() -> None: ...

        @classmethod
        def test(
                cls,
                *,
                inputs: Optional[Mapping[str, Any]] = ...,
                name: str,
                test_ref: str
            ) -> ValidationStep: ...


    class azure.mgmt.platformvalidation.models.ValidationTest(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidationTestProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationTestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestCategory(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidationTestCategoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationTestCategoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestCategoryProperties(_Model):
        audience: Optional[Union[str, CatalogAudience]]
        description: Optional[str]
        display_name: Optional[str]
        owners: Optional[list[str]]
        parent_category_id: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                audience: Optional[Union[str, CatalogAudience]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                owners: Optional[list[str]] = ..., 
                parent_category_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestFailureDetails(_Model):
        details: Optional[str]
        diagnostic_info: Optional[str]
        error_code: Optional[str]
        error_message: Optional[str]
        recommended_actions: Optional[list[str]]


    class azure.mgmt.platformvalidation.models.ValidationTestInput(_Model):
        definition: ValidationTestInputDefinition
        name: str

        @overload
        def __init__(
                self, 
                *, 
                definition: ValidationTestInputDefinition, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestInputDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "Array"
        BOOLEAN = "Boolean"
        INTEGER = "Integer"
        NUMBER = "Number"
        OBJECT = "Object"
        STRING = "String"


    class azure.mgmt.platformvalidation.models.ValidationTestInputDefinition(_Model):
        allowed_values: Optional[list[str]]
        default_value: Optional[str]
        description: Optional[str]
        required: Optional[bool]
        type: Optional[Union[str, ValidationTestInputDataType]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: Optional[list[str]] = ..., 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                type: Optional[Union[str, ValidationTestInputDataType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestOverallState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISABLED = "Disabled"
        DRAFT = "Draft"
        PUBLISHED = "Published"


    class azure.mgmt.platformvalidation.models.ValidationTestPassDetails(_Model):
        result_code: Optional[str]
        result_details: Optional[str]
        test_name: Optional[str]


    class azure.mgmt.platformvalidation.models.ValidationTestProperties(_Model):
        audience: Optional[Union[str, CatalogAudience]]
        category_ids: Optional[list[str]]
        current_version: Optional[str]
        description: Optional[str]
        inputs: Optional[list[ValidationTestInput]]
        last_published_at: Optional[datetime]
        latest_published_version: Optional[str]
        overall_state: Optional[Union[str, ValidationTestOverallState]]
        owners: Optional[list[str]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        test_store_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                audience: Optional[Union[str, CatalogAudience]] = ..., 
                category_ids: Optional[list[str]] = ..., 
                current_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: Optional[list[ValidationTestInput]] = ..., 
                last_published_at: Optional[datetime] = ..., 
                latest_published_version: Optional[str] = ..., 
                overall_state: Optional[Union[str, ValidationTestOverallState]] = ..., 
                owners: Optional[list[str]] = ..., 
                test_store_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestRun(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidationTestRunProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationTestRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestRunProperties(_Model):
        completed_at: Optional[datetime]
        error: Optional[ErrorDetail]
        failure_details: Optional[list[ValidationTestFailureDetails]]
        inputs_json: Optional[str]
        pass_details: Optional[list[ValidationTestPassDetails]]
        provisioning_state: Optional[Union[str, ValidationTestRunProvisioningState]]
        reported_at: Optional[datetime]
        started_at: Optional[datetime]
        status: Optional[Union[str, ValidationTestRunStatus]]
        test_category_ids: Optional[list[str]]
        test_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                inputs_json: Optional[str] = ..., 
                test_category_ids: Optional[list[str]] = ..., 
                test_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestRunProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.platformvalidation.models.ValidationTestRunStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        ERROR = "Error"
        NOT_RUNNING = "NotRunning"
        READY = "Ready"
        RUNNING = "Running"
        SCHEDULED = "Scheduled"
        STOPPED = "Stopped"


    class azure.mgmt.platformvalidation.models.ValidationTestVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidationTestVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidationTestVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.platformvalidation.models.ValidationTestVersionProperties(_Model):
        audience: Optional[Union[str, CatalogAudience]]
        category_ids: Optional[list[str]]
        content_hash: Optional[str]
        description: Optional[str]
        inputs: Optional[list[ValidationTestInput]]
        overall_state: Optional[Union[str, ValidationTestOverallState]]
        owners: Optional[list[str]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        test_store_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                audience: Optional[Union[str, CatalogAudience]] = ..., 
                category_ids: Optional[list[str]] = ..., 
                content_hash: Optional[str] = ..., 
                description: Optional[str] = ..., 
                inputs: Optional[list[ValidationTestInput]] = ..., 
                overall_state: Optional[Union[str, ValidationTestOverallState]] = ..., 
                owners: Optional[list[str]] = ..., 
                test_store_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.platformvalidation.operations

    class azure.mgmt.platformvalidation.operations.CloudValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: CloudValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: CloudValidation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: CloudValidationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: CloudValidationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudValidation]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                **kwargs: Any
            ) -> CloudValidation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudValidation]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CloudValidation]: ...


    class azure.mgmt.platformvalidation.operations.ExecutionPlanRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: ExecutionPlanRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExecutionPlanRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: ExecutionPlanRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExecutionPlanRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExecutionPlanRun]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> ExecutionPlanRun: ...

        @distributed_trace
        def list_by_execution_plan(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExecutionPlanRun]: ...


    class azure.mgmt.platformvalidation.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.platformvalidation.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.platformvalidation.operations.ValidationExecutionPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: ValidationExecutionPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: ValidationExecutionPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: ValidationExecutionPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: ValidationExecutionPlanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationExecutionPlan]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                **kwargs: Any
            ) -> ValidationExecutionPlan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ValidationExecutionPlan]: ...


    class azure.mgmt.platformvalidation.operations.ValidationTestCategoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                validation_test_category_name: str, 
                **kwargs: Any
            ) -> ValidationTestCategory: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ValidationTestCategory]: ...


    class azure.mgmt.platformvalidation.operations.ValidationTestRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: ValidationTestRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationTestRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: ValidationTestRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationTestRun]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidationTestRun]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                validation_test_run_name: str, 
                **kwargs: Any
            ) -> ValidationTestRun: ...

        @distributed_trace
        def list_by_execution_plan_run(
                self, 
                resource_group_name: str, 
                cloud_validation_name: str, 
                validation_execution_plan_name: str, 
                execution_plan_run_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ValidationTestRun]: ...


    class azure.mgmt.platformvalidation.operations.ValidationTestVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                validation_test_name: str, 
                version: str, 
                **kwargs: Any
            ) -> ValidationTestVersion: ...

        @distributed_trace
        def list(
                self, 
                validation_test_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ValidationTestVersion]: ...


    class azure.mgmt.platformvalidation.operations.ValidationTestsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                validation_test_name: str, 
                **kwargs: Any
            ) -> ValidationTest: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ValidationTest]: ...


namespace azure.mgmt.platformvalidation.types

    class azure.mgmt.platformvalidation.types.CloudValidation(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        properties: ForwardRef('CloudValidationProperties', module='types')
        systemData: ForwardRef('SystemData', module='types')
        tags: dict[str, str]
        type: str


    class azure.mgmt.platformvalidation.types.CloudValidationProperties(TypedDict, total=False):
        key "description": str
        key "overallState": Union[str, CloudValidationOverallState]
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        error: ForwardRef('ErrorDetail', module='types')
        managedOnBehalfOfConfiguration: ForwardRef('ManagedOnBehalfOfConfiguration', module='types')
        overallState: Union[str, CloudValidationOverallState]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.platformvalidation.types.CloudValidationUpdate(TypedDict, total=False):
        properties: ForwardRef('CloudValidationUpdateProperties', module='types')
        tags: dict[str, str]


    class azure.mgmt.platformvalidation.types.CloudValidationUpdateProperties(TypedDict, total=False):
        key "description": str
        key "overallState": Union[str, CloudValidationOverallState]
        description: str
        overallState: Union[str, CloudValidationOverallState]


    class azure.mgmt.platformvalidation.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.platformvalidation.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.platformvalidation.types.ExecutionPlanRun(ProxyResource):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        properties: ForwardRef('ExecutionPlanRunProperties', module='types')
        systemData: ForwardRef('SystemData', module='types')
        type: str


    class azure.mgmt.platformvalidation.types.ExecutionPlanRunProperties(TypedDict, total=False):
        key "completedAt": str
        key "description": str
        key "planConfigurationSnapshot": str
        key "provisioningState": Union[str, ExecutionPlanRunProvisioningState]
        key "reportedAt": str
        key "startedAt": str
        key "status": Union[str, ExecutionPlanRunStatus]
        completedAt: str
        description: str
        error: ForwardRef('ErrorDetail', module='types')
        planConfigurationSnapshot: str
        provisioningState: Union[str, ExecutionPlanRunProvisioningState]
        reportedAt: str
        startedAt: str
        status: Union[str, ExecutionPlanRunStatus]
        testRunIds: list[str]
        testRunSummary: ForwardRef('TestRunSummary', module='types')


    class azure.mgmt.platformvalidation.types.ManagedOnBehalfOfConfiguration(TypedDict, total=False):
        moboBrokerResources: list[MoboBrokerResource]


    class azure.mgmt.platformvalidation.types.MoboBrokerResource(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.platformvalidation.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        systemData: ForwardRef('SystemData', module='types')
        type: str


    class azure.mgmt.platformvalidation.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        systemData: ForwardRef('SystemData', module='types')
        type: str


    class azure.mgmt.platformvalidation.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.platformvalidation.types.TestRunSummary(TypedDict, total=False):
        key "failedTests": int
        key "message": str
        key "overallResult": Union[str, TestRunOverallResult]
        key "passedTests": int
        key "skippedTests": int
        key "totalTests": int
        failedTests: int
        message: str
        overallResult: Union[str, TestRunOverallResult]
        passedTests: int
        skippedTests: int
        totalTests: int


    class azure.mgmt.platformvalidation.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        systemData: ForwardRef('SystemData', module='types')
        tags: dict[str, str]
        type: str


    class azure.mgmt.platformvalidation.types.ValidationExecutionPlan(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "type": str
        id: str
        location: str
        name: str
        properties: ForwardRef('ValidationExecutionPlanProperties', module='types')
        systemData: ForwardRef('SystemData', module='types')
        tags: dict[str, str]
        type: str


    class azure.mgmt.platformvalidation.types.ValidationExecutionPlanProperties(TypedDict, total=False):
        key "description": str
        key "overallState": Union[str, ValidationExecutionPlanOverallState]
        key "planConfigurationJson": str
        key "planConfigurationUri": str
        key "provisioningState": Union[str, ValidationExecutionPlanProvisioningState]
        description: str
        error: ForwardRef('ErrorDetail', module='types')
        overallState: Union[str, ValidationExecutionPlanOverallState]
        planConfigurationJson: str
        planConfigurationUri: str
        provisioningState: Union[str, ValidationExecutionPlanProvisioningState]


    class azure.mgmt.platformvalidation.types.ValidationExecutionPlanUpdate(TypedDict, total=False):
        properties: ForwardRef('ValidationExecutionPlanUpdateProperties', module='types')
        tags: dict[str, str]


    class azure.mgmt.platformvalidation.types.ValidationExecutionPlanUpdateProperties(TypedDict, total=False):
        key "description": str
        key "overallState": Union[str, ValidationExecutionPlanOverallState]
        key "planConfigurationJson": str
        key "planConfigurationUri": str
        description: str
        overallState: Union[str, ValidationExecutionPlanOverallState]
        planConfigurationJson: str
        planConfigurationUri: str


    class azure.mgmt.platformvalidation.types.ValidationTestFailureDetails(TypedDict, total=False):
        key "details": str
        key "diagnosticInfo": str
        key "errorCode": str
        key "errorMessage": str
        details: str
        diagnosticInfo: str
        errorCode: str
        errorMessage: str
        recommendedActions: list[str]


    class azure.mgmt.platformvalidation.types.ValidationTestPassDetails(TypedDict, total=False):
        key "resultCode": str
        key "resultDetails": str
        key "testName": str
        resultCode: str
        resultDetails: str
        testName: str


    class azure.mgmt.platformvalidation.types.ValidationTestRun(ProxyResource):
        key "id": str
        key "name": str
        key "type": str
        id: str
        name: str
        properties: ForwardRef('ValidationTestRunProperties', module='types')
        systemData: ForwardRef('SystemData', module='types')
        type: str


    class azure.mgmt.platformvalidation.types.ValidationTestRunProperties(TypedDict, total=False):
        key "completedAt": str
        key "inputsJson": str
        key "provisioningState": Union[str, ValidationTestRunProvisioningState]
        key "reportedAt": str
        key "startedAt": str
        key "status": Union[str, ValidationTestRunStatus]
        key "testId": str
        completedAt: str
        error: ForwardRef('ErrorDetail', module='types')
        failureDetails: list[ValidationTestFailureDetails]
        inputsJson: str
        passDetails: list[ValidationTestPassDetails]
        provisioningState: Union[str, ValidationTestRunProvisioningState]
        reportedAt: str
        startedAt: str
        status: Union[str, ValidationTestRunStatus]
        testCategoryIds: list[str]
        testId: str


```