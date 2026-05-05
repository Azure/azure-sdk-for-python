```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.automanage

    class azure.mgmt.automanage.AutomanageClient: implements ContextManager 
        best_practices: BestPracticesOperations
        best_practices_versions: BestPracticesVersionsOperations
        configuration_profile_assignments: ConfigurationProfileAssignmentsOperations
        configuration_profile_hci_assignments: ConfigurationProfileHCIAssignmentsOperations
        configuration_profile_hcrp_assignments: ConfigurationProfileHCRPAssignmentsOperations
        configuration_profiles: ConfigurationProfilesOperations
        configuration_profiles_versions: ConfigurationProfilesVersionsOperations
        hci_reports: HCIReportsOperations
        hcrp_reports: HCRPReportsOperations
        operations: Operations
        reports: ReportsOperations
        service_principals: ServicePrincipalsOperations

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


namespace azure.mgmt.automanage.aio

    class azure.mgmt.automanage.aio.AutomanageClient: implements AsyncContextManager 
        best_practices: BestPracticesOperations
        best_practices_versions: BestPracticesVersionsOperations
        configuration_profile_assignments: ConfigurationProfileAssignmentsOperations
        configuration_profile_hci_assignments: ConfigurationProfileHCIAssignmentsOperations
        configuration_profile_hcrp_assignments: ConfigurationProfileHCRPAssignmentsOperations
        configuration_profiles: ConfigurationProfilesOperations
        configuration_profiles_versions: ConfigurationProfilesVersionsOperations
        hci_reports: HCIReportsOperations
        hcrp_reports: HCRPReportsOperations
        operations: Operations
        reports: ReportsOperations
        service_principals: ServicePrincipalsOperations

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


namespace azure.mgmt.automanage.aio.operations

    class azure.mgmt.automanage.aio.operations.BestPracticesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                best_practice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BestPractice: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BestPractice]: ...


    class azure.mgmt.automanage.aio.operations.BestPracticesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                best_practice_name: str, 
                version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BestPractice: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                best_practice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[BestPractice]: ...


    class azure.mgmt.automanage.aio.operations.ConfigurationProfileAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_cluster_name(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_machine_name(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_virtual_machines(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfileAssignment]: ...


    class azure.mgmt.automanage.aio.operations.ConfigurationProfileHCIAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...


    class azure.mgmt.automanage.aio.operations.ConfigurationProfileHCRPAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...


    class azure.mgmt.automanage.aio.operations.ConfigurationProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfile]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfile]: ...

        @overload
        async def update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        async def update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...


    class azure.mgmt.automanage.aio.operations.ConfigurationProfilesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        async def create_or_update(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_name: str, 
                version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def list_child_resources(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationProfile]: ...


    class azure.mgmt.automanage.aio.operations.HCIReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Report]: ...


    class azure.mgmt.automanage.aio.operations.HCRPReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Report]: ...


    class azure.mgmt.automanage.aio.operations.Operations:

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


    class azure.mgmt.automanage.aio.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Report]: ...


    class azure.mgmt.automanage.aio.operations.ServicePrincipalsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServicePrincipal: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServicePrincipal]: ...


namespace azure.mgmt.automanage.models

    class azure.mgmt.automanage.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.automanage.models.AssignmentReportProperties(Model):
        configuration_profile: str
        duration: timedelta
        end_time: str
        error: ErrorDetail
        last_modified_time: str
        report_format_version: str
        resources: list[ReportResource]
        start_time: str
        status: str
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
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


    class azure.mgmt.automanage.models.BestPractice(Model):
        id: str
        name: str
        properties: ConfigurationProfileProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ConfigurationProfileProperties] = ..., 
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


    class azure.mgmt.automanage.models.BestPracticeList(Model):
        value: list[BestPractice]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[BestPractice]] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfile(TrackedResource):
        id: str
        location: str
        name: str
        properties: ConfigurationProfileProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ConfigurationProfileProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileAssignment(ProxyResource):
        id: str
        managed_by: str
        name: str
        properties: ConfigurationProfileAssignmentProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ConfigurationProfileAssignmentProperties] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileAssignmentList(Model):
        value: list[ConfigurationProfileAssignment]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationProfileAssignment]] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileAssignmentProperties(Model):
        configuration_profile: str
        status: str
        target_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                configuration_profile: Optional[str] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileList(Model):
        value: list[ConfigurationProfile]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationProfile]] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileProperties(Model):
        configuration: JSON

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                configuration: Optional[JSON] = ..., 
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


    class azure.mgmt.automanage.models.ConfigurationProfileUpdate(UpdateResource):
        properties: ConfigurationProfileProperties
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ConfigurationProfileProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.automanage.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.automanage.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

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


    class azure.mgmt.automanage.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.automanage.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.automanage.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.automanage.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.automanage.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.automanage.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.automanage.models.ProxyResource(Resource):
        id: str
        name: str
        type: str

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


    class azure.mgmt.automanage.models.Report(ProxyResource):
        id: str
        name: str
        properties: AssignmentReportProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[AssignmentReportProperties] = ..., 
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


    class azure.mgmt.automanage.models.ReportList(Model):
        value: list[Report]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Report]] = ..., 
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


    class azure.mgmt.automanage.models.ReportResource(Model):
        error: ErrorDetail
        id: str
        name: str
        status: str
        type: str

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


    class azure.mgmt.automanage.models.Resource(Model):
        id: str
        name: str
        type: str

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


    class azure.mgmt.automanage.models.ServicePrincipal(ProxyResource):
        id: str
        name: str
        properties: ServicePrincipalProperties
        system_data: SystemData
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                properties: Optional[ServicePrincipalProperties] = ..., 
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


    class azure.mgmt.automanage.models.ServicePrincipalListResult(Model):
        value: list[ServicePrincipal]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ServicePrincipal]] = ..., 
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


    class azure.mgmt.automanage.models.ServicePrincipalProperties(Model):
        authorization_set: bool
        service_principal_id: str

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


    class azure.mgmt.automanage.models.SystemData(Model):
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


    class azure.mgmt.automanage.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.automanage.models.UpdateResource(Model):
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


namespace azure.mgmt.automanage.operations

    class azure.mgmt.automanage.operations.BestPracticesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                best_practice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BestPractice: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BestPractice]: ...


    class azure.mgmt.automanage.operations.BestPracticesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                best_practice_name: str, 
                version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> BestPractice: ...

        @distributed_trace
        def list_by_tenant(
                self, 
                best_practice_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[BestPractice]: ...


    class azure.mgmt.automanage.operations.ConfigurationProfileAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_assignment_name: str, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_cluster_name(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_machine_name(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfileAssignment]: ...

        @distributed_trace
        def list_by_virtual_machines(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfileAssignment]: ...


    class azure.mgmt.automanage.operations.ConfigurationProfileHCIAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...


    class azure.mgmt.automanage.operations.ConfigurationProfileHCRPAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: ConfigurationProfileAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfileAssignment: ...


    class azure.mgmt.automanage.operations.ConfigurationProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfile]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfile]: ...

        @overload
        def update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        def update(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...


    class azure.mgmt.automanage.operations.ConfigurationProfilesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                parameters: ConfigurationProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @overload
        def create_or_update(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                configuration_profile_name: str, 
                version_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                configuration_profile_name: str, 
                version_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ConfigurationProfile: ...

        @distributed_trace
        def list_child_resources(
                self, 
                configuration_profile_name: str, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ConfigurationProfile]: ...


    class azure.mgmt.automanage.operations.HCIReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Report]: ...


    class azure.mgmt.automanage.operations.HCRPReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                machine_name: str, 
                configuration_profile_assignment_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Report]: ...


    class azure.mgmt.automanage.operations.Operations:

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


    class azure.mgmt.automanage.operations.ReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                report_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Report: ...

        @distributed_trace
        def list_by_configuration_profile_assignments(
                self, 
                resource_group_name: str, 
                configuration_profile_assignment_name: str, 
                vm_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Report]: ...


    class azure.mgmt.automanage.operations.ServicePrincipalsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServicePrincipal: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServicePrincipal]: ...


```