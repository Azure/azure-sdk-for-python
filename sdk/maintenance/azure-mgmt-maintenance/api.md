```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.maintenance

    class azure.mgmt.maintenance.MaintenanceManagementClient: implements ContextManager 
        apply_update_for_resource_group: ApplyUpdateForResourceGroupOperations
        apply_updates: ApplyUpdatesOperations
        configuration_assignments: ConfigurationAssignmentsOperations
        configuration_assignments_for_resource_group: ConfigurationAssignmentsForResourceGroupOperations
        configuration_assignments_for_subscriptions: ConfigurationAssignmentsForSubscriptionsOperations
        configuration_assignments_within_subscription: ConfigurationAssignmentsWithinSubscriptionOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        maintenance_configurations_for_resource_group: MaintenanceConfigurationsForResourceGroupOperations
        operations: Operations
        public_maintenance_configurations: PublicMaintenanceConfigurationsOperations
        scheduled_event: ScheduledEventOperations
        updates: UpdatesOperations

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


namespace azure.mgmt.maintenance.aio

    class azure.mgmt.maintenance.aio.MaintenanceManagementClient: implements AsyncContextManager 
        apply_update_for_resource_group: ApplyUpdateForResourceGroupOperations
        apply_updates: ApplyUpdatesOperations
        configuration_assignments: ConfigurationAssignmentsOperations
        configuration_assignments_for_resource_group: ConfigurationAssignmentsForResourceGroupOperations
        configuration_assignments_for_subscriptions: ConfigurationAssignmentsForSubscriptionsOperations
        configuration_assignments_within_subscription: ConfigurationAssignmentsWithinSubscriptionOperations
        maintenance_configurations: MaintenanceConfigurationsOperations
        maintenance_configurations_for_resource_group: MaintenanceConfigurationsForResourceGroupOperations
        operations: Operations
        public_maintenance_configurations: PublicMaintenanceConfigurationsOperations
        scheduled_event: ScheduledEventOperations
        updates: UpdatesOperations

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


namespace azure.mgmt.maintenance.aio.operations

    class azure.mgmt.maintenance.aio.operations.ApplyUpdateForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ApplyUpdate]: ...


    class azure.mgmt.maintenance.aio.operations.ApplyUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @overload
        async def create_or_update_or_cancel(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                apply_update: ApplyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @overload
        async def create_or_update_or_cancel(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                apply_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace_async
        async def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace_async
        async def get_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ApplyUpdate]: ...


    class azure.mgmt.maintenance.aio.operations.ConfigurationAssignmentsForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...


    class azure.mgmt.maintenance.aio.operations.ConfigurationAssignmentsForSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...


    class azure.mgmt.maintenance.aio.operations.ConfigurationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        async def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace_async
        async def delete_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace_async
        async def get_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationAssignment]: ...

        @distributed_trace
        def list_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.aio.operations.ConfigurationAssignmentsWithinSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.aio.operations.MaintenanceConfigurationsForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.aio.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Optional[MaintenanceConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[MaintenanceConfiguration]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...


    class azure.mgmt.maintenance.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.maintenance.aio.operations.PublicMaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.aio.operations.ScheduledEventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def acknowledge(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_event_id: str, 
                **kwargs: Any
            ) -> ScheduledEventApproveResponse: ...


    class azure.mgmt.maintenance.aio.operations.UpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Update]: ...

        @distributed_trace
        def list_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Update]: ...


namespace azure.mgmt.maintenance.models

    class azure.mgmt.maintenance.models.ApplyUpdate(Resource):
        id: str
        last_update_time: datetime
        name: str
        resource_id: str
        status: Union[str, UpdateStatus]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                last_update_time: Optional[datetime] = ..., 
                resource_id: Optional[str] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ConfigurationAssignment(Resource):
        filter: ConfigurationAssignmentFilterProperties
        id: str
        location: str
        maintenance_configuration_id: str
        name: str
        resource_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter: Optional[ConfigurationAssignmentFilterProperties] = ..., 
                location: Optional[str] = ..., 
                maintenance_configuration_id: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ConfigurationAssignmentFilterProperties(Model):
        locations: list[str]
        os_types: list[str]
        resource_groups: list[str]
        resource_types: list[str]
        tag_settings: TagSettingsProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                locations: Optional[List[str]] = ..., 
                os_types: Optional[List[str]] = ..., 
                resource_groups: Optional[List[str]] = ..., 
                resource_types: Optional[List[str]] = ..., 
                tag_settings: Optional[TagSettingsProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.maintenance.models.ErrorDetails(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ImpactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREEZE = "Freeze"
        NONE = "None"
        REDEPLOY = "Redeploy"
        RESTART = "Restart"


    class azure.mgmt.maintenance.models.InputLinuxParameters(Model):
        classifications_to_include: list[str]
        package_name_masks_to_exclude: list[str]
        package_name_masks_to_include: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[List[str]] = ..., 
                package_name_masks_to_exclude: Optional[List[str]] = ..., 
                package_name_masks_to_include: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.InputPatchConfiguration(Model):
        linux_parameters: InputLinuxParameters
        reboot_setting: Union[str, RebootOptions]
        windows_parameters: InputWindowsParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                linux_parameters: Optional[InputLinuxParameters] = ..., 
                reboot_setting: Union[str, RebootOptions] = "IfRequired", 
                windows_parameters: Optional[InputWindowsParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.InputWindowsParameters(Model):
        classifications_to_include: list[str]
        exclude_kbs_requiring_reboot: bool
        kb_numbers_to_exclude: list[str]
        kb_numbers_to_include: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[List[str]] = ..., 
                exclude_kbs_requiring_reboot: Optional[bool] = ..., 
                kb_numbers_to_exclude: Optional[List[str]] = ..., 
                kb_numbers_to_include: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ListApplyUpdate(Model):
        value: list[ApplyUpdate]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ApplyUpdate]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ListConfigurationAssignmentsResult(Model):
        value: list[ConfigurationAssignment]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ConfigurationAssignment]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ListMaintenanceConfigurationsResult(Model):
        value: list[MaintenanceConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[MaintenanceConfiguration]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ListUpdatesResult(Model):
        value: list[Update]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Update]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.MaintenanceConfiguration(Resource):
        duration: str
        expiration_date_time: str
        extension_properties: dict[str, str]
        id: str
        install_patches: InputPatchConfiguration
        location: str
        maintenance_scope: Union[str, MaintenanceScope]
        name: str
        namespace: str
        recur_every: str
        start_date_time: str
        system_data: SystemData
        tags: dict[str, str]
        time_zone: str
        type: str
        visibility: Union[str, Visibility]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                expiration_date_time: Optional[str] = ..., 
                extension_properties: Optional[Dict[str, str]] = ..., 
                install_patches: Optional[InputPatchConfiguration] = ..., 
                location: Optional[str] = ..., 
                maintenance_scope: Optional[Union[str, MaintenanceScope]] = ..., 
                namespace: Optional[str] = ..., 
                recur_every: Optional[str] = ..., 
                start_date_time: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time_zone: Optional[str] = ..., 
                visibility: Optional[Union[str, Visibility]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.MaintenanceError(Model):
        error: ErrorDetails

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.MaintenanceScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTENSION = "Extension"
        HOST = "Host"
        IN_GUEST_PATCH = "InGuestPatch"
        OS_IMAGE = "OSImage"
        RESOURCE = "Resource"
        SQLDB = "SQLDB"
        SQL_MANAGED_INSTANCE = "SQLManagedInstance"


    class azure.mgmt.maintenance.models.Operation(Model):
        display: OperationInfo
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationInfo] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.OperationInfo(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.OperationsListResult(Model):
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.RebootOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"


    class azure.mgmt.maintenance.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.ScheduledEventApproveResponse(Model):
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.TagOperators(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.maintenance.models.TagSettingsProperties(Model):
        filter_operator: Union[str, TagOperators]
        tags: dict[str, list[str]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                filter_operator: Optional[Union[str, TagOperators]] = ..., 
                tags: Optional[Dict[str, List[str]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.Update(Model):
        impact_duration_in_sec: int
        impact_type: Union[str, ImpactType]
        maintenance_scope: Union[str, MaintenanceScope]
        not_before: datetime
        resource_id: str
        status: Union[str, UpdateStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                impact_duration_in_sec: Optional[int] = ..., 
                impact_type: Optional[Union[str, ImpactType]] = ..., 
                maintenance_scope: Optional[Union[str, MaintenanceScope]] = ..., 
                not_before: Optional[datetime] = ..., 
                resource_id: Optional[str] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.maintenance.models.UpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "Cancel"
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"
        NO_UPDATES_PENDING = "NoUpdatesPending"
        PENDING = "Pending"
        RETRY_LATER = "RetryLater"
        RETRY_NOW = "RetryNow"


    class azure.mgmt.maintenance.models.Visibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        PUBLIC = "Public"


namespace azure.mgmt.maintenance.operations

    class azure.mgmt.maintenance.operations.ApplyUpdateForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[ApplyUpdate]: ...


    class azure.mgmt.maintenance.operations.ApplyUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @overload
        def create_or_update_or_cancel(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                apply_update: ApplyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @overload
        def create_or_update_or_cancel(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                apply_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace
        def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace
        def get_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                apply_update_name: str, 
                **kwargs: Any
            ) -> ApplyUpdate: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ApplyUpdate]: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsForSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace
        def get(
                self, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def update(
                self, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: ConfigurationAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @overload
        def create_or_update_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                configuration_assignment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace
        def delete_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> Optional[ConfigurationAssignment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def get_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                configuration_assignment_name: str, 
                **kwargs: Any
            ) -> ConfigurationAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Iterable[ConfigurationAssignment]: ...

        @distributed_trace
        def list_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Iterable[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsWithinSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.operations.MaintenanceConfigurationsForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Optional[MaintenanceConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[MaintenanceConfiguration]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: MaintenanceConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...


    class azure.mgmt.maintenance.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.maintenance.operations.PublicMaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.operations.ScheduledEventOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def acknowledge(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_event_id: str, 
                **kwargs: Any
            ) -> ScheduledEventApproveResponse: ...


    class azure.mgmt.maintenance.operations.UpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Iterable[Update]: ...

        @distributed_trace
        def list_parent(
                self, 
                resource_group_name: str, 
                provider_name: str, 
                resource_parent_type: str, 
                resource_parent_name: str, 
                resource_type: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Iterable[Update]: ...


```