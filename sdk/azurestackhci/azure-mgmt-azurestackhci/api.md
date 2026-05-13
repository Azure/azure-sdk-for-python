```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.azurestackhci

    class azure.mgmt.azurestackhci.AzureStackHCIClient: implements ContextManager 
        arc_settings: ArcSettingsOperations
        cluster_jobs: ClusterJobsOperations
        clusters: ClustersOperations
        deployment_settings: DeploymentSettingsOperations
        device_pools: DevicePoolsOperations
        edge_device_jobs: EdgeDeviceJobsOperations
        edge_devices: EdgeDevicesOperations
        edge_machine_jobs: EdgeMachineJobsOperations
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
        edge_machine_jobs: EdgeMachineJobsOperations
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
                reconcile_arc_settings_request: JSON, 
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
                arc_setting: JSON, 
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
                arc_setting: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name']}, api_versions_list=['2026-04-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> ClusterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                change_ring_request: JSON, 
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
                remote_support_request: JSON, 
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
                software_assurance_change_request: JSON, 
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
                log_collection_request: JSON, 
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
                body: JSON, 
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
                upload_certificate_request: JSON, 
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
                cluster: JSON, 
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
                cluster: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name']}, api_versions_list=['2026-04-01-preview'])
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
                body: JSON, 
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
                properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> DevicePool: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                validate_request: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name']}, api_versions_list=['2026-04-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachineJob]: ...


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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name']}, api_versions_list=['2026-04-01-preview'])
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
                properties: JSON, 
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

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> EdgeMachine: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EdgeMachine]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                extension: JSON, 
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
                extension: JSON, 
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
                extension_upgrade_parameters: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'os_image_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                location: str, 
                os_image_name: str, 
                **kwargs: Any
            ) -> OsImage: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                validation_request: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'platform_update_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                location: str, 
                platform_update_name: str, 
                **kwargs: Any
            ) -> PlatformUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'publisher_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'update_content_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        async def get(
                self, 
                location: str, 
                update_content_name: str, 
                **kwargs: Any
            ) -> UpdateContent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                update_runs_properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-01-preview'])
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
                body: JSON, 
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
                update_location_properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'update_name']}, api_versions_list=['2026-04-01-preview'])
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
                update_properties: JSON, 
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


    class azure.mgmt.azurestackhci.models.AvailabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"
        NOTIFY = "Notify"
        ONLINE = "Online"


    class azure.mgmt.azurestackhci.models.ChangeRingRequest(_Model):
        properties: Optional[ChangeRingRequestProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeRingRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.azurestackhci.models.ChangeRingRequestProperties(_Model):
        target_ring: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_ring: Optional[str] = ...
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


    class azure.mgmt.azurestackhci.models.ClusterSdnProperties(SdnProperties):
        sdn_api_address: str
        sdn_domain_name: str
        sdn_integration_intent: Optional[Union[str, SdnIntegrationIntent]]
        sdn_status: Union[str, SdnStatus]


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


    class azure.mgmt.azurestackhci.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.azurestackhci.models.DefaultExtensionDetails(_Model):
        category: Optional[str]
        consent_time: Optional[datetime]


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


    class azure.mgmt.azurestackhci.models.EdgeMachineNetworkProfile(_Model):
        nic_details: Optional[list[EdgeMachineNicDetail]]
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
        extension_profile: Optional[ExtensionProfile]
        hardware_profile: Optional[HardwareProfile]
        last_updated: Optional[datetime]
        network_profile: Optional[EdgeMachineNetworkProfile]
        os_profile: Optional[OsProfile]
        sbe_deployment_package_info: Optional[SbeDeploymentPackageInfo]
        storage_profile: Optional[StorageProfile]


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
        CONFIGURE_CVM = "ConfigureCVM"
        CONFIGURE_SDN_INTEGRATION = "ConfigureSdnIntegration"


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
        custom_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
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


    class azure.mgmt.azurestackhci.models.ReportedProperties(_Model):
        confidential_vm_profile: Optional[ConfidentialVmProfile]
        device_state: Optional[Union[str, DeviceState]]
        extension_profile: Optional[ExtensionProfile]
        last_sync_timestamp: Optional[datetime]


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
        S2D = "S2D"
        SAN = "SAN"
        SANS2D = "SANS2D"


    class azure.mgmt.azurestackhci.models.SwitchDetail(_Model):
        extensions: Optional[list[SwitchExtension]]
        switch_name: Optional[str]
        switch_type: Optional[str]


    class azure.mgmt.azurestackhci.models.SwitchExtension(_Model):
        extension_enabled: Optional[bool]
        extension_name: Optional[str]
        switch_id: Optional[str]


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


    class azure.mgmt.azurestackhci.models.WindowsServerSubscription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


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
                reconcile_arc_settings_request: JSON, 
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
                arc_setting: JSON, 
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
                arc_setting: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name']}, api_versions_list=['2026-04-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'jobs_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> ClusterJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                change_ring_request: JSON, 
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
                remote_support_request: JSON, 
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
                software_assurance_change_request: JSON, 
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
                log_collection_request: JSON, 
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
                body: JSON, 
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
                upload_certificate_request: JSON, 
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
                cluster: JSON, 
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
                cluster: JSON, 
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
                resource: JSON, 
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
                body: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name']}, api_versions_list=['2026-04-01-preview'])
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
                body: JSON, 
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
                properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'device_pool_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                device_pool_name: str, 
                **kwargs: Any
            ) -> DevicePool: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DevicePool]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                resource: JSON, 
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
                resource: JSON, 
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
                validate_request: JSON, 
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name']}, api_versions_list=['2026-04-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'jobs_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                jobs_name: str, 
                **kwargs: Any
            ) -> EdgeMachineJob: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachineJob]: ...


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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name']}, api_versions_list=['2026-04-01-preview'])
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
                properties: JSON, 
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

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'edge_machine_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                edge_machine_name: str, 
                **kwargs: Any
            ) -> EdgeMachine: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EdgeMachine]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                extension: JSON, 
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
                extension: JSON, 
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
                extension_upgrade_parameters: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'os_image_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                location: str, 
                os_image_name: str, 
                **kwargs: Any
            ) -> OsImage: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                validation_request: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'platform_update_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                location: str, 
                platform_update_name: str, 
                **kwargs: Any
            ) -> PlatformUpdate: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'publisher_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                publisher_name: str, 
                **kwargs: Any
            ) -> Publisher: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                resource: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'update_content_name', 'accept']}, api_versions_list=['2026-04-01-preview'])
        def get(
                self, 
                location: str, 
                update_content_name: str, 
                **kwargs: Any
            ) -> UpdateContent: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-04-01-preview'])
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
                update_runs_properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name']}, api_versions_list=['2026-04-01-preview'])
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
                body: JSON, 
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
                update_location_properties: JSON, 
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
        @api_version_validation(method_added_on='2026-04-01-preview', params_added_on={'2026-04-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cluster_name', 'update_name']}, api_versions_list=['2026-04-01-preview'])
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
                update_properties: JSON, 
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


```