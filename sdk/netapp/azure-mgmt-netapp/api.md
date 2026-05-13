```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.netapp

    class azure.mgmt.netapp.NetAppManagementClient: implements ContextManager 
        accounts: AccountsOperations
        backup_policies: BackupPoliciesOperations
        backup_vaults: BackupVaultsOperations
        backups: BackupsOperations
        backups_under_account: BackupsUnderAccountOperations
        backups_under_backup_vault: BackupsUnderBackupVaultOperations
        backups_under_volume: BackupsUnderVolumeOperations
        buckets: BucketsOperations
        caches: CachesOperations
        net_app_resource: NetAppResourceOperations
        net_app_resource_quota_limits: NetAppResourceQuotaLimitsOperations
        net_app_resource_quota_limits_account: NetAppResourceQuotaLimitsAccountOperations
        net_app_resource_region_infos: NetAppResourceRegionInfosOperations
        net_app_resource_usages: NetAppResourceUsagesOperations
        operations: Operations
        pools: PoolsOperations
        ransomware_reports: RansomwareReportsOperations
        snapshot_policies: SnapshotPoliciesOperations
        snapshots: SnapshotsOperations
        subvolumes: SubvolumesOperations
        volume_groups: VolumeGroupsOperations
        volume_quota_rules: VolumeQuotaRulesOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.netapp.aio

    class azure.mgmt.netapp.aio.NetAppManagementClient: implements AsyncContextManager 
        accounts: AccountsOperations
        backup_policies: BackupPoliciesOperations
        backup_vaults: BackupVaultsOperations
        backups: BackupsOperations
        backups_under_account: BackupsUnderAccountOperations
        backups_under_backup_vault: BackupsUnderBackupVaultOperations
        backups_under_volume: BackupsUnderVolumeOperations
        buckets: BucketsOperations
        caches: CachesOperations
        net_app_resource: NetAppResourceOperations
        net_app_resource_quota_limits: NetAppResourceQuotaLimitsOperations
        net_app_resource_quota_limits_account: NetAppResourceQuotaLimitsAccountOperations
        net_app_resource_region_infos: NetAppResourceRegionInfosOperations
        net_app_resource_usages: NetAppResourceUsagesOperations
        operations: Operations
        pools: PoolsOperations
        ransomware_reports: RansomwareReportsOperations
        snapshot_policies: SnapshotPoliciesOperations
        snapshots: SnapshotsOperations
        subvolumes: SubvolumesOperations
        volume_groups: VolumeGroupsOperations
        volume_quota_rules: VolumeQuotaRulesOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.netapp.aio.operations

    class azure.mgmt.netapp.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[ChangeKeyVault] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: NetAppAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_get_change_key_vault_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[GetKeyVaultStatusResponse]: ...

        @distributed_trace_async
        async def begin_renew_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[EncryptionTransitionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: NetAppAccountPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetAppAccount]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> NetAppAccount: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetAppAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[NetAppAccount]: ...


    class azure.mgmt.netapp.aio.operations.BackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: BackupPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: BackupPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> BackupPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupPolicy]: ...


    class azure.mgmt.netapp.aio.operations.BackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: BackupVault, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: BackupVaultPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[BackupVault]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                **kwargs: Any
            ) -> BackupVault: ...

        @distributed_trace
        def list_by_net_app_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BackupVault]: ...


    class azure.mgmt.netapp.aio.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Backup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[BackupPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Backup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> Backup: ...

        @distributed_trace_async
        async def get_latest_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> BackupStatus: ...

        @distributed_trace_async
        async def get_volume_latest_restore_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> RestoreStatus: ...

        @distributed_trace
        def list_by_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Backup]: ...


    class azure.mgmt.netapp.aio.operations.BackupsUnderAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: BackupsMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.netapp.aio.operations.BackupsUnderBackupVaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: BackupRestoreFiles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.netapp.aio.operations.BackupsUnderVolumeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: BackupsMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.netapp.aio.operations.BucketsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: Bucket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketCredentialsExpiry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def begin_refresh_certificate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Bucket]: ...

        @overload
        async def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketCredentialsExpiry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @overload
        async def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @overload
        async def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> Bucket: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Bucket]: ...


    class azure.mgmt.netapp.aio.operations.CachesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: PoolChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def begin_reset_smb_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: CacheUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cache]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> Cache: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01', params_added_on={'2026-01-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'accept']}, api_versions_list=['2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cache]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        async def list_peering_passphrases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> PeeringPassphrases: ...


    class azure.mgmt.netapp.aio.operations.NetAppResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: UpdateNetworkSiblingSetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSiblingSet]: ...

        @overload
        async def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSiblingSet]: ...

        @overload
        async def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSiblingSet]: ...

        @overload
        async def check_file_path_availability(
                self, 
                location: str, 
                body: FilePathAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_file_path_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_file_path_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: ResourceNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_quota_availability(
                self, 
                location: str, 
                body: QuotaAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_quota_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def check_quota_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        async def query_network_sibling_set(
                self, 
                location: str, 
                body: QueryNetworkSiblingSetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @overload
        async def query_network_sibling_set(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @overload
        async def query_network_sibling_set(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @distributed_trace_async
        async def query_region_info(
                self, 
                location: str, 
                **kwargs: Any
            ) -> RegionInfo: ...


    class azure.mgmt.netapp.aio.operations.NetAppResourceQuotaLimitsAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'quota_limit_name', 'accept']}, api_versions_list=['2025-08-01', '2025-09-01', '2025-12-01', '2025-12-15-preview', '2026-01-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                quota_limit_name: str, 
                **kwargs: Any
            ) -> QuotaItem: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2025-09-01', '2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaItem]: ...


    class azure.mgmt.netapp.aio.operations.NetAppResourceQuotaLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                quota_limit_name: str, 
                **kwargs: Any
            ) -> QuotaItem: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaItem]: ...


    class azure.mgmt.netapp.aio.operations.NetAppResourceRegionInfosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> RegionInfoResource: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegionInfoResource]: ...


    class azure.mgmt.netapp.aio.operations.NetAppResourceUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                usage_type: str, 
                **kwargs: Any
            ) -> UsageResult: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UsageResult]: ...


    class azure.mgmt.netapp.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.netapp.aio.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: CapacityPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: CapacityPoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapacityPool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> CapacityPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CapacityPool]: ...


    class azure.mgmt.netapp.aio.operations.RansomwareReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: RansomwareSuspectsClearRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-12-01', params_added_on={'2025-12-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'ransomware_report_name', 'accept']}, api_versions_list=['2025-12-01', '2025-12-15-preview', '2026-01-01'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                **kwargs: Any
            ) -> RansomwareReport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01', params_added_on={'2025-12-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'accept']}, api_versions_list=['2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RansomwareReport]: ...


    class azure.mgmt.netapp.aio.operations.SnapshotPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: SnapshotPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SnapshotPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SnapshotPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SnapshotPolicy]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: SnapshotPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SnapshotPolicy]: ...

        @distributed_trace_async
        async def list_volumes(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> SnapshotPolicyVolumeList: ...


    class azure.mgmt.netapp.aio.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: SnapshotRestoreFiles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: SnapshotPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Snapshot]: ...


    class azure.mgmt.netapp.aio.operations.SubvolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: SubvolumeInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_get_metadata(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: SubvolumePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SubvolumeInfo]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> SubvolumeInfo: ...

        @distributed_trace
        def list_by_volume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SubvolumeInfo]: ...


    class azure.mgmt.netapp.aio.operations.VolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: VolumeGroupDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupDetails]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupDetails]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroupDetails]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroupDetails: ...

        @distributed_trace
        def list_by_net_app_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VolumeGroup]: ...


    class azure.mgmt.netapp.aio.operations.VolumeQuotaRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: VolumeQuotaRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: VolumeQuotaRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeQuotaRule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                **kwargs: Any
            ) -> VolumeQuotaRule: ...

        @distributed_trace
        def list_by_volume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VolumeQuotaRule]: ...


    class azure.mgmt.netapp.aio.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_authorize_external_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SvmPeerCommandResponse]: ...

        @overload
        async def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: AuthorizeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[BreakFileLocksRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[BreakReplicationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_finalize_external_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_finalize_relocation(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: GetGroupIdListForLDAPUserRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        async def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        async def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        async def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[QuotaReportFilterRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ListQuotaReportResult]: ...

        @overload
        async def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ListQuotaReportResult]: ...

        @overload
        async def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ListQuotaReportResult]: ...

        @overload
        async def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: PeerClusterForVolumeMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPeerCommandResponse]: ...

        @overload
        async def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPeerCommandResponse]: ...

        @overload
        async def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ClusterPeerCommandResponse]: ...

        @distributed_trace_async
        async def begin_perform_replication_transfer(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: PoolChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_populate_availability_zone(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def begin_re_initialize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: ReestablishReplicationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[RelocateVolumeRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_reset_cifs_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_resync_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: VolumeRevert, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_revert_relocation(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_split_clone_from_parent(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: VolumePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Volume]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[ListReplicationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Replication]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Replication]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[Replication]: ...

        @distributed_trace_async
        async def replication_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ReplicationStatus: ...


namespace azure.mgmt.netapp.models

    class azure.mgmt.netapp.models.AcceptGrowCapacityPoolForShortTermCloneSplit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        DECLINED = "Declined"


    class azure.mgmt.netapp.models.AccountEncryption(_Model):
        identity: Optional[EncryptionIdentity]
        key_source: Optional[Union[str, KeySource]]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EncryptionIdentity] = ..., 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.AccountProperties(_Model):
        active_directories: Optional[list[ActiveDirectory]]
        disable_showmount: Optional[bool]
        encryption: Optional[AccountEncryption]
        multi_ad_status: Optional[Union[str, MultiAdStatus]]
        nfs_v4_id_domain: Optional[str]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_directories: Optional[list[ActiveDirectory]] = ..., 
                encryption: Optional[AccountEncryption] = ..., 
                nfs_v4_id_domain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ActiveDirectory(_Model):
        active_directory_id: Optional[str]
        ad_name: Optional[str]
        administrators: Optional[list[str]]
        aes_encryption: Optional[bool]
        allow_local_nfs_users_with_ldap: Optional[bool]
        backup_operators: Optional[list[str]]
        dns: Optional[str]
        domain: Optional[str]
        encrypt_dc_connections: Optional[bool]
        kdc_ip: Optional[str]
        ldap_over_tls: Optional[bool]
        ldap_search_scope: Optional[LdapSearchScopeOpt]
        ldap_signing: Optional[bool]
        organizational_unit: Optional[str]
        password: Optional[str]
        preferred_servers_for_ldap_client: Optional[str]
        security_operators: Optional[list[str]]
        server_root_ca_certificate: Optional[str]
        site: Optional[str]
        smb_server_name: Optional[str]
        status: Optional[Union[str, ActiveDirectoryStatus]]
        status_details: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_directory_id: Optional[str] = ..., 
                ad_name: Optional[str] = ..., 
                administrators: Optional[list[str]] = ..., 
                aes_encryption: Optional[bool] = ..., 
                allow_local_nfs_users_with_ldap: Optional[bool] = ..., 
                backup_operators: Optional[list[str]] = ..., 
                dns: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                encrypt_dc_connections: Optional[bool] = ..., 
                kdc_ip: Optional[str] = ..., 
                ldap_over_tls: Optional[bool] = ..., 
                ldap_search_scope: Optional[LdapSearchScopeOpt] = ..., 
                ldap_signing: Optional[bool] = ..., 
                organizational_unit: Optional[str] = ..., 
                password: Optional[str] = ..., 
                preferred_servers_for_ldap_client: Optional[str] = ..., 
                security_operators: Optional[list[str]] = ..., 
                server_root_ca_certificate: Optional[str] = ..., 
                site: Optional[str] = ..., 
                smb_server_name: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ActiveDirectoryStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        DELETED = "Deleted"
        ERROR = "Error"
        IN_USE = "InUse"
        UPDATING = "Updating"


    class azure.mgmt.netapp.models.ActualRansomwareProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        LEARNING = "Learning"
        PAUSED = "Paused"


    class azure.mgmt.netapp.models.ApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ORACLE = "ORACLE"
        SAP_HANA = "SAP-HANA"


    class azure.mgmt.netapp.models.AuthorizeRequest(_Model):
        remote_volume_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                remote_volume_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.AvsDataStore(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.AzureKeyVaultDetails(_Model):
        certificate_akv_details: Optional[CertificateAkvDetails]
        credentials_akv_details: Optional[CredentialsAkvDetails]

        @overload
        def __init__(
                self, 
                *, 
                certificate_akv_details: Optional[CertificateAkvDetails] = ..., 
                credentials_akv_details: Optional[CredentialsAkvDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Backup(ProxyResource):
        id: str
        name: str
        properties: BackupProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: BackupProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BackupPatch(_Model):
        properties: Optional[BackupPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BackupPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BackupPatchProperties(_Model):
        label: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                label: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BackupPolicy(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: BackupPolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: BackupPolicyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BackupPolicyPatch(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[BackupPolicyProperties]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[BackupPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BackupPolicyProperties(_Model):
        backup_policy_id: Optional[str]
        daily_backups_to_keep: Optional[int]
        enabled: Optional[bool]
        monthly_backups_to_keep: Optional[int]
        provisioning_state: Optional[str]
        volume_backups: Optional[list[VolumeBackups]]
        volumes_assigned: Optional[int]
        weekly_backups_to_keep: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                daily_backups_to_keep: Optional[int] = ..., 
                enabled: Optional[bool] = ..., 
                monthly_backups_to_keep: Optional[int] = ..., 
                weekly_backups_to_keep: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BackupProperties(_Model):
        backup_id: Optional[str]
        backup_policy_resource_id: Optional[str]
        backup_type: Optional[Union[str, BackupType]]
        completion_date: Optional[datetime]
        creation_date: Optional[datetime]
        failure_reason: Optional[str]
        is_large_volume: Optional[bool]
        label: Optional[str]
        provisioning_state: Optional[str]
        size: Optional[int]
        snapshot_creation_date: Optional[datetime]
        snapshot_name: Optional[str]
        use_existing_snapshot: Optional[bool]
        volume_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                label: Optional[str] = ..., 
                snapshot_name: Optional[str] = ..., 
                use_existing_snapshot: Optional[bool] = ..., 
                volume_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BackupRestoreFiles(_Model):
        destination_volume_id: str
        file_list: list[str]
        restore_file_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_volume_id: str, 
                file_list: list[str], 
                restore_file_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BackupStatus(_Model):
        error_message: Optional[str]
        healthy: Optional[bool]
        last_transfer_size: Optional[int]
        last_transfer_type: Optional[str]
        mirror_state: Optional[Union[str, MirrorState]]
        relationship_status: Optional[Union[str, VolumeBackupRelationshipStatus]]
        total_transfer_bytes: Optional[int]
        transfer_progress_bytes: Optional[int]
        unhealthy_reason: Optional[str]


    class azure.mgmt.netapp.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        SCHEDULED = "Scheduled"


    class azure.mgmt.netapp.models.BackupVault(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[BackupVaultProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[BackupVaultProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BackupVaultPatch(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BackupVaultProperties(_Model):
        provisioning_state: Optional[str]


    class azure.mgmt.netapp.models.BackupsMigrationRequest(_Model):
        backup_vault_id: str

        @overload
        def __init__(
                self, 
                *, 
                backup_vault_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BreakFileLocksRequest(_Model):
        client_ip: Optional[str]
        confirm_running_disruptive_operation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                client_ip: Optional[str] = ..., 
                confirm_running_disruptive_operation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BreakReplicationRequest(_Model):
        force_break_replication: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                force_break_replication: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Bucket(ProxyResource):
        id: str
        name: str
        properties: Optional[BucketProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BucketProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BucketCredentialsExpiry(_Model):
        key_pair_expiry_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                key_pair_expiry_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BucketGenerateCredentials(_Model):
        access_key: Optional[str]
        key_pair_expiry: Optional[datetime]
        secret_key: Optional[str]


    class azure.mgmt.netapp.models.BucketPatch(ProxyResource):
        id: str
        name: str
        properties: Optional[BucketPatchProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BucketPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.BucketPatchPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.netapp.models.BucketPatchProperties(_Model):
        akv_details: Optional[AzureKeyVaultDetails]
        file_system_user: Optional[FileSystemUser]
        permissions: Optional[Union[str, BucketPatchPermissions]]
        provisioning_state: Optional[Union[str, NetAppProvisioningState]]
        server: Optional[BucketServerPatchProperties]

        @overload
        def __init__(
                self, 
                *, 
                akv_details: Optional[AzureKeyVaultDetails] = ..., 
                file_system_user: Optional[FileSystemUser] = ..., 
                permissions: Optional[Union[str, BucketPatchPermissions]] = ..., 
                server: Optional[BucketServerPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BucketPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.netapp.models.BucketProperties(_Model):
        akv_details: Optional[AzureKeyVaultDetails]
        file_system_user: Optional[FileSystemUser]
        path: Optional[str]
        permissions: Optional[Union[str, BucketPermissions]]
        provisioning_state: Optional[Union[str, NetAppProvisioningState]]
        server: Optional[BucketServerProperties]
        status: Optional[Union[str, CredentialsStatus]]

        @overload
        def __init__(
                self, 
                *, 
                akv_details: Optional[AzureKeyVaultDetails] = ..., 
                file_system_user: Optional[FileSystemUser] = ..., 
                path: Optional[str] = ..., 
                permissions: Optional[Union[str, BucketPermissions]] = ..., 
                server: Optional[BucketServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BucketServerPatchProperties(_Model):
        certificate_object: Optional[str]
        fqdn: Optional[str]
        on_certificate_conflict_action: Optional[Union[str, OnCertificateConflictAction]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_object: Optional[str] = ..., 
                fqdn: Optional[str] = ..., 
                on_certificate_conflict_action: Optional[Union[str, OnCertificateConflictAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.BucketServerProperties(_Model):
        certificate_common_name: Optional[str]
        certificate_expiry_date: Optional[datetime]
        certificate_object: Optional[str]
        fqdn: Optional[str]
        ip_address: Optional[str]
        on_certificate_conflict_action: Optional[Union[str, OnCertificateConflictAction]]

        @overload
        def __init__(
                self, 
                *, 
                certificate_object: Optional[str] = ..., 
                fqdn: Optional[str] = ..., 
                on_certificate_conflict_action: Optional[Union[str, OnCertificateConflictAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Cache(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: CacheProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: CacheProperties, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CacheLifeCycleState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_PEERING_OFFER_SENT = "ClusterPeeringOfferSent"
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        VSERVER_PEERING_OFFER_SENT = "VserverPeeringOfferSent"


    class azure.mgmt.netapp.models.CacheMountTargetProperties(_Model):
        ip_address: Optional[str]
        mount_target_id: Optional[str]
        smb_server_fqdn: Optional[str]


    class azure.mgmt.netapp.models.CacheProperties(_Model):
        actual_throughput_mibps: Optional[float]
        cache_state: Optional[Union[str, CacheLifeCycleState]]
        cache_subnet_resource_id: str
        cifs_change_notifications: Optional[Union[str, CifsChangeNotifyState]]
        encryption: Optional[Union[str, EncryptionState]]
        encryption_key_source: Union[str, EncryptionKeySource]
        export_policy: Optional[CachePropertiesExportPolicy]
        file_path: str
        global_file_locking: Optional[Union[str, GlobalFileLockingState]]
        kerberos: Optional[Union[str, KerberosState]]
        key_vault_private_endpoint_resource_id: Optional[str]
        language: Optional[Union[str, VolumeLanguage]]
        ldap: Optional[Union[str, LdapState]]
        ldap_server_type: Optional[Union[str, LdapServerType]]
        maximum_number_of_files: Optional[int]
        mount_targets: Optional[list[CacheMountTargetProperties]]
        origin_cluster_information: OriginClusterInformation
        peering_subnet_resource_id: str
        protocol_types: Optional[list[Union[str, ProtocolTypes]]]
        provisioning_state: Optional[Union[str, CacheProvisioningState]]
        size: int
        smb_settings: Optional[SmbSettings]
        throughput_mibps: Optional[float]
        write_back: Optional[Union[str, EnableWriteBackState]]

        @overload
        def __init__(
                self, 
                *, 
                cache_subnet_resource_id: str, 
                cifs_change_notifications: Optional[Union[str, CifsChangeNotifyState]] = ..., 
                encryption_key_source: Union[str, EncryptionKeySource], 
                export_policy: Optional[CachePropertiesExportPolicy] = ..., 
                file_path: str, 
                global_file_locking: Optional[Union[str, GlobalFileLockingState]] = ..., 
                kerberos: Optional[Union[str, KerberosState]] = ..., 
                key_vault_private_endpoint_resource_id: Optional[str] = ..., 
                ldap: Optional[Union[str, LdapState]] = ..., 
                ldap_server_type: Optional[Union[str, LdapServerType]] = ..., 
                origin_cluster_information: OriginClusterInformation, 
                peering_subnet_resource_id: str, 
                protocol_types: Optional[list[Union[str, ProtocolTypes]]] = ..., 
                size: int, 
                smb_settings: Optional[SmbSettings] = ..., 
                throughput_mibps: Optional[float] = ..., 
                write_back: Optional[Union[str, EnableWriteBackState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CachePropertiesExportPolicy(_Model):
        rules: Optional[list[ExportPolicyRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[ExportPolicyRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CacheProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.netapp.models.CacheUpdate(_Model):
        properties: Optional[CacheUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CacheUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CacheUpdateProperties(_Model):
        cifs_change_notifications: Optional[Union[str, CifsChangeNotifyState]]
        export_policy: Optional[CachePropertiesExportPolicy]
        key_vault_private_endpoint_resource_id: Optional[str]
        protocol_types: Optional[list[Union[str, ProtocolTypes]]]
        size: Optional[int]
        smb_settings: Optional[SmbSettings]
        throughput_mibps: Optional[float]
        write_back: Optional[Union[str, EnableWriteBackState]]

        @overload
        def __init__(
                self, 
                *, 
                cifs_change_notifications: Optional[Union[str, CifsChangeNotifyState]] = ..., 
                export_policy: Optional[CachePropertiesExportPolicy] = ..., 
                key_vault_private_endpoint_resource_id: Optional[str] = ..., 
                protocol_types: Optional[list[Union[str, ProtocolTypes]]] = ..., 
                size: Optional[int] = ..., 
                smb_settings: Optional[SmbSettings] = ..., 
                throughput_mibps: Optional[float] = ..., 
                write_back: Optional[Union[str, EnableWriteBackState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CapacityPool(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: PoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: PoolProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.CapacityPoolPatch(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[PoolPatchProperties]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PoolPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.CertificateAkvDetails(_Model):
        certificate_key_vault_uri: Optional[str]
        certificate_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_key_vault_uri: Optional[str] = ..., 
                certificate_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ChangeKeyVault(_Model):
        key_name: str
        key_vault_private_endpoints: list[KeyVaultPrivateEndpoint]
        key_vault_resource_id: Optional[str]
        key_vault_uri: str

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_private_endpoints: list[KeyVaultPrivateEndpoint], 
                key_vault_resource_id: Optional[str] = ..., 
                key_vault_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CheckAvailabilityResponse(_Model):
        is_available: Optional[bool]
        message: Optional[str]
        reason: Optional[Union[str, InAvailabilityReasonType]]

        @overload
        def __init__(
                self, 
                *, 
                is_available: Optional[bool] = ..., 
                message: Optional[str] = ..., 
                reason: Optional[Union[str, InAvailabilityReasonType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CheckNameResourceTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS = "Microsoft.NetApp/netAppAccounts"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_BACKUP_VAULTS_BACKUPS = "Microsoft.NetApp/netAppAccounts/backupVaults/backups"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS = "Microsoft.NetApp/netAppAccounts/capacityPools"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES_BACKUPS = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes/backups"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES_SNAPSHOTS = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes/snapshots"


    class azure.mgmt.netapp.models.CheckQuotaNameResourceTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS = "Microsoft.NetApp/netAppAccounts"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_BACKUP_VAULTS_BACKUPS = "Microsoft.NetApp/netAppAccounts/backupVaults/backups"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS = "Microsoft.NetApp/netAppAccounts/capacityPools"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES_BACKUPS = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes/backups"
        MICROSOFT_NET_APP_NET_APP_ACCOUNTS_CAPACITY_POOLS_VOLUMES_SNAPSHOTS = "Microsoft.NetApp/netAppAccounts/capacityPools/volumes/snapshots"


    class azure.mgmt.netapp.models.ChownMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESTRICTED = "Restricted"
        UNRESTRICTED = "Unrestricted"


    class azure.mgmt.netapp.models.CifsChangeNotifyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.CifsUser(_Model):
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ClusterPeerCommandResponse(_Model):
        properties: Optional[ClusterPeerCommandResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterPeerCommandResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ClusterPeerCommandResponseProperties(_Model):
        cluster_peering_command: Optional[str]
        passphrase: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_peering_command: Optional[str] = ..., 
                passphrase: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CoolAccessRetrievalPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NEVER = "Never"
        ON_READ = "OnRead"


    class azure.mgmt.netapp.models.CoolAccessTieringPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        SNAPSHOT_ONLY = "SnapshotOnly"


    class azure.mgmt.netapp.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.netapp.models.CredentialsAkvDetails(_Model):
        credentials_key_vault_uri: Optional[str]
        secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credentials_key_vault_uri: Optional[str] = ..., 
                secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.CredentialsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREDENTIALS_EXPIRED = "CredentialsExpired"
        NO_CREDENTIALS_SET = "NoCredentialsSet"


    class azure.mgmt.netapp.models.DailySchedule(_Model):
        hour: Optional[int]
        minute: Optional[int]
        snapshots_to_keep: Optional[int]
        used_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                hour: Optional[int] = ..., 
                minute: Optional[int] = ..., 
                snapshots_to_keep: Optional[int] = ..., 
                used_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.DesiredRansomwareProtectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.DestinationReplication(_Model):
        region: Optional[str]
        replication_type: Optional[Union[str, ReplicationType]]
        resource_id: Optional[str]
        zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                region: Optional[str] = ..., 
                replication_type: Optional[Union[str, ReplicationType]] = ..., 
                resource_id: Optional[str] = ..., 
                zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Dimension(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.EnableSubvolumes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.EnableWriteBackState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.EncryptionIdentity(_Model):
        federated_client_id: Optional[str]
        principal_id: Optional[str]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                federated_client_id: Optional[str] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.EncryptionKeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"
        MICROSOFT_NET_APP = "Microsoft.NetApp"


    class azure.mgmt.netapp.models.EncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.EncryptionTransitionRequest(_Model):
        private_endpoint_id: str
        virtual_network_id: str

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint_id: str, 
                virtual_network_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.EncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOUBLE = "Double"
        SINGLE = "Single"


    class azure.mgmt.netapp.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DST = "dst"
        SRC = "src"


    class azure.mgmt.netapp.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.netapp.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.netapp.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Exclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        NONE = "None"


    class azure.mgmt.netapp.models.ExportPolicyRule(_Model):
        allowed_clients: Optional[str]
        chown_mode: Optional[Union[str, ChownMode]]
        cifs: Optional[bool]
        has_root_access: Optional[bool]
        kerberos5_i_read_only: Optional[bool]
        kerberos5_i_read_write: Optional[bool]
        kerberos5_p_read_only: Optional[bool]
        kerberos5_p_read_write: Optional[bool]
        kerberos5_read_only: Optional[bool]
        kerberos5_read_write: Optional[bool]
        nfsv3: Optional[bool]
        nfsv41: Optional[bool]
        rule_index: Optional[int]
        unix_read_only: Optional[bool]
        unix_read_write: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allowed_clients: Optional[str] = ..., 
                chown_mode: Optional[Union[str, ChownMode]] = ..., 
                cifs: Optional[bool] = ..., 
                has_root_access: Optional[bool] = ..., 
                kerberos5_i_read_only: Optional[bool] = ..., 
                kerberos5_i_read_write: Optional[bool] = ..., 
                kerberos5_p_read_only: Optional[bool] = ..., 
                kerberos5_p_read_write: Optional[bool] = ..., 
                kerberos5_read_only: Optional[bool] = ..., 
                kerberos5_read_write: Optional[bool] = ..., 
                nfsv3: Optional[bool] = ..., 
                nfsv41: Optional[bool] = ..., 
                rule_index: Optional[int] = ..., 
                unix_read_only: Optional[bool] = ..., 
                unix_read_write: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ExternalReplicationSetupStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_PEER_PENDING = "ClusterPeerPending"
        CLUSTER_PEER_REQUIRED = "ClusterPeerRequired"
        NO_ACTION_REQUIRED = "NoActionRequired"
        REPLICATION_CREATE_REQUIRED = "ReplicationCreateRequired"
        V_SERVER_PEER_REQUIRED = "VServerPeerRequired"


    class azure.mgmt.netapp.models.FileAccessLogs(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.FilePathAvailabilityRequest(_Model):
        availability_zone: Optional[str]
        name: str
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                name: str, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.FileSystemUser(_Model):
        cifs_user: Optional[CifsUser]
        nfs_user: Optional[NfsUser]

        @overload
        def __init__(
                self, 
                *, 
                cifs_user: Optional[CifsUser] = ..., 
                nfs_user: Optional[NfsUser] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.GetGroupIdListForLDAPUserRequest(_Model):
        username: str

        @overload
        def __init__(
                self, 
                *, 
                username: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.GetGroupIdListForLDAPUserResponse(_Model):
        group_ids_for_ldap_user: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids_for_ldap_user: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.GetKeyVaultStatusResponse(_Model):
        properties: Optional[GetKeyVaultStatusResponseProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GetKeyVaultStatusResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.GetKeyVaultStatusResponseProperties(_Model):
        key_name: Optional[str]
        key_vault_private_endpoints: Optional[list[KeyVaultPrivateEndpoint]]
        key_vault_resource_id: Optional[str]
        key_vault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_private_endpoints: Optional[list[KeyVaultPrivateEndpoint]] = ..., 
                key_vault_resource_id: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.GlobalFileLockingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.HourlySchedule(_Model):
        minute: Optional[int]
        snapshots_to_keep: Optional[int]
        used_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                minute: Optional[int] = ..., 
                snapshots_to_keep: Optional[int] = ..., 
                used_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.InAvailabilityReasonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.netapp.models.KerberosState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"
        MICROSOFT_NET_APP = "Microsoft.NetApp"


    class azure.mgmt.netapp.models.KeyVaultPrivateEndpoint(_Model):
        private_endpoint_id: Optional[str]
        virtual_network_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint_id: Optional[str] = ..., 
                virtual_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.KeyVaultProperties(_Model):
        key_name: str
        key_vault_id: Optional[str]
        key_vault_resource_id: Optional[str]
        key_vault_uri: str
        status: Optional[Union[str, KeyVaultStatus]]

        @overload
        def __init__(
                self, 
                *, 
                key_name: str, 
                key_vault_resource_id: Optional[str] = ..., 
                key_vault_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.KeyVaultStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED = "Created"
        DELETED = "Deleted"
        ERROR = "Error"
        IN_USE = "InUse"
        UPDATING = "Updating"


    class azure.mgmt.netapp.models.LdapSearchScopeOpt(_Model):
        group_dn: Optional[str]
        group_membership_filter: Optional[str]
        user_dn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_dn: Optional[str] = ..., 
                group_membership_filter: Optional[str] = ..., 
                user_dn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.LdapServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY = "ActiveDirectory"
        OPEN_LDAP = "OpenLDAP"


    class azure.mgmt.netapp.models.LdapState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.ListQuotaReportResponse(_Model):
        quota_report_records: Optional[list[QuotaReport]]

        @overload
        def __init__(
                self, 
                *, 
                quota_report_records: Optional[list[QuotaReport]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ListQuotaReportResult(_Model):
        properties: Optional[ListQuotaReportResponse]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ListQuotaReportResponse] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ListReplicationsRequest(_Model):
        exclude: Optional[Union[str, Exclude]]

        @overload
        def __init__(
                self, 
                *, 
                exclude: Optional[Union[str, Exclude]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.LogSpecification(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.netapp.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.netapp.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"


    class azure.mgmt.netapp.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        category: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        enable_regional_mdm_account: Optional[bool]
        fill_gap_with_zero: Optional[bool]
        internal_metric_name: Optional[str]
        is_internal: Optional[bool]
        name: Optional[str]
        resource_id_dimension_name_override: Optional[str]
        source_mdm_account: Optional[str]
        source_mdm_namespace: Optional[str]
        supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[bool] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                internal_metric_name: Optional[str] = ..., 
                is_internal: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                source_mdm_account: Optional[str] = ..., 
                source_mdm_namespace: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[Union[str, MetricAggregationType]]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.MirrorState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROKEN = "Broken"
        MIRRORED = "Mirrored"
        UNINITIALIZED = "Uninitialized"


    class azure.mgmt.netapp.models.MonthlySchedule(_Model):
        days_of_month: Optional[str]
        hour: Optional[int]
        minute: Optional[int]
        snapshots_to_keep: Optional[int]
        used_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                days_of_month: Optional[str] = ..., 
                hour: Optional[int] = ..., 
                minute: Optional[int] = ..., 
                snapshots_to_keep: Optional[int] = ..., 
                used_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.MountTargetProperties(_Model):
        file_system_id: str
        ip_address: Optional[str]
        mount_target_id: Optional[str]
        smb_server_fqdn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_system_id: str, 
                smb_server_fqdn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.MultiAdStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.NetAppAccount(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.NetAppAccountPatch(_Model):
        id: Optional[str]
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[AccountProperties]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.NetAppProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        PATCHING = "Patching"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.netapp.models.NetworkFeatures(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        BASIC_STANDARD = "Basic_Standard"
        STANDARD = "Standard"
        STANDARD_BASIC = "Standard_Basic"


    class azure.mgmt.netapp.models.NetworkSiblingSet(_Model):
        network_features: Optional[Union[str, NetworkFeatures]]
        network_sibling_set_id: Optional[str]
        network_sibling_set_state_id: Optional[str]
        nic_info_list: Optional[list[NicInfo]]
        provisioning_state: Optional[Union[str, NetworkSiblingSetProvisioningState]]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_features: Optional[Union[str, NetworkFeatures]] = ..., 
                network_sibling_set_id: Optional[str] = ..., 
                network_sibling_set_state_id: Optional[str] = ..., 
                nic_info_list: Optional[list[NicInfo]] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.NetworkSiblingSetProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.netapp.models.NfsUser(_Model):
        group_id: Optional[int]
        user_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[int] = ..., 
                user_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.NicInfo(_Model):
        ip_address: Optional[str]
        volume_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                volume_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.OnCertificateConflictAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAIL = "Fail"
        UPDATE = "Update"


    class azure.mgmt.netapp.models.Operation(_Model):
        display: Optional[OperationDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.OriginClusterInformation(_Model):
        peer_addresses: list[str]
        peer_cluster_name: str
        peer_volume_name: str
        peer_vserver_name: str

        @overload
        def __init__(
                self, 
                *, 
                peer_addresses: list[str], 
                peer_cluster_name: str, 
                peer_volume_name: str, 
                peer_vserver_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PeerClusterForVolumeMigrationRequest(_Model):
        peer_ip_addresses: list[str]

        @overload
        def __init__(
                self, 
                *, 
                peer_ip_addresses: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PeeringPassphrases(_Model):
        cluster_peering_command: str
        cluster_peering_passphrase: str
        critical_warning: Optional[str]
        vserver_peering_command: str

        @overload
        def __init__(
                self, 
                *, 
                cluster_peering_command: str, 
                cluster_peering_passphrase: str, 
                vserver_peering_command: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PlacementKeyValuePairs(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PoolChangeRequest(_Model):
        new_pool_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                new_pool_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PoolPatchProperties(_Model):
        cool_access: Optional[bool]
        custom_throughput_mibps: Optional[int]
        qos_type: Optional[Union[str, QosType]]
        size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cool_access: Optional[bool] = ..., 
                custom_throughput_mibps: Optional[int] = ..., 
                qos_type: Optional[Union[str, QosType]] = ..., 
                size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.PoolProperties(_Model):
        cool_access: Optional[bool]
        custom_throughput_mibps: Optional[int]
        encryption_type: Optional[Union[str, EncryptionType]]
        pool_id: Optional[str]
        provisioning_state: Optional[str]
        qos_type: Optional[Union[str, QosType]]
        service_level: Union[str, ServiceLevel]
        size: int
        total_throughput_mibps: Optional[float]
        utilized_throughput_mibps: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                cool_access: Optional[bool] = ..., 
                custom_throughput_mibps: Optional[int] = ..., 
                encryption_type: Optional[Union[str, EncryptionType]] = ..., 
                qos_type: Optional[Union[str, QosType]] = ..., 
                service_level: Union[str, ServiceLevel], 
                size: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ProtocolTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NF_SV3 = "NFSv3"
        NF_SV4 = "NFSv4"
        SMB = "SMB"


    class azure.mgmt.netapp.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.netapp.models.QosType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.netapp.models.QueryNetworkSiblingSetRequest(_Model):
        network_sibling_set_id: str
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                network_sibling_set_id: str, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.QuotaAvailabilityRequest(_Model):
        name: str
        resource_group: str
        type: Union[str, CheckQuotaNameResourceTypes]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_group: str, 
                type: Union[str, CheckQuotaNameResourceTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.QuotaItem(ProxyResource):
        id: str
        name: str
        properties: Optional[QuotaItemProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.QuotaItemProperties(_Model):
        current: Optional[int]
        default: Optional[int]
        usage: Optional[int]


    class azure.mgmt.netapp.models.QuotaReport(_Model):
        is_derived_quota: Optional[bool]
        percentage_used: Optional[float]
        quota_limit_total_in_ki_bs: Optional[int]
        quota_limit_used_in_ki_bs: Optional[int]
        quota_target: Optional[str]
        quota_type: Optional[Union[str, QuotaType]]

        @overload
        def __init__(
                self, 
                *, 
                is_derived_quota: Optional[bool] = ..., 
                percentage_used: Optional[float] = ..., 
                quota_limit_total_in_ki_bs: Optional[int] = ..., 
                quota_limit_used_in_ki_bs: Optional[int] = ..., 
                quota_target: Optional[str] = ..., 
                quota_type: Optional[Union[str, QuotaType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.QuotaReportFilterRequest(_Model):
        quota_target: Optional[str]
        quota_type: Optional[Union[str, QuotaType]]
        usage_threshold_percentage: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                quota_target: Optional[str] = ..., 
                quota_type: Optional[Union[str, QuotaType]] = ..., 
                usage_threshold_percentage: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.QuotaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT_GROUP_QUOTA = "DefaultGroupQuota"
        DEFAULT_USER_QUOTA = "DefaultUserQuota"
        INDIVIDUAL_GROUP_QUOTA = "IndividualGroupQuota"
        INDIVIDUAL_USER_QUOTA = "IndividualUserQuota"


    class azure.mgmt.netapp.models.RansomwareProtectionPatchSettings(_Model):
        desired_ransomware_protection_state: Optional[Union[str, DesiredRansomwareProtectionState]]

        @overload
        def __init__(
                self, 
                *, 
                desired_ransomware_protection_state: Optional[Union[str, DesiredRansomwareProtectionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RansomwareProtectionSettings(_Model):
        actual_ransomware_protection_state: Optional[Union[str, ActualRansomwareProtectionState]]
        desired_ransomware_protection_state: Optional[Union[str, DesiredRansomwareProtectionState]]

        @overload
        def __init__(
                self, 
                *, 
                desired_ransomware_protection_state: Optional[Union[str, DesiredRansomwareProtectionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RansomwareReport(ProxyResource):
        id: str
        name: str
        properties: Optional[RansomwareReportProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RansomwareReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RansomwareReportProperties(_Model):
        cleared_count: Optional[int]
        event_time: Optional[datetime]
        provisioning_state: Optional[str]
        reported_count: Optional[int]
        severity: Optional[Union[str, RansomwareReportSeverity]]
        state: Optional[Union[str, RansomwareReportState]]
        suspects: Optional[list[RansomwareSuspects]]


    class azure.mgmt.netapp.models.RansomwareReportSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MODERATE = "Moderate"
        NONE = "None"


    class azure.mgmt.netapp.models.RansomwareReportState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        RESOLVED = "Resolved"


    class azure.mgmt.netapp.models.RansomwareSuspectResolution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE_POSITIVE = "FalsePositive"
        POTENTIAL_THREAT = "PotentialThreat"


    class azure.mgmt.netapp.models.RansomwareSuspects(_Model):
        extension: Optional[str]
        file_count: Optional[int]
        resolution: Optional[Union[str, RansomwareSuspectResolution]]
        suspect_files: Optional[list[SuspectFile]]


    class azure.mgmt.netapp.models.RansomwareSuspectsClearRequest(_Model):
        extensions: list[str]
        resolution: Union[str, RansomwareSuspectResolution]

        @overload
        def __init__(
                self, 
                *, 
                extensions: list[str], 
                resolution: Union[str, RansomwareSuspectResolution]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ReestablishReplicationRequest(_Model):
        source_volume_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                source_volume_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RegionInfo(_Model):
        availability_zone_mappings: Optional[list[RegionInfoAvailabilityZoneMappingsItem]]
        storage_to_network_proximity: Optional[Union[str, RegionStorageToNetworkProximity]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone_mappings: Optional[list[RegionInfoAvailabilityZoneMappingsItem]] = ..., 
                storage_to_network_proximity: Optional[Union[str, RegionStorageToNetworkProximity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RegionInfoAvailabilityZoneMappingsItem(_Model):
        availability_zone: Optional[str]
        is_available: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone: Optional[str] = ..., 
                is_available: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RegionInfoResource(ProxyResource):
        id: str
        name: str
        properties: Optional[RegionInfo]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegionInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.RegionStorageToNetworkProximity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACROSS_T2 = "AcrossT2"
        DEFAULT = "Default"
        T1 = "T1"
        T1_AND_ACROSS_T2 = "T1AndAcrossT2"
        T1_AND_T2 = "T1AndT2"
        T1_AND_T2_AND_ACROSS_T2 = "T1AndT2AndAcrossT2"
        T2 = "T2"
        T2_AND_ACROSS_T2 = "T2AndAcrossT2"


    class azure.mgmt.netapp.models.RelocateVolumeRequest(_Model):
        creation_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RemotePath(_Model):
        external_host_name: str
        server_name: str
        volume_name: str

        @overload
        def __init__(
                self, 
                *, 
                external_host_name: str, 
                server_name: str, 
                volume_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Replication(_Model):
        endpoint_type: Optional[Union[str, EndpointType]]
        mirror_state: Optional[Union[str, ReplicationMirrorState]]
        remote_volume_region: Optional[str]
        remote_volume_resource_id: Optional[str]
        replication_creation_time: Optional[datetime]
        replication_deletion_time: Optional[datetime]
        replication_id: Optional[str]
        replication_schedule: Optional[Union[str, ReplicationSchedule]]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: Optional[Union[str, EndpointType]] = ..., 
                remote_volume_region: Optional[str] = ..., 
                remote_volume_resource_id: Optional[str] = ..., 
                replication_schedule: Optional[Union[str, ReplicationSchedule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ReplicationMirrorState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROKEN = "Broken"
        MIRRORED = "Mirrored"
        UNINITIALIZED = "Uninitialized"


    class azure.mgmt.netapp.models.ReplicationObject(_Model):
        destination_replications: Optional[list[DestinationReplication]]
        endpoint_type: Optional[Union[str, EndpointType]]
        external_replication_setup_info: Optional[str]
        external_replication_setup_status: Optional[Union[str, ExternalReplicationSetupStatus]]
        mirror_state: Optional[Union[str, MirrorState]]
        relationship_status: Optional[Union[str, VolumeReplicationRelationshipStatus]]
        remote_path: Optional[RemotePath]
        remote_volume_region: Optional[str]
        remote_volume_resource_id: Optional[str]
        replication_id: Optional[str]
        replication_schedule: Optional[Union[str, ReplicationSchedule]]

        @overload
        def __init__(
                self, 
                *, 
                remote_path: Optional[RemotePath] = ..., 
                remote_volume_region: Optional[str] = ..., 
                remote_volume_resource_id: Optional[str] = ..., 
                replication_schedule: Optional[Union[str, ReplicationSchedule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ReplicationSchedule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "daily"
        ENUM_10_MINUTELY = "_10minutely"
        HOURLY = "hourly"


    class azure.mgmt.netapp.models.ReplicationStatus(_Model):
        error_message: Optional[str]
        healthy: Optional[bool]
        mirror_state: Optional[Union[str, MirrorState]]
        relationship_status: Optional[Union[str, VolumeReplicationRelationshipStatus]]
        total_progress: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                healthy: Optional[bool] = ..., 
                mirror_state: Optional[Union[str, MirrorState]] = ..., 
                relationship_status: Optional[Union[str, VolumeReplicationRelationshipStatus]] = ..., 
                total_progress: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.ReplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CROSS_REGION_REPLICATION = "CrossRegionReplication"
        CROSS_ZONE_REPLICATION = "CrossZoneReplication"


    class azure.mgmt.netapp.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.netapp.models.ResourceNameAvailabilityRequest(_Model):
        name: str
        resource_group: str
        type: Union[str, CheckNameResourceTypes]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                resource_group: str, 
                type: Union[str, CheckNameResourceTypes]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.RestoreStatus(_Model):
        error_message: Optional[str]
        healthy: Optional[bool]
        mirror_state: Optional[Union[str, MirrorState]]
        relationship_status: Optional[Union[str, VolumeRestoreRelationshipStatus]]
        total_transfer_bytes: Optional[int]
        unhealthy_reason: Optional[str]


    class azure.mgmt.netapp.models.SecurityStyle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NTFS = "ntfs"
        UNIX = "unix"


    class azure.mgmt.netapp.models.ServiceLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLEXIBLE = "Flexible"
        PREMIUM = "Premium"
        STANDARD = "Standard"
        STANDARD_ZRS = "StandardZRS"
        ULTRA = "Ultra"


    class azure.mgmt.netapp.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SmbAccessBasedEnumeration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.SmbEncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.SmbNonBrowsable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.netapp.models.SmbSettings(_Model):
        smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]]
        smb_encryption: Optional[Union[str, SmbEncryptionState]]
        smb_non_browsable: Optional[Union[str, SmbNonBrowsable]]

        @overload
        def __init__(
                self, 
                *, 
                smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]] = ..., 
                smb_encryption: Optional[Union[str, SmbEncryptionState]] = ..., 
                smb_non_browsable: Optional[Union[str, SmbNonBrowsable]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.Snapshot(ProxyResource):
        id: str
        location: str
        name: str
        properties: Optional[SnapshotProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SnapshotProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SnapshotPatch(_Model):


    class azure.mgmt.netapp.models.SnapshotPolicy(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: SnapshotPolicyProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: SnapshotPolicyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SnapshotPolicyPatch(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[SnapshotPolicyProperties]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[SnapshotPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SnapshotPolicyProperties(_Model):
        daily_schedule: Optional[DailySchedule]
        enabled: Optional[bool]
        hourly_schedule: Optional[HourlySchedule]
        monthly_schedule: Optional[MonthlySchedule]
        provisioning_state: Optional[str]
        weekly_schedule: Optional[WeeklySchedule]

        @overload
        def __init__(
                self, 
                *, 
                daily_schedule: Optional[DailySchedule] = ..., 
                enabled: Optional[bool] = ..., 
                hourly_schedule: Optional[HourlySchedule] = ..., 
                monthly_schedule: Optional[MonthlySchedule] = ..., 
                weekly_schedule: Optional[WeeklySchedule] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SnapshotPolicyVolumeList(_Model):
        next_link: Optional[str]
        value: list[Volume]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Volume]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SnapshotProperties(_Model):
        created: Optional[datetime]
        provisioning_state: Optional[str]
        snapshot_id: Optional[str]


    class azure.mgmt.netapp.models.SnapshotRestoreFiles(_Model):
        destination_path: Optional[str]
        file_paths: list[str]

        @overload
        def __init__(
                self, 
                *, 
                destination_path: Optional[str] = ..., 
                file_paths: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SubvolumeInfo(ProxyResource):
        id: str
        name: str
        properties: Optional[SubvolumeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubvolumeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SubvolumeModel(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[SubvolumeModelProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubvolumeModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SubvolumeModelProperties(_Model):
        accessed_time_stamp: Optional[datetime]
        bytes_used: Optional[int]
        changed_time_stamp: Optional[datetime]
        creation_time_stamp: Optional[datetime]
        modified_time_stamp: Optional[datetime]
        parent_path: Optional[str]
        path: Optional[str]
        permissions: Optional[str]
        provisioning_state: Optional[str]
        size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                accessed_time_stamp: Optional[datetime] = ..., 
                bytes_used: Optional[int] = ..., 
                changed_time_stamp: Optional[datetime] = ..., 
                creation_time_stamp: Optional[datetime] = ..., 
                modified_time_stamp: Optional[datetime] = ..., 
                parent_path: Optional[str] = ..., 
                path: Optional[str] = ..., 
                permissions: Optional[str] = ..., 
                provisioning_state: Optional[str] = ..., 
                size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SubvolumePatchParams(_Model):
        path: Optional[str]
        size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                path: Optional[str] = ..., 
                size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SubvolumePatchRequest(_Model):
        properties: Optional[SubvolumePatchParams]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubvolumePatchParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.SubvolumeProperties(_Model):
        parent_path: Optional[str]
        path: Optional[str]
        provisioning_state: Optional[str]
        size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                parent_path: Optional[str] = ..., 
                path: Optional[str] = ..., 
                size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SuspectFile(_Model):
        file_timestamp: Optional[datetime]
        suspect_file_name: Optional[str]


    class azure.mgmt.netapp.models.SvmPeerCommandResponse(_Model):
        properties: Optional[SvmPeerCommandResponseProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SvmPeerCommandResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SvmPeerCommandResponseProperties(_Model):
        svm_peering_command: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                svm_peering_command: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.SystemData(_Model):
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


    class azure.mgmt.netapp.models.TrackedResource(Resource):
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


    class azure.mgmt.netapp.models.UpdateNetworkSiblingSetRequest(_Model):
        network_features: Union[str, NetworkFeatures]
        network_sibling_set_id: str
        network_sibling_set_state_id: str
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                network_features: Union[str, NetworkFeatures], 
                network_sibling_set_id: str, 
                network_sibling_set_state_id: str, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.UsageName(_Model):
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


    class azure.mgmt.netapp.models.UsageProperties(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        unit: Optional[str]


    class azure.mgmt.netapp.models.UsageResult(_Model):
        id: Optional[str]
        name: Optional[UsageName]
        properties: Optional[UsageProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UsageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.netapp.models.Volume(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: VolumeProperties
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
                properties: VolumeProperties, 
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


    class azure.mgmt.netapp.models.VolumeBackupProperties(_Model):
        backup_policy_id: Optional[str]
        backup_vault_id: Optional[str]
        policy_enforced: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                backup_policy_id: Optional[str] = ..., 
                backup_vault_id: Optional[str] = ..., 
                policy_enforced: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeBackupRelationshipStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IDLE = "Idle"
        TRANSFERRING = "Transferring"
        UNKNOWN = "Unknown"


    class azure.mgmt.netapp.models.VolumeBackups(_Model):
        backups_count: Optional[int]
        policy_enabled: Optional[bool]
        volume_name: Optional[str]
        volume_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backups_count: Optional[int] = ..., 
                policy_enabled: Optional[bool] = ..., 
                volume_name: Optional[str] = ..., 
                volume_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroup(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[VolumeGroupListProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VolumeGroupListProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroupDetails(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[VolumeGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VolumeGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroupListProperties(_Model):
        group_meta_data: Optional[VolumeGroupMetaData]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                group_meta_data: Optional[VolumeGroupMetaData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroupMetaData(_Model):
        application_identifier: Optional[str]
        application_type: Optional[Union[str, ApplicationType]]
        global_placement_rules: Optional[list[PlacementKeyValuePairs]]
        group_description: Optional[str]
        volumes_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                application_identifier: Optional[str] = ..., 
                application_type: Optional[Union[str, ApplicationType]] = ..., 
                global_placement_rules: Optional[list[PlacementKeyValuePairs]] = ..., 
                group_description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroupProperties(_Model):
        group_meta_data: Optional[VolumeGroupMetaData]
        provisioning_state: Optional[str]
        volumes: Optional[list[VolumeGroupVolumeProperties]]

        @overload
        def __init__(
                self, 
                *, 
                group_meta_data: Optional[VolumeGroupMetaData] = ..., 
                volumes: Optional[list[VolumeGroupVolumeProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeGroupVolumeProperties(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: VolumeProperties
        tags: Optional[dict[str, str]]
        type: Optional[str]
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: VolumeProperties, 
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


    class azure.mgmt.netapp.models.VolumeLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AR = "ar"
        AR_UTF8 = "ar.utf-8"
        C = "c"
        CS = "cs"
        CS_UTF8 = "cs.utf-8"
        C_UTF8 = "c.utf-8"
        DA = "da"
        DA_UTF8 = "da.utf-8"
        DE = "de"
        DE_UTF8 = "de.utf-8"
        EN = "en"
        EN_US = "en-us"
        EN_US_UTF8 = "en-us.utf-8"
        EN_UTF8 = "en.utf-8"
        ES = "es"
        ES_UTF8 = "es.utf-8"
        FI = "fi"
        FI_UTF8 = "fi.utf-8"
        FR = "fr"
        FR_UTF8 = "fr.utf-8"
        HE = "he"
        HE_UTF8 = "he.utf-8"
        HR = "hr"
        HR_UTF8 = "hr.utf-8"
        HU = "hu"
        HU_UTF8 = "hu.utf-8"
        IT = "it"
        IT_UTF8 = "it.utf-8"
        JA = "ja"
        JA_JP932 = "ja-jp.932"
        JA_JP932_UTF8 = "ja-jp.932.utf-8"
        JA_JP_PCK = "ja-jp.pck"
        JA_JP_PCK_UTF8 = "ja-jp.pck.utf-8"
        JA_JP_PCK_V2 = "ja-jp.pck-v2"
        JA_JP_PCK_V2_UTF8 = "ja-jp.pck-v2.utf-8"
        JA_UTF8 = "ja.utf-8"
        JA_V1 = "ja-v1"
        JA_V1_UTF8 = "ja-v1.utf-8"
        KO = "ko"
        KO_UTF8 = "ko.utf-8"
        NL = "nl"
        NL_UTF8 = "nl.utf-8"
        NO = "no"
        NO_UTF8 = "no.utf-8"
        PL = "pl"
        PL_UTF8 = "pl.utf-8"
        PT = "pt"
        PT_UTF8 = "pt.utf-8"
        RO = "ro"
        RO_UTF8 = "ro.utf-8"
        RU = "ru"
        RU_UTF8 = "ru.utf-8"
        SK = "sk"
        SK_UTF8 = "sk.utf-8"
        SL = "sl"
        SL_UTF8 = "sl.utf-8"
        SV = "sv"
        SV_UTF8 = "sv.utf-8"
        TR = "tr"
        TR_UTF8 = "tr.utf-8"
        UTF8_MB4 = "utf8mb4"
        ZH = "zh"
        ZH_GBK = "zh.gbk"
        ZH_GBK_UTF8 = "zh.gbk.utf-8"
        ZH_TW = "zh-tw"
        ZH_TW_BIG5 = "zh-tw.big5"
        ZH_TW_BIG5_UTF8 = "zh-tw.big5.utf-8"
        ZH_TW_UTF8 = "zh-tw.utf-8"
        ZH_UTF8 = "zh.utf-8"


    class azure.mgmt.netapp.models.VolumePatch(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[VolumePatchProperties]
        tags: Optional[dict[str, str]]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[VolumePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.VolumePatchProperties(_Model):
        cool_access: Optional[bool]
        cool_access_retrieval_policy: Optional[Union[str, CoolAccessRetrievalPolicy]]
        cool_access_tiering_policy: Optional[Union[str, CoolAccessTieringPolicy]]
        coolness_period: Optional[int]
        data_protection: Optional[VolumePatchPropertiesDataProtection]
        default_group_quota_in_ki_bs: Optional[int]
        default_user_quota_in_ki_bs: Optional[int]
        export_policy: Optional[VolumePatchPropertiesExportPolicy]
        is_default_quota_enabled: Optional[bool]
        protocol_types: Optional[list[str]]
        service_level: Optional[Union[str, ServiceLevel]]
        smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]]
        smb_non_browsable: Optional[Union[str, SmbNonBrowsable]]
        snapshot_directory_visible: Optional[bool]
        throughput_mibps: Optional[float]
        unix_permissions: Optional[str]
        usage_threshold: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cool_access: Optional[bool] = ..., 
                cool_access_retrieval_policy: Optional[Union[str, CoolAccessRetrievalPolicy]] = ..., 
                cool_access_tiering_policy: Optional[Union[str, CoolAccessTieringPolicy]] = ..., 
                coolness_period: Optional[int] = ..., 
                data_protection: Optional[VolumePatchPropertiesDataProtection] = ..., 
                default_group_quota_in_ki_bs: Optional[int] = ..., 
                default_user_quota_in_ki_bs: Optional[int] = ..., 
                export_policy: Optional[VolumePatchPropertiesExportPolicy] = ..., 
                is_default_quota_enabled: Optional[bool] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                service_level: Optional[Union[str, ServiceLevel]] = ..., 
                smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]] = ..., 
                smb_non_browsable: Optional[Union[str, SmbNonBrowsable]] = ..., 
                snapshot_directory_visible: Optional[bool] = ..., 
                throughput_mibps: Optional[float] = ..., 
                unix_permissions: Optional[str] = ..., 
                usage_threshold: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumePatchPropertiesDataProtection(_Model):
        backup: Optional[VolumeBackupProperties]
        ransomware_protection: Optional[RansomwareProtectionPatchSettings]
        snapshot: Optional[VolumeSnapshotProperties]

        @overload
        def __init__(
                self, 
                *, 
                backup: Optional[VolumeBackupProperties] = ..., 
                ransomware_protection: Optional[RansomwareProtectionPatchSettings] = ..., 
                snapshot: Optional[VolumeSnapshotProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumePatchPropertiesExportPolicy(_Model):
        rules: Optional[list[ExportPolicyRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[ExportPolicyRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeProperties(_Model):
        accept_grow_capacity_pool_for_short_term_clone_split: Optional[Union[str, AcceptGrowCapacityPoolForShortTermCloneSplit]]
        actual_throughput_mibps: Optional[float]
        avs_data_store: Optional[Union[str, AvsDataStore]]
        backup_id: Optional[str]
        baremetal_tenant_id: Optional[str]
        capacity_pool_resource_id: Optional[str]
        clone_progress: Optional[int]
        cool_access: Optional[bool]
        cool_access_retrieval_policy: Optional[Union[str, CoolAccessRetrievalPolicy]]
        cool_access_tiering_policy: Optional[Union[str, CoolAccessTieringPolicy]]
        coolness_period: Optional[int]
        creation_token: str
        data_protection: Optional[VolumePropertiesDataProtection]
        data_store_resource_id: Optional[list[str]]
        default_group_quota_in_ki_bs: Optional[int]
        default_user_quota_in_ki_bs: Optional[int]
        delete_base_snapshot: Optional[bool]
        effective_network_features: Optional[Union[str, NetworkFeatures]]
        enable_subvolumes: Optional[Union[str, EnableSubvolumes]]
        encrypted: Optional[bool]
        encryption_key_source: Optional[Union[str, EncryptionKeySource]]
        export_policy: Optional[VolumePropertiesExportPolicy]
        file_access_logs: Optional[Union[str, FileAccessLogs]]
        file_system_id: Optional[str]
        inherited_size_in_bytes: Optional[int]
        is_default_quota_enabled: Optional[bool]
        is_large_volume: Optional[bool]
        is_restoring: Optional[bool]
        kerberos_enabled: Optional[bool]
        key_vault_private_endpoint_resource_id: Optional[str]
        ldap_enabled: Optional[bool]
        maximum_number_of_files: Optional[int]
        mount_targets: Optional[list[MountTargetProperties]]
        network_features: Optional[Union[str, NetworkFeatures]]
        network_sibling_set_id: Optional[str]
        originating_resource_id: Optional[str]
        placement_rules: Optional[list[PlacementKeyValuePairs]]
        protocol_types: Optional[list[str]]
        provisioned_availability_zone: Optional[str]
        provisioning_state: Optional[str]
        proximity_placement_group: Optional[str]
        security_style: Optional[Union[str, SecurityStyle]]
        service_level: Optional[Union[str, ServiceLevel]]
        smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]]
        smb_continuously_available: Optional[bool]
        smb_encryption: Optional[bool]
        smb_non_browsable: Optional[Union[str, SmbNonBrowsable]]
        snapshot_directory_visible: Optional[bool]
        snapshot_id: Optional[str]
        storage_to_network_proximity: Optional[Union[str, VolumeStorageToNetworkProximity]]
        subnet_id: str
        t2_network: Optional[str]
        throughput_mibps: Optional[float]
        unix_permissions: Optional[str]
        usage_threshold: int
        volume_group_name: Optional[str]
        volume_spec_name: Optional[str]
        volume_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accept_grow_capacity_pool_for_short_term_clone_split: Optional[Union[str, AcceptGrowCapacityPoolForShortTermCloneSplit]] = ..., 
                avs_data_store: Optional[Union[str, AvsDataStore]] = ..., 
                backup_id: Optional[str] = ..., 
                capacity_pool_resource_id: Optional[str] = ..., 
                cool_access: Optional[bool] = ..., 
                cool_access_retrieval_policy: Optional[Union[str, CoolAccessRetrievalPolicy]] = ..., 
                cool_access_tiering_policy: Optional[Union[str, CoolAccessTieringPolicy]] = ..., 
                coolness_period: Optional[int] = ..., 
                creation_token: str, 
                data_protection: Optional[VolumePropertiesDataProtection] = ..., 
                default_group_quota_in_ki_bs: Optional[int] = ..., 
                default_user_quota_in_ki_bs: Optional[int] = ..., 
                delete_base_snapshot: Optional[bool] = ..., 
                enable_subvolumes: Optional[Union[str, EnableSubvolumes]] = ..., 
                encryption_key_source: Optional[Union[str, EncryptionKeySource]] = ..., 
                export_policy: Optional[VolumePropertiesExportPolicy] = ..., 
                is_default_quota_enabled: Optional[bool] = ..., 
                is_large_volume: Optional[bool] = ..., 
                kerberos_enabled: Optional[bool] = ..., 
                key_vault_private_endpoint_resource_id: Optional[str] = ..., 
                ldap_enabled: Optional[bool] = ..., 
                network_features: Optional[Union[str, NetworkFeatures]] = ..., 
                placement_rules: Optional[list[PlacementKeyValuePairs]] = ..., 
                protocol_types: Optional[list[str]] = ..., 
                proximity_placement_group: Optional[str] = ..., 
                security_style: Optional[Union[str, SecurityStyle]] = ..., 
                service_level: Optional[Union[str, ServiceLevel]] = ..., 
                smb_access_based_enumeration: Optional[Union[str, SmbAccessBasedEnumeration]] = ..., 
                smb_continuously_available: Optional[bool] = ..., 
                smb_encryption: Optional[bool] = ..., 
                smb_non_browsable: Optional[Union[str, SmbNonBrowsable]] = ..., 
                snapshot_directory_visible: Optional[bool] = ..., 
                snapshot_id: Optional[str] = ..., 
                subnet_id: str, 
                throughput_mibps: Optional[float] = ..., 
                unix_permissions: Optional[str] = ..., 
                usage_threshold: int, 
                volume_spec_name: Optional[str] = ..., 
                volume_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumePropertiesDataProtection(_Model):
        backup: Optional[VolumeBackupProperties]
        ransomware_protection: Optional[RansomwareProtectionSettings]
        replication: Optional[ReplicationObject]
        snapshot: Optional[VolumeSnapshotProperties]
        volume_relocation: Optional[VolumeRelocationProperties]

        @overload
        def __init__(
                self, 
                *, 
                backup: Optional[VolumeBackupProperties] = ..., 
                ransomware_protection: Optional[RansomwareProtectionSettings] = ..., 
                replication: Optional[ReplicationObject] = ..., 
                snapshot: Optional[VolumeSnapshotProperties] = ..., 
                volume_relocation: Optional[VolumeRelocationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumePropertiesExportPolicy(_Model):
        rules: Optional[list[ExportPolicyRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[ExportPolicyRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeQuotaRule(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[VolumeQuotaRulesProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[VolumeQuotaRulesProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.VolumeQuotaRulePatch(_Model):
        properties: Optional[VolumeQuotaRulesProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeQuotaRulesProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.netapp.models.VolumeQuotaRulesProperties(_Model):
        provisioning_state: Optional[Union[str, NetAppProvisioningState]]
        quota_size_in_ki_bs: Optional[int]
        quota_target: Optional[str]
        quota_type: Optional[Union[str, QuotaType]]

        @overload
        def __init__(
                self, 
                *, 
                quota_size_in_ki_bs: Optional[int] = ..., 
                quota_target: Optional[str] = ..., 
                quota_type: Optional[Union[str, QuotaType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeRelocationProperties(_Model):
        ready_to_be_finalized: Optional[bool]
        relocation_requested: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                relocation_requested: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeReplicationRelationshipStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IDLE = "Idle"
        TRANSFERRING = "Transferring"


    class azure.mgmt.netapp.models.VolumeRestoreRelationshipStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IDLE = "Idle"
        TRANSFERRING = "Transferring"
        UNKNOWN = "Unknown"


    class azure.mgmt.netapp.models.VolumeRevert(_Model):
        snapshot_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                snapshot_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeSnapshotProperties(_Model):
        snapshot_policy_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                snapshot_policy_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.netapp.models.VolumeStorageToNetworkProximity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACROSS_T2 = "AcrossT2"
        DEFAULT = "Default"
        T1 = "T1"
        T2 = "T2"


    class azure.mgmt.netapp.models.WeeklySchedule(_Model):
        day: Optional[str]
        hour: Optional[int]
        minute: Optional[int]
        snapshots_to_keep: Optional[int]
        used_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                day: Optional[str] = ..., 
                hour: Optional[int] = ..., 
                minute: Optional[int] = ..., 
                snapshots_to_keep: Optional[int] = ..., 
                used_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.netapp.operations

    class azure.mgmt.netapp.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[ChangeKeyVault] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_change_key_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: NetAppAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_get_change_key_vault_information(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[GetKeyVaultStatusResponse]: ...

        @distributed_trace
        def begin_renew_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[EncryptionTransitionRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_transition_to_cmk(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: NetAppAccountPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetAppAccount]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> NetAppAccount: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetAppAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[NetAppAccount]: ...


    class azure.mgmt.netapp.operations.BackupPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: BackupPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: BackupPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_policy_name: str, 
                **kwargs: Any
            ) -> BackupPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupPolicy]: ...


    class azure.mgmt.netapp.operations.BackupVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: BackupVault, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: BackupVaultPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[BackupVault]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                **kwargs: Any
            ) -> BackupVault: ...

        @distributed_trace
        def list_by_net_app_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[BackupVault]: ...


    class azure.mgmt.netapp.operations.BackupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Backup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[BackupPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Backup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                **kwargs: Any
            ) -> Backup: ...

        @distributed_trace
        def get_latest_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> BackupStatus: ...

        @distributed_trace
        def get_volume_latest_restore_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> RestoreStatus: ...

        @distributed_trace
        def list_by_vault(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Backup]: ...


    class azure.mgmt.netapp.operations.BackupsUnderAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: BackupsMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.netapp.operations.BackupsUnderBackupVaultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: BackupRestoreFiles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                backup_vault_name: str, 
                backup_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.netapp.operations.BackupsUnderVolumeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: BackupsMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate_backups(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.netapp.operations.BucketsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: Bucket, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketCredentialsExpiry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_generate_akv_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def begin_refresh_certificate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Bucket]: ...

        @overload
        def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: BucketCredentialsExpiry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @overload
        def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @overload
        def generate_credentials(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BucketGenerateCredentials: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'bucket_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                bucket_name: str, 
                **kwargs: Any
            ) -> Bucket: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Bucket]: ...


    class azure.mgmt.netapp.operations.CachesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: Cache, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: PoolChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def begin_reset_smb_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: CacheUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cache]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> Cache: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01', params_added_on={'2026-01-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'accept']}, api_versions_list=['2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cache]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-15-preview', params_added_on={'2025-12-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'cache_name', 'accept']}, api_versions_list=['2025-12-15-preview', '2026-01-01'])
        def list_peering_passphrases(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                cache_name: str, 
                **kwargs: Any
            ) -> PeeringPassphrases: ...


    class azure.mgmt.netapp.operations.NetAppResourceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: UpdateNetworkSiblingSetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSiblingSet]: ...

        @overload
        def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSiblingSet]: ...

        @overload
        def begin_update_network_sibling_set(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkSiblingSet]: ...

        @overload
        def check_file_path_availability(
                self, 
                location: str, 
                body: FilePathAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_file_path_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_file_path_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: ResourceNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_quota_availability(
                self, 
                location: str, 
                body: QuotaAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_quota_availability(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def check_quota_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckAvailabilityResponse: ...

        @overload
        def query_network_sibling_set(
                self, 
                location: str, 
                body: QueryNetworkSiblingSetRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @overload
        def query_network_sibling_set(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @overload
        def query_network_sibling_set(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkSiblingSet: ...

        @distributed_trace
        def query_region_info(
                self, 
                location: str, 
                **kwargs: Any
            ) -> RegionInfo: ...


    class azure.mgmt.netapp.operations.NetAppResourceQuotaLimitsAccountOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'quota_limit_name', 'accept']}, api_versions_list=['2025-08-01', '2025-09-01', '2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                quota_limit_name: str, 
                **kwargs: Any
            ) -> QuotaItem: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2025-08-01', '2025-09-01', '2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[QuotaItem]: ...


    class azure.mgmt.netapp.operations.NetAppResourceQuotaLimitsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                quota_limit_name: str, 
                **kwargs: Any
            ) -> QuotaItem: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[QuotaItem]: ...


    class azure.mgmt.netapp.operations.NetAppResourceRegionInfosOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> RegionInfoResource: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[RegionInfoResource]: ...


    class azure.mgmt.netapp.operations.NetAppResourceUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                usage_type: str, 
                **kwargs: Any
            ) -> UsageResult: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[UsageResult]: ...


    class azure.mgmt.netapp.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.netapp.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: CapacityPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: CapacityPoolPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapacityPool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> CapacityPool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CapacityPool]: ...


    class azure.mgmt.netapp.operations.RansomwareReportsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: RansomwareSuspectsClearRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_clear_suspects(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01', params_added_on={'2025-12-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'ransomware_report_name', 'accept']}, api_versions_list=['2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                ransomware_report_name: str, 
                **kwargs: Any
            ) -> RansomwareReport: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-12-01', params_added_on={'2025-12-01': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'pool_name', 'volume_name', 'accept']}, api_versions_list=['2025-12-01', '2025-12-15-preview', '2026-01-01'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RansomwareReport]: ...


    class azure.mgmt.netapp.operations.SnapshotPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: SnapshotPolicyPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SnapshotPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SnapshotPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SnapshotPolicy]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: SnapshotPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> SnapshotPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SnapshotPolicy]: ...

        @distributed_trace
        def list_volumes(
                self, 
                resource_group_name: str, 
                account_name: str, 
                snapshot_policy_name: str, 
                **kwargs: Any
            ) -> SnapshotPolicyVolumeList: ...


    class azure.mgmt.netapp.operations.SnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: SnapshotRestoreFiles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restore_files(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: SnapshotPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Snapshot]: ...


    class azure.mgmt.netapp.operations.SubvolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: SubvolumeInfo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_get_metadata(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> LROPoller[SubvolumeModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: SubvolumePatchRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SubvolumeInfo]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                subvolume_name: str, 
                **kwargs: Any
            ) -> SubvolumeInfo: ...

        @distributed_trace
        def list_by_volume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SubvolumeInfo]: ...


    class azure.mgmt.netapp.operations.VolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: VolumeGroupDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupDetails]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupDetails]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroupDetails]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroupDetails: ...

        @distributed_trace
        def list_by_net_app_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VolumeGroup]: ...


    class azure.mgmt.netapp.operations.VolumeQuotaRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: VolumeQuotaRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: VolumeQuotaRulePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeQuotaRule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                volume_quota_rule_name: str, 
                **kwargs: Any
            ) -> VolumeQuotaRule: ...

        @distributed_trace
        def list_by_volume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VolumeQuotaRule]: ...


    class azure.mgmt.netapp.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_authorize_external_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[SvmPeerCommandResponse]: ...

        @overload
        def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: AuthorizeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_authorize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[BreakFileLocksRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_file_locks(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[BreakReplicationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_break_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_finalize_external_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_finalize_relocation(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: GetGroupIdListForLDAPUserRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        def begin_list_get_group_id_list_for_ldap_user(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GetGroupIdListForLDAPUserResponse]: ...

        @overload
        def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[QuotaReportFilterRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ListQuotaReportResult]: ...

        @overload
        def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ListQuotaReportResult]: ...

        @overload
        def begin_list_quota_report(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ListQuotaReportResult]: ...

        @overload
        def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: PeerClusterForVolumeMigrationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPeerCommandResponse]: ...

        @overload
        def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPeerCommandResponse]: ...

        @overload
        def begin_peer_external_cluster(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ClusterPeerCommandResponse]: ...

        @distributed_trace
        def begin_perform_replication_transfer(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: PoolChangeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pool_change(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_populate_availability_zone(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def begin_re_initialize_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: ReestablishReplicationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_reestablish_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[RelocateVolumeRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_relocate(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_reset_cifs_password(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_resync_replication(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: VolumeRevert, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revert(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_revert_relocation(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_split_clone_from_parent(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: VolumePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Volume]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[ListReplicationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Replication]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Replication]: ...

        @overload
        def list_replications(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[Replication]: ...

        @distributed_trace
        def replication_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                pool_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> ReplicationStatus: ...


```