```py
namespace azure.mgmt.sqlvirtualmachine

    class azure.mgmt.sqlvirtualmachine.SqlVirtualMachineManagementClient: implements ContextManager 
        availability_group_listeners: AvailabilityGroupListenersOperations
        operations: Operations
        sql_virtual_machine_groups: SqlVirtualMachineGroupsOperations
        sql_virtual_machine_troubleshoot: SqlVirtualMachineTroubleshootOperations
        sql_virtual_machines: SqlVirtualMachinesOperations

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


namespace azure.mgmt.sqlvirtualmachine.aio

    class azure.mgmt.sqlvirtualmachine.aio.SqlVirtualMachineManagementClient: implements AsyncContextManager 
        availability_group_listeners: AvailabilityGroupListenersOperations
        operations: Operations
        sql_virtual_machine_groups: SqlVirtualMachineGroupsOperations
        sql_virtual_machine_troubleshoot: SqlVirtualMachineTroubleshootOperations
        sql_virtual_machines: SqlVirtualMachinesOperations

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


namespace azure.mgmt.sqlvirtualmachine.aio.operations

    class azure.mgmt.sqlvirtualmachine.aio.operations.AvailabilityGroupListenersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: AvailabilityGroupListener, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilityGroupListener]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: AvailabilityGroupListener, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilityGroupListener]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AvailabilityGroupListener]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityGroupListener: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilityGroupListener]: ...


    class azure.mgmt.sqlvirtualmachine.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.sqlvirtualmachine.aio.operations.SqlVirtualMachineGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> SqlVirtualMachineGroup: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlVirtualMachineGroup]: ...


    class azure.mgmt.sqlvirtualmachine.aio.operations.SqlVirtualMachineTroubleshootOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVmTroubleshooting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVmTroubleshooting]: ...

        @overload
        async def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVmTroubleshooting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVmTroubleshooting]: ...

        @overload
        async def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVmTroubleshooting]: ...


    class azure.mgmt.sqlvirtualmachine.aio.operations.SqlVirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: DiskConfigAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: DiskConfigAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachine: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_sql_vm_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlVirtualMachine]: ...


namespace azure.mgmt.sqlvirtualmachine.models

    class azure.mgmt.sqlvirtualmachine.models.AADAuthenticationSettings(_Model):
        client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AdditionalFeaturesServerConfigurations(_Model):
        is_r_services_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_r_services_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AdditionalOsPatch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WSUS = "WSUS"
        WU = "WU"
        WUMU = "WUMU"


    class azure.mgmt.sqlvirtualmachine.models.AdditionalVmPatch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_UPDATE = "MicrosoftUpdate"
        NOT_SET = "NotSet"


    class azure.mgmt.sqlvirtualmachine.models.AgConfiguration(_Model):
        replicas: Optional[list[AgReplica]]

        @overload
        def __init__(
                self, 
                *, 
                replicas: Optional[list[AgReplica]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AgReplica(_Model):
        commit: Optional[Union[str, Commit]]
        failover: Optional[Union[str, Failover]]
        readable_secondary: Optional[Union[str, ReadableSecondary]]
        role: Optional[Union[str, Role]]
        sql_virtual_machine_instance_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commit: Optional[Union[str, Commit]] = ..., 
                failover: Optional[Union[str, Failover]] = ..., 
                readable_secondary: Optional[Union[str, ReadableSecondary]] = ..., 
                role: Optional[Union[str, Role]] = ..., 
                sql_virtual_machine_instance_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AssessmentDayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.sqlvirtualmachine.models.AssessmentSettings(_Model):
        enable: Optional[bool]
        run_immediately: Optional[bool]
        schedule: Optional[Schedule]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                run_immediately: Optional[bool] = ..., 
                schedule: Optional[Schedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AutoBackupDaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.sqlvirtualmachine.models.AutoBackupSettings(_Model):
        backup_schedule_type: Optional[Union[str, BackupScheduleType]]
        backup_system_dbs: Optional[bool]
        days_of_week: Optional[list[Union[str, AutoBackupDaysOfWeek]]]
        enable: Optional[bool]
        enable_encryption: Optional[bool]
        full_backup_frequency: Optional[Union[str, FullBackupFrequencyType]]
        full_backup_start_time: Optional[int]
        full_backup_window_hours: Optional[int]
        log_backup_frequency: Optional[int]
        password: Optional[str]
        retention_period: Optional[int]
        storage_access_key: Optional[str]
        storage_account_url: Optional[str]
        storage_container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_schedule_type: Optional[Union[str, BackupScheduleType]] = ..., 
                backup_system_dbs: Optional[bool] = ..., 
                days_of_week: Optional[list[Union[str, AutoBackupDaysOfWeek]]] = ..., 
                enable: Optional[bool] = ..., 
                enable_encryption: Optional[bool] = ..., 
                full_backup_frequency: Optional[Union[str, FullBackupFrequencyType]] = ..., 
                full_backup_start_time: Optional[int] = ..., 
                full_backup_window_hours: Optional[int] = ..., 
                log_backup_frequency: Optional[int] = ..., 
                password: Optional[str] = ..., 
                retention_period: Optional[int] = ..., 
                storage_access_key: Optional[str] = ..., 
                storage_account_url: Optional[str] = ..., 
                storage_container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AutoPatchingSettings(_Model):
        additional_vm_patch: Optional[Union[str, AdditionalVmPatch]]
        day_of_week: Optional[Union[str, DayOfWeek]]
        enable: Optional[bool]
        maintenance_window_duration: Optional[int]
        maintenance_window_starting_hour: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_vm_patch: Optional[Union[str, AdditionalVmPatch]] = ..., 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                enable: Optional[bool] = ..., 
                maintenance_window_duration: Optional[int] = ..., 
                maintenance_window_starting_hour: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AvailabilityGroupListener(ProxyResource):
        id: str
        name: str
        properties: Optional[AvailabilityGroupListenerProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvailabilityGroupListenerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.AvailabilityGroupListenerProperties(_Model):
        availability_group_configuration: Optional[AgConfiguration]
        availability_group_name: Optional[str]
        create_default_availability_group_if_not_exist: Optional[bool]
        load_balancer_configurations: Optional[list[LoadBalancerConfiguration]]
        multi_subnet_ip_configurations: Optional[list[MultiSubnetIpConfiguration]]
        port: Optional[int]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_group_configuration: Optional[AgConfiguration] = ..., 
                availability_group_name: Optional[str] = ..., 
                create_default_availability_group_if_not_exist: Optional[bool] = ..., 
                load_balancer_configurations: Optional[list[LoadBalancerConfiguration]] = ..., 
                multi_subnet_ip_configurations: Optional[list[MultiSubnetIpConfiguration]] = ..., 
                port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.BackupScheduleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATED = "Automated"
        MANUAL = "Manual"


    class azure.mgmt.sqlvirtualmachine.models.ClusterConfiguration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOMAINFUL = "Domainful"


    class azure.mgmt.sqlvirtualmachine.models.ClusterManagerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WSFC = "WSFC"


    class azure.mgmt.sqlvirtualmachine.models.ClusterSubnetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_SUBNET = "MultiSubnet"
        SINGLE_SUBNET = "SingleSubnet"


    class azure.mgmt.sqlvirtualmachine.models.Commit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNCHRONOUS_COMMIT = "Asynchronous_Commit"
        SYNCHRONOUS_COMMIT = "Synchronous_Commit"


    class azure.mgmt.sqlvirtualmachine.models.ConnectivityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "LOCAL"
        PRIVATE = "PRIVATE"
        PUBLIC = "PUBLIC"


    class azure.mgmt.sqlvirtualmachine.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.sqlvirtualmachine.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVERYDAY = "Everyday"
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.sqlvirtualmachine.models.DiskConfigAssessmentRequest(_Model):
        run_disk_config_rules: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                run_disk_config_rules: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.DiskConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "ADD"
        EXTEND = "EXTEND"
        NEW = "NEW"


    class azure.mgmt.sqlvirtualmachine.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.sqlvirtualmachine.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.sqlvirtualmachine.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.Failover(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.sqlvirtualmachine.models.FullBackupFrequencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        WEEKLY = "Weekly"


    class azure.mgmt.sqlvirtualmachine.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.sqlvirtualmachine.models.KeyVaultCredentialSettings(_Model):
        azure_key_vault_url: Optional[str]
        credential_name: Optional[str]
        enable: Optional[bool]
        service_principal_name: Optional[str]
        service_principal_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_key_vault_url: Optional[str] = ..., 
                credential_name: Optional[str] = ..., 
                enable: Optional[bool] = ..., 
                service_principal_name: Optional[str] = ..., 
                service_principal_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.LeastPrivilegeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLED = "Enabled"
        NOT_SET = "NotSet"


    class azure.mgmt.sqlvirtualmachine.models.LoadBalancerConfiguration(_Model):
        load_balancer_resource_id: Optional[str]
        private_ip_address: Optional[PrivateIPAddress]
        probe_port: Optional[int]
        public_ip_address_resource_id: Optional[str]
        sql_virtual_machine_instances: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                load_balancer_resource_id: Optional[str] = ..., 
                private_ip_address: Optional[PrivateIPAddress] = ..., 
                probe_port: Optional[int] = ..., 
                public_ip_address_resource_id: Optional[str] = ..., 
                sql_virtual_machine_instances: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.MultiSubnetIpConfiguration(_Model):
        private_ip_address: PrivateIPAddress
        sql_virtual_machine_instance: str

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: PrivateIPAddress, 
                sql_virtual_machine_instance: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[Union[str, OperationOrigin]]
        properties: Optional[dict[str, Any]]


    class azure.mgmt.sqlvirtualmachine.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.sqlvirtualmachine.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.sqlvirtualmachine.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.sqlvirtualmachine.models.PrivateIPAddress(_Model):
        ip_address: Optional[str]
        subnet_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                subnet_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.sqlvirtualmachine.models.ReadableSecondary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        NO = "No"
        READ_ONLY = "Read_Only"


    class azure.mgmt.sqlvirtualmachine.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.sqlvirtualmachine.models.ResourceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, IdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.Role(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.sqlvirtualmachine.models.SQLInstanceSettings(_Model):
        collation: Optional[str]
        is_ifi_enabled: Optional[bool]
        is_lpim_enabled: Optional[bool]
        is_optimize_for_ad_hoc_workloads_enabled: Optional[bool]
        max_dop: Optional[int]
        max_server_memory_mb: Optional[int]
        min_server_memory_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                collation: Optional[str] = ..., 
                is_ifi_enabled: Optional[bool] = ..., 
                is_lpim_enabled: Optional[bool] = ..., 
                is_optimize_for_ad_hoc_workloads_enabled: Optional[bool] = ..., 
                max_dop: Optional[int] = ..., 
                max_server_memory_mb: Optional[int] = ..., 
                min_server_memory_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SQLStorageSettings(_Model):
        default_file_path: Optional[str]
        luns: Optional[list[int]]
        use_storage_pool: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                default_file_path: Optional[str] = ..., 
                luns: Optional[list[int]] = ..., 
                use_storage_pool: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SQLTempDbSettings(_Model):
        data_file_count: Optional[int]
        data_file_size: Optional[int]
        data_growth: Optional[int]
        default_file_path: Optional[str]
        log_file_size: Optional[int]
        log_growth: Optional[int]
        luns: Optional[list[int]]
        persist_folder: Optional[bool]
        persist_folder_path: Optional[str]
        use_storage_pool: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                data_file_count: Optional[int] = ..., 
                data_file_size: Optional[int] = ..., 
                data_growth: Optional[int] = ..., 
                default_file_path: Optional[str] = ..., 
                log_file_size: Optional[int] = ..., 
                log_growth: Optional[int] = ..., 
                luns: Optional[list[int]] = ..., 
                persist_folder: Optional[bool] = ..., 
                persist_folder_path: Optional[str] = ..., 
                use_storage_pool: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HA = "HA"


    class azure.mgmt.sqlvirtualmachine.models.Schedule(_Model):
        day_of_week: Optional[Union[str, AssessmentDayOfWeek]]
        enable: Optional[bool]
        monthly_occurrence: Optional[int]
        start_time: Optional[str]
        weekly_interval: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, AssessmentDayOfWeek]] = ..., 
                enable: Optional[bool] = ..., 
                monthly_occurrence: Optional[int] = ..., 
                start_time: Optional[str] = ..., 
                weekly_interval: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.ServerConfigurationsManagementSettings(_Model):
        additional_features_server_configurations: Optional[AdditionalFeaturesServerConfigurations]
        azure_ad_authentication_settings: Optional[AADAuthenticationSettings]
        sql_connectivity_update_settings: Optional[SqlConnectivityUpdateSettings]
        sql_instance_settings: Optional[SQLInstanceSettings]
        sql_storage_update_settings: Optional[SqlStorageUpdateSettings]
        sql_workload_type_update_settings: Optional[SqlWorkloadTypeUpdateSettings]

        @overload
        def __init__(
                self, 
                *, 
                additional_features_server_configurations: Optional[AdditionalFeaturesServerConfigurations] = ..., 
                azure_ad_authentication_settings: Optional[AADAuthenticationSettings] = ..., 
                sql_connectivity_update_settings: Optional[SqlConnectivityUpdateSettings] = ..., 
                sql_instance_settings: Optional[SQLInstanceSettings] = ..., 
                sql_storage_update_settings: Optional[SqlStorageUpdateSettings] = ..., 
                sql_workload_type_update_settings: Optional[SqlWorkloadTypeUpdateSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlConnectivityUpdateSettings(_Model):
        connectivity_type: Optional[Union[str, ConnectivityType]]
        port: Optional[int]
        sql_auth_update_password: Optional[str]
        sql_auth_update_user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_type: Optional[Union[str, ConnectivityType]] = ..., 
                port: Optional[int] = ..., 
                sql_auth_update_password: Optional[str] = ..., 
                sql_auth_update_user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlImageSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        ENTERPRISE = "Enterprise"
        EXPRESS = "Express"
        STANDARD = "Standard"
        WEB = "Web"


    class azure.mgmt.sqlvirtualmachine.models.SqlManagementMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        LIGHT_WEIGHT = "LightWeight"
        NO_AGENT = "NoAgent"


    class azure.mgmt.sqlvirtualmachine.models.SqlServerLicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AHUB = "AHUB"
        DR = "DR"
        PAYG = "PAYG"


    class azure.mgmt.sqlvirtualmachine.models.SqlStorageUpdateSettings(_Model):
        disk_configuration_type: Optional[Union[str, DiskConfigurationType]]
        disk_count: Optional[int]
        starting_device_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                disk_configuration_type: Optional[Union[str, DiskConfigurationType]] = ..., 
                disk_count: Optional[int] = ..., 
                starting_device_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachine(TrackedResource):
        id: str
        identity: Optional[ResourceIdentity]
        location: str
        name: str
        properties: Optional[SqlVirtualMachineProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ResourceIdentity] = ..., 
                location: str, 
                properties: Optional[SqlVirtualMachineProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SqlVirtualMachineGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SqlVirtualMachineGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroupProperties(_Model):
        cluster_configuration: Optional[Union[str, ClusterConfiguration]]
        cluster_manager_type: Optional[Union[str, ClusterManagerType]]
        provisioning_state: Optional[str]
        scale_type: Optional[Union[str, ScaleType]]
        sql_image_offer: Optional[str]
        sql_image_sku: Optional[Union[str, SqlVmGroupImageSku]]
        wsfc_domain_profile: Optional[WsfcDomainProfile]

        @overload
        def __init__(
                self, 
                *, 
                sql_image_offer: Optional[str] = ..., 
                sql_image_sku: Optional[Union[str, SqlVmGroupImageSku]] = ..., 
                wsfc_domain_profile: Optional[WsfcDomainProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroupUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineProperties(_Model):
        additional_vm_patch: Optional[Union[str, AdditionalOsPatch]]
        assessment_settings: Optional[AssessmentSettings]
        auto_backup_settings: Optional[AutoBackupSettings]
        auto_patching_settings: Optional[AutoPatchingSettings]
        enable_automatic_upgrade: Optional[bool]
        key_vault_credential_settings: Optional[KeyVaultCredentialSettings]
        least_privilege_mode: Optional[Union[str, LeastPrivilegeMode]]
        os_type: Optional[Union[str, OsType]]
        provisioning_state: Optional[str]
        server_configurations_management_settings: Optional[ServerConfigurationsManagementSettings]
        sql_image_offer: Optional[str]
        sql_image_sku: Optional[Union[str, SqlImageSku]]
        sql_management: Optional[Union[str, SqlManagementMode]]
        sql_server_license_type: Optional[Union[str, SqlServerLicenseType]]
        sql_virtual_machine_group_resource_id: Optional[str]
        storage_configuration_settings: Optional[StorageConfigurationSettings]
        troubleshooting_status: Optional[TroubleshootingStatus]
        virtual_machine_identity_settings: Optional[VirtualMachineIdentity]
        virtual_machine_resource_id: Optional[str]
        wsfc_domain_credentials: Optional[WsfcDomainCredentials]
        wsfc_static_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_settings: Optional[AssessmentSettings] = ..., 
                auto_backup_settings: Optional[AutoBackupSettings] = ..., 
                auto_patching_settings: Optional[AutoPatchingSettings] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                key_vault_credential_settings: Optional[KeyVaultCredentialSettings] = ..., 
                least_privilege_mode: Optional[Union[str, LeastPrivilegeMode]] = ..., 
                server_configurations_management_settings: Optional[ServerConfigurationsManagementSettings] = ..., 
                sql_image_offer: Optional[str] = ..., 
                sql_image_sku: Optional[Union[str, SqlImageSku]] = ..., 
                sql_management: Optional[Union[str, SqlManagementMode]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                sql_virtual_machine_group_resource_id: Optional[str] = ..., 
                storage_configuration_settings: Optional[StorageConfigurationSettings] = ..., 
                virtual_machine_identity_settings: Optional[VirtualMachineIdentity] = ..., 
                virtual_machine_resource_id: Optional[str] = ..., 
                wsfc_domain_credentials: Optional[WsfcDomainCredentials] = ..., 
                wsfc_static_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlVmGroupImageSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        ENTERPRISE = "Enterprise"


    class azure.mgmt.sqlvirtualmachine.models.SqlVmTroubleshooting(_Model):
        end_time_utc: Optional[datetime]
        properties: Optional[TroubleshootingAdditionalProperties]
        start_time_utc: Optional[datetime]
        troubleshooting_scenario: Optional[Union[str, TroubleshootingScenario]]
        virtual_machine_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time_utc: Optional[datetime] = ..., 
                properties: Optional[TroubleshootingAdditionalProperties] = ..., 
                start_time_utc: Optional[datetime] = ..., 
                troubleshooting_scenario: Optional[Union[str, TroubleshootingScenario]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.SqlWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DW = "DW"
        GENERAL = "GENERAL"
        OLTP = "OLTP"


    class azure.mgmt.sqlvirtualmachine.models.SqlWorkloadTypeUpdateSettings(_Model):
        sql_workload_type: Optional[Union[str, SqlWorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                sql_workload_type: Optional[Union[str, SqlWorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.StorageConfigurationSettings(_Model):
        disk_configuration_type: Optional[Union[str, DiskConfigurationType]]
        enable_storage_config_blade: Optional[bool]
        sql_data_settings: Optional[SQLStorageSettings]
        sql_log_settings: Optional[SQLStorageSettings]
        sql_system_db_on_data_disk: Optional[bool]
        sql_temp_db_settings: Optional[SQLTempDbSettings]
        storage_workload_type: Optional[Union[str, StorageWorkloadType]]

        @overload
        def __init__(
                self, 
                *, 
                disk_configuration_type: Optional[Union[str, DiskConfigurationType]] = ..., 
                enable_storage_config_blade: Optional[bool] = ..., 
                sql_data_settings: Optional[SQLStorageSettings] = ..., 
                sql_log_settings: Optional[SQLStorageSettings] = ..., 
                sql_system_db_on_data_disk: Optional[bool] = ..., 
                sql_temp_db_settings: Optional[SQLTempDbSettings] = ..., 
                storage_workload_type: Optional[Union[str, StorageWorkloadType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.StorageWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DW = "DW"
        GENERAL = "GENERAL"
        OLTP = "OLTP"


    class azure.mgmt.sqlvirtualmachine.models.SystemData(_Model):
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


    class azure.mgmt.sqlvirtualmachine.models.TrackedResource(Resource):
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


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingAdditionalProperties(_Model):
        unhealthy_replica_info: Optional[UnhealthyReplicaInfo]

        @overload
        def __init__(
                self, 
                *, 
                unhealthy_replica_info: Optional[UnhealthyReplicaInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingScenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNHEALTHY_REPLICA = "UnhealthyReplica"


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingStatus(_Model):
        end_time_utc: Optional[datetime]
        last_trigger_time_utc: Optional[datetime]
        properties: Optional[TroubleshootingAdditionalProperties]
        root_cause: Optional[str]
        start_time_utc: Optional[datetime]
        troubleshooting_scenario: Optional[Union[str, TroubleshootingScenario]]


    class azure.mgmt.sqlvirtualmachine.models.UnhealthyReplicaInfo(_Model):
        availability_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.VirtualMachineIdentity(_Model):
        resource_id: Optional[str]
        type: Optional[Union[str, VmIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                type: Optional[Union[str, VmIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.VmIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.sqlvirtualmachine.models.WsfcDomainCredentials(_Model):
        cluster_bootstrap_account_password: Optional[str]
        cluster_operator_account_password: Optional[str]
        sql_service_account_password: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_bootstrap_account_password: Optional[str] = ..., 
                cluster_operator_account_password: Optional[str] = ..., 
                sql_service_account_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.sqlvirtualmachine.models.WsfcDomainProfile(_Model):
        cluster_bootstrap_account: Optional[str]
        cluster_operator_account: Optional[str]
        cluster_subnet_type: Optional[Union[str, ClusterSubnetType]]
        domain_fqdn: Optional[str]
        file_share_witness_path: Optional[str]
        is_sql_service_account_gmsa: Optional[bool]
        ou_path: Optional[str]
        sql_service_account: Optional[str]
        storage_account_primary_key: Optional[str]
        storage_account_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_bootstrap_account: Optional[str] = ..., 
                cluster_operator_account: Optional[str] = ..., 
                cluster_subnet_type: Optional[Union[str, ClusterSubnetType]] = ..., 
                domain_fqdn: Optional[str] = ..., 
                file_share_witness_path: Optional[str] = ..., 
                is_sql_service_account_gmsa: Optional[bool] = ..., 
                ou_path: Optional[str] = ..., 
                sql_service_account: Optional[str] = ..., 
                storage_account_primary_key: Optional[str] = ..., 
                storage_account_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.sqlvirtualmachine.operations

    class azure.mgmt.sqlvirtualmachine.operations.AvailabilityGroupListenersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: AvailabilityGroupListener, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilityGroupListener]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: AvailabilityGroupListener, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilityGroupListener]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AvailabilityGroupListener]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AvailabilityGroupListener: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvailabilityGroupListener]: ...


    class azure.mgmt.sqlvirtualmachine.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachineGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: SqlVirtualMachineGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> SqlVirtualMachineGroup: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlVirtualMachineGroup]: ...


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachineTroubleshootOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVmTroubleshooting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVmTroubleshooting]: ...

        @overload
        def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVmTroubleshooting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVmTroubleshooting]: ...

        @overload
        def begin_troubleshoot(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVmTroubleshooting]: ...


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: DiskConfigAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: DiskConfigAssessmentRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_fetch_dc_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: SqlVirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachine: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_sql_vm_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlVirtualMachine]: ...


namespace azure.mgmt.sqlvirtualmachine.types

    class azure.mgmt.sqlvirtualmachine.types.AADAuthenticationSettings(TypedDict, total=False):
        key "clientId": str
        client_id: str


    class azure.mgmt.sqlvirtualmachine.types.AdditionalFeaturesServerConfigurations(TypedDict, total=False):
        key "isRServicesEnabled": bool
        is_r_services_enabled: bool


    class azure.mgmt.sqlvirtualmachine.types.AgConfiguration(TypedDict, total=False):
        replicas: list[AgReplica]


    class azure.mgmt.sqlvirtualmachine.types.AgReplica(TypedDict, total=False):
        key "commit": Union[str, Commit]
        key "failover": Union[str, Failover]
        key "readableSecondary": Union[str, ReadableSecondary]
        key "role": Union[str, Role]
        key "sqlVirtualMachineInstanceId": str
        commit: Union[str, Commit]
        failover: Union[str, Failover]
        readable_secondary: Union[str, ReadableSecondary]
        role: Union[str, Role]
        sql_virtual_machine_instance_id: str


    class azure.mgmt.sqlvirtualmachine.types.AssessmentSettings(TypedDict, total=False):
        key "enable": bool
        key "runImmediately": bool
        key "schedule": ForwardRef('Schedule', module='types')
        enable: bool
        run_immediately: bool
        schedule: Schedule


    class azure.mgmt.sqlvirtualmachine.types.AutoBackupSettings(TypedDict, total=False):
        key "backupScheduleType": Union[str, BackupScheduleType]
        key "backupSystemDbs": bool
        key "enable": bool
        key "enableEncryption": bool
        key "fullBackupFrequency": Union[str, FullBackupFrequencyType]
        key "fullBackupStartTime": int
        key "fullBackupWindowHours": int
        key "logBackupFrequency": int
        key "password": str
        key "retentionPeriod": int
        key "storageAccessKey": str
        key "storageAccountUrl": str
        key "storageContainerName": str
        backup_schedule_type: Union[str, BackupScheduleType]
        backup_system_dbs: bool
        daysOfWeek: list[Union[str, AutoBackupDaysOfWeek]]
        days_of_week: list[Union[str, AutoBackupDaysOfWeek]]
        enable: bool
        enable_encryption: bool
        full_backup_frequency: Union[str, FullBackupFrequencyType]
        full_backup_start_time: int
        full_backup_window_hours: int
        log_backup_frequency: int
        password: str
        retention_period: int
        storage_access_key: str
        storage_account_url: str
        storage_container_name: str


    class azure.mgmt.sqlvirtualmachine.types.AutoPatchingSettings(TypedDict, total=False):
        key "additionalVmPatch": Union[str, AdditionalVmPatch]
        key "dayOfWeek": Union[str, DayOfWeek]
        key "enable": bool
        key "maintenanceWindowDuration": int
        key "maintenanceWindowStartingHour": int
        additional_vm_patch: Union[str, AdditionalVmPatch]
        day_of_week: Union[str, DayOfWeek]
        enable: bool
        maintenance_window_duration: int
        maintenance_window_starting_hour: int


    class azure.mgmt.sqlvirtualmachine.types.AvailabilityGroupListener(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AvailabilityGroupListenerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AvailabilityGroupListenerProperties
        system_data: SystemData
        type: str


    class azure.mgmt.sqlvirtualmachine.types.AvailabilityGroupListenerProperties(TypedDict, total=False):
        key "availabilityGroupConfiguration": ForwardRef('AgConfiguration', module='types')
        key "availabilityGroupName": str
        key "createDefaultAvailabilityGroupIfNotExist": bool
        key "port": int
        key "provisioningState": str
        availability_group_configuration: AgConfiguration
        availability_group_name: str
        create_default_availability_group_if_not_exist: bool
        loadBalancerConfigurations: list[LoadBalancerConfiguration]
        load_balancer_configurations: list[LoadBalancerConfiguration]
        multiSubnetIpConfigurations: list[MultiSubnetIpConfiguration]
        multi_subnet_ip_configurations: list[MultiSubnetIpConfiguration]
        port: int
        provisioning_state: str


    class azure.mgmt.sqlvirtualmachine.types.DiskConfigAssessmentRequest(TypedDict, total=False):
        key "runDiskConfigRules": bool
        run_disk_config_rules: bool


    class azure.mgmt.sqlvirtualmachine.types.KeyVaultCredentialSettings(TypedDict, total=False):
        key "azureKeyVaultUrl": str
        key "credentialName": str
        key "enable": bool
        key "servicePrincipalName": str
        key "servicePrincipalSecret": str
        azure_key_vault_url: str
        credential_name: str
        enable: bool
        service_principal_name: str
        service_principal_secret: str


    class azure.mgmt.sqlvirtualmachine.types.LoadBalancerConfiguration(TypedDict, total=False):
        key "loadBalancerResourceId": str
        key "privateIpAddress": ForwardRef('PrivateIPAddress', module='types')
        key "probePort": int
        key "publicIpAddressResourceId": str
        load_balancer_resource_id: str
        private_ip_address: PrivateIPAddress
        probe_port: int
        public_ip_address_resource_id: str
        sqlVirtualMachineInstances: list[str]
        sql_virtual_machine_instances: list[str]


    class azure.mgmt.sqlvirtualmachine.types.MultiSubnetIpConfiguration(TypedDict, total=False):
        key "privateIpAddress": Required[PrivateIPAddress]
        key "sqlVirtualMachineInstance": Required[str]
        private_ip_address: PrivateIPAddress
        sql_virtual_machine_instance: str


    class azure.mgmt.sqlvirtualmachine.types.PrivateIPAddress(TypedDict, total=False):
        key "ipAddress": str
        key "subnetResourceId": str
        ip_address: str
        subnet_resource_id: str


    class azure.mgmt.sqlvirtualmachine.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.sqlvirtualmachine.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.sqlvirtualmachine.types.ResourceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, IdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]


    class azure.mgmt.sqlvirtualmachine.types.SQLInstanceSettings(TypedDict, total=False):
        key "collation": str
        key "isIfiEnabled": bool
        key "isLpimEnabled": bool
        key "isOptimizeForAdHocWorkloadsEnabled": bool
        key "maxDop": int
        key "maxServerMemoryMB": int
        key "minServerMemoryMB": int
        collation: str
        is_ifi_enabled: bool
        is_lpim_enabled: bool
        is_optimize_for_ad_hoc_workloads_enabled: bool
        max_dop: int
        max_server_memory_mb: int
        min_server_memory_mb: int


    class azure.mgmt.sqlvirtualmachine.types.SQLStorageSettings(TypedDict, total=False):
        key "defaultFilePath": str
        key "useStoragePool": bool
        default_file_path: str
        luns: list[int]
        use_storage_pool: bool


    class azure.mgmt.sqlvirtualmachine.types.SQLTempDbSettings(TypedDict, total=False):
        key "dataFileCount": int
        key "dataFileSize": int
        key "dataGrowth": int
        key "defaultFilePath": str
        key "logFileSize": int
        key "logGrowth": int
        key "persistFolder": bool
        key "persistFolderPath": str
        key "useStoragePool": bool
        data_file_count: int
        data_file_size: int
        data_growth: int
        default_file_path: str
        log_file_size: int
        log_growth: int
        luns: list[int]
        persist_folder: bool
        persist_folder_path: str
        use_storage_pool: bool


    class azure.mgmt.sqlvirtualmachine.types.Schedule(TypedDict, total=False):
        key "dayOfWeek": Union[str, AssessmentDayOfWeek]
        key "enable": bool
        key "monthlyOccurrence": int
        key "startTime": str
        key "weeklyInterval": int
        day_of_week: Union[str, AssessmentDayOfWeek]
        enable: bool
        monthly_occurrence: int
        start_time: str
        weekly_interval: int


    class azure.mgmt.sqlvirtualmachine.types.ServerConfigurationsManagementSettings(TypedDict, total=False):
        key "additionalFeaturesServerConfigurations": ForwardRef('AdditionalFeaturesServerConfigurations', module='types')
        key "azureAdAuthenticationSettings": ForwardRef('AADAuthenticationSettings', module='types')
        key "sqlConnectivityUpdateSettings": ForwardRef('SqlConnectivityUpdateSettings', module='types')
        key "sqlInstanceSettings": ForwardRef('SQLInstanceSettings', module='types')
        key "sqlStorageUpdateSettings": ForwardRef('SqlStorageUpdateSettings', module='types')
        key "sqlWorkloadTypeUpdateSettings": ForwardRef('SqlWorkloadTypeUpdateSettings', module='types')
        additional_features_server_configurations: AdditionalFeaturesServerConfigurations
        azure_ad_authentication_settings: AADAuthenticationSettings
        sql_connectivity_update_settings: SqlConnectivityUpdateSettings
        sql_instance_settings: SQLInstanceSettings
        sql_storage_update_settings: SqlStorageUpdateSettings
        sql_workload_type_update_settings: SqlWorkloadTypeUpdateSettings


    class azure.mgmt.sqlvirtualmachine.types.SqlConnectivityUpdateSettings(TypedDict, total=False):
        key "connectivityType": Union[str, ConnectivityType]
        key "port": int
        key "sqlAuthUpdatePassword": str
        key "sqlAuthUpdateUserName": str
        connectivity_type: Union[str, ConnectivityType]
        port: int
        sql_auth_update_password: str
        sql_auth_update_user_name: str


    class azure.mgmt.sqlvirtualmachine.types.SqlStorageUpdateSettings(TypedDict, total=False):
        key "diskConfigurationType": Union[str, DiskConfigurationType]
        key "diskCount": int
        key "startingDeviceId": int
        disk_configuration_type: Union[str, DiskConfigurationType]
        disk_count: int
        starting_device_id: int


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachine(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ResourceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SqlVirtualMachineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ResourceIdentity
        location: str
        name: str
        properties: SqlVirtualMachineProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachineGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SqlVirtualMachineGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SqlVirtualMachineGroupProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachineGroupProperties(TypedDict, total=False):
        key "clusterConfiguration": Union[str, ClusterConfiguration]
        key "clusterManagerType": Union[str, ClusterManagerType]
        key "provisioningState": str
        key "scaleType": Union[str, ScaleType]
        key "sqlImageOffer": str
        key "sqlImageSku": Union[str, SqlVmGroupImageSku]
        key "wsfcDomainProfile": ForwardRef('WsfcDomainProfile', module='types')
        cluster_configuration: Union[str, ClusterConfiguration]
        cluster_manager_type: Union[str, ClusterManagerType]
        provisioning_state: str
        scale_type: Union[str, ScaleType]
        sql_image_offer: str
        sql_image_sku: Union[str, SqlVmGroupImageSku]
        wsfc_domain_profile: WsfcDomainProfile


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachineGroupUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachineProperties(TypedDict, total=False):
        key "additionalVmPatch": Union[str, AdditionalOsPatch]
        key "assessmentSettings": ForwardRef('AssessmentSettings', module='types')
        key "autoBackupSettings": ForwardRef('AutoBackupSettings', module='types')
        key "autoPatchingSettings": ForwardRef('AutoPatchingSettings', module='types')
        key "enableAutomaticUpgrade": bool
        key "keyVaultCredentialSettings": ForwardRef('KeyVaultCredentialSettings', module='types')
        key "leastPrivilegeMode": Union[str, LeastPrivilegeMode]
        key "osType": Union[str, OsType]
        key "provisioningState": str
        key "serverConfigurationsManagementSettings": ForwardRef('ServerConfigurationsManagementSettings', module='types')
        key "sqlImageOffer": str
        key "sqlImageSku": Union[str, SqlImageSku]
        key "sqlManagement": Union[str, SqlManagementMode]
        key "sqlServerLicenseType": Union[str, SqlServerLicenseType]
        key "sqlVirtualMachineGroupResourceId": str
        key "storageConfigurationSettings": ForwardRef('StorageConfigurationSettings', module='types')
        key "troubleshootingStatus": ForwardRef('TroubleshootingStatus', module='types')
        key "virtualMachineIdentitySettings": ForwardRef('VirtualMachineIdentity', module='types')
        key "virtualMachineResourceId": str
        key "wsfcDomainCredentials": ForwardRef('WsfcDomainCredentials', module='types')
        key "wsfcStaticIp": str
        additional_vm_patch: Union[str, AdditionalOsPatch]
        assessment_settings: AssessmentSettings
        auto_backup_settings: AutoBackupSettings
        auto_patching_settings: AutoPatchingSettings
        enable_automatic_upgrade: bool
        key_vault_credential_settings: KeyVaultCredentialSettings
        least_privilege_mode: Union[str, LeastPrivilegeMode]
        os_type: Union[str, OsType]
        provisioning_state: str
        server_configurations_management_settings: ServerConfigurationsManagementSettings
        sql_image_offer: str
        sql_image_sku: Union[str, SqlImageSku]
        sql_management: Union[str, SqlManagementMode]
        sql_server_license_type: Union[str, SqlServerLicenseType]
        sql_virtual_machine_group_resource_id: str
        storage_configuration_settings: StorageConfigurationSettings
        troubleshooting_status: TroubleshootingStatus
        virtual_machine_identity_settings: VirtualMachineIdentity
        virtual_machine_resource_id: str
        wsfc_domain_credentials: WsfcDomainCredentials
        wsfc_static_ip: str


    class azure.mgmt.sqlvirtualmachine.types.SqlVirtualMachineUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.sqlvirtualmachine.types.SqlVmTroubleshooting(TypedDict, total=False):
        key "endTimeUtc": str
        key "properties": ForwardRef('TroubleshootingAdditionalProperties', module='types')
        key "startTimeUtc": str
        key "troubleshootingScenario": Union[str, TroubleshootingScenario]
        key "virtualMachineResourceId": str
        end_time_utc: str
        properties: TroubleshootingAdditionalProperties
        start_time_utc: str
        troubleshooting_scenario: Union[str, TroubleshootingScenario]
        virtual_machine_resource_id: str


    class azure.mgmt.sqlvirtualmachine.types.SqlWorkloadTypeUpdateSettings(TypedDict, total=False):
        key "sqlWorkloadType": Union[str, SqlWorkloadType]
        sql_workload_type: Union[str, SqlWorkloadType]


    class azure.mgmt.sqlvirtualmachine.types.StorageConfigurationSettings(TypedDict, total=False):
        key "diskConfigurationType": Union[str, DiskConfigurationType]
        key "enableStorageConfigBlade": bool
        key "sqlDataSettings": ForwardRef('SQLStorageSettings', module='types')
        key "sqlLogSettings": ForwardRef('SQLStorageSettings', module='types')
        key "sqlSystemDbOnDataDisk": bool
        key "sqlTempDbSettings": ForwardRef('SQLTempDbSettings', module='types')
        key "storageWorkloadType": Union[str, StorageWorkloadType]
        disk_configuration_type: Union[str, DiskConfigurationType]
        enable_storage_config_blade: bool
        sql_data_settings: SQLStorageSettings
        sql_log_settings: SQLStorageSettings
        sql_system_db_on_data_disk: bool
        sql_temp_db_settings: SQLTempDbSettings
        storage_workload_type: Union[str, StorageWorkloadType]


    class azure.mgmt.sqlvirtualmachine.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.sqlvirtualmachine.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.sqlvirtualmachine.types.TroubleshootingAdditionalProperties(TypedDict, total=False):
        key "unhealthyReplicaInfo": ForwardRef('UnhealthyReplicaInfo', module='types')
        unhealthy_replica_info: UnhealthyReplicaInfo


    class azure.mgmt.sqlvirtualmachine.types.TroubleshootingStatus(TypedDict, total=False):
        key "endTimeUtc": str
        key "lastTriggerTimeUtc": str
        key "properties": ForwardRef('TroubleshootingAdditionalProperties', module='types')
        key "rootCause": str
        key "startTimeUtc": str
        key "troubleshootingScenario": Union[str, TroubleshootingScenario]
        end_time_utc: str
        last_trigger_time_utc: str
        properties: TroubleshootingAdditionalProperties
        root_cause: str
        start_time_utc: str
        troubleshooting_scenario: Union[str, TroubleshootingScenario]


    class azure.mgmt.sqlvirtualmachine.types.UnhealthyReplicaInfo(TypedDict, total=False):
        key "availabilityGroupName": str
        availability_group_name: str


    class azure.mgmt.sqlvirtualmachine.types.VirtualMachineIdentity(TypedDict, total=False):
        key "resourceId": str
        key "type": Union[str, VmIdentityType]
        resource_id: str
        type: Union[str, VmIdentityType]


    class azure.mgmt.sqlvirtualmachine.types.WsfcDomainCredentials(TypedDict, total=False):
        key "clusterBootstrapAccountPassword": str
        key "clusterOperatorAccountPassword": str
        key "sqlServiceAccountPassword": str
        cluster_bootstrap_account_password: str
        cluster_operator_account_password: str
        sql_service_account_password: str


    class azure.mgmt.sqlvirtualmachine.types.WsfcDomainProfile(TypedDict, total=False):
        key "clusterBootstrapAccount": str
        key "clusterOperatorAccount": str
        key "clusterSubnetType": Union[str, ClusterSubnetType]
        key "domainFqdn": str
        key "fileShareWitnessPath": str
        key "isSqlServiceAccountGmsa": bool
        key "ouPath": str
        key "sqlServiceAccount": str
        key "storageAccountPrimaryKey": str
        key "storageAccountUrl": str
        cluster_bootstrap_account: str
        cluster_operator_account: str
        cluster_subnet_type: Union[str, ClusterSubnetType]
        domain_fqdn: str
        file_share_witness_path: str
        is_sql_service_account_gmsa: bool
        ou_path: str
        sql_service_account: str
        storage_account_primary_key: str
        storage_account_url: str


```