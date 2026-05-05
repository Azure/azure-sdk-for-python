```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.computebulkactions

    class azure.mgmt.computebulkactions.ComputeBulkActionsMgmtClient: implements ContextManager 
        bulk_actions: BulkActionsOperations
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


namespace azure.mgmt.computebulkactions.aio

    class azure.mgmt.computebulkactions.aio.ComputeBulkActionsMgmtClient: implements AsyncContextManager 
        bulk_actions: BulkActionsOperations
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


namespace azure.mgmt.computebulkactions.aio.operations

    class azure.mgmt.computebulkactions.aio.operations.BulkActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedLaunchBulkInstancesOperation: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                location: str, 
                id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: CancelOperationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: ExecuteCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: ExecuteDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: ExecuteDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: ExecuteHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: ExecuteStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: GetOperationStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        async def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...


    class azure.mgmt.computebulkactions.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.computebulkactions.models

    class azure.mgmt.computebulkactions.models.AcceleratorManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        NVIDIA = "Nvidia"
        XILINX = "Xilinx"


    class azure.mgmt.computebulkactions.models.AcceleratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FPGA = "FPGA"
        GPU = "GPU"


    class azure.mgmt.computebulkactions.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computebulkactions.models.AdditionalCapabilities(_Model):
        hibernation_enabled: Optional[bool]
        ultra_ssd_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                hibernation_enabled: Optional[bool] = ..., 
                ultra_ssd_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.AdditionalUnattendContent(_Model):
        component_name: Optional[Literal["Microsoft-Windows-Shell-Setup"]]
        content: Optional[str]
        pass_name: Optional[Literal["OobeSystem"]]
        setting_name: Optional[Union[str, SettingNames]]

        @overload
        def __init__(
                self, 
                *, 
                component_name: Optional[Literal[Microsoft-Windows-Shell-Setup]] = ..., 
                content: Optional[str] = ..., 
                pass_name: Optional[Literal[OobeSystem]] = ..., 
                setting_name: Optional[Union[str, SettingNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.AllInstancesDown(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.AllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OPTIMIZED = "CapacityOptimized"
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.computebulkactions.models.ApiEntityReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ApiError(_Model):
        code: Optional[str]
        details: Optional[list[ApiErrorBase]]
        innererror: Optional[InnerError]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ApiErrorBase]] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ApiErrorBase(_Model):
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


    class azure.mgmt.computebulkactions.models.ApplicationProfile(_Model):
        gallery_applications: Optional[list[VMGalleryApplication]]

        @overload
        def __init__(
                self, 
                *, 
                gallery_applications: Optional[list[VMGalleryApplication]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ArchitectureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "ARM64"
        X64 = "X64"


    class azure.mgmt.computebulkactions.models.BootDiagnostics(_Model):
        enabled: Optional[bool]
        storage_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                storage_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CachingTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.computebulkactions.models.CancelOperationsRequest(_Model):
        correlationid: str
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CancelOperationsResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CapacityReservationProfile(_Model):
        capacity_reservation_group: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_group: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CapacityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM = "VM"
        V_CPU = "VCpu"


    class azure.mgmt.computebulkactions.models.ComputeProfile(_Model):
        compute_api_version: Optional[str]
        extensions: Optional[list[VirtualMachineExtension]]
        virtual_machine_profile: VirtualMachineProfile

        @overload
        def __init__(
                self, 
                *, 
                compute_api_version: Optional[str] = ..., 
                extensions: Optional[list[VirtualMachineExtension]] = ..., 
                virtual_machine_profile: VirtualMachineProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CpuManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        AMPERE = "Ampere"
        INTEL = "Intel"
        MICROSOFT = "Microsoft"


    class azure.mgmt.computebulkactions.models.CreateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computebulkactions.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        detach_option: Optional[Union[str, DiskDetachOptionTypes]]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        lun: int
        managed_disk: Optional[ManagedDiskParameters]
        name: Optional[str]
        source_resource: Optional[ApiEntityReference]
        to_be_detached: Optional[bool]
        vhd: Optional[VirtualHardDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                create_option: Union[str, DiskCreateOptionTypes], 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                detach_option: Optional[Union[str, DiskDetachOptionTypes]] = ..., 
                disk_size_gb: Optional[int] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                lun: int, 
                managed_disk: Optional[ManagedDiskParameters] = ..., 
                name: Optional[str] = ..., 
                source_resource: Optional[ApiEntityReference] = ..., 
                to_be_detached: Optional[bool] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DeadlineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE_BY = "CompleteBy"
        INITIATE_AT = "InitiateAt"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.DeallocateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DeleteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.computebulkactions.models.DeleteResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DiagnosticsProfile(_Model):
        boot_diagnostics: Optional[BootDiagnostics]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnostics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DiffDiskOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"


    class azure.mgmt.computebulkactions.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "CacheDisk"
        NVME_DISK = "NvmeDisk"
        RESOURCE_DISK = "ResourceDisk"


    class azure.mgmt.computebulkactions.models.DiffDiskSettings(_Model):
        option: Optional[Union[str, DiffDiskOptions]]
        placement: Optional[Union[str, DiffDiskPlacement]]

        @overload
        def __init__(
                self, 
                *, 
                option: Optional[Union[str, DiffDiskOptions]] = ..., 
                placement: Optional[Union[str, DiffDiskPlacement]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DiskControllerTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NV_ME = "NVMe"
        SCSI = "SCSI"


    class azure.mgmt.computebulkactions.models.DiskCreateOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "Attach"
        COPY = "Copy"
        EMPTY = "Empty"
        FROM_IMAGE = "FromImage"
        RESTORE = "Restore"


    class azure.mgmt.computebulkactions.models.DiskDeleteOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.computebulkactions.models.DiskDetachOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE_DETACH = "ForceDetach"


    class azure.mgmt.computebulkactions.models.DiskEncryptionSetParameters(SubResource):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DiskEncryptionSettings(_Model):
        disk_encryption_key: Optional[KeyVaultSecretReference]
        enabled: Optional[bool]
        key_encryption_key: Optional[KeyVaultKeyReference]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_key: Optional[KeyVaultSecretReference] = ..., 
                enabled: Optional[bool] = ..., 
                key_encryption_key: Optional[KeyVaultKeyReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.DomainNameLabelScopeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.computebulkactions.models.EncryptionIdentity(_Model):
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computebulkactions.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computebulkactions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.EventGridAndResourceGraph(_Model):
        enable: Optional[bool]
        scheduled_events_api_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                scheduled_events_api_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.EvictionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.computebulkactions.models.ExecuteCreateRequest(_Model):
        correlationid: Optional[str]
        execution_parameters: ExecutionParameters
        resource_config_parameters: ResourceProvisionPayload

        @overload
        def __init__(
                self, 
                *, 
                correlationid: Optional[str] = ..., 
                execution_parameters: ExecutionParameters, 
                resource_config_parameters: ResourceProvisionPayload
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteDeallocateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteDeleteRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        force_deletion: Optional[bool]
        resources: Optional[Resources]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                force_deletion: Optional[bool] = ..., 
                resources: Optional[Resources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteHibernateRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecuteStartRequest(_Model):
        correlationid: str
        execution_parameters: ExecutionParameters
        resources: Optional[Resources]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                execution_parameters: ExecutionParameters, 
                resources: Optional[Resources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ExecutionParameters(_Model):
        optimization_preference: Optional[Union[str, OptimizationPreference]]
        retry_policy: Optional[RetryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                optimization_preference: Optional[Union[str, OptimizationPreference]] = ..., 
                retry_policy: Optional[RetryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.GetOperationStatusRequest(_Model):
        correlationid: str
        operation_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                correlationid: str, 
                operation_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.GetOperationStatusResponse(_Model):
        results: list[ResourceOperation]

        @overload
        def __init__(
                self, 
                *, 
                results: list[ResourceOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.HibernateResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.HostEndpointSettings(_Model):
        in_vm_access_control_profile_reference_id: Optional[str]
        mode: Optional[Union[str, Modes]]

        @overload
        def __init__(
                self, 
                *, 
                in_vm_access_control_profile_reference_id: Optional[str] = ..., 
                mode: Optional[Union[str, Modes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.HyperVGeneration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN1 = "Gen1"
        GEN2 = "Gen2"


    class azure.mgmt.computebulkactions.models.IPVersions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.computebulkactions.models.ImageReference(SubResource):
        community_gallery_image_id: Optional[str]
        id: str
        offer: Optional[str]
        publisher: Optional[str]
        shared_gallery_image_id: Optional[str]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                shared_gallery_image_id: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.InnerError(_Model):
        error_detail: Optional[str]
        exception_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_detail: Optional[str] = ..., 
                exception_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.KeyVaultKeyReference(_Model):
        key_url: str
        source_vault: SubResource

        @overload
        def __init__(
                self, 
                *, 
                key_url: str, 
                source_vault: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.KeyVaultSecretReference(_Model):
        secret_url: str
        source_vault: SubResource

        @overload
        def __init__(
                self, 
                *, 
                secret_url: str, 
                source_vault: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.LaunchBulkInstancesOperationProperties(_Model):
        capacity: int
        capacity_type: Optional[Union[str, CapacityType]]
        compute_profile: ComputeProfile
        priority_profile: PriorityProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retry_policy: Optional[RetryPolicy]
        vm_attributes: Optional[VMAttributes]
        vm_sizes_profile: Optional[list[VmSizeProfile]]
        zone_allocation_policy: Optional[ZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                capacity_type: Optional[Union[str, CapacityType]] = ..., 
                compute_profile: ComputeProfile, 
                priority_profile: PriorityProfile, 
                retry_policy: Optional[RetryPolicy] = ..., 
                vm_attributes: Optional[VMAttributes] = ..., 
                vm_sizes_profile: Optional[list[VmSizeProfile]] = ..., 
                zone_allocation_policy: Optional[ZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.LinuxConfiguration(_Model):
        disable_password_authentication: Optional[bool]
        enable_vm_agent_platform_updates: Optional[bool]
        patch_settings: Optional[LinuxPatchSettings]
        provision_vm_agent: Optional[bool]
        ssh: Optional[SshConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                disable_password_authentication: Optional[bool] = ..., 
                enable_vm_agent_platform_updates: Optional[bool] = ..., 
                patch_settings: Optional[LinuxPatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.LinuxPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computebulkactions.models.LinuxPatchSettings(_Model):
        assessment_mode: Optional[Union[str, LinuxPatchAssessmentMode]]
        automatic_by_platform_settings: Optional[LinuxVMGuestPatchAutomaticByPlatformSettings]
        patch_mode: Optional[Union[str, LinuxVMGuestPatchMode]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_mode: Optional[Union[str, LinuxPatchAssessmentMode]] = ..., 
                automatic_by_platform_settings: Optional[LinuxVMGuestPatchAutomaticByPlatformSettings] = ..., 
                patch_mode: Optional[Union[str, LinuxVMGuestPatchMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.LinuxVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.LinuxVMGuestPatchAutomaticByPlatformSettings(_Model):
        bypass_platform_safety_checks_on_user_schedule: Optional[bool]
        reboot_setting: Optional[Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]]

        @overload
        def __init__(
                self, 
                *, 
                bypass_platform_safety_checks_on_user_schedule: Optional[bool] = ..., 
                reboot_setting: Optional[Union[str, LinuxVMGuestPatchAutomaticByPlatformRebootSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.LinuxVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computebulkactions.models.LocalStorageDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        SSD = "SSD"


    class azure.mgmt.computebulkactions.models.LocationBasedLaunchBulkInstancesOperation(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        plan: Optional[Plan]
        properties: Optional[LaunchBulkInstancesOperationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[LaunchBulkInstancesOperationProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ManagedDiskParameters(SubResource):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        id: str
        security_profile: Optional[VMDiskSecurityProfile]
        storage_account_type: Optional[Union[str, StorageAccountTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                id: Optional[str] = ..., 
                security_profile: Optional[VMDiskSecurityProfile] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.computebulkactions.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.computebulkactions.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.mgmt.computebulkactions.models.Modes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DISABLED = "Disabled"
        ENFORCE = "Enforce"


    class azure.mgmt.computebulkactions.models.NetworkApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUM_2020_11_01 = "2020-11-01"
        ENUM_2022_11_01 = "2022-11-01"


    class azure.mgmt.computebulkactions.models.NetworkInterfaceAuxiliaryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCELERATED_CONNECTIONS = "AcceleratedConnections"
        FLOATING = "Floating"
        NONE = "None"


    class azure.mgmt.computebulkactions.models.NetworkInterfaceAuxiliarySku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A1 = "A1"
        A2 = "A2"
        A4 = "A4"
        A8 = "A8"
        NONE = "None"


    class azure.mgmt.computebulkactions.models.NetworkInterfaceReference(SubResource):
        id: str
        properties: Optional[NetworkInterfaceReferenceProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[NetworkInterfaceReferenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.NetworkInterfaceReferenceProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        primary: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.NetworkProfile(_Model):
        network_api_version: Optional[Union[str, NetworkApiVersion]]
        network_interface_configurations: Optional[list[VirtualMachineNetworkInterfaceConfiguration]]
        network_interfaces: Optional[list[NetworkInterfaceReference]]

        @overload
        def __init__(
                self, 
                *, 
                network_api_version: Optional[Union[str, NetworkApiVersion]] = ..., 
                network_interface_configurations: Optional[list[VirtualMachineNetworkInterfaceConfiguration]] = ..., 
                network_interfaces: Optional[list[NetworkInterfaceReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.OSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        diff_disk_settings: Optional[DiffDiskSettings]
        disk_size_gb: Optional[int]
        encryption_settings: Optional[DiskEncryptionSettings]
        image: Optional[VirtualHardDisk]
        managed_disk: Optional[ManagedDiskParameters]
        name: Optional[str]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        vhd: Optional[VirtualHardDisk]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                create_option: Union[str, DiskCreateOptionTypes], 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                diff_disk_settings: Optional[DiffDiskSettings] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption_settings: Optional[DiskEncryptionSettings] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                managed_disk: Optional[ManagedDiskParameters] = ..., 
                name: Optional[str] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.OSImageNotificationProfile(_Model):
        enable: Optional[bool]
        not_before_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                not_before_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.OSProfile(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        allow_extension_operations: Optional[bool]
        computer_name: Optional[str]
        custom_data: Optional[str]
        linux_configuration: Optional[LinuxConfiguration]
        require_guest_provision_signal: Optional[bool]
        secrets: Optional[list[VaultSecretGroup]]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                allow_extension_operations: Optional[bool] = ..., 
                computer_name: Optional[str] = ..., 
                custom_data: Optional[str] = ..., 
                linux_configuration: Optional[LinuxConfiguration] = ..., 
                require_guest_provision_signal: Optional[bool] = ..., 
                secrets: Optional[list[VaultSecretGroup]] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.computebulkactions.models.Operation(_Model):
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


    class azure.mgmt.computebulkactions.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computebulkactions.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        CANCELLED = "Cancelled"
        EXECUTING = "Executing"
        FAILED = "Failed"
        PENDING_EXECUTION = "PendingExecution"
        PENDING_SCHEDULING = "PendingScheduling"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.OptimizationPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        COST = "Cost"
        COST_AVAILABILITY_BALANCED = "CostAvailabilityBalanced"


    class azure.mgmt.computebulkactions.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computebulkactions.models.PatchSettings(_Model):
        assessment_mode: Optional[Union[str, WindowsPatchAssessmentMode]]
        automatic_by_platform_settings: Optional[WindowsVMGuestPatchAutomaticByPlatformSettings]
        enable_hotpatching: Optional[bool]
        patch_mode: Optional[Union[str, WindowsVMGuestPatchMode]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_mode: Optional[Union[str, WindowsPatchAssessmentMode]] = ..., 
                automatic_by_platform_settings: Optional[WindowsVMGuestPatchAutomaticByPlatformSettings] = ..., 
                enable_hotpatching: Optional[bool] = ..., 
                patch_mode: Optional[Union[str, WindowsVMGuestPatchMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.PriorityProfile(_Model):
        allocation_strategy: Optional[Union[str, AllocationStrategy]]
        eviction_policy: Optional[Union[str, EvictionPolicy]]
        max_price_per_vm: Optional[float]
        type: Optional[Union[str, VirtualMachineType]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, AllocationStrategy]] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                max_price_per_vm: Optional[float] = ..., 
                type: Optional[Union[str, VirtualMachineType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ProtocolTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.computebulkactions.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computebulkactions.models.ProxyAgentSettings(_Model):
        add_proxy_agent_extension: Optional[bool]
        enabled: Optional[bool]
        imds: Optional[HostEndpointSettings]
        key_incarnation_id: Optional[int]
        mode: Optional[Union[str, Mode]]
        wire_server: Optional[HostEndpointSettings]

        @overload
        def __init__(
                self, 
                *, 
                add_proxy_agent_extension: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                imds: Optional[HostEndpointSettings] = ..., 
                key_incarnation_id: Optional[int] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
                wire_server: Optional[HostEndpointSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.computebulkactions.models.PublicIPAddressSku(_Model):
        name: Optional[Union[str, PublicIPAddressSkuName]]
        tier: Optional[Union[str, PublicIPAddressSkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, PublicIPAddressSkuName]] = ..., 
                tier: Optional[Union[str, PublicIPAddressSkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.PublicIPAddressSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.computebulkactions.models.PublicIPAddressSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBALEnum = "Global"
        REGIONAL = "Regional"


    class azure.mgmt.computebulkactions.models.PublicIPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.computebulkactions.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computebulkactions.models.ResourceOperation(_Model):
        error_code: Optional[str]
        error_details: Optional[str]
        operation: Optional[ResourceOperationDetails]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_details: Optional[str] = ..., 
                operation: Optional[ResourceOperationDetails] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ResourceOperationDetails(_Model):
        completed_at: Optional[datetime]
        deadline: Optional[datetime]
        deadline_type: Optional[Union[str, DeadlineType]]
        op_type: Optional[Union[str, ResourceOperationType]]
        operation_id: str
        resource_id: Optional[str]
        resource_operation_error: Optional[ResourceOperationError]
        retry_policy: Optional[RetryPolicy]
        state: Optional[Union[str, OperationState]]
        subscription_id: Optional[str]
        timezone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                deadline: Optional[datetime] = ..., 
                deadline_type: Optional[Union[str, DeadlineType]] = ..., 
                op_type: Optional[Union[str, ResourceOperationType]] = ..., 
                operation_id: str, 
                resource_id: Optional[str] = ..., 
                resource_operation_error: Optional[ResourceOperationError] = ..., 
                retry_policy: Optional[RetryPolicy] = ..., 
                state: Optional[Union[str, OperationState]] = ..., 
                subscription_id: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ResourceOperationError(_Model):
        error_code: str
        error_details: str

        @overload
        def __init__(
                self, 
                *, 
                error_code: str, 
                error_details: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ResourceOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"
        HIBERNATE = "Hibernate"
        START = "Start"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.ResourceProvisionPayload(_Model):
        base_profile: Optional[dict[str, Any]]
        resource_count: int
        resource_overrides: Optional[list[dict[str, Any]]]
        resource_prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                base_profile: Optional[dict[str, Any]] = ..., 
                resource_count: int, 
                resource_overrides: Optional[list[dict[str, Any]]] = ..., 
                resource_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.Resources(_Model):
        ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.RetryPolicy(_Model):
        retry_count: Optional[int]
        retry_window_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                retry_count: Optional[int] = ..., 
                retry_window_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ScheduledEventsAdditionalPublishingTargets(_Model):
        event_grid_and_resource_graph: Optional[EventGridAndResourceGraph]

        @overload
        def __init__(
                self, 
                *, 
                event_grid_and_resource_graph: Optional[EventGridAndResourceGraph] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ScheduledEventsPolicy(_Model):
        all_instances_down: Optional[AllInstancesDown]
        scheduled_events_additional_publishing_targets: Optional[ScheduledEventsAdditionalPublishingTargets]
        user_initiated_reboot: Optional[UserInitiatedReboot]
        user_initiated_redeploy: Optional[UserInitiatedRedeploy]

        @overload
        def __init__(
                self, 
                *, 
                all_instances_down: Optional[AllInstancesDown] = ..., 
                scheduled_events_additional_publishing_targets: Optional[ScheduledEventsAdditionalPublishingTargets] = ..., 
                user_initiated_reboot: Optional[UserInitiatedReboot] = ..., 
                user_initiated_redeploy: Optional[UserInitiatedRedeploy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ScheduledEventsProfile(_Model):
        os_image_notification_profile: Optional[OSImageNotificationProfile]
        terminate_notification_profile: Optional[TerminateNotificationProfile]

        @overload
        def __init__(
                self, 
                *, 
                os_image_notification_profile: Optional[OSImageNotificationProfile] = ..., 
                terminate_notification_profile: Optional[TerminateNotificationProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.computebulkactions.models.SecurityProfile(_Model):
        encryption_at_host: Optional[bool]
        encryption_identity: Optional[EncryptionIdentity]
        proxy_agent_settings: Optional[ProxyAgentSettings]
        security_type: Optional[Union[str, SecurityTypes]]
        uefi_settings: Optional[UefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                encryption_at_host: Optional[bool] = ..., 
                encryption_identity: Optional[EncryptionIdentity] = ..., 
                proxy_agent_settings: Optional[ProxyAgentSettings] = ..., 
                security_type: Optional[Union[str, SecurityTypes]] = ..., 
                uefi_settings: Optional[UefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.computebulkactions.models.SettingNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_LOGON = "AutoLogon"
        FIRST_LOGON_COMMANDS = "FirstLogonCommands"


    class azure.mgmt.computebulkactions.models.SshConfiguration(_Model):
        public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.SshPublicKey(_Model):
        key_data: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_data: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.StartResourceOperationResponse(_Model):
        description: str
        location: str
        results: Optional[list[ResourceOperation]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                location: str, 
                results: Optional[list[ResourceOperation]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.StorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.computebulkactions.models.StorageProfile(_Model):
        data_disks: Optional[list[DataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[OSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[DataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[OSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.SystemData(_Model):
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


    class azure.mgmt.computebulkactions.models.TerminateNotificationProfile(_Model):
        enable: Optional[bool]
        not_before_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable: Optional[bool] = ..., 
                not_before_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.UefiSettings(_Model):
        secure_boot_enabled: Optional[bool]
        v_tpm_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secure_boot_enabled: Optional[bool] = ..., 
                v_tpm_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.computebulkactions.models.UserInitiatedReboot(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.UserInitiatedRedeploy(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMAttributeMinMaxDouble(_Model):
        max: Optional[float]
        min: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max: Optional[float] = ..., 
                min: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMAttributeMinMaxInteger(_Model):
        max: Optional[int]
        min: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max: Optional[int] = ..., 
                min: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMAttributeSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"
        REQUIRED = "Required"


    class azure.mgmt.computebulkactions.models.VMAttributes(_Model):
        accelerator_count: Optional[VMAttributeMinMaxInteger]
        accelerator_manufacturers: Optional[list[Union[str, AcceleratorManufacturer]]]
        accelerator_support: Optional[Union[str, VMAttributeSupport]]
        accelerator_types: Optional[list[Union[str, AcceleratorType]]]
        allowed_vm_sizes: Optional[list[str]]
        architecture_types: list[Union[str, ArchitectureType]]
        burstable_support: Optional[Union[str, VMAttributeSupport]]
        cpu_manufacturers: Optional[list[Union[str, CpuManufacturer]]]
        data_disk_count: Optional[VMAttributeMinMaxInteger]
        excluded_vm_sizes: Optional[list[str]]
        hyper_v_generations: Optional[list[Union[str, HyperVGeneration]]]
        local_storage_disk_types: Optional[list[Union[str, LocalStorageDiskType]]]
        local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble]
        local_storage_support: Optional[Union[str, VMAttributeSupport]]
        memory_in_gi_b: VMAttributeMinMaxDouble
        memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble]
        network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble]
        network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_support: Optional[Union[str, VMAttributeSupport]]
        v_cpu_count: VMAttributeMinMaxInteger
        vm_categories: Optional[list[Union[str, VMCategory]]]

        @overload
        def __init__(
                self, 
                *, 
                accelerator_count: Optional[VMAttributeMinMaxInteger] = ..., 
                accelerator_manufacturers: Optional[list[Union[str, AcceleratorManufacturer]]] = ..., 
                accelerator_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                accelerator_types: Optional[list[Union[str, AcceleratorType]]] = ..., 
                allowed_vm_sizes: Optional[list[str]] = ..., 
                architecture_types: list[Union[str, ArchitectureType]], 
                burstable_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                cpu_manufacturers: Optional[list[Union[str, CpuManufacturer]]] = ..., 
                data_disk_count: Optional[VMAttributeMinMaxInteger] = ..., 
                excluded_vm_sizes: Optional[list[str]] = ..., 
                hyper_v_generations: Optional[list[Union[str, HyperVGeneration]]] = ..., 
                local_storage_disk_types: Optional[list[Union[str, LocalStorageDiskType]]] = ..., 
                local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble] = ..., 
                local_storage_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                memory_in_gi_b: VMAttributeMinMaxDouble, 
                memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble] = ..., 
                network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble] = ..., 
                network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                v_cpu_count: VMAttributeMinMaxInteger, 
                vm_categories: Optional[list[Union[str, VMCategory]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_OPTIMIZED = "ComputeOptimized"
        FPGA_ACCELERATED = "FpgaAccelerated"
        GENERAL_PURPOSE = "GeneralPurpose"
        GPU_ACCELERATED = "GpuAccelerated"
        HIGH_PERFORMANCE_COMPUTE = "HighPerformanceCompute"
        MEMORY_OPTIMIZED = "MemoryOptimized"
        STORAGE_OPTIMIZED = "StorageOptimized"


    class azure.mgmt.computebulkactions.models.VMDiskSecurityProfile(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                security_encryption_type: Optional[Union[str, SecurityEncryptionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMGalleryApplication(_Model):
        configuration_reference: Optional[str]
        enable_automatic_upgrade: Optional[bool]
        order: Optional[int]
        package_reference_id: str
        tags: Optional[str]
        treat_failure_as_deployment_failure: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                configuration_reference: Optional[str] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                order: Optional[int] = ..., 
                package_reference_id: str, 
                tags: Optional[str] = ..., 
                treat_failure_as_deployment_failure: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VMOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLING = "Cancelling"
        CANCEL_FAILED_STATUS_UNKNOWN = "CancelFailedStatusUnknown"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computebulkactions.models.VaultCertificate(_Model):
        certificate_store: Optional[str]
        certificate_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_store: Optional[str] = ..., 
                certificate_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VaultSecretGroup(_Model):
        source_vault: Optional[SubResource]
        vault_certificates: Optional[list[VaultCertificate]]

        @overload
        def __init__(
                self, 
                *, 
                source_vault: Optional[SubResource] = ..., 
                vault_certificates: Optional[list[VaultCertificate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualHardDisk(_Model):
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachine(_Model):
        error: Optional[ApiError]
        id: str
        name: str
        operation_status: Union[str, VMOperationStatus]
        type: Optional[str]


    class azure.mgmt.computebulkactions.models.VirtualMachineExtension(_Model):
        name: str
        properties: VirtualMachineExtensionProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: VirtualMachineExtensionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[dict[str, Any]]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        provision_after_extensions: Optional[list[str]]
        publisher: Optional[str]
        settings: Optional[dict[str, Any]]
        suppress_failures: Optional[bool]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                force_update_tag: Optional[str] = ..., 
                protected_settings: Optional[dict[str, Any]] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[dict[str, Any]] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineIpTag(_Model):
        ip_tag_type: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ip_tag_type: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineNetworkInterfaceConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceConfigurationProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineNetworkInterfaceConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineNetworkInterfaceConfigurationProperties(_Model):
        auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]]
        auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]]
        delete_option: Optional[Union[str, DeleteOptions]]
        disable_tcp_state_tracking: Optional[bool]
        dns_settings: Optional[VirtualMachineNetworkInterfaceDnsSettingsConfiguration]
        dscp_configuration: Optional[SubResource]
        enable_accelerated_networking: Optional[bool]
        enable_fpga: Optional[bool]
        enable_ip_forwarding: Optional[bool]
        ip_configurations: list[VirtualMachineNetworkInterfaceIPConfiguration]
        network_security_group: Optional[SubResource]
        primary: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]] = ..., 
                auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]] = ..., 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                disable_tcp_state_tracking: Optional[bool] = ..., 
                dns_settings: Optional[VirtualMachineNetworkInterfaceDnsSettingsConfiguration] = ..., 
                dscp_configuration: Optional[SubResource] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                enable_fpga: Optional[bool] = ..., 
                enable_ip_forwarding: Optional[bool] = ..., 
                ip_configurations: list[VirtualMachineNetworkInterfaceIPConfiguration], 
                network_security_group: Optional[SubResource] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineNetworkInterfaceDnsSettingsConfiguration(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineNetworkInterfaceIPConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineNetworkInterfaceIPConfigurationProperties(_Model):
        application_gateway_backend_address_pools: Optional[list[SubResource]]
        application_security_groups: Optional[list[SubResource]]
        load_balancer_backend_address_pools: Optional[list[SubResource]]
        primary: Optional[bool]
        private_ip_address_version: Optional[Union[str, IPVersions]]
        public_ip_address_configuration: Optional[VirtualMachinePublicIPAddressConfiguration]
        subnet: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[list[SubResource]] = ..., 
                application_security_groups: Optional[list[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[list[SubResource]] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address_version: Optional[Union[str, IPVersions]] = ..., 
                public_ip_address_configuration: Optional[VirtualMachinePublicIPAddressConfiguration] = ..., 
                subnet: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineProfile(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        application_profile: Optional[ApplicationProfile]
        capacity_reservation: Optional[CapacityReservationProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        extensions_time_budget: Optional[str]
        license_type: Optional[str]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OSProfile]
        scheduled_events_policy: Optional[ScheduledEventsPolicy]
        scheduled_events_profile: Optional[ScheduledEventsProfile]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[StorageProfile]
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                application_profile: Optional[ApplicationProfile] = ..., 
                capacity_reservation: Optional[CapacityReservationProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                extensions_time_budget: Optional[str] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                scheduled_events_policy: Optional[ScheduledEventsPolicy] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
                user_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachinePublicIPAddressConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachinePublicIPAddressConfigurationProperties]
        sku: Optional[PublicIPAddressSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachinePublicIPAddressConfigurationProperties] = ..., 
                sku: Optional[PublicIPAddressSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachinePublicIPAddressConfigurationProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        dns_settings: Optional[VirtualMachinePublicIPAddressDnsSettingsConfiguration]
        idle_timeout_in_minutes: Optional[int]
        ip_tags: Optional[list[VirtualMachineIpTag]]
        public_ip_address_version: Optional[Union[str, IPVersions]]
        public_ip_allocation_method: Optional[Union[str, PublicIPAllocationMethod]]
        public_ip_prefix: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                dns_settings: Optional[VirtualMachinePublicIPAddressDnsSettingsConfiguration] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                ip_tags: Optional[list[VirtualMachineIpTag]] = ..., 
                public_ip_address_version: Optional[Union[str, IPVersions]] = ..., 
                public_ip_allocation_method: Optional[Union[str, PublicIPAllocationMethod]] = ..., 
                public_ip_prefix: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachinePublicIPAddressDnsSettingsConfiguration(_Model):
        domain_name_label: str
        domain_name_label_scope: Optional[Union[str, DomainNameLabelScopeTypes]]

        @overload
        def __init__(
                self, 
                *, 
                domain_name_label: str, 
                domain_name_label_scope: Optional[Union[str, DomainNameLabelScopeTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.VirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.computebulkactions.models.VmSizeProfile(_Model):
        name: str
        rank: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                rank: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.WinRMConfiguration(_Model):
        listeners: Optional[list[WinRMListener]]

        @overload
        def __init__(
                self, 
                *, 
                listeners: Optional[list[WinRMListener]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.WinRMListener(_Model):
        certificate_url: Optional[str]
        protocol: Optional[Union[str, ProtocolTypes]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_url: Optional[str] = ..., 
                protocol: Optional[Union[str, ProtocolTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.WindowsConfiguration(_Model):
        additional_unattend_content: Optional[list[AdditionalUnattendContent]]
        enable_automatic_updates: Optional[bool]
        patch_settings: Optional[PatchSettings]
        provision_vm_agent: Optional[bool]
        time_zone: Optional[str]
        win_rm: Optional[WinRMConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                additional_unattend_content: Optional[list[AdditionalUnattendContent]] = ..., 
                enable_automatic_updates: Optional[bool] = ..., 
                patch_settings: Optional[PatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                time_zone: Optional[str] = ..., 
                win_rm: Optional[WinRMConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.WindowsPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computebulkactions.models.WindowsVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.computebulkactions.models.WindowsVMGuestPatchAutomaticByPlatformSettings(_Model):
        bypass_platform_safety_checks_on_user_schedule: Optional[bool]
        reboot_setting: Optional[Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]]

        @overload
        def __init__(
                self, 
                *, 
                bypass_platform_safety_checks_on_user_schedule: Optional[bool] = ..., 
                reboot_setting: Optional[Union[str, WindowsVMGuestPatchAutomaticByPlatformRebootSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.WindowsVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_OS = "AutomaticByOS"
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        MANUAL = "Manual"


    class azure.mgmt.computebulkactions.models.ZoneAllocationPolicy(_Model):
        distribution_strategy: Union[str, ZoneDistributionStrategy]
        zone_preferences: Optional[list[ZonePreference]]

        @overload
        def __init__(
                self, 
                *, 
                distribution_strategy: Union[str, ZoneDistributionStrategy], 
                zone_preferences: Optional[list[ZonePreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computebulkactions.models.ZoneDistributionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT_BALANCED = "BestEffortBalanced"
        BEST_EFFORT_SINGLE_ZONE = "BestEffortSingleZone"
        PRIORITIZED = "Prioritized"
        STRICT_BALANCED = "StrictBalanced"


    class azure.mgmt.computebulkactions.models.ZonePreference(_Model):
        rank: Optional[int]
        zone: str

        @overload
        def __init__(
                self, 
                *, 
                rank: Optional[int] = ..., 
                zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.computebulkactions.operations

    class azure.mgmt.computebulkactions.operations.BulkActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: LocationBasedLaunchBulkInstancesOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                delete_instances: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> LocationBasedLaunchBulkInstancesOperation: ...

        @distributed_trace
        def get_operation_status(
                self, 
                location: str, 
                id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[LocationBasedLaunchBulkInstancesOperation]: ...

        @distributed_trace
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                location: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: CancelOperationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_cancel_operations(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CancelOperationsResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: ExecuteCreateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_create(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: ExecuteDeallocateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_deallocate(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeallocateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: ExecuteDeleteRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_delete(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: ExecuteHibernateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_hibernate(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HibernateResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: ExecuteStartRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_execute_start(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StartResourceOperationResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: GetOperationStatusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...

        @overload
        def virtual_machines_get_operation_status(
                self, 
                location: str, 
                request_body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetOperationStatusResponse: ...


    class azure.mgmt.computebulkactions.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```