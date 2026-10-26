```py
namespace azure.mgmt.sovereign

    class azure.mgmt.sovereign.SovereignClient: implements ContextManager 
        operations: Operations
        sovereign_view_operations: SovereignViewOperationsOperations

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


namespace azure.mgmt.sovereign.aio

    class azure.mgmt.sovereign.aio.SovereignClient: implements AsyncContextManager 
        operations: Operations
        sovereign_view_operations: SovereignViewOperationsOperations

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


namespace azure.mgmt.sovereign.aio.operations

    class azure.mgmt.sovereign.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_local(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_local(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability_local(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.sovereign.aio.operations.SovereignViewOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: SovereignViewResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: SovereignViewResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewRemediateResult]: ...

        @overload
        async def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewRemediateResult]: ...

        @overload
        async def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewRemediateResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: SovereignViewResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: SovereignViewResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SovereignViewResource]: ...

        @overload
        async def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        async def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        async def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        async def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceResourceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @overload
        async def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceResourceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @overload
        async def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @distributed_trace_async
        async def compliance_summary(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> SovereignViewComplianceSummaryResult: ...

        @overload
        async def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewFilterValuesContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @overload
        async def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewFilterValuesContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @overload
        async def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> SovereignViewResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SovereignViewResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SovereignViewResource]: ...

        @overload
        async def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewOperationalStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        async def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewOperationalStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        async def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        async def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediationResultContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...

        @overload
        async def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediationResultContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...

        @overload
        async def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...


namespace azure.mgmt.sovereign.models

    class azure.mgmt.sovereign.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.sovereign.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.sovereign.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.sovereign.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.ComplianceDimension(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CONTINUITY = "BusinessContinuity"
        CONTROLLED_NETWORK_EXPOSURE = "ControlledNetworkExposure"
        DATA_RESIDENCY = "DataResidency"
        ENCRYPTION_AT_REST = "EncryptionAtRest"
        ENCRYPTION_IN_TRANSIT = "EncryptionInTransit"
        ENCRYPTION_IN_USE = "EncryptionInUse"


    class azure.mgmt.sovereign.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.sovereign.models.DataResidencyResourceEvaluationScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESIDENCY360 = "Residency360"
        RESOURCE_ONLY = "ResourceOnly"


    class azure.mgmt.sovereign.models.DataState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        PROCESSED = "Processed"
        PROCESSING = "Processing"


    class azure.mgmt.sovereign.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.sovereign.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.sovereign.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.Operation(_Model):
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


    class azure.mgmt.sovereign.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.sovereign.models.OperationalStatusEvaluationParameter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERMISSIONS_EVALUATION = "PermissionsEvaluation"
        POLICY_ASSIGNMENT_EVALUATION = "PolicyAssignmentEvaluation"


    class azure.mgmt.sovereign.models.OperationalStatusRequestMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETAILED = "Detailed"
        SUMMARY = "Summary"


    class azure.mgmt.sovereign.models.OperationalStatusStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.sovereign.models.OperationalStatusUnhealthyReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MI_MISSING = "MIMissing"
        MI_PERMISSION_MISSING = "MIPermissionMissing"
        POLICY_ASSIGNMENT_MISSING = "PolicyAssignmentMissing"


    class azure.mgmt.sovereign.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.sovereign.models.PolicyComplianceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        CONFLICT = "Conflict"
        CONSTRAINED = "Constrained"
        NON_COMPLIANT = "NonCompliant"
        NOT_APPLICABLE = "NotApplicable"
        NOT_EVALUATED = "NotEvaluated"
        OTHERS = "Others"


    class azure.mgmt.sovereign.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.sovereign.models.ReportState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        GENERATING = "Generating"
        NO_DATA_YET = "NoDataYet"
        REFRESHING = "Refreshing"
        RETRYING = "Retrying"
        STALE = "Stale"
        UP_TO_DATE = "UpToDate"


    class azure.mgmt.sovereign.models.ReportStatus(_Model):
        next_attempt: Optional[datetime]
        state: Union[str, ReportState]

        @overload
        def __init__(
                self, 
                *, 
                next_attempt: Optional[datetime] = ..., 
                state: Union[str, ReportState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.sovereign.models.ScopeLevelOperationalStatusStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.sovereign.models.SovereignViewAffectedScopes(_Model):
        action_required: Optional[str]
        id: str
        name: str
        status: Union[str, ScopeLevelOperationalStatusStates]
        type: Union[str, SovereignViewScopeType]

        @overload
        def __init__(
                self, 
                *, 
                action_required: Optional[str] = ..., 
                id: str, 
                name: str, 
                status: Union[str, ScopeLevelOperationalStatusStates], 
                type: Union[str, SovereignViewScopeType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewArmTemplateBundle(_Model):
        parameters: str
        template: str

        @overload
        def __init__(
                self, 
                *, 
                parameters: str, 
                template: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetail(_Model):
        evaluated_at: Optional[datetime]
        policy_assignment_id: str
        policy_initiative_id: str

        @overload
        def __init__(
                self, 
                *, 
                evaluated_at: Optional[datetime] = ..., 
                policy_assignment_id: str, 
                policy_initiative_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailResource(_Model):
        dimension_details: list[SovereignViewDimensionDetail]
        location: str
        parent_resource_id: Optional[str]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                dimension_details: list[SovereignViewDimensionDetail], 
                location: str, 
                parent_resource_id: Optional[str] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsContent(_Model):
        compliance_dimensions: Optional[list[SovereignViewComplianceDetailsDimensionFilter]]
        filters: Optional[list[SovereignViewComplianceDetailsFilters]]
        search: Optional[SovereignViewComplianceDetailsSearch]
        skip: Optional[int]
        sort: Optional[list[SovereignViewComplianceDetailsSort]]
        top: int

        @overload
        def __init__(
                self, 
                *, 
                compliance_dimensions: Optional[list[SovereignViewComplianceDetailsDimensionFilter]] = ..., 
                filters: Optional[list[SovereignViewComplianceDetailsFilters]] = ..., 
                search: Optional[SovereignViewComplianceDetailsSearch] = ..., 
                skip: Optional[int] = ..., 
                sort: Optional[list[SovereignViewComplianceDetailsSort]] = ..., 
                top: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsDimensionFilter(_Model):
        dimension: Union[str, ComplianceDimension]
        states: list[Union[str, PolicyComplianceState]]

        @overload
        def __init__(
                self, 
                *, 
                dimension: Union[str, ComplianceDimension], 
                states: list[Union[str, PolicyComplianceState]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsFilterOperators(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN = "In"


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsFilters(_Model):
        field: Union[str, SovereignViewFilterField]
        operator: Union[str, SovereignViewComplianceDetailsFilterOperators]
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                field: Union[str, SovereignViewFilterField], 
                operator: Union[str, SovereignViewComplianceDetailsFilterOperators], 
                value: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsResult(_Model):
        error: Optional[ErrorDetail]
        last_evaluated: datetime
        report_status: ReportStatus
        resources: Optional[list[SovereignViewComplianceDetailResource]]
        total_resources: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                last_evaluated: datetime, 
                report_status: ReportStatus, 
                resources: Optional[list[SovereignViewComplianceDetailResource]] = ..., 
                total_resources: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsSearch(_Model):
        field: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                field: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsSort(_Model):
        direction: Union[str, SovereignViewComplianceDetailsSortDirections]
        field: str
        sorting_order: Optional[list[Union[str, PolicyComplianceState]]]

        @overload
        def __init__(
                self, 
                *, 
                direction: Union[str, SovereignViewComplianceDetailsSortDirections], 
                field: str, 
                sorting_order: Optional[list[Union[str, PolicyComplianceState]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceDetailsSortDirections(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.mgmt.sovereign.models.SovereignViewComplianceDimensionSummary(_Model):
        compliant_count: int
        conflict_count: int
        constrained_count: int
        dimension: Union[str, ComplianceDimension]
        non_compliant_count: int
        not_applicable_count: int
        not_evaluated_count: int
        others_count: int
        total_resources: int

        @overload
        def __init__(
                self, 
                *, 
                compliant_count: int, 
                conflict_count: int, 
                constrained_count: int, 
                dimension: Union[str, ComplianceDimension], 
                non_compliant_count: int, 
                not_applicable_count: int, 
                not_evaluated_count: int, 
                others_count: int, 
                total_resources: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceOverallSummary(_Model):
        compliant_count: int
        conflict_count: int
        constrained_count: int
        non_compliant_count: int
        not_applicable_count: int
        not_evaluated_count: int
        others_count: int
        total_management_groups: int
        total_resource_groups: int
        total_resources: int
        total_subscriptions: int

        @overload
        def __init__(
                self, 
                *, 
                compliant_count: int, 
                conflict_count: int, 
                constrained_count: int, 
                non_compliant_count: int, 
                not_applicable_count: int, 
                not_evaluated_count: int, 
                others_count: int, 
                total_management_groups: int, 
                total_resource_groups: int, 
                total_resources: int, 
                total_subscriptions: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceResourceDetailsContent(_Model):
        dimension: Union[str, ComplianceDimension]
        evaluated_at: Optional[datetime]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                dimension: Union[str, ComplianceDimension], 
                evaluated_at: Optional[datetime] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceResourceDetailsResult(_Model):
        dimension: Union[str, ComplianceDimension]
        evaluated_at: datetime
        evaluations: list[SovereignViewDataEvaluation]
        resource_id: str
        state: Union[str, PolicyComplianceState]

        @overload
        def __init__(
                self, 
                *, 
                dimension: Union[str, ComplianceDimension], 
                evaluated_at: datetime, 
                evaluations: list[SovereignViewDataEvaluation], 
                resource_id: str, 
                state: Union[str, PolicyComplianceState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewComplianceSummaryResult(_Model):
        dimension_summaries: Optional[list[SovereignViewComplianceDimensionSummary]]
        error: Optional[ErrorDetail]
        last_evaluated: datetime
        overall_summary: Optional[SovereignViewComplianceOverallSummary]
        report_status: ReportStatus
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dimension_summaries: Optional[list[SovereignViewComplianceDimensionSummary]] = ..., 
                error: Optional[ErrorDetail] = ..., 
                last_evaluated: datetime, 
                overall_summary: Optional[SovereignViewComplianceOverallSummary] = ..., 
                report_status: ReportStatus, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDataEvaluation(_Model):
        evaluation_outcomes: list[SovereignViewDataEvaluationOutcome]
        evaluation_source_id: str
        intent: Union[str, SovereignViewEvaluationIntent]
        source: Union[str, SovereignViewLinkedResourceEvaluationSource]

        @overload
        def __init__(
                self, 
                *, 
                evaluation_outcomes: list[SovereignViewDataEvaluationOutcome], 
                evaluation_source_id: str, 
                intent: Union[str, SovereignViewEvaluationIntent], 
                source: Union[str, SovereignViewLinkedResourceEvaluationSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDataEvaluationOutcome(_Model):
        actual_value: Optional[str]
        additional_info: Optional[str]
        additional_info_code_id: Optional[str]
        expected_value: Optional[str]
        reason: Optional[str]
        reason_code_id: Optional[str]
        resource_id: Optional[str]
        state: Union[str, PolicyComplianceState]

        @overload
        def __init__(
                self, 
                *, 
                actual_value: Optional[str] = ..., 
                additional_info: Optional[str] = ..., 
                additional_info_code_id: Optional[str] = ..., 
                expected_value: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                reason_code_id: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                state: Union[str, PolicyComplianceState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDataResidencyDimensionSettings(_Model):
        parameters: SovereignViewDataResidencyParameters
        resource_evaluation_scope: Union[str, DataResidencyResourceEvaluationScope]

        @overload
        def __init__(
                self, 
                *, 
                parameters: SovereignViewDataResidencyParameters, 
                resource_evaluation_scope: Union[str, DataResidencyResourceEvaluationScope]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDataResidencyParameters(_Model):
        allowed_locations: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_locations: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDimensionDetail(_Model):
        compliance_details: list[SovereignViewComplianceDetail]
        dimension: Union[str, ComplianceDimension]
        evaluated_at: datetime
        sources: list[Union[str, SovereignViewResourceEvaluationSource]]
        state: Union[str, PolicyComplianceState]

        @overload
        def __init__(
                self, 
                *, 
                compliance_details: list[SovereignViewComplianceDetail], 
                dimension: Union[str, ComplianceDimension], 
                evaluated_at: datetime, 
                sources: list[Union[str, SovereignViewResourceEvaluationSource]], 
                state: Union[str, PolicyComplianceState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewDimensionSettings(_Model):
        data_residency: Optional[SovereignViewDataResidencyDimensionSettings]

        @overload
        def __init__(
                self, 
                *, 
                data_residency: Optional[SovereignViewDataResidencyDimensionSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewEvaluationIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CONTINUITY = "BusinessContinuity"
        GEO_REPLICA = "GeoReplica"
        LINKED_RESOURCES = "LinkedResources"


    class azure.mgmt.sovereign.models.SovereignViewFilterField(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS_CONTINUITY = "BusinessContinuity"
        CONTROLLED_NETWORK_EXPOSURE = "ControlledNetworkExposure"
        DATA_RESIDENCY = "DataResidency"
        ENCRYPTION_AT_REST = "EncryptionAtRest"
        ENCRYPTION_IN_TRANSIT = "EncryptionInTransit"
        ENCRYPTION_IN_USE = "EncryptionInUse"
        PARENT_RESOURCE_NAME = "ParentResourceName"
        REGION = "Region"
        RESOURCE_GROUP = "ResourceGroup"
        RESOURCE_NAME = "ResourceName"
        RESOURCE_TYPE = "ResourceType"
        SUBSCRIPTION = "Subscription"


    class azure.mgmt.sovereign.models.SovereignViewFilterValueItem(_Model):
        count: int
        display_name: Optional[str]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                display_name: Optional[str] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewFilterValuesContent(_Model):
        filters: Optional[list[SovereignViewComplianceDetailsFilters]]
        requested_filter: Union[str, SovereignViewFilterField]
        search_term: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[list[SovereignViewComplianceDetailsFilters]] = ..., 
                requested_filter: Union[str, SovereignViewFilterField], 
                search_term: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewFilterValuesResult(_Model):
        data_state: Union[str, DataState]
        error: Optional[ErrorDetail]
        requested_filter: Optional[Union[str, SovereignViewFilterField]]
        total_count: Optional[int]
        values_property: Optional[list[SovereignViewFilterValueItem]]

        @overload
        def __init__(
                self, 
                *, 
                data_state: Union[str, DataState], 
                error: Optional[ErrorDetail] = ..., 
                requested_filter: Optional[Union[str, SovereignViewFilterField]] = ..., 
                total_count: Optional[int] = ..., 
                values_property: Optional[list[SovereignViewFilterValueItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewLinkedResourceEvaluationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARG = "ARG"
        BUSINESS_CONTINUITY = "BusinessContinuity"
        LOG_ANALYTICS = "LogAnalytics"


    class azure.mgmt.sovereign.models.SovereignViewManagementGroupScope(_Model):
        id: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewOperationalStatusContent(_Model):
        evaluation_parameters: Optional[list[Union[str, OperationalStatusEvaluationParameter]]]
        mode: Optional[Union[str, OperationalStatusRequestMode]]

        @overload
        def __init__(
                self, 
                *, 
                evaluation_parameters: Optional[list[Union[str, OperationalStatusEvaluationParameter]]] = ..., 
                mode: Optional[Union[str, OperationalStatusRequestMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewOperationalStatusDetails(_Model):
        affected_scopes: Optional[list[SovereignViewAffectedScopes]]
        reason: Union[str, OperationalStatusUnhealthyReason]

        @overload
        def __init__(
                self, 
                *, 
                affected_scopes: Optional[list[SovereignViewAffectedScopes]] = ..., 
                reason: Union[str, OperationalStatusUnhealthyReason]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewOperationalStatusResult(_Model):
        details: Optional[list[SovereignViewOperationalStatusDetails]]
        name: str
        status: Union[str, OperationalStatusStates]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[SovereignViewOperationalStatusDetails]] = ..., 
                name: str, 
                status: Union[str, OperationalStatusStates]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewPolicyInitiativeDetail(_Model):
        dimension: Union[str, ComplianceDimension]
        policy_assignment_ids: list[str]
        policy_initiative_id: str
        policy_version: str

        @overload
        def __init__(
                self, 
                *, 
                dimension: Union[str, ComplianceDimension], 
                policy_assignment_ids: list[str], 
                policy_initiative_id: str, 
                policy_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRegulatoryDocumentName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SOVEREIGN_CONTROL_BASELINE = "SovereignControlBaseline"


    class azure.mgmt.sovereign.models.SovereignViewRemediateContent(_Model):
        dimension_type: Union[str, ComplianceDimension]
        residency_remediation_request: SovereignViewResidencyRemediationContent

        @overload
        def __init__(
                self, 
                *, 
                dimension_type: Union[str, ComplianceDimension], 
                residency_remediation_request: SovereignViewResidencyRemediationContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRemediateResult(_Model):
        error: Optional[ErrorDetail]
        remediation_id: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                remediation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRemediationPayloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM_TEMPLATE_BUNDLE = "ArmTemplateBundle"


    class azure.mgmt.sovereign.models.SovereignViewRemediationResult(_Model):
        created_at: Optional[datetime]
        dimension_type: Union[str, ComplianceDimension]
        error: Optional[ErrorDetail]
        expires_at: Optional[datetime]
        remediation_id: str
        results: Optional[list[SovereignViewRemediationResultItem]]
        status: Union[str, SovereignViewRemediationStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                dimension_type: Union[str, ComplianceDimension], 
                error: Optional[ErrorDetail] = ..., 
                expires_at: Optional[datetime] = ..., 
                remediation_id: str, 
                results: Optional[list[SovereignViewRemediationResultItem]] = ..., 
                status: Union[str, SovereignViewRemediationStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRemediationResultContent(_Model):
        remediation_id: str

        @overload
        def __init__(
                self, 
                *, 
                remediation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRemediationResultItem(_Model):
        resource_ids: list[str]
        result: SovereignViewArmTemplateBundle
        type: Union[str, SovereignViewRemediationPayloadType]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: list[str], 
                result: SovereignViewArmTemplateBundle, 
                type: Union[str, SovereignViewRemediationPayloadType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewRemediationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.sovereign.models.SovereignViewResidencyRemediationConfiguration(_Model):
        target_region: str
        target_resource_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_region: str, 
                target_resource_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResidencyRemediationContent(_Model):
        configuration: SovereignViewResidencyRemediationConfiguration
        resources: list[SovereignViewResidencyRemediationResource]

        @overload
        def __init__(
                self, 
                *, 
                configuration: SovereignViewResidencyRemediationConfiguration, 
                resources: list[SovereignViewResidencyRemediationResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResidencyRemediationResource(_Model):
        configuration: SovereignViewResidencyRemediationResourceConfiguration
        id: str

        @overload
        def __init__(
                self, 
                *, 
                configuration: SovereignViewResidencyRemediationResourceConfiguration, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResidencyRemediationResourceConfiguration(_Model):
        source_region: str
        target_resource_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_region: str, 
                target_resource_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResource(TrackedResource):
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: str
        name: str
        properties: Optional[SovereignViewResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[SovereignViewResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResourceEvaluationSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POLICY = "Policy"
        SOVEREIGN_INTELLIGENCE = "SovereignIntelligence"


    class azure.mgmt.sovereign.models.SovereignViewResourcePatch(_Model):
        identity: Optional[SystemAssignedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewResourceProperties(_Model):
        dimension_settings: Optional[SovereignViewDimensionSettings]
        is_workload: Optional[bool]
        policy_initiatives: list[SovereignViewPolicyInitiativeDetail]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regulatory_document_name: Optional[Union[str, SovereignViewRegulatoryDocumentName]]
        scope: SovereignViewScope

        @overload
        def __init__(
                self, 
                *, 
                dimension_settings: Optional[SovereignViewDimensionSettings] = ..., 
                is_workload: Optional[bool] = ..., 
                policy_initiatives: list[SovereignViewPolicyInitiativeDetail], 
                regulatory_document_name: Optional[Union[str, SovereignViewRegulatoryDocumentName]] = ..., 
                scope: SovereignViewScope
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewScope(_Model):
        management_groups: Optional[list[SovereignViewManagementGroupScope]]
        subscriptions: Optional[list[SovereignViewSubscriptionScope]]

        @overload
        def __init__(
                self, 
                *, 
                management_groups: Optional[list[SovereignViewManagementGroupScope]] = ..., 
                subscriptions: Optional[list[SovereignViewSubscriptionScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SovereignViewScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGEMENT_GROUP = "ManagementGroup"
        SUBSCRIPTION = "Subscription"


    class azure.mgmt.sovereign.models.SovereignViewSubscriptionScope(_Model):
        id: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sovereign.models.SystemAssignedServiceIdentity(_Model):
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


    class azure.mgmt.sovereign.models.SystemAssignedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.sovereign.models.SystemData(_Model):
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


    class azure.mgmt.sovereign.models.TrackedResource(Resource):
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


namespace azure.mgmt.sovereign.operations

    class azure.mgmt.sovereign.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_local(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_local(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability_local(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.sovereign.operations.SovereignViewOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: SovereignViewResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: SovereignViewResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewRemediateResult]: ...

        @overload
        def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediateContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewRemediateResult]: ...

        @overload
        def begin_remediate(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewRemediateResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: SovereignViewResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: SovereignViewResourcePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SovereignViewResource]: ...

        @overload
        def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        def compliance_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceDetailsResult: ...

        @overload
        def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceResourceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @overload
        def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewComplianceResourceDetailsContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @overload
        def compliance_resource_details(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewComplianceResourceDetailsResult: ...

        @distributed_trace
        def compliance_summary(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> SovereignViewComplianceSummaryResult: ...

        @overload
        def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewFilterValuesContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @overload
        def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewFilterValuesContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @overload
        def filter_values(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewFilterValuesResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                **kwargs: Any
            ) -> SovereignViewResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SovereignViewResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SovereignViewResource]: ...

        @overload
        def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewOperationalStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewOperationalStatusContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        def operational_status(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewOperationalStatusResult: ...

        @overload
        def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediationResultContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...

        @overload
        def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: SovereignViewRemediationResultContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...

        @overload
        def remediation_result(
                self, 
                resource_group_name: str, 
                sovereign_view_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SovereignViewRemediationResult: ...


namespace azure.mgmt.sovereign.types

    class azure.mgmt.sovereign.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.sovereign.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.sovereign.types.SovereignViewComplianceDetailsContent(TypedDict, total=False):
        key "search": ForwardRef('SovereignViewComplianceDetailsSearch', module='types')
        key "skip": int
        key "top": Required[int]
        complianceDimensions: list[SovereignViewComplianceDetailsDimensionFilter]
        filters: list[SovereignViewComplianceDetailsFilters]
        search: SovereignViewComplianceDetailsSearch
        skip: int
        sort: list[SovereignViewComplianceDetailsSort]
        top: int


    class azure.mgmt.sovereign.types.SovereignViewComplianceDetailsDimensionFilter(TypedDict, total=False):
        key "dimension": Required[Union[str, ComplianceDimension]]
        key "states": Required[list[Union[str, PolicyComplianceState]]]
        dimension: Union[str, ComplianceDimension]
        states: list[Union[str, PolicyComplianceState]]


    class azure.mgmt.sovereign.types.SovereignViewComplianceDetailsFilters(TypedDict, total=False):
        key "field": Required[Union[str, SovereignViewFilterField]]
        key "operator": Required[Union[str, SovereignViewComplianceDetailsFilterOperators]]
        key "value": Required[list[str]]
        field: Union[str, SovereignViewFilterField]
        operator: Union[str, SovereignViewComplianceDetailsFilterOperators]
        value: list[str]


    class azure.mgmt.sovereign.types.SovereignViewComplianceDetailsSearch(TypedDict, total=False):
        key "field": Required[str]
        key "value": Required[str]
        field: str
        value: str


    class azure.mgmt.sovereign.types.SovereignViewComplianceDetailsSort(TypedDict, total=False):
        key "direction": Required[Union[str, SovereignViewComplianceDetailsSortDirections]]
        key "field": Required[str]
        direction: Union[str, SovereignViewComplianceDetailsSortDirections]
        field: str
        sortingOrder: list[Union[str, PolicyComplianceState]]


    class azure.mgmt.sovereign.types.SovereignViewComplianceResourceDetailsContent(TypedDict, total=False):
        key "dimension": Required[Union[str, ComplianceDimension]]
        key "evaluatedAt": str
        key "resourceId": Required[str]
        dimension: Union[str, ComplianceDimension]
        evaluatedAt: str
        resourceId: str


    class azure.mgmt.sovereign.types.SovereignViewDataResidencyDimensionSettings(TypedDict, total=False):
        key "parameters": Required[SovereignViewDataResidencyParameters]
        key "resourceEvaluationScope": Required[Union[str, DataResidencyResourceEvaluationScope]]
        parameters: SovereignViewDataResidencyParameters
        resourceEvaluationScope: Union[str, DataResidencyResourceEvaluationScope]


    class azure.mgmt.sovereign.types.SovereignViewDataResidencyParameters(TypedDict, total=False):
        key "allowedLocations": Required[list[str]]
        allowedLocations: list[str]


    class azure.mgmt.sovereign.types.SovereignViewDimensionSettings(TypedDict, total=False):
        key "dataResidency": ForwardRef('SovereignViewDataResidencyDimensionSettings', module='types')
        dataResidency: SovereignViewDataResidencyDimensionSettings


    class azure.mgmt.sovereign.types.SovereignViewFilterValuesContent(TypedDict, total=False):
        key "requestedFilter": Required[Union[str, SovereignViewFilterField]]
        key "searchTerm": str
        filters: list[SovereignViewComplianceDetailsFilters]
        requestedFilter: Union[str, SovereignViewFilterField]
        searchTerm: str


    class azure.mgmt.sovereign.types.SovereignViewManagementGroupScope(TypedDict, total=False):
        key "id": Required[str]
        key "name": str
        id: str
        name: str


    class azure.mgmt.sovereign.types.SovereignViewOperationalStatusContent(TypedDict, total=False):
        key "mode": Union[str, OperationalStatusRequestMode]
        evaluationParameters: list[Union[str, OperationalStatusEvaluationParameter]]
        mode: Union[str, OperationalStatusRequestMode]


    class azure.mgmt.sovereign.types.SovereignViewPolicyInitiativeDetail(TypedDict, total=False):
        key "dimension": Required[Union[str, ComplianceDimension]]
        key "policyAssignmentIds": Required[list[str]]
        key "policyInitiativeId": Required[str]
        key "policyVersion": Required[str]
        dimension: Union[str, ComplianceDimension]
        policyAssignmentIds: list[str]
        policyInitiativeId: str
        policyVersion: str


    class azure.mgmt.sovereign.types.SovereignViewRemediateContent(TypedDict, total=False):
        key "dimensionType": Required[Union[str, ComplianceDimension]]
        key "residencyRemediationRequest": Required[SovereignViewResidencyRemediationContent]
        dimensionType: Union[str, ComplianceDimension]
        residencyRemediationRequest: SovereignViewResidencyRemediationContent


    class azure.mgmt.sovereign.types.SovereignViewRemediationResultContent(TypedDict, total=False):
        key "remediationId": Required[str]
        remediationId: str


    class azure.mgmt.sovereign.types.SovereignViewResidencyRemediationConfiguration(TypedDict, total=False):
        key "targetRegion": Required[str]
        key "targetResourceGroupName": str
        targetRegion: str
        targetResourceGroupName: str


    class azure.mgmt.sovereign.types.SovereignViewResidencyRemediationContent(TypedDict, total=False):
        key "configuration": Required[SovereignViewResidencyRemediationConfiguration]
        key "resources": Required[list[SovereignViewResidencyRemediationResource]]
        configuration: SovereignViewResidencyRemediationConfiguration
        resources: list[SovereignViewResidencyRemediationResource]


    class azure.mgmt.sovereign.types.SovereignViewResidencyRemediationResource(TypedDict, total=False):
        key "configuration": Required[SovereignViewResidencyRemediationResourceConfiguration]
        key "id": Required[str]
        configuration: SovereignViewResidencyRemediationResourceConfiguration
        id: str


    class azure.mgmt.sovereign.types.SovereignViewResidencyRemediationResourceConfiguration(TypedDict, total=False):
        key "sourceRegion": Required[str]
        key "targetResourceGroupName": str
        sourceRegion: str
        targetResourceGroupName: str


    class azure.mgmt.sovereign.types.SovereignViewResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SovereignViewResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: SystemAssignedServiceIdentity
        location: str
        name: str
        properties: SovereignViewResourceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.sovereign.types.SovereignViewResourcePatch(TypedDict, total=False):
        key "identity": ForwardRef('SystemAssignedServiceIdentity', module='types')
        identity: SystemAssignedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.sovereign.types.SovereignViewResourceProperties(TypedDict, total=False):
        key "dimensionSettings": ForwardRef('SovereignViewDimensionSettings', module='types')
        key "isWorkload": bool
        key "policyInitiatives": Required[list[SovereignViewPolicyInitiativeDetail]]
        key "provisioningState": Union[str, ProvisioningState]
        key "regulatoryDocumentName": Union[str, SovereignViewRegulatoryDocumentName]
        key "scope": Required[SovereignViewScope]
        dimensionSettings: SovereignViewDimensionSettings
        isWorkload: bool
        policyInitiatives: list[SovereignViewPolicyInitiativeDetail]
        provisioningState: Union[str, ProvisioningState]
        regulatoryDocumentName: Union[str, SovereignViewRegulatoryDocumentName]
        scope: SovereignViewScope


    class azure.mgmt.sovereign.types.SovereignViewScope(TypedDict, total=False):
        managementGroups: list[SovereignViewManagementGroupScope]
        subscriptions: list[SovereignViewSubscriptionScope]


    class azure.mgmt.sovereign.types.SovereignViewSubscriptionScope(TypedDict, total=False):
        key "id": Required[str]
        key "name": str
        id: str
        name: str


    class azure.mgmt.sovereign.types.SystemAssignedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, SystemAssignedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, SystemAssignedServiceIdentityType]


    class azure.mgmt.sovereign.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.sovereign.types.TrackedResource(Resource):
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


```