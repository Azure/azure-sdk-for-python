```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.baremetalinfrastructure

    class azure.mgmt.baremetalinfrastructure.BareMetalInfrastructureClient: implements ContextManager 
        azure_bare_metal_instances: AzureBareMetalInstancesOperations
        azure_bare_metal_storage_instances: AzureBareMetalStorageInstancesOperations
        operations: Operations

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


namespace azure.mgmt.baremetalinfrastructure.aio

    class azure.mgmt.baremetalinfrastructure.aio.BareMetalInfrastructureClient: implements AsyncContextManager 
        azure_bare_metal_instances: AzureBareMetalInstancesOperations
        azure_bare_metal_storage_instances: AzureBareMetalStorageInstancesOperations
        operations: Operations

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


namespace azure.mgmt.baremetalinfrastructure.aio.operations

    class azure.mgmt.baremetalinfrastructure.aio.operations.AzureBareMetalInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                force_parameter: Optional[ForceState] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                force_parameter: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_shutdown(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatus]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureBareMetalInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureBareMetalInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                tags_parameter: Tags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                tags_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...


    class azure.mgmt.baremetalinfrastructure.aio.operations.AzureBareMetalStorageInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                request_body_parameters: AzureBareMetalStorageInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                request_body_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureBareMetalStorageInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[AzureBareMetalStorageInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                tags_parameter: Tags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                tags_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...


    class azure.mgmt.baremetalinfrastructure.aio.operations.Operations:

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


namespace azure.mgmt.baremetalinfrastructure.models

    class azure.mgmt.baremetalinfrastructure.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.baremetalinfrastructure.models.AsyncOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXECUTING = "Executing"
        FAILED = "Failed"
        REQUESTING = "Requesting"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalHardwareTypeNamesEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CISCO_UCS = "Cisco_UCS"
        HPE = "HPE"
        SDFLEX = "SDFLEX"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalInstance(TrackedResource):
        azure_bare_metal_instance_id: str
        hardware_profile: HardwareProfile
        hw_revision: str
        id: str
        location: str
        name: str
        network_profile: NetworkProfile
        os_profile: OSProfile
        partner_node_id: str
        power_state: Union[str, AzureBareMetalInstancePowerStateEnum]
        provisioning_state: Union[str, AzureBareMetalProvisioningStatesEnum]
        proximity_placement_group: str
        storage_profile: StorageProfile
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hardware_profile: Optional[HardwareProfile] = ..., 
                location: str, 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                partner_node_id: Optional[str] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalInstanceForcePowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalInstancePowerStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTARTING = "restarting"
        STARTED = "started"
        STARTING = "starting"
        STOPPED = "stopped"
        STOPPING = "stopping"
        UNKNOWN = "unknown"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalInstanceSizeNamesEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        S112 = "S112"
        S144 = "S144"
        S144_M = "S144m"
        S192 = "S192"
        S192_M = "S192m"
        S192_XM = "S192xm"
        S224 = "S224"
        S224_M = "S224m"
        S224_OM = "S224om"
        S224_OO = "S224oo"
        S224_OOM = "S224oom"
        S224_OOO = "S224ooo"
        S384 = "S384"
        S384_M = "S384m"
        S384_XM = "S384xm"
        S384_XXM = "S384xxm"
        S448 = "S448"
        S448_M = "S448m"
        S448_OM = "S448om"
        S448_OO = "S448oo"
        S448_OOM = "S448oom"
        S448_OOO = "S448ooo"
        S448_SE = "S448se"
        S576_M = "S576m"
        S576_XM = "S576xm"
        S672 = "S672"
        S672_M = "S672m"
        S672_OM = "S672om"
        S672_OO = "S672oo"
        S672_OOM = "S672oom"
        S672_OOO = "S672ooo"
        S72 = "S72"
        S72_M = "S72m"
        S768 = "S768"
        S768_M = "S768m"
        S768_XM = "S768xm"
        S896 = "S896"
        S896_M = "S896m"
        S896_OM = "S896om"
        S896_OO = "S896oo"
        S896_OOM = "S896oom"
        S896_OOO = "S896ooo"
        S96 = "S96"
        S960_M = "S960m"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalInstancesListResult(Model):
        next_link: str
        value: list[AzureBareMetalInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureBareMetalInstance]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalProvisioningStatesEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalStorageInstance(TrackedResource):
        azure_bare_metal_storage_instance_unique_identifier: str
        id: str
        location: str
        name: str
        storage_properties: StorageProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_bare_metal_storage_instance_unique_identifier: Optional[str] = ..., 
                location: str, 
                storage_properties: Optional[StorageProperties] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.AzureBareMetalStorageInstancesListResult(Model):
        next_link: str
        value: list[AzureBareMetalStorageInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AzureBareMetalStorageInstance]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.baremetalinfrastructure.models.Disk(Model):
        disk_size_gb: int
        lun: int
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_size_gb: Optional[int] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.ErrorDetail(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.ErrorResponse(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.ForceState(Model):
        force_state: Union[str, AzureBareMetalInstanceForcePowerState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                force_state: Optional[Union[str, AzureBareMetalInstanceForcePowerState]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.HardwareProfile(Model):
        azure_bare_metal_instance_size: Union[str, AzureBareMetalInstanceSizeNamesEnum]
        hardware_type: Union[str, AzureBareMetalHardwareTypeNamesEnum]

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


    class azure.mgmt.baremetalinfrastructure.models.NetworkInterface(Model):
        ip_address: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address: Optional[str] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.NetworkProfile(Model):
        circuit_id: str
        network_interfaces: list[NetworkInterface]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_interfaces: Optional[List[NetworkInterface]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.OSProfile(Model):
        computer_name: str
        os_type: str
        ssh_public_key: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                computer_name: Optional[str] = ..., 
                ssh_public_key: Optional[str] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.OperationDisplay(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.OperationListResult(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.OperationStatus(Model):
        error: OperationStatusError
        name: str
        start_time: str
        status: Union[str, AsyncOperationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[OperationStatusError] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[str] = ..., 
                status: Optional[Union[str, AsyncOperationStatus]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.OperationStatusError(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.baremetalinfrastructure.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.baremetalinfrastructure.models.Resource(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.StorageBillingProperties(Model):
        azure_bare_metal_storage_instance_size: str
        billing_mode: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_bare_metal_storage_instance_size: Optional[str] = ..., 
                billing_mode: Optional[str] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.StorageProfile(Model):
        nfs_ip_address: str
        os_disks: list[Disk]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                os_disks: Optional[List[Disk]] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.StorageProperties(Model):
        generation: str
        hardware_type: str
        offering_type: str
        provisioning_state: Union[str, ProvisioningState]
        storage_billing_properties: StorageBillingProperties
        storage_type: str
        workload_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                generation: Optional[str] = ..., 
                hardware_type: Optional[str] = ..., 
                offering_type: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                storage_billing_properties: Optional[StorageBillingProperties] = ..., 
                storage_type: Optional[str] = ..., 
                workload_type: Optional[str] = ..., 
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


    class azure.mgmt.baremetalinfrastructure.models.SystemData(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.Tags(Model):
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


    class azure.mgmt.baremetalinfrastructure.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
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


namespace azure.mgmt.baremetalinfrastructure.operations

    class azure.mgmt.baremetalinfrastructure.operations.AzureBareMetalInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                force_parameter: Optional[ForceState] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                force_parameter: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_shutdown(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatus]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureBareMetalInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureBareMetalInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                tags_parameter: Tags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_instance_name: str, 
                tags_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalInstance: ...


    class azure.mgmt.baremetalinfrastructure.operations.AzureBareMetalStorageInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                request_body_parameters: AzureBareMetalStorageInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                request_body_parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureBareMetalStorageInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[AzureBareMetalStorageInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                tags_parameter: Tags, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                azure_bare_metal_storage_instance_name: str, 
                tags_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureBareMetalStorageInstance: ...


    class azure.mgmt.baremetalinfrastructure.operations.Operations:

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