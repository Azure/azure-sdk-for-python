```py
namespace azure.mgmt.commvaultcontentstore

    class azure.mgmt.commvaultcontentstore.CommvaultContentStoreMgmtClient: implements ContextManager 
        cloud_accounts: CloudAccountsOperations
        operations: Operations
        plans: PlansOperations
        protected_items: ProtectedItemsOperations
        protected_items_operation_group: ProtectedItemsOperationGroupOperations
        protection_groups: ProtectionGroupsOperations
        role_mappings: RoleMappingsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        storages: StoragesOperations

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


namespace azure.mgmt.commvaultcontentstore.aio

    class azure.mgmt.commvaultcontentstore.aio.CommvaultContentStoreMgmtClient: implements AsyncContextManager 
        cloud_accounts: CloudAccountsOperations
        operations: Operations
        plans: PlansOperations
        protected_items: ProtectedItemsOperations
        protected_items_operation_group: ProtectedItemsOperationGroupOperations
        protection_groups: ProtectionGroupsOperations
        role_mappings: RoleMappingsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        storages: StoragesOperations

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


namespace azure.mgmt.commvaultcontentstore.aio.operations

    class azure.mgmt.commvaultcontentstore.aio.operations.CloudAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: CloudAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: CloudAccountUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudAccount]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> CloudAccount: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-06-02-preview', params_added_on={'2026-06-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-06-02-preview', '2026-07-01-preview', '2026-07-03-preview'])
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CloudAccount]: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.PlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: CommvaultPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommvaultPlan]: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommvaultPlan]: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommvaultPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                **kwargs: Any
            ) -> CommvaultPlan: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommvaultPlan]: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.ProtectedItemsOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def count_by_protection_groups(
                self, 
                body: CountProtectedItemsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...

        @overload
        async def count_by_protection_groups(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...

        @overload
        async def count_by_protection_groups(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.ProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> ProtectedItem: ...

        @distributed_trace_async
        async def get_restore_points(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> RestorePoints: ...

        @distributed_trace
        def list_by_protection_group(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectedItem]: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: RestoreProtectionItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.ProtectionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: BackupProtectionGroupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        async def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        async def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: ProtectionGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionGroup]: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionGroup]: ...

        @overload
        async def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProtectionGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: StopBackupProtectionGroupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> ProtectionGroup: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProtectionGroup]: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: RestoreProtectionItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        async def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'protection_group_name']}, api_versions_list=['2026-03-01-preview', '2026-05-01-preview', '2026-06-01-preview', '2026-06-02-preview', '2026-07-01-preview', '2026-07-03-preview'])
        async def resume_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.RoleMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: RoleMapping, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name']}, api_versions_list=['2026-07-03-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-07-03-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> RoleMapping: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-07-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RoleMapping]: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        async def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SaaSResourceDetailsResponse]: ...


    class azure.mgmt.commvaultcontentstore.aio.operations.StoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: Storage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Storage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Storage]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Storage]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> Storage: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Storage]: ...


namespace azure.mgmt.commvaultcontentstore.models

    class azure.mgmt.commvaultcontentstore.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.commvaultcontentstore.models.ActivateSaaSParameterRequest(_Model):
        saa_s_guid: str

        @overload
        def __init__(
                self, 
                *, 
                saa_s_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.BackUpType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTH = "BOTH"
        FULL = "FULL"
        INCREMENTAL = "INCREMENTAL"


    class azure.mgmt.commvaultcontentstore.models.BackupLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIFFERENTIAL = "DIFFERENTIAL"
        FULL = "FULL"
        INCREMENTAL = "INCREMENTAL"
        SYNTHETIC_FULL = "SYNTHETIC_FULL"


    class azure.mgmt.commvaultcontentstore.models.BackupOptions(_Model):
        backup_copy_immediately: bool
        backup_level: Optional[Union[str, BackupLevel]]
        job_description: str
        notify_user_on_job_completion: bool
        run_snap_shot_backup: bool

        @overload
        def __init__(
                self, 
                *, 
                backup_copy_immediately: bool, 
                backup_level: Optional[Union[str, BackupLevel]] = ..., 
                job_description: str, 
                notify_user_on_job_completion: bool, 
                run_snap_shot_backup: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.BackupProtectionGroupRequest(_Model):
        backup_options: BackupOptions
        vm_list: list[VmListItem]

        @overload
        def __init__(
                self, 
                *, 
                backup_options: BackupOptions, 
                vm_list: list[VmListItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.BackupProtectionGroupResponse(_Model):
        job_ids: list[str]
        task_id: int


    class azure.mgmt.commvaultcontentstore.models.BackupRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_FULLS = "ALL_FULLS"
        ALL_JOBS = "ALL_JOBS"
        DAILY_FULLS = "DAILY_FULLS"
        HALF_YEARLY_FULLS = "HALF_YEARLY_FULLS"
        HOURLY_FULLS = "HOURLY_FULLS"
        MONTHLY_FULLS = "MONTHLY_FULLS"
        QUARTERLY_FULLS = "QUARTERLY_FULLS"
        WEEKLY_FULLS = "WEEKLY_FULLS"
        YEARLY_FULLS = "YEARLY_FULLS"


    class azure.mgmt.commvaultcontentstore.models.CloudAccount(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[CloudAccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[CloudAccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CloudAccountProperties(_Model):
        backup_admin_on_cca_create: Optional[EntityInfo]
        marketplace: MarketplaceDetails
        multi_person_authorization_on_cca_create: Optional[EntityInfo]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        sso_url: Optional[str]
        user: UserDetails

        @overload
        def __init__(
                self, 
                *, 
                backup_admin_on_cca_create: Optional[EntityInfo] = ..., 
                marketplace: MarketplaceDetails, 
                multi_person_authorization_on_cca_create: Optional[EntityInfo] = ..., 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CloudAccountUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[CloudAccountUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[CloudAccountUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CloudAccountUpdateProperties(_Model):
        marketplace: Optional[MarketplaceDetails]
        user: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                marketplace: Optional[MarketplaceDetails] = ..., 
                user: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CommvaultPlan(ProxyResource):
        id: str
        name: str
        properties: Optional[PlanProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlanProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CountProtectedItemsRequest(_Model):
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CountProtectedItemsResponse(_Model):
        count: str

        @overload
        def __init__(
                self, 
                *, 
                count: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.commvaultcontentstore.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "DAY"
        FRIDAY = "FRIDAY"
        MONDAY = "MONDAY"
        SATURDAY = "SATURDAY"
        SUNDAY = "SUNDAY"
        THURSDAY = "THURSDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"
        WEEKDAY = "WEEKDAY"
        WEEKEND_DAYS = "WEEKEND_DAYS"


    class azure.mgmt.commvaultcontentstore.models.EntityInfo(_Model):
        display_name: Optional[str]
        entity_type: Optional[Union[str, EntityType]]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                entity_type: Optional[Union[str, EntityType]] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.EntityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        USER = "User"


    class azure.mgmt.commvaultcontentstore.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.commvaultcontentstore.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.commvaultcontentstore.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ExtendedRetentionTime(_Model):
        backup_rule_type: Optional[Union[str, BackupRuleType]]
        retention_period: Optional[int]
        retention_time: Optional[Union[str, RetentionTime]]

        @overload
        def __init__(
                self, 
                *, 
                backup_rule_type: Optional[Union[str, BackupRuleType]] = ..., 
                retention_period: Optional[int] = ..., 
                retention_time: Optional[Union[str, RetentionTime]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.Frequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "daily"
        MINUTES = "minutes"
        MONTHLY = "monthly"
        WEEKLY = "weekly"
        YEARLY = "yearly"


    class azure.mgmt.commvaultcontentstore.models.LatestLinkedSaaSResponse(_Model):
        is_hidden_saa_s: Optional[bool]
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_hidden_saa_s: Optional[bool] = ..., 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.commvaultcontentstore.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.commvaultcontentstore.models.MarketplaceDetails(_Model):
        offer_details: OfferDetails
        saas_resource_id: Optional[str]
        subscription_id: Optional[str]
        subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                offer_details: OfferDetails, 
                saas_resource_id: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.commvaultcontentstore.models.MatchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        ANY = "any"


    class azure.mgmt.commvaultcontentstore.models.MonthOfYear(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APRIL = "APRIL"
        AUGUST = "AUGUST"
        DECEMBER = "DECEMBER"
        FEBRUARY = "FEBRUARY"
        JANUARY = "JANUARY"
        JULY = "JULY"
        JUNE = "JUNE"
        MARCH = "MARCH"
        MAY = "MAY"
        NOVEMBER = "NOVEMBER"
        OCTOBER = "OCTOBER"
        SEPTEMBER = "SEPTEMBER"


    class azure.mgmt.commvaultcontentstore.models.OfferDetails(_Model):
        offer_id: str
        plan_id: Optional[str]
        plan_name: Optional[str]
        publisher_id: str
        term_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: str, 
                plan_id: Optional[str] = ..., 
                plan_name: Optional[str] = ..., 
                publisher_id: str, 
                term_id: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.Operation(_Model):
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


    class azure.mgmt.commvaultcontentstore.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.commvaultcontentstore.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "contains"
        DOES_NOT_CONTAINS = "doesNotContains"
        DOES_NOT_EQUAL = "doesNotEqual"
        ENDS_WITH = "endsWith"
        EQUALS = "equals"
        STARTS_WITH = "startsWith"


    class azure.mgmt.commvaultcontentstore.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.commvaultcontentstore.models.PlanProperties(_Model):
        location: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        retention: Optional[Retention]
        schedules: Optional[list[Schedule]]
        storage_plans: list[StoragePlan]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                retention: Optional[Retention] = ..., 
                schedules: Optional[list[Schedule]] = ..., 
                storage_plans: list[StoragePlan]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectedItem(ProxyResource):
        id: str
        name: str
        properties: Optional[ProtectedItemProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProtectedItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectedItemProperties(_Model):
        last_back_up_time: int
        location: str
        resource_group: str
        resource_name: str
        vm_guid: str


    class azure.mgmt.commvaultcontentstore.models.ProtectionGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[ProtectionGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProtectionGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectionGroupProperties(_Model):
        backup_activity_status: Optional[str]
        data_source_type: Literal["AzureVM"]
        last_back_up_time: Optional[int]
        number_of_protected_items: Optional[int]
        plan: str
        protection_status: Optional[Union[str, ProtectionStatus]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        resources: ProtectionGroupResources

        @overload
        def __init__(
                self, 
                *, 
                plan: str, 
                resources: ProtectionGroupResources
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectionGroupResources(_Model):
        manual: Optional[list[str]]
        match_rules: Optional[ProtectionGroupResourcesMatchRules]

        @overload
        def __init__(
                self, 
                *, 
                manual: Optional[list[str]] = ..., 
                match_rules: Optional[ProtectionGroupResourcesMatchRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectionGroupResourcesMatchRules(_Model):
        match_type: Union[str, MatchType]
        rules: list[Rule]

        @overload
        def __init__(
                self, 
                *, 
                match_type: Union[str, MatchType], 
                rules: list[Rule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.ProtectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        BACKED_UP_WITH_ERROR = "backed_up_with_error"
        DISCOVERED = "discovered"
        NOT_PROTECTED = "not_protected"
        PENDING = "pending"
        PROTECTED = "protected"


    class azure.mgmt.commvaultcontentstore.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.commvaultcontentstore.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.commvaultcontentstore.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.commvaultcontentstore.models.RestorePoints(_Model):
        restore_times: list[int]


    class azure.mgmt.commvaultcontentstore.models.RestoreProtectionItemRequest(_Model):
        in_place_restore: bool
        restore_type: Optional[Union[str, RestoreType]]
        to_time: Optional[str]
        vm_destination_info: VmDestinationInfo

        @overload
        def __init__(
                self, 
                *, 
                in_place_restore: bool, 
                restore_type: Optional[Union[str, RestoreType]] = ..., 
                to_time: Optional[str] = ..., 
                vm_destination_info: VmDestinationInfo
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RestoreProtectionItemResponse(_Model):
        job_ids: list[str]
        task_id: int


    class azure.mgmt.commvaultcontentstore.models.RestoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK_ATTACH = "DISK_ATTACH"
        NONE = "NONE"
        VIRTUAL_MACHINE = "VIRTUAL_MACHINE"


    class azure.mgmt.commvaultcontentstore.models.Retention(_Model):
        number_of_snapshots: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                number_of_snapshots: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RetentionTime(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "monthly"
        YEARLY = "yearly"


    class azure.mgmt.commvaultcontentstore.models.RoleAssignment(_Model):
        entities: Optional[list[EntityInfo]]
        role_name: Optional[Union[str, RoleName]]

        @overload
        def __init__(
                self, 
                *, 
                entities: Optional[list[EntityInfo]] = ..., 
                role_name: Optional[Union[str, RoleName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RoleMapping(ProxyResource):
        id: str
        name: str
        properties: Optional[RoleMappingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RoleMappingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RoleMappingProperties(_Model):
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        roles: Optional[list[RoleAssignment]]

        @overload
        def __init__(
                self, 
                *, 
                roles: Optional[list[RoleAssignment]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RoleName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_ADMIN = "BackupAdmin"
        BACKUP_OPERATOR = "BackupOperator"
        BACKUP_USER = "BackupUser"
        MULTI_PERSON_AUTHORIZATION = "MultiPersonAuthorization"
        SECURITY_ADMIN = "SecurityAdmin"


    class azure.mgmt.commvaultcontentstore.models.Rule(_Model):
        operator: Union[str, Operator]
        property: Union[str, RuleProperty]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                operator: Union[str, Operator], 
                property: Union[str, RuleProperty], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.RuleProperty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NAME = "name"
        REGION = "region"
        RESOURCE_GROUP = "resourceGroup"
        STATUS = "status"
        TAG_NAME = "tagName"
        TAG_VALUE = "tagValue"


    class azure.mgmt.commvaultcontentstore.models.SaaSData(_Model):
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.SaaSResourceDetailsResponse(ProxyResource):
        id: str
        name: str
        saa_s_resource_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.Schedule(_Model):
        backup_type: Union[str, BackUpType]
        day_of_month: Optional[int]
        day_of_week: Optional[Union[str, DayOfWeek]]
        frequency: Optional[Union[str, Frequency]]
        month_of_year: Optional[Union[str, MonthOfYear]]
        runs_every: Optional[int]
        time: Optional[str]
        time_zone: Optional[str]
        week_of_month: Optional[Union[str, WeekOfMonth]]
        weekly_days: Optional[list[Union[str, WeeklyDays]]]

        @overload
        def __init__(
                self, 
                *, 
                backup_type: Union[str, BackUpType], 
                day_of_month: Optional[int] = ..., 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                frequency: Optional[Union[str, Frequency]] = ..., 
                month_of_year: Optional[Union[str, MonthOfYear]] = ..., 
                runs_every: Optional[int] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                week_of_month: Optional[Union[str, WeekOfMonth]] = ..., 
                weekly_days: Optional[list[Union[str, WeeklyDays]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.StopBackupProtectionGroupRequest(_Model):
        comment: Optional[str]
        reason: str

        @overload
        def __init__(
                self, 
                *, 
                comment: Optional[str] = ..., 
                reason: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.Storage(ProxyResource):
        id: str
        name: str
        properties: Optional[StorageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.StorageClassType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOL = "COLD"
        HOT = "HOT"


    class azure.mgmt.commvaultcontentstore.models.StoragePlan(_Model):
        backup_rule_type: Optional[Union[str, BackupRuleType]]
        copy_name: Optional[str]
        copy_precedence: Optional[int]
        extended_retention: Optional[list[ExtendedRetentionTime]]
        name: str
        retention_period: Optional[int]
        retention_time: Optional[Union[str, RetentionTime]]
        storage_pool_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backup_rule_type: Optional[Union[str, BackupRuleType]] = ..., 
                copy_name: Optional[str] = ..., 
                copy_precedence: Optional[int] = ..., 
                extended_retention: Optional[list[ExtendedRetentionTime]] = ..., 
                name: str, 
                retention_period: Optional[int] = ..., 
                retention_time: Optional[Union[str, RetentionTime]] = ..., 
                storage_pool_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.StorageProperties(_Model):
        class_property: Union[str, StorageClassType]
        location: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        storage_type: Union[str, StorageType]
        vendor: Union[str, Vendor]

        @overload
        def __init__(
                self, 
                *, 
                class_property: Union[str, StorageClassType], 
                location: str, 
                storage_type: Union[str, StorageType], 
                vendor: Union[str, Vendor]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.StorageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AIR_GAP_PROTECT = "Air_Gap_Protect"


    class azure.mgmt.commvaultcontentstore.models.SystemData(_Model):
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


    class azure.mgmt.commvaultcontentstore.models.TrackedResource(Resource):
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


    class azure.mgmt.commvaultcontentstore.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.commvaultcontentstore.models.UserDetails(_Model):
        email_address: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        phone_number: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                email_address: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.Vendor(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE = "Azure_Blob_Storage"


    class azure.mgmt.commvaultcontentstore.models.VmDestinationInfo(_Model):
        vm_info_list: list[VmInfo]

        @overload
        def __init__(
                self, 
                *, 
                vm_info_list: list[VmInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.VmInfo(_Model):
        attach_and_swap_os_disk: Optional[bool]
        name: Optional[str]
        network_id: Optional[str]
        power_on_vm_after_restore: Optional[bool]
        region: Optional[str]
        resource_group: Optional[str]
        source_vm_guid: str
        storage_account_id: str
        subnet_id: Optional[str]
        target_vm_guid: Optional[str]
        vmtags: Optional[list[VmTag]]

        @overload
        def __init__(
                self, 
                *, 
                attach_and_swap_os_disk: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                network_id: Optional[str] = ..., 
                power_on_vm_after_restore: Optional[bool] = ..., 
                region: Optional[str] = ..., 
                resource_group: Optional[str] = ..., 
                source_vm_guid: str, 
                storage_account_id: str, 
                subnet_id: Optional[str] = ..., 
                target_vm_guid: Optional[str] = ..., 
                vmtags: Optional[list[VmTag]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.VmListItem(_Model):
        vm_guid: str

        @overload
        def __init__(
                self, 
                *, 
                vm_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.commvaultcontentstore.models.VmTag(_Model):
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


    class azure.mgmt.commvaultcontentstore.models.WeekOfMonth(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "FIRST"
        FOURTH = "FOURTH"
        LAST = "LAST"
        SECOND = "SECOND"
        THIRD = "THIRD"


    class azure.mgmt.commvaultcontentstore.models.WeeklyDays(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "FRIDAY"
        MONDAY = "MONDAY"
        SATURDAY = "SATURDAY"
        SUNDAY = "SUNDAY"
        THURSDAY = "THURSDAY"
        TUESDAY = "TUESDAY"
        WEDNESDAY = "WEDNESDAY"


namespace azure.mgmt.commvaultcontentstore.operations

    class azure.mgmt.commvaultcontentstore.operations.CloudAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: CloudAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: CloudAccountUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudAccount]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> CloudAccount: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-06-02-preview', params_added_on={'2026-06-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-06-02-preview', '2026-07-01-preview', '2026-07-03-preview'])
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[CloudAccount]: ...


    class azure.mgmt.commvaultcontentstore.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.commvaultcontentstore.operations.PlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: CommvaultPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommvaultPlan]: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommvaultPlan]: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommvaultPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                plan_name: str, 
                **kwargs: Any
            ) -> CommvaultPlan: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommvaultPlan]: ...


    class azure.mgmt.commvaultcontentstore.operations.ProtectedItemsOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def count_by_protection_groups(
                self, 
                body: CountProtectedItemsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...

        @overload
        def count_by_protection_groups(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...

        @overload
        def count_by_protection_groups(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CountProtectedItemsResponse: ...


    class azure.mgmt.commvaultcontentstore.operations.ProtectedItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> ProtectedItem: ...

        @distributed_trace
        def get_restore_points(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                **kwargs: Any
            ) -> RestorePoints: ...

        @distributed_trace
        def list_by_protection_group(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectedItem]: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: RestoreProtectionItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                protected_item_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...


    class azure.mgmt.commvaultcontentstore.operations.ProtectionGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: BackupProtectionGroupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        def backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BackupProtectionGroupResponse: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: ProtectionGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionGroup]: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionGroup]: ...

        @overload
        def begin_create_orupdate(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProtectionGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: StopBackupProtectionGroupRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_stop_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> ProtectionGroup: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProtectionGroup]: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: RestoreProtectionItemRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @overload
        def restore(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RestoreProtectionItemResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'protection_group_name']}, api_versions_list=['2026-03-01-preview', '2026-05-01-preview', '2026-06-01-preview', '2026-06-02-preview', '2026-07-01-preview', '2026-07-03-preview'])
        def resume_backup(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                protection_group_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.commvaultcontentstore.operations.RoleMappingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: RoleMapping, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RoleMapping: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name']}, api_versions_list=['2026-07-03-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-07-03-preview'])
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> RoleMapping: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-03-preview', params_added_on={'2026-07-03-preview': ['api_version', 'subscription_id', 'resource_group_name', 'cloud_account_name', 'accept']}, api_versions_list=['2026-07-03-preview'])
        def list(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RoleMapping]: ...


    class azure.mgmt.commvaultcontentstore.operations.SaaSOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate_resource(
                self, 
                body: ActivateSaaSParameterRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...

        @overload
        def begin_activate_resource(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SaaSResourceDetailsResponse]: ...


    class azure.mgmt.commvaultcontentstore.operations.StoragesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: Storage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Storage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Storage]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Storage]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                storage_name: str, 
                **kwargs: Any
            ) -> Storage: ...

        @distributed_trace
        def list_by_cloud_account(
                self, 
                resource_group_name: str, 
                cloud_account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Storage]: ...


```