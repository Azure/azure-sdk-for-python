```py
namespace azure.mgmt.managedops

    class azure.mgmt.managedops.ManagedOpsMgmtClient: implements ContextManager 
        managed_ops: ManagedOpsOperations
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


namespace azure.mgmt.managedops.aio

    class azure.mgmt.managedops.aio.ManagedOpsMgmtClient: implements AsyncContextManager 
        managed_ops: ManagedOpsOperations
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


namespace azure.mgmt.managedops.aio.operations

    class azure.mgmt.managedops.aio.operations.ManagedOpsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: ManagedOp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @overload
        async def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: ManagedOp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @overload
        async def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                managed_ops_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                managed_ops_name: str, 
                properties: ManagedOpUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @overload
        async def begin_update(
                self, 
                managed_ops_name: str, 
                properties: ManagedOpUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @overload
        async def begin_update(
                self, 
                managed_ops_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedOp]: ...

        @distributed_trace_async
        async def get(
                self, 
                managed_ops_name: str, 
                **kwargs: Any
            ) -> ManagedOp: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedOp]: ...


    class azure.mgmt.managedops.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.managedops.models

    class azure.mgmt.managedops.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.managedops.models.AzureMonitorConfiguration(_Model):
        azure_monitor_workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.AzureMonitorInformation(_Model):
        dcr_id: str
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                dcr_id: str, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ChangeTrackingConfiguration(_Model):
        log_analytics_workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                log_analytics_workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ChangeTrackingInformation(_Model):
        dcr_id: str
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                dcr_id: str, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managedops.models.DefenderCspmInformation(_Model):
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.DefenderForServersInformation(_Model):
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.DesiredConfiguration(_Model):
        azure_monitor_insights: AzureMonitorConfiguration
        change_tracking_and_inventory: ChangeTrackingConfiguration
        defender_cspm: Optional[Union[str, DesiredEnablementState]]
        defender_for_servers: Optional[Union[str, DesiredEnablementState]]
        user_assigned_managed_identity_id: str

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_insights: AzureMonitorConfiguration, 
                change_tracking_and_inventory: ChangeTrackingConfiguration, 
                defender_cspm: Optional[Union[str, DesiredEnablementState]] = ..., 
                defender_for_servers: Optional[Union[str, DesiredEnablementState]] = ..., 
                user_assigned_managed_identity_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.DesiredConfigurationUpdate(_Model):
        defender_cspm: Optional[Union[str, DesiredEnablementState]]
        defender_for_servers: Optional[Union[str, DesiredEnablementState]]

        @overload
        def __init__(
                self, 
                *, 
                defender_cspm: Optional[Union[str, DesiredEnablementState]] = ..., 
                defender_for_servers: Optional[Union[str, DesiredEnablementState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.DesiredEnablementState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.managedops.models.EnablementState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.managedops.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.managedops.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.managedops.models.ErrorDetails(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.GuestConfigurationInformation(_Model):
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ManagedOp(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagedOpsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedOpsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ManagedOpUpdate(_Model):
        properties: Optional[ManagedOpUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedOpUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ManagedOpUpdateProperties(_Model):
        desired_configuration: Optional[DesiredConfigurationUpdate]

        @overload
        def __init__(
                self, 
                *, 
                desired_configuration: Optional[DesiredConfigurationUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ManagedOpsProperties(_Model):
        desired_configuration: DesiredConfiguration
        policy_assignment_properties: Optional[PolicyAssignmentProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        services: Optional[ServiceInformation]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                desired_configuration: DesiredConfiguration, 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.Operation(_Model):
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


    class azure.mgmt.managedops.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.managedops.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.managedops.models.PolicyAssignmentProperties(_Model):
        policy_initiative_assignment_id: str

        @overload
        def __init__(
                self, 
                *, 
                policy_initiative_assignment_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.managedops.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.managedops.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.managedops.models.ServiceInformation(_Model):
        azure_monitor_insights: Optional[AzureMonitorInformation]
        azure_policy_and_machine_configuration: Optional[GuestConfigurationInformation]
        azure_update_manager: Optional[UpdateManagerInformation]
        change_tracking_and_inventory: Optional[ChangeTrackingInformation]
        defender_cspm: Optional[DefenderCspmInformation]
        defender_for_servers: Optional[DefenderForServersInformation]


    class azure.mgmt.managedops.models.Sku(_Model):
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                tier: Union[str, SkuTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managedops.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_OPS = "ManagedOps"


    class azure.mgmt.managedops.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESSENTIAL = "Essential"


    class azure.mgmt.managedops.models.SystemData(_Model):
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


    class azure.mgmt.managedops.models.UpdateManagerInformation(_Model):
        enablement_status: Union[str, EnablementState]
        error_details: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                enablement_status: Union[str, EnablementState], 
                error_details: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.managedops.operations

    class azure.mgmt.managedops.operations.ManagedOpsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: ManagedOp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @overload
        def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: ManagedOp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @overload
        def begin_create_or_update(
                self, 
                managed_ops_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @distributed_trace
        def begin_delete(
                self, 
                managed_ops_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                managed_ops_name: str, 
                properties: ManagedOpUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @overload
        def begin_update(
                self, 
                managed_ops_name: str, 
                properties: ManagedOpUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @overload
        def begin_update(
                self, 
                managed_ops_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedOp]: ...

        @distributed_trace
        def get(
                self, 
                managed_ops_name: str, 
                **kwargs: Any
            ) -> ManagedOp: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ManagedOp]: ...


    class azure.mgmt.managedops.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.managedops.types

    class azure.mgmt.managedops.types.AzureMonitorConfiguration(TypedDict, total=False):
        key "azureMonitorWorkspaceId": Required[str]
        azureMonitorWorkspaceId: str


    class azure.mgmt.managedops.types.AzureMonitorInformation(TypedDict, total=False):
        key "dcrId": Required[str]
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        dcrId: str
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


    class azure.mgmt.managedops.types.ChangeTrackingConfiguration(TypedDict, total=False):
        key "logAnalyticsWorkspaceId": Required[str]
        logAnalyticsWorkspaceId: str


    class azure.mgmt.managedops.types.ChangeTrackingInformation(TypedDict, total=False):
        key "dcrId": Required[str]
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        dcrId: str
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


    class azure.mgmt.managedops.types.DefenderCspmInformation(TypedDict, total=False):
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


    class azure.mgmt.managedops.types.DefenderForServersInformation(TypedDict, total=False):
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


    class azure.mgmt.managedops.types.DesiredConfiguration(TypedDict, total=False):
        key "azureMonitorInsights": Required[AzureMonitorConfiguration]
        key "changeTrackingAndInventory": Required[ChangeTrackingConfiguration]
        key "defenderCspm": Union[str, DesiredEnablementState]
        key "defenderForServers": Union[str, DesiredEnablementState]
        key "userAssignedManagedIdentityId": Required[str]
        azureMonitorInsights: AzureMonitorConfiguration
        changeTrackingAndInventory: ChangeTrackingConfiguration
        defenderCspm: Union[str, DesiredEnablementState]
        defenderForServers: Union[str, DesiredEnablementState]
        userAssignedManagedIdentityId: str


    class azure.mgmt.managedops.types.DesiredConfigurationUpdate(TypedDict, total=False):
        key "defenderCspm": Union[str, DesiredEnablementState]
        key "defenderForServers": Union[str, DesiredEnablementState]
        defenderCspm: Union[str, DesiredEnablementState]
        defenderForServers: Union[str, DesiredEnablementState]


    class azure.mgmt.managedops.types.ErrorDetails(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        message: str


    class azure.mgmt.managedops.types.GuestConfigurationInformation(TypedDict, total=False):
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


    class azure.mgmt.managedops.types.ManagedOp(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagedOpsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ManagedOpsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.managedops.types.ManagedOpUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ManagedOpUpdateProperties', module='types')
        properties: ManagedOpUpdateProperties


    class azure.mgmt.managedops.types.ManagedOpUpdateProperties(TypedDict, total=False):
        key "desiredConfiguration": ForwardRef('DesiredConfigurationUpdate', module='types')
        desiredConfiguration: DesiredConfigurationUpdate


    class azure.mgmt.managedops.types.ManagedOpsProperties(TypedDict, total=False):
        key "desiredConfiguration": Required[DesiredConfiguration]
        key "policyAssignmentProperties": ForwardRef('PolicyAssignmentProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "services": ForwardRef('ServiceInformation', module='types')
        key "sku": ForwardRef('Sku', module='types')
        desiredConfiguration: DesiredConfiguration
        policyAssignmentProperties: PolicyAssignmentProperties
        provisioningState: Union[str, ProvisioningState]
        services: ServiceInformation
        sku: Sku


    class azure.mgmt.managedops.types.PolicyAssignmentProperties(TypedDict, total=False):
        key "policyInitiativeAssignmentId": Required[str]
        policyInitiativeAssignmentId: str


    class azure.mgmt.managedops.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.managedops.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.managedops.types.ServiceInformation(TypedDict, total=False):
        key "azureMonitorInsights": ForwardRef('AzureMonitorInformation', module='types')
        key "azurePolicyAndMachineConfiguration": ForwardRef('GuestConfigurationInformation', module='types')
        key "azureUpdateManager": ForwardRef('UpdateManagerInformation', module='types')
        key "changeTrackingAndInventory": ForwardRef('ChangeTrackingInformation', module='types')
        key "defenderCspm": ForwardRef('DefenderCspmInformation', module='types')
        key "defenderForServers": ForwardRef('DefenderForServersInformation', module='types')
        azureMonitorInsights: AzureMonitorInformation
        azurePolicyAndMachineConfiguration: GuestConfigurationInformation
        azureUpdateManager: UpdateManagerInformation
        changeTrackingAndInventory: ChangeTrackingInformation
        defenderCspm: DefenderCspmInformation
        defenderForServers: DefenderForServersInformation


    class azure.mgmt.managedops.types.Sku(TypedDict, total=False):
        key "name": Required[Union[str, SkuName]]
        key "tier": Required[Union[str, SkuTier]]
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.managedops.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.managedops.types.UpdateManagerInformation(TypedDict, total=False):
        key "enablementStatus": Required[Union[str, EnablementState]]
        key "errorDetails": ForwardRef('ErrorDetails', module='types')
        enablementStatus: Union[str, EnablementState]
        errorDetails: ErrorDetails


```