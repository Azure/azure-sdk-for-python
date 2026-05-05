```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AvailabilityGroupListener: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AvailabilityGroupListener]: ...


    class azure.mgmt.sqlvirtualmachine.aio.operations.Operations:

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachineGroup: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlVirtualMachineGroup]: ...


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
                parameters: IO, 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlVirtualMachine]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_sql_vm_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SqlVirtualMachine]: ...


namespace azure.mgmt.sqlvirtualmachine.models

    class azure.mgmt.sqlvirtualmachine.models.AADAuthenticationSettings(Model):
        client_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AdditionalFeaturesServerConfigurations(Model):
        is_r_services_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_r_services_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AgConfiguration(Model):
        replicas: list[AgReplica]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                replicas: Optional[List[AgReplica]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AgReplica(Model):
        commit: Union[str, Commit]
        failover: Union[str, Failover]
        readable_secondary: Union[str, ReadableSecondary]
        role: Union[str, Role]
        sql_virtual_machine_instance_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commit: Optional[Union[str, Commit]] = ..., 
                failover: Optional[Union[str, Failover]] = ..., 
                readable_secondary: Optional[Union[str, ReadableSecondary]] = ..., 
                role: Optional[Union[str, Role]] = ..., 
                sql_virtual_machine_instance_id: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AssessmentDayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.sqlvirtualmachine.models.AssessmentSettings(Model):
        enable: bool
        run_immediately: bool
        schedule: Schedule

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                run_immediately: Optional[bool] = ..., 
                schedule: Optional[Schedule] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AutoBackupDaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.sqlvirtualmachine.models.AutoBackupSettings(Model):
        backup_schedule_type: Union[str, BackupScheduleType]
        backup_system_dbs: bool
        days_of_week: Union[list[str, AutoBackupDaysOfWeek]]
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_schedule_type: Optional[Union[str, BackupScheduleType]] = ..., 
                backup_system_dbs: Optional[bool] = ..., 
                days_of_week: Optional[List[Union[str, AutoBackupDaysOfWeek]]] = ..., 
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
                storage_container_name: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AutoPatchingSettings(Model):
        day_of_week: Union[str, DayOfWeek]
        enable: bool
        maintenance_window_duration: int
        maintenance_window_starting_hour: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                enable: Optional[bool] = ..., 
                maintenance_window_duration: Optional[int] = ..., 
                maintenance_window_starting_hour: Optional[int] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AvailabilityGroupListener(ProxyResource):
        availability_group_configuration: AgConfiguration
        availability_group_name: str
        create_default_availability_group_if_not_exist: bool
        id: str
        load_balancer_configurations: list[LoadBalancerConfiguration]
        multi_subnet_ip_configurations: list[MultiSubnetIpConfiguration]
        name: str
        port: int
        provisioning_state: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_group_configuration: Optional[AgConfiguration] = ..., 
                availability_group_name: Optional[str] = ..., 
                create_default_availability_group_if_not_exist: Optional[bool] = ..., 
                load_balancer_configurations: Optional[List[LoadBalancerConfiguration]] = ..., 
                multi_subnet_ip_configurations: Optional[List[MultiSubnetIpConfiguration]] = ..., 
                port: Optional[int] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.AvailabilityGroupListenerListResult(Model):
        next_link: str
        value: list[AvailabilityGroupListener]

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
        ASYNCHRONOUS_COMMIT = "ASYNCHRONOUS_COMMIT"
        SYNCHRONOUS_COMMIT = "SYNCHRONOUS_COMMIT"


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


    class azure.mgmt.sqlvirtualmachine.models.DiskConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "ADD"
        EXTEND = "EXTEND"
        NEW = "NEW"


    class azure.mgmt.sqlvirtualmachine.models.ErrorAdditionalInfo(Model):
        info: JSON
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


    class azure.mgmt.sqlvirtualmachine.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

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


    class azure.mgmt.sqlvirtualmachine.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.Failover(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "AUTOMATIC"
        MANUAL = "MANUAL"


    class azure.mgmt.sqlvirtualmachine.models.FullBackupFrequencyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        WEEKLY = "Weekly"


    class azure.mgmt.sqlvirtualmachine.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.sqlvirtualmachine.models.KeyVaultCredentialSettings(Model):
        azure_key_vault_url: str
        credential_name: str
        enable: bool
        service_principal_name: str
        service_principal_secret: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_key_vault_url: Optional[str] = ..., 
                credential_name: Optional[str] = ..., 
                enable: Optional[bool] = ..., 
                service_principal_name: Optional[str] = ..., 
                service_principal_secret: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.LeastPrivilegeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLED = "Enabled"
        NOT_SET = "NotSet"


    class azure.mgmt.sqlvirtualmachine.models.LoadBalancerConfiguration(Model):
        load_balancer_resource_id: str
        private_ip_address: PrivateIPAddress
        probe_port: int
        public_ip_address_resource_id: str
        sql_virtual_machine_instances: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                load_balancer_resource_id: Optional[str] = ..., 
                private_ip_address: Optional[PrivateIPAddress] = ..., 
                probe_port: Optional[int] = ..., 
                public_ip_address_resource_id: Optional[str] = ..., 
                sql_virtual_machine_instances: Optional[List[str]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.MultiSubnetIpConfiguration(Model):
        private_ip_address: PrivateIPAddress
        sql_virtual_machine_instance: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_ip_address: PrivateIPAddress, 
                sql_virtual_machine_instance: str, 
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


    class azure.mgmt.sqlvirtualmachine.models.Operation(Model):
        display: OperationDisplay
        name: str
        origin: Union[str, OperationOrigin]
        properties: dict[str, JSON]

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


    class azure.mgmt.sqlvirtualmachine.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.sqlvirtualmachine.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.sqlvirtualmachine.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.sqlvirtualmachine.models.PrivateIPAddress(Model):
        ip_address: str
        subnet_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
                subnet_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.ProxyResource(Resource):
        id: str
        name: str
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


    class azure.mgmt.sqlvirtualmachine.models.ReadableSecondary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "ALL"
        NO = "NO"
        READ_ONLY = "READ_ONLY"


    class azure.mgmt.sqlvirtualmachine.models.Resource(Model):
        id: str
        name: str
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


    class azure.mgmt.sqlvirtualmachine.models.ResourceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, IdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityType]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.Role(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "PRIMARY"
        SECONDARY = "SECONDARY"


    class azure.mgmt.sqlvirtualmachine.models.SQLInstanceSettings(Model):
        collation: str
        is_ifi_enabled: bool
        is_lpim_enabled: bool
        is_optimize_for_ad_hoc_workloads_enabled: bool
        max_dop: int
        max_server_memory_mb: int
        min_server_memory_mb: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collation: Optional[str] = ..., 
                is_ifi_enabled: Optional[bool] = ..., 
                is_lpim_enabled: Optional[bool] = ..., 
                is_optimize_for_ad_hoc_workloads_enabled: Optional[bool] = ..., 
                max_dop: Optional[int] = ..., 
                max_server_memory_mb: Optional[int] = ..., 
                min_server_memory_mb: Optional[int] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SQLStorageSettings(Model):
        default_file_path: str
        luns: list[int]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_file_path: Optional[str] = ..., 
                luns: Optional[List[int]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SQLTempDbSettings(Model):
        data_file_count: int
        data_file_size: int
        data_growth: int
        default_file_path: str
        log_file_size: int
        log_growth: int
        luns: list[int]
        persist_folder: bool
        persist_folder_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_file_count: Optional[int] = ..., 
                data_file_size: Optional[int] = ..., 
                data_growth: Optional[int] = ..., 
                default_file_path: Optional[str] = ..., 
                log_file_size: Optional[int] = ..., 
                log_growth: Optional[int] = ..., 
                luns: Optional[List[int]] = ..., 
                persist_folder: Optional[bool] = ..., 
                persist_folder_path: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.ScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HA = "HA"


    class azure.mgmt.sqlvirtualmachine.models.Schedule(Model):
        day_of_week: Union[str, AssessmentDayOfWeek]
        enable: bool
        monthly_occurrence: int
        start_time: str
        weekly_interval: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, AssessmentDayOfWeek]] = ..., 
                enable: Optional[bool] = ..., 
                monthly_occurrence: Optional[int] = ..., 
                start_time: Optional[str] = ..., 
                weekly_interval: Optional[int] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.ServerConfigurationsManagementSettings(Model):
        additional_features_server_configurations: AdditionalFeaturesServerConfigurations
        azure_ad_authentication_settings: AADAuthenticationSettings
        sql_connectivity_update_settings: SqlConnectivityUpdateSettings
        sql_instance_settings: SQLInstanceSettings
        sql_storage_update_settings: SqlStorageUpdateSettings
        sql_workload_type_update_settings: SqlWorkloadTypeUpdateSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_features_server_configurations: Optional[AdditionalFeaturesServerConfigurations] = ..., 
                azure_ad_authentication_settings: Optional[AADAuthenticationSettings] = ..., 
                sql_connectivity_update_settings: Optional[SqlConnectivityUpdateSettings] = ..., 
                sql_instance_settings: Optional[SQLInstanceSettings] = ..., 
                sql_storage_update_settings: Optional[SqlStorageUpdateSettings] = ..., 
                sql_workload_type_update_settings: Optional[SqlWorkloadTypeUpdateSettings] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlConnectivityUpdateSettings(Model):
        connectivity_type: Union[str, ConnectivityType]
        port: int
        sql_auth_update_password: str
        sql_auth_update_user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connectivity_type: Optional[Union[str, ConnectivityType]] = ..., 
                port: Optional[int] = ..., 
                sql_auth_update_password: Optional[str] = ..., 
                sql_auth_update_user_name: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlStorageUpdateSettings(Model):
        disk_configuration_type: Union[str, DiskConfigurationType]
        disk_count: int
        starting_device_id: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_configuration_type: Optional[Union[str, DiskConfigurationType]] = ..., 
                disk_count: Optional[int] = ..., 
                starting_device_id: Optional[int] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachine(TrackedResource):
        assessment_settings: AssessmentSettings
        auto_backup_settings: AutoBackupSettings
        auto_patching_settings: AutoPatchingSettings
        enable_automatic_upgrade: bool
        id: str
        identity: ResourceIdentity
        key_vault_credential_settings: KeyVaultCredentialSettings
        least_privilege_mode: Union[str, LeastPrivilegeMode]
        location: str
        name: str
        provisioning_state: str
        server_configurations_management_settings: ServerConfigurationsManagementSettings
        sql_image_offer: str
        sql_image_sku: Union[str, SqlImageSku]
        sql_management: Union[str, SqlManagementMode]
        sql_server_license_type: Union[str, SqlServerLicenseType]
        sql_virtual_machine_group_resource_id: str
        storage_configuration_settings: StorageConfigurationSettings
        system_data: SystemData
        tags: dict[str, str]
        troubleshooting_status: TroubleshootingStatus
        type: str
        virtual_machine_resource_id: str
        wsfc_domain_credentials: WsfcDomainCredentials
        wsfc_static_ip: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                assessment_settings: Optional[AssessmentSettings] = ..., 
                auto_backup_settings: Optional[AutoBackupSettings] = ..., 
                auto_patching_settings: Optional[AutoPatchingSettings] = ..., 
                enable_automatic_upgrade: bool = False, 
                identity: Optional[ResourceIdentity] = ..., 
                key_vault_credential_settings: Optional[KeyVaultCredentialSettings] = ..., 
                least_privilege_mode: Union[str, LeastPrivilegeMode] = "NotSet", 
                location: str, 
                server_configurations_management_settings: Optional[ServerConfigurationsManagementSettings] = ..., 
                sql_image_offer: Optional[str] = ..., 
                sql_image_sku: Optional[Union[str, SqlImageSku]] = ..., 
                sql_management: Optional[Union[str, SqlManagementMode]] = ..., 
                sql_server_license_type: Optional[Union[str, SqlServerLicenseType]] = ..., 
                sql_virtual_machine_group_resource_id: Optional[str] = ..., 
                storage_configuration_settings: Optional[StorageConfigurationSettings] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                virtual_machine_resource_id: Optional[str] = ..., 
                wsfc_domain_credentials: Optional[WsfcDomainCredentials] = ..., 
                wsfc_static_ip: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroup(TrackedResource):
        cluster_configuration: Union[str, ClusterConfiguration]
        cluster_manager_type: Union[str, ClusterManagerType]
        id: str
        location: str
        name: str
        provisioning_state: str
        scale_type: Union[str, ScaleType]
        sql_image_offer: str
        sql_image_sku: Union[str, SqlVmGroupImageSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        wsfc_domain_profile: WsfcDomainProfile

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                sql_image_offer: Optional[str] = ..., 
                sql_image_sku: Optional[Union[str, SqlVmGroupImageSku]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                wsfc_domain_profile: Optional[WsfcDomainProfile] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroupListResult(Model):
        next_link: str
        value: list[SqlVirtualMachineGroup]

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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineGroupUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineListResult(Model):
        next_link: str
        value: list[SqlVirtualMachine]

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


    class azure.mgmt.sqlvirtualmachine.models.SqlVirtualMachineUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlVmGroupImageSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEVELOPER = "Developer"
        ENTERPRISE = "Enterprise"


    class azure.mgmt.sqlvirtualmachine.models.SqlVmTroubleshooting(Model):
        end_time_utc: datetime
        properties: TroubleshootingAdditionalProperties
        start_time_utc: datetime
        troubleshooting_scenario: Union[str, TroubleshootingScenario]
        virtual_machine_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time_utc: Optional[datetime] = ..., 
                properties: Optional[TroubleshootingAdditionalProperties] = ..., 
                start_time_utc: Optional[datetime] = ..., 
                troubleshooting_scenario: Optional[Union[str, TroubleshootingScenario]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.SqlWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DW = "DW"
        GENERAL = "GENERAL"
        OLTP = "OLTP"


    class azure.mgmt.sqlvirtualmachine.models.SqlWorkloadTypeUpdateSettings(Model):
        sql_workload_type: Union[str, SqlWorkloadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sql_workload_type: Optional[Union[str, SqlWorkloadType]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.StorageConfigurationSettings(Model):
        disk_configuration_type: Union[str, DiskConfigurationType]
        sql_data_settings: SQLStorageSettings
        sql_log_settings: SQLStorageSettings
        sql_system_db_on_data_disk: bool
        sql_temp_db_settings: SQLTempDbSettings
        storage_workload_type: Union[str, StorageWorkloadType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_configuration_type: Optional[Union[str, DiskConfigurationType]] = ..., 
                sql_data_settings: Optional[SQLStorageSettings] = ..., 
                sql_log_settings: Optional[SQLStorageSettings] = ..., 
                sql_system_db_on_data_disk: Optional[bool] = ..., 
                sql_temp_db_settings: Optional[SQLTempDbSettings] = ..., 
                storage_workload_type: Optional[Union[str, StorageWorkloadType]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.StorageWorkloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DW = "DW"
        GENERAL = "GENERAL"
        OLTP = "OLTP"


    class azure.mgmt.sqlvirtualmachine.models.SystemData(Model):
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


    class azure.mgmt.sqlvirtualmachine.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingAdditionalProperties(Model):
        unhealthy_replica_info: UnhealthyReplicaInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                unhealthy_replica_info: Optional[UnhealthyReplicaInfo] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingScenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNHEALTHY_REPLICA = "UnhealthyReplica"


    class azure.mgmt.sqlvirtualmachine.models.TroubleshootingStatus(Model):
        end_time_utc: datetime
        last_trigger_time_utc: datetime
        properties: TroubleshootingAdditionalProperties
        root_cause: str
        start_time_utc: datetime
        troubleshooting_scenario: Union[str, TroubleshootingScenario]

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


    class azure.mgmt.sqlvirtualmachine.models.UnhealthyReplicaInfo(Model):
        availability_group_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_group_name: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.WsfcDomainCredentials(Model):
        cluster_bootstrap_account_password: str
        cluster_operator_account_password: str
        sql_service_account_password: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_bootstrap_account_password: Optional[str] = ..., 
                cluster_operator_account_password: Optional[str] = ..., 
                sql_service_account_password: Optional[str] = ..., 
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


    class azure.mgmt.sqlvirtualmachine.models.WsfcDomainProfile(Model):
        cluster_bootstrap_account: str
        cluster_operator_account: str
        cluster_subnet_type: Union[str, ClusterSubnetType]
        domain_fqdn: str
        file_share_witness_path: str
        ou_path: str
        sql_service_account: str
        storage_account_primary_key: str
        storage_account_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_bootstrap_account: Optional[str] = ..., 
                cluster_operator_account: Optional[str] = ..., 
                cluster_subnet_type: Optional[Union[str, ClusterSubnetType]] = ..., 
                domain_fqdn: Optional[str] = ..., 
                file_share_witness_path: Optional[str] = ..., 
                ou_path: Optional[str] = ..., 
                sql_service_account: Optional[str] = ..., 
                storage_account_primary_key: Optional[str] = ..., 
                storage_account_url: Optional[str] = ..., 
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


namespace azure.mgmt.sqlvirtualmachine.operations

    class azure.mgmt.sqlvirtualmachine.operations.AvailabilityGroupListenersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
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
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                availability_group_listener_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AvailabilityGroupListener: ...

        @distributed_trace
        def list_by_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AvailabilityGroupListener]: ...


    class azure.mgmt.sqlvirtualmachine.operations.Operations:

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


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachineGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachineGroup: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlVirtualMachineGroup]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlVirtualMachineGroup]: ...


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachineTroubleshootOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVmTroubleshooting]: ...


    class azure.mgmt.sqlvirtualmachine.operations.SqlVirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_assessment(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
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
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlVirtualMachine]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                expand: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SqlVirtualMachine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlVirtualMachine]: ...

        @distributed_trace
        def list_by_sql_vm_group(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SqlVirtualMachine]: ...


```