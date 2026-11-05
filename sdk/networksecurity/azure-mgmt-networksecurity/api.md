```py
namespace azure.mgmt.networksecurity

    class azure.mgmt.networksecurity.NetworkSecurityMgmtClient: implements ContextManager 
        neuro_shield_findings: NeuroShieldFindingsOperations
        neuro_shield_mitigations: NeuroShieldMitigationsOperations
        neuro_shield_operation_statuses: NeuroShieldOperationStatusesOperations
        neuro_shield_protected_resources: NeuroShieldProtectedResourcesOperations
        neuro_shield_summaries: NeuroShieldSummariesOperations
        neuro_shields: NeuroShieldsOperations
        operations: Operations

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


namespace azure.mgmt.networksecurity.aio

    class azure.mgmt.networksecurity.aio.NetworkSecurityMgmtClient: implements AsyncContextManager 
        neuro_shield_findings: NeuroShieldFindingsOperations
        neuro_shield_mitigations: NeuroShieldMitigationsOperations
        neuro_shield_operation_statuses: NeuroShieldOperationStatusesOperations
        neuro_shield_protected_resources: NeuroShieldProtectedResourcesOperations
        neuro_shield_summaries: NeuroShieldSummariesOperations
        neuro_shields: NeuroShieldsOperations
        operations: Operations

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


namespace azure.mgmt.networksecurity.aio.operations

    class azure.mgmt.networksecurity.aio.operations.NeuroShieldFindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldFinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldFinding]: ...

        @distributed_trace_async
        async def mitigate(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...

        @distributed_trace_async
        async def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldMitigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def execute(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace_async
        async def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldOperationStatusesOperations:

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


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldProtectedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[NeuroShieldProtectedResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldProtectedResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldProtectedResource]: ...

        @distributed_trace_async
        async def trigger_inventory_upload(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldInventoryUploadRequestResult: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldSummary: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldSummary]: ...


    class azure.mgmt.networksecurity.aio.operations.NeuroShieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NeuroShieldResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...


    class azure.mgmt.networksecurity.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.networksecurity.models

    class azure.mgmt.networksecurity.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.networksecurity.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.networksecurity.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.networksecurity.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.networksecurity.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.networksecurity.models.NeuroShieldAgentHealth(_Model):
        last_seen_time: Optional[datetime]


    class azure.mgmt.networksecurity.models.NeuroShieldFinding(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldFindingProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldFindingProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldFindingProperties(_Model):
        cve_id: str
        description: str
        detected_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        reason: str
        severity: Union[str, NeuroShieldSeverityThreshold]
        status: Union[str, NeuroShieldFindingStatus]
        virtual_machine_arm_id: str


    class azure.mgmt.networksecurity.models.NeuroShieldFindingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        AWAITING_APPROVAL = "AwaitingApproval"
        MITIGATED = "Mitigated"
        MITIGATIONS_EXHAUSTED = "MitigationsExhausted"
        MITIGATION_IN_PROGRESS = "MitigationInProgress"
        SKIPPED = "Skipped"
        UNREACHABLE = "Unreachable"


    class azure.mgmt.networksecurity.models.NeuroShieldInventoryUploadRequestMetadata(_Model):
        expires_at: datetime
        request_id: str
        requested_at: datetime


    class azure.mgmt.networksecurity.models.NeuroShieldInventoryUploadRequestResult(_Model):
        deduplicated: bool
        expires_at: datetime
        request_id: str
        requested_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                deduplicated: bool, 
                expires_at: datetime, 
                request_id: str, 
                requested_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigation(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldMitigationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldMitigationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationActionResult(_Model):
        value: list[NeuroShieldMitigation]

        @overload
        def __init__(
                self, 
                *, 
                value: list[NeuroShieldMitigation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationProperties(_Model):
        applied_time: Optional[datetime]
        commands_summary: str
        cve_id: str
        finding_id: str
        is_rollbackable: bool
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        rank: int
        status: Union[str, NeuroShieldMitigationStatus]
        status_details: Optional[str]
        virtual_machine_arm_id: str


    class azure.mgmt.networksecurity.models.NeuroShieldMitigationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_APPROVAL = "AwaitingApproval"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        QUEUED = "Queued"
        ROLLBACK_FAILED = "RollbackFailed"
        ROLLBACK_IN_PROGRESS = "RollbackInProgress"
        ROLLED_BACK = "RolledBack"
        SKIPPED = "Skipped"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networksecurity.models.NeuroShieldPatch(_Model):
        properties: Optional[NeuroShieldPatchProperties]
        tags: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NeuroShieldPatchProperties] = ..., 
                tags: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldPatchProperties(_Model):
        description: Optional[str]
        response_mode: Optional[Union[str, NeuroShieldResponseMode]]
        severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                response_mode: Optional[Union[str, NeuroShieldResponseMode]] = ..., 
                severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProperties(_Model):
        description: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningStateNeuroShield]]
        resource_guid: Optional[str]
        response_mode: Union[str, NeuroShieldResponseMode]
        severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                response_mode: Union[str, NeuroShieldResponseMode], 
                severity_threshold: Optional[Union[str, NeuroShieldSeverityThreshold]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResource(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldProtectedResourceProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldProtectedResourceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                principal_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceProperties(_Model):
        agent_health: Optional[NeuroShieldAgentHealth]
        inventory_upload_request: Optional[NeuroShieldInventoryUploadRequestMetadata]
        provisioning_state: Optional[Union[str, ProvisioningStateNeuroShield]]
        target_identity: Optional[NeuroShieldProtectedResourceIdentity]
        target_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                target_identity: Optional[NeuroShieldProtectedResourceIdentity] = ..., 
                target_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldProtectedResourceUserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldResource(TrackedResource):
        e_tag: Optional[str]
        id: str
        location: str
        name: str
        properties: NeuroShieldProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: NeuroShieldProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldResponseMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.networksecurity.models.NeuroShieldSeverityThreshold(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.networksecurity.models.NeuroShieldSummary(ProxyResource):
        id: str
        name: str
        properties: NeuroShieldSummaryProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: NeuroShieldSummaryProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.NeuroShieldSummaryProperties(_Model):
        active_findings: int
        awaiting_approval_mitigations: int
        critical_findings: int
        failed_mitigations: int
        high_findings: int
        in_progress_mitigations: int
        low_findings: int
        medium_findings: int
        protected_count: int
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        queued_mitigations: int
        rollback_in_progress_mitigations: int
        scanned_protected_count: int
        succeeded_mitigations: int
        unreachable_findings: int

        @overload
        def __init__(
                self, 
                *, 
                active_findings: int, 
                awaiting_approval_mitigations: int, 
                critical_findings: int, 
                failed_mitigations: int, 
                high_findings: int, 
                in_progress_mitigations: int, 
                low_findings: int, 
                medium_findings: int, 
                protected_count: int, 
                queued_mitigations: int, 
                rollback_in_progress_mitigations: int, 
                scanned_protected_count: int, 
                succeeded_mitigations: int, 
                unreachable_findings: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networksecurity.models.Operation(_Model):
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


    class azure.mgmt.networksecurity.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.networksecurity.models.OperationStatusResult(_Model):
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


    class azure.mgmt.networksecurity.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.networksecurity.models.ProvisioningStateNeuroShield(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networksecurity.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.networksecurity.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.networksecurity.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.networksecurity.models.SystemData(_Model):
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


    class azure.mgmt.networksecurity.models.TrackedResource(Resource):
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


namespace azure.mgmt.networksecurity.operations

    class azure.mgmt.networksecurity.operations.NeuroShieldFindingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldFinding: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldFinding]: ...

        @distributed_trace
        def mitigate(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...

        @distributed_trace
        def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                finding_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigationActionResult: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldMitigationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def execute(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def list_by_neuro_shield(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldMitigation]: ...

        @distributed_trace
        def rollback(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                mitigation_id: str, 
                **kwargs: Any
            ) -> NeuroShieldMitigation: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldOperationStatusesOperations:

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


    class azure.mgmt.networksecurity.operations.NeuroShieldProtectedResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: NeuroShieldProtectedResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[NeuroShieldProtectedResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldProtectedResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldProtectedResource]: ...

        @distributed_trace
        def trigger_inventory_upload(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                protected_resource_name: str, 
                **kwargs: Any
            ) -> NeuroShieldInventoryUploadRequestResult: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldSummary: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldSummary]: ...


    class azure.mgmt.networksecurity.operations.NeuroShieldsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: NeuroShieldResource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldResource]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NeuroShieldResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: NeuroShieldPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                neuro_shield_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> NeuroShieldResource: ...


    class azure.mgmt.networksecurity.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.networksecurity.types

    class azure.mgmt.networksecurity.types.NeuroShieldAgentHealth(TypedDict, total=False):
        key "lastSeenTime": str
        lastSeenTime: str


    class azure.mgmt.networksecurity.types.NeuroShieldInventoryUploadRequestMetadata(TypedDict, total=False):
        key "expiresAt": Required[str]
        key "requestId": Required[str]
        key "requestedAt": Required[str]
        expiresAt: str
        requestId: str
        requestedAt: str


    class azure.mgmt.networksecurity.types.NeuroShieldPatch(TypedDict, total=False):
        key "properties": ForwardRef('NeuroShieldPatchProperties', module='types')
        key "tags": Any
        properties: NeuroShieldPatchProperties
        tags: Any


    class azure.mgmt.networksecurity.types.NeuroShieldPatchProperties(TypedDict, total=False):
        key "description": str
        key "responseMode": Union[str, NeuroShieldResponseMode]
        key "severityThreshold": Union[str, NeuroShieldSeverityThreshold]
        description: str
        responseMode: Union[str, NeuroShieldResponseMode]
        severityThreshold: Union[str, NeuroShieldSeverityThreshold]


    class azure.mgmt.networksecurity.types.NeuroShieldProperties(TypedDict, total=False):
        key "description": str
        key "provisioningState": Union[str, ProvisioningStateNeuroShield]
        key "resourceGuid": str
        key "responseMode": Required[Union[str, NeuroShieldResponseMode]]
        key "severityThreshold": Union[str, NeuroShieldSeverityThreshold]
        description: str
        provisioningState: Union[str, ProvisioningStateNeuroShield]
        resourceGuid: str
        responseMode: Union[str, NeuroShieldResponseMode]
        severityThreshold: Union[str, NeuroShieldSeverityThreshold]


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[NeuroShieldProtectedResourceProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NeuroShieldProtectedResourceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        key "userAssignedIdentities": Any
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: Any


    class azure.mgmt.networksecurity.types.NeuroShieldProtectedResourceProperties(TypedDict, total=False):
        key "agentHealth": ForwardRef('NeuroShieldAgentHealth', module='types')
        key "inventoryUploadRequest": ForwardRef('NeuroShieldInventoryUploadRequestMetadata', module='types')
        key "provisioningState": Union[str, ProvisioningStateNeuroShield]
        key "targetIdentity": ForwardRef('NeuroShieldProtectedResourceIdentity', module='types')
        key "targetResourceId": Required[str]
        agentHealth: NeuroShieldAgentHealth
        inventoryUploadRequest: NeuroShieldInventoryUploadRequestMetadata
        provisioningState: Union[str, ProvisioningStateNeuroShield]
        targetIdentity: NeuroShieldProtectedResourceIdentity
        targetResourceId: str


    class azure.mgmt.networksecurity.types.NeuroShieldResource(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": Required[NeuroShieldProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: NeuroShieldProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.networksecurity.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.networksecurity.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.networksecurity.types.TrackedResource(Resource):
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