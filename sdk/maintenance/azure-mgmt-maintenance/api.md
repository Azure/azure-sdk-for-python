```py
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
        scheduled_events: ScheduledEventsOperations
        updates: UpdatesOperations

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
        scheduled_events: ScheduledEventsOperations
        updates: UpdatesOperations

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
            ) -> AsyncItemPaged[ApplyUpdate]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[ApplyUpdate]: ...


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
            ) -> AsyncItemPaged[ConfigurationAssignment]: ...

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
            ) -> AsyncItemPaged[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.aio.operations.ConfigurationAssignmentsWithinSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ConfigurationAssignment]: ...


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
            ) -> AsyncItemPaged[MaintenanceConfiguration]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[MaintenanceConfiguration]: ...

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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.aio.operations.ScheduledEventsOperations:

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
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        async def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: ScheduledEventsIdList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        async def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: ScheduledEventsIdList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        async def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...


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
            ) -> AsyncItemPaged[Update]: ...

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
            ) -> AsyncItemPaged[Update]: ...


namespace azure.mgmt.maintenance.models

    class azure.mgmt.maintenance.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.maintenance.models.ApplyUpdate(ProxyResource):
        id: str
        name: str
        properties: Optional[ApplyUpdateProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maintenance.models.ApplyUpdateProperties(_Model):
        last_update_time: Optional[datetime]
        resource_id: Optional[str]
        status: Optional[Union[str, UpdateStatus]]

        @overload
        def __init__(
                self, 
                *, 
                last_update_time: Optional[datetime] = ..., 
                resource_id: Optional[str] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ConfigurationAssignment(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ConfigurationAssignmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ConfigurationAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maintenance.models.ConfigurationAssignmentFilterProperties(_Model):
        locations: Optional[list[str]]
        os_types: Optional[list[str]]
        resource_groups: Optional[list[str]]
        resource_types: Optional[list[str]]
        tag_settings: Optional[TagSettingsProperties]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                os_types: Optional[list[str]] = ..., 
                resource_groups: Optional[list[str]] = ..., 
                resource_types: Optional[list[str]] = ..., 
                tag_settings: Optional[TagSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ConfigurationAssignmentProperties(_Model):
        filter: Optional[ConfigurationAssignmentFilterProperties]
        maintenance_configuration_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[ConfigurationAssignmentFilterProperties] = ..., 
                maintenance_configuration_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.maintenance.models.ErrorDetails(_Model):
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


    class azure.mgmt.maintenance.models.ImpactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREEZE = "Freeze"
        NONE = "None"
        REDEPLOY = "Redeploy"
        RESTART = "Restart"


    class azure.mgmt.maintenance.models.InputLinuxParameters(_Model):
        classifications_to_include: Optional[list[str]]
        package_name_masks_to_exclude: Optional[list[str]]
        package_name_masks_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[str]] = ..., 
                package_name_masks_to_exclude: Optional[list[str]] = ..., 
                package_name_masks_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.InputPatchConfiguration(_Model):
        linux_parameters: Optional[InputLinuxParameters]
        reboot_setting: Optional[Union[str, RebootOptions]]
        windows_parameters: Optional[InputWindowsParameters]

        @overload
        def __init__(
                self, 
                *, 
                linux_parameters: Optional[InputLinuxParameters] = ..., 
                reboot_setting: Optional[Union[str, RebootOptions]] = ..., 
                windows_parameters: Optional[InputWindowsParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.InputWindowsParameters(_Model):
        classifications_to_include: Optional[list[str]]
        exclude_kbs_requiring_reboot: Optional[bool]
        kb_numbers_to_exclude: Optional[list[str]]
        kb_numbers_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[str]] = ..., 
                exclude_kbs_requiring_reboot: Optional[bool] = ..., 
                kb_numbers_to_exclude: Optional[list[str]] = ..., 
                kb_numbers_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.MaintenanceConfiguration(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[MaintenanceConfigurationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[MaintenanceConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.MaintenanceConfigurationProperties(_Model):
        extension_properties: Optional[dict[str, str]]
        install_patches: Optional[InputPatchConfiguration]
        maintenance_scope: Optional[Union[str, MaintenanceScope]]
        maintenance_window: Optional[MaintenanceWindow]
        namespace: Optional[str]
        visibility: Optional[Union[str, Visibility]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extension_properties: Optional[dict[str, str]] = ..., 
                install_patches: Optional[InputPatchConfiguration] = ..., 
                maintenance_scope: Optional[Union[str, MaintenanceScope]] = ..., 
                maintenance_window: Optional[MaintenanceWindow] = ..., 
                namespace: Optional[str] = ..., 
                visibility: Optional[Union[str, Visibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maintenance.models.MaintenanceError(_Model):
        error: Optional[ErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.MaintenanceScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTENSION = "Extension"
        HOST = "Host"
        IN_GUEST_PATCH = "InGuestPatch"
        OS_IMAGE = "OSImage"
        RESOURCE = "Resource"
        SQLDB = "SQLDB"
        SQL_MANAGED_INSTANCE = "SQLManagedInstance"


    class azure.mgmt.maintenance.models.MaintenanceWindow(_Model):
        duration: Optional[str]
        expiration_date_time: Optional[str]
        recur_every: Optional[str]
        start_date_time: Optional[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                expiration_date_time: Optional[str] = ..., 
                recur_every: Optional[str] = ..., 
                start_date_time: Optional[str] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationInfo]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.OperationInfo(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.maintenance.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.maintenance.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.maintenance.models.RebootOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"


    class azure.mgmt.maintenance.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.maintenance.models.ScheduledEventsAcknowledgeErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ScheduledEventsApproveResponse(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ScheduledEventsIdList(_Model):
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                value: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ScheduledEventsListAcknowledgeError(_Model):
        error: Optional[ScheduledEventsListAcknowledgeErrorDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ScheduledEventsListAcknowledgeErrorDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.ScheduledEventsListAcknowledgeErrorDetails(_Model):
        code: Optional[str]
        details: Optional[list[ScheduledEventsAcknowledgeErrorDetails]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ScheduledEventsAcknowledgeErrorDetails]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.SystemData(_Model):
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


    class azure.mgmt.maintenance.models.TagOperators(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.maintenance.models.TagSettingsProperties(_Model):
        filter_operator: Optional[Union[str, TagOperators]]
        tags: Optional[dict[str, list[str]]]

        @overload
        def __init__(
                self, 
                *, 
                filter_operator: Optional[Union[str, TagOperators]] = ..., 
                tags: Optional[dict[str, list[str]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maintenance.models.Update(_Model):
        impact_duration_in_sec: Optional[int]
        impact_type: Optional[Union[str, ImpactType]]
        maintenance_scope: Optional[Union[str, MaintenanceScope]]
        not_before: Optional[datetime]
        properties: Optional[UpdateProperties]
        status: Optional[Union[str, UpdateStatus]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                impact_duration_in_sec: Optional[int] = ..., 
                impact_type: Optional[Union[str, ImpactType]] = ..., 
                maintenance_scope: Optional[Union[str, MaintenanceScope]] = ..., 
                not_before: Optional[datetime] = ..., 
                properties: Optional[UpdateProperties] = ..., 
                status: Optional[Union[str, UpdateStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maintenance.models.UpdateProperties(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplyUpdate]: ...


    class azure.mgmt.maintenance.operations.ApplyUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def list(self, **kwargs: Any) -> ItemPaged[ApplyUpdate]: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsForResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[ConfigurationAssignment]: ...

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
            ) -> ItemPaged[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.operations.ConfigurationAssignmentsWithinSubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ConfigurationAssignment]: ...


    class azure.mgmt.maintenance.operations.MaintenanceConfigurationsForResourceGroupOperations:

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
            ) -> ItemPaged[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.operations.MaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def list(self, **kwargs: Any) -> ItemPaged[MaintenanceConfiguration]: ...

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
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.maintenance.operations.PublicMaintenanceConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_name: str, 
                **kwargs: Any
            ) -> MaintenanceConfiguration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[MaintenanceConfiguration]: ...


    class azure.mgmt.maintenance.operations.ScheduledEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def acknowledge(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_event_id: str, 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: ScheduledEventsIdList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: ScheduledEventsIdList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...

        @overload
        def acknowledge_list(
                self, 
                resource_group_name: str, 
                resource_type: str, 
                resource_name: str, 
                scheduled_events_id_list: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScheduledEventsApproveResponse: ...


    class azure.mgmt.maintenance.operations.UpdatesOperations:

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
            ) -> ItemPaged[Update]: ...

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
            ) -> ItemPaged[Update]: ...


namespace azure.mgmt.maintenance.types

    class azure.mgmt.maintenance.types.ApplyUpdate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ApplyUpdateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ApplyUpdateProperties
        systemData: SystemData
        type: str


    class azure.mgmt.maintenance.types.ApplyUpdateProperties(TypedDict, total=False):
        key "lastUpdateTime": str
        key "resourceId": str
        key "status": Union[str, UpdateStatus]
        lastUpdateTime: str
        resourceId: str
        status: Union[str, UpdateStatus]


    class azure.mgmt.maintenance.types.ConfigurationAssignment(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ConfigurationAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ConfigurationAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.maintenance.types.ConfigurationAssignmentFilterProperties(TypedDict, total=False):
        key "tagSettings": ForwardRef('TagSettingsProperties', module='types')
        locations: list[str]
        osTypes: list[str]
        resourceGroups: list[str]
        resourceTypes: list[str]
        tagSettings: TagSettingsProperties


    class azure.mgmt.maintenance.types.ConfigurationAssignmentProperties(TypedDict, total=False):
        key "filter": ForwardRef('ConfigurationAssignmentFilterProperties', module='types')
        key "maintenanceConfigurationId": str
        key "resourceId": str
        filter: ConfigurationAssignmentFilterProperties
        maintenanceConfigurationId: str
        resourceId: str


    class azure.mgmt.maintenance.types.InputLinuxParameters(TypedDict, total=False):
        classificationsToInclude: list[str]
        packageNameMasksToExclude: list[str]
        packageNameMasksToInclude: list[str]


    class azure.mgmt.maintenance.types.InputPatchConfiguration(TypedDict, total=False):
        key "linuxParameters": ForwardRef('InputLinuxParameters', module='types')
        key "rebootSetting": Union[str, RebootOptions]
        key "windowsParameters": ForwardRef('InputWindowsParameters', module='types')
        linuxParameters: InputLinuxParameters
        rebootSetting: Union[str, RebootOptions]
        windowsParameters: InputWindowsParameters


    class azure.mgmt.maintenance.types.InputWindowsParameters(TypedDict, total=False):
        key "excludeKbsRequiringReboot": bool
        classificationsToInclude: list[str]
        excludeKbsRequiringReboot: bool
        kbNumbersToExclude: list[str]
        kbNumbersToInclude: list[str]


    class azure.mgmt.maintenance.types.MaintenanceConfiguration(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('MaintenanceConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: MaintenanceConfigurationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.maintenance.types.MaintenanceConfigurationProperties(TypedDict, total=False):
        key "installPatches": ForwardRef('InputPatchConfiguration', module='types')
        key "maintenanceScope": Union[str, MaintenanceScope]
        key "maintenanceWindow": ForwardRef('MaintenanceWindow', module='types')
        key "namespace": str
        key "visibility": Union[str, Visibility]
        extensionProperties: dict[str, str]
        installPatches: InputPatchConfiguration
        maintenanceScope: Union[str, MaintenanceScope]
        maintenanceWindow: MaintenanceWindow
        namespace: str
        visibility: Union[str, Visibility]


    class azure.mgmt.maintenance.types.MaintenanceWindow(TypedDict, total=False):
        key "duration": str
        key "expirationDateTime": str
        key "recurEvery": str
        key "startDateTime": str
        key "timeZone": str
        duration: str
        expirationDateTime: str
        recurEvery: str
        startDateTime: str
        timeZone: str


    class azure.mgmt.maintenance.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.maintenance.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.maintenance.types.ScheduledEventsIdList(TypedDict, total=False):
        key "value": Required[list[str]]
        value: list[str]


    class azure.mgmt.maintenance.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.maintenance.types.TagSettingsProperties(TypedDict, total=False):
        key "filterOperator": Union[str, TagOperators]
        filterOperator: Union[str, TagOperators]
        tags: dict[str, list[str]]


```