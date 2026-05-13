```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.playwright

    class azure.mgmt.playwright.PlaywrightMgmtClient: implements ContextManager 
        operations: Operations
        playwright_quotas: PlaywrightQuotasOperations
        playwright_workspace_quotas: PlaywrightWorkspaceQuotasOperations
        playwright_workspaces: PlaywrightWorkspacesOperations

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


namespace azure.mgmt.playwright.aio

    class azure.mgmt.playwright.aio.PlaywrightMgmtClient: implements AsyncContextManager 
        operations: Operations
        playwright_quotas: PlaywrightQuotasOperations
        playwright_workspace_quotas: PlaywrightWorkspaceQuotasOperations
        playwright_workspaces: PlaywrightWorkspacesOperations

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


namespace azure.mgmt.playwright.aio.operations

    class azure.mgmt.playwright.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.playwright.aio.operations.PlaywrightQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                playwright_quota_name: Union[str, QuotaName], 
                **kwargs: Any
            ) -> PlaywrightQuota: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlaywrightQuota]: ...


    class azure.mgmt.playwright.aio.operations.PlaywrightWorkspaceQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                quota_name: Union[str, QuotaName], 
                **kwargs: Any
            ) -> PlaywrightWorkspaceQuota: ...

        @distributed_trace
        def list_by_playwright_workspace(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlaywrightWorkspaceQuota]: ...


    class azure.mgmt.playwright.aio.operations.PlaywrightWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: PlaywrightWorkspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlaywrightWorkspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlaywrightWorkspace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlaywrightWorkspace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

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
                body: JSON, 
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

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlaywrightWorkspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[PlaywrightWorkspace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: PlaywrightWorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...


namespace azure.mgmt.playwright.models

    class azure.mgmt.playwright.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.playwright.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.playwright.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.playwright.models.CheckNameAvailabilityResponse(_Model):
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


    class azure.mgmt.playwright.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.playwright.models.EnablementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.playwright.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.playwright.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.playwright.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.FreeTrialProperties(_Model):
        state: Union[str, FreeTrialState]
        workspace_id: str


    class azure.mgmt.playwright.models.FreeTrialState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        EXPIRED = "Expired"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.playwright.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.playwright.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.playwright.models.Operation(_Model):
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


    class azure.mgmt.playwright.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.playwright.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.playwright.models.PlaywrightQuota(ProxyResource):
        id: str
        name: str
        properties: Optional[PlaywrightQuotaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlaywrightQuotaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.PlaywrightQuotaProperties(_Model):
        free_trial: Optional[FreeTrialProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.playwright.models.PlaywrightWorkspace(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[PlaywrightWorkspaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[PlaywrightWorkspaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.PlaywrightWorkspaceFreeTrialProperties(_Model):
        allocated_value: int
        created_at: datetime
        expiry_at: datetime
        percentage_used: float
        used_value: float


    class azure.mgmt.playwright.models.PlaywrightWorkspaceProperties(_Model):
        dataplane_uri: Optional[str]
        local_auth: Optional[Union[str, EnablementStatus]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regional_affinity: Optional[Union[str, EnablementStatus]]
        reporting: Optional[Union[str, EnablementStatus]]
        storage_uri: Optional[str]
        workspace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                local_auth: Optional[Union[str, EnablementStatus]] = ..., 
                regional_affinity: Optional[Union[str, EnablementStatus]] = ..., 
                reporting: Optional[Union[str, EnablementStatus]] = ..., 
                storage_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.PlaywrightWorkspaceQuota(ProxyResource):
        id: str
        name: str
        properties: Optional[PlaywrightWorkspaceQuotaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlaywrightWorkspaceQuotaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.PlaywrightWorkspaceQuotaProperties(_Model):
        free_trial: Optional[PlaywrightWorkspaceFreeTrialProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.playwright.models.PlaywrightWorkspaceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[PlaywrightWorkspaceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[PlaywrightWorkspaceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.PlaywrightWorkspaceUpdateProperties(_Model):
        local_auth: Optional[Union[str, EnablementStatus]]
        regional_affinity: Optional[Union[str, EnablementStatus]]
        reporting: Optional[Union[str, EnablementStatus]]
        storage_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                local_auth: Optional[Union[str, EnablementStatus]] = ..., 
                regional_affinity: Optional[Union[str, EnablementStatus]] = ..., 
                reporting: Optional[Union[str, EnablementStatus]] = ..., 
                storage_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.playwright.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.playwright.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.playwright.models.QuotaName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXECUTION_MINUTES = "ExecutionMinutes"


    class azure.mgmt.playwright.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.playwright.models.SystemData(_Model):
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


    class azure.mgmt.playwright.models.TrackedResource(Resource):
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


    class azure.mgmt.playwright.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.playwright.operations

    class azure.mgmt.playwright.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.playwright.operations.PlaywrightQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                playwright_quota_name: Union[str, QuotaName], 
                **kwargs: Any
            ) -> PlaywrightQuota: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[PlaywrightQuota]: ...


    class azure.mgmt.playwright.operations.PlaywrightWorkspaceQuotasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                quota_name: Union[str, QuotaName], 
                **kwargs: Any
            ) -> PlaywrightWorkspaceQuota: ...

        @distributed_trace
        def list_by_playwright_workspace(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PlaywrightWorkspaceQuota]: ...


    class azure.mgmt.playwright.operations.PlaywrightWorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: PlaywrightWorkspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlaywrightWorkspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlaywrightWorkspace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlaywrightWorkspace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

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
                body: JSON, 
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

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PlaywrightWorkspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[PlaywrightWorkspace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: PlaywrightWorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                playwright_workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PlaywrightWorkspace: ...


```