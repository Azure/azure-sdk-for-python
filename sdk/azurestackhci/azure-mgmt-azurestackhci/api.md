```py
namespace azure.mgmt.azurestackhci

    class azure.mgmt.azurestackhci.AzureStackHCIClient: implements ContextManager 
        arc_settings: ArcSettingsOperations
        cluster_jobs: ClusterJobsOperations
        clusters: ClustersOperations
        deployment_settings: DeploymentSettingsOperations
        device_pools: DevicePoolsOperations
        edge_device_jobs: EdgeDeviceJobsOperations
        edge_devices: EdgeDevicesOperations
        edge_machine_disk_jobs: EdgeMachineDiskJobsOperations
        edge_machine_disk_privileged_jobs: EdgeMachineDiskPrivilegedJobsOperations
        edge_machine_disks: EdgeMachineDisksOperations
        edge_machine_gpu_jobs: EdgeMachineGpuJobsOperations
        edge_machine_gpus: EdgeMachineGpusOperations
        edge_machine_jobs: EdgeMachineJobsOperations
        edge_machine_network_adapter_jobs: EdgeMachineNetworkAdapterJobsOperations
        edge_machine_network_adapters: EdgeMachineNetworkAdaptersOperations
        edge_machine_updates: EdgeMachineUpdatesOperations
        edge_machine_volumes: EdgeMachineVolumesOperations
        edge_machines: EdgeMachinesOperations
        extensions: ExtensionsOperations
        kubernetes_versions: KubernetesVersionsOperations
        offers: OffersOperations
        operations: Operations
        os_images: OsImagesOperations
        ownership_vouchers: OwnershipVouchersOperations
        platform_updates: PlatformUpdatesOperations
        publishers: PublishersOperations
        security_settings: SecuritySettingsOperations
        skus: SkusOperations
        update_contents: UpdateContentsOperations
        update_runs: UpdateRunsOperations
        update_summaries: UpdateSummariesOperations
        update_summaries_operation_group: UpdateSummariesOperationGroupOperations
        updates: UpdatesOperations
        validated_solution_recipes: ValidatedSolutionRecipesOperations

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


namespace azure.mgmt.azurestackhci.aio

    class azure.mgmt.azurestackhci.aio.AzureStackHCIClient: implements AsyncContextManager 
        arc_settings: ArcSettingsOperations
        cluster_jobs: ClusterJobsOperations
        clusters: ClustersOperations
        deployment_settings: DeploymentSettingsOperations
        device_pools: DevicePoolsOperations
        edge_device_jobs: EdgeDeviceJobsOperations
        edge_devices: EdgeDevicesOperations
        edge_machine_disk_jobs: EdgeMachineDiskJobsOperations
        edge_machine_disk_privileged_jobs: EdgeMachineDiskPrivilegedJobsOperations
        edge_machine_disks: EdgeMachineDisksOperations
        edge_machine_gpu_jobs: EdgeMachineGpuJobsOperations
        edge_machine_gpus: EdgeMachineGpusOperations
        edge_machine_jobs: EdgeMachineJobsOperations
        edge_machine_network_adapter_jobs: EdgeMachineNetworkAdapterJobsOperations
        edge_machine_network_adapters: EdgeMachineNetworkAdaptersOperations
        edge_machine_updates: EdgeMachineUpdatesOperations
        edge_machine_volumes: EdgeMachineVolumesOperations
        edge_machines: EdgeMachinesOperations
        extensions: ExtensionsOperations
        kubernetes_versions: KubernetesVersionsOperations
        offers: OffersOperations
        operations: Operations
        os_images: OsImagesOperations
        ownership_vouchers: OwnershipVouchersOperations
        platform_updates: PlatformUpdatesOperations
        publishers: PublishersOperations
        security_settings: SecuritySettingsOperations
        skus: SkusOperations
        update_contents: UpdateContentsOperations
        update_runs: UpdateRunsOperations
        update_summaries: UpdateSummariesOperations
        update_summaries_operation_group: UpdateSummariesOperationGroupOperations
        updates: UpdatesOperations
        validated_solution_recipes: ValidatedSolutionRecipesOperations

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


namespace azure.mgmt.azurestackhci.aio.operations

    class azure.mgmt.azurestackhci.aio.operations.ArcSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcIdentityResponse]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_initialize_disable_process(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: ReconcileArcSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcSetting]: ...

        @overload
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: ReconcileArcSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcSetting]: ...

        @overload
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcSetting]: ...

        @distributed_trace_async
        async def consent_and_install_default_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @distributed_trace_async
        async def generate_password(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> PasswordCredential: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> ArcSetting: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ArcSetting]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSettingsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSettingsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...


    class azure.mgmt.azurestackhci.aio.operations.ClusterJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: ClusterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: ClusterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> ClusterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ClusterJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: ChangeRingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: ChangeRingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: RemoteSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: RemoteSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_create_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterIdentityResponse]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: SoftwareAssuranceChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: SoftwareAssuranceChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: LogCollectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: LogCollectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: SecretsLocationsChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: SecretsLocationsChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...


    class azure.mgmt.azurestackhci.aio.operations.DeploymentSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: DeploymentSetting, 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: DeploymentSetting, 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DeploymentSetting]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                deployment_settings_name: str = "default", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                deployment_settings_name: str = "default", 
                **kwargs: Any
            ) -> DeploymentSetting: ...

        @distributed_trace
        def list_by_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeploymentSetting]: ...


    class azure.mgmt.azurestackhci.aio.operations.DevicePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ClaimDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ClaimDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: DevicePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: DevicePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ReleaseDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ReleaseDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: DevicePoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: DevicePoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevicePool]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> DevicePool: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DevicePool]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeDeviceJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: EdgeDeviceJob, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDeviceJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: EdgeDeviceJob, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDeviceJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDeviceJob]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> EdgeDeviceJob: ...

        @distributed_trace
        def list_by_edge_device(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeDeviceJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: EdgeDevice, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDevice]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: EdgeDevice, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDevice]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeDevice]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: ValidateRequest, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateResponse]: ...

        @overload
        async def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: ValidateRequest, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateResponse]: ...

        @overload
        async def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ValidateResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> EdgeDevice: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeDevice]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineDiskJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: EdgeMachineDiskJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: EdgeMachineDiskJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'job_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDiskJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineDiskJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineDiskPrivilegedJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: EdgeMachineDiskPrivilegedJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: EdgeMachineDiskPrivilegedJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'privileged_job_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'privileged_job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDiskPrivilegedJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineDiskPrivilegedJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineDisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: EdgeMachineDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDisk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: EdgeMachineDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDisk]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineDisk]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDisk: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineDisk]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineGpuJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: EdgeMachineGpuJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpuJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: EdgeMachineGpuJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpuJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpuJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineGpuJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineGpuJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineGpusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: EdgeMachineGpu, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpu]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: EdgeMachineGpu, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpu]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineGpu]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> EdgeMachineGpu: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineGpu]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: EdgeMachineJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: EdgeMachineJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineNetworkAdapterJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: EdgeMachineNetworkAdapterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineNetworkAdapterJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: EdgeMachineNetworkAdapterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineNetworkAdapterJob]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineNetworkAdapterJob]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'job_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineNetworkAdapterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineNetworkAdapterJob]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineNetworkAdaptersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                **kwargs: Any
            ) -> EdgeMachineNetworkAdapter: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineNetworkAdapter]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: EdgeMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineUpdate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: EdgeMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineUpdate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineUpdate]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'default']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'default', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                **kwargs: Any
            ) -> EdgeMachineUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineUpdate]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachineVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: EdgeMachineVolume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineVolume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: EdgeMachineVolume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineVolume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineVolume]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'volume_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'volume_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> EdgeMachineVolume: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineVolume]: ...


    class azure.mgmt.azurestackhci.aio.operations.EdgeMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: EdgeMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: EdgeMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name']}, api_versions_list=['2026-05-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: EdgeMachinePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: EdgeMachinePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachine]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: EdgeMachineValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineValidateResponse]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: EdgeMachineValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineValidateResponse]: ...

        @overload
        async def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EdgeMachineValidateResponse]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> EdgeMachine: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachine]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EdgeMachine]: ...


    class azure.mgmt.azurestackhci.aio.operations.ExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: ExtensionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: ExtensionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: ExtensionUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: ExtensionUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> Extension: ...

        @distributed_trace
        def list_by_arc_setting(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Extension]: ...


    class azure.mgmt.azurestackhci.aio.operations.KubernetesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[KubernetesVersion]: ...


    class azure.mgmt.azurestackhci.aio.operations.OffersOperations:

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
                publisher_name: str, 
                offer_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Offer]: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Offer]: ...


    class azure.mgmt.azurestackhci.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.azurestackhci.aio.operations.OsImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'os_image_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                location: str, 
                os_image_name: str, 
                **kwargs: Any
            ) -> OsImage: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OsImage]: ...


    class azure.mgmt.azurestackhci.aio.operations.OwnershipVouchersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidateOwnershipVouchersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidateOwnershipVouchersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...

        @overload
        async def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...


    class azure.mgmt.azurestackhci.aio.operations.PlatformUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'platform_update_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                location: str, 
                platform_update_name: str, 
                **kwargs: Any
            ) -> PlatformUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlatformUpdate]: ...


    class azure.mgmt.azurestackhci.aio.operations.PublishersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'publisher_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Publisher]: ...


    class azure.mgmt.azurestackhci.aio.operations.SecuritySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: SecuritySetting, 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecuritySetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: SecuritySetting, 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecuritySetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecuritySetting]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                security_settings_name: str = "default", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                security_settings_name: str = "default", 
                **kwargs: Any
            ) -> SecuritySetting: ...

        @distributed_trace
        def list_by_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecuritySetting]: ...


    class azure.mgmt.azurestackhci.aio.operations.SkusOperations:

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
                publisher_name: str, 
                offer_name: str, 
                sku_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Sku: ...

        @distributed_trace
        def list_by_offer(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                offer_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Sku]: ...


    class azure.mgmt.azurestackhci.aio.operations.UpdateContentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'update_content_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        async def get(
                self, 
                location: str, 
                update_content_name: str, 
                **kwargs: Any
            ) -> UpdateContent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateContent]: ...


    class azure.mgmt.azurestackhci.aio.operations.UpdateRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> UpdateRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateRun]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...


    class azure.mgmt.azurestackhci.aio.operations.UpdateSummariesOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-30', '2026-05-01-preview'])
        async def begin_check_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CheckUpdatesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CheckUpdatesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.azurestackhci.aio.operations.UpdateSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpdateSummaries]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: UpdateSummaries, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: UpdateSummaries, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...


    class azure.mgmt.azurestackhci.aio.operations.UpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'update_name']}, api_versions_list=['2026-04-30', '2026-05-01-preview'])
        async def begin_prepare(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> Update: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Update]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: Update, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: Update, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...


    class azure.mgmt.azurestackhci.aio.operations.ValidatedSolutionRecipesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                validated_solution_recipe_name: str, 
                **kwargs: Any
            ) -> ValidatedSolutionRecipe: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ValidatedSolutionRecipe]: ...


namespace azure.mgmt.azurestackhci.models

    class azure.mgmt.azurestackhci.models.AccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIAGNOSTICS = "Diagnostics"
        DIAGNOSTICS_AND_REPAIR = "DiagnosticsAndRepair"


    class azure.mgmt.azurestackhci.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.azurestackhci.models.AddServerJobServerDetails(_Model):
        host_ipv4_address: str
        local_availability_zone_name: Optional[str]
        server_name: str
        server_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                host_ipv4_address: str, 
                local_availability_zone_name: Optional[str] = ..., 
                server_name: str, 
                server_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ApplyConfigurationNetworkAdapterJobProperties(EdgeMachineNetworkAdapterJobProperties, discriminator='ApplyConfiguration'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.APPLY_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        target_configuration: NetworkAdapterConfiguration

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                target_configuration: NetworkAdapterConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcConnectivityProperties(_Model):
        enabled: Optional[bool]
        service_configurations: Optional[list[ServiceConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                service_configurations: Optional[list[ServiceConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcExtensionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.ArcIdentityResponse(_Model):
        properties: Optional[ArcIdentityResponseProperties]


    class azure.mgmt.azurestackhci.models.ArcIdentityResponseProperties(_Model):
        arc_application_client_id: Optional[str]
        arc_application_object_id: Optional[str]
        arc_application_tenant_id: Optional[str]
        arc_service_principal_object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                arc_application_client_id: Optional[str] = ..., 
                arc_application_object_id: Optional[str] = ..., 
                arc_application_tenant_id: Optional[str] = ..., 
                arc_service_principal_object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[ArcSettingProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArcSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcSettingAggregateState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONNECTED = "Connected"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DISABLE_IN_PROGRESS = "DisableInProgress"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PARTIALLY_CONNECTED = "PartiallyConnected"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.ArcSettingProperties(_Model):
        aggregate_state: Optional[Union[str, ArcSettingAggregateState]]
        arc_application_client_id: Optional[str]
        arc_application_object_id: Optional[str]
        arc_application_tenant_id: Optional[str]
        arc_instance_resource_group: Optional[str]
        arc_service_principal_object_id: Optional[str]
        connectivity_properties: Optional[ArcConnectivityProperties]
        default_extensions: Optional[list[DefaultExtensionDetails]]
        per_node_details: Optional[list[PerNodeState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                arc_application_client_id: Optional[str] = ..., 
                arc_application_object_id: Optional[str] = ..., 
                arc_application_tenant_id: Optional[str] = ..., 
                arc_instance_resource_group: Optional[str] = ..., 
                arc_service_principal_object_id: Optional[str] = ..., 
                connectivity_properties: Optional[ArcConnectivityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcSettingsPatch(_Model):
        properties: Optional[ArcSettingsPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArcSettingsPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ArcSettingsPatchProperties(_Model):
        connectivity_properties: Optional[ArcConnectivityProperties]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_properties: Optional[ArcConnectivityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.AssemblyInfo(_Model):
        package_version: Optional[str]
        payload: Optional[list[AssemblyInfoPayload]]


    class azure.mgmt.azurestackhci.models.AssemblyInfoPayload(_Model):
        file_name: Optional[str]
        hash: Optional[str]
        identifier: Optional[str]
        url: Optional[str]


    class azure.mgmt.azurestackhci.models.AssignPartitionGpuJobProperties(EdgeMachineGpuJobProperties, discriminator='AssignPartition'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.ASSIGN_PARTITION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        vm_id: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                vm_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN = "Open"
        WPA2_ENTERPRISE = "WPA2-Enterprise"
        WPA2_PERSONAL = "WPA2-Personal"
        WPA3_ENTERPRISE = "WPA3-Enterprise"
        WPA3_PERSONAL = "WPA3-Personal"


    class azure.mgmt.azurestackhci.models.AvailabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"
        NOTIFY = "Notify"
        ONLINE = "Online"


    class azure.mgmt.azurestackhci.models.ChangeRingRequest(_Model):
        properties: ChangeRingRequestProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: ChangeRingRequestProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ChangeRingRequestProperties(_Model):
        target_ring: str

        @overload
        def __init__(
                self, 
                *, 
                target_ring: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.CheckUpdatesRequest(_Model):
        update_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                update_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClaimDeviceRequest(_Model):
        claimed_by: Optional[str]
        devices: list[str]

        @overload
        def __init__(
                self, 
                *, 
                claimed_by: Optional[str] = ..., 
                devices: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.Cluster(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[ClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[ClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterBillingProperties(_Model):
        next_billing_model: Optional[NextBillingModel]

        @overload
        def __init__(
                self, 
                *, 
                next_billing_model: Optional[NextBillingModel] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterDesiredProperties(_Model):
        diagnostic_level: Optional[Union[str, DiagnosticLevel]]
        windows_server_subscription: Optional[Union[str, WindowsServerSubscription]]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_level: Optional[Union[str, DiagnosticLevel]] = ..., 
                windows_server_subscription: Optional[Union[str, WindowsServerSubscription]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterIdentityResponse(_Model):
        properties: Optional[ClusterIdentityResponseProperties]


    class azure.mgmt.azurestackhci.models.ClusterIdentityResponseProperties(_Model):
        aad_application_object_id: Optional[str]
        aad_client_id: Optional[str]
        aad_service_principal_object_id: Optional[str]
        aad_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_application_object_id: Optional[str] = ..., 
                aad_client_id: Optional[str] = ..., 
                aad_service_principal_object_id: Optional[str] = ..., 
                aad_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterJob(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[JobReportedProperties]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterNode(_Model):
        core_count: Optional[float]
        ehc_resource_id: Optional[str]
        id: Optional[float]
        last_licensing_timestamp: Optional[datetime]
        manufacturer: Optional[str]
        memory_in_gi_b: Optional[float]
        model: Optional[str]
        name: Optional[str]
        node_type: Optional[Union[str, ClusterNodeType]]
        oem_activation: Optional[Union[str, OemActivation]]
        os_display_version: Optional[str]
        os_name: Optional[str]
        os_version: Optional[str]
        serial_number: Optional[str]
        windows_server_subscription: Optional[Union[str, WindowsServerSubscription]]


    class azure.mgmt.azurestackhci.models.ClusterNodeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST_PARTY = "FirstParty"
        THIRD_PARTY = "ThirdParty"


    class azure.mgmt.azurestackhci.models.ClusterPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ClusterPatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ClusterPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterPatchProperties(_Model):
        aad_client_id: Optional[str]
        aad_tenant_id: Optional[str]
        cloud_management_endpoint: Optional[str]
        desired_properties: Optional[ClusterDesiredProperties]

        @overload
        def __init__(
                self, 
                *, 
                aad_client_id: Optional[str] = ..., 
                aad_tenant_id: Optional[str] = ..., 
                cloud_management_endpoint: Optional[str] = ..., 
                desired_properties: Optional[ClusterDesiredProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterPattern(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RACK_AWARE = "RackAware"
        STANDARD = "Standard"


    class azure.mgmt.azurestackhci.models.ClusterProperties(_Model):
        aad_application_object_id: Optional[str]
        aad_client_id: Optional[str]
        aad_service_principal_object_id: Optional[str]
        aad_tenant_id: Optional[str]
        billing_model: Optional[str]
        billing_properties: Optional[ClusterBillingProperties]
        cloud_id: Optional[str]
        cloud_management_endpoint: Optional[str]
        cluster_pattern: Optional[Union[str, ClusterPattern]]
        confidential_vm_properties: Optional[ConfidentialVmProperties]
        connectivity_status: Optional[Union[str, ConnectivityStatus]]
        desired_properties: Optional[ClusterDesiredProperties]
        identity_provider: Optional[Union[str, IdentityProvider]]
        is_management_cluster: Optional[bool]
        isolated_vm_attestation_configuration: Optional[IsolatedVmAttestationConfiguration]
        last_billing_timestamp: Optional[datetime]
        last_sync_timestamp: Optional[datetime]
        local_availability_zones: Optional[list[LocalAvailabilityZones]]
        log_collection_properties: Optional[LogCollectionProperties]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        registration_timestamp: Optional[datetime]
        remote_support_properties: Optional[RemoteSupportProperties]
        reported_properties: Optional[ClusterReportedProperties]
        resource_provider_object_id: Optional[str]
        ring: Optional[str]
        sdn_properties: Optional[ClusterSdnProperties]
        secrets_locations: Optional[list[SecretsLocationDetails]]
        service_endpoint: Optional[str]
        software_assurance_properties: Optional[SoftwareAssuranceProperties]
        status: Optional[Union[str, Status]]
        storage_type: Optional[Union[str, StorageType]]
        trial_days_remaining: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                aad_application_object_id: Optional[str] = ..., 
                aad_client_id: Optional[str] = ..., 
                aad_service_principal_object_id: Optional[str] = ..., 
                aad_tenant_id: Optional[str] = ..., 
                cloud_management_endpoint: Optional[str] = ..., 
                desired_properties: Optional[ClusterDesiredProperties] = ..., 
                local_availability_zones: Optional[list[LocalAvailabilityZones]] = ..., 
                log_collection_properties: Optional[LogCollectionProperties] = ..., 
                remote_support_properties: Optional[RemoteSupportProperties] = ..., 
                secrets_locations: Optional[list[SecretsLocationDetails]] = ..., 
                software_assurance_properties: Optional[SoftwareAssuranceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterReportedProperties(_Model):
        cluster_id: Optional[str]
        cluster_name: Optional[str]
        cluster_type: Optional[Union[str, ClusterNodeType]]
        cluster_version: Optional[str]
        diagnostic_level: Optional[Union[str, DiagnosticLevel]]
        hardware_class: Optional[Union[str, HardwareClass]]
        imds_attestation: Optional[Union[str, ImdsAttestation]]
        last_updated: Optional[datetime]
        manufacturer: Optional[str]
        msi_expiration_time_stamp: Optional[datetime]
        nodes: Optional[list[ClusterNode]]
        oem_activation: Optional[Union[str, OemActivation]]
        supported_capabilities: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                diagnostic_level: Optional[Union[str, DiagnosticLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ClusterSdnProperties(_Model):
        sdn_api_address: Optional[str]
        sdn_domain_name: Optional[str]
        sdn_integration_intent: Optional[Union[str, SdnIntegrationIntent]]
        sdn_status: Optional[Union[str, SdnStatus]]


    class azure.mgmt.azurestackhci.models.ComplianceAssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_AND_AUTO_CORRECT = "ApplyAndAutoCorrect"
        AUDIT = "Audit"


    class azure.mgmt.azurestackhci.models.ComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "NonCompliant"
        PENDING = "Pending"


    class azure.mgmt.azurestackhci.models.ConfidentialVmIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.azurestackhci.models.ConfidentialVmProfile(_Model):
        igvm_status: Optional[Union[str, IgvmStatus]]
        status_details: Optional[list[IgvmStatusDetail]]

        @overload
        def __init__(
                self, 
                *, 
                status_details: Optional[list[IgvmStatusDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ConfidentialVmProperties(_Model):
        confidential_vm_intent: Optional[Union[str, ConfidentialVmIntent]]
        confidential_vm_status: Optional[Union[str, ConfidentialVmStatus]]
        confidential_vm_status_summary: Optional[str]


    class azure.mgmt.azurestackhci.models.ConfidentialVmStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PARTIALLY_ENABLED = "PartiallyEnabled"


    class azure.mgmt.azurestackhci.models.ConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTHENTICATION_FAILED = "AuthenticationFailed"
        CONNECTED = "Connected"
        CONNECTING = "Connecting"
        DISCONNECTED = "Disconnected"
        DISCONNECTING = "Disconnecting"
        NOT_CONFIGURED = "NotConfigured"


    class azure.mgmt.azurestackhci.models.ConnectivityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        NOT_CONNECTED_RECENTLY = "NotConnectedRecently"
        NOT_SPECIFIED = "NotSpecified"
        NOT_YET_REGISTERED = "NotYetRegistered"
        PARTIALLY_CONNECTED = "PartiallyConnected"


    class azure.mgmt.azurestackhci.models.ContentPayload(_Model):
        file_name: Optional[str]
        group: Optional[str]
        hash: Optional[str]
        hash_algorithm: Optional[str]
        identifier: Optional[str]
        package_size_in_bytes: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_name: Optional[str] = ..., 
                group: Optional[str] = ..., 
                hash: Optional[str] = ..., 
                hash_algorithm: Optional[str] = ..., 
                identifier: Optional[str] = ..., 
                package_size_in_bytes: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.CreatePartitionGpuJobProperties(EdgeMachineGpuJobProperties, discriminator='CreatePartition'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.CREATE_PARTITION]
        partition_count: int
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                partition_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.CreateVolumeJobProperties(EdgeMachineDiskJobProperties, discriminator='CreateVolume'):
        created_volume_id: Optional[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        file_system: Optional[Union[str, DiskFileSystemType]]
        job_id: str
        job_type: Literal[DiskJobType.CREATE_VOLUME]
        path: str
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        size_in_bytes: str
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                file_system: Optional[Union[str, DiskFileSystemType]] = ..., 
                path: str, 
                size_in_bytes: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurestackhci.models.DdaDetails(_Model):
        dda_pool: Optional[str]
        workload_detail: Optional[WorkloadDetails]


    class azure.mgmt.azurestackhci.models.DefaultExtensionDetails(_Model):
        category: Optional[str]
        consent_time: Optional[datetime]


    class azure.mgmt.azurestackhci.models.DeleteVolumeJobProperties(EdgeMachineDiskPrivilegedJobProperties, discriminator='DeleteVolume'):
        confirm_deletion: Optional[bool]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[PrivilegedJobType.DELETE_VOLUME]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        volume_path: str

        @overload
        def __init__(
                self, 
                *, 
                confirm_deletion: Optional[bool] = ..., 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                volume_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentCluster(_Model):
        azure_service_endpoint: Optional[str]
        cloud_account_name: Optional[str]
        cluster_pattern: Optional[Union[str, ClusterPattern]]
        hardware_class: Optional[Union[str, HardwareClass]]
        name: Optional[str]
        witness_path: Optional[str]
        witness_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_service_endpoint: Optional[str] = ..., 
                cloud_account_name: Optional[str] = ..., 
                cluster_pattern: Optional[Union[str, ClusterPattern]] = ..., 
                name: Optional[str] = ..., 
                witness_path: Optional[str] = ..., 
                witness_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentConfiguration(_Model):
        scale_units: list[ScaleUnits]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                scale_units: list[ScaleUnits], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentData(_Model):
        adou_path: Optional[str]
        assembly_info: Optional[AssemblyInfo]
        cluster: Optional[DeploymentCluster]
        domain_fqdn: Optional[str]
        host_network: Optional[DeploymentSettingHostNetwork]
        identity_provider: Optional[Union[str, IdentityProvider]]
        infrastructure_network: Optional[list[InfrastructureNetwork]]
        is_management_cluster: Optional[bool]
        local_availability_zones: Optional[list[LocalAvailabilityZones]]
        naming_prefix: Optional[str]
        observability: Optional[Observability]
        optional_services: Optional[OptionalServices]
        physical_nodes: Optional[list[PhysicalNodes]]
        sdn_integration: Optional[SdnIntegration]
        secrets: Optional[list[EceDeploymentSecrets]]
        secrets_location: Optional[str]
        security_settings: Optional[DeploymentSecuritySettings]
        storage: Optional[Storage]

        @overload
        def __init__(
                self, 
                *, 
                adou_path: Optional[str] = ..., 
                assembly_info: Optional[AssemblyInfo] = ..., 
                cluster: Optional[DeploymentCluster] = ..., 
                domain_fqdn: Optional[str] = ..., 
                host_network: Optional[DeploymentSettingHostNetwork] = ..., 
                identity_provider: Optional[Union[str, IdentityProvider]] = ..., 
                infrastructure_network: Optional[list[InfrastructureNetwork]] = ..., 
                is_management_cluster: Optional[bool] = ..., 
                local_availability_zones: Optional[list[LocalAvailabilityZones]] = ..., 
                naming_prefix: Optional[str] = ..., 
                observability: Optional[Observability] = ..., 
                optional_services: Optional[OptionalServices] = ..., 
                physical_nodes: Optional[list[PhysicalNodes]] = ..., 
                sdn_integration: Optional[SdnIntegration] = ..., 
                secrets: Optional[list[EceDeploymentSecrets]] = ..., 
                secrets_location: Optional[str] = ..., 
                security_settings: Optional[DeploymentSecuritySettings] = ..., 
                storage: Optional[Storage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOY = "Deploy"
        VALIDATE = "Validate"


    class azure.mgmt.azurestackhci.models.DeploymentSecuritySettings(_Model):
        bitlocker_boot_volume: Optional[bool]
        bitlocker_data_volumes: Optional[bool]
        credential_guard_enforced: Optional[bool]
        drift_control_enforced: Optional[bool]
        drtm_protection: Optional[bool]
        hvci_protection: Optional[bool]
        side_channel_mitigation_enforced: Optional[bool]
        smb_cluster_encryption: Optional[bool]
        smb_signing_enforced: Optional[bool]
        wdac_enforced: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                bitlocker_boot_volume: Optional[bool] = ..., 
                bitlocker_data_volumes: Optional[bool] = ..., 
                credential_guard_enforced: Optional[bool] = ..., 
                drift_control_enforced: Optional[bool] = ..., 
                drtm_protection: Optional[bool] = ..., 
                hvci_protection: Optional[bool] = ..., 
                side_channel_mitigation_enforced: Optional[bool] = ..., 
                smb_cluster_encryption: Optional[bool] = ..., 
                smb_signing_enforced: Optional[bool] = ..., 
                wdac_enforced: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[DeploymentSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingAdapterPropertyOverrides(_Model):
        jumbo_packet: Optional[str]
        network_direct: Optional[str]
        network_direct_technology: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                jumbo_packet: Optional[str] = ..., 
                network_direct: Optional[str] = ..., 
                network_direct_technology: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingHostNetwork(_Model):
        enable_storage_auto_ip: Optional[bool]
        intents: Optional[list[DeploymentSettingIntents]]
        san_networks: Optional[SanNetworks]
        storage_connectivity_switchless: Optional[bool]
        storage_networks: Optional[list[DeploymentSettingStorageNetworks]]

        @overload
        def __init__(
                self, 
                *, 
                enable_storage_auto_ip: Optional[bool] = ..., 
                intents: Optional[list[DeploymentSettingIntents]] = ..., 
                san_networks: Optional[SanNetworks] = ..., 
                storage_connectivity_switchless: Optional[bool] = ..., 
                storage_networks: Optional[list[DeploymentSettingStorageNetworks]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingIntents(_Model):
        adapter: Optional[list[str]]
        adapter_property_overrides: Optional[DeploymentSettingAdapterPropertyOverrides]
        name: Optional[str]
        override_adapter_property: Optional[bool]
        override_qos_policy: Optional[bool]
        override_virtual_switch_configuration: Optional[bool]
        qos_policy_overrides: Optional[QosPolicyOverrides]
        traffic_type: Optional[list[str]]
        virtual_switch_configuration_overrides: Optional[DeploymentSettingVirtualSwitchConfigurationOverrides]

        @overload
        def __init__(
                self, 
                *, 
                adapter: Optional[list[str]] = ..., 
                adapter_property_overrides: Optional[DeploymentSettingAdapterPropertyOverrides] = ..., 
                name: Optional[str] = ..., 
                override_adapter_property: Optional[bool] = ..., 
                override_qos_policy: Optional[bool] = ..., 
                override_virtual_switch_configuration: Optional[bool] = ..., 
                qos_policy_overrides: Optional[QosPolicyOverrides] = ..., 
                traffic_type: Optional[list[str]] = ..., 
                virtual_switch_configuration_overrides: Optional[DeploymentSettingVirtualSwitchConfigurationOverrides] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingStorageAdapterIPInfo(_Model):
        ipv4_address: Optional[str]
        physical_node: Optional[str]
        subnet_mask: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address: Optional[str] = ..., 
                physical_node: Optional[str] = ..., 
                subnet_mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingStorageNetworks(_Model):
        name: Optional[str]
        network_adapter_name: Optional[str]
        storage_adapter_ip_info: Optional[list[DeploymentSettingStorageAdapterIPInfo]]
        vlan_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                network_adapter_name: Optional[str] = ..., 
                storage_adapter_ip_info: Optional[list[DeploymentSettingStorageAdapterIPInfo]] = ..., 
                vlan_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingVirtualSwitchConfigurationOverrides(_Model):
        enable_iov: Optional[str]
        load_balancing_algorithm: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_iov: Optional[str] = ..., 
                load_balancing_algorithm: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentSettingsProperties(_Model):
        arc_node_resource_ids: list[str]
        deployment_configuration: DeploymentConfiguration
        deployment_mode: Union[str, DeploymentMode]
        operation_type: Optional[Union[str, OperationType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[EceReportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                arc_node_resource_ids: list[str], 
                deployment_configuration: DeploymentConfiguration, 
                deployment_mode: Union[str, DeploymentMode], 
                operation_type: Optional[Union[str, OperationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeploymentStep(_Model):
        description: Optional[str]
        end_time_utc: Optional[str]
        error: Optional[ErrorDetail]
        exception: Optional[list[str]]
        full_step_index: Optional[str]
        name: Optional[str]
        start_time_utc: Optional[str]
        status: Optional[str]
        steps: Optional[list[DeploymentStep]]


    class azure.mgmt.azurestackhci.models.DeviceConfiguration(_Model):
        device_metadata: Optional[str]
        nic_details: Optional[list[NicDetail]]

        @overload
        def __init__(
                self, 
                *, 
                device_metadata: Optional[str] = ..., 
                nic_details: Optional[list[NicDetail]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeviceDetail(_Model):
        claimed_by: Optional[str]
        device_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                device_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HCI = "HCI"


    class azure.mgmt.azurestackhci.models.DeviceLogCollectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhci.models.DevicePool(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[DevicePoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[DevicePoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DevicePoolPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DevicePoolProperties(_Model):
        cloud_id: Optional[str]
        custom_location_name: Optional[str]
        custom_location_resource_id: Optional[str]
        devices: Optional[list[DeviceDetail]]
        managed_resource_group: Optional[str]
        operation_details: Optional[list[OperationDetail]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                custom_location_name: Optional[str] = ..., 
                devices: Optional[list[DeviceDetail]] = ..., 
                managed_resource_group: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DeviceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        DRAINING = "Draining"
        IN_MAINTENANCE = "InMaintenance"
        NOT_SPECIFIED = "NotSpecified"
        PROCESSING = "Processing"
        REPAIRING = "Repairing"
        RESUMING = "Resuming"


    class azure.mgmt.azurestackhci.models.DiagnosticLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        ENHANCED = "Enhanced"
        OFF = "Off"


    class azure.mgmt.azurestackhci.models.DiskActionStatus(_Model):
        status: Optional[str]
        steps: Optional[list[DiskDeploymentStep]]


    class azure.mgmt.azurestackhci.models.DiskConfiguration(_Model):
        volumes: Optional[list[DiskVolumeConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                volumes: Optional[list[DiskVolumeConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DiskDeploymentStep(_Model):
        description: Optional[str]
        end_time_utc: Optional[str]
        exception: Optional[list[str]]
        full_step_index: Optional[str]
        name: Optional[str]
        start_time_utc: Optional[str]
        status: Optional[str]
        steps: Optional[list[DiskDeploymentStep]]


    class azure.mgmt.azurestackhci.models.DiskFileSystemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXT4 = "ext4"
        FAT = "fat"
        FAT32 = "fat32"
        NTFS = "NTFS"
        RE_FS = "ReFS"
        VFAT = "vfat"
        XFS = "xfs"


    class azure.mgmt.azurestackhci.models.DiskJobReportedProperties(_Model):
        deployment_status: Optional[DiskActionStatus]
        percent_complete: Optional[int]
        validation_status: Optional[DiskActionStatus]


    class azure.mgmt.azurestackhci.models.DiskJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_VOLUME = "CreateVolume"
        SYNC_CONFIGURATION = "SyncConfiguration"


    class azure.mgmt.azurestackhci.models.DiskReportedProperties(_Model):
        bus_location: Optional[str]
        disk_name: Optional[str]
        disk_type: Optional[Union[str, DiskType]]
        firmware_version: Optional[str]
        is_supported: Optional[bool]
        manufacturer: Optional[str]
        model: Optional[str]
        serial_number: Optional[str]
        size_in_bytes: Optional[str]
        state: Optional[Union[str, DiskState]]
        unallocated_size_in_bytes: Optional[str]
        volumes: Optional[list[DiskVolumeReportedProperties]]


    class azure.mgmt.azurestackhci.models.DiskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        MISSING = "Missing"
        OFFLINE = "Offline"
        ONLINE = "Online"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.DiskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        NV_ME = "NVMe"
        OTHER = "Other"
        SATA = "SATA"
        SCM = "SCM"
        SSD = "SSD"
        UNKNOWN = "Unknown"
        VIRTUAL = "Virtual"


    class azure.mgmt.azurestackhci.models.DiskVolumeConfiguration(_Model):
        file_system: Optional[Union[str, DiskFileSystemType]]
        path: str
        size_in_bytes: str

        @overload
        def __init__(
                self, 
                *, 
                file_system: Optional[Union[str, DiskFileSystemType]] = ..., 
                path: str, 
                size_in_bytes: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DiskVolumeReportedProperties(_Model):
        file_system: Optional[str]
        is_boot: Optional[bool]
        name: Optional[str]
        offset_in_bytes: Optional[int]
        partition_id: Optional[str]
        partition_number: Optional[int]
        path: Optional[str]
        resource_name: Optional[str]
        size_in_bytes: Optional[str]
        size_remaining_in_bytes: Optional[str]


    class azure.mgmt.azurestackhci.models.DnsServerConfig(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        USE_DNS_SERVER = "UseDnsServer"
        USE_FORWARDER = "UseForwarder"


    class azure.mgmt.azurestackhci.models.DnsZones(_Model):
        dns_forwarder: Optional[list[str]]
        dns_zone_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dns_forwarder: Optional[list[str]] = ..., 
                dns_zone_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DownloadOsJobProperties(EdgeMachineJobProperties, discriminator='DownloadOs'):
        deployment_mode: Union[str, DeploymentMode]
        download_request: DownloadRequest
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[EdgeMachineJobType.DOWNLOAD_OS]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[ProvisionOsReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                download_request: DownloadRequest, 
                reported_properties: Optional[ProvisionOsReportedProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DownloadOsProfile(_Model):
        gpg_pub_key: Optional[str]
        image_hash: Optional[str]
        os_image_location: Optional[str]
        os_name: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]
        vsr_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                gpg_pub_key: Optional[str] = ..., 
                image_hash: Optional[str] = ..., 
                os_image_location: Optional[str] = ..., 
                os_name: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                vsr_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.DownloadRequest(_Model):
        os_profile: DownloadOsProfile
        target: Union[str, ProvisioningOsType]

        @overload
        def __init__(
                self, 
                *, 
                os_profile: DownloadOsProfile, 
                target: Union[str, ProvisioningOsType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EAPMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EAP_FAST = "EAP-FAST"
        EAP_TLS = "EAP-TLS"
        EAP_TTLS = "EAP-TTLS"
        PEAP = "PEAP"


    class azure.mgmt.azurestackhci.models.EceActionStatus(_Model):
        status: Optional[str]
        steps: Optional[list[DeploymentStep]]


    class azure.mgmt.azurestackhci.models.EceDeploymentSecrets(_Model):
        ece_secret_name: Optional[Union[str, EceSecrets]]
        secret_location: Optional[str]
        secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ece_secret_name: Optional[Union[str, EceSecrets]] = ..., 
                secret_location: Optional[str] = ..., 
                secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EceReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.EceSecrets(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_STACK_LCM_USER_CREDENTIAL = "AzureStackLCMUserCredential"
        DEFAULT_ARB_APPLICATION = "DefaultARBApplication"
        LOCAL_ADMIN_CREDENTIAL = "LocalAdminCredential"
        WITNESS_STORAGE_KEY = "WitnessStorageKey"


    class azure.mgmt.azurestackhci.models.EdgeDevice(ExtensionResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeDeviceDisks(_Model):
        id: str
        is_supported: Optional[bool]
        manufacturer: Optional[str]
        model: Optional[str]
        size_in_bytes: Optional[str]
        type: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeDeviceJob(ExtensionResource):
        id: str
        kind: str
        name: str
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeDeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HCI = "HCI"


    class azure.mgmt.azurestackhci.models.EdgeDeviceProperties(_Model):
        device_configuration: Optional[DeviceConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                device_configuration: Optional[DeviceConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachine(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[EdgeMachineProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[EdgeMachineProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineAdapterPropertyOverrides(_Model):
        jumbo_packet: Optional[str]
        network_direct: Optional[str]
        network_direct_technology: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineCollectLogJobProperties(EdgeMachineJobProperties, discriminator='CollectLog'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        from_date: datetime
        job_id: str
        job_type: Literal[EdgeMachineJobType.COLLECT_LOG]
        last_log_generated: Optional[datetime]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[EdgeMachineCollectLogJobReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]
        to_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                from_date: datetime, 
                to_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineCollectLogJobReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        log_collection_session_details: Optional[list[LogCollectionJobSession]]
        percent_complete: Optional[int]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.EdgeMachineConnectivityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.azurestackhci.models.EdgeMachineDisk(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineDiskProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineDiskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskInfo(_Model):
        id: str
        is_supported: Optional[bool]
        manufacturer: Optional[str]
        model: Optional[str]
        size_in_bytes: Optional[str]
        type: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskJob(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineDiskJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineDiskJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[DiskJobReportedProperties]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskPrivilegedJob(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineDiskPrivilegedJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineDiskPrivilegedJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskPrivilegedJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[DiskJobReportedProperties]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineDiskProperties(_Model):
        disk_configuration: Optional[DiskConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[DiskReportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                disk_configuration: Optional[DiskConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineGpu(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineGpuProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineGpuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineGpuJob(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineGpuJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineGpuJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineGpuJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        gpu_id: Optional[str]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[JobReportedProperties]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineGpuJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGN_PARTITION = "AssignPartition"
        CREATE_PARTITION = "CreatePartition"
        REMOVE_PARTITION = "RemovePartition"
        SWITCH_MODE = "SwitchMode"


    class azure.mgmt.azurestackhci.models.EdgeMachineGpuProperties(_Model):
        accelerator_type: Optional[str]
        assignable: Optional[bool]
        assignment_status: Optional[str]
        dda_details: Optional[DdaDetails]
        gpu_id: Optional[str]
        gpu_mode: Optional[Union[str, GpuMode]]
        host_driver_version: Optional[str]
        manufacturer: Optional[str]
        memory_model: Optional[str]
        model: Optional[str]
        partition_details: Optional[GpuPartitionDetails]
        partitionable: Optional[bool]
        pci_location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]
        total_memory_in_bytes: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineHostNetwork(_Model):
        enable_storage_auto_ip: Optional[bool]
        intents: Optional[list[EdgeMachineHostNetworkIntent]]
        storage_connectivity_switchless: Optional[bool]
        storage_networks: Optional[list[EdgeMachineStorageNetwork]]


    class azure.mgmt.azurestackhci.models.EdgeMachineHostNetworkIntent(_Model):
        adapter_property_overrides: Optional[EdgeMachineAdapterPropertyOverrides]
        intent_adapters: Optional[list[str]]
        intent_name: Optional[str]
        intent_type: Optional[int]
        is_compute_intent_set: Optional[bool]
        is_management_intent_set: Optional[bool]
        is_network_intent_type: Optional[bool]
        is_only_storage: Optional[bool]
        is_only_stretch: Optional[bool]
        is_storage_intent_set: Optional[bool]
        is_stretch_intent_set: Optional[bool]
        override_adapter_property: Optional[bool]
        override_qos_policy: Optional[bool]
        override_virtual_switch_configuration: Optional[bool]
        qos_policy_overrides: Optional[QosPolicyOverrides]
        scope: Optional[int]
        virtual_switch_configuration_overrides: Optional[EdgeMachineVirtualSwitchConfigurationOverrides]


    class azure.mgmt.azurestackhci.models.EdgeMachineJob(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECT_LOG = "CollectLog"
        DOWNLOAD_OS = "DownloadOs"
        PROVISION_OS = "ProvisionOs"
        REMOTE_SUPPORT = "RemoteSupport"


    class azure.mgmt.azurestackhci.models.EdgeMachineKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"
        STANDARD = "Standard"


    class azure.mgmt.azurestackhci.models.EdgeMachineLifecycleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AWAITING_CONNECTION = "AwaitingConnection"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        INSTALLING_OS = "InstallingOs"
        PROVISIONED = "Provisioned"
        PROVISIONING = "Provisioning"
        READY_FOR_OS = "ReadyForOs"
        RESETTING_OS = "ResettingOs"
        UPDATING_OS = "UpdatingOs"


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkAdapter(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineNetworkAdapterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineNetworkAdapterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkAdapterJob(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineNetworkAdapterJobProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineNetworkAdapterJobProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkAdapterJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[NetworkAdapterJobReportedProperties]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkAdapterProperties(_Model):
        network_configuration: Optional[NetworkAdapterConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[NetworkAdapterReportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                network_configuration: Optional[NetworkAdapterConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkProfile(_Model):
        host_network: Optional[EdgeMachineHostNetwork]
        nic_details: Optional[list[EdgeMachineNicDetail]]
        sdn_properties: Optional[SdnProperties]
        switch_details: Optional[list[SwitchDetail]]


    class azure.mgmt.azurestackhci.models.EdgeMachineNicDetail(_Model):
        adapter_name: Optional[str]
        component_id: Optional[str]
        default_gateway: Optional[str]
        default_isolation_id: Optional[str]
        dns_servers: Optional[list[str]]
        driver_version: Optional[str]
        interface_description: Optional[str]
        ip4_address: Optional[str]
        mac_address: Optional[str]
        nic_status: Optional[str]
        nic_type: Optional[str]
        rdma_capability: Optional[Union[str, RdmaCapability]]
        slot: Optional[str]
        subnet_mask: Optional[str]
        switch_name: Optional[str]
        vlan_id: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachinePatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineProperties(_Model):
        arc_gateway_resource_id: Optional[str]
        arc_machine_resource_group_id: Optional[str]
        arc_machine_resource_id: Optional[str]
        claimed_by: Optional[str]
        cloud_id: Optional[str]
        connectivity_status: Optional[Union[str, EdgeMachineConnectivityStatus]]
        device_pool_resource_id: Optional[str]
        edge_machine_kind: Optional[Union[str, EdgeMachineKind]]
        last_sync_timestamp: Optional[datetime]
        lifecycle_details: Optional[LifecycleDetails]
        machine_state: Optional[Union[str, EdgeMachineState]]
        operation_details: Optional[list[OperationDetail]]
        ownership_voucher_details: Optional[OwnershipVoucherDetails]
        provisioning_details: Optional[ProvisioningDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[EdgeMachineReportedProperties]
        site_details: Optional[SiteDetails]

        @overload
        def __init__(
                self, 
                *, 
                arc_gateway_resource_id: Optional[str] = ..., 
                arc_machine_resource_group_id: Optional[str] = ..., 
                arc_machine_resource_id: Optional[str] = ..., 
                edge_machine_kind: Optional[Union[str, EdgeMachineKind]] = ..., 
                ownership_voucher_details: Optional[OwnershipVoucherDetails] = ..., 
                provisioning_details: Optional[ProvisioningDetails] = ..., 
                site_details: Optional[SiteDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineRemoteSupportJobProperties(EdgeMachineJobProperties, discriminator='RemoteSupport'):
        access_level: Union[str, RemoteSupportAccessLevel]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        expiration_timestamp: datetime
        job_id: str
        job_type: Literal[EdgeMachineJobType.REMOTE_SUPPORT]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[EdgeMachineRemoteSupportJobReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]
        type: Union[str, RemoteSupportType]

        @overload
        def __init__(
                self, 
                *, 
                access_level: Union[str, RemoteSupportAccessLevel], 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                expiration_timestamp: datetime, 
                type: Union[str, RemoteSupportType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineRemoteSupportJobReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        node_settings: Optional[EdgeMachineRemoteSupportNodeSettings]
        percent_complete: Optional[int]
        session_details: Optional[list[RemoteSupportSession]]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.EdgeMachineRemoteSupportNodeSettings(_Model):
        connection_error_message: Optional[str]
        connection_status: Optional[str]
        created_at: Optional[datetime]
        state: Optional[str]
        updated_at: Optional[datetime]


    class azure.mgmt.azurestackhci.models.EdgeMachineReportedProperties(_Model):
        confidential_vm_profile: Optional[ConfidentialVmProfile]
        extension_profile: Optional[ExtensionProfile]
        hardware_profile: Optional[HardwareProfile]
        last_updated: Optional[datetime]
        network_profile: Optional[EdgeMachineNetworkProfile]
        os_profile: Optional[OsProfile]
        sbe_deployment_package_info: Optional[SbeDeploymentPackageInfo]
        storage_profile: Optional[StorageProfile]
        workload_inventory: Optional[list[EdgeMachineWorkloadInventoryItem]]
        workload_inventory_last_updated: Optional[datetime]


    class azure.mgmt.azurestackhci.models.EdgeMachineState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        FAILED = "Failed"
        PREPARING = "Preparing"
        PURPOSED = "Purposed"
        REGISTERING = "Registering"
        RESETTING = "Resetting"
        TRANSITIONING = "Transitioning"
        UNPURPOSED = "Unpurposed"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.EdgeMachineStorageAdapterIpInfo(_Model):
        ipv4_address: Optional[str]
        physical_node: Optional[str]
        subnet_mask: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineStorageNetwork(_Model):
        name: Optional[str]
        network_adapter_name: Optional[str]
        storage_adapter_ip_info: Optional[list[EdgeMachineStorageAdapterIpInfo]]
        storage_vlan_id: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineUpdate(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineUpdateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineUpdateInfo(_Model):
        arc_agent_version: Optional[str]
        display_name: Optional[str]
        estimated_install_time_minutes: Optional[int]
        reboot_required: Optional[bool]
        release_notes_link: Optional[str]
        total_size_bytes: Optional[int]
        update_type: Optional[str]
        vsr_version: str

        @overload
        def __init__(
                self, 
                *, 
                arc_agent_version: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                estimated_install_time_minutes: Optional[int] = ..., 
                reboot_required: Optional[bool] = ..., 
                release_notes_link: Optional[str] = ..., 
                total_size_bytes: Optional[int] = ..., 
                update_type: Optional[str] = ..., 
                vsr_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineUpdateProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        solution_type: Optional[Union[str, ProvisioningOsType]]
        values_property: list[EdgeMachineUpdateInfo]

        @overload
        def __init__(
                self, 
                *, 
                solution_type: Optional[Union[str, ProvisioningOsType]] = ..., 
                values_property: list[EdgeMachineUpdateInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineValidateRequest(_Model):
        additional_info: Optional[str]
        edge_machine_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[str] = ..., 
                edge_machine_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineValidateResponse(_Model):
        status: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineVirtualSwitchConfigurationOverrides(_Model):
        enable_iov: Optional[str]
        load_balancing_algorithm: Optional[str]


    class azure.mgmt.azurestackhci.models.EdgeMachineVolume(ProxyResource):
        id: str
        name: str
        properties: Optional[EdgeMachineVolumeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeMachineVolumeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineVolumeProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reported_properties: Optional[VolumeReportedProperties]
        volume_configuration: Optional[VolumeConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                volume_configuration: Optional[VolumeConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.EdgeMachineWorkloadInventoryItem(_Model):
        memory_in_bytes: Optional[str]
        name: Optional[str]
        resource_id: Optional[str]
        state: Optional[str]
        virtual_processor_count: Optional[str]
        workload_id: Optional[str]
        workload_type: Optional[str]


    class azure.mgmt.azurestackhci.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.azurestackhci.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.azurestackhci.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.Extension(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtensionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionAggregateState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONNECTED = "Connected"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PARTIALLY_CONNECTED = "PartiallyConnected"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"
        UPGRADE_FAILED_ROLLBACK_SUCCEEDED = "UpgradeFailedRollbackSucceeded"


    class azure.mgmt.azurestackhci.models.ExtensionInstanceView(_Model):
        name: Optional[str]
        status: Optional[ExtensionInstanceViewStatus]
        type: Optional[str]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                status: Optional[ExtensionInstanceViewStatus] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionInstanceViewStatus(_Model):
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


    class azure.mgmt.azurestackhci.models.ExtensionManagedBy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        USER = "User"


    class azure.mgmt.azurestackhci.models.ExtensionParameters(_Model):
        auto_upgrade_minor_version: Optional[bool]
        enable_automatic_upgrade: Optional[bool]
        force_update_tag: Optional[str]
        protected_settings: Optional[Any]
        publisher: Optional[str]
        settings: Optional[Any]
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
                publisher: Optional[str] = ..., 
                settings: Optional[Any] = ..., 
                type: Optional[str] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionPatch(_Model):
        properties: Optional[ExtensionPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionPatchParameters(_Model):
        enable_automatic_upgrade: Optional[bool]
        protected_settings: Optional[Any]
        settings: Optional[Any]
        type_handler_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_automatic_upgrade: Optional[bool] = ..., 
                protected_settings: Optional[Any] = ..., 
                settings: Optional[Any] = ..., 
                type_handler_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionPatchProperties(_Model):
        extension_parameters: Optional[ExtensionPatchParameters]

        @overload
        def __init__(
                self, 
                *, 
                extension_parameters: Optional[ExtensionPatchParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionProfile(_Model):
        extensions: Optional[list[HciEdgeDeviceArcExtension]]


    class azure.mgmt.azurestackhci.models.ExtensionProperties(_Model):
        aggregate_state: Optional[Union[str, ExtensionAggregateState]]
        extension_parameters: Optional[ExtensionParameters]
        managed_by: Optional[Union[str, ExtensionManagedBy]]
        per_node_extension_details: Optional[list[PerNodeExtensionState]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                extension_parameters: Optional[ExtensionParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.models.ExtensionUpgradeParameters(_Model):
        target_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ForcePushNetworkAdapterJobProperties(EdgeMachineNetworkAdapterJobProperties, discriminator='ForcePush'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.FORCE_PUSH]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.GpuCreatePartitionJobProperties(ClusterJobProperties, discriminator='GpuCreatePartition'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.GPU_CREATE_PARTITION]
        partition_count: int
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                partition_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.GpuMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DDA = "DDA"
        GPUP = "GPUP"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.GpuPartitionDetails(_Model):
        assigned_partitions: Optional[int]
        available_decode: Optional[str]
        available_encode: Optional[str]
        available_partitions: Optional[int]
        available_vram: Optional[str]
        partition_size_mb: Optional[str]
        partitionable_gpu_name: Optional[str]
        partitions: Optional[list[PartitionDetails]]
        total_partitions: Optional[int]
        total_vram: Optional[str]
        valid_partition_count: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                partitionable_gpu_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.GpuSwitchModeJobProperties(ClusterJobProperties, discriminator='GpuSwitchMode'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.GPU_SWITCH_MODE]
        mode: Union[str, GpuMode]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                mode: Union[str, GpuMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HardwareClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARGE = "Large"
        MEDIUM = "Medium"
        SMALL = "Small"


    class azure.mgmt.azurestackhci.models.HardwareProfile(_Model):
        cpu_cores: Optional[int]
        cpu_sockets: Optional[int]
        manufacturer: Optional[str]
        memory_capacity_in_gb: Optional[int]
        model: Optional[str]
        processor_type: Optional[str]
        serial_number: Optional[str]


    class azure.mgmt.azurestackhci.models.HciAddServerJobProperties(ClusterJobProperties, discriminator='AddServer'):
        add_server_job_server_details: list[AddServerJobServerDetails]
        cloud_account_name: Optional[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.ADD_SERVER]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        secrets: Optional[list[EceDeploymentSecrets]]
        start_time_utc: datetime
        status: Union[str, JobStatus]
        witness_path: Optional[str]
        witness_type: Optional[Union[str, WitnessType]]

        @overload
        def __init__(
                self, 
                *, 
                add_server_job_server_details: list[AddServerJobServerDetails], 
                cloud_account_name: Optional[str] = ..., 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                secrets: Optional[list[EceDeploymentSecrets]] = ..., 
                witness_path: Optional[str] = ..., 
                witness_type: Optional[Union[str, WitnessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciCollectLogJobProperties(HciEdgeDeviceJobProperties, discriminator='CollectLog'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        from_date: datetime
        job_id: str
        job_type: Literal[HciEdgeDeviceJobType.COLLECT_LOG]
        last_log_generated: Optional[datetime]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[LogCollectionReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]
        to_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                from_date: datetime, 
                to_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciConfigureCvmJobProperties(ClusterJobProperties, discriminator='ConfigureCVM'):
        confidential_vm_intent: Union[str, ConfidentialVmIntent]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.CONFIGURE_CVM]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                confidential_vm_intent: Union[str, ConfidentialVmIntent], 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciConfigureSdnIntegrationJobProperties(ClusterJobProperties, discriminator='ConfigureSdnIntegration'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.CONFIGURE_SDN_INTEGRATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        sdn_integration_intent: Union[str, SdnIntegrationIntent]
        sdn_prefix: Optional[str]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                sdn_integration_intent: Union[str, SdnIntegrationIntent], 
                sdn_prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciEdgeDevice(EdgeDevice, discriminator='HCI'):
        id: str
        kind: Literal[DeviceKind.HCI]
        name: str
        properties: Optional[HciEdgeDeviceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HciEdgeDeviceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceAdapterPropertyOverrides(_Model):
        jumbo_packet: Optional[str]
        network_direct: Optional[str]
        network_direct_technology: Optional[str]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceArcExtension(_Model):
        error_details: Optional[list[HciValidationFailureDetail]]
        extension_name: Optional[str]
        extension_resource_id: Optional[str]
        managed_by: Optional[Union[str, ExtensionManagedBy]]
        state: Optional[Union[str, ArcExtensionState]]
        type_handler_version: Optional[str]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceHostNetwork(_Model):
        enable_storage_auto_ip: Optional[bool]
        intents: Optional[list[HciEdgeDeviceIntents]]
        storage_connectivity_switchless: Optional[bool]
        storage_networks: Optional[list[HciEdgeDeviceStorageNetworks]]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceIntents(_Model):
        adapter_property_overrides: Optional[HciEdgeDeviceAdapterPropertyOverrides]
        intent_adapters: Optional[list[str]]
        intent_name: Optional[str]
        intent_type: Optional[int]
        is_compute_intent_set: Optional[bool]
        is_management_intent_set: Optional[bool]
        is_network_intent_type: Optional[bool]
        is_only_storage: Optional[bool]
        is_only_stretch: Optional[bool]
        is_storage_intent_set: Optional[bool]
        is_stretch_intent_set: Optional[bool]
        override_adapter_property: Optional[bool]
        override_qos_policy: Optional[bool]
        override_virtual_switch_configuration: Optional[bool]
        qos_policy_overrides: Optional[QosPolicyOverrides]
        scope: Optional[int]
        virtual_switch_configuration_overrides: Optional[HciEdgeDeviceVirtualSwitchConfigurationOverrides]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceJob(EdgeDeviceJob, discriminator='HCI'):
        id: str
        kind: Literal[EdgeDeviceKind.HCI]
        name: str
        properties: HciEdgeDeviceJobProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: HciEdgeDeviceJobProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceJobProperties(_Model):
        deployment_mode: Optional[Union[str, DeploymentMode]]
        end_time_utc: Optional[datetime]
        job_id: Optional[str]
        job_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, JobStatus]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                job_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECT_LOG = "CollectLog"
        REMOTE_SUPPORT = "RemoteSupport"


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceProperties(EdgeDeviceProperties):
        device_configuration: DeviceConfiguration
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[HciReportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                device_configuration: Optional[DeviceConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceStorageAdapterIPInfo(_Model):
        ipv4_address: Optional[str]
        physical_node: Optional[str]
        subnet_mask: Optional[str]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceStorageNetworks(_Model):
        name: Optional[str]
        network_adapter_name: Optional[str]
        storage_adapter_ip_info: Optional[list[HciEdgeDeviceStorageAdapterIPInfo]]
        storage_vlan_id: Optional[str]


    class azure.mgmt.azurestackhci.models.HciEdgeDeviceVirtualSwitchConfigurationOverrides(_Model):
        enable_iov: Optional[str]
        load_balancing_algorithm: Optional[str]


    class azure.mgmt.azurestackhci.models.HciHardwareProfile(_Model):
        processor_type: Optional[str]


    class azure.mgmt.azurestackhci.models.HciJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_SERVER = "AddServer"
        CONFIGURE_CVM = "ConfigureCVM"
        CONFIGURE_SDN_INTEGRATION = "ConfigureSdnIntegration"
        GPU_CREATE_PARTITION = "GpuCreatePartition"
        GPU_SWITCH_MODE = "GpuSwitchMode"
        REPAIR_SERVER = "RepairServer"
        VM_CONNECT_PROVISION = "VmConnectProvision"
        VM_CONNECT_REMOVE = "VmConnectRemove"


    class azure.mgmt.azurestackhci.models.HciNetworkProfile(_Model):
        host_network: Optional[HciEdgeDeviceHostNetwork]
        nic_details: Optional[list[HciNicDetail]]
        sdn_properties: Optional[SdnProperties]
        switch_details: Optional[list[SwitchDetail]]


    class azure.mgmt.azurestackhci.models.HciNicDetail(_Model):
        adapter_name: Optional[str]
        component_id: Optional[str]
        default_gateway: Optional[str]
        default_isolation_id: Optional[str]
        dns_servers: Optional[list[str]]
        driver_version: Optional[str]
        interface_description: Optional[str]
        ip4_address: Optional[str]
        mac_address: Optional[str]
        nic_status: Optional[str]
        nic_type: Optional[str]
        rdma_capability: Optional[Union[str, RdmaCapability]]
        slot: Optional[str]
        subnet_mask: Optional[str]
        switch_name: Optional[str]
        vlan_id: Optional[str]


    class azure.mgmt.azurestackhci.models.HciOsProfile(_Model):
        assembly_version: Optional[str]
        boot_type: Optional[str]


    class azure.mgmt.azurestackhci.models.HciRemoteSupportJobProperties(HciEdgeDeviceJobProperties, discriminator='RemoteSupport'):
        access_level: Union[str, RemoteSupportAccessLevel]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        expiration_timestamp: datetime
        job_id: str
        job_type: Literal[HciEdgeDeviceJobType.REMOTE_SUPPORT]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[RemoteSupportJobReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]
        type: Union[str, RemoteSupportType]

        @overload
        def __init__(
                self, 
                *, 
                access_level: Union[str, RemoteSupportAccessLevel], 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                expiration_timestamp: datetime, 
                type: Union[str, RemoteSupportType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciRepairServerJobProperties(ClusterJobProperties, discriminator='RepairServer'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.REPAIR_SERVER]
        provisioning_state: Union[str, ProvisioningState]
        repair_server_job_server_details: list[RepairServerJobServerDetails]
        reported_properties: JobReportedProperties
        secrets: Optional[list[EceDeploymentSecrets]]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                repair_server_job_server_details: list[RepairServerJobServerDetails], 
                secrets: Optional[list[EceDeploymentSecrets]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.HciReportedProperties(ReportedProperties):
        confidential_vm_profile: ConfidentialVmProfile
        device_state: Union[str, DeviceState]
        extension_profile: ExtensionProfile
        hardware_profile: Optional[HciHardwareProfile]
        last_sync_timestamp: datetime
        network_profile: Optional[HciNetworkProfile]
        os_profile: Optional[HciOsProfile]
        sbe_deployment_package_info: Optional[SbeDeploymentPackageInfo]
        storage_profile: Optional[HciStorageProfile]


    class azure.mgmt.azurestackhci.models.HciStorageProfile(_Model):
        disks: Optional[list[EdgeDeviceDisks]]
        poolable_disks_count: Optional[int]


    class azure.mgmt.azurestackhci.models.HciValidationFailureDetail(_Model):
        exception: Optional[str]


    class azure.mgmt.azurestackhci.models.HealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        FAILURE = "Failure"
        IN_PROGRESS = "InProgress"
        SUCCESS = "Success"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.azurestackhci.models.IdentityProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"
        LOCAL_IDENTITY = "LocalIdentity"


    class azure.mgmt.azurestackhci.models.IgvmStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.IgvmStatusDetail(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.azurestackhci.models.ImdsAttestation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.azurestackhci.models.InfrastructureNetwork(_Model):
        dns_server_config: Optional[Union[str, DnsServerConfig]]
        dns_servers: Optional[list[str]]
        dns_zones: Optional[list[DnsZones]]
        gateway: Optional[str]
        ip_pools: Optional[list[IpPools]]
        subnet_mask: Optional[str]
        use_dhcp: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                dns_server_config: Optional[Union[str, DnsServerConfig]] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                dns_zones: Optional[list[DnsZones]] = ..., 
                gateway: Optional[str] = ..., 
                ip_pools: Optional[list[IpPools]] = ..., 
                subnet_mask: Optional[str] = ..., 
                use_dhcp: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.InterfaceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "down"
        UP = "up"


    class azure.mgmt.azurestackhci.models.IpAddressRange(_Model):
        end_ip: str
        start_ip: str

        @overload
        def __init__(
                self, 
                *, 
                end_ip: str, 
                start_ip: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.IpAssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.azurestackhci.models.IpInterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DHCP = "Dhcp"
        STATIC = "Static"


    class azure.mgmt.azurestackhci.models.IpPools(_Model):
        ending_address: Optional[str]
        starting_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ending_address: Optional[str] = ..., 
                starting_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.IsolatedVmAttestationConfiguration(_Model):
        attestation_resource_id: Optional[str]
        attestation_service_endpoint: Optional[str]
        relying_party_service_endpoint: Optional[str]


    class azure.mgmt.azurestackhci.models.JobReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        percent_complete: Optional[int]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DEPLOYMENT_FAILED = "DeploymentFailed"
        DEPLOYMENT_IN_PROGRESS = "DeploymentInProgress"
        DEPLOYMENT_SUCCESS = "DeploymentSuccess"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        PAUSED = "Paused"
        SCHEDULED = "Scheduled"
        SUCCEEDED = "Succeeded"
        VALIDATION_FAILED = "ValidationFailed"
        VALIDATION_IN_PROGRESS = "ValidationInProgress"
        VALIDATION_SUCCESS = "ValidationSuccess"


    class azure.mgmt.azurestackhci.models.KubernetesVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[KubernetesVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[KubernetesVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.KubernetesVersionProperties(_Model):
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.LifecycleDetails(_Model):
        lifecycle_stages: list[LifecycleStage]
        lifecycle_status: Optional[LifecycleStatus]


    class azure.mgmt.azurestackhci.models.LifecycleOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"


    class azure.mgmt.azurestackhci.models.LifecycleStage(_Model):
        description: str
        end_time_utc: Optional[datetime]
        error: Optional[ErrorDetail]
        last_updated_utc: Optional[datetime]
        name: str
        start_time_utc: Optional[datetime]
        status: Union[str, LifecycleOperationStatus]
        sub_stages: Optional[list[LifecycleStage]]


    class azure.mgmt.azurestackhci.models.LifecycleStatus(_Model):
        last_updated_utc: datetime
        message: Optional[str]
        recommended_steps: Optional[list[str]]
        stage: Optional[str]
        status: Union[str, EdgeMachineLifecycleStatus]


    class azure.mgmt.azurestackhci.models.LocalAvailabilityZones(_Model):
        local_availability_zone_name: Optional[str]
        nodes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                local_availability_zone_name: Optional[str] = ..., 
                nodes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.LogCollectionError(_Model):
        error_code: Optional[str]
        error_message: Optional[str]


    class azure.mgmt.azurestackhci.models.LogCollectionJobSession(_Model):
        correlation_id: Optional[str]
        end_time: Optional[str]
        log_size: Optional[int]
        start_time: Optional[str]
        status: Optional[Union[str, DeviceLogCollectionStatus]]
        time_collected: Optional[str]


    class azure.mgmt.azurestackhci.models.LogCollectionJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "OnDemand"
        SCHEDULED = "Scheduled"


    class azure.mgmt.azurestackhci.models.LogCollectionProperties(_Model):
        from_date: Optional[datetime]
        last_log_generated: Optional[datetime]
        log_collection_session_details: Optional[list[LogCollectionSession]]
        to_date: Optional[datetime]


    class azure.mgmt.azurestackhci.models.LogCollectionReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        log_collection_session_details: Optional[list[LogCollectionJobSession]]
        percent_complete: Optional[int]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.LogCollectionRequest(_Model):
        properties: Optional[LogCollectionRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogCollectionRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.LogCollectionRequestProperties(_Model):
        from_date: datetime
        to_date: datetime

        @overload
        def __init__(
                self, 
                *, 
                from_date: datetime, 
                to_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.LogCollectionSession(_Model):
        correlation_id: Optional[str]
        end_time_collected: Optional[datetime]
        log_collection_error: Optional[LogCollectionError]
        log_collection_job_type: Optional[Union[str, LogCollectionJobType]]
        log_collection_status: Optional[Union[str, LogCollectionStatus]]
        log_end_time: Optional[datetime]
        log_size: Optional[int]
        log_start_time: Optional[datetime]
        time_collected: Optional[datetime]


    class azure.mgmt.azurestackhci.models.LogCollectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhci.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.azurestackhci.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.azurestackhci.models.NetworkAdapter(_Model):
        adapter_name: Optional[str]
        dns_address_array: Optional[list[str]]
        gateway: Optional[str]
        ip_address: Optional[str]
        ip_address_range: Optional[IpAddressRange]
        ip_assignment_type: Union[str, IpAssignmentType]
        mac_address: Optional[str]
        subnet_mask: Optional[str]
        vlan_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                adapter_name: Optional[str] = ..., 
                dns_address_array: Optional[list[str]] = ..., 
                gateway: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                ip_address_range: Optional[IpAddressRange] = ..., 
                ip_assignment_type: Union[str, IpAssignmentType], 
                mac_address: Optional[str] = ..., 
                subnet_mask: Optional[str] = ..., 
                vlan_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NetworkAdapterActionStatus(_Model):
        status: Optional[str]
        steps: Optional[list[NetworkAdapterDeploymentStep]]


    class azure.mgmt.azurestackhci.models.NetworkAdapterConfiguration(_Model):
        adapter_name: Optional[str]
        default_gateway: Optional[str]
        dns_servers: Optional[list[str]]
        interface_state: Optional[Union[str, InterfaceState]]
        ip4_address: Optional[str]
        ip_interface_type: Optional[Union[str, IpInterfaceType]]
        subnet_mask: Optional[str]
        vlan_id: Optional[int]
        wifi_configuration: Optional[WifiConfigurationDesiredProperties]

        @overload
        def __init__(
                self, 
                *, 
                adapter_name: Optional[str] = ..., 
                default_gateway: Optional[str] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                interface_state: Optional[Union[str, InterfaceState]] = ..., 
                ip4_address: Optional[str] = ..., 
                ip_interface_type: Optional[Union[str, IpInterfaceType]] = ..., 
                subnet_mask: Optional[str] = ..., 
                vlan_id: Optional[int] = ..., 
                wifi_configuration: Optional[WifiConfigurationDesiredProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NetworkAdapterDeploymentStep(_Model):
        description: Optional[str]
        end_time_utc: Optional[str]
        exception: Optional[list[str]]
        full_step_index: Optional[str]
        name: Optional[str]
        start_time_utc: Optional[str]
        status: Optional[str]
        steps: Optional[list[NetworkAdapterDeploymentStep]]


    class azure.mgmt.azurestackhci.models.NetworkAdapterJobReportedProperties(_Model):
        deployment_status: Optional[NetworkAdapterActionStatus]
        percent_complete: Optional[int]
        validation_status: Optional[NetworkAdapterActionStatus]


    class azure.mgmt.azurestackhci.models.NetworkAdapterJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_CONFIGURATION = "ApplyConfiguration"
        FORCE_PUSH = "ForcePush"
        SYNC_CONFIGURATION = "SyncConfiguration"


    class azure.mgmt.azurestackhci.models.NetworkAdapterOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhci.models.NetworkAdapterProvisioningStatus(_Model):
        operation_id: Optional[str]
        status: Optional[Union[str, NetworkAdapterOperationStatus]]


    class azure.mgmt.azurestackhci.models.NetworkAdapterReportedProperties(_Model):
        adapter_name: Optional[str]
        component_id: Optional[str]
        default_gateway: Optional[str]
        default_isolation_id: Optional[str]
        dns_servers: Optional[list[str]]
        driver_version: Optional[str]
        interface_description: Optional[str]
        interface_speed: Optional[int]
        interface_state: Optional[Union[str, InterfaceState]]
        interface_type: Optional[Union[str, NetworkInterfaceType]]
        ip4_address: Optional[str]
        ip_interface_type: Optional[Union[str, IpInterfaceType]]
        mac_address: Optional[str]
        management_interface: Optional[bool]
        network_adapter_status: Optional[NetworkAdapterStatus]
        nic_status: Optional[str]
        nic_type: Optional[str]
        rdma_capability: Optional[Union[str, RdmaCapability]]
        slot: Optional[str]
        subnet_mask: Optional[str]
        switch_name: Optional[str]
        vlan_id: Optional[int]
        wifi_configuration: Optional[WifiConfigurationReportedProperties]

        @overload
        def __init__(
                self, 
                *, 
                adapter_name: Optional[str] = ..., 
                default_gateway: Optional[str] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                ip4_address: Optional[str] = ..., 
                subnet_mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NetworkAdapterStatus(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        provisioning_status: Optional[NetworkAdapterProvisioningStatus]


    class azure.mgmt.azurestackhci.models.NetworkConfiguration(_Model):
        network_adapters: Optional[list[NetworkAdapter]]

        @overload
        def __init__(
                self, 
                *, 
                network_adapters: Optional[list[NetworkAdapter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NetworkController(_Model):
        mac_address_pool_start: Optional[str]
        mac_address_pool_stop: Optional[str]
        network_virtualization_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                mac_address_pool_start: Optional[str] = ..., 
                mac_address_pool_stop: Optional[str] = ..., 
                network_virtualization_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NetworkInterfaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ETH = "Eth"
        WIFI = "wifi"


    class azure.mgmt.azurestackhci.models.NextBillingModel(_Model):
        billing_model: Optional[str]
        capabilities_enabled: Optional[list[str]]
        trial_days_remaining: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                billing_model: Optional[str] = ..., 
                capabilities_enabled: Optional[list[str]] = ..., 
                trial_days_remaining: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NicDetail(_Model):
        adapter_name: Optional[str]
        component_id: Optional[str]
        default_gateway: Optional[str]
        default_isolation_id: Optional[str]
        dns_servers: Optional[list[str]]
        driver_version: Optional[str]
        interface_description: Optional[str]
        ip4_address: Optional[str]
        subnet_mask: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                adapter_name: Optional[str] = ..., 
                component_id: Optional[str] = ..., 
                default_gateway: Optional[str] = ..., 
                default_isolation_id: Optional[str] = ..., 
                dns_servers: Optional[list[str]] = ..., 
                driver_version: Optional[str] = ..., 
                interface_description: Optional[str] = ..., 
                ip4_address: Optional[str] = ..., 
                subnet_mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.NodeArcState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONNECTED = "Connected"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DISABLE_IN_PROGRESS = "DisableInProgress"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PARTIALLY_CONNECTED = "PartiallyConnected"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.NodeExtensionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONNECTED = "Connected"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PARTIALLY_CONNECTED = "PartiallyConnected"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.OSOperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVISION = "Provision"
        RE_IMAGE = "ReImage"
        UPDATE = "Update"


    class azure.mgmt.azurestackhci.models.Observability(_Model):
        episodic_data_upload: Optional[bool]
        eu_location: Optional[bool]
        streaming_data_client: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                episodic_data_upload: Optional[bool] = ..., 
                eu_location: Optional[bool] = ..., 
                streaming_data_client: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OemActivation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.azurestackhci.models.Offer(ProxyResource):
        id: str
        name: str
        properties: Optional[OfferProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OfferProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.OfferProperties(_Model):
        content: Optional[str]
        content_version: Optional[str]
        provisioning_state: Optional[str]
        publisher_id: Optional[str]
        sku_mappings: Optional[list[SkuMappings]]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_version: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                sku_mappings: Optional[list[SkuMappings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OnboardingConfiguration(_Model):
        arc_virtual_machine_id: Optional[str]
        location: Optional[str]
        resource_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, OnboardingResourceType]]

        @overload
        def __init__(
                self, 
                *, 
                arc_virtual_machine_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                type: Optional[Union[str, OnboardingResourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OnboardingResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HYBRID_COMPUTE_MACHINE = "HybridComputeMachine"


    class azure.mgmt.azurestackhci.models.Operation(_Model):
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


    class azure.mgmt.azurestackhci.models.OperationDetail(_Model):
        description: Optional[str]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        resource_id: Optional[str]
        status: Optional[str]
        type: Optional[str]


    class azure.mgmt.azurestackhci.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.azurestackhci.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_PROVISIONING = "ClusterProvisioning"
        CLUSTER_UPGRADE = "ClusterUpgrade"


    class azure.mgmt.azurestackhci.models.OptionalServices(_Model):
        confidential_vm_intent: Optional[Union[str, ConfidentialVmIntent]]
        custom_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidential_vm_intent: Optional[Union[str, ConfidentialVmIntent]] = ..., 
                custom_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.azurestackhci.models.OsImage(ProxyResource):
        id: str
        name: str
        properties: Optional[OsImageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OsImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OsImageProperties(_Model):
        composed_image_iso_hash: Optional[str]
        composed_image_iso_url: Optional[str]
        composed_image_version: Optional[str]
        validated_solution_recipe_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                composed_image_iso_hash: Optional[str] = ..., 
                composed_image_iso_url: Optional[str] = ..., 
                composed_image_version: Optional[str] = ..., 
                validated_solution_recipe_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OsProfile(_Model):
        assembly_version: Optional[str]
        base_image_version: Optional[str]
        boot_type: Optional[str]
        build_number: Optional[str]
        image_version: Optional[str]
        os_sku: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]


    class azure.mgmt.azurestackhci.models.OsProvisionProfile(_Model):
        gpg_pub_key: Optional[str]
        image_hash: Optional[str]
        operation_type: Optional[Union[str, OSOperationType]]
        os_image_location: Optional[str]
        os_name: Optional[str]
        os_type: Optional[str]
        os_version: Optional[str]
        vsr_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                gpg_pub_key: Optional[str] = ..., 
                image_hash: Optional[str] = ..., 
                operation_type: Optional[Union[str, OSOperationType]] = ..., 
                os_image_location: Optional[str] = ..., 
                os_name: Optional[str] = ..., 
                os_type: Optional[str] = ..., 
                os_version: Optional[str] = ..., 
                vsr_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OverprovisioningRatio(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE = "1"
        TWO = "2"
        ZERO = "0"


    class azure.mgmt.azurestackhci.models.OwnerKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_MANAGED = "MicrosoftManaged"


    class azure.mgmt.azurestackhci.models.OwnershipVoucherDetails(_Model):
        owner_key_type: Union[str, OwnerKeyType]
        ownership_voucher: str
        validation_details: Optional[OwnershipVoucherValidationDetails]

        @overload
        def __init__(
                self, 
                *, 
                owner_key_type: Union[str, OwnerKeyType], 
                ownership_voucher: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OwnershipVoucherValidationDetails(_Model):
        azure_machine_id: Optional[str]
        error: Optional[ErrorDetail]
        id: Optional[str]
        manufacturer: Optional[str]
        model_name: Optional[str]
        serial_number: Optional[str]
        validation_status: Optional[Union[str, OwnershipVoucherValidationStatus]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                azure_machine_id: Optional[str] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                model_name: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                validation_status: Optional[Union[str, OwnershipVoucherValidationStatus]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.OwnershipVoucherValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.azurestackhci.models.PackageVersionInfo(_Model):
        last_updated: Optional[datetime]
        package_type: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_updated: Optional[datetime] = ..., 
                package_type: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PartitionDetails(_Model):
        current_decode: Optional[str]
        current_encode: Optional[str]
        current_vram: Optional[str]
        partition_id: Optional[int]
        unique_id: Optional[str]
        workload_detail: Optional[WorkloadDetails]


    class azure.mgmt.azurestackhci.models.PasswordCredential(_Model):
        end_date_time: Optional[datetime]
        key_id: Optional[str]
        secret_text: Optional[str]
        start_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_date_time: Optional[datetime] = ..., 
                key_id: Optional[str] = ..., 
                secret_text: Optional[str] = ..., 
                start_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PerNodeExtensionState(_Model):
        extension: Optional[str]
        instance_view: Optional[ExtensionInstanceView]
        name: Optional[str]
        state: Optional[Union[str, NodeExtensionState]]
        type_handler_version: Optional[str]


    class azure.mgmt.azurestackhci.models.PerNodeRemoteSupportSession(_Model):
        access_level: Optional[Union[str, AccessLevel]]
        duration: Optional[int]
        node_name: Optional[str]
        session_end_time: Optional[datetime]
        session_start_time: Optional[datetime]
        transcript_location: Optional[str]


    class azure.mgmt.azurestackhci.models.PerNodeState(_Model):
        arc_instance: Optional[str]
        arc_node_service_principal_object_id: Optional[str]
        name: Optional[str]
        state: Optional[Union[str, NodeArcState]]


    class azure.mgmt.azurestackhci.models.PhysicalNodes(_Model):
        ipv4_address: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ipv4_address: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PlatformPayload(_Model):
        payload_hash: Optional[str]
        payload_identifier: Optional[str]
        payload_package_size_in_bytes: Optional[str]
        payload_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                payload_hash: Optional[str] = ..., 
                payload_identifier: Optional[str] = ..., 
                payload_package_size_in_bytes: Optional[str] = ..., 
                payload_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PlatformUpdate(ProxyResource):
        id: str
        name: str
        properties: Optional[PlatformUpdateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlatformUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PlatformUpdateDetails(_Model):
        platform_payloads: list[PlatformPayload]
        platform_version: Optional[str]
        validated_solution_recipe_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                platform_payloads: list[PlatformPayload], 
                platform_version: Optional[str] = ..., 
                validated_solution_recipe_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PlatformUpdateProperties(_Model):
        platform_update_details: list[PlatformUpdateDetails]

        @overload
        def __init__(
                self, 
                *, 
                platform_update_details: list[PlatformUpdateDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PrecheckResult(_Model):
        additional_data: Optional[str]
        description: Optional[str]
        display_name: Optional[str]
        health_check_source: Optional[str]
        health_check_tags: Optional[Any]
        name: Optional[str]
        remediation: Optional[str]
        severity: Optional[Union[str, Severity]]
        status: Optional[Union[str, Status]]
        tags: Optional[PrecheckResultTags]
        target_resource_id: Optional[str]
        target_resource_name: Optional[str]
        target_resource_type: Optional[str]
        timestamp: Optional[datetime]
        title: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_data: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                health_check_source: Optional[str] = ..., 
                health_check_tags: Optional[Any] = ..., 
                name: Optional[str] = ..., 
                remediation: Optional[str] = ..., 
                severity: Optional[Union[str, Severity]] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                tags: Optional[PrecheckResultTags] = ..., 
                target_resource_id: Optional[str] = ..., 
                target_resource_name: Optional[str] = ..., 
                target_resource_type: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                title: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PrecheckResultTags(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.PrivilegedJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_VOLUME = "DeleteVolume"


    class azure.mgmt.azurestackhci.models.ProvisionOsJobProperties(EdgeMachineJobProperties, discriminator='ProvisionOs'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[EdgeMachineJobType.PROVISION_OS]
        provisioning_request: ProvisioningRequest
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: Optional[ProvisionOsReportedProperties]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                provisioning_request: ProvisioningRequest, 
                reported_properties: Optional[ProvisionOsReportedProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ProvisionOsReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        percent_complete: Optional[int]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.ProvisioningDetails(_Model):
        os_profile: OsProvisionProfile
        user_details: Optional[list[UserDetails]]

        @overload
        def __init__(
                self, 
                *, 
                os_profile: OsProvisionProfile, 
                user_details: Optional[list[UserDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ProvisioningOsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_LINUX = "AzureLinux"
        HCI = "HCI"


    class azure.mgmt.azurestackhci.models.ProvisioningRequest(_Model):
        custom_configuration: Optional[str]
        device_configuration: Optional[TargetDeviceConfiguration]
        onboarding_configuration: Optional[OnboardingConfiguration]
        os_profile: OsProvisionProfile
        target: Union[str, ProvisioningOsType]
        user_details: Optional[list[UserDetails]]

        @overload
        def __init__(
                self, 
                *, 
                custom_configuration: Optional[str] = ..., 
                device_configuration: Optional[TargetDeviceConfiguration] = ..., 
                onboarding_configuration: Optional[OnboardingConfiguration] = ..., 
                os_profile: OsProvisionProfile, 
                target: Union[str, ProvisioningOsType], 
                user_details: Optional[list[UserDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CONNECTED = "Connected"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        DISABLE_IN_PROGRESS = "DisableInProgress"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        MOVING = "Moving"
        NOT_SPECIFIED = "NotSpecified"
        PARTIALLY_CONNECTED = "PartiallyConnected"
        PARTIALLY_SUCCEEDED = "PartiallySucceeded"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.azurestackhci.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.models.Publisher(ProxyResource):
        id: str
        name: str
        properties: Optional[PublisherProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PublisherProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.PublisherProperties(_Model):
        provisioning_state: Optional[str]


    class azure.mgmt.azurestackhci.models.QosPolicyOverrides(_Model):
        bandwidth_percentage_smb: Optional[str]
        priority_value8021_action_cluster: Optional[str]
        priority_value8021_action_smb: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_percentage_smb: Optional[str] = ..., 
                priority_value8021_action_cluster: Optional[str] = ..., 
                priority_value8021_action_smb: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RawCertificateData(_Model):
        certificates: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                certificates: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RdmaCapability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.azurestackhci.models.RebootRequirement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.ReconcileArcSettingsRequest(_Model):
        properties: Optional[ReconcileArcSettingsRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ReconcileArcSettingsRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ReconcileArcSettingsRequestProperties(_Model):
        cluster_nodes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_nodes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ReleaseDeviceRequest(_Model):
        devices: list[str]

        @overload
        def __init__(
                self, 
                *, 
                devices: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RemoteSupportAccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIAGNOSTICS = "Diagnostics"
        DIAGNOSTICS_AND_REPAIR = "DiagnosticsAndRepair"
        NONE = "None"


    class azure.mgmt.azurestackhci.models.RemoteSupportJobNodeSettings(_Model):
        connection_error_message: Optional[str]
        connection_status: Optional[str]
        created_at: Optional[datetime]
        state: Optional[str]
        updated_at: Optional[datetime]


    class azure.mgmt.azurestackhci.models.RemoteSupportJobReportedProperties(_Model):
        deployment_status: Optional[EceActionStatus]
        node_settings: Optional[RemoteSupportJobNodeSettings]
        percent_complete: Optional[int]
        session_details: Optional[list[RemoteSupportSession]]
        validation_status: Optional[EceActionStatus]


    class azure.mgmt.azurestackhci.models.RemoteSupportNodeSettings(_Model):
        arc_resource_id: Optional[str]
        connection_error_message: Optional[str]
        connection_status: Optional[str]
        created_at: Optional[datetime]
        state: Optional[str]
        transcript_location: Optional[str]
        updated_at: Optional[datetime]


    class azure.mgmt.azurestackhci.models.RemoteSupportProperties(_Model):
        access_level: Optional[Union[str, AccessLevel]]
        expiration_time_stamp: Optional[datetime]
        remote_support_node_settings: Optional[list[RemoteSupportNodeSettings]]
        remote_support_provisioning_state: Optional[Union[str, RemoteSupportProvisioningState]]
        remote_support_session_details: Optional[list[PerNodeRemoteSupportSession]]
        remote_support_type: Optional[Union[str, RemoteSupportType]]


    class azure.mgmt.azurestackhci.models.RemoteSupportProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        GRANT_IN_PROGRESS = "GrantInProgress"
        NONE = "None"
        REVOKE_IN_PROGRESS = "RevokeInProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.azurestackhci.models.RemoteSupportRequest(_Model):
        properties: Optional[RemoteSupportRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RemoteSupportRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RemoteSupportRequestProperties(_Model):
        access_level: Optional[Union[str, AccessLevel]]
        expiration_time_stamp: Optional[datetime]
        remote_support_type: Optional[Union[str, RemoteSupportType]]

        @overload
        def __init__(
                self, 
                *, 
                expiration_time_stamp: Optional[datetime] = ..., 
                remote_support_type: Optional[Union[str, RemoteSupportType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RemoteSupportSession(_Model):
        access_level: Optional[Union[str, RemoteSupportAccessLevel]]
        session_end_time: Optional[datetime]
        session_id: Optional[str]
        session_start_time: Optional[datetime]
        transcript_location: Optional[str]


    class azure.mgmt.azurestackhci.models.RemoteSupportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE = "Enable"
        REVOKE = "Revoke"


    class azure.mgmt.azurestackhci.models.RemovePartitionGpuJobProperties(EdgeMachineGpuJobProperties, discriminator='RemovePartition'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.REMOVE_PARTITION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        vm_id: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                vm_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.RepairServerJobServerDetails(_Model):
        server_name: str
        server_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                server_name: str, 
                server_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ReportedProperties(_Model):
        confidential_vm_profile: Optional[ConfidentialVmProfile]
        device_state: Optional[Union[str, DeviceState]]
        extension_profile: Optional[ExtensionProfile]
        last_sync_timestamp: Optional[datetime]


    class azure.mgmt.azurestackhci.models.ResolutionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPT_REPORTED = "AcceptReported"
        APPLY_DESIRED = "ApplyDesired"


    class azure.mgmt.azurestackhci.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.azurestackhci.models.SanAdapterIPConfig(_Model):
        address_prefix: Optional[str]
        name: Optional[str]
        network_adapter_name: Optional[str]
        vlan_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                address_prefix: Optional[str] = ..., 
                name: Optional[str] = ..., 
                network_adapter_name: Optional[str] = ..., 
                vlan_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SanAdapterProperties(_Model):
        bandwidth_percentage_smb: Optional[int]
        jumbo_packet: Optional[int]
        priority_value8021_action_cluster: Optional[int]
        priority_value8021_action_smb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                bandwidth_percentage_smb: Optional[int] = ..., 
                jumbo_packet: Optional[int] = ..., 
                priority_value8021_action_cluster: Optional[int] = ..., 
                priority_value8021_action_smb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SanClusterNetworkConfig(_Model):
        adapter_ip_config: Optional[list[SanAdapterIPConfig]]
        adapter_properties: Optional[SanAdapterProperties]

        @overload
        def __init__(
                self, 
                *, 
                adapter_ip_config: Optional[list[SanAdapterIPConfig]] = ..., 
                adapter_properties: Optional[SanAdapterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SanNetworks(_Model):
        cluster_network_config: Optional[SanClusterNetworkConfig]

        @overload
        def __init__(
                self, 
                *, 
                cluster_network_config: Optional[SanClusterNetworkConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SbeCredentials(_Model):
        ece_secret_name: Optional[str]
        secret_location: Optional[str]
        secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ece_secret_name: Optional[str] = ..., 
                secret_location: Optional[str] = ..., 
                secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SbeDeploymentInfo(_Model):
        family: Optional[str]
        publisher: Optional[str]
        sbe_manifest_creation_date: Optional[datetime]
        sbe_manifest_source: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                family: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sbe_manifest_creation_date: Optional[datetime] = ..., 
                sbe_manifest_source: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SbeDeploymentPackageInfo(_Model):
        code: Optional[str]
        message: Optional[str]
        sbe_manifest: Optional[str]


    class azure.mgmt.azurestackhci.models.SbePartnerInfo(_Model):
        credential_list: Optional[list[SbeCredentials]]
        partner_properties: Optional[list[SbePartnerProperties]]
        sbe_deployment_info: Optional[SbeDeploymentInfo]

        @overload
        def __init__(
                self, 
                *, 
                credential_list: Optional[list[SbeCredentials]] = ..., 
                partner_properties: Optional[list[SbePartnerProperties]] = ..., 
                sbe_deployment_info: Optional[SbeDeploymentInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SbePartnerProperties(_Model):
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


    class azure.mgmt.azurestackhci.models.ScaleUnits(_Model):
        deployment_data: DeploymentData
        sbe_partner_info: Optional[SbePartnerInfo]

        @overload
        def __init__(
                self, 
                *, 
                deployment_data: DeploymentData, 
                sbe_partner_info: Optional[SbePartnerInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SdnIntegration(_Model):
        network_controller: Optional[NetworkController]

        @overload
        def __init__(
                self, 
                *, 
                network_controller: Optional[NetworkController] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SdnIntegrationIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.azurestackhci.models.SdnProperties(_Model):
        sdn_api_address: Optional[str]
        sdn_domain_name: Optional[str]
        sdn_status: Optional[Union[str, SdnStatus]]


    class azure.mgmt.azurestackhci.models.SdnStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT = "KeyVault"
        SSH_PUB_KEY = "SshPubKey"


    class azure.mgmt.azurestackhci.models.SecretsLocationDetails(_Model):
        secrets_location: str
        secrets_type: Union[str, SecretsType]

        @overload
        def __init__(
                self, 
                *, 
                secrets_location: str, 
                secrets_type: Union[str, SecretsType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SecretsLocationsChangeRequest(_Model):
        properties: Optional[list[SecretsLocationDetails]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[list[SecretsLocationDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SecretsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_SECRETS = "BackupSecrets"


    class azure.mgmt.azurestackhci.models.SecurityComplianceStatus(_Model):
        data_at_rest_encrypted: Optional[Union[str, ComplianceStatus]]
        data_in_transit_protected: Optional[Union[str, ComplianceStatus]]
        last_updated: Optional[datetime]
        secured_core_compliance: Optional[Union[str, ComplianceStatus]]
        wdac_compliance: Optional[Union[str, ComplianceStatus]]


    class azure.mgmt.azurestackhci.models.SecurityProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        secured_core_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]]
        security_compliance_status: Optional[SecurityComplianceStatus]
        smb_encryption_for_intra_cluster_traffic_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]]
        wdac_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]]

        @overload
        def __init__(
                self, 
                *, 
                secured_core_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]] = ..., 
                smb_encryption_for_intra_cluster_traffic_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]] = ..., 
                wdac_compliance_assignment: Optional[Union[str, ComplianceAssignmentType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SecuritySetting(ProxyResource):
        id: str
        name: str
        properties: Optional[SecurityProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.ServiceConfiguration(_Model):
        port: int
        service_name: Union[str, ServiceName]

        @overload
        def __init__(
                self, 
                *, 
                port: int, 
                service_name: Union[str, ServiceName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ServiceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAC = "WAC"


    class azure.mgmt.azurestackhci.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRITICAL = "Critical"
        HIDDEN = "Hidden"
        INFORMATIONAL = "Informational"
        WARNING = "Warning"


    class azure.mgmt.azurestackhci.models.SiteDetails(_Model):
        device_configuration: Optional[TargetDeviceConfiguration]
        site_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                device_configuration: Optional[TargetDeviceConfiguration] = ..., 
                site_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.Sku(ProxyResource):
        id: str
        name: str
        properties: Optional[SkuProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SkuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.SkuMappings(_Model):
        catalog_plan_id: Optional[str]
        marketplace_sku_id: Optional[str]
        marketplace_sku_versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                catalog_plan_id: Optional[str] = ..., 
                marketplace_sku_id: Optional[str] = ..., 
                marketplace_sku_versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SkuProperties(_Model):
        content: Optional[str]
        content_version: Optional[str]
        offer_id: Optional[str]
        provisioning_state: Optional[str]
        publisher_id: Optional[str]
        sku_mappings: Optional[list[SkuMappings]]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_version: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                sku_mappings: Optional[list[SkuMappings]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SoftwareAssuranceChangeRequest(_Model):
        properties: Optional[SoftwareAssuranceChangeRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SoftwareAssuranceChangeRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SoftwareAssuranceChangeRequestProperties(_Model):
        software_assurance_intent: Optional[Union[str, SoftwareAssuranceIntent]]

        @overload
        def __init__(
                self, 
                *, 
                software_assurance_intent: Optional[Union[str, SoftwareAssuranceIntent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SoftwareAssuranceIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.azurestackhci.models.SoftwareAssuranceProperties(_Model):
        last_updated: Optional[datetime]
        software_assurance_intent: Optional[Union[str, SoftwareAssuranceIntent]]
        software_assurance_status: Optional[Union[str, SoftwareAssuranceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                software_assurance_intent: Optional[Union[str, SoftwareAssuranceIntent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SoftwareAssuranceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.azurestackhci.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDITIONAL_CONTENT_REQUIRED = "AdditionalContentRequired"
        DOWNLOADING = "Downloading"
        DOWNLOAD_FAILED = "DownloadFailed"
        HAS_PREREQUISITE = "HasPrerequisite"
        HEALTH_CHECKING = "HealthChecking"
        HEALTH_CHECK_EXPIRED = "HealthCheckExpired"
        HEALTH_CHECK_FAILED = "HealthCheckFailed"
        INSTALLATION_FAILED = "InstallationFailed"
        INSTALLED = "Installed"
        INSTALLING = "Installing"
        INVALID = "Invalid"
        NOT_APPLICABLE_BECAUSE_ANOTHER_UPDATE_IS_IN_PROGRESS = "NotApplicableBecauseAnotherUpdateIsInProgress"
        OBSOLETE = "Obsolete"
        PENDING_OEM_VALIDATION = "PendingOEMValidation"
        PREPARATION_FAILED = "PreparationFailed"
        PREPARING = "Preparing"
        READY = "Ready"
        READY_TO_INSTALL = "ReadyToInstall"
        RECALLED = "Recalled"
        SCAN_FAILED = "ScanFailed"
        SCAN_IN_PROGRESS = "ScanInProgress"


    class azure.mgmt.azurestackhci.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED_RECENTLY = "ConnectedRecently"
        DEPLOYMENT_FAILED = "DeploymentFailed"
        DEPLOYMENT_IN_PROGRESS = "DeploymentInProgress"
        DEPLOYMENT_SUCCESS = "DeploymentSuccess"
        DISCONNECTED = "Disconnected"
        ERROR = "Error"
        NOT_CONNECTED_RECENTLY = "NotConnectedRecently"
        NOT_SPECIFIED = "NotSpecified"
        NOT_YET_REGISTERED = "NotYetRegistered"
        VALIDATION_FAILED = "ValidationFailed"
        VALIDATION_IN_PROGRESS = "ValidationInProgress"
        VALIDATION_SUCCESS = "ValidationSuccess"


    class azure.mgmt.azurestackhci.models.StatusLevelTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.azurestackhci.models.Step(_Model):
        description: Optional[str]
        end_time_utc: Optional[datetime]
        error_message: Optional[str]
        expected_execution_time: Optional[str]
        last_updated_time_utc: Optional[datetime]
        name: Optional[str]
        start_time_utc: Optional[datetime]
        status: Optional[str]
        steps: Optional[list[Step]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                end_time_utc: Optional[datetime] = ..., 
                error_message: Optional[str] = ..., 
                expected_execution_time: Optional[str] = ..., 
                last_updated_time_utc: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                start_time_utc: Optional[datetime] = ..., 
                status: Optional[str] = ..., 
                steps: Optional[list[Step]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.Storage(_Model):
        configuration_mode: Optional[str]
        s2_d: Optional[StorageS2dConfig]
        san: Optional[StorageSanConfig]
        storage_type: Optional[Union[str, StorageType]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_mode: Optional[str] = ..., 
                s2_d: Optional[StorageS2dConfig] = ..., 
                san: Optional[StorageSanConfig] = ..., 
                storage_type: Optional[Union[str, StorageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.StorageConfiguration(_Model):
        partition_size: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                partition_size: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.StorageProfile(_Model):
        disks: Optional[list[EdgeMachineDiskInfo]]
        poolable_disks_count: Optional[int]


    class azure.mgmt.azurestackhci.models.StorageS2dConfig(_Model):
        overprovisioning_ratio: Optional[Union[str, OverprovisioningRatio]]
        volume_type: Optional[Union[str, VolumeType]]

        @overload
        def __init__(
                self, 
                *, 
                overprovisioning_ratio: Optional[Union[str, OverprovisioningRatio]] = ..., 
                volume_type: Optional[Union[str, VolumeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.StorageSanConfig(_Model):
        infra_perf_lun_id: Optional[str]
        infra_vol_lun_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                infra_perf_lun_id: Optional[str] = ..., 
                infra_vol_lun_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        S2_D = "S2D"
        SAN = "SAN"
        SANS2_D = "SANS2D"


    class azure.mgmt.azurestackhci.models.SwitchDetail(_Model):
        extensions: Optional[list[SwitchExtension]]
        switch_name: Optional[str]
        switch_type: Optional[str]


    class azure.mgmt.azurestackhci.models.SwitchExtension(_Model):
        extension_enabled: Optional[bool]
        extension_name: Optional[str]
        switch_id: Optional[str]


    class azure.mgmt.azurestackhci.models.SwitchModeGpuJobProperties(EdgeMachineGpuJobProperties, discriminator='SwitchMode'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.SWITCH_MODE]
        mode: Union[str, GpuMode]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                mode: Union[str, GpuMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SyncConfigurationJobProperties(EdgeMachineDiskJobProperties, discriminator='SyncConfiguration'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[DiskJobType.SYNC_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        resolution_strategy: Union[str, ResolutionStrategy]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                resolution_strategy: Union[str, ResolutionStrategy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SyncConfigurationNetworkAdapterJobProperties(EdgeMachineNetworkAdapterJobProperties, discriminator='SyncConfiguration'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.SYNC_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        resolution_strategy: Union[str, ResolutionStrategy]
        start_time_utc: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                resolution_strategy: Union[str, ResolutionStrategy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.SystemData(_Model):
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


    class azure.mgmt.azurestackhci.models.TargetDeviceConfiguration(_Model):
        host_name: Optional[str]
        network: Optional[NetworkConfiguration]
        storage: Optional[StorageConfiguration]
        time: Optional[TimeConfiguration]
        web_proxy: Optional[WebProxyConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                network: Optional[NetworkConfiguration] = ..., 
                storage: Optional[StorageConfiguration] = ..., 
                time: Optional[TimeConfiguration] = ..., 
                web_proxy: Optional[WebProxyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.TimeConfiguration(_Model):
        primary_time_server: Optional[str]
        secondary_time_server: Optional[str]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                primary_time_server: Optional[str] = ..., 
                secondary_time_server: Optional[str] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.TrackedResource(Resource):
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


    class azure.mgmt.azurestackhci.models.Update(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[UpdateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[UpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateContent(ProxyResource):
        id: str
        name: str
        properties: Optional[UpdateContentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpdateContentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateContentProperties(_Model):
        update_payloads: list[ContentPayload]

        @overload
        def __init__(
                self, 
                *, 
                update_payloads: list[ContentPayload]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdatePrerequisite(_Model):
        package_name: Optional[str]
        update_type: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                package_name: Optional[str] = ..., 
                update_type: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateProperties(_Model):
        additional_properties: Optional[str]
        availability_type: Optional[Union[str, AvailabilityType]]
        component_versions: Optional[list[PackageVersionInfo]]
        description: Optional[str]
        display_name: Optional[str]
        health_check_date: Optional[datetime]
        health_check_result: Optional[list[PrecheckResult]]
        health_state: Optional[Union[str, HealthState]]
        installed_date: Optional[datetime]
        min_sbe_version_required: Optional[str]
        package_path: Optional[str]
        package_size_in_mb: Optional[float]
        package_type: Optional[str]
        prerequisites: Optional[list[UpdatePrerequisite]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        publisher: Optional[str]
        reboot_required: Optional[Union[str, RebootRequirement]]
        release_link: Optional[str]
        state: Optional[Union[str, State]]
        update_state_properties: Optional[UpdateStateProperties]
        version: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                additional_properties: Optional[str] = ..., 
                availability_type: Optional[Union[str, AvailabilityType]] = ..., 
                component_versions: Optional[list[PackageVersionInfo]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                health_check_date: Optional[datetime] = ..., 
                health_check_result: Optional[list[PrecheckResult]] = ..., 
                health_state: Optional[Union[str, HealthState]] = ..., 
                installed_date: Optional[datetime] = ..., 
                min_sbe_version_required: Optional[str] = ..., 
                package_path: Optional[str] = ..., 
                package_size_in_mb: Optional[float] = ..., 
                package_type: Optional[str] = ..., 
                prerequisites: Optional[list[UpdatePrerequisite]] = ..., 
                publisher: Optional[str] = ..., 
                reboot_required: Optional[Union[str, RebootRequirement]] = ..., 
                release_link: Optional[str] = ..., 
                state: Optional[Union[str, State]] = ..., 
                update_state_properties: Optional[UpdateStateProperties] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateRun(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[UpdateRunProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[UpdateRunProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateRunProperties(_Model):
        duration: Optional[str]
        last_updated_time: Optional[datetime]
        progress: Optional[Step]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, UpdateRunPropertiesState]]
        time_started: Optional[datetime]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[str] = ..., 
                last_updated_time: Optional[datetime] = ..., 
                progress: Optional[Step] = ..., 
                state: Optional[Union[str, UpdateRunPropertiesState]] = ..., 
                time_started: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateRunPropertiesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.azurestackhci.models.UpdateStateProperties(_Model):
        notify_message: Optional[str]
        progress_percentage: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                notify_message: Optional[str] = ..., 
                progress_percentage: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateSummaries(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[UpdateSummariesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[UpdateSummariesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateSummariesProperties(_Model):
        current_oem_version: Optional[str]
        current_sbe_version: Optional[str]
        current_version: Optional[str]
        hardware_model: Optional[str]
        health_check_date: Optional[datetime]
        health_check_result: Optional[list[PrecheckResult]]
        health_state: Optional[Union[str, HealthState]]
        last_checked: Optional[datetime]
        last_updated: Optional[datetime]
        oem_family: Optional[str]
        package_versions: Optional[list[PackageVersionInfo]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Optional[Union[str, UpdateSummariesPropertiesState]]

        @overload
        def __init__(
                self, 
                *, 
                current_oem_version: Optional[str] = ..., 
                current_sbe_version: Optional[str] = ..., 
                current_version: Optional[str] = ..., 
                hardware_model: Optional[str] = ..., 
                health_check_date: Optional[datetime] = ..., 
                health_check_result: Optional[list[PrecheckResult]] = ..., 
                health_state: Optional[Union[str, HealthState]] = ..., 
                last_checked: Optional[datetime] = ..., 
                last_updated: Optional[datetime] = ..., 
                oem_family: Optional[str] = ..., 
                package_versions: Optional[list[PackageVersionInfo]] = ..., 
                state: Optional[Union[str, UpdateSummariesPropertiesState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UpdateSummariesPropertiesState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLIED_SUCCESSFULLY = "AppliedSuccessfully"
        NEEDS_ATTENTION = "NeedsAttention"
        PREPARATION_FAILED = "PreparationFailed"
        PREPARATION_IN_PROGRESS = "PreparationInProgress"
        UNKNOWN = "Unknown"
        UPDATE_AVAILABLE = "UpdateAvailable"
        UPDATE_FAILED = "UpdateFailed"
        UPDATE_IN_PROGRESS = "UpdateInProgress"


    class azure.mgmt.azurestackhci.models.UploadCertificateRequest(_Model):
        properties: Optional[RawCertificateData]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RawCertificateData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.azurestackhci.models.UserDetails(_Model):
        secret_location: Optional[str]
        secret_type: Union[str, SecretType]
        ssh_pub_key: Optional[list[str]]
        user_name: str

        @overload
        def __init__(
                self, 
                *, 
                secret_location: Optional[str] = ..., 
                secret_type: Union[str, SecretType], 
                ssh_pub_key: Optional[list[str]] = ..., 
                user_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidateOwnershipVouchersRequest(_Model):
        ownership_voucher_details: list[OwnershipVoucherDetails]

        @overload
        def __init__(
                self, 
                *, 
                ownership_voucher_details: list[OwnershipVoucherDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidateOwnershipVouchersResponse(_Model):
        ownership_voucher_validation_details: list[OwnershipVoucherValidationDetails]

        @overload
        def __init__(
                self, 
                *, 
                ownership_voucher_validation_details: list[OwnershipVoucherValidationDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidateRequest(_Model):
        additional_info: Optional[str]
        edge_device_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[str] = ..., 
                edge_device_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidateResponse(_Model):
        status: Optional[str]


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipe(ProxyResource):
        id: str
        name: str
        properties: Optional[ValidatedSolutionRecipeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ValidatedSolutionRecipeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeCapabilities(_Model):
        cluster_capabilities: list[ValidatedSolutionRecipeCapability]
        node_capabilities: list[ValidatedSolutionRecipeCapability]

        @overload
        def __init__(
                self, 
                *, 
                cluster_capabilities: list[ValidatedSolutionRecipeCapability], 
                node_capabilities: list[ValidatedSolutionRecipeCapability]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeCapability(_Model):
        capability_name: str

        @overload
        def __init__(
                self, 
                *, 
                capability_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeComponent(_Model):
        install_order: Optional[int]
        metadata: Optional[ValidatedSolutionRecipeComponentMetadata]
        name: str
        payloads: Optional[list[ValidatedSolutionRecipeComponentPayload]]
        required_version: Optional[str]
        tags: list[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                install_order: Optional[int] = ..., 
                metadata: Optional[ValidatedSolutionRecipeComponentMetadata] = ..., 
                name: str, 
                payloads: Optional[list[ValidatedSolutionRecipeComponentPayload]] = ..., 
                required_version: Optional[str] = ..., 
                tags: list[str], 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeComponentMetadata(_Model):
        catalog: Optional[str]
        enable_automatic_upgrade: Optional[bool]
        expected_hash: Optional[str]
        extension_type: Optional[str]
        lcm_update: Optional[bool]
        link: Optional[str]
        name: Optional[str]
        preview_source: Optional[str]
        publisher: Optional[str]
        release_train: Optional[str]
        ring: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                catalog: Optional[str] = ..., 
                enable_automatic_upgrade: Optional[bool] = ..., 
                expected_hash: Optional[str] = ..., 
                extension_type: Optional[str] = ..., 
                lcm_update: Optional[bool] = ..., 
                link: Optional[str] = ..., 
                name: Optional[str] = ..., 
                preview_source: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                ring: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeComponentPayload(_Model):
        file_name: str
        hash: str
        identifier: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                file_name: str, 
                hash: str, 
                identifier: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeContent(_Model):
        capabilities: Optional[ValidatedSolutionRecipeCapabilities]
        components: list[ValidatedSolutionRecipeComponent]
        info: ValidatedSolutionRecipeInfo

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[ValidatedSolutionRecipeCapabilities] = ..., 
                components: list[ValidatedSolutionRecipeComponent], 
                info: ValidatedSolutionRecipeInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeInfo(_Model):
        solution_type: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                solution_type: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ValidatedSolutionRecipeProperties(_Model):
        recipe_content: ValidatedSolutionRecipeContent
        signature: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                recipe_content: ValidatedSolutionRecipeContent, 
                signature: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.VmConnectJobDetails(_Model):
        node_name: Optional[str]
        vm_name: str
        vm_resource_group_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                node_name: Optional[str] = ..., 
                vm_name: str, 
                vm_resource_group_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.VmConnectProvisionJobProperties(ClusterJobProperties, discriminator='VmConnectProvision'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.VM_CONNECT_PROVISION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        vm_connect_provision_job_details: list[VmConnectJobDetails]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                vm_connect_provision_job_details: list[VmConnectJobDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.VmConnectRemoveJobProperties(ClusterJobProperties, discriminator='VmConnectRemove'):
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: datetime
        job_id: str
        job_type: Literal[HciJobType.VM_CONNECT_REMOVE]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: datetime
        status: Union[str, JobStatus]
        vm_connect_remove_job_details: list[VmConnectJobDetails]

        @overload
        def __init__(
                self, 
                *, 
                deployment_mode: Optional[Union[str, DeploymentMode]] = ..., 
                vm_connect_remove_job_details: list[VmConnectJobDetails]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.VolumeConfiguration(_Model):
        reserved: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                reserved: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.VolumeReportedProperties(_Model):
        file_system: Optional[str]
        is_boot: Optional[bool]
        name: Optional[str]
        offset_in_bytes: Optional[int]
        parent_disk_id: Optional[str]
        partition_id: Optional[str]
        path: Optional[str]
        size_in_bytes: Optional[str]
        size_remaining_in_bytes: Optional[str]


    class azure.mgmt.azurestackhci.models.VolumeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED = "Fixed"
        THIN_PROVISIONED = "ThinProvisioned"


    class azure.mgmt.azurestackhci.models.WebProxyConfiguration(_Model):
        bypass_list: Optional[list[str]]
        connection_uri: Optional[str]
        port: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bypass_list: Optional[list[str]] = ..., 
                connection_uri: Optional[str] = ..., 
                port: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.WifiConfigurationDesiredProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        eap_method: Optional[Union[str, EAPMethod]]
        ssid: Optional[str]
        username: Optional[str]
        wifi_secret: Optional[WifiSecret]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                eap_method: Optional[Union[str, EAPMethod]] = ..., 
                ssid: Optional[str] = ..., 
                username: Optional[str] = ..., 
                wifi_secret: Optional[WifiSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.WifiConfigurationReportedProperties(_Model):
        authentication_type: Optional[Union[str, AuthenticationType]]
        connection_state: Optional[Union[str, ConnectionState]]
        eap_method: Optional[Union[str, EAPMethod]]
        last_successful_connection_timestamp: Optional[str]
        signal_strength: Optional[int]
        ssid: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authentication_type: Optional[Union[str, AuthenticationType]] = ..., 
                eap_method: Optional[Union[str, EAPMethod]] = ..., 
                ssid: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.WifiSecret(_Model):
        secret_location: Optional[str]
        secret_name: Optional[str]
        secret_type: Optional[Union[str, WifiSecretType]]

        @overload
        def __init__(
                self, 
                *, 
                secret_location: Optional[str] = ..., 
                secret_name: Optional[str] = ..., 
                secret_type: Optional[Union[str, WifiSecretType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.WifiSecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WI_FI_CA_CERTIFICATE = "WiFiCACertificate"
        WI_FI_CERTIFICATE = "WiFiCertificate"
        WI_FI_PASSWORD = "WiFiPassword"


    class azure.mgmt.azurestackhci.models.WindowsServerSubscription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.azurestackhci.models.WitnessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOUD = "Cloud"
        FILE_SHARE = "FileShare"


    class azure.mgmt.azurestackhci.models.WorkloadDetails(_Model):
        slot_location: Optional[str]
        workload_id: Optional[str]
        workload_name: Optional[str]
        workload_status: Optional[str]
        workload_type: Optional[str]


namespace azure.mgmt.azurestackhci.operations

    class azure.mgmt.azurestackhci.operations.ArcSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> LROPoller[ArcIdentityResponse]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_initialize_disable_process(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: ReconcileArcSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcSetting]: ...

        @overload
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: ReconcileArcSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcSetting]: ...

        @overload
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                reconcile_arc_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcSetting]: ...

        @distributed_trace
        def consent_and_install_default_extensions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @distributed_trace
        def generate_password(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> PasswordCredential: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> ArcSetting: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ArcSetting]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSettingsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: ArcSettingsPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                arc_setting: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArcSetting: ...


    class azure.mgmt.azurestackhci.operations.ClusterJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: ClusterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: ClusterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> ClusterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ClusterJob]: ...


    class azure.mgmt.azurestackhci.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: ChangeRingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: ChangeRingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_change_ring(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                change_ring_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: RemoteSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: RemoteSupportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_configure_remote_support(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                remote_support_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_create_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[ClusterIdentityResponse]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: SoftwareAssuranceChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: SoftwareAssuranceChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_extend_software_assurance_benefit(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                software_assurance_change_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: LogCollectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: LogCollectionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_trigger_log_collection(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_collection_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: SecretsLocationsChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: SecretsLocationsChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update_secrets_locations(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: UploadCertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upload_certificate(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                upload_certificate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Cluster]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: ClusterPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Cluster: ...


    class azure.mgmt.azurestackhci.operations.DeploymentSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: DeploymentSetting, 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: DeploymentSetting, 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                deployment_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DeploymentSetting]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                deployment_settings_name: str = "default", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                deployment_settings_name: str = "default", 
                **kwargs: Any
            ) -> DeploymentSetting: ...

        @distributed_trace
        def list_by_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DeploymentSetting]: ...


    class azure.mgmt.azurestackhci.operations.DevicePoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ClaimDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ClaimDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_claim_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: DevicePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: DevicePool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ReleaseDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: ReleaseDeviceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_release_devices(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: DevicePoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: DevicePoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> DevicePool: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DevicePool]: ...


    class azure.mgmt.azurestackhci.operations.EdgeDeviceJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: EdgeDeviceJob, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDeviceJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: EdgeDeviceJob, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDeviceJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDeviceJob]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                jobs_name: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> EdgeDeviceJob: ...

        @distributed_trace
        def list_by_edge_device(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> ItemPaged[EdgeDeviceJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: EdgeDevice, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDevice]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: EdgeDevice, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDevice]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                resource: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeDevice]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: ValidateRequest, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateResponse]: ...

        @overload
        def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: ValidateRequest, 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateResponse]: ...

        @overload
        def begin_validate(
                self, 
                resource_uri: str, 
                validate_request: IO[bytes], 
                edge_device_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ValidateResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                edge_device_name: str = "default", 
                **kwargs: Any
            ) -> EdgeDevice: ...

        @distributed_trace
        def list(
                self, 
                resource_uri: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeDevice]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineDiskJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: EdgeMachineDiskJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: EdgeMachineDiskJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'job_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDiskJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineDiskJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineDiskPrivilegedJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: EdgeMachineDiskPrivilegedJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: EdgeMachineDiskPrivilegedJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDiskPrivilegedJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'privileged_job_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'privileged_job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                privileged_job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDiskPrivilegedJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineDiskPrivilegedJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineDisksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: EdgeMachineDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDisk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: EdgeMachineDisk, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDisk]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineDisk]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'disk_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                disk_name: str, 
                **kwargs: Any
            ) -> EdgeMachineDisk: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineDisk]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineGpuJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: EdgeMachineGpuJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpuJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: EdgeMachineGpuJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpuJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpuJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineGpuJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineGpuJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineGpusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: EdgeMachineGpu, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpu]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: EdgeMachineGpu, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpu]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineGpu]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'gpu_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                gpu_name: str, 
                **kwargs: Any
            ) -> EdgeMachineGpu: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineGpu]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: EdgeMachineJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: EdgeMachineJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineNetworkAdapterJobsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: EdgeMachineNetworkAdapterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineNetworkAdapterJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: EdgeMachineNetworkAdapterJob, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineNetworkAdapterJob]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineNetworkAdapterJob]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'job_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'job_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                job_name: str, 
                **kwargs: Any
            ) -> EdgeMachineNetworkAdapterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineNetworkAdapterJob]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineNetworkAdaptersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'network_adapter_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                network_adapter_name: str, 
                **kwargs: Any
            ) -> EdgeMachineNetworkAdapter: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineNetworkAdapter]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: EdgeMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineUpdate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: EdgeMachineUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineUpdate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineUpdate]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'default']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'default', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                default: str, 
                **kwargs: Any
            ) -> EdgeMachineUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineUpdate]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachineVolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: EdgeMachineVolume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineVolume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: EdgeMachineVolume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineVolume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineVolume]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'volume_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'volume_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> EdgeMachineVolume: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineVolume]: ...


    class azure.mgmt.azurestackhci.operations.EdgeMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: EdgeMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: EdgeMachine, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name']}, api_versions_list=['2026-05-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: EdgeMachinePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: EdgeMachinePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachine]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: EdgeMachineValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineValidateResponse]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: EdgeMachineValidateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineValidateResponse]: ...

        @overload
        def begin_validate(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EdgeMachineValidateResponse]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> EdgeMachine: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachine]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EdgeMachine]: ...


    class azure.mgmt.azurestackhci.operations.ExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: ExtensionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: ExtensionPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: ExtensionUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: ExtensionUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                extension_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> Extension: ...

        @distributed_trace
        def list_by_arc_setting(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                arc_setting_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Extension]: ...


    class azure.mgmt.azurestackhci.operations.KubernetesVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[KubernetesVersion]: ...


    class azure.mgmt.azurestackhci.operations.OffersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                offer_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Offer: ...

        @distributed_trace
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Offer]: ...

        @distributed_trace
        def list_by_publisher(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Offer]: ...


    class azure.mgmt.azurestackhci.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.azurestackhci.operations.OsImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'os_image_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                location: str, 
                os_image_name: str, 
                **kwargs: Any
            ) -> OsImage: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[OsImage]: ...


    class azure.mgmt.azurestackhci.operations.OwnershipVouchersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidateOwnershipVouchersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: ValidateOwnershipVouchersRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...

        @overload
        def validate(
                self, 
                resource_group_name: str, 
                location: str, 
                validation_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateOwnershipVouchersResponse: ...


    class azure.mgmt.azurestackhci.operations.PlatformUpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'platform_update_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                location: str, 
                platform_update_name: str, 
                **kwargs: Any
            ) -> PlatformUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[PlatformUpdate]: ...


    class azure.mgmt.azurestackhci.operations.PublishersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'publisher_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list_by_cluster(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Publisher]: ...


    class azure.mgmt.azurestackhci.operations.SecuritySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: SecuritySetting, 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecuritySetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: SecuritySetting, 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecuritySetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                security_settings_name: str = "default", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecuritySetting]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                security_settings_name: str = "default", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                security_settings_name: str = "default", 
                **kwargs: Any
            ) -> SecuritySetting: ...

        @distributed_trace
        def list_by_clusters(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecuritySetting]: ...


    class azure.mgmt.azurestackhci.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                offer_name: str, 
                sku_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> Sku: ...

        @distributed_trace
        def list_by_offer(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                offer_name: str, 
                *, 
                expand: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Sku]: ...


    class azure.mgmt.azurestackhci.operations.UpdateContentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'update_content_name', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def get(
                self, 
                location: str, 
                update_content_name: str, 
                **kwargs: Any
            ) -> UpdateContent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-01-preview', params_added_on={'2026-05-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-01-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[UpdateContent]: ...


    class azure.mgmt.azurestackhci.operations.UpdateRunsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                **kwargs: Any
            ) -> UpdateRun: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UpdateRun]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: UpdateRun, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_run_name: str, 
                update_runs_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateRun: ...


    class azure.mgmt.azurestackhci.operations.UpdateSummariesOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-30', '2026-05-01-preview'])
        def begin_check_health(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CheckUpdatesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: CheckUpdatesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_check_updates(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.azurestackhci.operations.UpdateSummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UpdateSummaries]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: UpdateSummaries, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: UpdateSummaries, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_location_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateSummaries: ...


    class azure.mgmt.azurestackhci.operations.UpdatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_post(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-30', params_added_on={'2026-04-30': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'update_name']}, api_versions_list=['2026-04-30', '2026-05-01-preview'])
        def begin_prepare(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                **kwargs: Any
            ) -> Update: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Update]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: Update, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: Update, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                update_name: str, 
                update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Update: ...


    class azure.mgmt.azurestackhci.operations.ValidatedSolutionRecipesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                validated_solution_recipe_name: str, 
                **kwargs: Any
            ) -> ValidatedSolutionRecipe: ...

        @distributed_trace
        def list_by_subscription_location_resource(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ValidatedSolutionRecipe]: ...


namespace azure.mgmt.azurestackhci.types

    class azure.mgmt.azurestackhci.types.AddServerJobServerDetails(TypedDict, total=False):
        key "hostIpv4Address": Required[str]
        key "localAvailabilityZoneName": str
        key "serverName": Required[str]
        key "serverResourceId": Required[str]
        host_ipv4_address: str
        local_availability_zone_name: str
        server_name: str
        server_resource_id: str


    class azure.mgmt.azurestackhci.types.ApplyConfigurationNetworkAdapterJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[NetworkAdapterJobType.APPLY_CONFIGURATION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('NetworkAdapterJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "targetConfiguration": Required[NetworkAdapterConfiguration]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.APPLY_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        target_configuration: NetworkAdapterConfiguration


    class azure.mgmt.azurestackhci.types.ArcConnectivityProperties(TypedDict, total=False):
        key "enabled": bool
        enabled: bool
        serviceConfigurations: list[ServiceConfiguration]
        service_configurations: list[ServiceConfiguration]


    class azure.mgmt.azurestackhci.types.ArcSetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ArcSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ArcSettingProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.ArcSettingProperties(TypedDict, total=False):
        key "aggregateState": Union[str, ArcSettingAggregateState]
        key "arcApplicationClientId": str
        key "arcApplicationObjectId": str
        key "arcApplicationTenantId": str
        key "arcInstanceResourceGroup": str
        key "arcServicePrincipalObjectId": str
        key "connectivityProperties": ForwardRef('ArcConnectivityProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        aggregate_state: Union[str, ArcSettingAggregateState]
        arc_application_client_id: str
        arc_application_object_id: str
        arc_application_tenant_id: str
        arc_instance_resource_group: str
        arc_service_principal_object_id: str
        connectivity_properties: ArcConnectivityProperties
        defaultExtensions: list[DefaultExtensionDetails]
        default_extensions: list[DefaultExtensionDetails]
        perNodeDetails: list[PerNodeState]
        per_node_details: list[PerNodeState]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.azurestackhci.types.ArcSettingsPatch(TypedDict, total=False):
        key "properties": ForwardRef('ArcSettingsPatchProperties', module='types')
        properties: ArcSettingsPatchProperties
        tags: dict[str, str]


    class azure.mgmt.azurestackhci.types.ArcSettingsPatchProperties(TypedDict, total=False):
        key "connectivityProperties": ForwardRef('ArcConnectivityProperties', module='types')
        connectivity_properties: ArcConnectivityProperties


    class azure.mgmt.azurestackhci.types.AssemblyInfo(TypedDict, total=False):
        key "packageVersion": str
        package_version: str
        payload: list[AssemblyInfoPayload]


    class azure.mgmt.azurestackhci.types.AssemblyInfoPayload(TypedDict, total=False):
        key "fileName": str
        key "hash": str
        key "identifier": str
        key "url": str
        file_name: str
        hash: str
        identifier: str
        url: str


    class azure.mgmt.azurestackhci.types.AssignPartitionGpuJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "gpuId": str
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineGpuJobType.ASSIGN_PARTITION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "vmId": Required[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.ASSIGN_PARTITION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        vm_id: str


    class azure.mgmt.azurestackhci.types.ChangeRingRequest(TypedDict, total=False):
        key "properties": Required[ChangeRingRequestProperties]
        properties: ChangeRingRequestProperties


    class azure.mgmt.azurestackhci.types.ChangeRingRequestProperties(TypedDict, total=False):
        key "targetRing": Required[str]
        target_ring: str


    class azure.mgmt.azurestackhci.types.CheckUpdatesRequest(TypedDict, total=False):
        key "updateName": str
        update_name: str


    class azure.mgmt.azurestackhci.types.ClaimDeviceRequest(TypedDict, total=False):
        key "claimedBy": str
        key "devices": Required[list[str]]
        claimed_by: str
        devices: list[str]


    class azure.mgmt.azurestackhci.types.Cluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: ClusterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhci.types.ClusterBillingProperties(TypedDict, total=False):
        key "nextBillingModel": ForwardRef('NextBillingModel', module='types')
        next_billing_model: NextBillingModel


    class azure.mgmt.azurestackhci.types.ClusterDesiredProperties(TypedDict, total=False):
        key "diagnosticLevel": Union[str, DiagnosticLevel]
        key "windowsServerSubscription": Union[str, WindowsServerSubscription]
        diagnostic_level: Union[str, DiagnosticLevel]
        windows_server_subscription: Union[str, WindowsServerSubscription]


    class azure.mgmt.azurestackhci.types.ClusterJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ClusterJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ClusterJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.ClusterNode(TypedDict, total=False):
        key "coreCount": float
        key "ehcResourceId": str
        key "id": float
        key "lastLicensingTimestamp": str
        key "manufacturer": str
        key "memoryInGiB": float
        key "model": str
        key "name": str
        key "nodeType": Union[str, ClusterNodeType]
        key "oemActivation": Union[str, OemActivation]
        key "osDisplayVersion": str
        key "osName": str
        key "osVersion": str
        key "serialNumber": str
        key "windowsServerSubscription": Union[str, WindowsServerSubscription]
        core_count: float
        ehc_resource_id: str
        id: float
        last_licensing_timestamp: str
        manufacturer: str
        memory_in_gi_b: float
        model: str
        name: str
        node_type: Union[str, ClusterNodeType]
        oem_activation: Union[str, OemActivation]
        os_display_version: str
        os_name: str
        os_version: str
        serial_number: str
        windows_server_subscription: Union[str, WindowsServerSubscription]


    class azure.mgmt.azurestackhci.types.ClusterPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ClusterPatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: ClusterPatchProperties
        tags: dict[str, str]


    class azure.mgmt.azurestackhci.types.ClusterPatchProperties(TypedDict, total=False):
        key "aadClientId": str
        key "aadTenantId": str
        key "cloudManagementEndpoint": str
        key "desiredProperties": ForwardRef('ClusterDesiredProperties', module='types')
        aad_client_id: str
        aad_tenant_id: str
        cloud_management_endpoint: str
        desired_properties: ClusterDesiredProperties


    class azure.mgmt.azurestackhci.types.ClusterProperties(TypedDict, total=False):
        key "aadApplicationObjectId": str
        key "aadClientId": str
        key "aadServicePrincipalObjectId": str
        key "aadTenantId": str
        key "billingModel": str
        key "billingProperties": ForwardRef('ClusterBillingProperties', module='types')
        key "cloudId": str
        key "cloudManagementEndpoint": str
        key "clusterPattern": Union[str, ClusterPattern]
        key "confidentialVmProperties": ForwardRef('ConfidentialVmProperties', module='types')
        key "connectivityStatus": Union[str, ConnectivityStatus]
        key "desiredProperties": ForwardRef('ClusterDesiredProperties', module='types')
        key "identityProvider": Union[str, IdentityProvider]
        key "isManagementCluster": bool
        key "isolatedVmAttestationConfiguration": ForwardRef('IsolatedVmAttestationConfiguration', module='types')
        key "lastBillingTimestamp": str
        key "lastSyncTimestamp": str
        key "logCollectionProperties": ForwardRef('LogCollectionProperties', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "registrationTimestamp": str
        key "remoteSupportProperties": ForwardRef('RemoteSupportProperties', module='types')
        key "reportedProperties": ForwardRef('ClusterReportedProperties', module='types')
        key "resourceProviderObjectId": str
        key "ring": str
        key "sdnProperties": ForwardRef('ClusterSdnProperties', module='types')
        key "serviceEndpoint": str
        key "softwareAssuranceProperties": ForwardRef('SoftwareAssuranceProperties', module='types')
        key "status": Union[str, Status]
        key "storageType": Union[str, StorageType]
        key "trialDaysRemaining": float
        aad_application_object_id: str
        aad_client_id: str
        aad_service_principal_object_id: str
        aad_tenant_id: str
        billing_model: str
        billing_properties: ClusterBillingProperties
        cloud_id: str
        cloud_management_endpoint: str
        cluster_pattern: Union[str, ClusterPattern]
        confidential_vm_properties: ConfidentialVmProperties
        connectivity_status: Union[str, ConnectivityStatus]
        desired_properties: ClusterDesiredProperties
        identity_provider: Union[str, IdentityProvider]
        is_management_cluster: bool
        isolated_vm_attestation_configuration: IsolatedVmAttestationConfiguration
        last_billing_timestamp: str
        last_sync_timestamp: str
        localAvailabilityZones: list[LocalAvailabilityZones]
        local_availability_zones: list[LocalAvailabilityZones]
        log_collection_properties: LogCollectionProperties
        provisioning_state: Union[str, ProvisioningState]
        registration_timestamp: str
        remote_support_properties: RemoteSupportProperties
        reported_properties: ClusterReportedProperties
        resource_provider_object_id: str
        ring: str
        sdn_properties: ClusterSdnProperties
        secretsLocations: list[SecretsLocationDetails]
        secrets_locations: list[SecretsLocationDetails]
        service_endpoint: str
        software_assurance_properties: SoftwareAssuranceProperties
        status: Union[str, Status]
        storage_type: Union[str, StorageType]
        trial_days_remaining: float


    class azure.mgmt.azurestackhci.types.ClusterReportedProperties(TypedDict, total=False):
        key "clusterId": str
        key "clusterName": str
        key "clusterType": Union[str, ClusterNodeType]
        key "clusterVersion": str
        key "diagnosticLevel": Union[str, DiagnosticLevel]
        key "hardwareClass": Union[str, HardwareClass]
        key "imdsAttestation": Union[str, ImdsAttestation]
        key "lastUpdated": str
        key "manufacturer": str
        key "msiExpirationTimeStamp": str
        key "oemActivation": Union[str, OemActivation]
        cluster_id: str
        cluster_name: str
        cluster_type: Union[str, ClusterNodeType]
        cluster_version: str
        diagnostic_level: Union[str, DiagnosticLevel]
        hardware_class: Union[str, HardwareClass]
        imds_attestation: Union[str, ImdsAttestation]
        last_updated: str
        manufacturer: str
        msi_expiration_time_stamp: str
        nodes: list[ClusterNode]
        oem_activation: Union[str, OemActivation]
        supportedCapabilities: list[str]
        supported_capabilities: list[str]


    class azure.mgmt.azurestackhci.types.ClusterSdnProperties(TypedDict, total=False):
        key "sdnApiAddress": str
        key "sdnDomainName": str
        key "sdnIntegrationIntent": Union[str, SdnIntegrationIntent]
        key "sdnStatus": Union[str, SdnStatus]
        sdn_api_address: str
        sdn_domain_name: str
        sdn_integration_intent: Union[str, SdnIntegrationIntent]
        sdn_status: Union[str, SdnStatus]


    class azure.mgmt.azurestackhci.types.ConfidentialVmProfile(TypedDict, total=False):
        key "igvmStatus": Union[str, IgvmStatus]
        igvm_status: Union[str, IgvmStatus]
        statusDetails: list[IgvmStatusDetail]
        status_details: list[IgvmStatusDetail]


    class azure.mgmt.azurestackhci.types.ConfidentialVmProperties(TypedDict, total=False):
        key "confidentialVmIntent": Union[str, ConfidentialVmIntent]
        key "confidentialVmStatus": Union[str, ConfidentialVmStatus]
        key "confidentialVmStatusSummary": str
        confidential_vm_intent: Union[str, ConfidentialVmIntent]
        confidential_vm_status: Union[str, ConfidentialVmStatus]
        confidential_vm_status_summary: str


    class azure.mgmt.azurestackhci.types.CreatePartitionGpuJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "gpuId": str
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineGpuJobType.CREATE_PARTITION]]
        key "partitionCount": Required[int]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.CREATE_PARTITION]
        partition_count: int
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.CreateVolumeJobProperties(TypedDict, total=False):
        key "createdVolumeId": str
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "fileSystem": Union[str, DiskFileSystemType]
        key "jobId": str
        key "jobType": Required[Literal[DiskJobType.CREATE_VOLUME]]
        key "path": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('DiskJobReportedProperties', module='types')
        key "sizeInBytes": Required[str]
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        created_volume_id: str
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        file_system: Union[str, DiskFileSystemType]
        job_id: str
        job_type: Literal[DiskJobType.CREATE_VOLUME]
        path: str
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        size_in_bytes: str
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.DdaDetails(TypedDict, total=False):
        key "ddaPool": str
        key "workloadDetail": ForwardRef('WorkloadDetails', module='types')
        dda_pool: str
        workload_detail: WorkloadDetails


    class azure.mgmt.azurestackhci.types.DefaultExtensionDetails(TypedDict, total=False):
        key "category": str
        key "consentTime": str
        category: str
        consent_time: str


    class azure.mgmt.azurestackhci.types.DeleteVolumeJobProperties(TypedDict, total=False):
        key "confirmDeletion": bool
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[PrivilegedJobType.DELETE_VOLUME]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('DiskJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "volumePath": Required[str]
        confirm_deletion: bool
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[PrivilegedJobType.DELETE_VOLUME]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        volume_path: str


    class azure.mgmt.azurestackhci.types.DeploymentCluster(TypedDict, total=False):
        key "azureServiceEndpoint": str
        key "cloudAccountName": str
        key "clusterPattern": Union[str, ClusterPattern]
        key "hardwareClass": Union[str, HardwareClass]
        key "name": str
        key "witnessPath": str
        key "witnessType": str
        azure_service_endpoint: str
        cloud_account_name: str
        cluster_pattern: Union[str, ClusterPattern]
        hardware_class: Union[str, HardwareClass]
        name: str
        witness_path: str
        witness_type: str


    class azure.mgmt.azurestackhci.types.DeploymentConfiguration(TypedDict, total=False):
        key "scaleUnits": Required[list[ScaleUnits]]
        key "version": str
        scale_units: list[ScaleUnits]
        version: str


    class azure.mgmt.azurestackhci.types.DeploymentData(TypedDict, total=False):
        key "adouPath": str
        key "assemblyInfo": ForwardRef('AssemblyInfo', module='types')
        key "cluster": ForwardRef('DeploymentCluster', module='types')
        key "domainFqdn": str
        key "hostNetwork": ForwardRef('DeploymentSettingHostNetwork', module='types')
        key "identityProvider": Union[str, IdentityProvider]
        key "isManagementCluster": bool
        key "namingPrefix": str
        key "observability": ForwardRef('Observability', module='types')
        key "optionalServices": ForwardRef('OptionalServices', module='types')
        key "sdnIntegration": ForwardRef('SdnIntegration', module='types')
        key "secretsLocation": str
        key "securitySettings": ForwardRef('DeploymentSecuritySettings', module='types')
        key "storage": ForwardRef('Storage', module='types')
        adou_path: str
        assembly_info: AssemblyInfo
        cluster: DeploymentCluster
        domain_fqdn: str
        host_network: DeploymentSettingHostNetwork
        identity_provider: Union[str, IdentityProvider]
        infrastructureNetwork: list[InfrastructureNetwork]
        infrastructure_network: list[InfrastructureNetwork]
        is_management_cluster: bool
        localAvailabilityZones: list[LocalAvailabilityZones]
        local_availability_zones: list[LocalAvailabilityZones]
        naming_prefix: str
        observability: Observability
        optional_services: OptionalServices
        physicalNodes: list[PhysicalNodes]
        physical_nodes: list[PhysicalNodes]
        sdn_integration: SdnIntegration
        secrets: list[EceDeploymentSecrets]
        secrets_location: str
        security_settings: DeploymentSecuritySettings
        storage: Storage


    class azure.mgmt.azurestackhci.types.DeploymentSecuritySettings(TypedDict, total=False):
        key "bitlockerBootVolume": bool
        key "bitlockerDataVolumes": bool
        key "credentialGuardEnforced": bool
        key "driftControlEnforced": bool
        key "drtmProtection": bool
        key "hvciProtection": bool
        key "sideChannelMitigationEnforced": bool
        key "smbClusterEncryption": bool
        key "smbSigningEnforced": bool
        key "wdacEnforced": bool
        bitlocker_boot_volume: bool
        bitlocker_data_volumes: bool
        credential_guard_enforced: bool
        drift_control_enforced: bool
        drtm_protection: bool
        hvci_protection: bool
        side_channel_mitigation_enforced: bool
        smb_cluster_encryption: bool
        smb_signing_enforced: bool
        wdac_enforced: bool


    class azure.mgmt.azurestackhci.types.DeploymentSetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeploymentSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeploymentSettingsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.DeploymentSettingAdapterPropertyOverrides(TypedDict, total=False):
        key "jumboPacket": str
        key "networkDirect": str
        key "networkDirectTechnology": str
        jumbo_packet: str
        network_direct: str
        network_direct_technology: str


    class azure.mgmt.azurestackhci.types.DeploymentSettingHostNetwork(TypedDict, total=False):
        key "enableStorageAutoIp": bool
        key "sanNetworks": ForwardRef('SanNetworks', module='types')
        key "storageConnectivitySwitchless": bool
        enable_storage_auto_ip: bool
        intents: list[DeploymentSettingIntents]
        san_networks: SanNetworks
        storageNetworks: list[DeploymentSettingStorageNetworks]
        storage_connectivity_switchless: bool
        storage_networks: list[DeploymentSettingStorageNetworks]


    class azure.mgmt.azurestackhci.types.DeploymentSettingIntents(TypedDict, total=False):
        key "adapterPropertyOverrides": ForwardRef('DeploymentSettingAdapterPropertyOverrides', module='types')
        key "name": str
        key "overrideAdapterProperty": bool
        key "overrideQosPolicy": bool
        key "overrideVirtualSwitchConfiguration": bool
        key "qosPolicyOverrides": ForwardRef('QosPolicyOverrides', module='types')
        key "virtualSwitchConfigurationOverrides": ForwardRef('DeploymentSettingVirtualSwitchConfigurationOverrides', module='types')
        adapter: list[str]
        adapter_property_overrides: DeploymentSettingAdapterPropertyOverrides
        name: str
        override_adapter_property: bool
        override_qos_policy: bool
        override_virtual_switch_configuration: bool
        qos_policy_overrides: QosPolicyOverrides
        trafficType: list[str]
        traffic_type: list[str]
        virtual_switch_configuration_overrides: DeploymentSettingVirtualSwitchConfigurationOverrides


    class azure.mgmt.azurestackhci.types.DeploymentSettingStorageAdapterIPInfo(TypedDict, total=False):
        key "ipv4Address": str
        key "physicalNode": str
        key "subnetMask": str
        ipv4_address: str
        physical_node: str
        subnet_mask: str


    class azure.mgmt.azurestackhci.types.DeploymentSettingStorageNetworks(TypedDict, total=False):
        key "name": str
        key "networkAdapterName": str
        key "vlanId": str
        name: str
        network_adapter_name: str
        storageAdapterIPInfo: list[DeploymentSettingStorageAdapterIPInfo]
        storage_adapter_ip_info: list[DeploymentSettingStorageAdapterIPInfo]
        vlan_id: str


    class azure.mgmt.azurestackhci.types.DeploymentSettingVirtualSwitchConfigurationOverrides(TypedDict, total=False):
        key "enableIov": str
        key "loadBalancingAlgorithm": str
        enable_iov: str
        load_balancing_algorithm: str


    class azure.mgmt.azurestackhci.types.DeploymentSettingsProperties(TypedDict, total=False):
        key "arcNodeResourceIds": Required[list[str]]
        key "deploymentConfiguration": Required[DeploymentConfiguration]
        key "deploymentMode": Required[Union[str, DeploymentMode]]
        key "operationType": Union[str, OperationType]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('EceReportedProperties', module='types')
        arc_node_resource_ids: list[str]
        deployment_configuration: DeploymentConfiguration
        deployment_mode: Union[str, DeploymentMode]
        operation_type: Union[str, OperationType]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: EceReportedProperties


    class azure.mgmt.azurestackhci.types.DeploymentStep(TypedDict, total=False):
        key "description": str
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "fullStepIndex": str
        key "name": str
        key "startTimeUtc": str
        key "status": str
        description: str
        end_time_utc: str
        error: ErrorDetail
        exception: list[str]
        full_step_index: str
        name: str
        start_time_utc: str
        status: str
        steps: list[DeploymentStep]


    class azure.mgmt.azurestackhci.types.DeviceConfiguration(TypedDict, total=False):
        key "deviceMetadata": str
        device_metadata: str
        nicDetails: list[NicDetail]
        nic_details: list[NicDetail]


    class azure.mgmt.azurestackhci.types.DeviceDetail(TypedDict, total=False):
        key "claimedBy": str
        key "deviceResourceId": str
        claimed_by: str
        device_resource_id: str


    class azure.mgmt.azurestackhci.types.DeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HCI = "HCI"


    class azure.mgmt.azurestackhci.types.DevicePool(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DevicePoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: DevicePoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhci.types.DevicePoolPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.azurestackhci.types.DevicePoolProperties(TypedDict, total=False):
        key "cloudId": str
        key "customLocationName": str
        key "customLocationResourceId": str
        key "managedResourceGroup": str
        key "provisioningState": Union[str, ProvisioningState]
        cloud_id: str
        custom_location_name: str
        custom_location_resource_id: str
        devices: list[DeviceDetail]
        managed_resource_group: str
        operationDetails: list[OperationDetail]
        operation_details: list[OperationDetail]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.azurestackhci.types.DiskActionStatus(TypedDict, total=False):
        key "status": str
        status: str
        steps: list[DiskDeploymentStep]


    class azure.mgmt.azurestackhci.types.DiskConfiguration(TypedDict, total=False):
        volumes: list[DiskVolumeConfiguration]


    class azure.mgmt.azurestackhci.types.DiskDeploymentStep(TypedDict, total=False):
        key "description": str
        key "endTimeUtc": str
        key "fullStepIndex": str
        key "name": str
        key "startTimeUtc": str
        key "status": str
        description: str
        end_time_utc: str
        exception: list[str]
        full_step_index: str
        name: str
        start_time_utc: str
        status: str
        steps: list[DiskDeploymentStep]


    class azure.mgmt.azurestackhci.types.DiskJobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('DiskActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('DiskActionStatus', module='types')
        deployment_status: DiskActionStatus
        percent_complete: int
        validation_status: DiskActionStatus


    class azure.mgmt.azurestackhci.types.DiskJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_VOLUME = "CreateVolume"
        SYNC_CONFIGURATION = "SyncConfiguration"


    class azure.mgmt.azurestackhci.types.DiskReportedProperties(TypedDict, total=False):
        key "busLocation": str
        key "diskName": str
        key "diskType": Union[str, DiskType]
        key "firmwareVersion": str
        key "isSupported": bool
        key "manufacturer": str
        key "model": str
        key "serialNumber": str
        key "sizeInBytes": str
        key "state": Union[str, DiskState]
        key "unallocatedSizeInBytes": str
        bus_location: str
        disk_name: str
        disk_type: Union[str, DiskType]
        firmware_version: str
        is_supported: bool
        manufacturer: str
        model: str
        serial_number: str
        size_in_bytes: str
        state: Union[str, DiskState]
        unallocated_size_in_bytes: str
        volumes: list[DiskVolumeReportedProperties]


    class azure.mgmt.azurestackhci.types.DiskVolumeConfiguration(TypedDict, total=False):
        key "fileSystem": Union[str, DiskFileSystemType]
        key "path": Required[str]
        key "sizeInBytes": Required[str]
        file_system: Union[str, DiskFileSystemType]
        path: str
        size_in_bytes: str


    class azure.mgmt.azurestackhci.types.DiskVolumeReportedProperties(TypedDict, total=False):
        key "fileSystem": str
        key "isBoot": bool
        key "name": str
        key "offsetInBytes": int
        key "partitionId": str
        key "partitionNumber": int
        key "path": str
        key "resourceName": str
        key "sizeInBytes": str
        key "sizeRemainingInBytes": str
        file_system: str
        is_boot: bool
        name: str
        offset_in_bytes: int
        partition_id: str
        partition_number: int
        path: str
        resource_name: str
        size_in_bytes: str
        size_remaining_in_bytes: str


    class azure.mgmt.azurestackhci.types.DnsZones(TypedDict, total=False):
        key "dnsZoneName": str
        dnsForwarder: list[str]
        dns_forwarder: list[str]
        dns_zone_name: str


    class azure.mgmt.azurestackhci.types.DownloadOsJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "downloadRequest": Required[DownloadRequest]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineJobType.DOWNLOAD_OS]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('ProvisionOsReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        download_request: DownloadRequest
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[EdgeMachineJobType.DOWNLOAD_OS]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: ProvisionOsReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.DownloadOsProfile(TypedDict, total=False):
        key "gpgPubKey": str
        key "imageHash": str
        key "osImageLocation": str
        key "osName": str
        key "osType": str
        key "osVersion": str
        key "vsrVersion": str
        gpg_pub_key: str
        image_hash: str
        os_image_location: str
        os_name: str
        os_type: str
        os_version: str
        vsr_version: str


    class azure.mgmt.azurestackhci.types.DownloadRequest(TypedDict, total=False):
        key "osProfile": Required[DownloadOsProfile]
        key "target": Required[Union[str, ProvisioningOsType]]
        os_profile: DownloadOsProfile
        target: Union[str, ProvisioningOsType]


    class azure.mgmt.azurestackhci.types.EceActionStatus(TypedDict, total=False):
        key "status": str
        status: str
        steps: list[DeploymentStep]


    class azure.mgmt.azurestackhci.types.EceDeploymentSecrets(TypedDict, total=False):
        key "eceSecretName": Union[str, EceSecrets]
        key "secretLocation": str
        key "secretName": str
        ece_secret_name: Union[str, EceSecrets]
        secret_location: str
        secret_name: str


    class azure.mgmt.azurestackhci.types.EceReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.EdgeDevice(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[DeviceKind.HCI]]
        key "name": str
        key "properties": ForwardRef('HciEdgeDeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[DeviceKind.HCI]
        name: str
        properties: HciEdgeDeviceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeDeviceDisks(TypedDict, total=False):
        key "id": Required[str]
        key "isSupported": bool
        key "manufacturer": str
        key "model": str
        key "sizeInBytes": str
        key "type": str
        id: str
        is_supported: bool
        manufacturer: str
        model: str
        size_in_bytes: str
        type: str


    class azure.mgmt.azurestackhci.types.EdgeDeviceJob(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[EdgeDeviceKind.HCI]]
        key "name": str
        key "properties": Required[HciEdgeDeviceJobProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[EdgeDeviceKind.HCI]
        name: str
        properties: HciEdgeDeviceJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeDeviceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HCI = "HCI"


    class azure.mgmt.azurestackhci.types.EdgeDeviceProperties(TypedDict, total=False):
        key "deviceConfiguration": ForwardRef('DeviceConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        device_configuration: DeviceConfiguration
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.azurestackhci.types.EdgeMachine(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('EdgeMachineProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: EdgeMachineProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineAdapterPropertyOverrides(TypedDict, total=False):
        key "jumboPacket": str
        key "networkDirect": str
        key "networkDirectTechnology": str
        jumbo_packet: str
        network_direct: str
        network_direct_technology: str


    class azure.mgmt.azurestackhci.types.EdgeMachineCollectLogJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "fromDate": Required[str]
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineJobType.COLLECT_LOG]]
        key "lastLogGenerated": str
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('EdgeMachineCollectLogJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "toDate": Required[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        from_date: str
        job_id: str
        job_type: Literal[EdgeMachineJobType.COLLECT_LOG]
        last_log_generated: str
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: EdgeMachineCollectLogJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        to_date: str


    class azure.mgmt.azurestackhci.types.EdgeMachineCollectLogJobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        logCollectionSessionDetails: list[LogCollectionJobSession]
        log_collection_session_details: list[LogCollectionJobSession]
        percent_complete: int
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.EdgeMachineDisk(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineDiskProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineDiskProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineDiskInfo(TypedDict, total=False):
        key "id": Required[str]
        key "isSupported": bool
        key "manufacturer": str
        key "model": str
        key "sizeInBytes": str
        key "type": str
        id: str
        is_supported: bool
        manufacturer: str
        model: str
        size_in_bytes: str
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineDiskJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineDiskJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineDiskJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineDiskPrivilegedJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineDiskPrivilegedJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineDiskPrivilegedJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineDiskPrivilegedJobProperties(TypedDict, total=False):
        key "confirmDeletion": bool
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[PrivilegedJobType.DELETE_VOLUME]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('DiskJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "volumePath": Required[str]
        confirm_deletion: bool
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[PrivilegedJobType.DELETE_VOLUME]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        volume_path: str


    class azure.mgmt.azurestackhci.types.EdgeMachineDiskProperties(TypedDict, total=False):
        key "diskConfiguration": ForwardRef('DiskConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('DiskReportedProperties', module='types')
        disk_configuration: DiskConfiguration
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskReportedProperties


    class azure.mgmt.azurestackhci.types.EdgeMachineGpu(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineGpuProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineGpuProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineGpuJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineGpuJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineGpuJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineGpuJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGN_PARTITION = "AssignPartition"
        CREATE_PARTITION = "CreatePartition"
        REMOVE_PARTITION = "RemovePartition"
        SWITCH_MODE = "SwitchMode"


    class azure.mgmt.azurestackhci.types.EdgeMachineGpuProperties(TypedDict, total=False):
        key "acceleratorType": str
        key "assignable": bool
        key "assignmentStatus": str
        key "ddaDetails": ForwardRef('DdaDetails', module='types')
        key "gpuId": str
        key "gpuMode": Union[str, GpuMode]
        key "hostDriverVersion": str
        key "manufacturer": str
        key "memoryModel": str
        key "model": str
        key "partitionDetails": ForwardRef('GpuPartitionDetails', module='types')
        key "partitionable": bool
        key "pciLocation": str
        key "provisioningState": Union[str, ProvisioningState]
        key "status": str
        key "totalMemoryInBytes": str
        accelerator_type: str
        assignable: bool
        assignment_status: str
        dda_details: DdaDetails
        gpu_id: str
        gpu_mode: Union[str, GpuMode]
        host_driver_version: str
        manufacturer: str
        memory_model: str
        model: str
        partition_details: GpuPartitionDetails
        partitionable: bool
        pci_location: str
        provisioning_state: Union[str, ProvisioningState]
        status: str
        total_memory_in_bytes: str


    class azure.mgmt.azurestackhci.types.EdgeMachineHostNetwork(TypedDict, total=False):
        key "enableStorageAutoIp": bool
        key "storageConnectivitySwitchless": bool
        enable_storage_auto_ip: bool
        intents: list[EdgeMachineHostNetworkIntent]
        storageNetworks: list[EdgeMachineStorageNetwork]
        storage_connectivity_switchless: bool
        storage_networks: list[EdgeMachineStorageNetwork]


    class azure.mgmt.azurestackhci.types.EdgeMachineHostNetworkIntent(TypedDict, total=False):
        key "adapterPropertyOverrides": ForwardRef('EdgeMachineAdapterPropertyOverrides', module='types')
        key "intentName": str
        key "intentType": int
        key "isComputeIntentSet": bool
        key "isManagementIntentSet": bool
        key "isNetworkIntentType": bool
        key "isOnlyStorage": bool
        key "isOnlyStretch": bool
        key "isStorageIntentSet": bool
        key "isStretchIntentSet": bool
        key "overrideAdapterProperty": bool
        key "overrideQosPolicy": bool
        key "overrideVirtualSwitchConfiguration": bool
        key "qosPolicyOverrides": ForwardRef('QosPolicyOverrides', module='types')
        key "scope": int
        key "virtualSwitchConfigurationOverrides": ForwardRef('EdgeMachineVirtualSwitchConfigurationOverrides', module='types')
        adapter_property_overrides: EdgeMachineAdapterPropertyOverrides
        intentAdapters: list[str]
        intent_adapters: list[str]
        intent_name: str
        intent_type: int
        is_compute_intent_set: bool
        is_management_intent_set: bool
        is_network_intent_type: bool
        is_only_storage: bool
        is_only_stretch: bool
        is_storage_intent_set: bool
        is_stretch_intent_set: bool
        override_adapter_property: bool
        override_qos_policy: bool
        override_virtual_switch_configuration: bool
        qos_policy_overrides: QosPolicyOverrides
        scope: int
        virtual_switch_configuration_overrides: EdgeMachineVirtualSwitchConfigurationOverrides


    class azure.mgmt.azurestackhci.types.EdgeMachineJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECT_LOG = "CollectLog"
        DOWNLOAD_OS = "DownloadOs"
        PROVISION_OS = "ProvisionOs"
        REMOTE_SUPPORT = "RemoteSupport"


    class azure.mgmt.azurestackhci.types.EdgeMachineNetworkAdapterJob(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineNetworkAdapterJobProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineNetworkAdapterJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineNetworkProfile(TypedDict, total=False):
        key "hostNetwork": ForwardRef('EdgeMachineHostNetwork', module='types')
        key "sdnProperties": ForwardRef('SdnProperties', module='types')
        host_network: EdgeMachineHostNetwork
        nicDetails: list[EdgeMachineNicDetail]
        nic_details: list[EdgeMachineNicDetail]
        sdn_properties: SdnProperties
        switchDetails: list[SwitchDetail]
        switch_details: list[SwitchDetail]


    class azure.mgmt.azurestackhci.types.EdgeMachineNicDetail(TypedDict, total=False):
        key "adapterName": str
        key "componentId": str
        key "defaultGateway": str
        key "defaultIsolationId": str
        key "driverVersion": str
        key "interfaceDescription": str
        key "ip4Address": str
        key "macAddress": str
        key "nicStatus": str
        key "nicType": str
        key "rdmaCapability": Union[str, RdmaCapability]
        key "slot": str
        key "subnetMask": str
        key "switchName": str
        key "vlanId": str
        adapter_name: str
        component_id: str
        default_gateway: str
        default_isolation_id: str
        dnsServers: list[str]
        dns_servers: list[str]
        driver_version: str
        interface_description: str
        ip4_address: str
        mac_address: str
        nic_status: str
        nic_type: str
        rdma_capability: Union[str, RdmaCapability]
        slot: str
        subnet_mask: str
        switch_name: str
        vlan_id: str


    class azure.mgmt.azurestackhci.types.EdgeMachinePatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.azurestackhci.types.EdgeMachineProperties(TypedDict, total=False):
        key "arcGatewayResourceId": str
        key "arcMachineResourceGroupId": str
        key "arcMachineResourceId": str
        key "claimedBy": str
        key "cloudId": str
        key "connectivityStatus": Union[str, EdgeMachineConnectivityStatus]
        key "devicePoolResourceId": str
        key "edgeMachineKind": Union[str, EdgeMachineKind]
        key "lastSyncTimestamp": str
        key "lifecycleDetails": ForwardRef('LifecycleDetails', module='types')
        key "machineState": Union[str, EdgeMachineState]
        key "ownershipVoucherDetails": ForwardRef('OwnershipVoucherDetails', module='types')
        key "provisioningDetails": ForwardRef('ProvisioningDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('EdgeMachineReportedProperties', module='types')
        key "siteDetails": ForwardRef('SiteDetails', module='types')
        arc_gateway_resource_id: str
        arc_machine_resource_group_id: str
        arc_machine_resource_id: str
        claimed_by: str
        cloud_id: str
        connectivity_status: Union[str, EdgeMachineConnectivityStatus]
        device_pool_resource_id: str
        edge_machine_kind: Union[str, EdgeMachineKind]
        last_sync_timestamp: str
        lifecycle_details: LifecycleDetails
        machine_state: Union[str, EdgeMachineState]
        operationDetails: list[OperationDetail]
        operation_details: list[OperationDetail]
        ownership_voucher_details: OwnershipVoucherDetails
        provisioning_details: ProvisioningDetails
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: EdgeMachineReportedProperties
        site_details: SiteDetails


    class azure.mgmt.azurestackhci.types.EdgeMachineRemoteSupportJobProperties(TypedDict, total=False):
        key "accessLevel": Required[Union[str, RemoteSupportAccessLevel]]
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "expirationTimestamp": Required[str]
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineJobType.REMOTE_SUPPORT]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('EdgeMachineRemoteSupportJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "type": Required[Union[str, RemoteSupportType]]
        access_level: Union[str, RemoteSupportAccessLevel]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        expiration_timestamp: str
        job_id: str
        job_type: Literal[EdgeMachineJobType.REMOTE_SUPPORT]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: EdgeMachineRemoteSupportJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        type: Union[str, RemoteSupportType]


    class azure.mgmt.azurestackhci.types.EdgeMachineRemoteSupportJobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "nodeSettings": ForwardRef('EdgeMachineRemoteSupportNodeSettings', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        node_settings: EdgeMachineRemoteSupportNodeSettings
        percent_complete: int
        sessionDetails: list[RemoteSupportSession]
        session_details: list[RemoteSupportSession]
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.EdgeMachineRemoteSupportNodeSettings(TypedDict, total=False):
        key "connectionErrorMessage": str
        key "connectionStatus": str
        key "createdAt": str
        key "state": str
        key "updatedAt": str
        connection_error_message: str
        connection_status: str
        created_at: str
        state: str
        updated_at: str


    class azure.mgmt.azurestackhci.types.EdgeMachineReportedProperties(TypedDict, total=False):
        key "confidentialVmProfile": ForwardRef('ConfidentialVmProfile', module='types')
        key "extensionProfile": ForwardRef('ExtensionProfile', module='types')
        key "hardwareProfile": ForwardRef('HardwareProfile', module='types')
        key "lastUpdated": str
        key "networkProfile": ForwardRef('EdgeMachineNetworkProfile', module='types')
        key "osProfile": ForwardRef('OsProfile', module='types')
        key "sbeDeploymentPackageInfo": ForwardRef('SbeDeploymentPackageInfo', module='types')
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        key "workloadInventoryLastUpdated": str
        confidential_vm_profile: ConfidentialVmProfile
        extension_profile: ExtensionProfile
        hardware_profile: HardwareProfile
        last_updated: str
        network_profile: EdgeMachineNetworkProfile
        os_profile: OsProfile
        sbe_deployment_package_info: SbeDeploymentPackageInfo
        storage_profile: StorageProfile
        workloadInventory: list[EdgeMachineWorkloadInventoryItem]
        workload_inventory: list[EdgeMachineWorkloadInventoryItem]
        workload_inventory_last_updated: str


    class azure.mgmt.azurestackhci.types.EdgeMachineStorageAdapterIpInfo(TypedDict, total=False):
        key "ipv4Address": str
        key "physicalNode": str
        key "subnetMask": str
        ipv4_address: str
        physical_node: str
        subnet_mask: str


    class azure.mgmt.azurestackhci.types.EdgeMachineStorageNetwork(TypedDict, total=False):
        key "name": str
        key "networkAdapterName": str
        key "storageVlanId": str
        name: str
        network_adapter_name: str
        storageAdapterIPInfo: list[EdgeMachineStorageAdapterIpInfo]
        storage_adapter_ip_info: list[EdgeMachineStorageAdapterIpInfo]
        storage_vlan_id: str


    class azure.mgmt.azurestackhci.types.EdgeMachineUpdate(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineUpdateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineUpdateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineUpdateInfo(TypedDict, total=False):
        key "arcAgentVersion": str
        key "displayName": str
        key "estimatedInstallTimeMinutes": int
        key "rebootRequired": bool
        key "releaseNotesLink": str
        key "totalSizeBytes": int
        key "updateType": str
        key "vsrVersion": Required[str]
        arc_agent_version: str
        display_name: str
        estimated_install_time_minutes: int
        reboot_required: bool
        release_notes_link: str
        total_size_bytes: int
        update_type: str
        vsr_version: str


    class azure.mgmt.azurestackhci.types.EdgeMachineUpdateProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "solutionType": Union[str, ProvisioningOsType]
        key "values": Required[list[EdgeMachineUpdateInfo]]
        provisioning_state: Union[str, ProvisioningState]
        solution_type: Union[str, ProvisioningOsType]
        values_property: list[EdgeMachineUpdateInfo]


    class azure.mgmt.azurestackhci.types.EdgeMachineValidateRequest(TypedDict, total=False):
        key "additionalInfo": str
        key "edgeMachineIds": Required[list[str]]
        additional_info: str
        edge_machine_ids: list[str]


    class azure.mgmt.azurestackhci.types.EdgeMachineVirtualSwitchConfigurationOverrides(TypedDict, total=False):
        key "enableIov": str
        key "loadBalancingAlgorithm": str
        enable_iov: str
        load_balancing_algorithm: str


    class azure.mgmt.azurestackhci.types.EdgeMachineVolume(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EdgeMachineVolumeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EdgeMachineVolumeProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.EdgeMachineVolumeProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('VolumeReportedProperties', module='types')
        key "volumeConfiguration": ForwardRef('VolumeConfiguration', module='types')
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: VolumeReportedProperties
        volume_configuration: VolumeConfiguration


    class azure.mgmt.azurestackhci.types.EdgeMachineWorkloadInventoryItem(TypedDict, total=False):
        key "memoryInBytes": str
        key "name": str
        key "resourceId": str
        key "state": str
        key "virtualProcessorCount": str
        key "workloadId": str
        key "workloadType": str
        memory_in_bytes: str
        name: str
        resource_id: str
        state: str
        virtual_processor_count: str
        workload_id: str
        workload_type: str


    class azure.mgmt.azurestackhci.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.azurestackhci.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.azurestackhci.types.Extension(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ExtensionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ExtensionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.ExtensionInstanceView(TypedDict, total=False):
        key "name": str
        key "status": ForwardRef('ExtensionInstanceViewStatus', module='types')
        key "type": str
        key "typeHandlerVersion": str
        name: str
        status: ExtensionInstanceViewStatus
        type: str
        type_handler_version: str


    class azure.mgmt.azurestackhci.types.ExtensionInstanceViewStatus(TypedDict, total=False):
        key "code": str
        key "displayStatus": str
        key "level": Union[str, StatusLevelTypes]
        key "message": str
        key "time": str
        code: str
        display_status: str
        level: Union[str, StatusLevelTypes]
        message: str
        time: str


    class azure.mgmt.azurestackhci.types.ExtensionParameters(TypedDict, total=False):
        key "autoUpgradeMinorVersion": bool
        key "enableAutomaticUpgrade": bool
        key "forceUpdateTag": str
        key "protectedSettings": Any
        key "publisher": str
        key "settings": Any
        key "type": str
        key "typeHandlerVersion": str
        auto_upgrade_minor_version: bool
        enable_automatic_upgrade: bool
        force_update_tag: str
        protected_settings: Any
        publisher: str
        settings: Any
        type: str
        type_handler_version: str


    class azure.mgmt.azurestackhci.types.ExtensionPatch(TypedDict, total=False):
        key "properties": ForwardRef('ExtensionPatchProperties', module='types')
        properties: ExtensionPatchProperties


    class azure.mgmt.azurestackhci.types.ExtensionPatchParameters(TypedDict, total=False):
        key "enableAutomaticUpgrade": bool
        key "protectedSettings": Any
        key "settings": Any
        key "typeHandlerVersion": str
        enable_automatic_upgrade: bool
        protected_settings: Any
        settings: Any
        type_handler_version: str


    class azure.mgmt.azurestackhci.types.ExtensionPatchProperties(TypedDict, total=False):
        key "extensionParameters": ForwardRef('ExtensionPatchParameters', module='types')
        extension_parameters: ExtensionPatchParameters


    class azure.mgmt.azurestackhci.types.ExtensionProfile(TypedDict, total=False):
        extensions: list[HciEdgeDeviceArcExtension]


    class azure.mgmt.azurestackhci.types.ExtensionProperties(TypedDict, total=False):
        key "aggregateState": Union[str, ExtensionAggregateState]
        key "extensionParameters": ForwardRef('ExtensionParameters', module='types')
        key "managedBy": Union[str, ExtensionManagedBy]
        key "provisioningState": Union[str, ProvisioningState]
        aggregate_state: Union[str, ExtensionAggregateState]
        extension_parameters: ExtensionParameters
        managed_by: Union[str, ExtensionManagedBy]
        perNodeExtensionDetails: list[PerNodeExtensionState]
        per_node_extension_details: list[PerNodeExtensionState]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.azurestackhci.types.ExtensionResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.ExtensionUpgradeParameters(TypedDict, total=False):
        key "targetVersion": str
        target_version: str


    class azure.mgmt.azurestackhci.types.ForcePushNetworkAdapterJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[NetworkAdapterJobType.FORCE_PUSH]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('NetworkAdapterJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.FORCE_PUSH]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.GpuCreatePartitionJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.GPU_CREATE_PARTITION]]
        key "partitionCount": Required[int]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.GPU_CREATE_PARTITION]
        partition_count: int
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.GpuPartitionDetails(TypedDict, total=False):
        key "assignedPartitions": int
        key "availableDecode": str
        key "availableEncode": str
        key "availablePartitions": int
        key "availableVram": str
        key "partitionSizeMb": str
        key "partitionableGpuName": str
        key "totalPartitions": int
        key "totalVram": str
        assigned_partitions: int
        available_decode: str
        available_encode: str
        available_partitions: int
        available_vram: str
        partition_size_mb: str
        partitionable_gpu_name: str
        partitions: list[PartitionDetails]
        total_partitions: int
        total_vram: str
        validPartitionCount: list[str]
        valid_partition_count: list[str]


    class azure.mgmt.azurestackhci.types.GpuSwitchModeJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.GPU_SWITCH_MODE]]
        key "mode": Required[Union[str, GpuMode]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.GPU_SWITCH_MODE]
        mode: Union[str, GpuMode]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.HardwareProfile(TypedDict, total=False):
        key "cpuCores": int
        key "cpuSockets": int
        key "manufacturer": str
        key "memoryCapacityInGb": int
        key "model": str
        key "processorType": str
        key "serialNumber": str
        cpu_cores: int
        cpu_sockets: int
        manufacturer: str
        memory_capacity_in_gb: int
        model: str
        processor_type: str
        serial_number: str


    class azure.mgmt.azurestackhci.types.HciAddServerJobProperties(TypedDict, total=False):
        key "addServerJobServerDetails": Required[list[AddServerJobServerDetails]]
        key "cloudAccountName": str
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.ADD_SERVER]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "witnessPath": str
        key "witnessType": Union[str, WitnessType]
        add_server_job_server_details: list[AddServerJobServerDetails]
        cloud_account_name: str
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.ADD_SERVER]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        secrets: list[EceDeploymentSecrets]
        start_time_utc: str
        status: Union[str, JobStatus]
        witness_path: str
        witness_type: Union[str, WitnessType]


    class azure.mgmt.azurestackhci.types.HciCollectLogJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "fromDate": Required[str]
        key "jobId": str
        key "jobType": Required[Literal[HciEdgeDeviceJobType.COLLECT_LOG]]
        key "lastLogGenerated": str
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('LogCollectionReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "toDate": Required[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        from_date: str
        job_id: str
        job_type: Literal[HciEdgeDeviceJobType.COLLECT_LOG]
        last_log_generated: str
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: LogCollectionReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        to_date: str


    class azure.mgmt.azurestackhci.types.HciConfigureCvmJobProperties(TypedDict, total=False):
        key "confidentialVmIntent": Required[Union[str, ConfidentialVmIntent]]
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.CONFIGURE_CVM]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        confidential_vm_intent: Union[str, ConfidentialVmIntent]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.CONFIGURE_CVM]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.HciConfigureSdnIntegrationJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.CONFIGURE_SDN_INTEGRATION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "sdnIntegrationIntent": Required[Union[str, SdnIntegrationIntent]]
        key "sdnPrefix": str
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.CONFIGURE_SDN_INTEGRATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        sdn_integration_intent: Union[str, SdnIntegrationIntent]
        sdn_prefix: str
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.HciEdgeDevice(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[DeviceKind.HCI]]
        key "name": str
        key "properties": ForwardRef('HciEdgeDeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[DeviceKind.HCI]
        name: str
        properties: HciEdgeDeviceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceAdapterPropertyOverrides(TypedDict, total=False):
        key "jumboPacket": str
        key "networkDirect": str
        key "networkDirectTechnology": str
        jumbo_packet: str
        network_direct: str
        network_direct_technology: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceArcExtension(TypedDict, total=False):
        key "extensionName": str
        key "extensionResourceId": str
        key "managedBy": Union[str, ExtensionManagedBy]
        key "state": Union[str, ArcExtensionState]
        key "typeHandlerVersion": str
        errorDetails: list[HciValidationFailureDetail]
        error_details: list[HciValidationFailureDetail]
        extension_name: str
        extension_resource_id: str
        managed_by: Union[str, ExtensionManagedBy]
        state: Union[str, ArcExtensionState]
        type_handler_version: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceHostNetwork(TypedDict, total=False):
        key "enableStorageAutoIp": bool
        key "storageConnectivitySwitchless": bool
        enable_storage_auto_ip: bool
        intents: list[HciEdgeDeviceIntents]
        storageNetworks: list[HciEdgeDeviceStorageNetworks]
        storage_connectivity_switchless: bool
        storage_networks: list[HciEdgeDeviceStorageNetworks]


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceIntents(TypedDict, total=False):
        key "adapterPropertyOverrides": ForwardRef('HciEdgeDeviceAdapterPropertyOverrides', module='types')
        key "intentName": str
        key "intentType": int
        key "isComputeIntentSet": bool
        key "isManagementIntentSet": bool
        key "isNetworkIntentType": bool
        key "isOnlyStorage": bool
        key "isOnlyStretch": bool
        key "isStorageIntentSet": bool
        key "isStretchIntentSet": bool
        key "overrideAdapterProperty": bool
        key "overrideQosPolicy": bool
        key "overrideVirtualSwitchConfiguration": bool
        key "qosPolicyOverrides": ForwardRef('QosPolicyOverrides', module='types')
        key "scope": int
        key "virtualSwitchConfigurationOverrides": ForwardRef('HciEdgeDeviceVirtualSwitchConfigurationOverrides', module='types')
        adapter_property_overrides: HciEdgeDeviceAdapterPropertyOverrides
        intentAdapters: list[str]
        intent_adapters: list[str]
        intent_name: str
        intent_type: int
        is_compute_intent_set: bool
        is_management_intent_set: bool
        is_network_intent_type: bool
        is_only_storage: bool
        is_only_stretch: bool
        is_storage_intent_set: bool
        is_stretch_intent_set: bool
        override_adapter_property: bool
        override_qos_policy: bool
        override_virtual_switch_configuration: bool
        qos_policy_overrides: QosPolicyOverrides
        scope: int
        virtual_switch_configuration_overrides: HciEdgeDeviceVirtualSwitchConfigurationOverrides


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceJob(TypedDict, total=False):
        key "id": str
        key "kind": Required[Literal[EdgeDeviceKind.HCI]]
        key "name": str
        key "properties": Required[HciEdgeDeviceJobProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Literal[EdgeDeviceKind.HCI]
        name: str
        properties: HciEdgeDeviceJobProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECT_LOG = "CollectLog"
        REMOTE_SUPPORT = "RemoteSupport"


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceProperties(EdgeDeviceProperties):
        key "deviceConfiguration": ForwardRef('DeviceConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('HciReportedProperties', module='types')
        device_configuration: DeviceConfiguration
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: HciReportedProperties


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceStorageAdapterIPInfo(TypedDict, total=False):
        key "ipv4Address": str
        key "physicalNode": str
        key "subnetMask": str
        ipv4_address: str
        physical_node: str
        subnet_mask: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceStorageNetworks(TypedDict, total=False):
        key "name": str
        key "networkAdapterName": str
        key "storageVlanId": str
        name: str
        network_adapter_name: str
        storageAdapterIPInfo: list[HciEdgeDeviceStorageAdapterIPInfo]
        storage_adapter_ip_info: list[HciEdgeDeviceStorageAdapterIPInfo]
        storage_vlan_id: str


    class azure.mgmt.azurestackhci.types.HciEdgeDeviceVirtualSwitchConfigurationOverrides(TypedDict, total=False):
        key "enableIov": str
        key "loadBalancingAlgorithm": str
        enable_iov: str
        load_balancing_algorithm: str


    class azure.mgmt.azurestackhci.types.HciHardwareProfile(TypedDict, total=False):
        key "processorType": str
        processor_type: str


    class azure.mgmt.azurestackhci.types.HciJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_SERVER = "AddServer"
        CONFIGURE_CVM = "ConfigureCVM"
        CONFIGURE_SDN_INTEGRATION = "ConfigureSdnIntegration"
        GPU_CREATE_PARTITION = "GpuCreatePartition"
        GPU_SWITCH_MODE = "GpuSwitchMode"
        REPAIR_SERVER = "RepairServer"
        VM_CONNECT_PROVISION = "VmConnectProvision"
        VM_CONNECT_REMOVE = "VmConnectRemove"


    class azure.mgmt.azurestackhci.types.HciNetworkProfile(TypedDict, total=False):
        key "hostNetwork": ForwardRef('HciEdgeDeviceHostNetwork', module='types')
        key "sdnProperties": ForwardRef('SdnProperties', module='types')
        host_network: HciEdgeDeviceHostNetwork
        nicDetails: list[HciNicDetail]
        nic_details: list[HciNicDetail]
        sdn_properties: SdnProperties
        switchDetails: list[SwitchDetail]
        switch_details: list[SwitchDetail]


    class azure.mgmt.azurestackhci.types.HciNicDetail(TypedDict, total=False):
        key "adapterName": str
        key "componentId": str
        key "defaultGateway": str
        key "defaultIsolationId": str
        key "driverVersion": str
        key "interfaceDescription": str
        key "ip4Address": str
        key "macAddress": str
        key "nicStatus": str
        key "nicType": str
        key "rdmaCapability": Union[str, RdmaCapability]
        key "slot": str
        key "subnetMask": str
        key "switchName": str
        key "vlanId": str
        adapter_name: str
        component_id: str
        default_gateway: str
        default_isolation_id: str
        dnsServers: list[str]
        dns_servers: list[str]
        driver_version: str
        interface_description: str
        ip4_address: str
        mac_address: str
        nic_status: str
        nic_type: str
        rdma_capability: Union[str, RdmaCapability]
        slot: str
        subnet_mask: str
        switch_name: str
        vlan_id: str


    class azure.mgmt.azurestackhci.types.HciOsProfile(TypedDict, total=False):
        key "assemblyVersion": str
        key "bootType": str
        assembly_version: str
        boot_type: str


    class azure.mgmt.azurestackhci.types.HciRemoteSupportJobProperties(TypedDict, total=False):
        key "accessLevel": Required[Union[str, RemoteSupportAccessLevel]]
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "expirationTimestamp": Required[str]
        key "jobId": str
        key "jobType": Required[Literal[HciEdgeDeviceJobType.REMOTE_SUPPORT]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('RemoteSupportJobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "type": Required[Union[str, RemoteSupportType]]
        access_level: Union[str, RemoteSupportAccessLevel]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        expiration_timestamp: str
        job_id: str
        job_type: Literal[HciEdgeDeviceJobType.REMOTE_SUPPORT]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: RemoteSupportJobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        type: Union[str, RemoteSupportType]


    class azure.mgmt.azurestackhci.types.HciRepairServerJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.REPAIR_SERVER]]
        key "provisioningState": Union[str, ProvisioningState]
        key "repairServerJobServerDetails": Required[list[RepairServerJobServerDetails]]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.REPAIR_SERVER]
        provisioning_state: Union[str, ProvisioningState]
        repair_server_job_server_details: list[RepairServerJobServerDetails]
        reported_properties: JobReportedProperties
        secrets: list[EceDeploymentSecrets]
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.HciReportedProperties(ReportedProperties):
        key "confidentialVmProfile": ForwardRef('ConfidentialVmProfile', module='types')
        key "deviceState": Union[str, DeviceState]
        key "extensionProfile": ForwardRef('ExtensionProfile', module='types')
        key "hardwareProfile": ForwardRef('HciHardwareProfile', module='types')
        key "lastSyncTimestamp": str
        key "networkProfile": ForwardRef('HciNetworkProfile', module='types')
        key "osProfile": ForwardRef('HciOsProfile', module='types')
        key "sbeDeploymentPackageInfo": ForwardRef('SbeDeploymentPackageInfo', module='types')
        key "storageProfile": ForwardRef('HciStorageProfile', module='types')
        confidential_vm_profile: ConfidentialVmProfile
        device_state: Union[str, DeviceState]
        extension_profile: ExtensionProfile
        hardware_profile: HciHardwareProfile
        last_sync_timestamp: str
        network_profile: HciNetworkProfile
        os_profile: HciOsProfile
        sbe_deployment_package_info: SbeDeploymentPackageInfo
        storage_profile: HciStorageProfile


    class azure.mgmt.azurestackhci.types.HciStorageProfile(TypedDict, total=False):
        key "poolableDisksCount": int
        disks: list[EdgeDeviceDisks]
        poolable_disks_count: int


    class azure.mgmt.azurestackhci.types.HciValidationFailureDetail(TypedDict, total=False):
        key "exception": str
        exception: str


    class azure.mgmt.azurestackhci.types.IgvmStatusDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.azurestackhci.types.InfrastructureNetwork(TypedDict, total=False):
        key "dnsServerConfig": Union[str, DnsServerConfig]
        key "gateway": str
        key "subnetMask": str
        key "useDhcp": bool
        dnsServers: list[str]
        dnsZones: list[DnsZones]
        dns_server_config: Union[str, DnsServerConfig]
        dns_servers: list[str]
        dns_zones: list[DnsZones]
        gateway: str
        ipPools: list[IpPools]
        ip_pools: list[IpPools]
        subnet_mask: str
        use_dhcp: bool


    class azure.mgmt.azurestackhci.types.IpAddressRange(TypedDict, total=False):
        key "endIp": Required[str]
        key "startIp": Required[str]
        end_ip: str
        start_ip: str


    class azure.mgmt.azurestackhci.types.IpPools(TypedDict, total=False):
        key "endingAddress": str
        key "startingAddress": str
        ending_address: str
        starting_address: str


    class azure.mgmt.azurestackhci.types.IsolatedVmAttestationConfiguration(TypedDict, total=False):
        key "attestationResourceId": str
        key "attestationServiceEndpoint": str
        key "relyingPartyServiceEndpoint": str
        attestation_resource_id: str
        attestation_service_endpoint: str
        relying_party_service_endpoint: str


    class azure.mgmt.azurestackhci.types.JobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        percent_complete: int
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.LifecycleDetails(TypedDict, total=False):
        key "lifecycleStages": Required[list[LifecycleStage]]
        key "lifecycleStatus": ForwardRef('LifecycleStatus', module='types')
        lifecycle_stages: list[LifecycleStage]
        lifecycle_status: LifecycleStatus


    class azure.mgmt.azurestackhci.types.LifecycleStage(TypedDict, total=False):
        key "description": Required[str]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "lastUpdatedUtc": str
        key "name": Required[str]
        key "startTimeUtc": str
        key "status": Required[Union[str, LifecycleOperationStatus]]
        description: str
        end_time_utc: str
        error: ErrorDetail
        last_updated_utc: str
        name: str
        start_time_utc: str
        status: Union[str, LifecycleOperationStatus]
        subStages: list[LifecycleStage]
        sub_stages: list[LifecycleStage]


    class azure.mgmt.azurestackhci.types.LifecycleStatus(TypedDict, total=False):
        key "lastUpdatedUtc": Required[str]
        key "message": str
        key "stage": str
        key "status": Required[Union[str, EdgeMachineLifecycleStatus]]
        last_updated_utc: str
        message: str
        recommendedSteps: list[str]
        recommended_steps: list[str]
        stage: str
        status: Union[str, EdgeMachineLifecycleStatus]


    class azure.mgmt.azurestackhci.types.LocalAvailabilityZones(TypedDict, total=False):
        key "localAvailabilityZoneName": str
        local_availability_zone_name: str
        nodes: list[str]


    class azure.mgmt.azurestackhci.types.LogCollectionError(TypedDict, total=False):
        key "errorCode": str
        key "errorMessage": str
        error_code: str
        error_message: str


    class azure.mgmt.azurestackhci.types.LogCollectionJobSession(TypedDict, total=False):
        key "correlationId": str
        key "endTime": str
        key "logSize": int
        key "startTime": str
        key "status": Union[str, DeviceLogCollectionStatus]
        key "timeCollected": str
        correlation_id: str
        end_time: str
        log_size: int
        start_time: str
        status: Union[str, DeviceLogCollectionStatus]
        time_collected: str


    class azure.mgmt.azurestackhci.types.LogCollectionProperties(TypedDict, total=False):
        key "fromDate": str
        key "lastLogGenerated": str
        key "toDate": str
        from_date: str
        last_log_generated: str
        logCollectionSessionDetails: list[LogCollectionSession]
        log_collection_session_details: list[LogCollectionSession]
        to_date: str


    class azure.mgmt.azurestackhci.types.LogCollectionReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        logCollectionSessionDetails: list[LogCollectionJobSession]
        log_collection_session_details: list[LogCollectionJobSession]
        percent_complete: int
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.LogCollectionRequest(TypedDict, total=False):
        key "properties": ForwardRef('LogCollectionRequestProperties', module='types')
        properties: LogCollectionRequestProperties


    class azure.mgmt.azurestackhci.types.LogCollectionRequestProperties(TypedDict, total=False):
        key "fromDate": Required[str]
        key "toDate": Required[str]
        from_date: str
        to_date: str


    class azure.mgmt.azurestackhci.types.LogCollectionSession(TypedDict, total=False):
        key "correlationId": str
        key "endTimeCollected": str
        key "logCollectionError": ForwardRef('LogCollectionError', module='types')
        key "logCollectionJobType": Union[str, LogCollectionJobType]
        key "logCollectionStatus": Union[str, LogCollectionStatus]
        key "logEndTime": str
        key "logSize": int
        key "logStartTime": str
        key "timeCollected": str
        correlation_id: str
        end_time_collected: str
        log_collection_error: LogCollectionError
        log_collection_job_type: Union[str, LogCollectionJobType]
        log_collection_status: Union[str, LogCollectionStatus]
        log_end_time: str
        log_size: int
        log_start_time: str
        time_collected: str


    class azure.mgmt.azurestackhci.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.azurestackhci.types.NetworkAdapter(TypedDict, total=False):
        key "adapterName": str
        key "gateway": str
        key "ipAddress": str
        key "ipAddressRange": ForwardRef('IpAddressRange', module='types')
        key "ipAssignmentType": Required[Union[str, IpAssignmentType]]
        key "macAddress": str
        key "subnetMask": str
        key "vlanId": str
        adapter_name: str
        dnsAddressArray: list[str]
        dns_address_array: list[str]
        gateway: str
        ip_address: str
        ip_address_range: IpAddressRange
        ip_assignment_type: Union[str, IpAssignmentType]
        mac_address: str
        subnet_mask: str
        vlan_id: str


    class azure.mgmt.azurestackhci.types.NetworkAdapterActionStatus(TypedDict, total=False):
        key "status": str
        status: str
        steps: list[NetworkAdapterDeploymentStep]


    class azure.mgmt.azurestackhci.types.NetworkAdapterConfiguration(TypedDict, total=False):
        key "adapterName": str
        key "defaultGateway": str
        key "interfaceState": Union[str, InterfaceState]
        key "ip4Address": str
        key "ipInterfaceType": Union[str, IpInterfaceType]
        key "subnetMask": str
        key "vlanId": int
        key "wifiConfiguration": ForwardRef('WifiConfigurationDesiredProperties', module='types')
        adapter_name: str
        default_gateway: str
        dnsServers: list[str]
        dns_servers: list[str]
        interface_state: Union[str, InterfaceState]
        ip4_address: str
        ip_interface_type: Union[str, IpInterfaceType]
        subnet_mask: str
        vlan_id: int
        wifi_configuration: WifiConfigurationDesiredProperties


    class azure.mgmt.azurestackhci.types.NetworkAdapterDeploymentStep(TypedDict, total=False):
        key "description": str
        key "endTimeUtc": str
        key "fullStepIndex": str
        key "name": str
        key "startTimeUtc": str
        key "status": str
        description: str
        end_time_utc: str
        exception: list[str]
        full_step_index: str
        name: str
        start_time_utc: str
        status: str
        steps: list[NetworkAdapterDeploymentStep]


    class azure.mgmt.azurestackhci.types.NetworkAdapterJobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('NetworkAdapterActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('NetworkAdapterActionStatus', module='types')
        deployment_status: NetworkAdapterActionStatus
        percent_complete: int
        validation_status: NetworkAdapterActionStatus


    class azure.mgmt.azurestackhci.types.NetworkAdapterJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLY_CONFIGURATION = "ApplyConfiguration"
        FORCE_PUSH = "ForcePush"
        SYNC_CONFIGURATION = "SyncConfiguration"


    class azure.mgmt.azurestackhci.types.NetworkConfiguration(TypedDict, total=False):
        networkAdapters: list[NetworkAdapter]
        network_adapters: list[NetworkAdapter]


    class azure.mgmt.azurestackhci.types.NetworkController(TypedDict, total=False):
        key "macAddressPoolStart": str
        key "macAddressPoolStop": str
        key "networkVirtualizationEnabled": bool
        mac_address_pool_start: str
        mac_address_pool_stop: str
        network_virtualization_enabled: bool


    class azure.mgmt.azurestackhci.types.NextBillingModel(TypedDict, total=False):
        key "billingModel": str
        key "trialDaysRemaining": float
        billing_model: str
        capabilitiesEnabled: list[str]
        capabilities_enabled: list[str]
        trial_days_remaining: float


    class azure.mgmt.azurestackhci.types.NicDetail(TypedDict, total=False):
        key "adapterName": str
        key "componentId": str
        key "defaultGateway": str
        key "defaultIsolationId": str
        key "driverVersion": str
        key "interfaceDescription": str
        key "ip4Address": str
        key "subnetMask": str
        adapter_name: str
        component_id: str
        default_gateway: str
        default_isolation_id: str
        dnsServers: list[str]
        dns_servers: list[str]
        driver_version: str
        interface_description: str
        ip4_address: str
        subnet_mask: str


    class azure.mgmt.azurestackhci.types.Observability(TypedDict, total=False):
        key "episodicDataUpload": bool
        key "euLocation": bool
        key "streamingDataClient": bool
        episodic_data_upload: bool
        eu_location: bool
        streaming_data_client: bool


    class azure.mgmt.azurestackhci.types.OnboardingConfiguration(TypedDict, total=False):
        key "arcVirtualMachineId": str
        key "location": str
        key "resourceId": str
        key "tenantId": str
        key "type": Union[str, OnboardingResourceType]
        arc_virtual_machine_id: str
        location: str
        resource_id: str
        tenant_id: str
        type: Union[str, OnboardingResourceType]


    class azure.mgmt.azurestackhci.types.OperationDetail(TypedDict, total=False):
        key "description": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "id": str
        key "name": str
        key "resourceId": str
        key "status": str
        key "type": str
        description: str
        error: ErrorDetail
        id: str
        name: str
        resource_id: str
        status: str
        type: str


    class azure.mgmt.azurestackhci.types.OptionalServices(TypedDict, total=False):
        key "confidentialVmIntent": Union[str, ConfidentialVmIntent]
        key "customLocation": str
        confidential_vm_intent: Union[str, ConfidentialVmIntent]
        custom_location: str


    class azure.mgmt.azurestackhci.types.OsProfile(TypedDict, total=False):
        key "assemblyVersion": str
        key "baseImageVersion": str
        key "bootType": str
        key "buildNumber": str
        key "imageVersion": str
        key "osSku": str
        key "osType": str
        key "osVersion": str
        assembly_version: str
        base_image_version: str
        boot_type: str
        build_number: str
        image_version: str
        os_sku: str
        os_type: str
        os_version: str


    class azure.mgmt.azurestackhci.types.OsProvisionProfile(TypedDict, total=False):
        key "gpgPubKey": str
        key "imageHash": str
        key "operationType": Union[str, OSOperationType]
        key "osImageLocation": str
        key "osName": str
        key "osType": str
        key "osVersion": str
        key "vsrVersion": str
        gpg_pub_key: str
        image_hash: str
        operation_type: Union[str, OSOperationType]
        os_image_location: str
        os_name: str
        os_type: str
        os_version: str
        vsr_version: str


    class azure.mgmt.azurestackhci.types.OwnershipVoucherDetails(TypedDict, total=False):
        key "ownerKeyType": Required[Union[str, OwnerKeyType]]
        key "ownershipVoucher": Required[str]
        key "validationDetails": ForwardRef('OwnershipVoucherValidationDetails', module='types')
        owner_key_type: Union[str, OwnerKeyType]
        ownership_voucher: str
        validation_details: OwnershipVoucherValidationDetails


    class azure.mgmt.azurestackhci.types.OwnershipVoucherValidationDetails(TypedDict, total=False):
        key "azureMachineId": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "id": str
        key "manufacturer": str
        key "modelName": str
        key "serialNumber": str
        key "validationStatus": Union[str, OwnershipVoucherValidationStatus]
        key "version": str
        azure_machine_id: str
        error: ErrorDetail
        id: str
        manufacturer: str
        model_name: str
        serial_number: str
        validation_status: Union[str, OwnershipVoucherValidationStatus]
        version: str


    class azure.mgmt.azurestackhci.types.PackageVersionInfo(TypedDict, total=False):
        key "lastUpdated": str
        key "packageType": str
        key "version": str
        last_updated: str
        package_type: str
        version: str


    class azure.mgmt.azurestackhci.types.PartitionDetails(TypedDict, total=False):
        key "currentDecode": str
        key "currentEncode": str
        key "currentVram": str
        key "partitionId": int
        key "uniqueId": str
        key "workloadDetail": ForwardRef('WorkloadDetails', module='types')
        current_decode: str
        current_encode: str
        current_vram: str
        partition_id: int
        unique_id: str
        workload_detail: WorkloadDetails


    class azure.mgmt.azurestackhci.types.PerNodeExtensionState(TypedDict, total=False):
        key "extension": str
        key "instanceView": ForwardRef('ExtensionInstanceView', module='types')
        key "name": str
        key "state": Union[str, NodeExtensionState]
        key "typeHandlerVersion": str
        extension: str
        instance_view: ExtensionInstanceView
        name: str
        state: Union[str, NodeExtensionState]
        type_handler_version: str


    class azure.mgmt.azurestackhci.types.PerNodeRemoteSupportSession(TypedDict, total=False):
        key "accessLevel": Union[str, AccessLevel]
        key "duration": int
        key "nodeName": str
        key "sessionEndTime": str
        key "sessionStartTime": str
        key "transcriptLocation": str
        access_level: Union[str, AccessLevel]
        duration: int
        node_name: str
        session_end_time: str
        session_start_time: str
        transcript_location: str


    class azure.mgmt.azurestackhci.types.PerNodeState(TypedDict, total=False):
        key "arcInstance": str
        key "arcNodeServicePrincipalObjectId": str
        key "name": str
        key "state": Union[str, NodeArcState]
        arc_instance: str
        arc_node_service_principal_object_id: str
        name: str
        state: Union[str, NodeArcState]


    class azure.mgmt.azurestackhci.types.PhysicalNodes(TypedDict, total=False):
        key "ipv4Address": str
        key "name": str
        ipv4_address: str
        name: str


    class azure.mgmt.azurestackhci.types.PrecheckResult(TypedDict, total=False):
        key "additionalData": str
        key "description": str
        key "displayName": str
        key "healthCheckSource": str
        key "healthCheckTags": Any
        key "name": str
        key "remediation": str
        key "severity": Union[str, Severity]
        key "status": Union[str, Status]
        key "tags": ForwardRef('PrecheckResultTags', module='types')
        key "targetResourceID": str
        key "targetResourceName": str
        key "targetResourceType": str
        key "timestamp": str
        key "title": str
        additional_data: str
        description: str
        display_name: str
        health_check_source: str
        health_check_tags: Any
        name: str
        remediation: str
        severity: Union[str, Severity]
        status: Union[str, Status]
        tags: PrecheckResultTags
        target_resource_id: str
        target_resource_name: str
        target_resource_type: str
        timestamp: str
        title: str


    class azure.mgmt.azurestackhci.types.PrecheckResultTags(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.azurestackhci.types.PrivilegedJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_VOLUME = "DeleteVolume"


    class azure.mgmt.azurestackhci.types.ProvisionOsJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineJobType.PROVISION_OS]]
        key "provisioningRequest": Required[ProvisioningRequest]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('ProvisionOsReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[EdgeMachineJobType.PROVISION_OS]
        provisioning_request: ProvisioningRequest
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: ProvisionOsReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.ProvisionOsReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        percent_complete: int
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.ProvisioningDetails(TypedDict, total=False):
        key "osProfile": Required[OsProvisionProfile]
        os_profile: OsProvisionProfile
        userDetails: list[UserDetails]
        user_details: list[UserDetails]


    class azure.mgmt.azurestackhci.types.ProvisioningRequest(TypedDict, total=False):
        key "customConfiguration": str
        key "deviceConfiguration": ForwardRef('TargetDeviceConfiguration', module='types')
        key "onboardingConfiguration": ForwardRef('OnboardingConfiguration', module='types')
        key "osProfile": Required[OsProvisionProfile]
        key "target": Required[Union[str, ProvisioningOsType]]
        custom_configuration: str
        device_configuration: TargetDeviceConfiguration
        onboarding_configuration: OnboardingConfiguration
        os_profile: OsProvisionProfile
        target: Union[str, ProvisioningOsType]
        userDetails: list[UserDetails]
        user_details: list[UserDetails]


    class azure.mgmt.azurestackhci.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.QosPolicyOverrides(TypedDict, total=False):
        key "bandwidthPercentage_SMB": str
        key "priorityValue8021Action_Cluster": str
        key "priorityValue8021Action_SMB": str
        bandwidth_percentage_smb: str
        priority_value8021_action_cluster: str
        priority_value8021_action_smb: str


    class azure.mgmt.azurestackhci.types.RawCertificateData(TypedDict, total=False):
        certificates: list[str]


    class azure.mgmt.azurestackhci.types.ReconcileArcSettingsRequest(TypedDict, total=False):
        key "properties": ForwardRef('ReconcileArcSettingsRequestProperties', module='types')
        properties: ReconcileArcSettingsRequestProperties


    class azure.mgmt.azurestackhci.types.ReconcileArcSettingsRequestProperties(TypedDict, total=False):
        clusterNodes: list[str]
        cluster_nodes: list[str]


    class azure.mgmt.azurestackhci.types.ReleaseDeviceRequest(TypedDict, total=False):
        key "devices": Required[list[str]]
        devices: list[str]


    class azure.mgmt.azurestackhci.types.RemoteSupportJobNodeSettings(TypedDict, total=False):
        key "connectionErrorMessage": str
        key "connectionStatus": str
        key "createdAt": str
        key "state": str
        key "updatedAt": str
        connection_error_message: str
        connection_status: str
        created_at: str
        state: str
        updated_at: str


    class azure.mgmt.azurestackhci.types.RemoteSupportJobReportedProperties(TypedDict, total=False):
        key "deploymentStatus": ForwardRef('EceActionStatus', module='types')
        key "nodeSettings": ForwardRef('RemoteSupportJobNodeSettings', module='types')
        key "percentComplete": int
        key "validationStatus": ForwardRef('EceActionStatus', module='types')
        deployment_status: EceActionStatus
        node_settings: RemoteSupportJobNodeSettings
        percent_complete: int
        sessionDetails: list[RemoteSupportSession]
        session_details: list[RemoteSupportSession]
        validation_status: EceActionStatus


    class azure.mgmt.azurestackhci.types.RemoteSupportNodeSettings(TypedDict, total=False):
        key "arcResourceId": str
        key "connectionErrorMessage": str
        key "connectionStatus": str
        key "createdAt": str
        key "state": str
        key "transcriptLocation": str
        key "updatedAt": str
        arc_resource_id: str
        connection_error_message: str
        connection_status: str
        created_at: str
        state: str
        transcript_location: str
        updated_at: str


    class azure.mgmt.azurestackhci.types.RemoteSupportProperties(TypedDict, total=False):
        key "accessLevel": Union[str, AccessLevel]
        key "expirationTimeStamp": str
        key "remoteSupportProvisioningState": Union[str, RemoteSupportProvisioningState]
        key "remoteSupportType": Union[str, RemoteSupportType]
        access_level: Union[str, AccessLevel]
        expiration_time_stamp: str
        remoteSupportNodeSettings: list[RemoteSupportNodeSettings]
        remoteSupportSessionDetails: list[PerNodeRemoteSupportSession]
        remote_support_node_settings: list[RemoteSupportNodeSettings]
        remote_support_provisioning_state: Union[str, RemoteSupportProvisioningState]
        remote_support_session_details: list[PerNodeRemoteSupportSession]
        remote_support_type: Union[str, RemoteSupportType]


    class azure.mgmt.azurestackhci.types.RemoteSupportRequest(TypedDict, total=False):
        key "properties": ForwardRef('RemoteSupportRequestProperties', module='types')
        properties: RemoteSupportRequestProperties


    class azure.mgmt.azurestackhci.types.RemoteSupportRequestProperties(TypedDict, total=False):
        key "accessLevel": Union[str, AccessLevel]
        key "expirationTimeStamp": str
        key "remoteSupportType": Union[str, RemoteSupportType]
        access_level: Union[str, AccessLevel]
        expiration_time_stamp: str
        remote_support_type: Union[str, RemoteSupportType]


    class azure.mgmt.azurestackhci.types.RemoteSupportSession(TypedDict, total=False):
        key "accessLevel": Union[str, RemoteSupportAccessLevel]
        key "sessionEndTime": str
        key "sessionId": str
        key "sessionStartTime": str
        key "transcriptLocation": str
        access_level: Union[str, RemoteSupportAccessLevel]
        session_end_time: str
        session_id: str
        session_start_time: str
        transcript_location: str


    class azure.mgmt.azurestackhci.types.RemovePartitionGpuJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "gpuId": str
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineGpuJobType.REMOVE_PARTITION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "vmId": Required[str]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.REMOVE_PARTITION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        vm_id: str


    class azure.mgmt.azurestackhci.types.RepairServerJobServerDetails(TypedDict, total=False):
        key "serverName": Required[str]
        key "serverResourceId": Required[str]
        server_name: str
        server_resource_id: str


    class azure.mgmt.azurestackhci.types.ReportedProperties(TypedDict, total=False):
        key "confidentialVmProfile": ForwardRef('ConfidentialVmProfile', module='types')
        key "deviceState": Union[str, DeviceState]
        key "extensionProfile": ForwardRef('ExtensionProfile', module='types')
        key "lastSyncTimestamp": str
        confidential_vm_profile: ConfidentialVmProfile
        device_state: Union[str, DeviceState]
        extension_profile: ExtensionProfile
        last_sync_timestamp: str


    class azure.mgmt.azurestackhci.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.SanAdapterIPConfig(TypedDict, total=False):
        key "addressPrefix": str
        key "name": str
        key "networkAdapterName": str
        key "vlanId": int
        address_prefix: str
        name: str
        network_adapter_name: str
        vlan_id: int


    class azure.mgmt.azurestackhci.types.SanAdapterProperties(TypedDict, total=False):
        key "bandwidthPercentageSmb": int
        key "jumboPacket": int
        key "priorityValue8021ActionCluster": int
        key "priorityValue8021ActionSmb": int
        bandwidth_percentage_smb: int
        jumbo_packet: int
        priority_value8021_action_cluster: int
        priority_value8021_action_smb: int


    class azure.mgmt.azurestackhci.types.SanClusterNetworkConfig(TypedDict, total=False):
        key "adapterProperties": ForwardRef('SanAdapterProperties', module='types')
        adapterIPConfig: list[SanAdapterIPConfig]
        adapter_ip_config: list[SanAdapterIPConfig]
        adapter_properties: SanAdapterProperties


    class azure.mgmt.azurestackhci.types.SanNetworks(TypedDict, total=False):
        key "clusterNetworkConfig": ForwardRef('SanClusterNetworkConfig', module='types')
        cluster_network_config: SanClusterNetworkConfig


    class azure.mgmt.azurestackhci.types.SbeCredentials(TypedDict, total=False):
        key "eceSecretName": str
        key "secretLocation": str
        key "secretName": str
        ece_secret_name: str
        secret_location: str
        secret_name: str


    class azure.mgmt.azurestackhci.types.SbeDeploymentInfo(TypedDict, total=False):
        key "family": str
        key "publisher": str
        key "sbeManifestCreationDate": str
        key "sbeManifestSource": str
        key "version": str
        family: str
        publisher: str
        sbe_manifest_creation_date: str
        sbe_manifest_source: str
        version: str


    class azure.mgmt.azurestackhci.types.SbeDeploymentPackageInfo(TypedDict, total=False):
        key "code": str
        key "message": str
        key "sbeManifest": str
        code: str
        message: str
        sbe_manifest: str


    class azure.mgmt.azurestackhci.types.SbePartnerInfo(TypedDict, total=False):
        key "sbeDeploymentInfo": ForwardRef('SbeDeploymentInfo', module='types')
        credentialList: list[SbeCredentials]
        credential_list: list[SbeCredentials]
        partnerProperties: list[SbePartnerProperties]
        partner_properties: list[SbePartnerProperties]
        sbe_deployment_info: SbeDeploymentInfo


    class azure.mgmt.azurestackhci.types.SbePartnerProperties(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.azurestackhci.types.ScaleUnits(TypedDict, total=False):
        key "deploymentData": Required[DeploymentData]
        key "sbePartnerInfo": ForwardRef('SbePartnerInfo', module='types')
        deployment_data: DeploymentData
        sbe_partner_info: SbePartnerInfo


    class azure.mgmt.azurestackhci.types.SdnIntegration(TypedDict, total=False):
        key "networkController": ForwardRef('NetworkController', module='types')
        network_controller: NetworkController


    class azure.mgmt.azurestackhci.types.SdnProperties(TypedDict, total=False):
        key "sdnApiAddress": str
        key "sdnDomainName": str
        key "sdnStatus": Union[str, SdnStatus]
        sdn_api_address: str
        sdn_domain_name: str
        sdn_status: Union[str, SdnStatus]


    class azure.mgmt.azurestackhci.types.SecretsLocationDetails(TypedDict, total=False):
        key "secretsLocation": Required[str]
        key "secretsType": Required[Union[str, SecretsType]]
        secrets_location: str
        secrets_type: Union[str, SecretsType]


    class azure.mgmt.azurestackhci.types.SecretsLocationsChangeRequest(TypedDict, total=False):
        properties: list[SecretsLocationDetails]


    class azure.mgmt.azurestackhci.types.SecurityComplianceStatus(TypedDict, total=False):
        key "dataAtRestEncrypted": Union[str, ComplianceStatus]
        key "dataInTransitProtected": Union[str, ComplianceStatus]
        key "lastUpdated": str
        key "securedCoreCompliance": Union[str, ComplianceStatus]
        key "wdacCompliance": Union[str, ComplianceStatus]
        data_at_rest_encrypted: Union[str, ComplianceStatus]
        data_in_transit_protected: Union[str, ComplianceStatus]
        last_updated: str
        secured_core_compliance: Union[str, ComplianceStatus]
        wdac_compliance: Union[str, ComplianceStatus]


    class azure.mgmt.azurestackhci.types.SecurityProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "securedCoreComplianceAssignment": Union[str, ComplianceAssignmentType]
        key "securityComplianceStatus": ForwardRef('SecurityComplianceStatus', module='types')
        key "smbEncryptionForIntraClusterTrafficComplianceAssignment": Union[str, ComplianceAssignmentType]
        key "wdacComplianceAssignment": Union[str, ComplianceAssignmentType]
        provisioning_state: Union[str, ProvisioningState]
        secured_core_compliance_assignment: Union[str, ComplianceAssignmentType]
        security_compliance_status: SecurityComplianceStatus
        smb_encryption_for_intra_cluster_traffic_compliance_assignment: Union[str, ComplianceAssignmentType]
        wdac_compliance_assignment: Union[str, ComplianceAssignmentType]


    class azure.mgmt.azurestackhci.types.SecuritySetting(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.ServiceConfiguration(TypedDict, total=False):
        key "port": Required[int]
        key "serviceName": Required[Union[str, ServiceName]]
        port: int
        service_name: Union[str, ServiceName]


    class azure.mgmt.azurestackhci.types.SiteDetails(TypedDict, total=False):
        key "deviceConfiguration": ForwardRef('TargetDeviceConfiguration', module='types')
        key "siteResourceId": Required[str]
        device_configuration: TargetDeviceConfiguration
        site_resource_id: str


    class azure.mgmt.azurestackhci.types.SoftwareAssuranceChangeRequest(TypedDict, total=False):
        key "properties": ForwardRef('SoftwareAssuranceChangeRequestProperties', module='types')
        properties: SoftwareAssuranceChangeRequestProperties


    class azure.mgmt.azurestackhci.types.SoftwareAssuranceChangeRequestProperties(TypedDict, total=False):
        key "softwareAssuranceIntent": Union[str, SoftwareAssuranceIntent]
        software_assurance_intent: Union[str, SoftwareAssuranceIntent]


    class azure.mgmt.azurestackhci.types.SoftwareAssuranceProperties(TypedDict, total=False):
        key "lastUpdated": str
        key "softwareAssuranceIntent": Union[str, SoftwareAssuranceIntent]
        key "softwareAssuranceStatus": Union[str, SoftwareAssuranceStatus]
        last_updated: str
        software_assurance_intent: Union[str, SoftwareAssuranceIntent]
        software_assurance_status: Union[str, SoftwareAssuranceStatus]


    class azure.mgmt.azurestackhci.types.Step(TypedDict, total=False):
        key "description": str
        key "endTimeUtc": str
        key "errorMessage": str
        key "expectedExecutionTime": str
        key "lastUpdatedTimeUtc": str
        key "name": str
        key "startTimeUtc": str
        key "status": str
        description: str
        end_time_utc: str
        error_message: str
        expected_execution_time: str
        last_updated_time_utc: str
        name: str
        start_time_utc: str
        status: str
        steps: list[Step]


    class azure.mgmt.azurestackhci.types.Storage(TypedDict, total=False):
        key "configurationMode": str
        key "s2d": ForwardRef('StorageS2dConfig', module='types')
        key "san": ForwardRef('StorageSanConfig', module='types')
        key "storageType": Union[str, StorageType]
        configuration_mode: str
        s2_d: StorageS2dConfig
        san: StorageSanConfig
        storage_type: Union[str, StorageType]


    class azure.mgmt.azurestackhci.types.StorageConfiguration(TypedDict, total=False):
        key "partitionSize": str
        partition_size: str


    class azure.mgmt.azurestackhci.types.StorageProfile(TypedDict, total=False):
        key "poolableDisksCount": int
        disks: list[EdgeMachineDiskInfo]
        poolable_disks_count: int


    class azure.mgmt.azurestackhci.types.StorageS2dConfig(TypedDict, total=False):
        key "overprovisioningRatio": Union[str, OverprovisioningRatio]
        key "volumeType": Union[str, VolumeType]
        overprovisioning_ratio: Union[str, OverprovisioningRatio]
        volume_type: Union[str, VolumeType]


    class azure.mgmt.azurestackhci.types.StorageSanConfig(TypedDict, total=False):
        key "infraPerfLunId": str
        key "infraVolLunId": str
        infra_perf_lun_id: str
        infra_vol_lun_id: str


    class azure.mgmt.azurestackhci.types.SwitchDetail(TypedDict, total=False):
        key "switchName": str
        key "switchType": str
        extensions: list[SwitchExtension]
        switch_name: str
        switch_type: str


    class azure.mgmt.azurestackhci.types.SwitchExtension(TypedDict, total=False):
        key "extensionEnabled": bool
        key "extensionName": str
        key "switchId": str
        extension_enabled: bool
        extension_name: str
        switch_id: str


    class azure.mgmt.azurestackhci.types.SwitchModeGpuJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "gpuId": str
        key "jobId": str
        key "jobType": Required[Literal[EdgeMachineGpuJobType.SWITCH_MODE]]
        key "mode": Required[Union[str, GpuMode]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        gpu_id: str
        job_id: str
        job_type: Literal[EdgeMachineGpuJobType.SWITCH_MODE]
        mode: Union[str, GpuMode]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.SyncConfigurationJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[DiskJobType.SYNC_CONFIGURATION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('DiskJobReportedProperties', module='types')
        key "resolutionStrategy": Required[Union[str, ResolutionStrategy]]
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[DiskJobType.SYNC_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: DiskJobReportedProperties
        resolution_strategy: Union[str, ResolutionStrategy]
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.SyncConfigurationNetworkAdapterJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "error": ForwardRef('ErrorDetail', module='types')
        key "jobId": str
        key "jobType": Required[Literal[NetworkAdapterJobType.SYNC_CONFIGURATION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('NetworkAdapterJobReportedProperties', module='types')
        key "resolutionStrategy": Required[Union[str, ResolutionStrategy]]
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        error: ErrorDetail
        job_id: str
        job_type: Literal[NetworkAdapterJobType.SYNC_CONFIGURATION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: NetworkAdapterJobReportedProperties
        resolution_strategy: Union[str, ResolutionStrategy]
        start_time_utc: str
        status: Union[str, JobStatus]


    class azure.mgmt.azurestackhci.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.azurestackhci.types.TargetDeviceConfiguration(TypedDict, total=False):
        key "hostName": str
        key "network": ForwardRef('NetworkConfiguration', module='types')
        key "storage": ForwardRef('StorageConfiguration', module='types')
        key "time": ForwardRef('TimeConfiguration', module='types')
        key "webProxy": ForwardRef('WebProxyConfiguration', module='types')
        host_name: str
        network: NetworkConfiguration
        storage: StorageConfiguration
        time: TimeConfiguration
        web_proxy: WebProxyConfiguration


    class azure.mgmt.azurestackhci.types.TimeConfiguration(TypedDict, total=False):
        key "primaryTimeServer": str
        key "secondaryTimeServer": str
        key "timeZone": str
        primary_time_server: str
        secondary_time_server: str
        time_zone: str


    class azure.mgmt.azurestackhci.types.TrackedResource(Resource):
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


    class azure.mgmt.azurestackhci.types.Update(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('UpdateProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: UpdateProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.UpdatePrerequisite(TypedDict, total=False):
        key "packageName": str
        key "updateType": str
        key "version": str
        package_name: str
        update_type: str
        version: str


    class azure.mgmt.azurestackhci.types.UpdateProperties(TypedDict, total=False):
        key "additionalProperties": str
        key "availabilityType": Union[str, AvailabilityType]
        key "description": str
        key "displayName": str
        key "healthCheckDate": str
        key "healthState": Union[str, HealthState]
        key "installedDate": str
        key "minSbeVersionRequired": str
        key "packagePath": str
        key "packageSizeInMb": float
        key "packageType": str
        key "provisioningState": Union[str, ProvisioningState]
        key "publisher": str
        key "rebootRequired": Union[str, RebootRequirement]
        key "releaseLink": str
        key "state": Union[str, State]
        key "updateStateProperties": ForwardRef('UpdateStateProperties', module='types')
        key "version": str
        additional_properties: str
        availability_type: Union[str, AvailabilityType]
        componentVersions: list[PackageVersionInfo]
        component_versions: list[PackageVersionInfo]
        description: str
        display_name: str
        healthCheckResult: list[PrecheckResult]
        health_check_date: str
        health_check_result: list[PrecheckResult]
        health_state: Union[str, HealthState]
        installed_date: str
        min_sbe_version_required: str
        package_path: str
        package_size_in_mb: float
        package_type: str
        prerequisites: list[UpdatePrerequisite]
        provisioning_state: Union[str, ProvisioningState]
        publisher: str
        reboot_required: Union[str, RebootRequirement]
        release_link: str
        state: Union[str, State]
        update_state_properties: UpdateStateProperties
        version: str


    class azure.mgmt.azurestackhci.types.UpdateRun(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('UpdateRunProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: UpdateRunProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.UpdateRunProperties(TypedDict, total=False):
        key "duration": str
        key "lastUpdatedTime": str
        key "progress": ForwardRef('Step', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, UpdateRunPropertiesState]
        key "timeStarted": str
        duration: str
        last_updated_time: str
        progress: Step
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, UpdateRunPropertiesState]
        time_started: str


    class azure.mgmt.azurestackhci.types.UpdateStateProperties(TypedDict, total=False):
        key "notifyMessage": str
        key "progressPercentage": float
        notify_message: str
        progress_percentage: float


    class azure.mgmt.azurestackhci.types.UpdateSummaries(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('UpdateSummariesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: UpdateSummariesProperties
        system_data: SystemData
        type: str


    class azure.mgmt.azurestackhci.types.UpdateSummariesProperties(TypedDict, total=False):
        key "currentOemVersion": str
        key "currentSbeVersion": str
        key "currentVersion": str
        key "hardwareModel": str
        key "healthCheckDate": str
        key "healthState": Union[str, HealthState]
        key "lastChecked": str
        key "lastUpdated": str
        key "oemFamily": str
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, UpdateSummariesPropertiesState]
        current_oem_version: str
        current_sbe_version: str
        current_version: str
        hardware_model: str
        healthCheckResult: list[PrecheckResult]
        health_check_date: str
        health_check_result: list[PrecheckResult]
        health_state: Union[str, HealthState]
        last_checked: str
        last_updated: str
        oem_family: str
        packageVersions: list[PackageVersionInfo]
        package_versions: list[PackageVersionInfo]
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, UpdateSummariesPropertiesState]


    class azure.mgmt.azurestackhci.types.UploadCertificateRequest(TypedDict, total=False):
        key "properties": ForwardRef('RawCertificateData', module='types')
        properties: RawCertificateData


    class azure.mgmt.azurestackhci.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.azurestackhci.types.UserDetails(TypedDict, total=False):
        key "secretLocation": str
        key "secretType": Required[Union[str, SecretType]]
        key "userName": Required[str]
        secret_location: str
        secret_type: Union[str, SecretType]
        sshPubKey: list[str]
        ssh_pub_key: list[str]
        user_name: str


    class azure.mgmt.azurestackhci.types.ValidateOwnershipVouchersRequest(TypedDict, total=False):
        key "ownershipVoucherDetails": Required[list[OwnershipVoucherDetails]]
        ownership_voucher_details: list[OwnershipVoucherDetails]


    class azure.mgmt.azurestackhci.types.ValidateRequest(TypedDict, total=False):
        key "additionalInfo": str
        key "edgeDeviceIds": Required[list[str]]
        additional_info: str
        edge_device_ids: list[str]


    class azure.mgmt.azurestackhci.types.VmConnectJobDetails(TypedDict, total=False):
        key "nodeName": str
        key "vmName": Required[str]
        key "vmResourceGroupName": str
        node_name: str
        vm_name: str
        vm_resource_group_name: str


    class azure.mgmt.azurestackhci.types.VmConnectProvisionJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.VM_CONNECT_PROVISION]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "vmConnectProvisionJobDetails": Required[list[VmConnectJobDetails]]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.VM_CONNECT_PROVISION]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        vm_connect_provision_job_details: list[VmConnectJobDetails]


    class azure.mgmt.azurestackhci.types.VmConnectRemoveJobProperties(TypedDict, total=False):
        key "deploymentMode": Union[str, DeploymentMode]
        key "endTimeUtc": str
        key "jobId": str
        key "jobType": Required[Literal[HciJobType.VM_CONNECT_REMOVE]]
        key "provisioningState": Union[str, ProvisioningState]
        key "reportedProperties": ForwardRef('JobReportedProperties', module='types')
        key "startTimeUtc": str
        key "status": Union[str, JobStatus]
        key "vmConnectRemoveJobDetails": Required[list[VmConnectJobDetails]]
        deployment_mode: Union[str, DeploymentMode]
        end_time_utc: str
        job_id: str
        job_type: Literal[HciJobType.VM_CONNECT_REMOVE]
        provisioning_state: Union[str, ProvisioningState]
        reported_properties: JobReportedProperties
        start_time_utc: str
        status: Union[str, JobStatus]
        vm_connect_remove_job_details: list[VmConnectJobDetails]


    class azure.mgmt.azurestackhci.types.VolumeConfiguration(TypedDict, total=False):
        key "reserved": str
        reserved: str


    class azure.mgmt.azurestackhci.types.VolumeReportedProperties(TypedDict, total=False):
        key "fileSystem": str
        key "isBoot": bool
        key "name": str
        key "offsetInBytes": int
        key "parentDiskId": str
        key "partitionId": str
        key "path": str
        key "sizeInBytes": str
        key "sizeRemainingInBytes": str
        file_system: str
        is_boot: bool
        name: str
        offset_in_bytes: int
        parent_disk_id: str
        partition_id: str
        path: str
        size_in_bytes: str
        size_remaining_in_bytes: str


    class azure.mgmt.azurestackhci.types.WebProxyConfiguration(TypedDict, total=False):
        key "connectionUri": str
        key "port": str
        bypassList: list[str]
        bypass_list: list[str]
        connection_uri: str
        port: str


    class azure.mgmt.azurestackhci.types.WifiConfigurationDesiredProperties(TypedDict, total=False):
        key "authenticationType": Union[str, AuthenticationType]
        key "eapMethod": Union[str, EAPMethod]
        key "ssid": str
        key "username": str
        key "wifiSecret": ForwardRef('WifiSecret', module='types')
        authentication_type: Union[str, AuthenticationType]
        eap_method: Union[str, EAPMethod]
        ssid: str
        username: str
        wifi_secret: WifiSecret


    class azure.mgmt.azurestackhci.types.WifiSecret(TypedDict, total=False):
        key "secretLocation": str
        key "secretName": str
        key "secretType": Union[str, WifiSecretType]
        secret_location: str
        secret_name: str
        secret_type: Union[str, WifiSecretType]


    class azure.mgmt.azurestackhci.types.WorkloadDetails(TypedDict, total=False):
        key "slotLocation": str
        key "workloadId": str
        key "workloadName": str
        key "workloadStatus": str
        key "workloadType": str
        slot_location: str
        workload_id: str
        workload_name: str
        workload_status: str
        workload_type: str


```