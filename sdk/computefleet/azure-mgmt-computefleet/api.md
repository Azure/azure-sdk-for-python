```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.computefleet

    class azure.mgmt.computefleet.ComputeFleetMgmtClient: implements ContextManager 
        fleets: FleetsOperations
        operations: Operations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.computefleet.aio

    class azure.mgmt.computefleet.aio.ComputeFleetMgmtClient: implements AsyncContextManager 
        fleets: FleetsOperations
        operations: Operations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.computefleet.aio.operations

    class azure.mgmt.computefleet.aio.operations.FleetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name']}, api_versions_list=['2025-07-01-preview'])
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: Fleet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: FleetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Fleet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> Fleet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Fleet]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Fleet]: ...

        @distributed_trace
        def list_virtual_machine_scale_sets(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'filter', 'skiptoken', 'accept']}, api_versions_list=['2025-07-01-preview'])
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...


    class azure.mgmt.computefleet.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.computefleet.models

    class azure.mgmt.computefleet.models.AcceleratorManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        NVIDIA = "Nvidia"
        XILINX = "Xilinx"


    class azure.mgmt.computefleet.models.AcceleratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FPGA = "FPGA"
        GPU = "GPU"


    class azure.mgmt.computefleet.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.computefleet.models.AdditionalCapabilities(_Model):
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


    class azure.mgmt.computefleet.models.AdditionalLocationsProfile(_Model):
        location_profiles: List[LocationProfile]

        @overload
        def __init__(
                self, 
                *, 
                location_profiles: List[LocationProfile]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.AdditionalUnattendContent(_Model):
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


    class azure.mgmt.computefleet.models.ApiEntityReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ApiError(_Model):
        code: Optional[str]
        details: Optional[List[ApiErrorBase]]
        innererror: Optional[InnerError]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ApiErrorBase]] = ..., 
                innererror: Optional[InnerError] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ApiErrorBase(_Model):
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


    class azure.mgmt.computefleet.models.ApplicationProfile(_Model):
        gallery_applications: Optional[List[VMGalleryApplication]]

        @overload
        def __init__(
                self, 
                *, 
                gallery_applications: Optional[List[VMGalleryApplication]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ArchitectureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "ARM64"
        X64 = "X64"


    class azure.mgmt.computefleet.models.BaseVirtualMachineProfile(_Model):
        application_profile: Optional[ApplicationProfile]
        capacity_reservation: Optional[CapacityReservationProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        extension_profile: Optional[VirtualMachineScaleSetExtensionProfile]
        hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile]
        license_type: Optional[str]
        network_profile: Optional[VirtualMachineScaleSetNetworkProfile]
        os_profile: Optional[VirtualMachineScaleSetOSProfile]
        scheduled_events_profile: Optional[ScheduledEventsProfile]
        security_posture_reference: Optional[SecurityPostureReference]
        security_profile: Optional[SecurityProfile]
        service_artifact_reference: Optional[ServiceArtifactReference]
        storage_profile: Optional[VirtualMachineScaleSetStorageProfile]
        time_created: Optional[datetime]
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_profile: Optional[ApplicationProfile] = ..., 
                capacity_reservation: Optional[CapacityReservationProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                extension_profile: Optional[VirtualMachineScaleSetExtensionProfile] = ..., 
                hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[VirtualMachineScaleSetNetworkProfile] = ..., 
                os_profile: Optional[VirtualMachineScaleSetOSProfile] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_posture_reference: Optional[SecurityPostureReference] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                service_artifact_reference: Optional[ServiceArtifactReference] = ..., 
                storage_profile: Optional[VirtualMachineScaleSetStorageProfile] = ..., 
                user_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.BootDiagnostics(_Model):
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


    class azure.mgmt.computefleet.models.CachingTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.computefleet.models.CapacityReservationProfile(_Model):
        capacity_reservation_group: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_group: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.CapacityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM = "VM"
        V_CPU = "VCpu"


    class azure.mgmt.computefleet.models.ComputeProfile(_Model):
        additional_virtual_machine_capabilities: Optional[AdditionalCapabilities]
        base_virtual_machine_profile: BaseVirtualMachineProfile
        compute_api_version: Optional[str]
        platform_fault_domain_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_virtual_machine_capabilities: Optional[AdditionalCapabilities] = ..., 
                base_virtual_machine_profile: BaseVirtualMachineProfile, 
                compute_api_version: Optional[str] = ..., 
                platform_fault_domain_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.CpuManufacturer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        AMPERE = "Ampere"
        INTEL = "Intel"
        MICROSOFT = "Microsoft"


    class azure.mgmt.computefleet.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.computefleet.models.DeleteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.computefleet.models.DiagnosticsProfile(_Model):
        boot_diagnostics: Optional[BootDiagnostics]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnostics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.DiffDiskOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"


    class azure.mgmt.computefleet.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "CacheDisk"
        NVME_DISK = "NvmeDisk"
        RESOURCE_DISK = "ResourceDisk"


    class azure.mgmt.computefleet.models.DiffDiskSettings(_Model):
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


    class azure.mgmt.computefleet.models.DiskControllerTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NV_ME = "NVMe"
        SCSI = "SCSI"


    class azure.mgmt.computefleet.models.DiskCreateOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "Attach"
        COPY = "Copy"
        EMPTY = "Empty"
        FROM_IMAGE = "FromImage"
        RESTORE = "Restore"


    class azure.mgmt.computefleet.models.DiskDeleteOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.computefleet.models.DiskEncryptionSetParameters(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.DomainNameLabelScopeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.computefleet.models.EncryptionIdentity(_Model):
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.computefleet.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.computefleet.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.EvictionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.computefleet.models.Fleet(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        plan: Optional[Plan]
        properties: Optional[FleetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                plan: Optional[Plan] = ..., 
                properties: Optional[FleetProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zones: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.FleetMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE = "Instance"
        MANAGED = "Managed"


    class azure.mgmt.computefleet.models.FleetProperties(_Model):
        additional_locations_profile: Optional[AdditionalLocationsProfile]
        capacity_type: Optional[Union[str, CapacityType]]
        compute_profile: ComputeProfile
        mode: Optional[Union[str, FleetMode]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        regular_priority_profile: Optional[RegularPriorityProfile]
        spot_priority_profile: Optional[SpotPriorityProfile]
        time_created: Optional[datetime]
        unique_id: Optional[str]
        vm_attributes: Optional[VMAttributes]
        vm_sizes_profile: List[VmSizeProfile]
        zone_allocation_policy: Optional[ZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                additional_locations_profile: Optional[AdditionalLocationsProfile] = ..., 
                capacity_type: Optional[Union[str, CapacityType]] = ..., 
                compute_profile: ComputeProfile, 
                mode: Optional[Union[str, FleetMode]] = ..., 
                regular_priority_profile: Optional[RegularPriorityProfile] = ..., 
                spot_priority_profile: Optional[SpotPriorityProfile] = ..., 
                vm_attributes: Optional[VMAttributes] = ..., 
                vm_sizes_profile: List[VmSizeProfile], 
                zone_allocation_policy: Optional[ZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.FleetUpdate(_Model):
        identity: Optional[ManagedServiceIdentityUpdate]
        plan: Optional[ResourcePlanUpdate]
        properties: Optional[FleetProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityUpdate] = ..., 
                plan: Optional[ResourcePlanUpdate] = ..., 
                properties: Optional[FleetProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.IPVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.computefleet.models.ImageReference(_Model):
        community_gallery_image_id: Optional[str]
        exact_version: Optional[str]
        id: Optional[str]
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


    class azure.mgmt.computefleet.models.InnerError(_Model):
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


    class azure.mgmt.computefleet.models.KeyVaultSecretReference(_Model):
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


    class azure.mgmt.computefleet.models.LinuxConfiguration(_Model):
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


    class azure.mgmt.computefleet.models.LinuxPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computefleet.models.LinuxPatchSettings(_Model):
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


    class azure.mgmt.computefleet.models.LinuxVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.computefleet.models.LinuxVMGuestPatchAutomaticByPlatformSettings(_Model):
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


    class azure.mgmt.computefleet.models.LinuxVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computefleet.models.LocalStorageDiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        SSD = "SSD"


    class azure.mgmt.computefleet.models.LocationProfile(_Model):
        location: str
        virtual_machine_profile_override: Optional[BaseVirtualMachineProfile]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                virtual_machine_profile_override: Optional[BaseVirtualMachineProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.computefleet.models.ManagedServiceIdentityUpdate(_Model):
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.mgmt.computefleet.models.NetworkApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2020_11_01 = "2020-11-01"


    class azure.mgmt.computefleet.models.NetworkInterfaceAuxiliaryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCELERATED_CONNECTIONS = "AcceleratedConnections"
        FLOATING = "Floating"
        NONE = "None"


    class azure.mgmt.computefleet.models.NetworkInterfaceAuxiliarySku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A1 = "A1"
        A2 = "A2"
        A4 = "A4"
        A8 = "A8"
        NONE = "None"


    class azure.mgmt.computefleet.models.OSImageNotificationProfile(_Model):
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


    class azure.mgmt.computefleet.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.computefleet.models.Operation(_Model):
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


    class azure.mgmt.computefleet.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.computefleet.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.computefleet.models.PatchSettings(_Model):
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


    class azure.mgmt.computefleet.models.Plan(_Model):
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


    class azure.mgmt.computefleet.models.ProtocolTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.computefleet.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.computefleet.models.ProxyAgentSettings(_Model):
        enabled: Optional[bool]
        key_incarnation_id: Optional[int]
        mode: Optional[Union[str, Mode]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                key_incarnation_id: Optional[int] = ..., 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.PublicIPAddressSku(_Model):
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


    class azure.mgmt.computefleet.models.PublicIPAddressSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.computefleet.models.PublicIPAddressSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "Global"
        REGIONAL = "Regional"


    class azure.mgmt.computefleet.models.RegularPriorityAllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.computefleet.models.RegularPriorityProfile(_Model):
        allocation_strategy: Optional[Union[str, RegularPriorityAllocationStrategy]]
        capacity: Optional[int]
        min_capacity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, RegularPriorityAllocationStrategy]] = ..., 
                capacity: Optional[int] = ..., 
                min_capacity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.computefleet.models.ResourcePlanUpdate(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ScheduledEventsProfile(_Model):
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


    class azure.mgmt.computefleet.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.computefleet.models.SecurityPostureReference(_Model):
        exclude_extensions: Optional[List[str]]
        id: Optional[str]
        is_overridable: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exclude_extensions: Optional[List[str]] = ..., 
                id: Optional[str] = ..., 
                is_overridable: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.SecurityProfile(_Model):
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


    class azure.mgmt.computefleet.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.computefleet.models.ServiceArtifactReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.SettingNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_LOGON = "AutoLogon"
        FIRST_LOGON_COMMANDS = "FirstLogonCommands"


    class azure.mgmt.computefleet.models.SpotAllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OPTIMIZED = "CapacityOptimized"
        LOWEST_PRICE = "LowestPrice"
        PRICE_CAPACITY_OPTIMIZED = "PriceCapacityOptimized"


    class azure.mgmt.computefleet.models.SpotPriorityProfile(_Model):
        allocation_strategy: Optional[Union[str, SpotAllocationStrategy]]
        capacity: Optional[int]
        eviction_policy: Optional[Union[str, EvictionPolicy]]
        maintain: Optional[bool]
        max_price_per_vm: Optional[float]
        min_capacity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, SpotAllocationStrategy]] = ..., 
                capacity: Optional[int] = ..., 
                eviction_policy: Optional[Union[str, EvictionPolicy]] = ..., 
                maintain: Optional[bool] = ..., 
                max_price_per_vm: Optional[float] = ..., 
                min_capacity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.SshConfiguration(_Model):
        public_keys: Optional[List[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[List[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.SshPublicKey(_Model):
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


    class azure.mgmt.computefleet.models.StorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.computefleet.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.SystemData(_Model):
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


    class azure.mgmt.computefleet.models.TerminateNotificationProfile(_Model):
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


    class azure.mgmt.computefleet.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.UefiSettings(_Model):
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


    class azure.mgmt.computefleet.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.computefleet.models.VMAttributeMinMaxDouble(_Model):
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


    class azure.mgmt.computefleet.models.VMAttributeMinMaxInteger(_Model):
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


    class azure.mgmt.computefleet.models.VMAttributeSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        INCLUDED = "Included"
        REQUIRED = "Required"


    class azure.mgmt.computefleet.models.VMAttributes(_Model):
        accelerator_count: Optional[VMAttributeMinMaxInteger]
        accelerator_manufacturers: Optional[List[Union[str, AcceleratorManufacturer]]]
        accelerator_support: Optional[Union[str, VMAttributeSupport]]
        accelerator_types: Optional[List[Union[str, AcceleratorType]]]
        architecture_types: Optional[List[Union[str, ArchitectureType]]]
        burstable_support: Optional[Union[str, VMAttributeSupport]]
        cpu_manufacturers: Optional[List[Union[str, CpuManufacturer]]]
        data_disk_count: Optional[VMAttributeMinMaxInteger]
        excluded_vm_sizes: Optional[List[str]]
        local_storage_disk_types: Optional[List[Union[str, LocalStorageDiskType]]]
        local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble]
        local_storage_support: Optional[Union[str, VMAttributeSupport]]
        memory_in_gi_b: VMAttributeMinMaxDouble
        memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble]
        network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble]
        network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_network_interface_count: Optional[VMAttributeMinMaxInteger]
        rdma_support: Optional[Union[str, VMAttributeSupport]]
        v_cpu_count: VMAttributeMinMaxInteger
        vm_categories: Optional[List[Union[str, VMCategory]]]

        @overload
        def __init__(
                self, 
                *, 
                accelerator_count: Optional[VMAttributeMinMaxInteger] = ..., 
                accelerator_manufacturers: Optional[List[Union[str, AcceleratorManufacturer]]] = ..., 
                accelerator_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                accelerator_types: Optional[List[Union[str, AcceleratorType]]] = ..., 
                architecture_types: Optional[List[Union[str, ArchitectureType]]] = ..., 
                burstable_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                cpu_manufacturers: Optional[List[Union[str, CpuManufacturer]]] = ..., 
                data_disk_count: Optional[VMAttributeMinMaxInteger] = ..., 
                excluded_vm_sizes: Optional[List[str]] = ..., 
                local_storage_disk_types: Optional[List[Union[str, LocalStorageDiskType]]] = ..., 
                local_storage_in_gi_b: Optional[VMAttributeMinMaxDouble] = ..., 
                local_storage_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                memory_in_gi_b: VMAttributeMinMaxDouble, 
                memory_in_gi_b_per_v_cpu: Optional[VMAttributeMinMaxDouble] = ..., 
                network_bandwidth_in_mbps: Optional[VMAttributeMinMaxDouble] = ..., 
                network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_network_interface_count: Optional[VMAttributeMinMaxInteger] = ..., 
                rdma_support: Optional[Union[str, VMAttributeSupport]] = ..., 
                v_cpu_count: VMAttributeMinMaxInteger, 
                vm_categories: Optional[List[Union[str, VMCategory]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VMCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_OPTIMIZED = "ComputeOptimized"
        FPGA_ACCELERATED = "FpgaAccelerated"
        GENERAL_PURPOSE = "GeneralPurpose"
        GPU_ACCELERATED = "GpuAccelerated"
        HIGH_PERFORMANCE_COMPUTE = "HighPerformanceCompute"
        MEMORY_OPTIMIZED = "MemoryOptimized"
        STORAGE_OPTIMIZED = "StorageOptimized"


    class azure.mgmt.computefleet.models.VMDiskSecurityProfile(_Model):
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


    class azure.mgmt.computefleet.models.VMGalleryApplication(_Model):
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


    class azure.mgmt.computefleet.models.VMOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCEL_FAILED_STATUS_UNKNOWN = "CancelFailedStatusUnknown"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.computefleet.models.VMSizeProperties(_Model):
        v_cpus_available: Optional[int]
        v_cpus_per_core: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                v_cpus_available: Optional[int] = ..., 
                v_cpus_per_core: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VaultCertificate(_Model):
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


    class azure.mgmt.computefleet.models.VaultSecretGroup(_Model):
        source_vault: Optional[SubResource]
        vault_certificates: Optional[List[VaultCertificate]]

        @overload
        def __init__(
                self, 
                *, 
                source_vault: Optional[SubResource] = ..., 
                vault_certificates: Optional[List[VaultCertificate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualHardDisk(_Model):
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachine(_Model):
        error: Optional[ApiError]
        id: str
        name: str
        operation_status: Union[str, VMOperationStatus]
        type: Optional[str]


    class azure.mgmt.computefleet.models.VirtualMachineScaleSet(_Model):
        error: Optional[ApiError]
        id: str
        name: str
        operation_status: Union[str, ProvisioningState]
        type: Optional[str]


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetDataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        disk_iops_read_write: Optional[int]
        disk_m_bps_read_write: Optional[int]
        disk_size_gb: Optional[int]
        lun: int
        managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters]
        name: Optional[str]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                create_option: Union[str, DiskCreateOptionTypes], 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                disk_iops_read_write: Optional[int] = ..., 
                disk_m_bps_read_write: Optional[int] = ..., 
                disk_size_gb: Optional[int] = ..., 
                lun: int, 
                managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters] = ..., 
                name: Optional[str] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetExtension(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetExtensionProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VirtualMachineScaleSetExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetExtensionProfile(_Model):
        extensions: Optional[List[VirtualMachineScaleSetExtension]]
        extensions_time_budget: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[List[VirtualMachineScaleSetExtension]] = ..., 
                extensions_time_budget: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[Dict[str, Any]]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        provision_after_extensions: Optional[List[str]]
        provisioning_state: Optional[str]
        publisher: Optional[str]
        settings: Optional[Dict[str, Any]]
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
                protected_settings: Optional[Dict[str, Any]] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                provision_after_extensions: Optional[List[str]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[Dict[str, Any]] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetHardwareProfile(_Model):
        vm_size_properties: Optional[VMSizeProperties]

        @overload
        def __init__(
                self, 
                *, 
                vm_size_properties: Optional[VMSizeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetIPConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetIPConfigurationProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetIPConfigurationProperties(_Model):
        application_gateway_backend_address_pools: Optional[List[SubResource]]
        application_security_groups: Optional[List[SubResource]]
        load_balancer_backend_address_pools: Optional[List[SubResource]]
        load_balancer_inbound_nat_pools: Optional[List[SubResource]]
        primary: Optional[bool]
        private_ip_address_version: Optional[Union[str, IPVersion]]
        public_ip_address_configuration: Optional[VirtualMachineScaleSetPublicIPAddressConfiguration]
        subnet: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[List[SubResource]] = ..., 
                application_security_groups: Optional[List[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[List[SubResource]] = ..., 
                load_balancer_inbound_nat_pools: Optional[List[SubResource]] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address_version: Optional[Union[str, IPVersion]] = ..., 
                public_ip_address_configuration: Optional[VirtualMachineScaleSetPublicIPAddressConfiguration] = ..., 
                subnet: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetIpTag(_Model):
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


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetManagedDiskParameters(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        security_profile: Optional[VMDiskSecurityProfile]
        storage_account_type: Optional[Union[str, StorageAccountTypes]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                security_profile: Optional[VMDiskSecurityProfile] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetNetworkConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetNetworkConfigurationProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetNetworkConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetNetworkConfigurationDnsSettings(_Model):
        dns_servers: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetNetworkConfigurationProperties(_Model):
        auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]]
        auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]]
        delete_option: Optional[Union[str, DeleteOptions]]
        disable_tcp_state_tracking: Optional[bool]
        dns_settings: Optional[VirtualMachineScaleSetNetworkConfigurationDnsSettings]
        enable_accelerated_networking: Optional[bool]
        enable_fpga: Optional[bool]
        enable_ip_forwarding: Optional[bool]
        ip_configurations: List[VirtualMachineScaleSetIPConfiguration]
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
                dns_settings: Optional[VirtualMachineScaleSetNetworkConfigurationDnsSettings] = ..., 
                enable_accelerated_networking: Optional[bool] = ..., 
                enable_fpga: Optional[bool] = ..., 
                enable_ip_forwarding: Optional[bool] = ..., 
                ip_configurations: List[VirtualMachineScaleSetIPConfiguration], 
                network_security_group: Optional[SubResource] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetNetworkProfile(_Model):
        health_probe: Optional[ApiEntityReference]
        network_api_version: Optional[Union[str, NetworkApiVersion]]
        network_interface_configurations: Optional[List[VirtualMachineScaleSetNetworkConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                health_probe: Optional[ApiEntityReference] = ..., 
                network_api_version: Optional[Union[str, NetworkApiVersion]] = ..., 
                network_interface_configurations: Optional[List[VirtualMachineScaleSetNetworkConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetOSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        diff_disk_settings: Optional[DiffDiskSettings]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters]
        name: Optional[str]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        vhd_containers: Optional[List[str]]
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
                image: Optional[VirtualHardDisk] = ..., 
                managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters] = ..., 
                name: Optional[str] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                vhd_containers: Optional[List[str]] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetOSProfile(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        allow_extension_operations: Optional[bool]
        computer_name_prefix: Optional[str]
        custom_data: Optional[str]
        linux_configuration: Optional[LinuxConfiguration]
        require_guest_provision_signal: Optional[bool]
        secrets: Optional[List[VaultSecretGroup]]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                allow_extension_operations: Optional[bool] = ..., 
                computer_name_prefix: Optional[str] = ..., 
                custom_data: Optional[str] = ..., 
                linux_configuration: Optional[LinuxConfiguration] = ..., 
                require_guest_provision_signal: Optional[bool] = ..., 
                secrets: Optional[List[VaultSecretGroup]] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetPublicIPAddressConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationProperties]
        sku: Optional[PublicIPAddressSku]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationProperties] = ..., 
                sku: Optional[PublicIPAddressSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings(_Model):
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


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetPublicIPAddressConfigurationProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings]
        idle_timeout_in_minutes: Optional[int]
        ip_tags: Optional[List[VirtualMachineScaleSetIpTag]]
        public_ip_address_version: Optional[Union[str, IPVersion]]
        public_ip_prefix: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                ip_tags: Optional[List[VirtualMachineScaleSetIpTag]] = ..., 
                public_ip_address_version: Optional[Union[str, IPVersion]] = ..., 
                public_ip_prefix: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VirtualMachineScaleSetStorageProfile(_Model):
        data_disks: Optional[List[VirtualMachineScaleSetDataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[VirtualMachineScaleSetOSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[List[VirtualMachineScaleSetDataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[VirtualMachineScaleSetOSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.VmSizeProfile(_Model):
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


    class azure.mgmt.computefleet.models.WinRMConfiguration(_Model):
        listeners: Optional[List[WinRMListener]]

        @overload
        def __init__(
                self, 
                *, 
                listeners: Optional[List[WinRMListener]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.WinRMListener(_Model):
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


    class azure.mgmt.computefleet.models.WindowsConfiguration(_Model):
        additional_unattend_content: Optional[List[AdditionalUnattendContent]]
        enable_automatic_updates: Optional[bool]
        enable_vm_agent_platform_updates: Optional[bool]
        patch_settings: Optional[PatchSettings]
        provision_vm_agent: Optional[bool]
        time_zone: Optional[str]
        win_rm: Optional[WinRMConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                additional_unattend_content: Optional[List[AdditionalUnattendContent]] = ..., 
                enable_automatic_updates: Optional[bool] = ..., 
                enable_vm_agent_platform_updates: Optional[bool] = ..., 
                patch_settings: Optional[PatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                time_zone: Optional[str] = ..., 
                win_rm: Optional[WinRMConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.WindowsPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.computefleet.models.WindowsVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.computefleet.models.WindowsVMGuestPatchAutomaticByPlatformSettings(_Model):
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


    class azure.mgmt.computefleet.models.WindowsVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_OS = "AutomaticByOS"
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        MANUAL = "Manual"


    class azure.mgmt.computefleet.models.ZoneAllocationPolicy(_Model):
        distribution_strategy: Union[str, ZoneDistributionStrategy]
        zone_preferences: Optional[List[ZonePreference]]

        @overload
        def __init__(
                self, 
                *, 
                distribution_strategy: Union[str, ZoneDistributionStrategy], 
                zone_preferences: Optional[List[ZonePreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.computefleet.models.ZoneDistributionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_EFFORT_SINGLE_ZONE = "BestEffortSingleZone"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.computefleet.models.ZonePreference(_Model):
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


namespace azure.mgmt.computefleet.operations

    class azure.mgmt.computefleet.operations.FleetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'fleet_name']}, api_versions_list=['2025-07-01-preview'])
        def begin_cancel(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: Fleet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: FleetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Fleet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                fleet_name: str, 
                **kwargs: Any
            ) -> Fleet: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Fleet]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Fleet]: ...

        @distributed_trace
        def list_virtual_machine_scale_sets(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'filter', 'skiptoken', 'accept']}, api_versions_list=['2025-07-01-preview'])
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...


    class azure.mgmt.computefleet.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```