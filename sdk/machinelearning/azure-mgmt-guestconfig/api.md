```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.guestconfig

    class azure.mgmt.guestconfig.GuestConfigurationClient: implements ContextManager 
        guest_configuration_assignment_reports: GuestConfigurationAssignmentReportsOperations
        guest_configuration_assignment_reports_vmss: GuestConfigurationAssignmentReportsVMSSOperations
        guest_configuration_assignments: GuestConfigurationAssignmentsOperations
        guest_configuration_assignments_vmss: GuestConfigurationAssignmentsVMSSOperations
        guest_configuration_hcrp_assignment_reports: GuestConfigurationHCRPAssignmentReportsOperations
        guest_configuration_hcrp_assignments: GuestConfigurationHCRPAssignmentsOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.guestconfig.aio

    class azure.mgmt.guestconfig.aio.GuestConfigurationClient: implements AsyncContextManager 
        guest_configuration_assignment_reports: GuestConfigurationAssignmentReportsOperations
        guest_configuration_assignment_reports_vmss: GuestConfigurationAssignmentReportsVMSSOperations
        guest_configuration_assignments: GuestConfigurationAssignmentsOperations
        guest_configuration_assignments_vmss: GuestConfigurationAssignmentsVMSSOperations
        guest_configuration_hcrp_assignment_reports: GuestConfigurationHCRPAssignmentReportsOperations
        guest_configuration_hcrp_assignments: GuestConfigurationHCRPAssignmentsOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignmentReport]: ...


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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignment]: ...

        @distributed_trace
        def rg_list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignment]: ...

        @distributed_trace
        def subscription_list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.GuestConfigurationAssignmentsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[GuestConfigurationAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignment]: ...


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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.guestconfig.models

    class azure.mgmt.guestconfig.models.ActionAfterReboot(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_CONFIGURATION = "ContinueConfiguration"
        STOP_CONFIGURATION = "StopConfiguration"


    class azure.mgmt.guestconfig.models.AssignmentInfo(Model):
        configuration: ConfigurationInfo
        name: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                configuration: Optional[ConfigurationInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.AssignmentReport(Model):
        assignment: AssignmentInfo
        compliance_status: Union[str, ComplianceStatus]
        end_time: datetime
        id: str
        operation_type: Union[str, Type]
        report_id: str
        resources: list[AssignmentReportResource]
        start_time: datetime
        vm: VMInfo

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                assignment: Optional[AssignmentInfo] = ..., 
                resources: Optional[List[AssignmentReportResource]] = ..., 
                vm: Optional[VMInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.AssignmentReportDetails(Model):
        compliance_status: Union[str, ComplianceStatus]
        end_time: datetime
        job_id: str
        operation_type: Union[str, Type]
        resources: list[AssignmentReportResource]
        start_time: datetime

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resources: Optional[List[AssignmentReportResource]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.AssignmentReportResource(Model):
        compliance_status: Union[str, ComplianceStatus]
        properties: JSON
        reasons: list[AssignmentReportResourceComplianceReason]
        resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                reasons: Optional[List[AssignmentReportResourceComplianceReason]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.AssignmentReportResourceComplianceReason(Model):
        code: str
        phrase: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.AssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_AND_AUTO_CORRECT = "ApplyAndAutoCorrect"
        APPLY_AND_MONITOR = "ApplyAndMonitor"
        AUDIT = "Audit"
        DEPLOY_AND_AUTO_CORRECT = "DeployAndAutoCorrect"


    class azure.mgmt.guestconfig.models.ComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "NonCompliant"
        PENDING = "Pending"


    class azure.mgmt.guestconfig.models.ConfigurationInfo(Model):
        name: str
        version: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.ConfigurationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_AND_AUTO_CORRECT = "ApplyAndAutoCorrect"
        APPLY_AND_MONITOR = "ApplyAndMonitor"
        APPLY_ONLY = "ApplyOnly"


    class azure.mgmt.guestconfig.models.ConfigurationParameter(Model):
        name: str
        value: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.ConfigurationSetting(Model):
        action_after_reboot: Union[str, ActionAfterReboot]
        allow_module_overwrite: bool
        configuration_mode: Union[str, ConfigurationMode]
        configuration_mode_frequency_mins: float
        reboot_if_needed: bool
        refresh_frequency_mins: float

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.guestconfig.models.ErrorResponse(Model):
        error: ErrorResponseError

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.ErrorResponseError(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignment(ProxyResource):
        id: str
        location: str
        name: str
        properties: GuestConfigurationAssignmentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[GuestConfigurationAssignmentProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentList(Model):
        value: list[GuestConfigurationAssignment]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[GuestConfigurationAssignment]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentProperties(Model):
        assignment_hash: str
        compliance_status: Union[str, ComplianceStatus]
        context: str
        guest_configuration: GuestConfigurationNavigation
        last_compliance_status_checked: datetime
        latest_assignment_report: AssignmentReport
        latest_report_id: str
        parameter_hash: str
        provisioning_state: Union[str, ProvisioningState]
        resource_type: str
        target_resource_id: str
        vmss_vm_list: list[VMSSVMInfo]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                context: Optional[str] = ..., 
                guest_configuration: Optional[GuestConfigurationNavigation] = ..., 
                latest_assignment_report: Optional[AssignmentReport] = ..., 
                vmss_vm_list: Optional[List[VMSSVMInfo]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReport(Model):
        id: str
        name: str
        properties: GuestConfigurationAssignmentReportProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[GuestConfigurationAssignmentReportProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReportList(Model):
        value: list[GuestConfigurationAssignmentReport]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[GuestConfigurationAssignmentReport]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationAssignmentReportProperties(Model):
        assignment: AssignmentInfo
        compliance_status: Union[str, ComplianceStatus]
        details: AssignmentReportDetails
        end_time: datetime
        report_id: str
        start_time: datetime
        vm: VMInfo
        vmss_resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                assignment: Optional[AssignmentInfo] = ..., 
                details: Optional[AssignmentReportDetails] = ..., 
                vm: Optional[VMInfo] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.GuestConfigurationNavigation(Model):
        assignment_source: str
        assignment_type: Union[str, AssignmentType]
        configuration_parameter: list[ConfigurationParameter]
        configuration_protected_parameter: list[ConfigurationParameter]
        configuration_setting: ConfigurationSetting
        content_hash: str
        content_type: str
        content_uri: str
        kind: Union[str, Kind]
        name: str
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                assignment_type: Optional[Union[str, AssignmentType]] = ..., 
                configuration_parameter: Optional[List[ConfigurationParameter]] = ..., 
                configuration_protected_parameter: Optional[List[ConfigurationParameter]] = ..., 
                content_hash: Optional[str] = ..., 
                content_uri: Optional[str] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                name: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DSC = "DSC"


    class azure.mgmt.guestconfig.models.Operation(Model):
        display: OperationDisplay
        name: str
        status_code: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                status_code: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.OperationList(Model):
        value: list[Operation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATED = "Created"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.guestconfig.models.ProxyResource(Resource):
        id: str
        location: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.Resource(Model):
        id: str
        location: str
        name: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.Type(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONSISTENCY = "Consistency"
        INITIAL = "Initial"


    class azure.mgmt.guestconfig.models.VMInfo(Model):
        id: str
        uuid: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.guestconfig.models.VMSSVMInfo(Model):
        compliance_status: Union[str, ComplianceStatus]
        last_compliance_checked: datetime
        latest_report_id: str
        vm_id: str
        vm_resource_id: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


namespace azure.mgmt.guestconfig.operations

    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentReportsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                id: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignmentReport]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignment]: ...

        @distributed_trace
        def rg_list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignment]: ...

        @distributed_trace
        def subscription_list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationAssignmentsVMSSOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Optional[GuestConfigurationAssignment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vmss_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationHCRPAssignmentReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                report_id: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReport: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignmentReportList: ...


    class azure.mgmt.guestconfig.operations.GuestConfigurationHCRPAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                guest_configuration_assignment_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> GuestConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[GuestConfigurationAssignment]: ...


    class azure.mgmt.guestconfig.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


```