```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.compute

    class azure.mgmt.compute.ComputeManagementClient: implements ContextManager 
        availability_sets: AvailabilitySetsOperations
        capacity_reservation_groups: CapacityReservationGroupsOperations
        capacity_reservations: CapacityReservationsOperations
        community_galleries: CommunityGalleriesOperations
        community_gallery_image_versions: CommunityGalleryImageVersionsOperations
        community_gallery_images: CommunityGalleryImagesOperations
        dedicated_host_groups: DedicatedHostGroupsOperations
        dedicated_hosts: DedicatedHostsOperations
        disk_accesses: DiskAccessesOperations
        disk_encryption_sets: DiskEncryptionSetsOperations
        disk_restore_point: DiskRestorePointOperations
        disks: DisksOperations
        galleries: GalleriesOperations
        gallery_application_versions: GalleryApplicationVersionsOperations
        gallery_applications: GalleryApplicationsOperations
        gallery_image_versions: GalleryImageVersionsOperations
        gallery_images: GalleryImagesOperations
        gallery_in_vm_access_control_profile_versions: GalleryInVMAccessControlProfileVersionsOperations
        gallery_in_vm_access_control_profiles: GalleryInVMAccessControlProfilesOperations
        gallery_script_versions: GalleryScriptVersionsOperations
        gallery_scripts: GalleryScriptsOperations
        gallery_sharing_profile: GallerySharingProfileOperations
        images: ImagesOperations
        log_analytics: LogAnalyticsOperations
        operations: Operations
        proximity_placement_groups: ProximityPlacementGroupsOperations
        resource_skus: ResourceSkusOperations
        restore_point_collections: RestorePointCollectionsOperations
        restore_points: RestorePointsOperations
        shared_galleries: SharedGalleriesOperations
        shared_gallery_image_versions: SharedGalleryImageVersionsOperations
        shared_gallery_images: SharedGalleryImagesOperations
        snapshots: SnapshotsOperations
        soft_deleted_resource: SoftDeletedResourceOperations
        ssh_public_keys: SshPublicKeysOperations
        usage: UsageOperations
        virtual_machine_extension_images: VirtualMachineExtensionImagesOperations
        virtual_machine_extensions: VirtualMachineExtensionsOperations
        virtual_machine_images: VirtualMachineImagesOperations
        virtual_machine_images_edge_zone: VirtualMachineImagesEdgeZoneOperations
        virtual_machine_run_commands: VirtualMachineRunCommandsOperations
        virtual_machine_scale_set_extensions: VirtualMachineScaleSetExtensionsOperations
        virtual_machine_scale_set_life_cycle_hook_events: VirtualMachineScaleSetLifeCycleHookEventsOperations
        virtual_machine_scale_set_rolling_upgrades: VirtualMachineScaleSetRollingUpgradesOperations
        virtual_machine_scale_set_vm_extensions: VirtualMachineScaleSetVMExtensionsOperations
        virtual_machine_scale_set_vm_run_commands: VirtualMachineScaleSetVMRunCommandsOperations
        virtual_machine_scale_set_vms: VirtualMachineScaleSetVMsOperations
        virtual_machine_scale_sets: VirtualMachineScaleSetsOperations
        virtual_machine_sizes: VirtualMachineSizesOperations
        virtual_machines: VirtualMachinesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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


namespace azure.mgmt.compute.aio

    class azure.mgmt.compute.aio.ComputeManagementClient: implements AsyncContextManager 
        availability_sets: AvailabilitySetsOperations
        capacity_reservation_groups: CapacityReservationGroupsOperations
        capacity_reservations: CapacityReservationsOperations
        community_galleries: CommunityGalleriesOperations
        community_gallery_image_versions: CommunityGalleryImageVersionsOperations
        community_gallery_images: CommunityGalleryImagesOperations
        dedicated_host_groups: DedicatedHostGroupsOperations
        dedicated_hosts: DedicatedHostsOperations
        disk_accesses: DiskAccessesOperations
        disk_encryption_sets: DiskEncryptionSetsOperations
        disk_restore_point: DiskRestorePointOperations
        disks: DisksOperations
        galleries: GalleriesOperations
        gallery_application_versions: GalleryApplicationVersionsOperations
        gallery_applications: GalleryApplicationsOperations
        gallery_image_versions: GalleryImageVersionsOperations
        gallery_images: GalleryImagesOperations
        gallery_in_vm_access_control_profile_versions: GalleryInVMAccessControlProfileVersionsOperations
        gallery_in_vm_access_control_profiles: GalleryInVMAccessControlProfilesOperations
        gallery_script_versions: GalleryScriptVersionsOperations
        gallery_scripts: GalleryScriptsOperations
        gallery_sharing_profile: GallerySharingProfileOperations
        images: ImagesOperations
        log_analytics: LogAnalyticsOperations
        operations: Operations
        proximity_placement_groups: ProximityPlacementGroupsOperations
        resource_skus: ResourceSkusOperations
        restore_point_collections: RestorePointCollectionsOperations
        restore_points: RestorePointsOperations
        shared_galleries: SharedGalleriesOperations
        shared_gallery_image_versions: SharedGalleryImageVersionsOperations
        shared_gallery_images: SharedGalleryImagesOperations
        snapshots: SnapshotsOperations
        soft_deleted_resource: SoftDeletedResourceOperations
        ssh_public_keys: SshPublicKeysOperations
        usage: UsageOperations
        virtual_machine_extension_images: VirtualMachineExtensionImagesOperations
        virtual_machine_extensions: VirtualMachineExtensionsOperations
        virtual_machine_images: VirtualMachineImagesOperations
        virtual_machine_images_edge_zone: VirtualMachineImagesEdgeZoneOperations
        virtual_machine_run_commands: VirtualMachineRunCommandsOperations
        virtual_machine_scale_set_extensions: VirtualMachineScaleSetExtensionsOperations
        virtual_machine_scale_set_life_cycle_hook_events: VirtualMachineScaleSetLifeCycleHookEventsOperations
        virtual_machine_scale_set_rolling_upgrades: VirtualMachineScaleSetRollingUpgradesOperations
        virtual_machine_scale_set_vm_extensions: VirtualMachineScaleSetVMExtensionsOperations
        virtual_machine_scale_set_vm_run_commands: VirtualMachineScaleSetVMRunCommandsOperations
        virtual_machine_scale_set_vms: VirtualMachineScaleSetVMsOperations
        virtual_machine_scale_sets: VirtualMachineScaleSetsOperations
        virtual_machine_sizes: VirtualMachineSizesOperations
        virtual_machines: VirtualMachinesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
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


namespace azure.mgmt.compute.aio.operations

    class azure.mgmt.compute.aio.operations.AvailabilitySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[ConvertToVirtualMachineScaleSetInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def cancel_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilitySet]: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineSize]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailabilitySet]: ...

        @overload
        async def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: MigrateToVirtualMachineScaleSetInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: AvailabilitySetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        async def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: MigrateToVirtualMachineScaleSetInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.compute.aio.operations.CapacityReservationGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: CapacityReservationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                *, 
                expand: Optional[Union[str, CapacityReservationGroupInstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CapacityReservationGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                resource_ids_only: Optional[Union[str, ResourceIdOptionsForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CapacityReservationGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: CapacityReservationGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...


    class azure.mgmt.compute.aio.operations.CapacityReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: CapacityReservation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: CapacityReservationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityReservation]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                *, 
                expand: Optional[Union[str, CapacityReservationInstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> CapacityReservation: ...

        @distributed_trace
        def list_by_capacity_reservation_group(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CapacityReservation]: ...


    class azure.mgmt.compute.aio.operations.CommunityGalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                **kwargs: Any
            ) -> CommunityGallery: ...


    class azure.mgmt.compute.aio.operations.CommunityGalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> CommunityGalleryImageVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunityGalleryImageVersion]: ...


    class azure.mgmt.compute.aio.operations.CommunityGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> CommunityGalleryImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                public_gallery_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommunityGalleryImage]: ...


    class azure.mgmt.compute.aio.operations.DedicatedHostGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: DedicatedHostGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHostGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DedicatedHostGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: DedicatedHostGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...


    class azure.mgmt.compute.aio.operations.DedicatedHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: DedicatedHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: DedicatedHostUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DedicatedHost]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> DedicatedHost: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_by_host_group(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DedicatedHost]: ...


    class azure.mgmt.compute.aio.operations.DiskAccessesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: DiskAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: DiskAccessUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskAccess]: ...

        @overload
        async def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> DiskAccess: ...

        @distributed_trace_async
        async def get_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def get_private_link_resources(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DiskAccess]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiskAccess]: ...

        @distributed_trace
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.compute.aio.operations.DiskEncryptionSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: DiskEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: DiskEncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiskEncryptionSet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> DiskEncryptionSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DiskEncryptionSet]: ...

        @distributed_trace
        def list_associated_resources(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiskEncryptionSet]: ...


    class azure.mgmt.compute.aio.operations.DiskRestorePointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @distributed_trace_async
        async def begin_revoke_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                **kwargs: Any
            ) -> DiskRestorePoint: ...

        @distributed_trace
        def list_by_restore_point(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DiskRestorePoint]: ...


    class azure.mgmt.compute.aio.operations.DisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: Disk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @distributed_trace_async
        async def begin_revoke_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: DiskUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Disk]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> Disk: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Disk]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Disk]: ...


    class azure.mgmt.compute.aio.operations.GalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: Gallery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: GalleryUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                *, 
                expand: Optional[Union[str, GalleryExpandParams]] = ..., 
                select: Optional[Union[str, SelectPermissions]] = ..., 
                **kwargs: Any
            ) -> Gallery: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Gallery]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Gallery]: ...


    class azure.mgmt.compute.aio.operations.GalleryApplicationVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: GalleryApplicationVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: GalleryApplicationVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplicationVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                *, 
                expand: Optional[Union[str, ReplicationStatusTypes]] = ..., 
                **kwargs: Any
            ) -> GalleryApplicationVersion: ...

        @distributed_trace
        def list_by_gallery_application(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryApplicationVersion]: ...


    class azure.mgmt.compute.aio.operations.GalleryApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: GalleryApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: GalleryApplicationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryApplication]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> GalleryApplication: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryApplication]: ...


    class azure.mgmt.compute.aio.operations.GalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: GalleryImageVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: GalleryImageVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImageVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                *, 
                expand: Optional[Union[str, ReplicationStatusTypes]] = ..., 
                **kwargs: Any
            ) -> GalleryImageVersion: ...

        @distributed_trace
        def list_by_gallery_image(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryImageVersion]: ...


    class azure.mgmt.compute.aio.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: GalleryImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryImage]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> GalleryImage: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryImage]: ...


    class azure.mgmt.compute.aio.operations.GalleryInVMAccessControlProfileVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: GalleryInVMAccessControlProfileVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: GalleryInVMAccessControlProfileVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                **kwargs: Any
            ) -> GalleryInVMAccessControlProfileVersion: ...

        @distributed_trace
        def list_by_gallery_in_vm_access_control_profile(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryInVMAccessControlProfileVersion]: ...


    class azure.mgmt.compute.aio.operations.GalleryInVMAccessControlProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: GalleryInVMAccessControlProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: GalleryInVMAccessControlProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryInVMAccessControlProfile]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> GalleryInVMAccessControlProfile: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryInVMAccessControlProfile]: ...


    class azure.mgmt.compute.aio.operations.GalleryScriptVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: GalleryScriptVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'gallery_script_version_name']}, api_versions_list=['2025-03-03'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: GalleryScriptVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScriptVersion]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'gallery_script_version_name', 'accept']}, api_versions_list=['2025-03-03'])
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                **kwargs: Any
            ) -> GalleryScriptVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'accept']}, api_versions_list=['2025-03-03'])
        def list_by_gallery_script(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryScriptVersion]: ...


    class azure.mgmt.compute.aio.operations.GalleryScriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: GalleryScript, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name']}, api_versions_list=['2025-03-03'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: GalleryScriptUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GalleryScript]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'accept']}, api_versions_list=['2025-03-03'])
        async def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> GalleryScript: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'accept']}, api_versions_list=['2025-03-03'])
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GalleryScript]: ...


    class azure.mgmt.compute.aio.operations.GallerySharingProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: SharingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharingUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharingUpdate]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharingUpdate]: ...


    class azure.mgmt.compute.aio.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: ImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Image]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                image_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Image]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...


    class azure.mgmt.compute.aio.operations.LogAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: RequestRateByIntervalInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...

        @overload
        async def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...

        @overload
        async def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...

        @overload
        async def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: ThrottledRequestsInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...

        @overload
        async def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...

        @overload
        async def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogAnalyticsOperationResult]: ...


    class azure.mgmt.compute.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.compute.aio.operations.ProximityPlacementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: ProximityPlacementGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                *, 
                include_colocation_status: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProximityPlacementGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ProximityPlacementGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: ProximityPlacementGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...


    class azure.mgmt.compute.aio.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                include_extended_locations: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.compute.aio.operations.RestorePointCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: RestorePointCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                *, 
                expand: Optional[Union[str, RestorePointCollectionExpandOptions]] = ..., 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RestorePointCollection]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[RestorePointCollection]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: RestorePointCollectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...


    class azure.mgmt.compute.aio.operations.RestorePointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: RestorePoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestorePoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestorePoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RestorePoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                *, 
                expand: Optional[Union[str, RestorePointExpandOptions]] = ..., 
                **kwargs: Any
            ) -> RestorePoint: ...


    class azure.mgmt.compute.aio.operations.SharedGalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                **kwargs: Any
            ) -> SharedGallery: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedGallery]: ...


    class azure.mgmt.compute.aio.operations.SharedGalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> SharedGalleryImageVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedGalleryImageVersion]: ...


    class azure.mgmt.compute.aio.operations.SharedGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> SharedGalleryImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                gallery_unique_name: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedGalleryImage]: ...


    class azure.mgmt.compute.aio.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @overload
        async def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AccessUri]: ...

        @distributed_trace_async
        async def begin_revoke_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: SnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Snapshot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Snapshot]: ...


    class azure.mgmt.compute.aio.operations.SoftDeletedResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_artifact_name(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                artifact_type: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GallerySoftDeletedResource]: ...


    class azure.mgmt.compute.aio.operations.SshPublicKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: SshPublicKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[SshGenerateKeyPairInputParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @overload
        async def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @overload
        async def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SshPublicKeyResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SshPublicKeyResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: SshPublicKeyUpdateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...


    class azure.mgmt.compute.aio.operations.UsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineExtensionImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                publisher_name: str, 
                type: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineExtensionImage: ...

        @distributed_trace_async
        async def list_types(
                self, 
                location: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineExtensionImage]: ...

        @distributed_trace_async
        async def list_versions(
                self, 
                location: str, 
                publisher_name: str, 
                type: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineExtensionImage]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineExtension]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineExtension: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineExtensionsListResult: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineImagesEdgeZoneOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineImage: ...

        @distributed_trace_async
        async def list(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_offers(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_publishers(
                self, 
                location: str, 
                edge_zone: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_skus(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineImage: ...

        @distributed_trace_async
        async def list(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_by_edge_zone(
                self, 
                location: str, 
                edge_zone: str, 
                **kwargs: Any
            ) -> VmImagesInEdgeZoneListResult: ...

        @distributed_trace_async
        async def list_offers(
                self, 
                location: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_publishers(
                self, 
                location: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_skus(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace_async
        async def list_with_properties(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: str, 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImage]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommandUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                command_id: str, 
                **kwargs: Any
            ) -> RunCommandDocument: ...

        @distributed_trace_async
        async def get_by_virtual_machine(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RunCommandDocumentBase]: ...

        @distributed_trace
        def list_by_virtual_machine(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineRunCommand]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetExtension]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSetExtension]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetLifeCycleHookEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VMScaleSetLifecycleHookEvent]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: VMScaleSetLifecycleHookEventUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetRollingUpgradesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start_extension_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start_os_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_latest(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> RollingUpgradeStatusInfo: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetVMExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetVMExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetVMExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVMExtension]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMExtension: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMExtensionsListResult: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetVMRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommandUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineRunCommand]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetVMsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: AttachDetachDataDisksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @distributed_trace_async
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[VirtualMachineScaleSetVMReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: RunCommandInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: VirtualMachineScaleSetVM, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVM]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVM]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSetVM]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVM: ...

        @distributed_trace_async
        async def get_instance_view(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMInstanceView: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                virtual_machine_scale_set_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSetVM]: ...

        @distributed_trace_async
        async def retrieve_boot_diagnostics_data(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                sas_uri_expiration_time_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> RetrieveBootDiagnosticsDataResult: ...

        @distributed_trace_async
        async def simulate_eviction(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineScaleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VirtualMachineScaleSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: VirtualMachineScaleSetVMInstanceRequiredIDs, 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: JSON, 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reapply(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[VirtualMachineScaleSetReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VMScaleSetScaleOutInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: OrchestrationServiceStateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VirtualMachineScaleSetUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineScaleSet]: ...

        @overload
        async def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: VirtualMachineScaleSetVMInstanceRequiredIDs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VMScaleSetConvertToSinglePlacementGroupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def force_recovery_service_fabric_platform_update_domain_walk(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                placement_group_id: Optional[str] = ..., 
                platform_update_domain: int, 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> RecoveryWalkResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetVMScaleSets]] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSet: ...

        @distributed_trace_async
        async def get_instance_view(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> VirtualMachineScaleSetInstanceView: ...

        @distributed_trace
        def get_os_upgrade_history(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpgradeOperationHistoricalStatusInfo]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> AsyncItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineScaleSetSku]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachineSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineSize]: ...


    class azure.mgmt.compute.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_assess_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineAssessPatchesResult]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: AttachDetachDataDisksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @overload
        async def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageProfile]: ...

        @overload
        async def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachineCaptureParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineCaptureResult]: ...

        @overload
        async def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineCaptureResult]: ...

        @overload
        async def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineCaptureResult]: ...

        @distributed_trace_async
        async def begin_convert_to_managed_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        @api_version_validation(params_added_on={'2025-11-01': ['force_deallocate']}, api_versions_list=['2024-11-01', '2025-04-01', '2025-11-01'])
        async def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                force_deallocate: Optional[bool] = ..., 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: VirtualMachineInstallPatchesParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        async def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        async def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[MigrateVMToVirtualMachineScaleSetInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reapply(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[VirtualMachineReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: RunCommandInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @overload
        async def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RunCommandResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[VirtualMachine]: ...

        @distributed_trace_async
        async def generalize(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace_async
        async def instance_view(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> VirtualMachineInstanceView: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypeForListVMs]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                expand: Optional[Union[str, ExpandTypesForListVMs]] = ..., 
                filter: Optional[str] = ..., 
                status_only: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachineSize]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...

        @distributed_trace_async
        async def retrieve_boot_diagnostics_data(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                sas_uri_expiration_time_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> RetrieveBootDiagnosticsDataResult: ...

        @distributed_trace_async
        async def simulate_eviction(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...


namespace azure.mgmt.compute.models

    class azure.mgmt.compute.models.AccessControlRules(_Model):
        identities: Optional[list[AccessControlRulesIdentity]]
        privileges: Optional[list[AccessControlRulesPrivilege]]
        role_assignments: Optional[list[AccessControlRulesRoleAssignment]]
        roles: Optional[list[AccessControlRulesRole]]

        @overload
        def __init__(
                self, 
                *, 
                identities: Optional[list[AccessControlRulesIdentity]] = ..., 
                privileges: Optional[list[AccessControlRulesPrivilege]] = ..., 
                role_assignments: Optional[list[AccessControlRulesRoleAssignment]] = ..., 
                roles: Optional[list[AccessControlRulesRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AccessControlRulesIdentity(_Model):
        exe_path: Optional[str]
        group_name: Optional[str]
        name: str
        process_name: Optional[str]
        user_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                exe_path: Optional[str] = ..., 
                group_name: Optional[str] = ..., 
                name: str, 
                process_name: Optional[str] = ..., 
                user_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AccessControlRulesMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DISABLED = "Disabled"
        ENFORCE = "Enforce"


    class azure.mgmt.compute.models.AccessControlRulesPrivilege(_Model):
        name: str
        path: str
        query_parameters: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                path: str, 
                query_parameters: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AccessControlRulesRole(_Model):
        name: str
        privileges: list[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                privileges: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AccessControlRulesRoleAssignment(_Model):
        identities: list[str]
        role: str

        @overload
        def __init__(
                self, 
                *, 
                identities: list[str], 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ = "Read"
        WRITE = "Write"


    class azure.mgmt.compute.models.AccessUri(_Model):
        access_sas: Optional[str]
        security_data_access_sas: Optional[str]
        security_metadata_access_sas: Optional[str]


    class azure.mgmt.compute.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.compute.models.AdditionalCapabilities(_Model):
        enable_fips1403_encryption: Optional[bool]
        hibernation_enabled: Optional[bool]
        ultra_ssd_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_fips1403_encryption: Optional[bool] = ..., 
                hibernation_enabled: Optional[bool] = ..., 
                ultra_ssd_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AdditionalReplicaSet(_Model):
        regional_replica_count: Optional[int]
        storage_account_type: Optional[Union[str, StorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                regional_replica_count: Optional[int] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AdditionalUnattendContent(_Model):
        component_name: Optional[Union[str, ComponentNames]]
        content: Optional[str]
        pass_name: Optional[Union[str, PassNames]]
        setting_name: Optional[Union[str, SettingNames]]

        @overload
        def __init__(
                self, 
                *, 
                component_name: Optional[Union[str, ComponentNames]] = ..., 
                content: Optional[str] = ..., 
                pass_name: Optional[Union[str, PassNames]] = ..., 
                setting_name: Optional[Union[str, SettingNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AggregatedReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.AllInstancesDown(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AllocationStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY_OPTIMIZED = "CapacityOptimized"
        LOWEST_PRICE = "LowestPrice"
        PRIORITIZED = "Prioritized"


    class azure.mgmt.compute.models.AlternativeOption(_Model):
        type: Optional[Union[str, AlternativeType]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, AlternativeType]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AlternativeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        OFFER = "Offer"
        PLAN = "Plan"


    class azure.mgmt.compute.models.ApiEntityReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ApiError(_Model):
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


    class azure.mgmt.compute.models.ApiErrorBase(_Model):
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


    class azure.mgmt.compute.models.ApplicationProfile(_Model):
        gallery_applications: Optional[list[VMGalleryApplication]]

        @overload
        def __init__(
                self, 
                *, 
                gallery_applications: Optional[list[VMGalleryApplication]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Architecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "Arm64"
        X64 = "x64"


    class azure.mgmt.compute.models.ArchitectureTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "Arm64"
        X64 = "x64"


    class azure.mgmt.compute.models.AttachDetachDataDisksRequest(_Model):
        data_disks_to_attach: Optional[list[DataDisksToAttach]]
        data_disks_to_detach: Optional[list[DataDisksToDetach]]

        @overload
        def __init__(
                self, 
                *, 
                data_disks_to_attach: Optional[list[DataDisksToAttach]] = ..., 
                data_disks_to_detach: Optional[list[DataDisksToDetach]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AutomaticOSUpgradePolicy(_Model):
        disable_automatic_rollback: Optional[bool]
        enable_automatic_os_upgrade: Optional[bool]
        os_rolling_upgrade_deferral: Optional[bool]
        use_rolling_upgrade_policy: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable_automatic_rollback: Optional[bool] = ..., 
                enable_automatic_os_upgrade: Optional[bool] = ..., 
                os_rolling_upgrade_deferral: Optional[bool] = ..., 
                use_rolling_upgrade_policy: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AutomaticOSUpgradeProperties(_Model):
        automatic_os_upgrade_supported: bool

        @overload
        def __init__(
                self, 
                *, 
                automatic_os_upgrade_supported: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AutomaticRepairsPolicy(_Model):
        enabled: Optional[bool]
        grace_period: Optional[str]
        repair_action: Optional[Union[str, RepairAction]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                grace_period: Optional[str] = ..., 
                repair_action: Optional[Union[str, RepairAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AutomaticZoneRebalancingPolicy(_Model):
        enabled: Optional[bool]
        rebalance_behavior: Optional[Union[str, RebalanceBehavior]]
        rebalance_strategy: Optional[Union[str, RebalanceStrategy]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                rebalance_behavior: Optional[Union[str, RebalanceBehavior]] = ..., 
                rebalance_strategy: Optional[Union[str, RebalanceStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AvailabilityPolicy(_Model):
        action_on_disk_delay: Optional[Union[str, AvailabilityPolicyDiskDelay]]

        @overload
        def __init__(
                self, 
                *, 
                action_on_disk_delay: Optional[Union[str, AvailabilityPolicyDiskDelay]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AvailabilityPolicyDiskDelay(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_REATTACH = "AutomaticReattach"
        NONE = "None"


    class azure.mgmt.compute.models.AvailabilitySet(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AvailabilitySetProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AvailabilitySetProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.AvailabilitySetProperties(_Model):
        platform_fault_domain_count: Optional[int]
        platform_update_domain_count: Optional[int]
        proximity_placement_group: Optional[SubResource]
        scheduled_events_policy: Optional[ScheduledEventsPolicy]
        statuses: Optional[list[InstanceViewStatus]]
        virtual_machine_scale_set_migration_info: Optional[VirtualMachineScaleSetMigrationInfo]
        virtual_machines: Optional[list[SubResource]]

        @overload
        def __init__(
                self, 
                *, 
                platform_fault_domain_count: Optional[int] = ..., 
                platform_update_domain_count: Optional[int] = ..., 
                proximity_placement_group: Optional[SubResource] = ..., 
                scheduled_events_policy: Optional[ScheduledEventsPolicy] = ..., 
                virtual_machines: Optional[list[SubResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.AvailabilitySetUpdate(UpdateResource):
        properties: Optional[AvailabilitySetProperties]
        sku: Optional[Sku]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvailabilitySetProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.AvailablePatchSummary(_Model):
        assessment_activity_id: Optional[str]
        critical_and_security_patch_count: Optional[int]
        error: Optional[ApiError]
        last_modified_time: Optional[datetime]
        other_patch_count: Optional[int]
        reboot_pending: Optional[bool]
        start_time: Optional[datetime]
        status: Optional[Union[str, PatchOperationStatus]]


    class azure.mgmt.compute.models.BillingProfile(_Model):
        max_price: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max_price: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.BootDiagnostics(_Model):
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


    class azure.mgmt.compute.models.BootDiagnosticsInstanceView(_Model):
        console_screenshot_blob_uri: Optional[str]
        serial_console_log_blob_uri: Optional[str]
        status: Optional[InstanceViewStatus]


    class azure.mgmt.compute.models.CachingTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.compute.models.CapacityReservation(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CapacityReservationProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CapacityReservationProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CapacityReservationGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CapacityReservationGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationGroupInstanceView(_Model):
        capacity_reservations: Optional[list[CapacityReservationInstanceViewWithName]]
        shared_subscription_ids: Optional[list[SubResourceReadOnly]]


    class azure.mgmt.compute.models.CapacityReservationGroupInstanceViewTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.compute.models.CapacityReservationGroupProperties(_Model):
        capacity_reservations: Optional[list[SubResourceReadOnly]]
        instance_view: Optional[CapacityReservationGroupInstanceView]
        reservation_type: Optional[Union[str, ReservationType]]
        sharing_profile: Optional[ResourceSharingProfile]
        virtual_machines_associated: Optional[list[SubResourceReadOnly]]

        @overload
        def __init__(
                self, 
                *, 
                reservation_type: Optional[Union[str, ReservationType]] = ..., 
                sharing_profile: Optional[ResourceSharingProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationGroupUpdate(UpdateResource):
        properties: Optional[CapacityReservationGroupProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapacityReservationGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationInstanceView(_Model):
        statuses: Optional[list[InstanceViewStatus]]
        utilization_info: Optional[CapacityReservationUtilization]

        @overload
        def __init__(
                self, 
                *, 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                utilization_info: Optional[CapacityReservationUtilization] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationInstanceViewTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.compute.models.CapacityReservationInstanceViewWithName(CapacityReservationInstanceView):
        name: Optional[str]
        statuses: list[InstanceViewStatus]
        utilization_info: CapacityReservationUtilization

        @overload
        def __init__(
                self, 
                *, 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                utilization_info: Optional[CapacityReservationUtilization] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationProfile(_Model):
        capacity_reservation_group: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                capacity_reservation_group: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationProperties(_Model):
        instance_view: Optional[CapacityReservationInstanceView]
        platform_fault_domain_count: Optional[int]
        provisioning_state: Optional[str]
        provisioning_time: Optional[datetime]
        reservation_id: Optional[str]
        schedule_profile: Optional[ScheduleProfile]
        time_created: Optional[datetime]
        virtual_machines_associated: Optional[list[SubResourceReadOnly]]

        @overload
        def __init__(
                self, 
                *, 
                schedule_profile: Optional[ScheduleProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationUpdate(UpdateResource):
        properties: Optional[CapacityReservationProperties]
        sku: Optional[Sku]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapacityReservationProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CapacityReservationUtilization(_Model):
        current_capacity: Optional[int]
        virtual_machines_allocated: Optional[list[SubResourceReadOnly]]


    class azure.mgmt.compute.models.CloudError(_Model):
        error: Optional[ApiError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ApiError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGallery(PirCommunityGalleryResource):
        identifier: CommunityGalleryIdentifier
        location: str
        name: str
        properties: Optional[CommunityGalleryProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[CommunityGalleryIdentifier] = ..., 
                properties: Optional[CommunityGalleryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryIdentifier(_Model):
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                unique_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryImage(PirCommunityGalleryResource):
        identifier: CommunityGalleryIdentifier
        location: str
        name: str
        properties: Optional[CommunityGalleryImageProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[CommunityGalleryIdentifier] = ..., 
                properties: Optional[CommunityGalleryImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryImageIdentifier(_Model):
        offer: Optional[str]
        publisher: Optional[str]
        sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryImageProperties(_Model):
        architecture: Optional[Union[str, Architecture]]
        artifact_tags: Optional[dict[str, str]]
        disallowed: Optional[Disallowed]
        disclaimer: Optional[str]
        end_of_life_date: Optional[datetime]
        eula: Optional[str]
        features: Optional[list[GalleryImageFeature]]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        identifier: CommunityGalleryImageIdentifier
        os_state: Union[str, OperatingSystemStateTypes]
        os_type: Union[str, OperatingSystemTypes]
        privacy_statement_uri: Optional[str]
        purchase_plan: Optional[ImagePurchasePlan]
        recommended: Optional[RecommendedMachineConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                architecture: Optional[Union[str, Architecture]] = ..., 
                artifact_tags: Optional[dict[str, str]] = ..., 
                disallowed: Optional[Disallowed] = ..., 
                disclaimer: Optional[str] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                eula: Optional[str] = ..., 
                features: Optional[list[GalleryImageFeature]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                identifier: CommunityGalleryImageIdentifier, 
                os_state: Union[str, OperatingSystemStateTypes], 
                os_type: Union[str, OperatingSystemTypes], 
                privacy_statement_uri: Optional[str] = ..., 
                purchase_plan: Optional[ImagePurchasePlan] = ..., 
                recommended: Optional[RecommendedMachineConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryImageVersion(PirCommunityGalleryResource):
        identifier: CommunityGalleryIdentifier
        location: str
        name: str
        properties: Optional[CommunityGalleryImageVersionProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[CommunityGalleryIdentifier] = ..., 
                properties: Optional[CommunityGalleryImageVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryImageVersionProperties(_Model):
        artifact_tags: Optional[dict[str, str]]
        disclaimer: Optional[str]
        end_of_life_date: Optional[datetime]
        exclude_from_latest: Optional[bool]
        published_date: Optional[datetime]
        storage_profile: Optional[SharedGalleryImageVersionStorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                artifact_tags: Optional[dict[str, str]] = ..., 
                disclaimer: Optional[str] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                published_date: Optional[datetime] = ..., 
                storage_profile: Optional[SharedGalleryImageVersionStorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryInfo(_Model):
        community_gallery_enabled: Optional[bool]
        eula: Optional[str]
        public_name_prefix: Optional[str]
        public_names: Optional[list[str]]
        publisher_contact: Optional[str]
        publisher_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                eula: Optional[str] = ..., 
                public_name_prefix: Optional[str] = ..., 
                publisher_contact: Optional[str] = ..., 
                publisher_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryMetadata(_Model):
        eula: Optional[str]
        privacy_statement_uri: Optional[str]
        public_names: list[str]
        publisher_contact: str
        publisher_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                eula: Optional[str] = ..., 
                privacy_statement_uri: Optional[str] = ..., 
                public_names: list[str], 
                publisher_contact: str, 
                publisher_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CommunityGalleryProperties(_Model):
        artifact_tags: Optional[dict[str, str]]
        community_metadata: Optional[CommunityGalleryMetadata]
        disclaimer: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                artifact_tags: Optional[dict[str, str]] = ..., 
                community_metadata: Optional[CommunityGalleryMetadata] = ..., 
                disclaimer: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ComponentNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_WINDOWS_SHELL_SETUP = "Microsoft-Windows-Shell-Setup"


    class azure.mgmt.compute.models.ConfidentialVMEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTED_VM_GUEST_STATE_ONLY_WITH_PMK = "EncryptedVMGuestStateOnlyWithPmk"
        ENCRYPTED_WITH_CMK = "EncryptedWithCmk"
        ENCRYPTED_WITH_PMK = "EncryptedWithPmk"
        NON_PERSISTED_TPM = "NonPersistedTPM"


    class azure.mgmt.compute.models.ConsistencyModeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_CONSISTENT = "ApplicationConsistent"
        CRASH_CONSISTENT = "CrashConsistent"
        FILE_SYSTEM_CONSISTENT = "FileSystemConsistent"


    class azure.mgmt.compute.models.ConvertToVirtualMachineScaleSetInput(_Model):
        virtual_machine_scale_set_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                virtual_machine_scale_set_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CopyCompletionError(_Model):
        error_code: Union[str, CopyCompletionErrorReason]
        error_message: str

        @overload
        def __init__(
                self, 
                *, 
                error_code: Union[str, CopyCompletionErrorReason], 
                error_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.CopyCompletionErrorReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY_SOURCE_NOT_FOUND = "CopySourceNotFound"


    class azure.mgmt.compute.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.compute.models.CreationData(_Model):
        create_option: Union[str, DiskCreateOption]
        elastic_san_resource_id: Optional[str]
        gallery_image_reference: Optional[ImageDiskReference]
        image_reference: Optional[ImageDiskReference]
        instant_access_duration_minutes: Optional[int]
        logical_sector_size: Optional[int]
        performance_plus: Optional[bool]
        provisioned_bandwidth_copy_speed: Optional[Union[str, ProvisionedBandwidthCopyOption]]
        security_data_uri: Optional[str]
        security_metadata_uri: Optional[str]
        source_resource_id: Optional[str]
        source_unique_id: Optional[str]
        source_uri: Optional[str]
        storage_account_id: Optional[str]
        upload_size_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                create_option: Union[str, DiskCreateOption], 
                elastic_san_resource_id: Optional[str] = ..., 
                gallery_image_reference: Optional[ImageDiskReference] = ..., 
                image_reference: Optional[ImageDiskReference] = ..., 
                instant_access_duration_minutes: Optional[int] = ..., 
                logical_sector_size: Optional[int] = ..., 
                performance_plus: Optional[bool] = ..., 
                provisioned_bandwidth_copy_speed: Optional[Union[str, ProvisionedBandwidthCopyOption]] = ..., 
                security_data_uri: Optional[str] = ..., 
                security_metadata_uri: Optional[str] = ..., 
                source_resource_id: Optional[str] = ..., 
                source_uri: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                upload_size_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DataAccessAuthMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        NONE = "None"


    class azure.mgmt.compute.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        detach_option: Optional[Union[str, DiskDetachOptionTypes]]
        disk_iops_read_write: Optional[int]
        disk_m_bps_read_write: Optional[int]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        lun: int
        managed_disk: Optional[ManagedDiskParameters]
        name: Optional[str]
        source_resource: Optional[ApiEntityReference]
        storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]]
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
                disk_iops_read_write: Optional[int] = ..., 
                disk_m_bps_read_write: Optional[int] = ..., 
                disk_size_gb: Optional[int] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                lun: int, 
                managed_disk: Optional[ManagedDiskParameters] = ..., 
                name: Optional[str] = ..., 
                source_resource: Optional[ApiEntityReference] = ..., 
                storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]] = ..., 
                to_be_detached: Optional[bool] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DataDiskImage(_Model):
        lun: Optional[int]


    class azure.mgmt.compute.models.DataDiskImageEncryption(DiskImageEncryption):
        disk_encryption_set_id: str
        lun: int

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                lun: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DataDisksToAttach(_Model):
        caching: Optional[Union[str, CachingTypes]]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        disk_id: str
        lun: Optional[int]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                disk_id: str, 
                lun: Optional[int] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DataDisksToDetach(_Model):
        detach_option: Optional[Union[str, DiskDetachOptionTypes]]
        disk_id: str

        @overload
        def __init__(
                self, 
                *, 
                detach_option: Optional[Union[str, DiskDetachOptionTypes]] = ..., 
                disk_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHost(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DedicatedHostProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DedicatedHostProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostAllocatableVM(_Model):
        count: Optional[float]
        vm_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[float] = ..., 
                vm_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostAvailableCapacity(_Model):
        allocatable_v_ms: Optional[list[DedicatedHostAllocatableVM]]

        @overload
        def __init__(
                self, 
                *, 
                allocatable_v_ms: Optional[list[DedicatedHostAllocatableVM]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DedicatedHostGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DedicatedHostGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostGroupInstanceView(_Model):
        hosts: Optional[list[DedicatedHostInstanceViewWithName]]

        @overload
        def __init__(
                self, 
                *, 
                hosts: Optional[list[DedicatedHostInstanceViewWithName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostGroupProperties(_Model):
        additional_capabilities: Optional[DedicatedHostGroupPropertiesAdditionalCapabilities]
        hosts: Optional[list[SubResourceReadOnly]]
        instance_view: Optional[DedicatedHostGroupInstanceView]
        platform_fault_domain_count: int
        support_automatic_placement: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[DedicatedHostGroupPropertiesAdditionalCapabilities] = ..., 
                platform_fault_domain_count: int, 
                support_automatic_placement: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostGroupPropertiesAdditionalCapabilities(_Model):
        ultra_ssd_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                ultra_ssd_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostGroupUpdate(UpdateResource):
        properties: Optional[DedicatedHostGroupProperties]
        tags: dict[str, str]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DedicatedHostGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostInstanceView(_Model):
        asset_id: Optional[str]
        available_capacity: Optional[DedicatedHostAvailableCapacity]
        statuses: Optional[list[InstanceViewStatus]]

        @overload
        def __init__(
                self, 
                *, 
                available_capacity: Optional[DedicatedHostAvailableCapacity] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostInstanceViewWithName(DedicatedHostInstanceView):
        asset_id: str
        available_capacity: DedicatedHostAvailableCapacity
        name: Optional[str]
        statuses: list[InstanceViewStatus]

        @overload
        def __init__(
                self, 
                *, 
                available_capacity: Optional[DedicatedHostAvailableCapacity] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostLicenseTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        WINDOWS_SERVER_HYBRID = "Windows_Server_Hybrid"
        WINDOWS_SERVER_PERPETUAL = "Windows_Server_Perpetual"


    class azure.mgmt.compute.models.DedicatedHostProperties(_Model):
        auto_replace_on_failure: Optional[bool]
        host_id: Optional[str]
        instance_view: Optional[DedicatedHostInstanceView]
        license_type: Optional[Union[str, DedicatedHostLicenseTypes]]
        platform_fault_domain: Optional[int]
        provisioning_state: Optional[str]
        provisioning_time: Optional[datetime]
        time_created: Optional[datetime]
        virtual_machines: Optional[list[SubResourceReadOnly]]

        @overload
        def __init__(
                self, 
                *, 
                auto_replace_on_failure: Optional[bool] = ..., 
                license_type: Optional[Union[str, DedicatedHostLicenseTypes]] = ..., 
                platform_fault_domain: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DedicatedHostUpdate(UpdateResource):
        properties: Optional[DedicatedHostProperties]
        sku: Optional[Sku]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DedicatedHostProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DefaultVirtualMachineScaleSetInfo(_Model):
        constrained_maximum_capacity: Optional[bool]
        default_virtual_machine_scale_set: Optional[SubResource]


    class azure.mgmt.compute.models.DeleteOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.compute.models.DiagnosticsProfile(_Model):
        boot_diagnostics: Optional[BootDiagnostics]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnostics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiffDiskOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"


    class azure.mgmt.compute.models.DiffDiskPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_DISK = "CacheDisk"
        NVME_DISK = "NvmeDisk"
        RESOURCE_DISK = "ResourceDisk"


    class azure.mgmt.compute.models.DiffDiskSettings(_Model):
        enable_full_caching: Optional[bool]
        option: Optional[Union[str, DiffDiskOptions]]
        placement: Optional[Union[str, DiffDiskPlacement]]

        @overload
        def __init__(
                self, 
                *, 
                enable_full_caching: Optional[bool] = ..., 
                option: Optional[Union[str, DiffDiskOptions]] = ..., 
                placement: Optional[Union[str, DiffDiskPlacement]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Disallowed(_Model):
        disk_types: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                disk_types: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DisallowedConfiguration(_Model):
        vm_disk_type: Optional[Union[str, VmDiskTypes]]

        @overload
        def __init__(
                self, 
                *, 
                vm_disk_type: Optional[Union[str, VmDiskTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Disk(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        managed_by: Optional[str]
        managed_by_extended: Optional[list[str]]
        name: str
        properties: Optional[DiskProperties]
        sku: Optional[DiskSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[DiskProperties] = ..., 
                sku: Optional[DiskSku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskAccess(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[DiskAccessProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[DiskAccessProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskAccessProperties(_Model):
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        time_created: Optional[datetime]


    class azure.mgmt.compute.models.DiskAccessUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskControllerTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NV_ME = "NVMe"
        SCSI = "SCSI"


    class azure.mgmt.compute.models.DiskCreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "Attach"
        COPY = "Copy"
        COPY_FROM_SAN_SNAPSHOT = "CopyFromSanSnapshot"
        COPY_START = "CopyStart"
        EMPTY = "Empty"
        FROM_IMAGE = "FromImage"
        IMPORT = "Import"
        IMPORT_SECURE = "ImportSecure"
        RESTORE = "Restore"
        UPLOAD = "Upload"
        UPLOAD_PREPARED_SECURE = "UploadPreparedSecure"


    class azure.mgmt.compute.models.DiskCreateOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "Attach"
        COPY = "Copy"
        EMPTY = "Empty"
        FROM_IMAGE = "FromImage"
        RESTORE = "Restore"


    class azure.mgmt.compute.models.DiskDeleteOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        DETACH = "Detach"


    class azure.mgmt.compute.models.DiskDetachOptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCE_DETACH = "ForceDetach"


    class azure.mgmt.compute.models.DiskEncryptionSet(TrackedResource):
        id: str
        identity: Optional[EncryptionSetIdentity]
        location: str
        name: str
        properties: Optional[EncryptionSetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EncryptionSetIdentity] = ..., 
                location: str, 
                properties: Optional[EncryptionSetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskEncryptionSetIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.compute.models.DiskEncryptionSetParameters(SubResource):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskEncryptionSetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM_ENCRYPTED_WITH_CUSTOMER_KEY = "ConfidentialVmEncryptedWithCustomerKey"
        ENCRYPTION_AT_REST_WITH_CUSTOMER_KEY = "EncryptionAtRestWithCustomerKey"
        ENCRYPTION_AT_REST_WITH_PLATFORM_AND_CUSTOMER_KEYS = "EncryptionAtRestWithPlatformAndCustomerKeys"


    class azure.mgmt.compute.models.DiskEncryptionSetUpdate(_Model):
        identity: Optional[EncryptionSetIdentity]
        properties: Optional[DiskEncryptionSetUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EncryptionSetIdentity] = ..., 
                properties: Optional[DiskEncryptionSetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskEncryptionSetUpdateProperties(_Model):
        active_key: Optional[KeyForDiskEncryptionSet]
        encryption_type: Optional[Union[str, DiskEncryptionSetType]]
        federated_client_id: Optional[str]
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                active_key: Optional[KeyForDiskEncryptionSet] = ..., 
                encryption_type: Optional[Union[str, DiskEncryptionSetType]] = ..., 
                federated_client_id: Optional[str] = ..., 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskEncryptionSettings(_Model):
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


    class azure.mgmt.compute.models.DiskImageEncryption(_Model):
        disk_encryption_set_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskInstanceView(_Model):
        encryption_settings: Optional[list[DiskEncryptionSettings]]
        name: Optional[str]
        statuses: Optional[list[InstanceViewStatus]]
        storage_alignment_status: Optional[Union[str, StorageAlignmentStatus]]

        @overload
        def __init__(
                self, 
                *, 
                encryption_settings: Optional[list[DiskEncryptionSettings]] = ..., 
                name: Optional[str] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                storage_alignment_status: Optional[Union[str, StorageAlignmentStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskProperties(_Model):
        availability_policy: Optional[AvailabilityPolicy]
        bursting_enabled: Optional[bool]
        bursting_enabled_time: Optional[datetime]
        completion_percent: Optional[float]
        creation_data: CreationData
        data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]]
        disk_access_id: Optional[str]
        disk_iops_read_only: Optional[int]
        disk_iops_read_write: Optional[int]
        disk_m_bps_read_only: Optional[int]
        disk_m_bps_read_write: Optional[int]
        disk_size_bytes: Optional[int]
        disk_size_gb: Optional[int]
        disk_state: Optional[Union[str, DiskState]]
        encryption: Optional[Encryption]
        encryption_settings_collection: Optional[EncryptionSettingsCollection]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        last_ownership_update_time: Optional[datetime]
        max_shares: Optional[int]
        network_access_policy: Optional[Union[str, NetworkAccessPolicy]]
        optimized_for_frequent_attach: Optional[bool]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        property_updates_in_progress: Optional[PropertyUpdatesInProgress]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        purchase_plan: Optional[DiskPurchasePlan]
        security_profile: Optional[DiskSecurityProfile]
        share_info: Optional[list[ShareInfoElement]]
        supported_capabilities: Optional[SupportedCapabilities]
        supports_hibernation: Optional[bool]
        tier: Optional[str]
        time_created: Optional[datetime]
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_policy: Optional[AvailabilityPolicy] = ..., 
                bursting_enabled: Optional[bool] = ..., 
                completion_percent: Optional[float] = ..., 
                creation_data: CreationData, 
                data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]] = ..., 
                disk_access_id: Optional[str] = ..., 
                disk_iops_read_only: Optional[int] = ..., 
                disk_iops_read_write: Optional[int] = ..., 
                disk_m_bps_read_only: Optional[int] = ..., 
                disk_m_bps_read_write: Optional[int] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption: Optional[Encryption] = ..., 
                encryption_settings_collection: Optional[EncryptionSettingsCollection] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                max_shares: Optional[int] = ..., 
                network_access_policy: Optional[Union[str, NetworkAccessPolicy]] = ..., 
                optimized_for_frequent_attach: Optional[bool] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                purchase_plan: Optional[DiskPurchasePlan] = ..., 
                security_profile: Optional[DiskSecurityProfile] = ..., 
                supported_capabilities: Optional[SupportedCapabilities] = ..., 
                supports_hibernation: Optional[bool] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskPurchasePlan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskRestorePoint(ProxyResource):
        id: str
        name: str
        properties: Optional[DiskRestorePointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiskRestorePointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskRestorePointAttributes(SubResourceReadOnly):
        encryption: Optional[RestorePointEncryption]
        id: str
        source_disk_restore_point: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[RestorePointEncryption] = ..., 
                source_disk_restore_point: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskRestorePointInstanceView(_Model):
        id: Optional[str]
        replication_status: Optional[DiskRestorePointReplicationStatus]
        snapshot_access_state: Optional[Union[str, SnapshotAccessState]]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                replication_status: Optional[DiskRestorePointReplicationStatus] = ..., 
                snapshot_access_state: Optional[Union[str, SnapshotAccessState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskRestorePointProperties(_Model):
        completion_percent: Optional[float]
        disk_access_id: Optional[str]
        encryption: Optional[Encryption]
        family_id: Optional[str]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        logical_sector_size: Optional[int]
        network_access_policy: Optional[Union[str, NetworkAccessPolicy]]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        purchase_plan: Optional[DiskPurchasePlan]
        replication_state: Optional[str]
        security_profile: Optional[DiskSecurityProfile]
        source_resource_id: Optional[str]
        source_resource_location: Optional[str]
        source_unique_id: Optional[str]
        supported_capabilities: Optional[SupportedCapabilities]
        supports_hibernation: Optional[bool]
        time_created: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                completion_percent: Optional[float] = ..., 
                disk_access_id: Optional[str] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                network_access_policy: Optional[Union[str, NetworkAccessPolicy]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                purchase_plan: Optional[DiskPurchasePlan] = ..., 
                security_profile: Optional[DiskSecurityProfile] = ..., 
                supported_capabilities: Optional[SupportedCapabilities] = ..., 
                supports_hibernation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskRestorePointReplicationStatus(_Model):
        completion_percent: Optional[int]
        status: Optional[InstanceViewStatus]

        @overload
        def __init__(
                self, 
                *, 
                completion_percent: Optional[int] = ..., 
                status: Optional[InstanceViewStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskSecurityProfile(_Model):
        secure_vm_disk_encryption_set_id: Optional[str]
        security_type: Optional[Union[str, DiskSecurityTypes]]

        @overload
        def __init__(
                self, 
                *, 
                secure_vm_disk_encryption_set_id: Optional[str] = ..., 
                security_type: Optional[Union[str, DiskSecurityTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskSecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM_DISK_ENCRYPTED_WITH_CUSTOMER_KEY = "ConfidentialVM_DiskEncryptedWithCustomerKey"
        CONFIDENTIAL_VM_DISK_ENCRYPTED_WITH_PLATFORM_KEY = "ConfidentialVM_DiskEncryptedWithPlatformKey"
        CONFIDENTIAL_VM_NON_PERSISTED_TPM = "ConfidentialVM_NonPersistedTPM"
        CONFIDENTIAL_VM_VMGUEST_STATE_ONLY_ENCRYPTED_WITH_PLATFORM_KEY = "ConfidentialVM_VMGuestStateOnlyEncryptedWithPlatformKey"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.compute.models.DiskSku(_Model):
        name: Optional[Union[str, DiskStorageAccountTypes]]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, DiskStorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DiskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_SAS = "ActiveSAS"
        ACTIVE_SAS_FROZEN = "ActiveSASFrozen"
        ACTIVE_UPLOAD = "ActiveUpload"
        ATTACHED = "Attached"
        FROZEN = "Frozen"
        READY_TO_UPLOAD = "ReadyToUpload"
        RESERVED = "Reserved"
        UNATTACHED = "Unattached"


    class azure.mgmt.compute.models.DiskStorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.compute.models.DiskUpdate(_Model):
        properties: Optional[DiskUpdateProperties]
        sku: Optional[DiskSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiskUpdateProperties] = ..., 
                sku: Optional[DiskSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.DiskUpdateProperties(_Model):
        availability_policy: Optional[AvailabilityPolicy]
        bursting_enabled: Optional[bool]
        data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]]
        disk_access_id: Optional[str]
        disk_iops_read_only: Optional[int]
        disk_iops_read_write: Optional[int]
        disk_m_bps_read_only: Optional[int]
        disk_m_bps_read_write: Optional[int]
        disk_size_gb: Optional[int]
        encryption: Optional[Encryption]
        encryption_settings_collection: Optional[EncryptionSettingsCollection]
        max_shares: Optional[int]
        network_access_policy: Optional[Union[str, NetworkAccessPolicy]]
        optimized_for_frequent_attach: Optional[bool]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        property_updates_in_progress: Optional[PropertyUpdatesInProgress]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        purchase_plan: Optional[DiskPurchasePlan]
        supported_capabilities: Optional[SupportedCapabilities]
        supports_hibernation: Optional[bool]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability_policy: Optional[AvailabilityPolicy] = ..., 
                bursting_enabled: Optional[bool] = ..., 
                data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]] = ..., 
                disk_access_id: Optional[str] = ..., 
                disk_iops_read_only: Optional[int] = ..., 
                disk_iops_read_write: Optional[int] = ..., 
                disk_m_bps_read_only: Optional[int] = ..., 
                disk_m_bps_read_write: Optional[int] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption: Optional[Encryption] = ..., 
                encryption_settings_collection: Optional[EncryptionSettingsCollection] = ..., 
                max_shares: Optional[int] = ..., 
                network_access_policy: Optional[Union[str, NetworkAccessPolicy]] = ..., 
                optimized_for_frequent_attach: Optional[bool] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                purchase_plan: Optional[DiskPurchasePlan] = ..., 
                supported_capabilities: Optional[SupportedCapabilities] = ..., 
                supports_hibernation: Optional[bool] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.DomainNameLabelScopeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.compute.models.EdgeZoneStorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.compute.models.Encryption(_Model):
        disk_encryption_set_id: Optional[str]
        type: Optional[Union[str, EncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                type: Optional[Union[str, EncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionIdentity(_Model):
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionImages(_Model):
        data_disk_images: Optional[list[DataDiskImageEncryption]]
        os_disk_image: Optional[OSDiskImageEncryption]

        @overload
        def __init__(
                self, 
                *, 
                data_disk_images: Optional[list[DataDiskImageEncryption]] = ..., 
                os_disk_image: Optional[OSDiskImageEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionSetIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, DiskEncryptionSetIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, DiskEncryptionSetIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionSetProperties(_Model):
        active_key: Optional[KeyForDiskEncryptionSet]
        auto_key_rotation_error: Optional[ApiError]
        encryption_type: Optional[Union[str, DiskEncryptionSetType]]
        federated_client_id: Optional[str]
        last_key_rotation_timestamp: Optional[datetime]
        previous_keys: Optional[list[KeyForDiskEncryptionSet]]
        provisioning_state: Optional[str]
        rotation_to_latest_key_version_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                active_key: Optional[KeyForDiskEncryptionSet] = ..., 
                encryption_type: Optional[Union[str, DiskEncryptionSetType]] = ..., 
                federated_client_id: Optional[str] = ..., 
                rotation_to_latest_key_version_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionSettingsCollection(_Model):
        enabled: bool
        encryption_settings: Optional[list[EncryptionSettingsElement]]
        encryption_settings_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool, 
                encryption_settings: Optional[list[EncryptionSettingsElement]] = ..., 
                encryption_settings_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionSettingsElement(_Model):
        disk_encryption_key: Optional[KeyVaultAndSecretReference]
        key_encryption_key: Optional[KeyVaultAndKeyReference]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_key: Optional[KeyVaultAndSecretReference] = ..., 
                key_encryption_key: Optional[KeyVaultAndKeyReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTION_AT_REST_WITH_CUSTOMER_KEY = "EncryptionAtRestWithCustomerKey"
        ENCRYPTION_AT_REST_WITH_PLATFORM_AND_CUSTOMER_KEYS = "EncryptionAtRestWithPlatformAndCustomerKeys"
        ENCRYPTION_AT_REST_WITH_PLATFORM_KEY = "EncryptionAtRestWithPlatformKey"


    class azure.mgmt.compute.models.EndpointAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.compute.models.EndpointTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMDS = "IMDS"
        WIRE_SERVER = "WireServer"


    class azure.mgmt.compute.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.compute.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.compute.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.EventGridAndResourceGraph(_Model):
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


    class azure.mgmt.compute.models.ExecutedValidation(_Model):
        execution_time: Optional[datetime]
        status: Optional[Union[str, ValidationStatus]]
        type: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                execution_time: Optional[datetime] = ..., 
                status: Optional[Union[str, ValidationStatus]] = ..., 
                type: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ExecutionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.ExpandTypeForListVMs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.compute.models.ExpandTypesForGetCapacityReservationGroups(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VIRTUAL_MACHINES_REF = "virtualMachines/$ref"
        VIRTUAL_MACHINE_SCALE_SET_VMS_REF = "virtualMachineScaleSetVMs/$ref"


    class azure.mgmt.compute.models.ExpandTypesForGetVMScaleSets(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USER_DATA = "userData"


    class azure.mgmt.compute.models.ExpandTypesForListVMs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.compute.models.ExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, ExtendedLocationTypes]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ExtendedLocationTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.compute.models.ExtendedLocationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.compute.models.ExternalHealthPolicy(_Model):
        enabled: Optional[bool]
        expiry_duration: Optional[timedelta]
        grace_period: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expiry_duration: Optional[timedelta] = ..., 
                grace_period: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.FileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VHD = "VHD"
        VHDX = "VHDX"


    class azure.mgmt.compute.models.Gallery(TrackedResource):
        id: str
        identity: Optional[GalleryIdentity]
        location: str
        name: str
        properties: Optional[GalleryProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[GalleryIdentity] = ..., 
                location: str, 
                properties: Optional[GalleryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryApplication(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryApplicationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryApplicationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationCustomAction(_Model):
        description: Optional[str]
        name: str
        parameters: Optional[list[GalleryApplicationCustomActionParameter]]
        script: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[list[GalleryApplicationCustomActionParameter]] = ..., 
                script: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationCustomActionParameter(_Model):
        default_value: Optional[str]
        description: Optional[str]
        name: str
        required: Optional[bool]
        type: Optional[Union[str, GalleryApplicationCustomActionParameterType]]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                required: Optional[bool] = ..., 
                type: Optional[Union[str, GalleryApplicationCustomActionParameterType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationCustomActionParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_DATA_BLOB = "ConfigurationDataBlob"
        LOG_OUTPUT_BLOB = "LogOutputBlob"
        STRING = "String"


    class azure.mgmt.compute.models.GalleryApplicationProperties(_Model):
        custom_actions: Optional[list[GalleryApplicationCustomAction]]
        description: Optional[str]
        end_of_life_date: Optional[datetime]
        eula: Optional[str]
        privacy_statement_uri: Optional[str]
        release_note_uri: Optional[str]
        supported_os_type: Union[str, OperatingSystemTypes]

        @overload
        def __init__(
                self, 
                *, 
                custom_actions: Optional[list[GalleryApplicationCustomAction]] = ..., 
                description: Optional[str] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                eula: Optional[str] = ..., 
                privacy_statement_uri: Optional[str] = ..., 
                release_note_uri: Optional[str] = ..., 
                supported_os_type: Union[str, OperatingSystemTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationScriptRebootBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        RERUN = "Rerun"


    class azure.mgmt.compute.models.GalleryApplicationUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryApplicationProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryApplicationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryApplicationVersionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryApplicationVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationVersionProperties(_Model):
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        publishing_profile: GalleryApplicationVersionPublishingProfile
        replication_status: Optional[ReplicationStatus]
        safety_profile: Optional[GalleryApplicationVersionSafetyProfile]

        @overload
        def __init__(
                self, 
                *, 
                publishing_profile: GalleryApplicationVersionPublishingProfile, 
                safety_profile: Optional[GalleryApplicationVersionSafetyProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationVersionPublishingProfile(GalleryArtifactPublishingProfileBase):
        advanced_settings: Optional[dict[str, str]]
        custom_actions: Optional[list[GalleryApplicationCustomAction]]
        enable_health_check: Optional[bool]
        end_of_life_date: datetime
        exclude_from_latest: bool
        manage_actions: Optional[UserArtifactManage]
        published_date: datetime
        replica_count: int
        replication_mode: Union[str, ReplicationMode]
        settings: Optional[UserArtifactSettings]
        source: UserArtifactSource
        storage_account_strategy: Union[str, StorageAccountStrategy]
        storage_account_type: Union[str, StorageAccountType]
        target_extended_locations: list[GalleryTargetExtendedLocation]
        target_regions: list[TargetRegion]

        @overload
        def __init__(
                self, 
                *, 
                advanced_settings: Optional[dict[str, str]] = ..., 
                custom_actions: Optional[list[GalleryApplicationCustomAction]] = ..., 
                enable_health_check: Optional[bool] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                manage_actions: Optional[UserArtifactManage] = ..., 
                replica_count: Optional[int] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                settings: Optional[UserArtifactSettings] = ..., 
                source: UserArtifactSource, 
                storage_account_strategy: Optional[Union[str, StorageAccountStrategy]] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ..., 
                target_extended_locations: Optional[list[GalleryTargetExtendedLocation]] = ..., 
                target_regions: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationVersionSafetyProfile(GalleryArtifactSafetyProfileBase):
        allow_deletion_of_replicated_locations: bool

        @overload
        def __init__(
                self, 
                *, 
                allow_deletion_of_replicated_locations: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryApplicationVersionUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryApplicationVersionProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryApplicationVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryArtifactPublishingProfileBase(_Model):
        end_of_life_date: Optional[datetime]
        exclude_from_latest: Optional[bool]
        published_date: Optional[datetime]
        replica_count: Optional[int]
        replication_mode: Optional[Union[str, ReplicationMode]]
        storage_account_strategy: Optional[Union[str, StorageAccountStrategy]]
        storage_account_type: Optional[Union[str, StorageAccountType]]
        target_extended_locations: Optional[list[GalleryTargetExtendedLocation]]
        target_regions: Optional[list[TargetRegion]]

        @overload
        def __init__(
                self, 
                *, 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                replica_count: Optional[int] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                storage_account_strategy: Optional[Union[str, StorageAccountStrategy]] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ..., 
                target_extended_locations: Optional[list[GalleryTargetExtendedLocation]] = ..., 
                target_regions: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryArtifactSafetyProfileBase(_Model):
        allow_deletion_of_replicated_locations: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_deletion_of_replicated_locations: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryArtifactVersionFullSource(GalleryArtifactVersionSource):
        community_gallery_image_id: Optional[str]
        id: str
        virtual_machine_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                virtual_machine_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryArtifactVersionSource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryDataDiskImage(GalleryDiskImage):
        host_caching: Union[str, HostCaching]
        lun: int
        size_in_gb: int
        source: GalleryDiskImageSource

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, HostCaching]] = ..., 
                lun: int, 
                source: Optional[GalleryDiskImageSource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryDiskImage(_Model):
        host_caching: Optional[Union[str, HostCaching]]
        size_in_gb: Optional[int]
        source: Optional[GalleryDiskImageSource]

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, HostCaching]] = ..., 
                source: Optional[GalleryDiskImageSource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryDiskImageSource(GalleryArtifactVersionSource):
        id: str
        storage_account_id: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                storage_account_id: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryExpandParams(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHARING_PROFILE_GROUPS = "SharingProfile/Groups"


    class azure.mgmt.compute.models.GalleryExtendedLocation(_Model):
        name: Optional[str]
        type: Optional[Union[str, GalleryExtendedLocationType]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Union[str, GalleryExtendedLocationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE_ZONE = "EdgeZone"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.GalleryIdentifier(_Model):
        unique_name: Optional[str]


    class azure.mgmt.compute.models.GalleryIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImage(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryImageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryImageFeature(_Model):
        name: Optional[str]
        starts_at_version: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                starts_at_version: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageIdentifier(_Model):
        offer: str
        publisher: str
        sku: str

        @overload
        def __init__(
                self, 
                *, 
                offer: str, 
                publisher: str, 
                sku: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageProperties(_Model):
        allow_update_image: Optional[bool]
        architecture: Optional[Union[str, Architecture]]
        description: Optional[str]
        disallowed: Optional[Disallowed]
        end_of_life_date: Optional[datetime]
        eula: Optional[str]
        features: Optional[list[GalleryImageFeature]]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        identifier: GalleryImageIdentifier
        os_state: Union[str, OperatingSystemStateTypes]
        os_type: Union[str, OperatingSystemTypes]
        privacy_statement_uri: Optional[str]
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        purchase_plan: Optional[ImagePurchasePlan]
        recommended: Optional[RecommendedMachineConfiguration]
        release_note_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_update_image: Optional[bool] = ..., 
                architecture: Optional[Union[str, Architecture]] = ..., 
                description: Optional[str] = ..., 
                disallowed: Optional[Disallowed] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                eula: Optional[str] = ..., 
                features: Optional[list[GalleryImageFeature]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                identifier: GalleryImageIdentifier, 
                os_state: Union[str, OperatingSystemStateTypes], 
                os_type: Union[str, OperatingSystemTypes], 
                privacy_statement_uri: Optional[str] = ..., 
                purchase_plan: Optional[ImagePurchasePlan] = ..., 
                recommended: Optional[RecommendedMachineConfiguration] = ..., 
                release_note_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryImageProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryImageVersionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryImageVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionProperties(_Model):
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        publishing_profile: Optional[GalleryImageVersionPublishingProfile]
        replication_status: Optional[ReplicationStatus]
        restore: Optional[bool]
        safety_profile: Optional[GalleryImageVersionSafetyProfile]
        security_profile: Optional[ImageVersionSecurityProfile]
        storage_profile: GalleryImageVersionStorageProfile
        validations_profile: Optional[ValidationsProfile]

        @overload
        def __init__(
                self, 
                *, 
                publishing_profile: Optional[GalleryImageVersionPublishingProfile] = ..., 
                restore: Optional[bool] = ..., 
                safety_profile: Optional[GalleryImageVersionSafetyProfile] = ..., 
                security_profile: Optional[ImageVersionSecurityProfile] = ..., 
                storage_profile: GalleryImageVersionStorageProfile
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionPublishingProfile(GalleryArtifactPublishingProfileBase):
        end_of_life_date: datetime
        exclude_from_latest: bool
        published_date: datetime
        replica_count: int
        replication_mode: Union[str, ReplicationMode]
        storage_account_strategy: Union[str, StorageAccountStrategy]
        storage_account_type: Union[str, StorageAccountType]
        target_extended_locations: list[GalleryTargetExtendedLocation]
        target_regions: list[TargetRegion]

        @overload
        def __init__(
                self, 
                *, 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                replica_count: Optional[int] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                storage_account_strategy: Optional[Union[str, StorageAccountStrategy]] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ..., 
                target_extended_locations: Optional[list[GalleryTargetExtendedLocation]] = ..., 
                target_regions: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionSafetyProfile(GalleryArtifactSafetyProfileBase):
        allow_deletion_of_replicated_locations: bool
        block_deletion_before_end_of_life: Optional[bool]
        policy_violations: Optional[list[PolicyViolation]]
        reported_for_policy_violation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_deletion_of_replicated_locations: Optional[bool] = ..., 
                block_deletion_before_end_of_life: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionStorageProfile(_Model):
        data_disk_images: Optional[list[GalleryDataDiskImage]]
        os_disk_image: Optional[GalleryOSDiskImage]
        source: Optional[GalleryArtifactVersionFullSource]

        @overload
        def __init__(
                self, 
                *, 
                data_disk_images: Optional[list[GalleryDataDiskImage]] = ..., 
                os_disk_image: Optional[GalleryOSDiskImage] = ..., 
                source: Optional[GalleryArtifactVersionFullSource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionUefiSettings(_Model):
        additional_signatures: Optional[UefiKeySignatures]
        signature_template_names: Optional[list[Union[str, UefiSignatureTemplateName]]]

        @overload
        def __init__(
                self, 
                *, 
                additional_signatures: Optional[UefiKeySignatures] = ..., 
                signature_template_names: Optional[list[Union[str, UefiSignatureTemplateName]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryImageVersionUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryImageVersionProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryImageVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfile(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryInVMAccessControlProfileProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryInVMAccessControlProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfileProperties(GalleryResourceProfilePropertiesBase):
        applicable_host_endpoint: Union[str, EndpointTypes]
        description: Optional[str]
        os_type: Union[str, OperatingSystemTypes]
        provisioning_state: Union[str, GalleryProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                applicable_host_endpoint: Union[str, EndpointTypes], 
                description: Optional[str] = ..., 
                os_type: Union[str, OperatingSystemTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfileUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryInVMAccessControlProfileProperties]
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryInVMAccessControlProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfileVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryInVMAccessControlProfileVersionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryInVMAccessControlProfileVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfileVersionProperties(GalleryResourceProfileVersionPropertiesBase):
        default_access: Union[str, EndpointAccess]
        exclude_from_latest: bool
        mode: Union[str, AccessControlRulesMode]
        provisioning_state: Union[str, GalleryProvisioningState]
        published_date: datetime
        replication_status: ReplicationStatus
        rules: Optional[AccessControlRules]
        target_locations: list[TargetRegion]

        @overload
        def __init__(
                self, 
                *, 
                default_access: Union[str, EndpointAccess], 
                exclude_from_latest: Optional[bool] = ..., 
                mode: Union[str, AccessControlRulesMode], 
                rules: Optional[AccessControlRules] = ..., 
                target_locations: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryInVMAccessControlProfileVersionUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryInVMAccessControlProfileVersionProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryInVMAccessControlProfileVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryOSDiskImage(GalleryDiskImage):
        host_caching: Union[str, HostCaching]
        size_in_gb: int
        source: GalleryDiskImageSource

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, HostCaching]] = ..., 
                source: Optional[GalleryDiskImageSource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryProperties(_Model):
        description: Optional[str]
        identifier: Optional[GalleryIdentifier]
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        sharing_profile: Optional[SharingProfile]
        sharing_status: Optional[SharingStatus]
        soft_delete_policy: Optional[SoftDeletePolicy]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                identifier: Optional[GalleryIdentifier] = ..., 
                sharing_profile: Optional[SharingProfile] = ..., 
                soft_delete_policy: Optional[SoftDeletePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.compute.models.GalleryResourceProfilePropertiesBase(_Model):
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]


    class azure.mgmt.compute.models.GalleryResourceProfileVersionPropertiesBase(_Model):
        exclude_from_latest: Optional[bool]
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        published_date: Optional[datetime]
        replication_status: Optional[ReplicationStatus]
        target_locations: Optional[list[TargetRegion]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_from_latest: Optional[bool] = ..., 
                target_locations: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScript(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryScriptProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryScriptProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptParameter(GenericGalleryParameter):
        default_value: str
        description: str
        enum_values: Optional[list[str]]
        max_value: Optional[str]
        min_value: Optional[str]
        name: str
        required: bool
        type: Optional[Union[str, GalleryScriptParameterType]]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enum_values: Optional[list[str]] = ..., 
                max_value: Optional[str] = ..., 
                min_value: Optional[str] = ..., 
                name: str, 
                required: Optional[bool] = ..., 
                type: Optional[Union[str, GalleryScriptParameterType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "Boolean"
        DOUBLE = "Double"
        ENUM = "Enum"
        INT = "Int"
        STRING = "String"


    class azure.mgmt.compute.models.GalleryScriptProperties(_Model):
        description: Optional[str]
        end_of_life_date: Optional[datetime]
        eula: Optional[str]
        privacy_statement_uri: Optional[str]
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        release_note_uri: Optional[str]
        supported_os_type: Union[str, OperatingSystemTypes]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                eula: Optional[str] = ..., 
                privacy_statement_uri: Optional[str] = ..., 
                release_note_uri: Optional[str] = ..., 
                supported_os_type: Union[str, OperatingSystemTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryScriptProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryScriptProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptVersion(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GalleryScriptVersionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GalleryScriptVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptVersionProperties(_Model):
        provisioning_state: Optional[Union[str, GalleryProvisioningState]]
        publishing_profile: GalleryScriptVersionPublishingProfile
        replication_status: Optional[ReplicationStatus]
        safety_profile: Optional[GalleryScriptVersionSafetyProfile]

        @overload
        def __init__(
                self, 
                *, 
                publishing_profile: GalleryScriptVersionPublishingProfile, 
                safety_profile: Optional[GalleryScriptVersionSafetyProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptVersionPublishingProfile(GalleryArtifactPublishingProfileBase):
        end_of_life_date: datetime
        exclude_from_latest: bool
        published_date: datetime
        replica_count: int
        replication_mode: Union[str, ReplicationMode]
        source: ScriptSource
        storage_account_strategy: Union[str, StorageAccountStrategy]
        storage_account_type: Union[str, StorageAccountType]
        target_extended_locations: list[GalleryTargetExtendedLocation]
        target_regions: list[TargetRegion]

        @overload
        def __init__(
                self, 
                *, 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                replica_count: Optional[int] = ..., 
                replication_mode: Optional[Union[str, ReplicationMode]] = ..., 
                source: ScriptSource, 
                storage_account_strategy: Optional[Union[str, StorageAccountStrategy]] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ..., 
                target_extended_locations: Optional[list[GalleryTargetExtendedLocation]] = ..., 
                target_regions: Optional[list[TargetRegion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptVersionSafetyProfile(GalleryArtifactSafetyProfileBase):
        allow_deletion_of_replicated_locations: bool

        @overload
        def __init__(
                self, 
                *, 
                allow_deletion_of_replicated_locations: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryScriptVersionUpdate(UpdateResourceDefinition):
        id: str
        name: str
        properties: Optional[GalleryScriptVersionProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryScriptVersionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GallerySharingPermissionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMUNITY = "Community"
        GROUPS = "Groups"
        PRIVATE = "Private"


    class azure.mgmt.compute.models.GallerySoftDeletedResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[GallerySoftDeletedResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[GallerySoftDeletedResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GallerySoftDeletedResourceProperties(_Model):
        resource_arm_id: Optional[str]
        soft_deleted_artifact_type: Optional[Union[str, SoftDeletedArtifactTypes]]
        soft_deleted_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_arm_id: Optional[str] = ..., 
                soft_deleted_artifact_type: Optional[Union[str, SoftDeletedArtifactTypes]] = ..., 
                soft_deleted_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryTargetExtendedLocation(_Model):
        encryption: Optional[EncryptionImages]
        extended_location: Optional[GalleryExtendedLocation]
        extended_location_replica_count: Optional[int]
        name: Optional[str]
        storage_account_type: Optional[Union[str, EdgeZoneStorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[EncryptionImages] = ..., 
                extended_location: Optional[GalleryExtendedLocation] = ..., 
                extended_location_replica_count: Optional[int] = ..., 
                name: Optional[str] = ..., 
                storage_account_type: Optional[Union[str, EdgeZoneStorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GalleryUpdate(UpdateResourceDefinition):
        id: str
        identity: Optional[GalleryIdentity]
        name: str
        properties: Optional[GalleryProperties]
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[GalleryIdentity] = ..., 
                properties: Optional[GalleryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.GenericGalleryParameter(_Model):
        default_value: Optional[str]
        description: Optional[str]
        name: str
        required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.GrantAccessData(_Model):
        access: Union[str, AccessLevel]
        duration_in_seconds: int
        file_format: Optional[Union[str, FileFormat]]
        get_secure_vm_guest_state_sas: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                access: Union[str, AccessLevel], 
                duration_in_seconds: int, 
                file_format: Optional[Union[str, FileFormat]] = ..., 
                get_secure_vm_guest_state_sas: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.HardwareProfile(_Model):
        vm_size: Optional[Union[str, VirtualMachineSizeTypes]]
        vm_size_properties: Optional[VMSizeProperties]

        @overload
        def __init__(
                self, 
                *, 
                vm_size: Optional[Union[str, VirtualMachineSizeTypes]] = ..., 
                vm_size_properties: Optional[VMSizeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.HighSpeedInterconnectPlacement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TRUNK = "Trunk"


    class azure.mgmt.compute.models.HostCaching(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.compute.models.HostEndpointSettings(_Model):
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


    class azure.mgmt.compute.models.HyperVGeneration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.compute.models.HyperVGenerationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.compute.models.HyperVGenerationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.compute.models.IPVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.compute.models.IPVersions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        I_PV4 = "IPv4"
        I_PV6 = "IPv6"


    class azure.mgmt.compute.models.Image(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[ImageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[ImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.ImageDataDisk(ImageDisk):
        blob_uri: str
        caching: Union[str, CachingTypes]
        disk_encryption_set: DiskEncryptionSetParameters
        disk_size_gb: int
        lun: int
        managed_disk: SubResource
        snapshot: SubResource
        storage_account_type: Union[str, StorageAccountTypes]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                disk_size_gb: Optional[int] = ..., 
                lun: int, 
                managed_disk: Optional[SubResource] = ..., 
                snapshot: Optional[SubResource] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageDeprecationStatus(_Model):
        alternative_option: Optional[AlternativeOption]
        image_state: Optional[Union[str, ImageState]]
        scheduled_deprecation_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                alternative_option: Optional[AlternativeOption] = ..., 
                image_state: Optional[Union[str, ImageState]] = ..., 
                scheduled_deprecation_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageDisk(_Model):
        blob_uri: Optional[str]
        caching: Optional[Union[str, CachingTypes]]
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        disk_size_gb: Optional[int]
        managed_disk: Optional[SubResource]
        snapshot: Optional[SubResource]
        storage_account_type: Optional[Union[str, StorageAccountTypes]]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                disk_size_gb: Optional[int] = ..., 
                managed_disk: Optional[SubResource] = ..., 
                snapshot: Optional[SubResource] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageDiskReference(_Model):
        community_gallery_image_id: Optional[str]
        id: Optional[str]
        lun: Optional[int]
        shared_gallery_image_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_image_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                lun: Optional[int] = ..., 
                shared_gallery_image_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageOSDisk(ImageDisk):
        blob_uri: str
        caching: Union[str, CachingTypes]
        disk_encryption_set: DiskEncryptionSetParameters
        disk_size_gb: int
        managed_disk: SubResource
        os_state: Union[str, OperatingSystemStateTypes]
        os_type: Union[str, OperatingSystemTypes]
        snapshot: SubResource
        storage_account_type: Union[str, StorageAccountTypes]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                disk_size_gb: Optional[int] = ..., 
                managed_disk: Optional[SubResource] = ..., 
                os_state: Union[str, OperatingSystemStateTypes], 
                os_type: Union[str, OperatingSystemTypes], 
                snapshot: Optional[SubResource] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageProperties(_Model):
        hyper_v_generation: Optional[Union[str, HyperVGenerationTypes]]
        provisioning_state: Optional[str]
        source_virtual_machine: Optional[SubResource]
        storage_profile: Optional[ImageStorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                hyper_v_generation: Optional[Union[str, HyperVGenerationTypes]] = ..., 
                source_virtual_machine: Optional[SubResource] = ..., 
                storage_profile: Optional[ImageStorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImagePurchasePlan(_Model):
        name: Optional[str]
        product: Optional[str]
        publisher: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                publisher: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageReference(SubResource):
        community_gallery_image_id: Optional[str]
        exact_version: Optional[str]
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


    class azure.mgmt.compute.models.ImageState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DEPRECATED = "Deprecated"
        SCHEDULED_FOR_DEPRECATION = "ScheduledForDeprecation"


    class azure.mgmt.compute.models.ImageStorageProfile(_Model):
        data_disks: Optional[list[ImageDataDisk]]
        os_disk: Optional[ImageOSDisk]
        zone_resilient: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[ImageDataDisk]] = ..., 
                os_disk: Optional[ImageOSDisk] = ..., 
                zone_resilient: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ImageUpdate(UpdateResource):
        properties: Optional[ImageProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.ImageVersionSecurityProfile(_Model):
        uefi_settings: Optional[GalleryImageVersionUefiSettings]

        @overload
        def __init__(
                self, 
                *, 
                uefi_settings: Optional[GalleryImageVersionUefiSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.InnerError(_Model):
        errordetail: Optional[str]
        exceptiontype: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                errordetail: Optional[str] = ..., 
                exceptiontype: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.InstanceViewStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, StatusLevelTypes]]
        message: Optional[str]
        time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, StatusLevelTypes]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.InstanceViewTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"
        RESILIENCY_VIEW = "resiliencyView"
        USER_DATA = "userData"


    class azure.mgmt.compute.models.IntervalInMins(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIVE_MINS = "FiveMins"
        SIXTY_MINS = "SixtyMins"
        THIRTY_MINS = "ThirtyMins"
        THREE_MINS = "ThreeMins"


    class azure.mgmt.compute.models.KeyForDiskEncryptionSet(_Model):
        key_url: str
        source_vault: Optional[SourceVault]

        @overload
        def __init__(
                self, 
                *, 
                key_url: str, 
                source_vault: Optional[SourceVault] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.KeyVaultAndKeyReference(_Model):
        key_url: str
        source_vault: SourceVault

        @overload
        def __init__(
                self, 
                *, 
                key_url: str, 
                source_vault: SourceVault
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.KeyVaultAndSecretReference(_Model):
        secret_url: str
        source_vault: SourceVault

        @overload
        def __init__(
                self, 
                *, 
                secret_url: str, 
                source_vault: SourceVault
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.KeyVaultKeyReference(_Model):
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


    class azure.mgmt.compute.models.KeyVaultSecretReference(_Model):
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


    class azure.mgmt.compute.models.LastPatchInstallationSummary(_Model):
        error: Optional[ApiError]
        excluded_patch_count: Optional[int]
        failed_patch_count: Optional[int]
        installation_activity_id: Optional[str]
        installed_patch_count: Optional[int]
        last_modified_time: Optional[datetime]
        maintenance_window_exceeded: Optional[bool]
        not_selected_patch_count: Optional[int]
        pending_patch_count: Optional[int]
        start_time: Optional[datetime]
        status: Optional[Union[str, PatchOperationStatus]]


    class azure.mgmt.compute.models.LifecycleHook(_Model):
        default_action: Optional[Union[str, LifecycleHookAction]]
        type: Optional[Union[str, VMScaleSetLifecycleHookEventType]]
        wait_duration: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, LifecycleHookAction]] = ..., 
                type: Optional[Union[str, VMScaleSetLifecycleHookEventType]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.LifecycleHookAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVE = "Approve"
        REJECT = "Reject"


    class azure.mgmt.compute.models.LifecycleHookActionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        REJECTED = "Rejected"
        WAITING = "Waiting"


    class azure.mgmt.compute.models.LifecycleHooksProfile(_Model):
        lifecycle_hooks: Optional[list[LifecycleHook]]

        @overload
        def __init__(
                self, 
                *, 
                lifecycle_hooks: Optional[list[LifecycleHook]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.LinuxConfiguration(_Model):
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


    class azure.mgmt.compute.models.LinuxParameters(_Model):
        classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationLinux]]]
        maintenance_run_id: Optional[str]
        package_name_masks_to_exclude: Optional[list[str]]
        package_name_masks_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationLinux]]] = ..., 
                maintenance_run_id: Optional[str] = ..., 
                package_name_masks_to_exclude: Optional[list[str]] = ..., 
                package_name_masks_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.LinuxPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.models.LinuxPatchSettings(_Model):
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


    class azure.mgmt.compute.models.LinuxVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.LinuxVMGuestPatchAutomaticByPlatformSettings(_Model):
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


    class azure.mgmt.compute.models.LinuxVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.models.LogAnalyticsInputBase(_Model):
        blob_container_sas_uri: str
        from_time: datetime
        group_by_client_application_id: Optional[bool]
        group_by_operation_name: Optional[bool]
        group_by_resource_name: Optional[bool]
        group_by_throttle_policy: Optional[bool]
        group_by_user_agent: Optional[bool]
        to_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                blob_container_sas_uri: str, 
                from_time: datetime, 
                group_by_client_application_id: Optional[bool] = ..., 
                group_by_operation_name: Optional[bool] = ..., 
                group_by_resource_name: Optional[bool] = ..., 
                group_by_throttle_policy: Optional[bool] = ..., 
                group_by_user_agent: Optional[bool] = ..., 
                to_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.LogAnalyticsOperationResult(_Model):
        properties: Optional[LogAnalyticsOutput]


    class azure.mgmt.compute.models.LogAnalyticsOutput(_Model):
        output: Optional[str]


    class azure.mgmt.compute.models.MaintenanceOperationResultCodeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAINTENANCE_ABORTED = "MaintenanceAborted"
        MAINTENANCE_COMPLETED = "MaintenanceCompleted"
        NONE = "None"
        RETRY_LATER = "RetryLater"


    class azure.mgmt.compute.models.MaintenanceRedeployStatus(_Model):
        is_customer_initiated_maintenance_allowed: Optional[bool]
        last_operation_message: Optional[str]
        last_operation_result_code: Optional[Union[str, MaintenanceOperationResultCodeTypes]]
        maintenance_window_end_time: Optional[datetime]
        maintenance_window_start_time: Optional[datetime]
        pre_maintenance_window_end_time: Optional[datetime]
        pre_maintenance_window_start_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                is_customer_initiated_maintenance_allowed: Optional[bool] = ..., 
                last_operation_message: Optional[str] = ..., 
                last_operation_result_code: Optional[Union[str, MaintenanceOperationResultCodeTypes]] = ..., 
                maintenance_window_end_time: Optional[datetime] = ..., 
                maintenance_window_start_time: Optional[datetime] = ..., 
                pre_maintenance_window_end_time: Optional[datetime] = ..., 
                pre_maintenance_window_start_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ManagedDiskParameters(SubResource):
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


    class azure.mgmt.compute.models.MaxInstancePercentPerZonePolicy(_Model):
        enabled: Optional[bool]
        value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.MigrateToVirtualMachineScaleSetInput(_Model):
        virtual_machine_scale_set_flexible: SubResource

        @overload
        def __init__(
                self, 
                *, 
                virtual_machine_scale_set_flexible: SubResource
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.MigrateVMToVirtualMachineScaleSetInput(_Model):
        target_fault_domain: Optional[int]
        target_vm_size: Optional[str]
        target_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_fault_domain: Optional[int] = ..., 
                target_vm_size: Optional[str] = ..., 
                target_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCE = "Enforce"


    class azure.mgmt.compute.models.Modes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        DISABLED = "Disabled"
        ENFORCE = "Enforce"


    class azure.mgmt.compute.models.NetworkAccessPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_ALL = "AllowAll"
        ALLOW_PRIVATE = "AllowPrivate"
        DENY_ALL = "DenyAll"


    class azure.mgmt.compute.models.NetworkApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TWO_THOUSAND_TWENTY11_01 = "2020-11-01"
        TWO_THOUSAND_TWENTY_TWO11_01 = "2022-11-01"


    class azure.mgmt.compute.models.NetworkInterfaceAuxiliaryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCELERATED_CONNECTIONS = "AcceleratedConnections"
        FLOATING = "Floating"
        NONE = "None"


    class azure.mgmt.compute.models.NetworkInterfaceAuxiliarySku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A1 = "A1"
        A2 = "A2"
        A4 = "A4"
        A8 = "A8"
        NONE = "None"


    class azure.mgmt.compute.models.NetworkInterfaceReference(SubResource):
        id: str
        properties: Optional[NetworkInterfaceReferenceProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                properties: Optional[NetworkInterfaceReferenceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.NetworkInterfaceReferenceProperties(_Model):
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


    class azure.mgmt.compute.models.NetworkProfile(_Model):
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


    class azure.mgmt.compute.models.OSDisk(_Model):
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
        storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]]
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
                storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]] = ..., 
                vhd: Optional[VirtualHardDisk] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OSDiskImage(_Model):
        operating_system: Union[str, OperatingSystemTypes]

        @overload
        def __init__(
                self, 
                *, 
                operating_system: Union[str, OperatingSystemTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OSDiskImageEncryption(DiskImageEncryption):
        disk_encryption_set_id: str
        security_profile: Optional[OSDiskImageSecurityProfile]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set_id: Optional[str] = ..., 
                security_profile: Optional[OSDiskImageSecurityProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OSDiskImageSecurityProfile(_Model):
        confidential_vm_encryption_type: Optional[Union[str, ConfidentialVMEncryptionType]]
        secure_vm_disk_encryption_set_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidential_vm_encryption_type: Optional[Union[str, ConfidentialVMEncryptionType]] = ..., 
                secure_vm_disk_encryption_set_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OSImageNotificationProfile(_Model):
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


    class azure.mgmt.compute.models.OSProfile(_Model):
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


    class azure.mgmt.compute.models.OSProfileProvisioningData(_Model):
        admin_password: Optional[str]
        custom_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                custom_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OperatingSystemStateTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERALIZED = "Generalized"
        SPECIALIZED = "Specialized"


    class azure.mgmt.compute.models.OperatingSystemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.compute.models.OperatingSystemTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.compute.models.Operation(_Model):
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


    class azure.mgmt.compute.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.compute.models.OperationRecoverySettings(_Model):
        reimage_recovery_policy: Optional[ReimageRecoveryPolicy]
        restart_recovery_policy: Optional[RestartRecoveryPolicy]
        start_recovery_policy: Optional[StartRecoveryPolicy]

        @overload
        def __init__(
                self, 
                *, 
                reimage_recovery_policy: Optional[ReimageRecoveryPolicy] = ..., 
                restart_recovery_policy: Optional[RestartRecoveryPolicy] = ..., 
                start_recovery_policy: Optional[StartRecoveryPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OrchestrationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLEXIBLE = "Flexible"
        UNIFORM = "Uniform"


    class azure.mgmt.compute.models.OrchestrationServiceNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_REPAIRS = "AutomaticRepairs"
        AUTOMATIC_ZONE_REBALANCING = "AutomaticZoneRebalancing"


    class azure.mgmt.compute.models.OrchestrationServiceOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.compute.models.OrchestrationServiceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_RUNNING = "NotRunning"
        RUNNING = "Running"
        SUSPENDED = "Suspended"


    class azure.mgmt.compute.models.OrchestrationServiceStateAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESUME = "Resume"
        SUSPEND = "Suspend"


    class azure.mgmt.compute.models.OrchestrationServiceStateInput(_Model):
        action: Union[str, OrchestrationServiceStateAction]
        service_name: Union[str, OrchestrationServiceNames]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, OrchestrationServiceStateAction], 
                service_name: Union[str, OrchestrationServiceNames]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.OrchestrationServiceSummary(_Model):
        last_status_change_time: Optional[datetime]
        latest_operation_status: Optional[Union[str, OrchestrationServiceOperationStatus]]
        service_name: Optional[Union[str, OrchestrationServiceNames]]
        service_state: Optional[Union[str, OrchestrationServiceState]]


    class azure.mgmt.compute.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.compute.models.PassNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OOBE_SYSTEM = "OobeSystem"


    class azure.mgmt.compute.models.PatchAssessmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.PatchInstallationDetail(_Model):
        classifications: Optional[list[str]]
        installation_state: Optional[Union[str, PatchInstallationState]]
        kb_id: Optional[str]
        name: Optional[str]
        patch_id: Optional[str]
        version: Optional[str]


    class azure.mgmt.compute.models.PatchInstallationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDED = "Excluded"
        FAILED = "Failed"
        INSTALLED = "Installed"
        NOT_SELECTED = "NotSelected"
        PENDING = "Pending"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.PatchOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.PatchSettings(_Model):
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


    class azure.mgmt.compute.models.PirCommunityGalleryResource(_Model):
        identifier: Optional[CommunityGalleryIdentifier]
        location: Optional[str]
        name: Optional[str]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[CommunityGalleryIdentifier] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.PirResource(_Model):
        location: Optional[str]
        name: Optional[str]


    class azure.mgmt.compute.models.PirSharedGalleryResource(PirResource):
        identifier: Optional[SharedGalleryIdentifier]
        location: str
        name: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[SharedGalleryIdentifier] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.Placement(_Model):
        exclude_zones: Optional[list[str]]
        include_zones: Optional[list[str]]
        zone_placement_policy: Optional[Union[str, ZonePlacementPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_zones: Optional[list[str]] = ..., 
                include_zones: Optional[list[str]] = ..., 
                zone_placement_policy: Optional[Union[str, ZonePlacementPolicyType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Plan(_Model):
        name: Optional[str]
        product: Optional[str]
        promotion_code: Optional[str]
        publisher: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                product: Optional[str] = ..., 
                promotion_code: Optional[str] = ..., 
                publisher: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PlatformAttribute(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.compute.models.PolicyViolation(_Model):
        category: Optional[Union[str, PolicyViolationCategory]]
        details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, PolicyViolationCategory]] = ..., 
                details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PolicyViolationCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPYRIGHT_VALIDATION = "CopyrightValidation"
        IMAGE_FLAGGED_UNSAFE = "ImageFlaggedUnsafe"
        IP_THEFT = "IpTheft"
        OTHER = "Other"


    class azure.mgmt.compute.models.PriorityMixPolicy(_Model):
        base_regular_priority_count: Optional[int]
        regular_priority_percentage_above_base: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                base_regular_priority_count: Optional[int] = ..., 
                regular_priority_percentage_above_base: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.compute.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.compute.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.compute.models.PrivateLinkResource(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[PrivateLinkResourceProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.PropertyUpdatesInProgress(_Model):
        target_tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ProtocolTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.compute.models.ProvisionedBandwidthCopyOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENHANCED = "Enhanced"
        NONE = "None"


    class azure.mgmt.compute.models.ProximityPlacementGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProximityPlacementGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProximityPlacementGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.ProximityPlacementGroupProperties(_Model):
        availability_sets: Optional[list[SubResourceWithColocationStatus]]
        colocation_status: Optional[InstanceViewStatus]
        intent: Optional[ProximityPlacementGroupPropertiesIntent]
        proximity_placement_group_type: Optional[Union[str, ProximityPlacementGroupType]]
        virtual_machine_scale_sets: Optional[list[SubResourceWithColocationStatus]]
        virtual_machines: Optional[list[SubResourceWithColocationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                colocation_status: Optional[InstanceViewStatus] = ..., 
                intent: Optional[ProximityPlacementGroupPropertiesIntent] = ..., 
                proximity_placement_group_type: Optional[Union[str, ProximityPlacementGroupType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ProximityPlacementGroupPropertiesIntent(_Model):
        vm_sizes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                vm_sizes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ProximityPlacementGroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD = "Standard"
        ULTRA = "Ultra"


    class azure.mgmt.compute.models.ProximityPlacementGroupUpdate(UpdateResource):
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ProxyAgentSettings(_Model):
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


    class azure.mgmt.compute.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.compute.models.PublicIPAddressSku(_Model):
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


    class azure.mgmt.compute.models.PublicIPAddressSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.compute.models.PublicIPAddressSkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "Global"
        REGIONAL = "Regional"


    class azure.mgmt.compute.models.PublicIPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.compute.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.compute.models.PurchasePlan(_Model):
        name: str
        product: str
        publisher: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                publisher: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RebalanceBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_BEFORE_DELETE = "CreateBeforeDelete"


    class azure.mgmt.compute.models.RebalanceStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RECREATE = "Recreate"


    class azure.mgmt.compute.models.RecommendedMachineConfiguration(_Model):
        memory: Optional[ResourceRange]
        v_cp_us: Optional[ResourceRange]

        @overload
        def __init__(
                self, 
                *, 
                memory: Optional[ResourceRange] = ..., 
                v_cp_us: Optional[ResourceRange] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RecoveryWalkResponse(_Model):
        next_platform_update_domain: Optional[int]
        walk_performed: Optional[bool]


    class azure.mgmt.compute.models.RegionalReplicationStatus(_Model):
        details: Optional[str]
        progress: Optional[int]
        region: Optional[str]
        state: Optional[Union[str, ReplicationState]]


    class azure.mgmt.compute.models.RegionalSharingStatus(_Model):
        details: Optional[str]
        region: Optional[str]
        state: Optional[Union[str, SharingState]]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[str] = ..., 
                region: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ReimageRecoveryPolicy(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RepairAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REIMAGE = "Reimage"
        REPLACE = "Replace"
        RESTART = "Restart"


    class azure.mgmt.compute.models.ReplicationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL = "Full"
        SHALLOW = "Shallow"


    class azure.mgmt.compute.models.ReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        REPLICATING = "Replicating"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.ReplicationStatus(_Model):
        aggregated_state: Optional[Union[str, AggregatedReplicationState]]
        summary: Optional[list[RegionalReplicationStatus]]


    class azure.mgmt.compute.models.ReplicationStatusTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REPLICATION_STATUS = "ReplicationStatus"
        UEFI_SETTINGS = "UefiSettings"


    class azure.mgmt.compute.models.RequestRateByIntervalInput(LogAnalyticsInputBase):
        blob_container_sas_uri: str
        from_time: datetime
        group_by_client_application_id: bool
        group_by_operation_name: bool
        group_by_resource_name: bool
        group_by_throttle_policy: bool
        group_by_user_agent: bool
        interval_length: Union[str, IntervalInMins]
        to_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                blob_container_sas_uri: str, 
                from_time: datetime, 
                group_by_client_application_id: Optional[bool] = ..., 
                group_by_operation_name: Optional[bool] = ..., 
                group_by_resource_name: Optional[bool] = ..., 
                group_by_throttle_policy: Optional[bool] = ..., 
                group_by_user_agent: Optional[bool] = ..., 
                interval_length: Union[str, IntervalInMins], 
                to_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ReservationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "Block"
        TARGETED = "Targeted"


    class azure.mgmt.compute.models.ResiliencyPolicy(_Model):
        automatic_zone_rebalancing_policy: Optional[AutomaticZoneRebalancingPolicy]
        operation_recovery_settings: Optional[OperationRecoverySettings]
        resilient_vm_creation_policy: Optional[ResilientVMCreationPolicy]
        resilient_vm_deletion_policy: Optional[ResilientVMDeletionPolicy]
        zone_allocation_policy: Optional[ZoneAllocationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                automatic_zone_rebalancing_policy: Optional[AutomaticZoneRebalancingPolicy] = ..., 
                operation_recovery_settings: Optional[OperationRecoverySettings] = ..., 
                resilient_vm_creation_policy: Optional[ResilientVMCreationPolicy] = ..., 
                resilient_vm_deletion_policy: Optional[ResilientVMDeletionPolicy] = ..., 
                zone_allocation_policy: Optional[ZoneAllocationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ResiliencyProfile(_Model):
        zone_movement: Optional[ZoneMovement]

        @overload
        def __init__(
                self, 
                *, 
                zone_movement: Optional[ZoneMovement] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ResilientVMCreationPolicy(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ResilientVMDeletionPolicy(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ResilientVMDeletionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.compute.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.compute.models.ResourceIdOptionsForGetCapacityReservationGroups(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CREATED_IN_SUBSCRIPTION = "CreatedInSubscription"
        SHARED_WITH_SUBSCRIPTION = "SharedWithSubscription"


    class azure.mgmt.compute.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.compute.models.ResourceRange(_Model):
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


    class azure.mgmt.compute.models.ResourceSharingProfile(_Model):
        subscription_ids: Optional[list[SubResource]]

        @overload
        def __init__(
                self, 
                *, 
                subscription_ids: Optional[list[SubResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ResourceSku(_Model):
        api_versions: Optional[list[str]]
        capabilities: Optional[list[ResourceSkuCapabilities]]
        capacity: Optional[ResourceSkuCapacity]
        costs: Optional[list[ResourceSkuCosts]]
        family: Optional[str]
        kind: Optional[str]
        location_info: Optional[list[ResourceSkuLocationInfo]]
        locations: Optional[list[str]]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[ResourceSkuRestrictions]]
        size: Optional[str]
        tier: Optional[str]


    class azure.mgmt.compute.models.ResourceSkuCapabilities(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.compute.models.ResourceSkuCapacity(_Model):
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, ResourceSkuCapacityScaleType]]


    class azure.mgmt.compute.models.ResourceSkuCapacityScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.compute.models.ResourceSkuCosts(_Model):
        extended_unit: Optional[str]
        meter_id: Optional[str]
        quantity: Optional[int]


    class azure.mgmt.compute.models.ResourceSkuLocationInfo(_Model):
        extended_locations: Optional[list[str]]
        location: Optional[str]
        type: Optional[Union[str, ExtendedLocationType]]
        zone_details: Optional[list[ResourceSkuZoneDetails]]
        zones: Optional[list[str]]


    class azure.mgmt.compute.models.ResourceSkuRestrictionInfo(_Model):
        locations: Optional[list[str]]
        zones: Optional[list[str]]


    class azure.mgmt.compute.models.ResourceSkuRestrictions(_Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: Optional[ResourceSkuRestrictionInfo]
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: Optional[list[str]]


    class azure.mgmt.compute.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.compute.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.compute.models.ResourceSkuZoneDetails(_Model):
        capabilities: Optional[list[ResourceSkuCapabilities]]
        name: Optional[list[str]]


    class azure.mgmt.compute.models.RestartRecoveryPolicy(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePoint(ProxyResource):
        id: str
        name: str
        properties: Optional[RestorePointProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorePointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.RestorePointCollection(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[RestorePointCollectionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[RestorePointCollectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.RestorePointCollectionExpandOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTORE_POINTS = "restorePoints"


    class azure.mgmt.compute.models.RestorePointCollectionProperties(_Model):
        instant_access: Optional[bool]
        provisioning_state: Optional[str]
        restore_point_collection_id: Optional[str]
        restore_points: Optional[list[RestorePoint]]
        source: Optional[RestorePointCollectionSourceProperties]

        @overload
        def __init__(
                self, 
                *, 
                instant_access: Optional[bool] = ..., 
                source: Optional[RestorePointCollectionSourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointCollectionSourceProperties(_Model):
        id: Optional[str]
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointCollectionUpdate(UpdateResource):
        properties: Optional[RestorePointCollectionProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RestorePointCollectionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.RestorePointEncryption(_Model):
        disk_encryption_set: Optional[DiskEncryptionSetParameters]
        type: Optional[Union[str, RestorePointEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                disk_encryption_set: Optional[DiskEncryptionSetParameters] = ..., 
                type: Optional[Union[str, RestorePointEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTION_AT_REST_WITH_CUSTOMER_KEY = "EncryptionAtRestWithCustomerKey"
        ENCRYPTION_AT_REST_WITH_PLATFORM_AND_CUSTOMER_KEYS = "EncryptionAtRestWithPlatformAndCustomerKeys"
        ENCRYPTION_AT_REST_WITH_PLATFORM_KEY = "EncryptionAtRestWithPlatformKey"


    class azure.mgmt.compute.models.RestorePointExpandOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTANCE_VIEW = "instanceView"


    class azure.mgmt.compute.models.RestorePointInstanceView(_Model):
        disk_restore_points: Optional[list[DiskRestorePointInstanceView]]
        statuses: Optional[list[InstanceViewStatus]]

        @overload
        def __init__(
                self, 
                *, 
                disk_restore_points: Optional[list[DiskRestorePointInstanceView]] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointProperties(_Model):
        consistency_mode: Optional[Union[str, ConsistencyModeTypes]]
        exclude_disks: Optional[list[ApiEntityReference]]
        instance_view: Optional[RestorePointInstanceView]
        instant_access_duration_minutes: Optional[int]
        provisioning_state: Optional[str]
        source_metadata: Optional[RestorePointSourceMetadata]
        source_restore_point: Optional[ApiEntityReference]
        time_created: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                consistency_mode: Optional[Union[str, ConsistencyModeTypes]] = ..., 
                exclude_disks: Optional[list[ApiEntityReference]] = ..., 
                instant_access_duration_minutes: Optional[int] = ..., 
                source_metadata: Optional[RestorePointSourceMetadata] = ..., 
                source_restore_point: Optional[ApiEntityReference] = ..., 
                time_created: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointSourceMetadata(_Model):
        diagnostics_profile: Optional[DiagnosticsProfile]
        hardware_profile: Optional[HardwareProfile]
        hyper_v_generation: Optional[Union[str, HyperVGenerationTypes]]
        license_type: Optional[str]
        location: Optional[str]
        os_profile: Optional[OSProfile]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[RestorePointSourceVMStorageProfile]
        user_data: Optional[str]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_profile: Optional[RestorePointSourceVMStorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointSourceVMDataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        disk_restore_point: Optional[DiskRestorePointAttributes]
        disk_size_gb: Optional[int]
        lun: Optional[int]
        managed_disk: Optional[ManagedDiskParameters]
        name: Optional[str]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disk_restore_point: Optional[DiskRestorePointAttributes] = ..., 
                managed_disk: Optional[ManagedDiskParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointSourceVMOSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        disk_restore_point: Optional[DiskRestorePointAttributes]
        disk_size_gb: Optional[int]
        encryption_settings: Optional[DiskEncryptionSettings]
        managed_disk: Optional[ManagedDiskParameters]
        name: Optional[str]
        os_type: Optional[Union[str, OperatingSystemType]]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disk_restore_point: Optional[DiskRestorePointAttributes] = ..., 
                managed_disk: Optional[ManagedDiskParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RestorePointSourceVMStorageProfile(_Model):
        data_disks: Optional[list[RestorePointSourceVMDataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        os_disk: Optional[RestorePointSourceVMOSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[RestorePointSourceVMDataDisk]] = ..., 
                os_disk: Optional[RestorePointSourceVMOSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RetrieveBootDiagnosticsDataResult(_Model):
        console_screenshot_blob_uri: Optional[str]
        serial_console_log_blob_uri: Optional[str]


    class azure.mgmt.compute.models.RollbackStatusInfo(_Model):
        failed_rolledback_instance_count: Optional[int]
        rollback_error: Optional[ApiError]
        successfully_rolledback_instance_count: Optional[int]


    class azure.mgmt.compute.models.RollingUpgradeActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "Cancel"
        START = "Start"


    class azure.mgmt.compute.models.RollingUpgradePolicy(_Model):
        enable_cross_zone_upgrade: Optional[bool]
        max_batch_instance_percent: Optional[int]
        max_surge: Optional[bool]
        max_unhealthy_instance_percent: Optional[int]
        max_unhealthy_upgraded_instance_percent: Optional[int]
        pause_time_between_batches: Optional[str]
        prioritize_unhealthy_instances: Optional[bool]
        rollback_failed_instances_on_policy_breach: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_cross_zone_upgrade: Optional[bool] = ..., 
                max_batch_instance_percent: Optional[int] = ..., 
                max_surge: Optional[bool] = ..., 
                max_unhealthy_instance_percent: Optional[int] = ..., 
                max_unhealthy_upgraded_instance_percent: Optional[int] = ..., 
                pause_time_between_batches: Optional[str] = ..., 
                prioritize_unhealthy_instances: Optional[bool] = ..., 
                rollback_failed_instances_on_policy_breach: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RollingUpgradeProgressInfo(_Model):
        failed_instance_count: Optional[int]
        in_progress_instance_count: Optional[int]
        pending_instance_count: Optional[int]
        successful_instance_count: Optional[int]


    class azure.mgmt.compute.models.RollingUpgradeRunningStatus(_Model):
        code: Optional[Union[str, RollingUpgradeStatusCode]]
        last_action: Optional[Union[str, RollingUpgradeActionType]]
        last_action_time: Optional[datetime]
        start_time: Optional[datetime]


    class azure.mgmt.compute.models.RollingUpgradeStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAULTED = "Faulted"
        ROLLING_FORWARD = "RollingForward"


    class azure.mgmt.compute.models.RollingUpgradeStatusInfo(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[RollingUpgradeStatusInfoProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[RollingUpgradeStatusInfoProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.RollingUpgradeStatusInfoProperties(_Model):
        error: Optional[ApiError]
        policy: Optional[RollingUpgradePolicy]
        progress: Optional[RollingUpgradeProgressInfo]
        running_status: Optional[RollingUpgradeRunningStatus]


    class azure.mgmt.compute.models.RunCommandDocument(RunCommandDocumentBase):
        description: str
        id: str
        label: str
        os_type: Union[str, OperatingSystemTypes]
        parameters: Optional[list[RunCommandParameterDefinition]]
        schema: str
        script: list[str]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                label: str, 
                os_type: Union[str, OperatingSystemTypes], 
                parameters: Optional[list[RunCommandParameterDefinition]] = ..., 
                schema: str, 
                script: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandDocumentBase(_Model):
        description: str
        id: str
        label: str
        os_type: Union[str, OperatingSystemTypes]
        schema: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                label: str, 
                os_type: Union[str, OperatingSystemTypes], 
                schema: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandInput(_Model):
        command_id: str
        parameters: Optional[list[RunCommandInputParameter]]
        script: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                command_id: str, 
                parameters: Optional[list[RunCommandInputParameter]] = ..., 
                script: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandInputParameter(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandManagedIdentity(_Model):
        client_id: Optional[str]
        object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandParameterDefinition(_Model):
        default_value: Optional[str]
        name: str
        required: Optional[bool]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[str] = ..., 
                name: str, 
                required: Optional[bool] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.RunCommandResult(_Model):
        value: Optional[list[InstanceViewStatus]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ScaleInPolicy(_Model):
        force_deletion: Optional[bool]
        prioritize_unhealthy_v_ms: Optional[bool]
        rules: Optional[list[Union[str, VirtualMachineScaleSetScaleInRules]]]

        @overload
        def __init__(
                self, 
                *, 
                force_deletion: Optional[bool] = ..., 
                prioritize_unhealthy_v_ms: Optional[bool] = ..., 
                rules: Optional[list[Union[str, VirtualMachineScaleSetScaleInRules]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ScheduleProfile(_Model):
        end: Optional[str]
        start: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end: Optional[str] = ..., 
                start: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ScheduledEventsAdditionalPublishingTargets(_Model):
        event_grid_and_resource_graph: Optional[EventGridAndResourceGraph]

        @overload
        def __init__(
                self, 
                *, 
                event_grid_and_resource_graph: Optional[EventGridAndResourceGraph] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ScheduledEventsPolicy(_Model):
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


    class azure.mgmt.compute.models.ScheduledEventsProfile(_Model):
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


    class azure.mgmt.compute.models.ScriptShellTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        POWERSHELL7 = "Powershell7"


    class azure.mgmt.compute.models.ScriptSource(_Model):
        parameters: Optional[list[GalleryScriptParameter]]
        script_link: str

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[list[GalleryScriptParameter]] = ..., 
                script_link: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SecurityEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_WITH_VM_GUEST_STATE = "DiskWithVMGuestState"
        NON_PERSISTED_TPM = "NonPersistedTPM"
        VM_GUEST_STATE_ONLY = "VMGuestStateOnly"


    class azure.mgmt.compute.models.SecurityPostureReference(_Model):
        exclude_extensions: Optional[list[str]]
        id: str
        is_overridable: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exclude_extensions: Optional[list[str]] = ..., 
                id: str, 
                is_overridable: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SecurityPostureReferenceUpdate(_Model):
        exclude_extensions: Optional[list[str]]
        id: Optional[str]
        is_overridable: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exclude_extensions: Optional[list[str]] = ..., 
                id: Optional[str] = ..., 
                is_overridable: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SecurityProfile(_Model):
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


    class azure.mgmt.compute.models.SecurityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL_VM = "ConfidentialVM"
        STANDARD = "Standard"
        TRUSTED_LAUNCH = "TrustedLaunch"


    class azure.mgmt.compute.models.SelectPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERMISSIONS = "Permissions"


    class azure.mgmt.compute.models.ServiceArtifactReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SettingNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_LOGON = "AutoLogon"
        FIRST_LOGON_COMMANDS = "FirstLogonCommands"


    class azure.mgmt.compute.models.ShareInfoElement(_Model):
        vm_uri: Optional[str]


    class azure.mgmt.compute.models.SharedGallery(PirSharedGalleryResource):
        identifier: SharedGalleryIdentifier
        location: str
        name: str
        properties: Optional[SharedGalleryProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[SharedGalleryIdentifier] = ..., 
                properties: Optional[SharedGalleryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryDataDiskImage(SharedGalleryDiskImage):
        disk_size_gb: int
        host_caching: Union[str, SharedGalleryHostCaching]
        lun: int

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, SharedGalleryHostCaching]] = ..., 
                lun: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryDiskImage(_Model):
        disk_size_gb: Optional[int]
        host_caching: Optional[Union[str, SharedGalleryHostCaching]]

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, SharedGalleryHostCaching]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryHostCaching(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.compute.models.SharedGalleryIdentifier(_Model):
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                unique_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryImage(PirSharedGalleryResource):
        identifier: SharedGalleryIdentifier
        location: str
        name: str
        properties: Optional[SharedGalleryImageProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[SharedGalleryIdentifier] = ..., 
                properties: Optional[SharedGalleryImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryImageProperties(_Model):
        architecture: Optional[Union[str, Architecture]]
        artifact_tags: Optional[dict[str, str]]
        disallowed: Optional[Disallowed]
        end_of_life_date: Optional[datetime]
        eula: Optional[str]
        features: Optional[list[GalleryImageFeature]]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        identifier: GalleryImageIdentifier
        os_state: Union[str, OperatingSystemStateTypes]
        os_type: Union[str, OperatingSystemTypes]
        privacy_statement_uri: Optional[str]
        purchase_plan: Optional[ImagePurchasePlan]
        recommended: Optional[RecommendedMachineConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                architecture: Optional[Union[str, Architecture]] = ..., 
                artifact_tags: Optional[dict[str, str]] = ..., 
                disallowed: Optional[Disallowed] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                eula: Optional[str] = ..., 
                features: Optional[list[GalleryImageFeature]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                identifier: GalleryImageIdentifier, 
                os_state: Union[str, OperatingSystemStateTypes], 
                os_type: Union[str, OperatingSystemTypes], 
                privacy_statement_uri: Optional[str] = ..., 
                purchase_plan: Optional[ImagePurchasePlan] = ..., 
                recommended: Optional[RecommendedMachineConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryImageVersion(PirSharedGalleryResource):
        identifier: SharedGalleryIdentifier
        location: str
        name: str
        properties: Optional[SharedGalleryImageVersionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identifier: Optional[SharedGalleryIdentifier] = ..., 
                properties: Optional[SharedGalleryImageVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryImageVersionProperties(_Model):
        artifact_tags: Optional[dict[str, str]]
        end_of_life_date: Optional[datetime]
        exclude_from_latest: Optional[bool]
        published_date: Optional[datetime]
        storage_profile: Optional[SharedGalleryImageVersionStorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                artifact_tags: Optional[dict[str, str]] = ..., 
                end_of_life_date: Optional[datetime] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                published_date: Optional[datetime] = ..., 
                storage_profile: Optional[SharedGalleryImageVersionStorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryImageVersionStorageProfile(_Model):
        data_disk_images: Optional[list[SharedGalleryDataDiskImage]]
        os_disk_image: Optional[SharedGalleryOSDiskImage]

        @overload
        def __init__(
                self, 
                *, 
                data_disk_images: Optional[list[SharedGalleryDataDiskImage]] = ..., 
                os_disk_image: Optional[SharedGalleryOSDiskImage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryOSDiskImage(SharedGalleryDiskImage):
        disk_size_gb: int
        host_caching: Union[str, SharedGalleryHostCaching]

        @overload
        def __init__(
                self, 
                *, 
                host_caching: Optional[Union[str, SharedGalleryHostCaching]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharedGalleryProperties(_Model):
        artifact_tags: Optional[dict[str, str]]


    class azure.mgmt.compute.models.SharedToValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TENANT = "tenant"


    class azure.mgmt.compute.models.SharingProfile(_Model):
        community_gallery_info: Optional[CommunityGalleryInfo]
        groups: Optional[list[SharingProfileGroup]]
        permissions: Optional[Union[str, GallerySharingPermissionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                community_gallery_info: Optional[CommunityGalleryInfo] = ..., 
                permissions: Optional[Union[str, GallerySharingPermissionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharingProfileGroup(_Model):
        ids: Optional[list[str]]
        type: Optional[Union[str, SharingProfileGroupTypes]]

        @overload
        def __init__(
                self, 
                *, 
                ids: Optional[list[str]] = ..., 
                type: Optional[Union[str, SharingProfileGroupTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharingProfileGroupTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD_TENANTS = "AADTenants"
        SUBSCRIPTIONS = "Subscriptions"


    class azure.mgmt.compute.models.SharingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.SharingStatus(_Model):
        aggregated_state: Optional[Union[str, SharingState]]
        summary: Optional[list[RegionalSharingStatus]]

        @overload
        def __init__(
                self, 
                *, 
                summary: Optional[list[RegionalSharingStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharingUpdate(_Model):
        groups: Optional[list[SharingProfileGroup]]
        operation_type: Union[str, SharingUpdateOperationTypes]

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[list[SharingProfileGroup]] = ..., 
                operation_type: Union[str, SharingUpdateOperationTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SharingUpdateOperationTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "Add"
        ENABLE_COMMUNITY = "EnableCommunity"
        REMOVE = "Remove"
        RESET = "Reset"


    class azure.mgmt.compute.models.Sku(_Model):
        capacity: Optional[int]
        name: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SkuProfile(_Model):
        allocation_strategy: Optional[Union[str, AllocationStrategy]]
        vm_sizes: Optional[list[SkuProfileVMSize]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_strategy: Optional[Union[str, AllocationStrategy]] = ..., 
                vm_sizes: Optional[list[SkuProfileVMSize]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SkuProfileVMSize(_Model):
        name: Optional[str]
        rank: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                rank: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.Snapshot(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        managed_by: Optional[str]
        name: str
        properties: Optional[SnapshotProperties]
        sku: Optional[SnapshotSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[SnapshotProperties] = ..., 
                sku: Optional[SnapshotSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SnapshotAccessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        AVAILABLE_WITH_INSTANT_ACCESS = "AvailableWithInstantAccess"
        INSTANT_ACCESS = "InstantAccess"
        PENDING = "Pending"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.SnapshotProperties(_Model):
        completion_percent: Optional[float]
        copy_completion_error: Optional[CopyCompletionError]
        creation_data: CreationData
        data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]]
        disk_access_id: Optional[str]
        disk_size_bytes: Optional[int]
        disk_size_gb: Optional[int]
        disk_state: Optional[Union[str, DiskState]]
        encryption: Optional[Encryption]
        encryption_settings_collection: Optional[EncryptionSettingsCollection]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        incremental: Optional[bool]
        incremental_snapshot_family_id: Optional[str]
        network_access_policy: Optional[Union[str, NetworkAccessPolicy]]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        purchase_plan: Optional[DiskPurchasePlan]
        security_profile: Optional[DiskSecurityProfile]
        snapshot_access_state: Optional[Union[str, SnapshotAccessState]]
        supported_capabilities: Optional[SupportedCapabilities]
        supports_hibernation: Optional[bool]
        time_created: Optional[datetime]
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completion_percent: Optional[float] = ..., 
                copy_completion_error: Optional[CopyCompletionError] = ..., 
                creation_data: CreationData, 
                data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]] = ..., 
                disk_access_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption: Optional[Encryption] = ..., 
                encryption_settings_collection: Optional[EncryptionSettingsCollection] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                incremental: Optional[bool] = ..., 
                network_access_policy: Optional[Union[str, NetworkAccessPolicy]] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                purchase_plan: Optional[DiskPurchasePlan] = ..., 
                security_profile: Optional[DiskSecurityProfile] = ..., 
                supported_capabilities: Optional[SupportedCapabilities] = ..., 
                supports_hibernation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SnapshotSku(_Model):
        name: Optional[Union[str, SnapshotStorageAccountTypes]]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SnapshotStorageAccountTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SnapshotStorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.compute.models.SnapshotUpdate(_Model):
        properties: Optional[SnapshotUpdateProperties]
        sku: Optional[SnapshotSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SnapshotUpdateProperties] = ..., 
                sku: Optional[SnapshotSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SnapshotUpdateProperties(_Model):
        data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]]
        disk_access_id: Optional[str]
        disk_size_gb: Optional[int]
        encryption: Optional[Encryption]
        encryption_settings_collection: Optional[EncryptionSettingsCollection]
        network_access_policy: Optional[Union[str, NetworkAccessPolicy]]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        snapshot_access_state: Optional[Union[str, SnapshotAccessState]]
        supported_capabilities: Optional[SupportedCapabilities]
        supports_hibernation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                data_access_auth_mode: Optional[Union[str, DataAccessAuthMode]] = ..., 
                disk_access_id: Optional[str] = ..., 
                disk_size_gb: Optional[int] = ..., 
                encryption: Optional[Encryption] = ..., 
                encryption_settings_collection: Optional[EncryptionSettingsCollection] = ..., 
                network_access_policy: Optional[Union[str, NetworkAccessPolicy]] = ..., 
                os_type: Optional[Union[str, OperatingSystemTypes]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                supported_capabilities: Optional[SupportedCapabilities] = ..., 
                supports_hibernation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SoftDeletePolicy(_Model):
        is_soft_delete_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_soft_delete_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SoftDeletedArtifactTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGES = "Images"


    class azure.mgmt.compute.models.SourceVault(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SpotRestorePolicy(_Model):
        enabled: Optional[bool]
        restore_timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                restore_timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SshConfiguration(_Model):
        public_keys: Optional[list[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[list[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SshEncryptionTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ED25519 = "Ed25519"
        RSA = "RSA"


    class azure.mgmt.compute.models.SshGenerateKeyPairInputParameters(_Model):
        encryption_type: Optional[Union[str, SshEncryptionTypes]]

        @overload
        def __init__(
                self, 
                *, 
                encryption_type: Optional[Union[str, SshEncryptionTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SshPublicKey(_Model):
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


    class azure.mgmt.compute.models.SshPublicKeyGenerateKeyPairResult(_Model):
        id: str
        private_key: str
        public_key: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                private_key: str, 
                public_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SshPublicKeyResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SshPublicKeyResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SshPublicKeyResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.SshPublicKeyResourceProperties(_Model):
        public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SshPublicKeyUpdateResource(UpdateResource):
        properties: Optional[SshPublicKeyResourceProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SshPublicKeyResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.StartRecoveryPolicy(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.StatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.compute.models.StorageAccountStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_STANDARD_LRS = "DefaultStandard_LRS"
        PREFER_STANDARD_ZRS = "PreferStandard_ZRS"


    class azure.mgmt.compute.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_ZRS = "Standard_ZRS"


    class azure.mgmt.compute.models.StorageAccountTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.compute.models.StorageAlignmentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIGNED = "Aligned"
        UNALIGNED = "Unaligned"


    class azure.mgmt.compute.models.StorageFaultDomainAlignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIGNED = "Aligned"
        BEST_EFFORT_ALIGNED = "BestEffortAligned"


    class azure.mgmt.compute.models.StorageProfile(_Model):
        align_regional_disks_to_vm_zone: Optional[bool]
        data_disks: Optional[list[DataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[OSDisk]

        @overload
        def __init__(
                self, 
                *, 
                align_regional_disks_to_vm_zone: Optional[bool] = ..., 
                data_disks: Optional[list[DataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[OSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SubResource(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SubResourceReadOnly(_Model):
        id: Optional[str]


    class azure.mgmt.compute.models.SubResourceWithColocationStatus(SubResource):
        colocation_status: Optional[InstanceViewStatus]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                colocation_status: Optional[InstanceViewStatus] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SupportedCapabilities(_Model):
        accelerated_network: Optional[bool]
        architecture: Optional[Union[str, Architecture]]
        disk_controller_types: Optional[str]
        supported_security_option: Optional[Union[str, SupportedSecurityOption]]

        @overload
        def __init__(
                self, 
                *, 
                accelerated_network: Optional[bool] = ..., 
                architecture: Optional[Union[str, Architecture]] = ..., 
                disk_controller_types: Optional[str] = ..., 
                supported_security_option: Optional[Union[str, SupportedSecurityOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.SupportedSecurityOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRUSTED_LAUNCH_AND_CONFIDENTIAL_VM_SUPPORTED = "TrustedLaunchAndConfidentialVMSupported"
        TRUSTED_LAUNCH_SUPPORTED = "TrustedLaunchSupported"


    class azure.mgmt.compute.models.SystemData(_Model):
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


    class azure.mgmt.compute.models.TargetRegion(_Model):
        additional_replica_sets: Optional[list[AdditionalReplicaSet]]
        encryption: Optional[EncryptionImages]
        exclude_from_latest: Optional[bool]
        name: str
        regional_replica_count: Optional[int]
        storage_account_type: Optional[Union[str, StorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                additional_replica_sets: Optional[list[AdditionalReplicaSet]] = ..., 
                encryption: Optional[EncryptionImages] = ..., 
                exclude_from_latest: Optional[bool] = ..., 
                name: str, 
                regional_replica_count: Optional[int] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.TerminateNotificationProfile(_Model):
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


    class azure.mgmt.compute.models.ThrottledRequestsInput(LogAnalyticsInputBase):
        blob_container_sas_uri: str
        from_time: datetime
        group_by_client_application_id: bool
        group_by_operation_name: bool
        group_by_resource_name: bool
        group_by_throttle_policy: bool
        group_by_user_agent: bool
        to_time: datetime

        @overload
        def __init__(
                self, 
                *, 
                blob_container_sas_uri: str, 
                from_time: datetime, 
                group_by_client_application_id: Optional[bool] = ..., 
                group_by_operation_name: Optional[bool] = ..., 
                group_by_resource_name: Optional[bool] = ..., 
                group_by_throttle_policy: Optional[bool] = ..., 
                group_by_user_agent: Optional[bool] = ..., 
                to_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.TrackedResource(Resource):
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


    class azure.mgmt.compute.models.UefiKey(_Model):
        type: Optional[Union[str, UefiKeyType]]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, UefiKeyType]] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UefiKeySignatures(_Model):
        db: Optional[list[UefiKey]]
        dbx: Optional[list[UefiKey]]
        kek: Optional[list[UefiKey]]
        pk: Optional[UefiKey]

        @overload
        def __init__(
                self, 
                *, 
                db: Optional[list[UefiKey]] = ..., 
                dbx: Optional[list[UefiKey]] = ..., 
                kek: Optional[list[UefiKey]] = ..., 
                pk: Optional[UefiKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UefiKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHA256 = "sha256"
        X509 = "x509"


    class azure.mgmt.compute.models.UefiSettings(_Model):
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


    class azure.mgmt.compute.models.UefiSignatureTemplateName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_UEFI_CERTIFICATE_AUTHORITY_TEMPLATE = "MicrosoftUefiCertificateAuthorityTemplate"
        MICROSOFT_WINDOWS_TEMPLATE = "MicrosoftWindowsTemplate"
        NO_SIGNATURE_TEMPLATE = "NoSignatureTemplate"


    class azure.mgmt.compute.models.UpdateResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UpdateResourceDefinition(_Model):
        id: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        ROLLING = "Rolling"


    class azure.mgmt.compute.models.UpgradeOperationHistoricalStatusInfo(_Model):
        location: Optional[str]
        properties: Optional[UpgradeOperationHistoricalStatusInfoProperties]
        type: Optional[str]


    class azure.mgmt.compute.models.UpgradeOperationHistoricalStatusInfoProperties(_Model):
        error: Optional[ApiError]
        progress: Optional[RollingUpgradeProgressInfo]
        rollback_info: Optional[RollbackStatusInfo]
        running_status: Optional[UpgradeOperationHistoryStatus]
        started_by: Optional[Union[str, UpgradeOperationInvoker]]
        target_image_reference: Optional[ImageReference]


    class azure.mgmt.compute.models.UpgradeOperationHistoryStatus(_Model):
        code: Optional[Union[str, UpgradeState]]
        end_time: Optional[datetime]
        start_time: Optional[datetime]


    class azure.mgmt.compute.models.UpgradeOperationInvoker(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLATFORM = "Platform"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.compute.models.UpgradePolicy(_Model):
        automatic_os_upgrade_policy: Optional[AutomaticOSUpgradePolicy]
        mode: Optional[Union[str, UpgradeMode]]
        rolling_upgrade_policy: Optional[RollingUpgradePolicy]

        @overload
        def __init__(
                self, 
                *, 
                automatic_os_upgrade_policy: Optional[AutomaticOSUpgradePolicy] = ..., 
                mode: Optional[Union[str, UpgradeMode]] = ..., 
                rolling_upgrade_policy: Optional[RollingUpgradePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UpgradeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAULTED = "Faulted"
        ROLLING_FORWARD = "RollingForward"


    class azure.mgmt.compute.models.Usage(_Model):
        current_value: int
        limit: int
        name: UsageName
        unit: Literal["Count"]

        @overload
        def __init__(
                self, 
                *, 
                current_value: int, 
                limit: int, 
                name: UsageName
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UserArtifactManage(_Model):
        install: str
        remove: str
        update_property: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                install: str, 
                remove: str, 
                update_property: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UserArtifactSettings(_Model):
        config_file_name: Optional[str]
        package_file_name: Optional[str]
        script_behavior_after_reboot: Optional[Union[str, GalleryApplicationScriptRebootBehavior]]

        @overload
        def __init__(
                self, 
                *, 
                config_file_name: Optional[str] = ..., 
                package_file_name: Optional[str] = ..., 
                script_behavior_after_reboot: Optional[Union[str, GalleryApplicationScriptRebootBehavior]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UserArtifactSource(_Model):
        default_configuration_link: Optional[str]
        media_link: str

        @overload
        def __init__(
                self, 
                *, 
                default_configuration_link: Optional[str] = ..., 
                media_link: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UserAssignedIdentitiesValue(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.compute.models.UserInitiatedReboot(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.UserInitiatedRedeploy(_Model):
        automatically_approve: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                automatically_approve: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMDiskSecurityProfile(_Model):
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


    class azure.mgmt.compute.models.VMGalleryApplication(_Model):
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


    class azure.mgmt.compute.models.VMGuestPatchClassificationLinux(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        OTHER = "Other"
        SECURITY = "Security"


    class azure.mgmt.compute.models.VMGuestPatchClassificationWindows(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        DEFINITION = "Definition"
        FEATURE_PACK = "FeaturePack"
        SECURITY = "Security"
        SERVICE_PACK = "ServicePack"
        TOOLS = "Tools"
        UPDATES = "Updates"
        UPDATE_ROLL_UP = "UpdateRollUp"


    class azure.mgmt.compute.models.VMGuestPatchRebootBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS_REQUIRES_REBOOT = "AlwaysRequiresReboot"
        CAN_REQUEST_REBOOT = "CanRequestReboot"
        NEVER_REBOOTS = "NeverReboots"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.VMGuestPatchRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"


    class azure.mgmt.compute.models.VMGuestPatchRebootStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        NOT_NEEDED = "NotNeeded"
        REQUIRED = "Required"
        STARTED = "Started"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.VMScaleSetConvertToSinglePlacementGroupInput(_Model):
        active_placement_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_placement_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEvent(ProxyResource):
        id: str
        name: str
        properties: Optional[VMScaleSetLifecycleHookEventProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VMScaleSetLifecycleHookEventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventAdditionalContext(_Model):
        priority: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                priority: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventProperties(_Model):
        additional_context: Optional[VMScaleSetLifecycleHookEventAdditionalContext]
        default_action: Optional[Union[str, LifecycleHookAction]]
        max_wait_until: Optional[str]
        state: Optional[Union[str, VMScaleSetLifecycleHookEventState]]
        target_resources: Optional[list[VMScaleSetLifecycleHookEventTargetResource]]
        time_created: Optional[str]
        type: Optional[Union[str, VMScaleSetLifecycleHookEventType]]
        wait_until: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_context: Optional[VMScaleSetLifecycleHookEventAdditionalContext] = ..., 
                target_resources: Optional[list[VMScaleSetLifecycleHookEventTargetResource]] = ..., 
                type: Optional[Union[str, VMScaleSetLifecycleHookEventType]] = ..., 
                wait_until: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        COMPLETED = "Completed"


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventTargetResource(_Model):
        action_state: Optional[Union[str, LifecycleHookActionState]]
        resource: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                action_state: Optional[Union[str, LifecycleHookActionState]] = ..., 
                resource: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UPGRADE_AUTO_OS_ROLLING_BATCH_STARTING = "UpgradeAutoOSRollingBatchStarting"
        UPGRADE_AUTO_OS_SCHEDULING = "UpgradeAutoOSScheduling"


    class azure.mgmt.compute.models.VMScaleSetLifecycleHookEventUpdate(_Model):
        properties: Optional[VMScaleSetLifecycleHookEventProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VMScaleSetLifecycleHookEventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetScaleOutInput(_Model):
        capacity: int
        properties: Optional[VMScaleSetScaleOutInputProperties]

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                properties: Optional[VMScaleSetScaleOutInputProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMScaleSetScaleOutInputProperties(_Model):
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VMSizeProperties(_Model):
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


    class azure.mgmt.compute.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.ValidationsProfile(_Model):
        executed_validations: Optional[list[ExecutedValidation]]
        platform_attributes: Optional[list[PlatformAttribute]]
        validation_etag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                executed_validations: Optional[list[ExecutedValidation]] = ..., 
                platform_attributes: Optional[list[PlatformAttribute]] = ..., 
                validation_etag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VaultCertificate(_Model):
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


    class azure.mgmt.compute.models.VaultSecretGroup(_Model):
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


    class azure.mgmt.compute.models.VirtualHardDisk(_Model):
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachine(TrackedResource):
        etag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[VirtualMachineIdentity]
        location: str
        managed_by: Optional[str]
        name: str
        placement: Optional[Placement]
        plan: Optional[Plan]
        properties: Optional[VirtualMachineProperties]
        resources: Optional[list[VirtualMachineExtension]]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[VirtualMachineIdentity] = ..., 
                location: str, 
                placement: Optional[Placement] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[VirtualMachineProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineAgentInstanceView(_Model):
        extension_handlers: Optional[list[VirtualMachineExtensionHandlerInstanceView]]
        statuses: Optional[list[InstanceViewStatus]]
        vm_agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extension_handlers: Optional[list[VirtualMachineExtensionHandlerInstanceView]] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                vm_agent_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineAssessPatchesResult(_Model):
        assessment_activity_id: Optional[str]
        available_patches: Optional[list[VirtualMachineSoftwarePatchProperties]]
        critical_and_security_patch_count: Optional[int]
        error: Optional[ApiError]
        other_patch_count: Optional[int]
        reboot_pending: Optional[bool]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, PatchOperationStatus]]


    class azure.mgmt.compute.models.VirtualMachineCaptureParameters(_Model):
        destination_container_name: str
        overwrite_vhds: bool
        vhd_prefix: str

        @overload
        def __init__(
                self, 
                *, 
                destination_container_name: str, 
                overwrite_vhds: bool, 
                vhd_prefix: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineCaptureResult(SubResource):
        content_version: Optional[str]
        id: str
        parameters: Optional[Any]
        resources: Optional[list[Any]]
        schema: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineEvictionPolicyTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        DELETE = "Delete"


    class azure.mgmt.compute.models.VirtualMachineExtension(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[VirtualMachineExtensionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[VirtualMachineExtensionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionHandlerInstanceView(_Model):
        status: Optional[InstanceViewStatus]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[InstanceViewStatus] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionImage(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[VirtualMachineExtensionImageProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[VirtualMachineExtensionImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionImageProperties(_Model):
        compute_role: str
        handler_schema: str
        operating_system: str
        supports_multiple_extensions: Optional[bool]
        vm_scale_set_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                compute_role: str, 
                handler_schema: str, 
                operating_system: str, 
                supports_multiple_extensions: Optional[bool] = ..., 
                vm_scale_set_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionInstanceView(_Model):
        name: Optional[str]
        statuses: Optional[list[InstanceViewStatus]]
        substatuses: Optional[list[InstanceViewStatus]]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                substatuses: Optional[list[InstanceViewStatus]] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        instance_view: Optional[VirtualMachineExtensionInstanceView]
        protected_settings: Optional[Any]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        provision_after_extensions: Optional[list[str]]
        provisioning_state: Optional[str]
        publisher: Optional[str]
        settings: Optional[Any]
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
                instance_view: Optional[VirtualMachineExtensionInstanceView] = ..., 
                protected_settings: Optional[Any] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[Any] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionUpdate(UpdateResource):
        properties: Optional[VirtualMachineExtensionUpdateProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineExtensionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionUpdateProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[Any]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        publisher: Optional[str]
        settings: Optional[Any]
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
                protected_settings: Optional[Any] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[Any] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineExtensionsListResult(_Model):
        value: Optional[list[VirtualMachineExtension]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[VirtualMachineExtension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineHealthStatus(_Model):
        status: Optional[InstanceViewStatus]


    class azure.mgmt.compute.models.VirtualMachineIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineImage(VirtualMachineImageResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[VirtualMachineImageProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                id: Optional[str] = ..., 
                location: str, 
                name: str, 
                properties: Optional[VirtualMachineImageProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineImageFeature(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineImageProperties(_Model):
        architecture: Optional[Union[str, ArchitectureTypes]]
        automatic_os_upgrade_properties: Optional[AutomaticOSUpgradeProperties]
        data_disk_images: Optional[list[DataDiskImage]]
        disallowed: Optional[DisallowedConfiguration]
        features: Optional[list[VirtualMachineImageFeature]]
        hyper_v_generation: Optional[Union[str, HyperVGenerationTypes]]
        image_deprecation_status: Optional[ImageDeprecationStatus]
        os_disk_image: Optional[OSDiskImage]
        plan: Optional[PurchasePlan]

        @overload
        def __init__(
                self, 
                *, 
                architecture: Optional[Union[str, ArchitectureTypes]] = ..., 
                automatic_os_upgrade_properties: Optional[AutomaticOSUpgradeProperties] = ..., 
                data_disk_images: Optional[list[DataDiskImage]] = ..., 
                disallowed: Optional[DisallowedConfiguration] = ..., 
                features: Optional[list[VirtualMachineImageFeature]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGenerationTypes]] = ..., 
                image_deprecation_status: Optional[ImageDeprecationStatus] = ..., 
                os_disk_image: Optional[OSDiskImage] = ..., 
                plan: Optional[PurchasePlan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineImageResource(SubResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                id: Optional[str] = ..., 
                location: str, 
                name: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineInstallPatchesParameters(_Model):
        linux_parameters: Optional[LinuxParameters]
        maximum_duration: Optional[timedelta]
        reboot_setting: Union[str, VMGuestPatchRebootSetting]
        windows_parameters: Optional[WindowsParameters]

        @overload
        def __init__(
                self, 
                *, 
                linux_parameters: Optional[LinuxParameters] = ..., 
                maximum_duration: Optional[timedelta] = ..., 
                reboot_setting: Union[str, VMGuestPatchRebootSetting], 
                windows_parameters: Optional[WindowsParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineInstallPatchesResult(_Model):
        error: Optional[ApiError]
        excluded_patch_count: Optional[int]
        failed_patch_count: Optional[int]
        installation_activity_id: Optional[str]
        installed_patch_count: Optional[int]
        maintenance_window_exceeded: Optional[bool]
        not_selected_patch_count: Optional[int]
        patches: Optional[list[PatchInstallationDetail]]
        pending_patch_count: Optional[int]
        reboot_status: Optional[Union[str, VMGuestPatchRebootStatus]]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, PatchOperationStatus]]


    class azure.mgmt.compute.models.VirtualMachineInstanceView(_Model):
        assigned_host: Optional[str]
        boot_diagnostics: Optional[BootDiagnosticsInstanceView]
        computer_name: Optional[str]
        disks: Optional[list[DiskInstanceView]]
        extensions: Optional[list[VirtualMachineExtensionInstanceView]]
        hyper_v_generation: Optional[Union[str, HyperVGenerationType]]
        is_vm_in_standby_pool: Optional[bool]
        maintenance_redeploy_status: Optional[MaintenanceRedeployStatus]
        os_name: Optional[str]
        os_version: Optional[str]
        patch_status: Optional[VirtualMachinePatchStatus]
        platform_fault_domain: Optional[int]
        platform_update_domain: Optional[int]
        rdp_thumb_print: Optional[str]
        statuses: Optional[list[InstanceViewStatus]]
        vm_agent: Optional[VirtualMachineAgentInstanceView]
        vm_health: Optional[VirtualMachineHealthStatus]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnosticsInstanceView] = ..., 
                computer_name: Optional[str] = ..., 
                disks: Optional[list[DiskInstanceView]] = ..., 
                extensions: Optional[list[VirtualMachineExtensionInstanceView]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGenerationType]] = ..., 
                maintenance_redeploy_status: Optional[MaintenanceRedeployStatus] = ..., 
                os_name: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                patch_status: Optional[VirtualMachinePatchStatus] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                platform_update_domain: Optional[int] = ..., 
                rdp_thumb_print: Optional[str] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                vm_agent: Optional[VirtualMachineAgentInstanceView] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineIpTag(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineNetworkInterfaceConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceConfigurationProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

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

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineNetworkInterfaceConfigurationProperties(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineNetworkInterfaceDnsSettingsConfiguration(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineNetworkInterfaceIPConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineNetworkInterfaceIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineNetworkInterfaceIPConfigurationProperties(_Model):
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


    class azure.mgmt.compute.models.VirtualMachinePatchStatus(_Model):
        available_patch_summary: Optional[AvailablePatchSummary]
        configuration_statuses: Optional[list[InstanceViewStatus]]
        last_patch_installation_summary: Optional[LastPatchInstallationSummary]

        @overload
        def __init__(
                self, 
                *, 
                available_patch_summary: Optional[AvailablePatchSummary] = ..., 
                last_patch_installation_summary: Optional[LastPatchInstallationSummary] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachinePriorityTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOW = "Low"
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.compute.models.VirtualMachineProperties(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        application_profile: Optional[ApplicationProfile]
        availability_set: Optional[SubResource]
        billing_profile: Optional[BillingProfile]
        capacity_reservation: Optional[CapacityReservationProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        eviction_policy: Optional[Union[str, VirtualMachineEvictionPolicyTypes]]
        extensions_time_budget: Optional[str]
        hardware_profile: Optional[HardwareProfile]
        host: Optional[SubResource]
        host_group: Optional[SubResource]
        instance_view: Optional[VirtualMachineInstanceView]
        license_type: Optional[str]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OSProfile]
        platform_fault_domain: Optional[int]
        priority: Optional[Union[str, VirtualMachinePriorityTypes]]
        provisioning_state: Optional[str]
        proximity_placement_group: Optional[SubResource]
        resiliency_profile: Optional[ResiliencyProfile]
        scheduled_events_policy: Optional[ScheduledEventsPolicy]
        scheduled_events_profile: Optional[ScheduledEventsProfile]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[StorageProfile]
        time_created: Optional[datetime]
        user_data: Optional[str]
        virtual_machine_scale_set: Optional[SubResource]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                application_profile: Optional[ApplicationProfile] = ..., 
                availability_set: Optional[SubResource] = ..., 
                billing_profile: Optional[BillingProfile] = ..., 
                capacity_reservation: Optional[CapacityReservationProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                eviction_policy: Optional[Union[str, VirtualMachineEvictionPolicyTypes]] = ..., 
                extensions_time_budget: Optional[str] = ..., 
                hardware_profile: Optional[HardwareProfile] = ..., 
                host: Optional[SubResource] = ..., 
                host_group: Optional[SubResource] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                priority: Optional[Union[str, VirtualMachinePriorityTypes]] = ..., 
                proximity_placement_group: Optional[SubResource] = ..., 
                resiliency_profile: Optional[ResiliencyProfile] = ..., 
                scheduled_events_policy: Optional[ScheduledEventsPolicy] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
                user_data: Optional[str] = ..., 
                virtual_machine_scale_set: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachinePublicIPAddressConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachinePublicIPAddressConfigurationProperties]
        sku: Optional[PublicIPAddressSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

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

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachinePublicIPAddressConfigurationProperties(_Model):
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


    class azure.mgmt.compute.models.VirtualMachinePublicIPAddressDnsSettingsConfiguration(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineReimageParameters(_Model):
        exact_version: Optional[str]
        os_profile: Optional[OSProfileProvisioningData]
        temp_disk: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exact_version: Optional[str] = ..., 
                os_profile: Optional[OSProfileProvisioningData] = ..., 
                temp_disk: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineRunCommand(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[VirtualMachineRunCommandProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[VirtualMachineRunCommandProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineRunCommandInstanceView(_Model):
        end_time: Optional[datetime]
        error: Optional[str]
        execution_message: Optional[str]
        execution_state: Optional[Union[str, ExecutionState]]
        exit_code: Optional[int]
        output: Optional[str]
        start_time: Optional[datetime]
        statuses: Optional[list[InstanceViewStatus]]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[str] = ..., 
                execution_message: Optional[str] = ..., 
                execution_state: Optional[Union[str, ExecutionState]] = ..., 
                exit_code: Optional[int] = ..., 
                output: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineRunCommandProperties(_Model):
        async_execution: Optional[bool]
        error_blob_managed_identity: Optional[RunCommandManagedIdentity]
        error_blob_uri: Optional[str]
        instance_view: Optional[VirtualMachineRunCommandInstanceView]
        output_blob_managed_identity: Optional[RunCommandManagedIdentity]
        output_blob_uri: Optional[str]
        parameters: Optional[list[RunCommandInputParameter]]
        protected_parameters: Optional[list[RunCommandInputParameter]]
        provisioning_state: Optional[str]
        run_as_password: Optional[str]
        run_as_user: Optional[str]
        source: Optional[VirtualMachineRunCommandScriptSource]
        timeout_in_seconds: Optional[int]
        treat_failure_as_deployment_failure: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                async_execution: Optional[bool] = ..., 
                error_blob_managed_identity: Optional[RunCommandManagedIdentity] = ..., 
                error_blob_uri: Optional[str] = ..., 
                output_blob_managed_identity: Optional[RunCommandManagedIdentity] = ..., 
                output_blob_uri: Optional[str] = ..., 
                parameters: Optional[list[RunCommandInputParameter]] = ..., 
                protected_parameters: Optional[list[RunCommandInputParameter]] = ..., 
                run_as_password: Optional[str] = ..., 
                run_as_user: Optional[str] = ..., 
                source: Optional[VirtualMachineRunCommandScriptSource] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                treat_failure_as_deployment_failure: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineRunCommandScriptSource(_Model):
        command_id: Optional[str]
        gallery_script_reference_id: Optional[str]
        script: Optional[str]
        script_shell: Optional[Union[str, ScriptShellTypes]]
        script_uri: Optional[str]
        script_uri_managed_identity: Optional[RunCommandManagedIdentity]

        @overload
        def __init__(
                self, 
                *, 
                command_id: Optional[str] = ..., 
                gallery_script_reference_id: Optional[str] = ..., 
                script: Optional[str] = ..., 
                script_shell: Optional[Union[str, ScriptShellTypes]] = ..., 
                script_uri: Optional[str] = ..., 
                script_uri_managed_identity: Optional[RunCommandManagedIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineRunCommandUpdate(UpdateResource):
        properties: Optional[VirtualMachineRunCommandProperties]
        tags: dict[str, str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineRunCommandProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSet(TrackedResource):
        etag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        identity: Optional[VirtualMachineScaleSetIdentity]
        location: str
        name: str
        placement: Optional[Placement]
        plan: Optional[Plan]
        properties: Optional[VirtualMachineScaleSetProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                identity: Optional[VirtualMachineScaleSetIdentity] = ..., 
                location: str, 
                placement: Optional[Placement] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[VirtualMachineScaleSetProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetDataDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        disk_iops_read_write: Optional[int]
        disk_m_bps_read_write: Optional[int]
        disk_size_gb: Optional[int]
        lun: int
        managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters]
        name: Optional[str]
        storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]]
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
                storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetExtension(SubResourceReadOnly):
        id: str
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetExtensionProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VirtualMachineScaleSetExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetExtensionProfile(_Model):
        extensions: Optional[list[VirtualMachineScaleSetExtension]]
        extensions_time_budget: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                extensions: Optional[list[VirtualMachineScaleSetExtension]] = ..., 
                extensions_time_budget: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[Any]
        protected_settings_from_key_vault: Optional[KeyVaultSecretReference]
        provision_after_extensions: Optional[list[str]]
        provisioning_state: Optional[str]
        publisher: Optional[str]
        settings: Optional[Any]
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
                protected_settings: Optional[Any] = ..., 
                protected_settings_from_key_vault: Optional[KeyVaultSecretReference] = ..., 
                provision_after_extensions: Optional[list[str]] = ..., 
                publisher: Optional[str] = ..., 
                settings: Optional[Any] = ..., 
                suppress_failures: Optional[bool] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetExtensionUpdate(SubResourceReadOnly):
        id: str
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetExtensionProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineScaleSetExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetHardwareProfile(_Model):
        vm_size_properties: Optional[VMSizeProperties]

        @overload
        def __init__(
                self, 
                *, 
                vm_size_properties: Optional[VMSizeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetIPConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetIPConfigurationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetIPConfigurationProperties(_Model):
        application_gateway_backend_address_pools: Optional[list[SubResource]]
        application_security_groups: Optional[list[SubResource]]
        load_balancer_backend_address_pools: Optional[list[SubResource]]
        load_balancer_inbound_nat_pools: Optional[list[SubResource]]
        primary: Optional[bool]
        private_ip_address_version: Optional[Union[str, IPVersion]]
        public_ip_address_configuration: Optional[VirtualMachineScaleSetPublicIPAddressConfiguration]
        subnet: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[list[SubResource]] = ..., 
                application_security_groups: Optional[list[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[list[SubResource]] = ..., 
                load_balancer_inbound_nat_pools: Optional[list[SubResource]] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address_version: Optional[Union[str, IPVersion]] = ..., 
                public_ip_address_configuration: Optional[VirtualMachineScaleSetPublicIPAddressConfiguration] = ..., 
                subnet: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentitiesValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetInstanceView(_Model):
        extensions: Optional[list[VirtualMachineScaleSetVMExtensionsSummary]]
        orchestration_services: Optional[list[OrchestrationServiceSummary]]
        statuses: Optional[list[InstanceViewStatus]]
        virtual_machine: Optional[VirtualMachineScaleSetInstanceViewStatusesSummary]

        @overload
        def __init__(
                self, 
                *, 
                statuses: Optional[list[InstanceViewStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetInstanceViewStatusesSummary(_Model):
        statuses_summary: Optional[list[VirtualMachineStatusCodeCount]]


    class azure.mgmt.compute.models.VirtualMachineScaleSetIpTag(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineScaleSetManagedDiskParameters(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineScaleSetMigrationInfo(_Model):
        default_virtual_machine_scale_set_info: Optional[DefaultVirtualMachineScaleSetInfo]
        migrate_to_virtual_machine_scale_set: Optional[SubResource]


    class azure.mgmt.compute.models.VirtualMachineScaleSetNetworkConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetNetworkConfigurationProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetNetworkConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetNetworkConfigurationDnsSettings(_Model):
        dns_servers: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetNetworkConfigurationProperties(_Model):
        auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]]
        auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]]
        delete_option: Optional[Union[str, DeleteOptions]]
        disable_tcp_state_tracking: Optional[bool]
        dns_settings: Optional[VirtualMachineScaleSetNetworkConfigurationDnsSettings]
        enable_accelerated_networking: Optional[bool]
        enable_fpga: Optional[bool]
        enable_ip_forwarding: Optional[bool]
        ip_configurations: list[VirtualMachineScaleSetIPConfiguration]
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
                ip_configurations: list[VirtualMachineScaleSetIPConfiguration], 
                network_security_group: Optional[SubResource] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetNetworkProfile(_Model):
        health_probe: Optional[ApiEntityReference]
        network_api_version: Optional[Union[str, NetworkApiVersion]]
        network_interface_configurations: Optional[list[VirtualMachineScaleSetNetworkConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                health_probe: Optional[ApiEntityReference] = ..., 
                network_api_version: Optional[Union[str, NetworkApiVersion]] = ..., 
                network_interface_configurations: Optional[list[VirtualMachineScaleSetNetworkConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetOSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        create_option: Union[str, DiskCreateOptionTypes]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        diff_disk_settings: Optional[DiffDiskSettings]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters]
        name: Optional[str]
        os_type: Optional[Union[str, OperatingSystemTypes]]
        storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]]
        vhd_containers: Optional[list[str]]
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
                storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]] = ..., 
                vhd_containers: Optional[list[str]] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetOSProfile(_Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        allow_extension_operations: Optional[bool]
        computer_name_prefix: Optional[str]
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
                computer_name_prefix: Optional[str] = ..., 
                custom_data: Optional[str] = ..., 
                linux_configuration: Optional[LinuxConfiguration] = ..., 
                require_guest_provision_signal: Optional[bool] = ..., 
                secrets: Optional[list[VaultSecretGroup]] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetProperties(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        automatic_repairs_policy: Optional[AutomaticRepairsPolicy]
        constrained_maximum_capacity: Optional[bool]
        do_not_run_extensions_on_overprovisioned_v_ms: Optional[bool]
        external_health_policy: Optional[ExternalHealthPolicy]
        high_speed_interconnect_placement: Optional[Union[str, HighSpeedInterconnectPlacement]]
        host_group: Optional[SubResource]
        lifecycle_hooks_profile: Optional[LifecycleHooksProfile]
        orchestration_mode: Optional[Union[str, OrchestrationMode]]
        overprovision: Optional[bool]
        platform_fault_domain_count: Optional[int]
        priority_mix_policy: Optional[PriorityMixPolicy]
        provisioning_state: Optional[str]
        proximity_placement_group: Optional[SubResource]
        resiliency_policy: Optional[ResiliencyPolicy]
        scale_in_policy: Optional[ScaleInPolicy]
        scheduled_events_policy: Optional[ScheduledEventsPolicy]
        single_placement_group: Optional[bool]
        sku_profile: Optional[SkuProfile]
        spot_restore_policy: Optional[SpotRestorePolicy]
        time_created: Optional[datetime]
        unique_id: Optional[str]
        upgrade_policy: Optional[UpgradePolicy]
        virtual_machine_profile: Optional[VirtualMachineScaleSetVMProfile]
        zonal_platform_fault_domain_align_mode: Optional[Union[str, ZonalPlatformFaultDomainAlignMode]]
        zone_balance: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                automatic_repairs_policy: Optional[AutomaticRepairsPolicy] = ..., 
                constrained_maximum_capacity: Optional[bool] = ..., 
                do_not_run_extensions_on_overprovisioned_v_ms: Optional[bool] = ..., 
                external_health_policy: Optional[ExternalHealthPolicy] = ..., 
                high_speed_interconnect_placement: Optional[Union[str, HighSpeedInterconnectPlacement]] = ..., 
                host_group: Optional[SubResource] = ..., 
                lifecycle_hooks_profile: Optional[LifecycleHooksProfile] = ..., 
                orchestration_mode: Optional[Union[str, OrchestrationMode]] = ..., 
                overprovision: Optional[bool] = ..., 
                platform_fault_domain_count: Optional[int] = ..., 
                priority_mix_policy: Optional[PriorityMixPolicy] = ..., 
                proximity_placement_group: Optional[SubResource] = ..., 
                resiliency_policy: Optional[ResiliencyPolicy] = ..., 
                scale_in_policy: Optional[ScaleInPolicy] = ..., 
                scheduled_events_policy: Optional[ScheduledEventsPolicy] = ..., 
                single_placement_group: Optional[bool] = ..., 
                sku_profile: Optional[SkuProfile] = ..., 
                spot_restore_policy: Optional[SpotRestorePolicy] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                virtual_machine_profile: Optional[VirtualMachineScaleSetVMProfile] = ..., 
                zonal_platform_fault_domain_align_mode: Optional[Union[str, ZonalPlatformFaultDomainAlignMode]] = ..., 
                zone_balance: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetPublicIPAddressConfiguration(_Model):
        name: str
        properties: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationProperties]
        sku: Optional[PublicIPAddressSku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationProperties] = ..., 
                sku: Optional[PublicIPAddressSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings(_Model):
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


    class azure.mgmt.compute.models.VirtualMachineScaleSetPublicIPAddressConfigurationProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings]
        idle_timeout_in_minutes: Optional[int]
        ip_tags: Optional[list[VirtualMachineScaleSetIpTag]]
        public_ip_address_version: Optional[Union[str, IPVersion]]
        public_ip_prefix: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                ip_tags: Optional[list[VirtualMachineScaleSetIpTag]] = ..., 
                public_ip_address_version: Optional[Union[str, IPVersion]] = ..., 
                public_ip_prefix: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetReimageParameters(VirtualMachineScaleSetVMReimageParameters):
        exact_version: str
        force_update_os_disk_for_ephemeral: bool
        instance_ids: Optional[list[str]]
        os_profile: OSProfileProvisioningData
        temp_disk: bool

        @overload
        def __init__(
                self, 
                *, 
                exact_version: Optional[str] = ..., 
                force_update_os_disk_for_ephemeral: Optional[bool] = ..., 
                instance_ids: Optional[list[str]] = ..., 
                os_profile: Optional[OSProfileProvisioningData] = ..., 
                temp_disk: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetScaleInRules(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NEWEST_VM = "NewestVM"
        OLDEST_VM = "OldestVM"


    class azure.mgmt.compute.models.VirtualMachineScaleSetSku(_Model):
        capacity: Optional[VirtualMachineScaleSetSkuCapacity]
        resource_type: Optional[str]
        sku: Optional[Sku]


    class azure.mgmt.compute.models.VirtualMachineScaleSetSkuCapacity(_Model):
        default_capacity: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        scale_type: Optional[Union[str, VirtualMachineScaleSetSkuScaleType]]


    class azure.mgmt.compute.models.VirtualMachineScaleSetSkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        NONE = "None"


    class azure.mgmt.compute.models.VirtualMachineScaleSetStorageProfile(_Model):
        data_disks: Optional[list[VirtualMachineScaleSetDataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[VirtualMachineScaleSetOSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[VirtualMachineScaleSetDataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[VirtualMachineScaleSetOSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdate(UpdateResource):
        identity: Optional[VirtualMachineScaleSetIdentity]
        placement: Optional[Placement]
        plan: Optional[Plan]
        properties: Optional[VirtualMachineScaleSetUpdateProperties]
        sku: Optional[Sku]
        tags: dict[str, str]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[VirtualMachineScaleSetIdentity] = ..., 
                placement: Optional[Placement] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[VirtualMachineScaleSetUpdateProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateIPConfiguration(_Model):
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetUpdateIPConfigurationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VirtualMachineScaleSetUpdateIPConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateIPConfigurationProperties(_Model):
        application_gateway_backend_address_pools: Optional[list[SubResource]]
        application_security_groups: Optional[list[SubResource]]
        load_balancer_backend_address_pools: Optional[list[SubResource]]
        load_balancer_inbound_nat_pools: Optional[list[SubResource]]
        primary: Optional[bool]
        private_ip_address_version: Optional[Union[str, IPVersion]]
        public_ip_address_configuration: Optional[VirtualMachineScaleSetUpdatePublicIPAddressConfiguration]
        subnet: Optional[ApiEntityReference]

        @overload
        def __init__(
                self, 
                *, 
                application_gateway_backend_address_pools: Optional[list[SubResource]] = ..., 
                application_security_groups: Optional[list[SubResource]] = ..., 
                load_balancer_backend_address_pools: Optional[list[SubResource]] = ..., 
                load_balancer_inbound_nat_pools: Optional[list[SubResource]] = ..., 
                primary: Optional[bool] = ..., 
                private_ip_address_version: Optional[Union[str, IPVersion]] = ..., 
                public_ip_address_configuration: Optional[VirtualMachineScaleSetUpdatePublicIPAddressConfiguration] = ..., 
                subnet: Optional[ApiEntityReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateNetworkConfiguration(_Model):
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetUpdateNetworkConfigurationProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VirtualMachineScaleSetUpdateNetworkConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateNetworkConfigurationProperties(_Model):
        auxiliary_mode: Optional[Union[str, NetworkInterfaceAuxiliaryMode]]
        auxiliary_sku: Optional[Union[str, NetworkInterfaceAuxiliarySku]]
        delete_option: Optional[Union[str, DeleteOptions]]
        disable_tcp_state_tracking: Optional[bool]
        dns_settings: Optional[VirtualMachineScaleSetNetworkConfigurationDnsSettings]
        enable_accelerated_networking: Optional[bool]
        enable_fpga: Optional[bool]
        enable_ip_forwarding: Optional[bool]
        ip_configurations: Optional[list[VirtualMachineScaleSetUpdateIPConfiguration]]
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
                ip_configurations: Optional[list[VirtualMachineScaleSetUpdateIPConfiguration]] = ..., 
                network_security_group: Optional[SubResource] = ..., 
                primary: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateNetworkProfile(_Model):
        health_probe: Optional[ApiEntityReference]
        network_api_version: Optional[Union[str, NetworkApiVersion]]
        network_interface_configurations: Optional[list[VirtualMachineScaleSetUpdateNetworkConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                health_probe: Optional[ApiEntityReference] = ..., 
                network_api_version: Optional[Union[str, NetworkApiVersion]] = ..., 
                network_interface_configurations: Optional[list[VirtualMachineScaleSetUpdateNetworkConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateOSDisk(_Model):
        caching: Optional[Union[str, CachingTypes]]
        delete_option: Optional[Union[str, DiskDeleteOptionTypes]]
        diff_disk_settings: Optional[DiffDiskSettings]
        disk_size_gb: Optional[int]
        image: Optional[VirtualHardDisk]
        managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters]
        storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]]
        vhd_containers: Optional[list[str]]
        write_accelerator_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingTypes]] = ..., 
                delete_option: Optional[Union[str, DiskDeleteOptionTypes]] = ..., 
                diff_disk_settings: Optional[DiffDiskSettings] = ..., 
                disk_size_gb: Optional[int] = ..., 
                image: Optional[VirtualHardDisk] = ..., 
                managed_disk: Optional[VirtualMachineScaleSetManagedDiskParameters] = ..., 
                storage_fault_domain_alignment: Optional[Union[str, StorageFaultDomainAlignmentType]] = ..., 
                vhd_containers: Optional[list[str]] = ..., 
                write_accelerator_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateOSProfile(_Model):
        custom_data: Optional[str]
        linux_configuration: Optional[LinuxConfiguration]
        secrets: Optional[list[VaultSecretGroup]]
        windows_configuration: Optional[WindowsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                custom_data: Optional[str] = ..., 
                linux_configuration: Optional[LinuxConfiguration] = ..., 
                secrets: Optional[list[VaultSecretGroup]] = ..., 
                windows_configuration: Optional[WindowsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateProperties(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        automatic_repairs_policy: Optional[AutomaticRepairsPolicy]
        do_not_run_extensions_on_overprovisioned_v_ms: Optional[bool]
        lifecycle_hooks_profile: Optional[LifecycleHooksProfile]
        overprovision: Optional[bool]
        priority_mix_policy: Optional[PriorityMixPolicy]
        proximity_placement_group: Optional[SubResource]
        resiliency_policy: Optional[ResiliencyPolicy]
        scale_in_policy: Optional[ScaleInPolicy]
        single_placement_group: Optional[bool]
        sku_profile: Optional[SkuProfile]
        spot_restore_policy: Optional[SpotRestorePolicy]
        upgrade_policy: Optional[UpgradePolicy]
        virtual_machine_profile: Optional[VirtualMachineScaleSetUpdateVMProfile]
        zonal_platform_fault_domain_align_mode: Optional[Union[str, ZonalPlatformFaultDomainAlignMode]]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                automatic_repairs_policy: Optional[AutomaticRepairsPolicy] = ..., 
                do_not_run_extensions_on_overprovisioned_v_ms: Optional[bool] = ..., 
                lifecycle_hooks_profile: Optional[LifecycleHooksProfile] = ..., 
                overprovision: Optional[bool] = ..., 
                priority_mix_policy: Optional[PriorityMixPolicy] = ..., 
                proximity_placement_group: Optional[SubResource] = ..., 
                resiliency_policy: Optional[ResiliencyPolicy] = ..., 
                scale_in_policy: Optional[ScaleInPolicy] = ..., 
                single_placement_group: Optional[bool] = ..., 
                sku_profile: Optional[SkuProfile] = ..., 
                spot_restore_policy: Optional[SpotRestorePolicy] = ..., 
                upgrade_policy: Optional[UpgradePolicy] = ..., 
                virtual_machine_profile: Optional[VirtualMachineScaleSetUpdateVMProfile] = ..., 
                zonal_platform_fault_domain_align_mode: Optional[Union[str, ZonalPlatformFaultDomainAlignMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdatePublicIPAddressConfiguration(_Model):
        name: Optional[str]
        properties: Optional[VirtualMachineScaleSetUpdatePublicIPAddressConfigurationProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[VirtualMachineScaleSetUpdatePublicIPAddressConfigurationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdatePublicIPAddressConfigurationProperties(_Model):
        delete_option: Optional[Union[str, DeleteOptions]]
        dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings]
        idle_timeout_in_minutes: Optional[int]
        public_ip_prefix: Optional[SubResource]

        @overload
        def __init__(
                self, 
                *, 
                delete_option: Optional[Union[str, DeleteOptions]] = ..., 
                dns_settings: Optional[VirtualMachineScaleSetPublicIPAddressConfigurationDnsSettings] = ..., 
                idle_timeout_in_minutes: Optional[int] = ..., 
                public_ip_prefix: Optional[SubResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateStorageProfile(_Model):
        data_disks: Optional[list[VirtualMachineScaleSetDataDisk]]
        disk_controller_type: Optional[Union[str, DiskControllerTypes]]
        image_reference: Optional[ImageReference]
        os_disk: Optional[VirtualMachineScaleSetUpdateOSDisk]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[VirtualMachineScaleSetDataDisk]] = ..., 
                disk_controller_type: Optional[Union[str, DiskControllerTypes]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_disk: Optional[VirtualMachineScaleSetUpdateOSDisk] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetUpdateVMProfile(_Model):
        billing_profile: Optional[BillingProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        extension_profile: Optional[VirtualMachineScaleSetExtensionProfile]
        hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile]
        license_type: Optional[str]
        network_profile: Optional[VirtualMachineScaleSetUpdateNetworkProfile]
        os_profile: Optional[VirtualMachineScaleSetUpdateOSProfile]
        scheduled_events_profile: Optional[ScheduledEventsProfile]
        security_posture_reference: Optional[SecurityPostureReferenceUpdate]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[VirtualMachineScaleSetUpdateStorageProfile]
        user_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_profile: Optional[BillingProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                extension_profile: Optional[VirtualMachineScaleSetExtensionProfile] = ..., 
                hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[VirtualMachineScaleSetUpdateNetworkProfile] = ..., 
                os_profile: Optional[VirtualMachineScaleSetUpdateOSProfile] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_posture_reference: Optional[SecurityPostureReferenceUpdate] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[VirtualMachineScaleSetUpdateStorageProfile] = ..., 
                user_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVM(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[VirtualMachineIdentity]
        instance_id: Optional[str]
        location: str
        name: str
        plan: Optional[Plan]
        properties: Optional[VirtualMachineScaleSetVMProperties]
        resources: Optional[list[VirtualMachineExtension]]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[VirtualMachineIdentity] = ..., 
                location: str, 
                plan: Optional[Plan] = ..., 
                properties: Optional[VirtualMachineScaleSetVMProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMExtension(SubResourceReadOnly):
        id: str
        location: Optional[str]
        name: Optional[str]
        properties: Optional[VirtualMachineExtensionProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VirtualMachineExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMExtensionUpdate(SubResourceReadOnly):
        id: str
        name: Optional[str]
        properties: Optional[VirtualMachineExtensionUpdateProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineExtensionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMExtensionsListResult(_Model):
        value: Optional[list[VirtualMachineScaleSetVMExtension]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[VirtualMachineScaleSetVMExtension]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMExtensionsSummary(_Model):
        name: Optional[str]
        statuses_summary: Optional[list[VirtualMachineStatusCodeCount]]


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMInstanceIDs(_Model):
        instance_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                instance_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMInstanceRequiredIDs(_Model):
        instance_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                instance_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMInstanceView(_Model):
        assigned_host: Optional[str]
        boot_diagnostics: Optional[BootDiagnosticsInstanceView]
        computer_name: Optional[str]
        disks: Optional[list[DiskInstanceView]]
        extensions: Optional[list[VirtualMachineExtensionInstanceView]]
        hyper_v_generation: Optional[Union[str, HyperVGeneration]]
        maintenance_redeploy_status: Optional[MaintenanceRedeployStatus]
        os_name: Optional[str]
        os_version: Optional[str]
        placement_group_id: Optional[str]
        platform_fault_domain: Optional[int]
        platform_update_domain: Optional[int]
        rdp_thumb_print: Optional[str]
        statuses: Optional[list[InstanceViewStatus]]
        vm_agent: Optional[VirtualMachineAgentInstanceView]
        vm_health: Optional[VirtualMachineHealthStatus]

        @overload
        def __init__(
                self, 
                *, 
                boot_diagnostics: Optional[BootDiagnosticsInstanceView] = ..., 
                computer_name: Optional[str] = ..., 
                disks: Optional[list[DiskInstanceView]] = ..., 
                extensions: Optional[list[VirtualMachineExtensionInstanceView]] = ..., 
                hyper_v_generation: Optional[Union[str, HyperVGeneration]] = ..., 
                maintenance_redeploy_status: Optional[MaintenanceRedeployStatus] = ..., 
                os_name: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                placement_group_id: Optional[str] = ..., 
                platform_fault_domain: Optional[int] = ..., 
                platform_update_domain: Optional[int] = ..., 
                rdp_thumb_print: Optional[str] = ..., 
                statuses: Optional[list[InstanceViewStatus]] = ..., 
                vm_agent: Optional[VirtualMachineAgentInstanceView] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMNetworkProfileConfiguration(_Model):
        network_interface_configurations: Optional[list[VirtualMachineScaleSetNetworkConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                network_interface_configurations: Optional[list[VirtualMachineScaleSetNetworkConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMProfile(_Model):
        application_profile: Optional[ApplicationProfile]
        billing_profile: Optional[BillingProfile]
        capacity_reservation: Optional[CapacityReservationProfile]
        diagnostics_profile: Optional[DiagnosticsProfile]
        eviction_policy: Optional[Union[str, VirtualMachineEvictionPolicyTypes]]
        extension_profile: Optional[VirtualMachineScaleSetExtensionProfile]
        hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile]
        license_type: Optional[str]
        network_profile: Optional[VirtualMachineScaleSetNetworkProfile]
        os_profile: Optional[VirtualMachineScaleSetOSProfile]
        priority: Optional[Union[str, VirtualMachinePriorityTypes]]
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
                billing_profile: Optional[BillingProfile] = ..., 
                capacity_reservation: Optional[CapacityReservationProfile] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                eviction_policy: Optional[Union[str, VirtualMachineEvictionPolicyTypes]] = ..., 
                extension_profile: Optional[VirtualMachineScaleSetExtensionProfile] = ..., 
                hardware_profile: Optional[VirtualMachineScaleSetHardwareProfile] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[VirtualMachineScaleSetNetworkProfile] = ..., 
                os_profile: Optional[VirtualMachineScaleSetOSProfile] = ..., 
                priority: Optional[Union[str, VirtualMachinePriorityTypes]] = ..., 
                scheduled_events_profile: Optional[ScheduledEventsProfile] = ..., 
                security_posture_reference: Optional[SecurityPostureReference] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                service_artifact_reference: Optional[ServiceArtifactReference] = ..., 
                storage_profile: Optional[VirtualMachineScaleSetStorageProfile] = ..., 
                user_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMProperties(_Model):
        additional_capabilities: Optional[AdditionalCapabilities]
        availability_set: Optional[SubResource]
        diagnostics_profile: Optional[DiagnosticsProfile]
        hardware_profile: Optional[HardwareProfile]
        instance_view: Optional[VirtualMachineScaleSetVMInstanceView]
        latest_model_applied: Optional[bool]
        license_type: Optional[str]
        model_definition_applied: Optional[str]
        network_profile: Optional[NetworkProfile]
        network_profile_configuration: Optional[VirtualMachineScaleSetVMNetworkProfileConfiguration]
        os_profile: Optional[OSProfile]
        protection_policy: Optional[VirtualMachineScaleSetVMProtectionPolicy]
        provisioning_state: Optional[str]
        resilient_vm_deletion_status: Optional[Union[str, ResilientVMDeletionStatus]]
        security_profile: Optional[SecurityProfile]
        storage_profile: Optional[StorageProfile]
        time_created: Optional[datetime]
        user_data: Optional[str]
        virtual_machine_resource_id: Optional[str]
        vm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_capabilities: Optional[AdditionalCapabilities] = ..., 
                availability_set: Optional[SubResource] = ..., 
                diagnostics_profile: Optional[DiagnosticsProfile] = ..., 
                hardware_profile: Optional[HardwareProfile] = ..., 
                license_type: Optional[str] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                network_profile_configuration: Optional[VirtualMachineScaleSetVMNetworkProfileConfiguration] = ..., 
                os_profile: Optional[OSProfile] = ..., 
                protection_policy: Optional[VirtualMachineScaleSetVMProtectionPolicy] = ..., 
                resilient_vm_deletion_status: Optional[Union[str, ResilientVMDeletionStatus]] = ..., 
                security_profile: Optional[SecurityProfile] = ..., 
                storage_profile: Optional[StorageProfile] = ..., 
                user_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMProtectionPolicy(_Model):
        protect_from_scale_in: Optional[bool]
        protect_from_scale_set_actions: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                protect_from_scale_in: Optional[bool] = ..., 
                protect_from_scale_set_actions: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineScaleSetVMReimageParameters(VirtualMachineReimageParameters):
        exact_version: str
        force_update_os_disk_for_ephemeral: Optional[bool]
        os_profile: OSProfileProvisioningData
        temp_disk: bool

        @overload
        def __init__(
                self, 
                *, 
                exact_version: Optional[str] = ..., 
                force_update_os_disk_for_ephemeral: Optional[bool] = ..., 
                os_profile: Optional[OSProfileProvisioningData] = ..., 
                temp_disk: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineSize(_Model):
        max_data_disk_count: Optional[int]
        memory_in_mb: Optional[int]
        name: Optional[str]
        number_of_cores: Optional[int]
        os_disk_size_in_mb: Optional[int]
        resource_disk_size_in_mb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_data_disk_count: Optional[int] = ..., 
                memory_in_mb: Optional[int] = ..., 
                name: Optional[str] = ..., 
                number_of_cores: Optional[int] = ..., 
                os_disk_size_in_mb: Optional[int] = ..., 
                resource_disk_size_in_mb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.VirtualMachineSizeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC_A0 = "Basic_A0"
        BASIC_A1 = "Basic_A1"
        BASIC_A2 = "Basic_A2"
        BASIC_A3 = "Basic_A3"
        BASIC_A4 = "Basic_A4"
        STANDARD_A0 = "Standard_A0"
        STANDARD_A1 = "Standard_A1"
        STANDARD_A10 = "Standard_A10"
        STANDARD_A11 = "Standard_A11"
        STANDARD_A1_V2 = "Standard_A1_v2"
        STANDARD_A2 = "Standard_A2"
        STANDARD_A2_M_V2 = "Standard_A2m_v2"
        STANDARD_A2_V2 = "Standard_A2_v2"
        STANDARD_A3 = "Standard_A3"
        STANDARD_A4 = "Standard_A4"
        STANDARD_A4_M_V2 = "Standard_A4m_v2"
        STANDARD_A4_V2 = "Standard_A4_v2"
        STANDARD_A5 = "Standard_A5"
        STANDARD_A6 = "Standard_A6"
        STANDARD_A7 = "Standard_A7"
        STANDARD_A8 = "Standard_A8"
        STANDARD_A8_M_V2 = "Standard_A8m_v2"
        STANDARD_A8_V2 = "Standard_A8_v2"
        STANDARD_A9 = "Standard_A9"
        STANDARD_B1_MS = "Standard_B1ms"
        STANDARD_B1_S = "Standard_B1s"
        STANDARD_B2_MS = "Standard_B2ms"
        STANDARD_B2_S = "Standard_B2s"
        STANDARD_B4_MS = "Standard_B4ms"
        STANDARD_B8_MS = "Standard_B8ms"
        STANDARD_D1 = "Standard_D1"
        STANDARD_D11 = "Standard_D11"
        STANDARD_D11_V2 = "Standard_D11_v2"
        STANDARD_D12 = "Standard_D12"
        STANDARD_D12_V2 = "Standard_D12_v2"
        STANDARD_D13 = "Standard_D13"
        STANDARD_D13_V2 = "Standard_D13_v2"
        STANDARD_D14 = "Standard_D14"
        STANDARD_D14_V2 = "Standard_D14_v2"
        STANDARD_D15_V2 = "Standard_D15_v2"
        STANDARD_D16_S_V3 = "Standard_D16s_v3"
        STANDARD_D16_V3 = "Standard_D16_v3"
        STANDARD_D1_V2 = "Standard_D1_v2"
        STANDARD_D2 = "Standard_D2"
        STANDARD_D2_S_V3 = "Standard_D2s_v3"
        STANDARD_D2_V2 = "Standard_D2_v2"
        STANDARD_D2_V3 = "Standard_D2_v3"
        STANDARD_D3 = "Standard_D3"
        STANDARD_D32_S_V3 = "Standard_D32s_v3"
        STANDARD_D32_V3 = "Standard_D32_v3"
        STANDARD_D3_V2 = "Standard_D3_v2"
        STANDARD_D4 = "Standard_D4"
        STANDARD_D4_S_V3 = "Standard_D4s_v3"
        STANDARD_D4_V2 = "Standard_D4_v2"
        STANDARD_D4_V3 = "Standard_D4_v3"
        STANDARD_D5_V2 = "Standard_D5_v2"
        STANDARD_D64_S_V3 = "Standard_D64s_v3"
        STANDARD_D64_V3 = "Standard_D64_v3"
        STANDARD_D8_S_V3 = "Standard_D8s_v3"
        STANDARD_D8_V3 = "Standard_D8_v3"
        STANDARD_DS1 = "Standard_DS1"
        STANDARD_DS11 = "Standard_DS11"
        STANDARD_DS11_V2 = "Standard_DS11_v2"
        STANDARD_DS12 = "Standard_DS12"
        STANDARD_DS12_V2 = "Standard_DS12_v2"
        STANDARD_DS13 = "Standard_DS13"
        STANDARD_DS13_2_V2 = "Standard_DS13-2_v2"
        STANDARD_DS13_4_V2 = "Standard_DS13-4_v2"
        STANDARD_DS13_V2 = "Standard_DS13_v2"
        STANDARD_DS14 = "Standard_DS14"
        STANDARD_DS14_4_V2 = "Standard_DS14-4_v2"
        STANDARD_DS14_8_V2 = "Standard_DS14-8_v2"
        STANDARD_DS14_V2 = "Standard_DS14_v2"
        STANDARD_DS15_V2 = "Standard_DS15_v2"
        STANDARD_DS1_V2 = "Standard_DS1_v2"
        STANDARD_DS2 = "Standard_DS2"
        STANDARD_DS2_V2 = "Standard_DS2_v2"
        STANDARD_DS3 = "Standard_DS3"
        STANDARD_DS3_V2 = "Standard_DS3_v2"
        STANDARD_DS4 = "Standard_DS4"
        STANDARD_DS4_V2 = "Standard_DS4_v2"
        STANDARD_DS5_V2 = "Standard_DS5_v2"
        STANDARD_E16_S_V3 = "Standard_E16s_v3"
        STANDARD_E16_V3 = "Standard_E16_v3"
        STANDARD_E2_S_V3 = "Standard_E2s_v3"
        STANDARD_E2_V3 = "Standard_E2_v3"
        STANDARD_E32_16_V3 = "Standard_E32-16_v3"
        STANDARD_E32_8_S_V3 = "Standard_E32-8s_v3"
        STANDARD_E32_S_V3 = "Standard_E32s_v3"
        STANDARD_E32_V3 = "Standard_E32_v3"
        STANDARD_E4_S_V3 = "Standard_E4s_v3"
        STANDARD_E4_V3 = "Standard_E4_v3"
        STANDARD_E64_16_S_V3 = "Standard_E64-16s_v3"
        STANDARD_E64_32_S_V3 = "Standard_E64-32s_v3"
        STANDARD_E64_S_V3 = "Standard_E64s_v3"
        STANDARD_E64_V3 = "Standard_E64_v3"
        STANDARD_E8_S_V3 = "Standard_E8s_v3"
        STANDARD_E8_V3 = "Standard_E8_v3"
        STANDARD_F1 = "Standard_F1"
        STANDARD_F16 = "Standard_F16"
        STANDARD_F16_S = "Standard_F16s"
        STANDARD_F16_S_V2 = "Standard_F16s_v2"
        STANDARD_F1_S = "Standard_F1s"
        STANDARD_F2 = "Standard_F2"
        STANDARD_F2_S = "Standard_F2s"
        STANDARD_F2_S_V2 = "Standard_F2s_v2"
        STANDARD_F32_S_V2 = "Standard_F32s_v2"
        STANDARD_F4 = "Standard_F4"
        STANDARD_F4_S = "Standard_F4s"
        STANDARD_F4_S_V2 = "Standard_F4s_v2"
        STANDARD_F64_S_V2 = "Standard_F64s_v2"
        STANDARD_F72_S_V2 = "Standard_F72s_v2"
        STANDARD_F8 = "Standard_F8"
        STANDARD_F8_S = "Standard_F8s"
        STANDARD_F8_S_V2 = "Standard_F8s_v2"
        STANDARD_G1 = "Standard_G1"
        STANDARD_G2 = "Standard_G2"
        STANDARD_G3 = "Standard_G3"
        STANDARD_G4 = "Standard_G4"
        STANDARD_G5 = "Standard_G5"
        STANDARD_GS1 = "Standard_GS1"
        STANDARD_GS2 = "Standard_GS2"
        STANDARD_GS3 = "Standard_GS3"
        STANDARD_GS4 = "Standard_GS4"
        STANDARD_GS4_4 = "Standard_GS4-4"
        STANDARD_GS4_8 = "Standard_GS4-8"
        STANDARD_GS5 = "Standard_GS5"
        STANDARD_GS5_16 = "Standard_GS5-16"
        STANDARD_GS5_8 = "Standard_GS5-8"
        STANDARD_H16 = "Standard_H16"
        STANDARD_H16_M = "Standard_H16m"
        STANDARD_H16_MR = "Standard_H16mr"
        STANDARD_H16_R = "Standard_H16r"
        STANDARD_H8 = "Standard_H8"
        STANDARD_H8_M = "Standard_H8m"
        STANDARD_L16_S = "Standard_L16s"
        STANDARD_L32_S = "Standard_L32s"
        STANDARD_L4_S = "Standard_L4s"
        STANDARD_L8_S = "Standard_L8s"
        STANDARD_M128_32_MS = "Standard_M128-32ms"
        STANDARD_M128_64_MS = "Standard_M128-64ms"
        STANDARD_M128_MS = "Standard_M128ms"
        STANDARD_M128_S = "Standard_M128s"
        STANDARD_M64_16_MS = "Standard_M64-16ms"
        STANDARD_M64_32_MS = "Standard_M64-32ms"
        STANDARD_M64_MS = "Standard_M64ms"
        STANDARD_M64_S = "Standard_M64s"
        STANDARD_NC12 = "Standard_NC12"
        STANDARD_NC12_S_V2 = "Standard_NC12s_v2"
        STANDARD_NC12_S_V3 = "Standard_NC12s_v3"
        STANDARD_NC24 = "Standard_NC24"
        STANDARD_NC24_R = "Standard_NC24r"
        STANDARD_NC24_RS_V2 = "Standard_NC24rs_v2"
        STANDARD_NC24_RS_V3 = "Standard_NC24rs_v3"
        STANDARD_NC24_S_V2 = "Standard_NC24s_v2"
        STANDARD_NC24_S_V3 = "Standard_NC24s_v3"
        STANDARD_NC6 = "Standard_NC6"
        STANDARD_NC6_S_V2 = "Standard_NC6s_v2"
        STANDARD_NC6_S_V3 = "Standard_NC6s_v3"
        STANDARD_ND12_S = "Standard_ND12s"
        STANDARD_ND24_RS = "Standard_ND24rs"
        STANDARD_ND24_S = "Standard_ND24s"
        STANDARD_ND6_S = "Standard_ND6s"
        STANDARD_NV12 = "Standard_NV12"
        STANDARD_NV24 = "Standard_NV24"
        STANDARD_NV6 = "Standard_NV6"


    class azure.mgmt.compute.models.VirtualMachineSoftwarePatchProperties(_Model):
        activity_id: Optional[str]
        assessment_state: Optional[Union[str, PatchAssessmentState]]
        classifications: Optional[list[str]]
        kb_id: Optional[str]
        last_modified_date_time: Optional[datetime]
        name: Optional[str]
        patch_id: Optional[str]
        published_date: Optional[datetime]
        reboot_behavior: Optional[Union[str, VMGuestPatchRebootBehavior]]
        version: Optional[str]


    class azure.mgmt.compute.models.VirtualMachineStatusCodeCount(_Model):
        code: Optional[str]
        count: Optional[int]


    class azure.mgmt.compute.models.VirtualMachineUpdate(UpdateResource):
        identity: Optional[VirtualMachineIdentity]
        plan: Optional[Plan]
        properties: Optional[VirtualMachineProperties]
        tags: dict[str, str]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[VirtualMachineIdentity] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[VirtualMachineProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.compute.models.VmDiskTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        UNMANAGED = "Unmanaged"


    class azure.mgmt.compute.models.VmImagesInEdgeZoneListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[VirtualMachineImageResource]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[VirtualMachineImageResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.WinRMConfiguration(_Model):
        listeners: Optional[list[WinRMListener]]

        @overload
        def __init__(
                self, 
                *, 
                listeners: Optional[list[WinRMListener]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.WinRMListener(_Model):
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


    class azure.mgmt.compute.models.WindowsConfiguration(_Model):
        additional_unattend_content: Optional[list[AdditionalUnattendContent]]
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
                additional_unattend_content: Optional[list[AdditionalUnattendContent]] = ..., 
                enable_automatic_updates: Optional[bool] = ..., 
                patch_settings: Optional[PatchSettings] = ..., 
                provision_vm_agent: Optional[bool] = ..., 
                time_zone: Optional[str] = ..., 
                win_rm: Optional[WinRMConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.WindowsParameters(_Model):
        classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationWindows]]]
        exclude_kbs_requiring_reboot: Optional[bool]
        kb_numbers_to_exclude: Optional[list[str]]
        kb_numbers_to_include: Optional[list[str]]
        max_patch_publish_date: Optional[datetime]
        patch_name_masks_to_exclude: Optional[list[str]]
        patch_name_masks_to_include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                classifications_to_include: Optional[list[Union[str, VMGuestPatchClassificationWindows]]] = ..., 
                exclude_kbs_requiring_reboot: Optional[bool] = ..., 
                kb_numbers_to_exclude: Optional[list[str]] = ..., 
                kb_numbers_to_include: Optional[list[str]] = ..., 
                max_patch_publish_date: Optional[datetime] = ..., 
                patch_name_masks_to_exclude: Optional[list[str]] = ..., 
                patch_name_masks_to_include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.WindowsPatchAssessmentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        IMAGE_DEFAULT = "ImageDefault"


    class azure.mgmt.compute.models.WindowsVMGuestPatchAutomaticByPlatformRebootSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "Always"
        IF_REQUIRED = "IfRequired"
        NEVER = "Never"
        UNKNOWN = "Unknown"


    class azure.mgmt.compute.models.WindowsVMGuestPatchAutomaticByPlatformSettings(_Model):
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


    class azure.mgmt.compute.models.WindowsVMGuestPatchMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC_BY_OS = "AutomaticByOS"
        AUTOMATIC_BY_PLATFORM = "AutomaticByPlatform"
        MANUAL = "Manual"


    class azure.mgmt.compute.models.ZonalPlatformFaultDomainAlignMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALIGNED = "Aligned"
        BEST_EFFORT_ALIGNED = "BestEffortAligned"
        UNALIGNED = "Unaligned"


    class azure.mgmt.compute.models.ZoneAllocationPolicy(_Model):
        max_instance_percent_per_zone_policy: Optional[MaxInstancePercentPerZonePolicy]
        max_zone_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_instance_percent_per_zone_policy: Optional[MaxInstancePercentPerZonePolicy] = ..., 
                max_zone_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ZoneMovement(_Model):
        is_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.compute.models.ZonePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        AUTO = "Auto"


namespace azure.mgmt.compute.operations

    class azure.mgmt.compute.operations.AvailabilitySetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[ConvertToVirtualMachineScaleSetInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_convert_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def cancel_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: AvailabilitySet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvailabilitySet]: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineSize]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailabilitySet]: ...

        @overload
        def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: MigrateToVirtualMachineScaleSetInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def start_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: AvailabilitySetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AvailabilitySet: ...

        @overload
        def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: MigrateToVirtualMachineScaleSetInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def validate_migration_to_virtual_machine_scale_set(
                self, 
                resource_group_name: str, 
                availability_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.compute.operations.CapacityReservationGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: CapacityReservationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                *, 
                expand: Optional[Union[str, CapacityReservationGroupInstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CapacityReservationGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                resource_ids_only: Optional[Union[str, ResourceIdOptionsForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CapacityReservationGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: CapacityReservationGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapacityReservationGroup: ...


    class azure.mgmt.compute.operations.CapacityReservationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: CapacityReservation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: CapacityReservationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityReservation]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                capacity_reservation_name: str, 
                *, 
                expand: Optional[Union[str, CapacityReservationInstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> CapacityReservation: ...

        @distributed_trace
        def list_by_capacity_reservation_group(
                self, 
                resource_group_name: str, 
                capacity_reservation_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetCapacityReservationGroups]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CapacityReservation]: ...


    class azure.mgmt.compute.operations.CommunityGalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                **kwargs: Any
            ) -> CommunityGallery: ...


    class azure.mgmt.compute.operations.CommunityGalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> CommunityGalleryImageVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunityGalleryImageVersion]: ...


    class azure.mgmt.compute.operations.CommunityGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                public_gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> CommunityGalleryImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                public_gallery_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommunityGalleryImage]: ...


    class azure.mgmt.compute.operations.DedicatedHostGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: DedicatedHostGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHostGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DedicatedHostGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: DedicatedHostGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DedicatedHostGroup: ...


    class azure.mgmt.compute.operations.DedicatedHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: DedicatedHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: DedicatedHostUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DedicatedHost]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> DedicatedHost: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                host_name: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_by_host_group(
                self, 
                resource_group_name: str, 
                host_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DedicatedHost]: ...


    class azure.mgmt.compute.operations.DiskAccessesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: DiskAccess, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: DiskAccessUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                disk_access: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskAccess]: ...

        @overload
        def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_update_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> DiskAccess: ...

        @distributed_trace
        def get_a_private_endpoint_connection(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def get_private_link_resources(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DiskAccess]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DiskAccess]: ...

        @distributed_trace
        def list_private_endpoint_connections(
                self, 
                resource_group_name: str, 
                disk_access_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.compute.operations.DiskEncryptionSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: DiskEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: DiskEncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                disk_encryption_set: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiskEncryptionSet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> DiskEncryptionSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DiskEncryptionSet]: ...

        @distributed_trace
        def list_associated_resources(
                self, 
                resource_group_name: str, 
                disk_encryption_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DiskEncryptionSet]: ...


    class azure.mgmt.compute.operations.DiskRestorePointOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @distributed_trace
        def begin_revoke_access(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                disk_restore_point_name: str, 
                **kwargs: Any
            ) -> DiskRestorePoint: ...

        @distributed_trace
        def list_by_restore_point(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                vm_restore_point_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DiskRestorePoint]: ...


    class azure.mgmt.compute.operations.DisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: Disk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @distributed_trace
        def begin_revoke_access(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: DiskUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                disk: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Disk]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> Disk: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Disk]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Disk]: ...


    class azure.mgmt.compute.operations.GalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: Gallery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: GalleryUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                *, 
                expand: Optional[Union[str, GalleryExpandParams]] = ..., 
                select: Optional[Union[str, SelectPermissions]] = ..., 
                **kwargs: Any
            ) -> Gallery: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Gallery]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Gallery]: ...


    class azure.mgmt.compute.operations.GalleryApplicationVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: GalleryApplicationVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: GalleryApplicationVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                gallery_application_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplicationVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application_version_name: str, 
                *, 
                expand: Optional[Union[str, ReplicationStatusTypes]] = ..., 
                **kwargs: Any
            ) -> GalleryApplicationVersion: ...

        @distributed_trace
        def list_by_gallery_application(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryApplicationVersion]: ...


    class azure.mgmt.compute.operations.GalleryApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: GalleryApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: GalleryApplicationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                gallery_application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryApplication]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_application_name: str, 
                **kwargs: Any
            ) -> GalleryApplication: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryApplication]: ...


    class azure.mgmt.compute.operations.GalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: GalleryImageVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: GalleryImageVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                gallery_image_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImageVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                *, 
                expand: Optional[Union[str, ReplicationStatusTypes]] = ..., 
                **kwargs: Any
            ) -> GalleryImageVersion: ...

        @distributed_trace
        def list_by_gallery_image(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryImageVersion]: ...


    class azure.mgmt.compute.operations.GalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: GalleryImage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: GalleryImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                gallery_image: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryImage]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> GalleryImage: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryImage]: ...


    class azure.mgmt.compute.operations.GalleryInVMAccessControlProfileVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: GalleryInVMAccessControlProfileVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: GalleryInVMAccessControlProfileVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                gallery_in_vm_access_control_profile_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfileVersion]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                in_vm_access_control_profile_version_name: str, 
                **kwargs: Any
            ) -> GalleryInVMAccessControlProfileVersion: ...

        @distributed_trace
        def list_by_gallery_in_vm_access_control_profile(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryInVMAccessControlProfileVersion]: ...


    class azure.mgmt.compute.operations.GalleryInVMAccessControlProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: GalleryInVMAccessControlProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: GalleryInVMAccessControlProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                gallery_in_vm_access_control_profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryInVMAccessControlProfile]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                in_vm_access_control_profile_name: str, 
                **kwargs: Any
            ) -> GalleryInVMAccessControlProfile: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryInVMAccessControlProfile]: ...


    class azure.mgmt.compute.operations.GalleryScriptVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: GalleryScriptVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'gallery_script_version_name']}, api_versions_list=['2025-03-03'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: GalleryScriptVersionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                gallery_script_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScriptVersion]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'gallery_script_version_name', 'accept']}, api_versions_list=['2025-03-03'])
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script_version_name: str, 
                **kwargs: Any
            ) -> GalleryScriptVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'accept']}, api_versions_list=['2025-03-03'])
        def list_by_gallery_script(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryScriptVersion]: ...


    class azure.mgmt.compute.operations.GalleryScriptsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: GalleryScript, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name']}, api_versions_list=['2025-03-03'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: GalleryScriptUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                gallery_script: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GalleryScript]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'gallery_script_name', 'accept']}, api_versions_list=['2025-03-03'])
        def get(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                gallery_script_name: str, 
                **kwargs: Any
            ) -> GalleryScript: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-03-03', params_added_on={'2025-03-03': ['api_version', 'subscription_id', 'resource_group_name', 'gallery_name', 'accept']}, api_versions_list=['2025-03-03'])
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GalleryScript]: ...


    class azure.mgmt.compute.operations.GallerySharingProfileOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: SharingUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharingUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharingUpdate]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                sharing_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharingUpdate]: ...


    class azure.mgmt.compute.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: Image, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: ImageUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                image_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Image]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                image_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Image]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...


    class azure.mgmt.compute.operations.LogAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: RequestRateByIntervalInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...

        @overload
        def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...

        @overload
        def begin_export_request_rate_by_interval(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...

        @overload
        def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: ThrottledRequestsInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...

        @overload
        def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...

        @overload
        def begin_export_throttled_requests(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogAnalyticsOperationResult]: ...


    class azure.mgmt.compute.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.compute.operations.ProximityPlacementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: ProximityPlacementGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                *, 
                include_colocation_status: Optional[str] = ..., 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProximityPlacementGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ProximityPlacementGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: ProximityPlacementGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                proximity_placement_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProximityPlacementGroup: ...


    class azure.mgmt.compute.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                include_extended_locations: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.compute.operations.RestorePointCollectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: RestorePointCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                *, 
                expand: Optional[Union[str, RestorePointCollectionExpandOptions]] = ..., 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RestorePointCollection]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[RestorePointCollection]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: RestorePointCollectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestorePointCollection: ...


    class azure.mgmt.compute.operations.RestorePointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: RestorePoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestorePoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestorePoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RestorePoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                restore_point_collection_name: str, 
                restore_point_name: str, 
                *, 
                expand: Optional[Union[str, RestorePointExpandOptions]] = ..., 
                **kwargs: Any
            ) -> RestorePoint: ...


    class azure.mgmt.compute.operations.SharedGalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                **kwargs: Any
            ) -> SharedGallery: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SharedGallery]: ...


    class azure.mgmt.compute.operations.SharedGalleryImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                gallery_image_version_name: str, 
                **kwargs: Any
            ) -> SharedGalleryImageVersion: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SharedGalleryImageVersion]: ...


    class azure.mgmt.compute.operations.SharedGalleryImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                gallery_unique_name: str, 
                gallery_image_name: str, 
                **kwargs: Any
            ) -> SharedGalleryImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                gallery_unique_name: str, 
                *, 
                shared_to: Optional[Union[str, SharedToValues]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SharedGalleryImage]: ...


    class azure.mgmt.compute.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: GrantAccessData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @overload
        def begin_grant_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                grant_access_data: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AccessUri]: ...

        @distributed_trace
        def begin_revoke_access(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: SnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                snapshot: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Snapshot]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Snapshot]: ...


    class azure.mgmt.compute.operations.SoftDeletedResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_artifact_name(
                self, 
                resource_group_name: str, 
                gallery_name: str, 
                artifact_type: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GallerySoftDeletedResource]: ...


    class azure.mgmt.compute.operations.SshPublicKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: SshPublicKeyResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[SshGenerateKeyPairInputParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @overload
        def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @overload
        def generate_key_pair(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyGenerateKeyPairResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SshPublicKeyResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SshPublicKeyResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: SshPublicKeyUpdateResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ssh_public_key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SshPublicKeyResource: ...


    class azure.mgmt.compute.operations.UsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.compute.operations.VirtualMachineExtensionImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                publisher_name: str, 
                type: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineExtensionImage: ...

        @distributed_trace
        def list_types(
                self, 
                location: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineExtensionImage]: ...

        @distributed_trace
        def list_versions(
                self, 
                location: str, 
                publisher_name: str, 
                type: str, 
                *, 
                filter: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineExtensionImage]: ...


    class azure.mgmt.compute.operations.VirtualMachineExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineExtension]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                vm_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineExtensionsListResult: ...


    class azure.mgmt.compute.operations.VirtualMachineImagesEdgeZoneOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_offers(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_publishers(
                self, 
                location: str, 
                edge_zone: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_skus(
                self, 
                location: str, 
                edge_zone: str, 
                publisher_name: str, 
                offer: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...


    class azure.mgmt.compute.operations.VirtualMachineImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                version: str, 
                **kwargs: Any
            ) -> VirtualMachineImage: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: Optional[str] = ..., 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_by_edge_zone(
                self, 
                location: str, 
                edge_zone: str, 
                **kwargs: Any
            ) -> VmImagesInEdgeZoneListResult: ...

        @distributed_trace
        def list_offers(
                self, 
                location: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_publishers(
                self, 
                location: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_skus(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                **kwargs: Any
            ) -> List[VirtualMachineImageResource]: ...

        @distributed_trace
        def list_with_properties(
                self, 
                location: str, 
                publisher_name: str, 
                offer: str, 
                skus: str, 
                *, 
                expand: str, 
                orderby: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[VirtualMachineImage]: ...


    class azure.mgmt.compute.operations.VirtualMachineRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommandUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                command_id: str, 
                **kwargs: Any
            ) -> RunCommandDocument: ...

        @distributed_trace
        def get_by_virtual_machine(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                run_command_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[RunCommandDocumentBase]: ...

        @distributed_trace
        def list_by_virtual_machine(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineRunCommand]: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetExtension]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vmss_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSetExtension]: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetLifeCycleHookEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VMScaleSetLifecycleHookEvent]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: VMScaleSetLifecycleHookEventUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                lifecycle_hook_event_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VMScaleSetLifecycleHookEvent: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetRollingUpgradesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_extension_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start_os_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_latest(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> RollingUpgradeStatusInfo: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetVMExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetVMExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: VirtualMachineScaleSetVMExtensionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                extension_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVMExtension]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_extension_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMExtension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMExtensionsListResult: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetVMRunCommandsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommand, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: VirtualMachineRunCommandUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                run_command: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineRunCommand]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                run_command_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> VirtualMachineRunCommand: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineRunCommand]: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetVMsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: AttachDetachDataDisksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @distributed_trace
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[VirtualMachineScaleSetVMReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                vm_scale_set_vm_reimage_input: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: RunCommandInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: VirtualMachineScaleSetVM, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVM]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVM]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSetVM]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVM: ...

        @distributed_trace
        def get_instance_view(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> VirtualMachineScaleSetVMInstanceView: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                virtual_machine_scale_set_name: str, 
                *, 
                expand: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                select: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSetVM]: ...

        @distributed_trace
        def retrieve_boot_diagnostics_data(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                *, 
                sas_uri_expiration_time_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> RetrieveBootDiagnosticsDataResult: ...

        @distributed_trace
        def simulate_eviction(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                instance_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.compute.operations.VirtualMachineScaleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_approve_rolling_upgrade(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VirtualMachineScaleSet, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: VirtualMachineScaleSetVMInstanceRequiredIDs, 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: JSON, 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reapply(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[VirtualMachineScaleSetReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_scale_set_reimage_input: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage_all(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restart(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VMScaleSetScaleOutInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_scale_out(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: OrchestrationServiceStateInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_set_orchestration_service_state(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[VirtualMachineScaleSetVMInstanceIDs] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VirtualMachineScaleSetUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineScaleSet]: ...

        @overload
        def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: VirtualMachineScaleSetVMInstanceRequiredIDs, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_instances(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                vm_instance_i_ds: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: VMScaleSetConvertToSinglePlacementGroupInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def convert_to_single_placement_group(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def force_recovery_service_fabric_platform_update_domain_walk(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                placement_group_id: Optional[str] = ..., 
                platform_update_domain: int, 
                zone: Optional[str] = ..., 
                **kwargs: Any
            ) -> RecoveryWalkResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypesForGetVMScaleSets]] = ..., 
                **kwargs: Any
            ) -> VirtualMachineScaleSet: ...

        @distributed_trace
        def get_instance_view(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> VirtualMachineScaleSetInstanceView: ...

        @distributed_trace
        def get_os_upgrade_history(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UpgradeOperationHistoricalStatusInfo]: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_all(self, **kwargs: Any) -> ItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSet]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                vm_scale_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineScaleSetSku]: ...


    class azure.mgmt.compute.operations.VirtualMachineSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineSize]: ...


    class azure.mgmt.compute.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_assess_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineAssessPatchesResult]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: AttachDetachDataDisksRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @overload
        def begin_attach_detach_data_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageProfile]: ...

        @overload
        def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachineCaptureParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineCaptureResult]: ...

        @overload
        def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineCaptureResult]: ...

        @overload
        def begin_capture(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineCaptureResult]: ...

        @distributed_trace
        def begin_convert_to_managed_disks(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachine, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        @api_version_validation(params_added_on={'2025-11-01': ['force_deallocate']}, api_versions_list=['2024-11-01', '2025-04-01', '2025-11-01'])
        def begin_deallocate(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                force_deallocate: Optional[bool] = ..., 
                hibernate: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                force_deletion: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: VirtualMachineInstallPatchesParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        def begin_install_patches(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                install_patches_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VirtualMachineInstallPatchesResult]: ...

        @overload
        def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[MigrateVMToVirtualMachineScaleSetInput] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_to_vm_scale_set(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_perform_maintenance(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_power_off(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                skip_shutdown: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reapply(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_redeploy(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[VirtualMachineReimageParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reimage(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: RunCommandInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @overload
        def begin_run_command(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RunCommandResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: VirtualMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[VirtualMachine]: ...

        @distributed_trace
        def generalize(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                expand: Optional[Union[str, InstanceViewTypes]] = ..., 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def instance_view(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> VirtualMachineInstanceView: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                *, 
                expand: Optional[Union[str, ExpandTypeForListVMs]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_all(
                self, 
                *, 
                expand: Optional[Union[str, ExpandTypesForListVMs]] = ..., 
                filter: Optional[str] = ..., 
                status_only: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...

        @distributed_trace
        def list_available_sizes(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachineSize]: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...

        @distributed_trace
        def retrieve_boot_diagnostics_data(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                *, 
                sas_uri_expiration_time_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> RetrieveBootDiagnosticsDataResult: ...

        @distributed_trace
        def simulate_eviction(
                self, 
                resource_group_name: str, 
                vm_name: str, 
                **kwargs: Any
            ) -> None: ...


```