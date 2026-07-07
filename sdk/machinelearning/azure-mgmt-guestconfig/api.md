```py
namespace azure.mgmt.guestconfig

    class azure.mgmt.guestconfig.GuestConfigurationClient: implements ContextManager 
        guest_configuration_assignment_reports: GuestConfigurationAssignmentReportsOperations
        guest_configuration_assignment_reports_vmss: GuestConfigurationAssignmentReportsVMSSOperations
        guest_configuration_assignments: GuestConfigurationAssignmentsOperations
        guest_configuration_assignments_vmss: GuestConfigurationAssignmentsVMSSOperations
        guest_configuration_connected_vmwarev_sphere_assignments: GuestConfigurationConnectedVMwarevSphereAssignmentsOperations
        guest_configuration_connected_vmwarev_sphere_assignments_reports: GuestConfigurationConnectedVMwarevSphereAssignmentsReportsOperations
        guest_configuration_hcrp_assignment_reports: GuestConfigurationHCRPAssignmentReportsOperations
        guest_configuration_hcrp_assignments: GuestConfigurationHCRPAssignmentsOperations
        operations: Operations

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


namespace azure.mgmt.guestconfig.aio

    class azure.mgmt.guestconfig.aio.GuestConfigurationClient: implements AsyncContextManager 
        guest_configuration_assignment_reports: GuestConfigurationAssignmentReportsOperations
        guest_configuration_assignment_reports_vmss: GuestConfigurationAssignmentReportsVMSSOperations
        guest_configuration_assignments: GuestConfigurationAssignmentsOperations
        guest_configuration_assignments_vmss: GuestConfigurationAssignmentsVMSSOperations
        guest_configuration_connected_vmwarev_sphere_assignments: GuestConfigurationConnectedVMwarevSphereAssignmentsOperations
        guest_configuration_connected_vmwarev_sphere_assignments_reports: GuestConfigurationConnectedVMwarevSphereAssignmentsReportsOperations
        guest_configuration_hcrp_assignment_reports: GuestConfigurationHCRPAssignmentReportsOperations
        guest_configuration_hcrp_assignments: GuestConfigurationHCRPAssignmentsOperations
        operations: Operations

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


namespace azure.mgmt.guestconfig.aio.operations

    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationAssignmentReportsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                id: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignmentReport]: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignment]: ...

        @distributed_trace
        def rg_list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignment]: ...

        @distributed_trace
        def subscription_list(self, **kwargs: Any) -> AsyncItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationAssignmentsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Optional[GuestConfigurationAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationConnectedVMwarevSphereAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationConnectedVMwarevSphereAssignmentsReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationHCRPAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationHCRPAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.guestconfig.models

    class azure.mgmt.guestconfig.models.ActionAfterReboot(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_CONFIGURATION = "ContinueConfiguration"
        STOP_CONFIGURATION = "StopConfiguration"


    class azure.mgmt.guestconfig.models.AssignmentInfo(_Model):
        configuration: Optional[ConfigurationInfo]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ConfigurationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.AssignmentReport(_Model):
        assignment: Optional[AssignmentInfo]
        compliance_status: Optional[Union[str, ComplianceStatus]]
        end_time: Optional[datetime]
        id: Optional[str]
        operation_type: Optional[Union[str, Type]]
        report_id: Optional[str]
        resources: Optional[list[AssignmentReportResource]]
        start_time: Optional[datetime]
        vm: Optional[VMInfo]

        @overload
        def __init__(
                self, 
                *, 
                assignment: Optional[AssignmentInfo] = ..., 
                resources: Optional[list[AssignmentReportResource]] = ..., 
                vm: Optional[VMInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.AssignmentReportDetails(_Model):
        compliance_status: Optional[Union[str, ComplianceStatus]]
        end_time: Optional[datetime]
        job_id: Optional[str]
        operation_type: Optional[Union[str, Type]]
        resources: Optional[list[AssignmentReportResource]]
        start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                resources: Optional[list[AssignmentReportResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.AssignmentReportResource(_Model):
        compliance_status: Optional[Union[str, ComplianceStatus]]
        properties: Optional[Any]
        reasons: Optional[list[AssignmentReportResourceComplianceReason]]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reasons: Optional[list[AssignmentReportResourceComplianceReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.AssignmentReportResourceComplianceReason(_Model):
        code: Optional[str]
        phrase: Optional[str]


    class azure.mgmt.guestconfig.models.AssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_AND_AUTO_CORRECT = "ApplyAndAutoCorrect"
        APPLY_AND_MONITOR = "ApplyAndMonitor"
        AUDIT = "Audit"
        DEPLOY_AND_AUTO_CORRECT = "DeployAndAutoCorrect"


    class azure.mgmt.guestconfig.models.ComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "NonCompliant"
        PENDING = "Pending"


    class azure.mgmt.guestconfig.models.ConfigurationInfo(_Model):
        name: Optional[str]
        version: Optional[str]


    class azure.mgmt.guestconfig.models.ConfigurationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_AND_AUTO_CORRECT = "ApplyAndAutoCorrect"
        APPLY_AND_MONITOR = "ApplyAndMonitor"
        APPLY_ONLY = "ApplyOnly"


    class azure.mgmt.guestconfig.models.ConfigurationParameter(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.ConfigurationSetting(_Model):
        action_after_reboot: Optional[Union[str, ActionAfterReboot]]
        allow_module_overwrite: Optional[bool]
        configuration_mode: Optional[Union[str, ConfigurationMode]]
        configuration_mode_frequency_mins: Optional[float]
        reboot_if_needed: Optional[bool]
        refresh_frequency_mins: Optional[float]


    class azure.mgmt.guestconfig.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.guestconfig.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.ErrorResponseError(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignment(ProxyResource):
        id: str
        location: str
        name: str
        properties: Optional[GuestConfigurationAssignmentProperties]
        system_data: Optional[SystemData]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: str, 
                properties: Optional[GuestConfigurationAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentProperties(_Model):
        assignment_hash: Optional[str]
        compliance_status: Optional[Union[str, ComplianceStatus]]
        context: Optional[str]
        guest_configuration: Optional[GuestConfigurationNavigation]
        last_compliance_status_checked: Optional[datetime]
        latest_assignment_report: Optional[AssignmentReport]
        latest_report_id: Optional[str]
        parameter_hash: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_type: Optional[str]
        target_resource_id: Optional[str]
        vmss_vm_list: Optional[list[VMSSVMInfo]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                guest_configuration: Optional[GuestConfigurationNavigation] = ..., 
                latest_assignment_report: Optional[AssignmentReport] = ..., 
                vmss_vm_list: Optional[list[VMSSVMInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReport(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[GuestConfigurationAssignmentReportProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GuestConfigurationAssignmentReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReportList(_Model):
        next_link: Optional[str]
        value: Optional[list[GuestConfigurationAssignmentReport]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[GuestConfigurationAssignmentReport]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReportProperties(_Model):
        assignment: Optional[AssignmentInfo]
        compliance_status: Optional[Union[str, ComplianceStatus]]
        details: Optional[AssignmentReportDetails]
        end_time: Optional[datetime]
        report_id: Optional[str]
        start_time: Optional[datetime]
        vm: Optional[VMInfo]
        vmss_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assignment: Optional[AssignmentInfo] = ..., 
                details: Optional[AssignmentReportDetails] = ..., 
                vm: Optional[VMInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationNavigation(_Model):
        assignment_source: Optional[str]
        assignment_type: Optional[Union[str, AssignmentType]]
        configuration_parameter: Optional[list[ConfigurationParameter]]
        configuration_protected_parameter: Optional[list[ConfigurationParameter]]
        configuration_setting: Optional[ConfigurationSetting]
        content_hash: Optional[str]
        content_managed_identity: Optional[str]
        content_type: Optional[str]
        content_uri: Optional[str]
        kind: Optional[Union[str, Kind]]
        name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                configuration_parameter: Optional[list[ConfigurationParameter]] = ..., 
                configuration_protected_parameter: Optional[list[ConfigurationParameter]] = ..., 
                content_hash: Optional[str] = ..., 
                content_managed_identity: Optional[str] = ..., 
                content_uri: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                name: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DSC = "DSC"


    class azure.mgmt.guestconfig.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        properties: Optional[OperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.guestconfig.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.OperationProperties(_Model):
        status_code: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status_code: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATED = "Created"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.guestconfig.models.ProxyResource(_Model):
        id: Optional[str]
        location: Optional[str]
        name: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.guestconfig.models.SystemData(_Model):
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


    class azure.mgmt.guestconfig.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENCY = "Consistency"
        INITIAL = "Initial"


    class azure.mgmt.guestconfig.models.VMInfo(_Model):
        id: Optional[str]
        uuid: Optional[str]


    class azure.mgmt.guestconfig.models.VMSSVMInfo(_Model):
        compliance_status: Optional[Union[str, ComplianceStatus]]
        last_compliance_checked: Optional[datetime]
        latest_report_id: Optional[str]
        vm_id: Optional[str]
        vm_resource_id: Optional[str]


namespace azure.mgmt.guestconfig.operations

    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentReportsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                id: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignmentReport]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignment]: ...

        @distributed_trace
        def rg_list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignment]: ...

        @distributed_trace
        def subscription_list(self, **kwargs: Any) -> ItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Optional[GuestConfigurationAssignment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationConnectedVMwarevSphereAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationConnectedVMwarevSphereAssignmentsReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                guest_configuration_assignment_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationHCRPAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationHCRPAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: GuestConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                guest_configuration_assignment_name: str, 
                resource_group_name: str, 
                machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.guestconfig.types

    class azure.mgmt.guestconfig.types.AssignmentInfo(TypedDict, total=False):
        key "configuration": ForwardRef('ConfigurationInfo', module='types')
        key "name": str
        configuration: ConfigurationInfo
        name: str


    class azure.mgmt.guestconfig.types.AssignmentReport(TypedDict, total=False):
        key "assignment": ForwardRef('AssignmentInfo', module='types')
        key "complianceStatus": Union[str, ComplianceStatus]
        key "endTime": str
        key "id": str
        key "operationType": Union[str, Type]
        key "reportId": str
        key "startTime": str
        key "vm": ForwardRef('VMInfo', module='types')
        assignment: AssignmentInfo
        compliance_status: Union[str, ComplianceStatus]
        end_time: str
        id: str
        operation_type: Union[str, Type]
        report_id: str
        resources: list[AssignmentReportResource]
        start_time: str
        vm: VMInfo


    class azure.mgmt.guestconfig.types.AssignmentReportDetails(TypedDict, total=False):
        key "complianceStatus": Union[str, ComplianceStatus]
        key "endTime": str
        key "jobId": str
        key "operationType": Union[str, Type]
        key "startTime": str
        compliance_status: Union[str, ComplianceStatus]
        end_time: str
        job_id: str
        operation_type: Union[str, Type]
        resources: list[AssignmentReportResource]
        start_time: str


    class azure.mgmt.guestconfig.types.AssignmentReportResource(TypedDict, total=False):
        key "complianceStatus": Union[str, ComplianceStatus]
        key "properties": Any
        key "resourceId": str
        compliance_status: Union[str, ComplianceStatus]
        properties: Any
        reasons: list[AssignmentReportResourceComplianceReason]
        resource_id: str


    class azure.mgmt.guestconfig.types.AssignmentReportResourceComplianceReason(TypedDict, total=False):
        key "code": str
        key "phrase": str
        code: str
        phrase: str


    class azure.mgmt.guestconfig.types.ConfigurationInfo(TypedDict, total=False):
        key "name": str
        key "version": str
        name: str
        version: str


    class azure.mgmt.guestconfig.types.ConfigurationParameter(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.guestconfig.types.ConfigurationSetting(TypedDict, total=False):
        key "actionAfterReboot": Union[str, ActionAfterReboot]
        key "allowModuleOverwrite": bool
        key "configurationMode": Union[str, ConfigurationMode]
        key "configurationModeFrequencyMins": float
        key "rebootIfNeeded": bool
        key "refreshFrequencyMins": float
        action_after_reboot: Union[str, ActionAfterReboot]
        allow_module_overwrite: bool
        configuration_mode: Union[str, ConfigurationMode]
        configuration_mode_frequency_mins: float
        reboot_if_needed: bool
        refresh_frequency_mins: float


    class azure.mgmt.guestconfig.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorResponseError', module='types')
        error: ErrorResponseError


    class azure.mgmt.guestconfig.types.ErrorResponseError(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.guestconfig.types.GuestConfigurationAssignment(ProxyResource):
        key "id": str
        key "location": str
        key "name": Required[str]
        key "properties": ForwardRef('GuestConfigurationAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: GuestConfigurationAssignmentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.guestconfig.types.GuestConfigurationAssignmentProperties(TypedDict, total=False):
        key "assignmentHash": Optional[str]
        key "complianceStatus": Union[str, ComplianceStatus]
        key "context": str
        key "guestConfiguration": ForwardRef('GuestConfigurationNavigation', module='types')
        key "lastComplianceStatusChecked": Optional[str]
        key "latestAssignmentReport": ForwardRef('AssignmentReport', module='types')
        key "latestReportId": Optional[str]
        key "parameterHash": Optional[str]
        key "provisioningState": Optional[Union[str, ProvisioningState]]
        key "resourceType": Optional[str]
        key "targetResourceId": Optional[str]
        assignment_hash: str
        compliance_status: Union[str, ComplianceStatus]
        context: str
        guest_configuration: GuestConfigurationNavigation
        last_compliance_status_checked: str
        latest_assignment_report: AssignmentReport
        latest_report_id: str
        parameter_hash: str
        provisioning_state: Union[str, ProvisioningState]
        resource_type: str
        target_resource_id: str
        vmssVMList: list[VMSSVMInfo]
        vmss_vm_list: list[VMSSVMInfo]


    class azure.mgmt.guestconfig.types.GuestConfigurationAssignmentReport(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GuestConfigurationAssignmentReportProperties', module='types')
        id: str
        name: str
        properties: GuestConfigurationAssignmentReportProperties


    class azure.mgmt.guestconfig.types.GuestConfigurationAssignmentReportList(TypedDict, total=False):
        key "nextLink": str
        next_link: str
        value: list[GuestConfigurationAssignmentReport]


    class azure.mgmt.guestconfig.types.GuestConfigurationAssignmentReportProperties(TypedDict, total=False):
        key "assignment": ForwardRef('AssignmentInfo', module='types')
        key "complianceStatus": Union[str, ComplianceStatus]
        key "details": Optional[AssignmentReportDetails]
        key "endTime": str
        key "reportId": str
        key "startTime": str
        key "vm": ForwardRef('VMInfo', module='types')
        key "vmssResourceId": str
        assignment: AssignmentInfo
        compliance_status: Union[str, ComplianceStatus]
        details: AssignmentReportDetails
        end_time: str
        report_id: str
        start_time: str
        vm: VMInfo
        vmss_resource_id: str


    class azure.mgmt.guestconfig.types.GuestConfigurationNavigation(TypedDict, total=False):
        key "assignmentSource": Optional[str]
        key "assignmentType": Union[str, AssignmentType]
        key "configurationSetting": ForwardRef('ConfigurationSetting', module='types')
        key "contentHash": str
        key "contentManagedIdentity": str
        key "contentType": Optional[str]
        key "contentUri": str
        key "kind": Union[str, Kind]
        key "name": str
        key "version": str
        assignment_source: str
        assignment_type: Union[str, AssignmentType]
        configurationParameter: list[ConfigurationParameter]
        configurationProtectedParameter: list[ConfigurationParameter]
        configuration_parameter: list[ConfigurationParameter]
        configuration_protected_parameter: list[ConfigurationParameter]
        configuration_setting: ConfigurationSetting
        content_hash: str
        content_managed_identity: str
        content_type: str
        content_uri: str
        kind: Union[str, Kind]
        name: str
        version: str


    class azure.mgmt.guestconfig.types.Operation(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "name": str
        key "properties": ForwardRef('OperationProperties', module='types')
        display: OperationDisplay
        name: str
        properties: OperationProperties


    class azure.mgmt.guestconfig.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.guestconfig.types.OperationProperties(TypedDict, total=False):
        key "statusCode": str
        status_code: str


    class azure.mgmt.guestconfig.types.ProxyResource(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": Required[str]
        key "type": str
        id: str
        location: str
        name: str
        type: str


    class azure.mgmt.guestconfig.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.guestconfig.types.VMInfo(TypedDict, total=False):
        key "id": str
        key "uuid": str
        id: str
        uuid: str


    class azure.mgmt.guestconfig.types.VMSSVMInfo(TypedDict, total=False):
        key "complianceStatus": Union[str, ComplianceStatus]
        key "lastComplianceChecked": Optional[str]
        key "latestReportId": Optional[str]
        key "vmId": str
        key "vmResourceId": str
        compliance_status: Union[str, ComplianceStatus]
        last_compliance_checked: str
        latest_report_id: str
        vm_id: str
        vm_resource_id: str


```