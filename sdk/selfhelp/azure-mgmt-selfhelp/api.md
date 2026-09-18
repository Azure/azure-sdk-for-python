```py
namespace azure.mgmt.selfhelp

    class azure.mgmt.selfhelp.SelfHelpMgmtClient: implements ContextManager 
        check_name_availability: CheckNameAvailabilityOperations
        diagnostics: DiagnosticsOperations
        discovery_solution: DiscoverySolutionOperations
        discovery_solution_nlp: DiscoverySolutionNLPOperations
        operations: Operations
        simplified_solutions: SimplifiedSolutionsOperations
        solution: SolutionOperations
        solution_self_help: SolutionSelfHelpOperations
        troubleshooters: TroubleshootersOperations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.selfhelp.aio

    class azure.mgmt.selfhelp.aio.SelfHelpMgmtClient: implements AsyncContextManager 
        check_name_availability: CheckNameAvailabilityOperations
        diagnostics: DiagnosticsOperations
        discovery_solution: DiscoverySolutionOperations
        discovery_solution_nlp: DiscoverySolutionNLPOperations
        operations: Operations
        simplified_solutions: SimplifiedSolutionsOperations
        solution: SolutionOperations
        solution_self_help: SolutionSelfHelpOperations
        troubleshooters: TroubleshootersOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.selfhelp.aio.operations

    class azure.mgmt.selfhelp.aio.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[CheckNameAvailabilityRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[CheckNameAvailabilityRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.selfhelp.aio.operations.DiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[DiagnosticResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[DiagnosticResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiagnosticResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                **kwargs: Any
            ) -> DiagnosticResource: ...


    class azure.mgmt.selfhelp.aio.operations.DiscoverySolutionNLPOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def discover_solutions(
                self, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        async def discover_solutions(
                self, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        async def discover_solutions(
                self, 
                discover_solution_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        async def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        async def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        async def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...


    class azure.mgmt.selfhelp.aio.operations.DiscoverySolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SolutionMetadataResource]: ...


    class azure.mgmt.selfhelp.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.selfhelp.aio.operations.SimplifiedSolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[SimplifiedSolutionsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SimplifiedSolutionsResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[SimplifiedSolutionsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SimplifiedSolutionsResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SimplifiedSolutionsResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                **kwargs: Any
            ) -> SimplifiedSolutionsResource: ...


    class azure.mgmt.selfhelp.aio.operations.SolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[SolutionResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[SolutionResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @overload
        async def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[SolutionPatchRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[SolutionPatchRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @overload
        async def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SolutionResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                solution_resource_name: str, 
                **kwargs: Any
            ) -> SolutionResource: ...

        @overload
        async def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[SolutionWarmUpRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[SolutionWarmUpRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.aio.operations.SolutionSelfHelpOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                solution_id: str, 
                **kwargs: Any
            ) -> SolutionResourceSelfHelp: ...


    class azure.mgmt.selfhelp.aio.operations.TroubleshootersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[ContinueRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[ContinueRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[TroubleshooterResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @overload
        async def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[TroubleshooterResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @overload
        async def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @distributed_trace_async
        async def end(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @distributed_trace_async
        async def restart(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> RestartTroubleshooterResponse: ...


namespace azure.mgmt.selfhelp.models

    class azure.mgmt.selfhelp.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.selfhelp.models.AggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVG = "Avg"
        COUNT = "Count"
        MAX = "Max"
        MIN = "Min"
        SUM = "Sum"


    class azure.mgmt.selfhelp.models.AutomatedCheckResult(_Model):
        result: Optional[str]
        status: Optional[str]
        type: Optional[Union[str, AutomatedCheckResultType]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                result: Optional[str] = ..., 
                status: Optional[str] = ..., 
                type: Optional[Union[str, AutomatedCheckResultType]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.AutomatedCheckResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        SUCCESS = "Success"
        WARNING = "Warning"


    class azure.mgmt.selfhelp.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.ClassificationService(_Model):
        display_name: Optional[str]
        resource_types: Optional[list[str]]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Confidence(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.selfhelp.models.ContinueRequestBody(_Model):
        responses: Optional[list[TroubleshooterResponse]]
        step_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                responses: Optional[list[TroubleshooterResponse]] = ..., 
                step_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.selfhelp.models.Diagnostic(_Model):
        error: Optional[Error]
        insights: Optional[list[Insight]]
        solution_id: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[Error] = ..., 
                insights: Optional[list[Insight]] = ..., 
                solution_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.DiagnosticInvocation(_Model):
        additional_parameters: Optional[dict[str, str]]
        solution_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_parameters: Optional[dict[str, str]] = ..., 
                solution_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.DiagnosticProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PARTIAL_COMPLETE = "PartialComplete"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.selfhelp.models.DiagnosticResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[DiagnosticResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiagnosticResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.DiagnosticResourceProperties(_Model):
        accepted_at: Optional[str]
        diagnostics: Optional[list[Diagnostic]]
        global_parameters: Optional[dict[str, str]]
        insights: Optional[list[DiagnosticInvocation]]
        provisioning_state: Optional[Union[str, DiagnosticProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                global_parameters: Optional[dict[str, str]] = ..., 
                insights: Optional[list[DiagnosticInvocation]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.DiscoveryNlpRequest(_Model):
        additional_context: Optional[str]
        issue_summary: str
        resource_id: Optional[str]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_context: Optional[str] = ..., 
                issue_summary: str, 
                resource_id: Optional[str] = ..., 
                service_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.DiscoveryNlpResponse(_Model):
        value: Optional[list[SolutionNlpMetadataResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SolutionNlpMetadataResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Error(_Model):
        code: Optional[str]
        details: Optional[list[Error]]
        message: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[Error]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.selfhelp.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.selfhelp.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.ExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCESS = "Success"
        WARNING = "Warning"


    class azure.mgmt.selfhelp.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.models.Filter(_Model):
        name: Optional[str]
        operator: Optional[str]
        values_property: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                operator: Optional[str] = ..., 
                values_property: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.FilterGroup(_Model):
        filter: Optional[list[Filter]]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[list[Filter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.ImportanceLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        INFORMATION = "Information"
        WARNING = "Warning"


    class azure.mgmt.selfhelp.models.Insight(_Model):
        id: Optional[str]
        importance_level: Optional[Union[str, ImportanceLevel]]
        results: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                importance_level: Optional[Union[str, ImportanceLevel]] = ..., 
                results: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.MetricsBasedChart(_Model):
        aggregation_type: Optional[Union[str, AggregationType]]
        filter_group: Optional[FilterGroup]
        name: Optional[str]
        replacement_key: Optional[str]
        time_span_duration: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[Union[str, AggregationType]] = ..., 
                filter_group: Optional[FilterGroup] = ..., 
                name: Optional[str] = ..., 
                replacement_key: Optional[str] = ..., 
                time_span_duration: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Name(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROBLEM_CLASSIFICATION_ID = "ProblemClassificationId"
        REPLACEMENT_KEY = "ReplacementKey"
        SOLUTION_ID = "SolutionId"


    class azure.mgmt.selfhelp.models.NlpSolutions(_Model):
        problem_classification_id: Optional[str]
        problem_description: Optional[str]
        problem_title: Optional[str]
        related_services: Optional[list[ClassificationService]]
        service_id: Optional[str]
        solutions: Optional[list[SolutionMetadataProperties]]

        @overload
        def __init__(
                self, 
                *, 
                problem_classification_id: Optional[str] = ..., 
                problem_description: Optional[str] = ..., 
                problem_title: Optional[str] = ..., 
                related_services: Optional[list[ClassificationService]] = ..., 
                service_id: Optional[str] = ..., 
                solutions: Optional[list[SolutionMetadataProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Operation(_Model):
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


    class azure.mgmt.selfhelp.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.selfhelp.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.selfhelp.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.models.QuestionContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML = "Html"
        MARKDOWN = "Markdown"
        TEXT = "Text"


    class azure.mgmt.selfhelp.models.QuestionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATE_TIME_PICKER = "DateTimePicker"
        DROPDOWN = "Dropdown"
        MULTI_LINE_INFO_BOX = "MultiLineInfoBox"
        MULTI_SELECT = "MultiSelect"
        RADIO_BUTTON = "RadioButton"
        TEXT_INPUT = "TextInput"


    class azure.mgmt.selfhelp.models.ReplacementMaps(_Model):
        diagnostics: Optional[list[SolutionsDiagnostic]]
        metrics_based_charts: Optional[list[MetricsBasedChart]]
        troubleshooters: Optional[list[SolutionsTroubleshooters]]
        video_groups: Optional[list[VideoGroup]]
        videos: Optional[list[Video]]
        web_results: Optional[list[WebResult]]

        @overload
        def __init__(
                self, 
                *, 
                diagnostics: Optional[list[SolutionsDiagnostic]] = ..., 
                metrics_based_charts: Optional[list[MetricsBasedChart]] = ..., 
                troubleshooters: Optional[list[SolutionsTroubleshooters]] = ..., 
                video_groups: Optional[list[VideoGroup]] = ..., 
                videos: Optional[list[Video]] = ..., 
                web_results: Optional[list[WebResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.ReplacementMapsSelfHelp(_Model):
        video_groups: Optional[list[VideoGroup]]
        videos: Optional[list[Video]]
        web_results: Optional[list[WebResult]]

        @overload
        def __init__(
                self, 
                *, 
                video_groups: Optional[list[VideoGroup]] = ..., 
                videos: Optional[list[Video]] = ..., 
                web_results: Optional[list[WebResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.selfhelp.models.ResponseOption(_Model):
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


    class azure.mgmt.selfhelp.models.ResponseValidationProperties(_Model):
        is_required: Optional[bool]
        max_length: Optional[int]
        regex: Optional[str]
        validation_error_message: Optional[str]
        validation_scope: Optional[Union[str, ValidationScope]]

        @overload
        def __init__(
                self, 
                *, 
                is_required: Optional[bool] = ..., 
                max_length: Optional[int] = ..., 
                regex: Optional[str] = ..., 
                validation_error_message: Optional[str] = ..., 
                validation_scope: Optional[Union[str, ValidationScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.RestartTroubleshooterResponse(_Model):
        troubleshooter_resource_name: Optional[str]


    class azure.mgmt.selfhelp.models.ResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        DOCUMENTATION = "Documentation"


    class azure.mgmt.selfhelp.models.SearchResult(_Model):
        confidence: Optional[Union[str, Confidence]]
        content: Optional[str]
        link: Optional[str]
        rank: Optional[int]
        result_type: Optional[Union[str, ResultType]]
        solution_id: Optional[str]
        source: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[Union[str, Confidence]] = ..., 
                content: Optional[str] = ..., 
                link: Optional[str] = ..., 
                rank: Optional[int] = ..., 
                result_type: Optional[Union[str, ResultType]] = ..., 
                solution_id: Optional[str] = ..., 
                source: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Section(_Model):
        content: Optional[str]
        replacement_maps: Optional[ReplacementMaps]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                replacement_maps: Optional[ReplacementMaps] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SectionSelfHelp(_Model):
        content: Optional[str]
        replacement_maps: Optional[ReplacementMapsSelfHelp]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                replacement_maps: Optional[ReplacementMapsSelfHelp] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SimplifiedSolutionsResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[SimplifiedSolutionsResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SimplifiedSolutionsResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SimplifiedSolutionsResourceProperties(_Model):
        appendix: Optional[dict[str, str]]
        content: Optional[str]
        parameters: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, SolutionProvisioningState]]
        solution_id: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                solution_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionMetadataProperties(_Model):
        description: Optional[str]
        required_inputs: Optional[list[str]]
        solution_id: Optional[str]
        solution_type: Optional[Union[str, SolutionType]]

        @overload
        def __init__(
                self, 
                *, 
                solution_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionMetadataResource(ProxyResource):
        id: str
        name: str
        properties: Optional[Solutions]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Solutions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionNlpMetadataResource(ProxyResource):
        id: str
        name: str
        properties: Optional[NlpSolutions]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NlpSolutions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionPatchRequestBody(_Model):
        properties: Optional[SolutionResourceProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PARTIAL_COMPLETE = "PartialComplete"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.selfhelp.models.SolutionResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[SolutionResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionResourceProperties(_Model):
        content: Optional[str]
        parameters: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, SolutionProvisioningState]]
        replacement_maps: Optional[ReplacementMaps]
        sections: Optional[list[Section]]
        solution_id: Optional[str]
        title: Optional[str]
        trigger_criteria: Optional[list[TriggerCriterion]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                trigger_criteria: Optional[list[TriggerCriterion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionResourceSelfHelp(ProxyResource):
        id: str
        name: str
        properties: Optional[SolutionsResourcePropertiesSelfHelp]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SolutionsResourcePropertiesSelfHelp] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIAGNOSTICS = "Diagnostics"
        SELF_HELP = "SelfHelp"
        SOLUTIONS = "Solutions"
        TROUBLESHOOTERS = "Troubleshooters"


    class azure.mgmt.selfhelp.models.SolutionWarmUpRequestBody(_Model):
        parameters: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Solutions(_Model):
        solutions: Optional[list[SolutionMetadataProperties]]

        @overload
        def __init__(
                self, 
                *, 
                solutions: Optional[list[SolutionMetadataProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionsDiagnostic(_Model):
        estimated_completion_time: Optional[str]
        insights: Optional[list[Insight]]
        replacement_key: Optional[str]
        required_parameters: Optional[list[str]]
        solution_id: Optional[str]
        status: Optional[Union[str, Status]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                estimated_completion_time: Optional[str] = ..., 
                insights: Optional[list[Insight]] = ..., 
                replacement_key: Optional[str] = ..., 
                required_parameters: Optional[list[str]] = ..., 
                solution_id: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SolutionsResourcePropertiesSelfHelp(_Model):
        content: Optional[str]
        replacement_maps: Optional[ReplacementMapsSelfHelp]
        sections: Optional[list[SectionSelfHelp]]
        solution_id: Optional[str]
        title: Optional[str]


    class azure.mgmt.selfhelp.models.SolutionsTroubleshooters(_Model):
        solution_id: Optional[str]
        summary: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                solution_id: Optional[str] = ..., 
                summary: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        MISSING_INPUTS = "MissingInputs"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMEOUT = "Timeout"


    class azure.mgmt.selfhelp.models.Step(_Model):
        automated_check_results: Optional[AutomatedCheckResult]
        description: Optional[str]
        error: Optional[ErrorDetail]
        execution_status: Optional[Union[str, ExecutionStatus]]
        execution_status_description: Optional[str]
        guidance: Optional[str]
        id: Optional[str]
        inputs: Optional[list[StepInput]]
        insights: Optional[list[Insight]]
        is_last_step: Optional[bool]
        title: Optional[str]
        type: Optional[Union[str, Type]]

        @overload
        def __init__(
                self, 
                *, 
                automated_check_results: Optional[AutomatedCheckResult] = ..., 
                description: Optional[str] = ..., 
                error: Optional[ErrorDetail] = ..., 
                execution_status: Optional[Union[str, ExecutionStatus]] = ..., 
                execution_status_description: Optional[str] = ..., 
                guidance: Optional[str] = ..., 
                id: Optional[str] = ..., 
                inputs: Optional[list[StepInput]] = ..., 
                insights: Optional[list[Insight]] = ..., 
                is_last_step: Optional[bool] = ..., 
                title: Optional[str] = ..., 
                type: Optional[Union[str, Type]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.StepInput(_Model):
        question_content: Optional[str]
        question_content_type: Optional[Union[str, QuestionContentType]]
        question_id: Optional[str]
        question_title: Optional[str]
        question_type: Optional[Union[str, QuestionType]]
        recommended_option: Optional[str]
        response_hint: Optional[str]
        response_options: Optional[list[ResponseOption]]
        response_validation_properties: Optional[ResponseValidationProperties]
        selected_option_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                question_content: Optional[str] = ..., 
                question_content_type: Optional[Union[str, QuestionContentType]] = ..., 
                question_id: Optional[str] = ..., 
                question_title: Optional[str] = ..., 
                question_type: Optional[Union[str, QuestionType]] = ..., 
                recommended_option: Optional[str] = ..., 
                response_hint: Optional[str] = ..., 
                response_options: Optional[list[ResponseOption]] = ..., 
                response_validation_properties: Optional[ResponseValidationProperties] = ..., 
                selected_option_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.SystemData(_Model):
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


    class azure.mgmt.selfhelp.models.TriggerCriterion(_Model):
        name: Optional[Union[str, Name]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, Name]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.TroubleshooterInstanceProperties(_Model):
        parameters: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, TroubleshooterProvisioningState]]
        solution_id: Optional[str]
        steps: Optional[list[Step]]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[dict[str, str]] = ..., 
                solution_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.TroubleshooterProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_CONTINUE = "AutoContinue"
        CANCELED = "Canceled"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.selfhelp.models.TroubleshooterResource(ExtensionResource):
        id: str
        name: str
        properties: Optional[TroubleshooterInstanceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TroubleshooterInstanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.models.TroubleshooterResponse(_Model):
        question_id: Optional[str]
        question_type: Optional[Union[str, QuestionType]]
        response: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                question_id: Optional[str] = ..., 
                question_type: Optional[Union[str, QuestionType]] = ..., 
                response: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATED_CHECK = "AutomatedCheck"
        DECISION = "Decision"
        INPUT = "Input"
        INSIGHT = "Insight"
        SOLUTION = "Solution"


    class azure.mgmt.selfhelp.models.ValidationScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GUID_FORMAT = "GuidFormat"
        IP_ADDRESS_FORMAT = "IpAddressFormat"
        NONE = "None"
        NUMBER_ONLY_FORMAT = "NumberOnlyFormat"
        URL_FORMAT = "URLFormat"


    class azure.mgmt.selfhelp.models.Video(VideoGroupVideo):
        replacement_key: Optional[str]
        src: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                replacement_key: Optional[str] = ..., 
                src: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.VideoGroup(_Model):
        replacement_key: Optional[str]
        videos: Optional[list[VideoGroupVideo]]

        @overload
        def __init__(
                self, 
                *, 
                replacement_key: Optional[str] = ..., 
                videos: Optional[list[VideoGroupVideo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.VideoGroupVideo(_Model):
        src: Optional[str]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                src: Optional[str] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.selfhelp.models.WebResult(_Model):
        replacement_key: Optional[str]
        search_results: Optional[list[SearchResult]]

        @overload
        def __init__(
                self, 
                *, 
                replacement_key: Optional[str] = ..., 
                search_results: Optional[list[SearchResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.selfhelp.operations

    class azure.mgmt.selfhelp.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[CheckNameAvailabilityRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[CheckNameAvailabilityRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_availability(
                self, 
                scope: str, 
                check_name_availability_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.selfhelp.operations.DiagnosticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[DiagnosticResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[DiagnosticResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                diagnostic_resource_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiagnosticResource]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                diagnostics_resource_name: str, 
                **kwargs: Any
            ) -> DiagnosticResource: ...


    class azure.mgmt.selfhelp.operations.DiscoverySolutionNLPOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def discover_solutions(
                self, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        def discover_solutions(
                self, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        def discover_solutions(
                self, 
                discover_solution_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[DiscoveryNlpRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...

        @overload
        def discover_solutions_by_subscription(
                self, 
                subscription_id: str, 
                discover_solution_request: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DiscoveryNlpResponse: ...


    class azure.mgmt.selfhelp.operations.DiscoverySolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SolutionMetadataResource]: ...


    class azure.mgmt.selfhelp.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.selfhelp.operations.SimplifiedSolutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[SimplifiedSolutionsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SimplifiedSolutionsResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[SimplifiedSolutionsResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SimplifiedSolutionsResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                simplified_solutions_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SimplifiedSolutionsResource]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                simplified_solutions_resource_name: str, 
                **kwargs: Any
            ) -> SimplifiedSolutionsResource: ...


    class azure.mgmt.selfhelp.operations.SolutionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[SolutionResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[SolutionResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @overload
        def begin_create(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[SolutionPatchRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[SolutionPatchRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @overload
        def begin_update(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_patch_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SolutionResource]: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                solution_resource_name: str, 
                **kwargs: Any
            ) -> SolutionResource: ...

        @overload
        def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[SolutionWarmUpRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[SolutionWarmUpRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def warm_up(
                self, 
                scope: str, 
                solution_resource_name: str, 
                solution_warm_up_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.selfhelp.operations.SolutionSelfHelpOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                solution_id: str, 
                **kwargs: Any
            ) -> SolutionResourceSelfHelp: ...


    class azure.mgmt.selfhelp.operations.TroubleshootersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[ContinueRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[ContinueRequestBody] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def continue_method(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                continue_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[TroubleshooterResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @overload
        def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[TroubleshooterResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @overload
        def create(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                create_troubleshooter_request_body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @distributed_trace
        def end(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> TroubleshooterResource: ...

        @distributed_trace
        def restart(
                self, 
                scope: str, 
                troubleshooter_name: str, 
                **kwargs: Any
            ) -> RestartTroubleshooterResponse: ...


namespace azure.mgmt.selfhelp.types

    class azure.mgmt.selfhelp.types.AutomatedCheckResult(TypedDict, total=False):
        key "result": str
        key "status": str
        key "type": Union[str, AutomatedCheckResultType]
        key "version": str
        result: str
        status: str
        type: Union[str, AutomatedCheckResultType]
        version: str


    class azure.mgmt.selfhelp.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.selfhelp.types.CheckNameAvailabilityResponse(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.selfhelp.types.ClassificationService(TypedDict, total=False):
        key "displayName": str
        key "serviceId": str
        display_name: str
        resourceTypes: list[str]
        resource_types: list[str]
        service_id: str


    class azure.mgmt.selfhelp.types.ContinueRequestBody(TypedDict, total=False):
        key "stepId": str
        responses: list[TroubleshooterResponse]
        step_id: str


    class azure.mgmt.selfhelp.types.Diagnostic(TypedDict, total=False):
        key "error": ForwardRef('Error', module='types')
        key "solutionId": str
        key "status": Union[str, Status]
        error: Error
        insights: list[Insight]
        solution_id: str
        status: Union[str, Status]


    class azure.mgmt.selfhelp.types.DiagnosticInvocation(TypedDict, total=False):
        key "solutionId": str
        additionalParameters: dict[str, str]
        additional_parameters: dict[str, str]
        solution_id: str


    class azure.mgmt.selfhelp.types.DiagnosticResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DiagnosticResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DiagnosticResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.DiagnosticResourceProperties(TypedDict, total=False):
        key "acceptedAt": str
        key "provisioningState": Union[str, DiagnosticProvisioningState]
        accepted_at: str
        diagnostics: list[Diagnostic]
        globalParameters: dict[str, str]
        global_parameters: dict[str, str]
        insights: list[DiagnosticInvocation]
        provisioning_state: Union[str, DiagnosticProvisioningState]


    class azure.mgmt.selfhelp.types.DiscoveryNlpRequest(TypedDict, total=False):
        key "additionalContext": str
        key "issueSummary": Required[str]
        key "resourceId": str
        key "serviceId": str
        additional_context: str
        issue_summary: str
        resource_id: str
        service_id: str


    class azure.mgmt.selfhelp.types.DiscoveryNlpResponse(TypedDict, total=False):
        value: list[SolutionNlpMetadataResource]


    class azure.mgmt.selfhelp.types.Error(TypedDict, total=False):
        key "code": str
        key "message": str
        key "type": str
        code: str
        details: list[Error]
        message: str
        type: str


    class azure.mgmt.selfhelp.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.selfhelp.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.selfhelp.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.selfhelp.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.Filter(TypedDict, total=False):
        key "name": str
        key "operator": str
        key "values": str
        name: str
        operator: str
        values_property: str


    class azure.mgmt.selfhelp.types.FilterGroup(TypedDict, total=False):
        filter: list[Filter]


    class azure.mgmt.selfhelp.types.Insight(TypedDict, total=False):
        key "id": str
        key "importanceLevel": Union[str, ImportanceLevel]
        key "results": str
        key "title": str
        id: str
        importance_level: Union[str, ImportanceLevel]
        results: str
        title: str


    class azure.mgmt.selfhelp.types.MetricsBasedChart(TypedDict, total=False):
        key "aggregationType": Union[str, AggregationType]
        key "filterGroup": ForwardRef('FilterGroup', module='types')
        key "name": str
        key "replacementKey": str
        key "timeSpanDuration": str
        key "title": str
        aggregation_type: Union[str, AggregationType]
        filter_group: FilterGroup
        name: str
        replacement_key: str
        time_span_duration: str
        title: str


    class azure.mgmt.selfhelp.types.NlpSolutions(TypedDict, total=False):
        key "problemClassificationId": str
        key "problemDescription": str
        key "problemTitle": str
        key "serviceId": str
        problem_classification_id: str
        problem_description: str
        problem_title: str
        relatedServices: list[ClassificationService]
        related_services: list[ClassificationService]
        service_id: str
        solutions: list[SolutionMetadataProperties]


    class azure.mgmt.selfhelp.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.selfhelp.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.selfhelp.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.ReplacementMaps(TypedDict, total=False):
        diagnostics: list[SolutionsDiagnostic]
        metricsBasedCharts: list[MetricsBasedChart]
        metrics_based_charts: list[MetricsBasedChart]
        troubleshooters: list[SolutionsTroubleshooters]
        videoGroups: list[VideoGroup]
        video_groups: list[VideoGroup]
        videos: list[Video]
        webResults: list[WebResult]
        web_results: list[WebResult]


    class azure.mgmt.selfhelp.types.ReplacementMapsSelfHelp(TypedDict, total=False):
        videoGroups: list[VideoGroup]
        video_groups: list[VideoGroup]
        videos: list[Video]
        webResults: list[WebResult]
        web_results: list[WebResult]


    class azure.mgmt.selfhelp.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.ResponseOption(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.selfhelp.types.ResponseValidationProperties(TypedDict, total=False):
        key "isRequired": bool
        key "maxLength": int
        key "regex": str
        key "validationErrorMessage": str
        key "validationScope": Union[str, ValidationScope]
        is_required: bool
        max_length: int
        regex: str
        validation_error_message: str
        validation_scope: Union[str, ValidationScope]


    class azure.mgmt.selfhelp.types.RestartTroubleshooterResponse(TypedDict, total=False):
        key "troubleshooterResourceName": str
        troubleshooter_resource_name: str


    class azure.mgmt.selfhelp.types.SearchResult(TypedDict, total=False):
        key "confidence": Union[str, Confidence]
        key "content": str
        key "link": str
        key "rank": int
        key "resultType": Union[str, ResultType]
        key "solutionId": str
        key "source": str
        key "title": str
        confidence: Union[str, Confidence]
        content: str
        link: str
        rank: int
        result_type: Union[str, ResultType]
        solution_id: str
        source: str
        title: str


    class azure.mgmt.selfhelp.types.Section(TypedDict, total=False):
        key "content": str
        key "replacementMaps": ForwardRef('ReplacementMaps', module='types')
        key "title": str
        content: str
        replacement_maps: ReplacementMaps
        title: str


    class azure.mgmt.selfhelp.types.SectionSelfHelp(TypedDict, total=False):
        key "content": str
        key "replacementMaps": ForwardRef('ReplacementMapsSelfHelp', module='types')
        key "title": str
        content: str
        replacement_maps: ReplacementMapsSelfHelp
        title: str


    class azure.mgmt.selfhelp.types.SimplifiedSolutionsResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SimplifiedSolutionsResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SimplifiedSolutionsResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.SimplifiedSolutionsResourceProperties(TypedDict, total=False):
        key "content": str
        key "provisioningState": Union[str, SolutionProvisioningState]
        key "solutionId": str
        key "title": str
        appendix: dict[str, str]
        content: str
        parameters: dict[str, str]
        provisioning_state: Union[str, SolutionProvisioningState]
        solution_id: str
        title: str


    class azure.mgmt.selfhelp.types.SolutionMetadataProperties(TypedDict, total=False):
        key "description": str
        key "solutionId": str
        key "solutionType": Union[str, SolutionType]
        description: str
        requiredInputs: list[str]
        required_inputs: list[str]
        solution_id: str
        solution_type: Union[str, SolutionType]


    class azure.mgmt.selfhelp.types.SolutionMetadataResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('Solutions', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: Solutions
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.SolutionNlpMetadataResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NlpSolutions', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NlpSolutions
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.SolutionPatchRequestBody(TypedDict, total=False):
        key "properties": ForwardRef('SolutionResourceProperties', module='types')
        properties: SolutionResourceProperties


    class azure.mgmt.selfhelp.types.SolutionResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SolutionResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.SolutionResourceProperties(TypedDict, total=False):
        key "content": str
        key "provisioningState": Union[str, SolutionProvisioningState]
        key "replacementMaps": ForwardRef('ReplacementMaps', module='types')
        key "solutionId": str
        key "title": str
        content: str
        parameters: dict[str, str]
        provisioning_state: Union[str, SolutionProvisioningState]
        replacement_maps: ReplacementMaps
        sections: list[Section]
        solution_id: str
        title: str
        triggerCriteria: list[TriggerCriterion]
        trigger_criteria: list[TriggerCriterion]


    class azure.mgmt.selfhelp.types.SolutionResourceSelfHelp(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SolutionsResourcePropertiesSelfHelp', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SolutionsResourcePropertiesSelfHelp
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.SolutionWarmUpRequestBody(TypedDict, total=False):
        parameters: dict[str, str]


    class azure.mgmt.selfhelp.types.Solutions(TypedDict, total=False):
        solutions: list[SolutionMetadataProperties]


    class azure.mgmt.selfhelp.types.SolutionsDiagnostic(TypedDict, total=False):
        key "estimatedCompletionTime": str
        key "replacementKey": str
        key "solutionId": str
        key "status": Union[str, Status]
        key "statusDetails": str
        estimated_completion_time: str
        insights: list[Insight]
        replacement_key: str
        requiredParameters: list[str]
        required_parameters: list[str]
        solution_id: str
        status: Union[str, Status]
        status_details: str


    class azure.mgmt.selfhelp.types.SolutionsResourcePropertiesSelfHelp(TypedDict, total=False):
        key "content": str
        key "replacementMaps": ForwardRef('ReplacementMapsSelfHelp', module='types')
        key "solutionId": str
        key "title": str
        content: str
        replacement_maps: ReplacementMapsSelfHelp
        sections: list[SectionSelfHelp]
        solution_id: str
        title: str


    class azure.mgmt.selfhelp.types.SolutionsTroubleshooters(TypedDict, total=False):
        key "solutionId": str
        key "summary": str
        key "title": str
        solution_id: str
        summary: str
        title: str


    class azure.mgmt.selfhelp.types.Step(TypedDict, total=False):
        key "automatedCheckResults": ForwardRef('AutomatedCheckResult', module='types')
        key "description": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "executionStatus": Union[str, ExecutionStatus]
        key "executionStatusDescription": str
        key "guidance": str
        key "id": str
        key "isLastStep": bool
        key "title": str
        key "type": Union[str, Type]
        automated_check_results: AutomatedCheckResult
        description: str
        error: ErrorDetail
        execution_status: Union[str, ExecutionStatus]
        execution_status_description: str
        guidance: str
        id: str
        inputs: list[StepInput]
        insights: list[Insight]
        is_last_step: bool
        title: str
        type: Union[str, Type]


    class azure.mgmt.selfhelp.types.StepInput(TypedDict, total=False):
        key "questionContent": str
        key "questionContentType": Union[str, QuestionContentType]
        key "questionId": str
        key "questionTitle": str
        key "questionType": Union[str, QuestionType]
        key "recommendedOption": str
        key "responseHint": str
        key "responseValidationProperties": ForwardRef('ResponseValidationProperties', module='types')
        key "selectedOptionValue": str
        question_content: str
        question_content_type: Union[str, QuestionContentType]
        question_id: str
        question_title: str
        question_type: Union[str, QuestionType]
        recommended_option: str
        responseOptions: list[ResponseOption]
        response_hint: str
        response_options: list[ResponseOption]
        response_validation_properties: ResponseValidationProperties
        selected_option_value: str


    class azure.mgmt.selfhelp.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.selfhelp.types.TriggerCriterion(TypedDict, total=False):
        key "name": Union[str, Name]
        key "value": str
        name: Union[str, Name]
        value: str


    class azure.mgmt.selfhelp.types.TroubleshooterInstanceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, TroubleshooterProvisioningState]
        key "solutionId": str
        parameters: dict[str, str]
        provisioning_state: Union[str, TroubleshooterProvisioningState]
        solution_id: str
        steps: list[Step]


    class azure.mgmt.selfhelp.types.TroubleshooterResource(ExtensionResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('TroubleshooterInstanceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: TroubleshooterInstanceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.selfhelp.types.TroubleshooterResponse(TypedDict, total=False):
        key "questionId": str
        key "questionType": Union[str, QuestionType]
        key "response": str
        question_id: str
        question_type: Union[str, QuestionType]
        response: str


    class azure.mgmt.selfhelp.types.Video(VideoGroupVideo):
        key "replacementKey": str
        key "src": str
        key "title": str
        replacement_key: str
        src: str
        title: str


    class azure.mgmt.selfhelp.types.VideoGroup(TypedDict, total=False):
        key "replacementKey": str
        replacement_key: str
        videos: list[VideoGroupVideo]


    class azure.mgmt.selfhelp.types.VideoGroupVideo(TypedDict, total=False):
        key "src": str
        key "title": str
        src: str
        title: str


    class azure.mgmt.selfhelp.types.WebResult(TypedDict, total=False):
        key "replacementKey": str
        replacement_key: str
        searchResults: list[SearchResult]
        search_results: list[SearchResult]


```