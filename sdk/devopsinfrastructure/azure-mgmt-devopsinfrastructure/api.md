```py
namespace azure.mgmt.devopsinfrastructure

    class azure.mgmt.devopsinfrastructure.DevOpsInfrastructureMgmtClient: implements ContextManager 
        image_versions: ImageVersionsOperations
        operations: Operations
        pools: PoolsOperations
        resource_details: ResourceDetailsOperations
        sku: SkuOperations
        subscription_usages: SubscriptionUsagesOperations

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


namespace azure.mgmt.devopsinfrastructure.aio

    class azure.mgmt.devopsinfrastructure.aio.DevOpsInfrastructureMgmtClient: implements AsyncContextManager 
        image_versions: ImageVersionsOperations
        operations: Operations
        pools: PoolsOperations
        resource_details: ResourceDetailsOperations
        sku: SkuOperations
        subscription_usages: SubscriptionUsagesOperations

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


namespace azure.mgmt.devopsinfrastructure.aio.operations

    class azure.mgmt.devopsinfrastructure.aio.operations.ImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image(
                self, 
                resource_group_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageVersion]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                body: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: DeleteResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: DeleteResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Pool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Pool]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.ResourceDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceDetailsObject]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.SkuOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.SubscriptionUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def usages(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Quota]: ...


namespace azure.mgmt.devopsinfrastructure.models

    class azure.mgmt.devopsinfrastructure.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.devopsinfrastructure.models.AgentProfile(_Model):
        kind: str
        resource_predictions: Optional[ResourcePredictions]
        resource_predictions_profile: Optional[ResourcePredictionsProfile]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                resource_predictions: Optional[ResourcePredictions] = ..., 
                resource_predictions_profile: Optional[ResourcePredictionsProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.AutomaticResourcePredictionsProfile(ResourcePredictionsProfile, discriminator='Automatic'):
        kind: Literal[ResourcePredictionsProfileType.AUTOMATIC]
        prediction_preference: Optional[Union[str, PredictionPreference]]

        @overload
        def __init__(
                self, 
                *, 
                prediction_preference: Optional[Union[str, PredictionPreference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.AvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.devopsinfrastructure.models.AzureDevOpsOrganizationProfile(OrganizationProfile, discriminator='AzureDevOps'):
        alias: Optional[str]
        description: Optional[str]
        kind: Literal["AzureDevOps"]
        organizations: list[Organization]
        permission_profile: Optional[AzureDevOpsPermissionProfile]
        update_description: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                alias: Optional[str] = ..., 
                description: Optional[str] = ..., 
                organizations: list[Organization], 
                permission_profile: Optional[AzureDevOpsPermissionProfile] = ..., 
                update_description: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.AzureDevOpsPermissionProfile(_Model):
        groups: Optional[list[str]]
        kind: Union[str, AzureDevOpsPermissionType]
        users: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[list[str]] = ..., 
                kind: Union[str, AzureDevOpsPermissionType], 
                users: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.AzureDevOpsPermissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATOR_ONLY = "CreatorOnly"
        INHERIT = "Inherit"
        SPECIFIC_ACCOUNTS = "SpecificAccounts"


    class azure.mgmt.devopsinfrastructure.models.CachingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.devopsinfrastructure.models.CertificateStoreNameOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MY = "My"
        ROOT = "Root"


    class azure.mgmt.devopsinfrastructure.models.CheckNameAvailability(_Model):
        name: str
        type: Union[str, DevOpsInfrastructureResourceType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, DevOpsInfrastructureResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.devopsinfrastructure.models.CheckNameAvailabilityResult(_Model):
        available: Union[str, AvailabilityStatus]
        message: str
        name: str
        reason: Union[str, CheckNameAvailabilityReason]

        @overload
        def __init__(
                self, 
                *, 
                available: Union[str, AvailabilityStatus], 
                message: str, 
                name: str, 
                reason: Union[str, CheckNameAvailabilityReason]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.devopsinfrastructure.models.DataDisk(_Model):
        caching: Optional[Union[str, CachingType]]
        disk_size_gi_b: Optional[int]
        drive_letter: Optional[str]
        storage_account_type: Optional[Union[str, StorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                caching: Optional[Union[str, CachingType]] = ..., 
                disk_size_gi_b: Optional[int] = ..., 
                drive_letter: Optional[str] = ..., 
                storage_account_type: Optional[Union[str, StorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.DeleteResourcesDetails(_Model):
        resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.DevOpsAzureSku(_Model):
        linux_nvme_path: Optional[str]
        name: str
        vm_sizes: Optional[list[VmSize]]
        windows_nvme_drive: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                linux_nvme_path: Optional[str] = ..., 
                name: str, 
                vm_sizes: Optional[list[VmSize]] = ..., 
                windows_nvme_drive: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.DevOpsInfrastructureResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_DEV_OPS_INFRASTRUCTURE_POOLS = "Microsoft.DevOpsInfrastructure/pools"


    class azure.mgmt.devopsinfrastructure.models.EphemeralType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        CACHE_DISK = "CacheDisk"
        NV_ME_DISK = "NVMeDisk"
        RESOURCE_DISK = "ResourceDisk"


    class azure.mgmt.devopsinfrastructure.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.FabricProfile(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.GitHubOrganization(_Model):
        repositories: Optional[list[str]]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                repositories: Optional[list[str]] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.GitHubOrganizationProfile(OrganizationProfile, discriminator='GitHub'):
        kind: Literal["GitHub"]
        organizations: list[GitHubOrganization]

        @overload
        def __init__(
                self, 
                *, 
                organizations: list[GitHubOrganization]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ImageVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ImageVersionProperties(_Model):
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.LogonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERACTIVE = "Interactive"
        SERVICE = "Service"


    class azure.mgmt.devopsinfrastructure.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.devopsinfrastructure.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.devopsinfrastructure.models.ManualResourcePredictionsProfile(ResourcePredictionsProfile, discriminator='Manual'):
        kind: Literal[ResourcePredictionsProfileType.MANUAL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.NetworkProfile(_Model):
        ip_addresses: Optional[list[str]]
        static_ip_address_count: Optional[int]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                static_ip_address_count: Optional[int] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.Operation(_Model):
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


    class azure.mgmt.devopsinfrastructure.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.Organization(_Model):
        alias: Optional[str]
        open_access: Optional[bool]
        parallelism: Optional[int]
        projects: Optional[list[str]]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                alias: Optional[str] = ..., 
                open_access: Optional[bool] = ..., 
                parallelism: Optional[int] = ..., 
                projects: Optional[list[str]] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.OrganizationProfile(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.devopsinfrastructure.models.OsDiskStorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"
        STANDARD_SSD = "StandardSSD"


    class azure.mgmt.devopsinfrastructure.models.OsProfile(_Model):
        logon_type: Optional[Union[str, LogonType]]
        secrets_management_settings: Optional[SecretsManagementSettings]

        @overload
        def __init__(
                self, 
                *, 
                logon_type: Optional[Union[str, LogonType]] = ..., 
                secrets_management_settings: Optional[SecretsManagementSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.Pool(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[PoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[PoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolImage(_Model):
        aliases: Optional[list[str]]
        buffer: Optional[str]
        ephemeral_type: Optional[Union[str, EphemeralType]]
        is_ephemeral: Optional[bool]
        provisioning_script_entry_point: Optional[str]
        provisioning_script_managed_identity_client_id: Optional[str]
        provisioning_script_should_restart: Optional[bool]
        provisioning_script_storage_account_resource_id: Optional[str]
        resource_id: Optional[str]
        well_known_image_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[list[str]] = ..., 
                buffer: Optional[str] = ..., 
                ephemeral_type: Optional[Union[str, EphemeralType]] = ..., 
                provisioning_script_entry_point: Optional[str] = ..., 
                provisioning_script_managed_identity_client_id: Optional[str] = ..., 
                provisioning_script_should_restart: Optional[bool] = ..., 
                provisioning_script_storage_account_resource_id: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                well_known_image_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolProperties(_Model):
        agent_profile: AgentProfile
        dev_center_project_resource_id: Optional[str]
        fabric_profile: FabricProfile
        maximum_concurrency: int
        organization_profile: OrganizationProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]
        runtime_configuration: Optional[RuntimeConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: AgentProfile, 
                dev_center_project_resource_id: Optional[str] = ..., 
                fabric_profile: FabricProfile, 
                maximum_concurrency: int, 
                organization_profile: OrganizationProfile, 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                runtime_configuration: Optional[RuntimeConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[PoolUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[PoolUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolUpdateProperties(_Model):
        agent_profile: Optional[AgentProfile]
        dev_center_project_resource_id: Optional[str]
        fabric_profile: Optional[FabricProfile]
        maximum_concurrency: Optional[int]
        organization_profile: Optional[OrganizationProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        runtime_configuration: Optional[RuntimeConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: Optional[AgentProfile] = ..., 
                dev_center_project_resource_id: Optional[str] = ..., 
                fabric_profile: Optional[FabricProfile] = ..., 
                maximum_concurrency: Optional[int] = ..., 
                organization_profile: Optional[OrganizationProfile] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ..., 
                runtime_configuration: Optional[RuntimeConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PredictionPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED = "Balanced"
        BEST_PERFORMANCE = "BestPerformance"
        MORE_COST_EFFECTIVE = "MoreCostEffective"
        MORE_PERFORMANCE = "MorePerformance"
        MOST_COST_EFFECTIVE = "MostCostEffective"


    class azure.mgmt.devopsinfrastructure.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.devopsinfrastructure.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.devopsinfrastructure.models.Quota(_Model):
        current_value: int
        id: str
        limit: int
        name: Optional[QuotaName]
        unit: str

        @overload
        def __init__(
                self, 
                *, 
                current_value: int, 
                id: str, 
                limit: int, 
                unit: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.QuotaName(_Model):
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


    class azure.mgmt.devopsinfrastructure.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.ResourceDetailsObject(ProxyResource):
        id: str
        name: str
        properties: Optional[ResourceDetailsObjectProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResourceDetailsObjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceDetailsObjectProperties(_Model):
        image: str
        image_version: str
        status: Union[str, ResourceStatus]

        @overload
        def __init__(
                self, 
                *, 
                image: str, 
                image_version: str, 
                status: Union[str, ResourceStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourcePredictions(_Model):


    class azure.mgmt.devopsinfrastructure.models.ResourcePredictionsProfile(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourcePredictionsProfileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.devopsinfrastructure.models.ResourceSku(ProxyResource):
        id: str
        name: str
        properties: Optional[ResourceSkuProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResourceSkuProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuCapabilities(_Model):
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


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuLocationInfo(_Model):
        location: str
        zone_details: list[ResourceSkuZoneDetails]
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                zone_details: list[ResourceSkuZoneDetails], 
                zones: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuProperties(_Model):
        capabilities: list[ResourceSkuCapabilities]
        family: str
        location_info: list[ResourceSkuLocationInfo]
        locations: list[str]
        resource_type: str
        restrictions: list[ResourceSkuRestrictions]
        size: str
        tier: str

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[ResourceSkuCapabilities], 
                family: str, 
                location_info: list[ResourceSkuLocationInfo], 
                locations: list[str], 
                resource_type: str, 
                restrictions: list[ResourceSkuRestrictions], 
                size: str, 
                tier: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionInfo(_Model):
        locations: Optional[list[str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictions(_Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: ResourceSkuRestrictionInfo
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]] = ..., 
                restriction_info: ResourceSkuRestrictionInfo, 
                type: Optional[Union[str, ResourceSkuRestrictionsType]] = ..., 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuZoneDetails(_Model):
        capabilities: list[ResourceSkuCapabilities]
        name: list[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[ResourceSkuCapabilities], 
                name: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOCATED = "Allocated"
        LEASED = "Leased"
        NOT_READY = "NotReady"
        PENDING_REIMAGE = "PendingReimage"
        PENDING_RETURN = "PendingReturn"
        PROVISIONING = "Provisioning"
        READY = "Ready"
        REIMAGING = "Reimaging"
        RETURNED = "Returned"
        STARTING = "Starting"
        UPDATING = "Updating"


    class azure.mgmt.devopsinfrastructure.models.RuntimeConfiguration(_Model):
        work_folder: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                work_folder: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.SecretsManagementSettings(_Model):
        certificate_store_location: Optional[str]
        certificate_store_name: Optional[Union[str, CertificateStoreNameOption]]
        key_exportable: bool
        observed_certificates: list[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_store_location: Optional[str] = ..., 
                certificate_store_name: Optional[Union[str, CertificateStoreNameOption]] = ..., 
                key_exportable: bool, 
                observed_certificates: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.Stateful(AgentProfile, discriminator='Stateful'):
        grace_period_time_span: Optional[str]
        kind: Literal["Stateful"]
        max_agent_lifetime: Optional[str]
        resource_predictions: ResourcePredictions
        resource_predictions_profile: ResourcePredictionsProfile

        @overload
        def __init__(
                self, 
                *, 
                grace_period_time_span: Optional[str] = ..., 
                max_agent_lifetime: Optional[str] = ..., 
                resource_predictions: Optional[ResourcePredictions] = ..., 
                resource_predictions_profile: Optional[ResourcePredictionsProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.StatelessAgentProfile(AgentProfile, discriminator='Stateless'):
        kind: Literal["Stateless"]
        resource_predictions: ResourcePredictions
        resource_predictions_profile: ResourcePredictionsProfile

        @overload
        def __init__(
                self, 
                *, 
                resource_predictions: Optional[ResourcePredictions] = ..., 
                resource_predictions_profile: Optional[ResourcePredictionsProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.StorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSDLRS = "StandardSSD_LRS"
        STANDARD_SSDZRS = "StandardSSD_ZRS"


    class azure.mgmt.devopsinfrastructure.models.StorageProfile(_Model):
        data_disks: Optional[list[DataDisk]]
        os_disk_storage_account_type: Optional[Union[str, OsDiskStorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[list[DataDisk]] = ..., 
                os_disk_storage_account_type: Optional[Union[str, OsDiskStorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.SystemData(_Model):
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


    class azure.mgmt.devopsinfrastructure.models.TrackedResource(Resource):
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


    class azure.mgmt.devopsinfrastructure.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.VmSize(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.VmssFabricProfile(FabricProfile, discriminator='Vmss'):
        images: list[PoolImage]
        kind: Literal["Vmss"]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OsProfile]
        sku: DevOpsAzureSku
        storage_profile: Optional[StorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                images: list[PoolImage], 
                network_profile: Optional[NetworkProfile] = ..., 
                os_profile: Optional[OsProfile] = ..., 
                sku: DevOpsAzureSku, 
                storage_profile: Optional[StorageProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.devopsinfrastructure.operations

    class azure.mgmt.devopsinfrastructure.operations.ImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image(
                self, 
                resource_group_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImageVersion]: ...


    class azure.mgmt.devopsinfrastructure.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.devopsinfrastructure.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                body: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: DeleteResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: DeleteResourcesDetails, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def delete_resources(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Pool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Pool]: ...


    class azure.mgmt.devopsinfrastructure.operations.ResourceDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceDetailsObject]: ...


    class azure.mgmt.devopsinfrastructure.operations.SkuOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.devopsinfrastructure.operations.SubscriptionUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def usages(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Quota]: ...


namespace azure.mgmt.devopsinfrastructure.types

    class azure.mgmt.devopsinfrastructure.types.AutomaticResourcePredictionsProfile(TypedDict, total=False):
        key "kind": Required[Literal[ResourcePredictionsProfileType.AUTOMATIC]]
        key "predictionPreference": Union[str, PredictionPreference]
        kind: Literal[ResourcePredictionsProfileType.AUTOMATIC]
        prediction_preference: Union[str, PredictionPreference]


    class azure.mgmt.devopsinfrastructure.types.AzureDevOpsOrganizationProfile(TypedDict, total=False):
        key "alias": str
        key "description": str
        key "kind": Required[Literal["AzureDevOps"]]
        key "organizations": Required[list[Organization]]
        key "permissionProfile": ForwardRef('AzureDevOpsPermissionProfile', module='types')
        key "updateDescription": bool
        alias: str
        description: str
        kind: Literal[AzureDevOps]
        organizations: list[Organization]
        permission_profile: AzureDevOpsPermissionProfile
        update_description: bool


    class azure.mgmt.devopsinfrastructure.types.AzureDevOpsPermissionProfile(TypedDict, total=False):
        key "kind": Required[Union[str, AzureDevOpsPermissionType]]
        groups: list[str]
        kind: Union[str, AzureDevOpsPermissionType]
        users: list[str]


    class azure.mgmt.devopsinfrastructure.types.CheckNameAvailability(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, DevOpsInfrastructureResourceType]]
        name: str
        type: Union[str, DevOpsInfrastructureResourceType]


    class azure.mgmt.devopsinfrastructure.types.DataDisk(TypedDict, total=False):
        key "caching": Union[str, CachingType]
        key "diskSizeGiB": int
        key "driveLetter": str
        key "storageAccountType": Union[str, StorageAccountType]
        caching: Union[str, CachingType]
        disk_size_gi_b: int
        drive_letter: str
        storage_account_type: Union[str, StorageAccountType]


    class azure.mgmt.devopsinfrastructure.types.DeleteResourcesDetails(TypedDict, total=False):
        key "resourceIds": Required[list[str]]
        resource_ids: list[str]


    class azure.mgmt.devopsinfrastructure.types.DevOpsAzureSku(TypedDict, total=False):
        key "linuxNvmePath": str
        key "name": Required[str]
        key "windowsNvmeDrive": str
        linux_nvme_path: str
        name: str
        vmSizes: list[VmSize]
        vm_sizes: list[VmSize]
        windows_nvme_drive: str


    class azure.mgmt.devopsinfrastructure.types.FabricProfile(TypedDict, total=False):
        key "images": Required[list[PoolImage]]
        key "kind": Required[Literal["Vmss"]]
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "osProfile": ForwardRef('OsProfile', module='types')
        key "sku": Required[DevOpsAzureSku]
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        images: list[PoolImage]
        kind: Literal[Vmss]
        network_profile: NetworkProfile
        os_profile: OsProfile
        sku: DevOpsAzureSku
        storage_profile: StorageProfile


    class azure.mgmt.devopsinfrastructure.types.GitHubOrganization(TypedDict, total=False):
        key "url": Required[str]
        repositories: list[str]
        url: str


    class azure.mgmt.devopsinfrastructure.types.GitHubOrganizationProfile(TypedDict, total=False):
        key "kind": Required[Literal["GitHub"]]
        key "organizations": Required[list[GitHubOrganization]]
        kind: Literal[GitHub]
        organizations: list[GitHubOrganization]


    class azure.mgmt.devopsinfrastructure.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.devopsinfrastructure.types.ManualResourcePredictionsProfile(TypedDict, total=False):
        key "kind": Required[Literal[ResourcePredictionsProfileType.MANUAL]]
        kind: Literal[ResourcePredictionsProfileType.MANUAL]


    class azure.mgmt.devopsinfrastructure.types.NetworkProfile(TypedDict, total=False):
        key "staticIpAddressCount": int
        key "subnetId": str
        ipAddresses: list[str]
        ip_addresses: list[str]
        static_ip_address_count: int
        subnet_id: str


    class azure.mgmt.devopsinfrastructure.types.Organization(TypedDict, total=False):
        key "alias": str
        key "openAccess": bool
        key "parallelism": int
        key "url": Required[str]
        alias: str
        open_access: bool
        parallelism: int
        projects: list[str]
        url: str


    class azure.mgmt.devopsinfrastructure.types.OsProfile(TypedDict, total=False):
        key "logonType": Union[str, LogonType]
        key "secretsManagementSettings": ForwardRef('SecretsManagementSettings', module='types')
        logon_type: Union[str, LogonType]
        secrets_management_settings: SecretsManagementSettings


    class azure.mgmt.devopsinfrastructure.types.Pool(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: PoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devopsinfrastructure.types.PoolImage(TypedDict, total=False):
        key "buffer": str
        key "ephemeralType": Union[str, EphemeralType]
        key "isEphemeral": bool
        key "provisioningScriptEntryPoint": str
        key "provisioningScriptManagedIdentityClientId": str
        key "provisioningScriptShouldRestart": bool
        key "provisioningScriptStorageAccountResourceId": str
        key "resourceId": str
        key "wellKnownImageName": str
        aliases: list[str]
        buffer: str
        ephemeral_type: Union[str, EphemeralType]
        is_ephemeral: bool
        provisioning_script_entry_point: str
        provisioning_script_managed_identity_client_id: str
        provisioning_script_should_restart: bool
        provisioning_script_storage_account_resource_id: str
        resource_id: str
        well_known_image_name: str


    class azure.mgmt.devopsinfrastructure.types.PoolProperties(TypedDict, total=False):
        key "agentProfile": Required[AgentProfile]
        key "devCenterProjectResourceId": str
        key "fabricProfile": Required[FabricProfile]
        key "maximumConcurrency": Required[int]
        key "organizationProfile": Required[OrganizationProfile]
        key "provisioningState": Union[str, ProvisioningState]
        key "runtimeConfiguration": ForwardRef('RuntimeConfiguration', module='types')
        agent_profile: AgentProfile
        dev_center_project_resource_id: str
        fabric_profile: FabricProfile
        maximum_concurrency: int
        organization_profile: OrganizationProfile
        provisioning_state: Union[str, ProvisioningState]
        runtime_configuration: RuntimeConfiguration


    class azure.mgmt.devopsinfrastructure.types.PoolUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('PoolUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: PoolUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devopsinfrastructure.types.PoolUpdateProperties(TypedDict, total=False):
        key "agentProfile": ForwardRef('AgentProfile', module='types')
        key "devCenterProjectResourceId": str
        key "fabricProfile": ForwardRef('FabricProfile', module='types')
        key "maximumConcurrency": int
        key "organizationProfile": ForwardRef('OrganizationProfile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "runtimeConfiguration": ForwardRef('RuntimeConfiguration', module='types')
        agent_profile: AgentProfile
        dev_center_project_resource_id: str
        fabric_profile: FabricProfile
        maximum_concurrency: int
        organization_profile: OrganizationProfile
        provisioning_state: Union[str, ProvisioningState]
        runtime_configuration: RuntimeConfiguration


    class azure.mgmt.devopsinfrastructure.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.devopsinfrastructure.types.ResourcePredictions(TypedDict, total=False):


    class azure.mgmt.devopsinfrastructure.types.ResourcePredictionsProfileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.devopsinfrastructure.types.RuntimeConfiguration(TypedDict, total=False):
        key "workFolder": str
        work_folder: str


    class azure.mgmt.devopsinfrastructure.types.SecretsManagementSettings(TypedDict, total=False):
        key "certificateStoreLocation": str
        key "certificateStoreName": Union[str, CertificateStoreNameOption]
        key "keyExportable": Required[bool]
        key "observedCertificates": Required[list[str]]
        certificate_store_location: str
        certificate_store_name: Union[str, CertificateStoreNameOption]
        key_exportable: bool
        observed_certificates: list[str]


    class azure.mgmt.devopsinfrastructure.types.Stateful(TypedDict, total=False):
        key "gracePeriodTimeSpan": str
        key "kind": Required[Literal["Stateful"]]
        key "maxAgentLifetime": str
        key "resourcePredictions": ForwardRef('ResourcePredictions', module='types')
        key "resourcePredictionsProfile": ForwardRef('ResourcePredictionsProfile', module='types')
        grace_period_time_span: str
        kind: Literal[Stateful]
        max_agent_lifetime: str
        resource_predictions: ResourcePredictions
        resource_predictions_profile: ResourcePredictionsProfile


    class azure.mgmt.devopsinfrastructure.types.StatelessAgentProfile(TypedDict, total=False):
        key "kind": Required[Literal["Stateless"]]
        key "resourcePredictions": ForwardRef('ResourcePredictions', module='types')
        key "resourcePredictionsProfile": ForwardRef('ResourcePredictionsProfile', module='types')
        kind: Literal[Stateless]
        resource_predictions: ResourcePredictions
        resource_predictions_profile: ResourcePredictionsProfile


    class azure.mgmt.devopsinfrastructure.types.StorageProfile(TypedDict, total=False):
        key "osDiskStorageAccountType": Union[str, OsDiskStorageAccountType]
        dataDisks: list[DataDisk]
        data_disks: list[DataDisk]
        os_disk_storage_account_type: Union[str, OsDiskStorageAccountType]


    class azure.mgmt.devopsinfrastructure.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.devopsinfrastructure.types.TrackedResource(Resource):
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


    class azure.mgmt.devopsinfrastructure.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.devopsinfrastructure.types.VmSize(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.devopsinfrastructure.types.VmssFabricProfile(TypedDict, total=False):
        key "images": Required[list[PoolImage]]
        key "kind": Required[Literal["Vmss"]]
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "osProfile": ForwardRef('OsProfile', module='types')
        key "sku": Required[DevOpsAzureSku]
        key "storageProfile": ForwardRef('StorageProfile', module='types')
        images: list[PoolImage]
        kind: Literal[Vmss]
        network_profile: NetworkProfile
        os_profile: OsProfile
        sku: DevOpsAzureSku
        storage_profile: StorageProfile


```