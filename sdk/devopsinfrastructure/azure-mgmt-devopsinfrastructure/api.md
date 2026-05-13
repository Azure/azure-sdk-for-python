```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                base_url: str = "https://management.azure.com", 
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
                base_url: str = "https://management.azure.com", 
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
            ) -> AsyncIterable[ImageVersion]: ...


    class azure.mgmt.devopsinfrastructure.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> AsyncIterable[Pool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[Pool]: ...


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
            ) -> AsyncIterable[ResourceDetailsObject]: ...


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
            ) -> AsyncIterable[ResourceSku]: ...


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
            ) -> AsyncIterable[Quota]: ...


namespace azure.mgmt.devopsinfrastructure.models

    class azure.mgmt.devopsinfrastructure.models.AgentProfile(Model):
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


    class azure.mgmt.devopsinfrastructure.models.AzureDevOpsOrganizationProfile(OrganizationProfile, discriminator='AzureDevOps'):
        kind: Literal["AzureDevOps"]
        organizations: List[Organization]
        permission_profile: Optional[AzureDevOpsPermissionProfile]

        @overload
        def __init__(
                self, 
                *, 
                organizations: List[Organization], 
                permission_profile: Optional[AzureDevOpsPermissionProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.AzureDevOpsPermissionProfile(Model):
        groups: Optional[List[str]]
        kind: Union[str, AzureDevOpsPermissionType]
        users: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                groups: Optional[List[str]] = ..., 
                kind: Union[str, AzureDevOpsPermissionType], 
                users: Optional[List[str]] = ...
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


    class azure.mgmt.devopsinfrastructure.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.devopsinfrastructure.models.DataDisk(Model):
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


    class azure.mgmt.devopsinfrastructure.models.DevOpsAzureSku(Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.FabricProfile(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.GitHubOrganization(Model):
        repositories: Optional[List[str]]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                repositories: Optional[List[str]] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.GitHubOrganizationProfile(OrganizationProfile, discriminator='GitHub'):
        kind: Literal["GitHub"]
        organizations: List[GitHubOrganization]

        @overload
        def __init__(
                self, 
                *, 
                organizations: List[GitHubOrganization]
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


    class azure.mgmt.devopsinfrastructure.models.ImageVersionProperties(Model):
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


    class azure.mgmt.devopsinfrastructure.models.ManagedServiceIdentity(Model):
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


    class azure.mgmt.devopsinfrastructure.models.NetworkProfile(Model):
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.Organization(Model):
        parallelism: Optional[int]
        projects: Optional[List[str]]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                parallelism: Optional[int] = ..., 
                projects: Optional[List[str]] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.OrganizationProfile(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.OsDiskStorageAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"
        STANDARD = "Standard"
        STANDARD_SSD = "StandardSSD"


    class azure.mgmt.devopsinfrastructure.models.OsProfile(Model):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolImage(Model):
        aliases: Optional[List[str]]
        buffer: Optional[str]
        resource_id: Optional[str]
        well_known_image_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aliases: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                well_known_image_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolProperties(Model):
        agent_profile: AgentProfile
        dev_center_project_resource_id: str
        fabric_profile: FabricProfile
        maximum_concurrency: int
        organization_profile: OrganizationProfile
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: AgentProfile, 
                dev_center_project_resource_id: str, 
                fabric_profile: FabricProfile, 
                maximum_concurrency: int, 
                organization_profile: OrganizationProfile, 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolUpdate(Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[PoolUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[PoolUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.PoolUpdateProperties(Model):
        agent_profile: Optional[AgentProfile]
        dev_center_project_resource_id: Optional[str]
        fabric_profile: Optional[FabricProfile]
        maximum_concurrency: Optional[int]
        organization_profile: Optional[OrganizationProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                agent_profile: Optional[AgentProfile] = ..., 
                dev_center_project_resource_id: Optional[str] = ..., 
                fabric_profile: Optional[FabricProfile] = ..., 
                maximum_concurrency: Optional[int] = ..., 
                organization_profile: Optional[OrganizationProfile] = ..., 
                provisioning_state: Optional[Union[str, ProvisioningState]] = ...
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


    class azure.mgmt.devopsinfrastructure.models.Quota(Model):
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


    class azure.mgmt.devopsinfrastructure.models.QuotaName(Model):
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


    class azure.mgmt.devopsinfrastructure.models.Resource(Model):
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


    class azure.mgmt.devopsinfrastructure.models.ResourceDetailsObjectProperties(Model):
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


    class azure.mgmt.devopsinfrastructure.models.ResourcePredictions(Model):


    class azure.mgmt.devopsinfrastructure.models.ResourcePredictionsProfile(Model):
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


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuCapabilities(Model):
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


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuLocationInfo(Model):
        location: str
        zone_details: List[ResourceSkuZoneDetails]
        zones: List[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                zone_details: List[ResourceSkuZoneDetails], 
                zones: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuProperties(Model):
        capabilities: List[ResourceSkuCapabilities]
        family: str
        location_info: List[ResourceSkuLocationInfo]
        locations: List[str]
        resource_type: str
        restrictions: List[ResourceSkuRestrictions]
        size: str
        tier: str

        @overload
        def __init__(
                self, 
                *, 
                capabilities: List[ResourceSkuCapabilities], 
                family: str, 
                location_info: List[ResourceSkuLocationInfo], 
                locations: List[str], 
                resource_type: str, 
                restrictions: List[ResourceSkuRestrictions], 
                size: str, 
                tier: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionInfo(Model):
        locations: Optional[List[str]]
        zones: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[List[str]] = ..., 
                zones: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictions(Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: ResourceSkuRestrictionInfo
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: List[str]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]] = ..., 
                restriction_info: ResourceSkuRestrictionInfo, 
                type: Optional[Union[str, ResourceSkuRestrictionsType]] = ..., 
                values_property: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.devopsinfrastructure.models.ResourceSkuZoneDetails(Model):
        capabilities: List[ResourceSkuCapabilities]
        name: List[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: List[ResourceSkuCapabilities], 
                name: List[str]
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


    class azure.mgmt.devopsinfrastructure.models.SecretsManagementSettings(Model):
        certificate_store_location: Optional[str]
        key_exportable: bool
        observed_certificates: List[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_store_location: Optional[str] = ..., 
                key_exportable: bool, 
                observed_certificates: List[str]
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


    class azure.mgmt.devopsinfrastructure.models.StorageProfile(Model):
        data_disks: Optional[List[DataDisk]]
        os_disk_storage_account_type: Optional[Union[str, OsDiskStorageAccountType]]

        @overload
        def __init__(
                self, 
                *, 
                data_disks: Optional[List[DataDisk]] = ..., 
                os_disk_storage_account_type: Optional[Union[str, OsDiskStorageAccountType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devopsinfrastructure.models.SystemData(Model):
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


    class azure.mgmt.devopsinfrastructure.models.UserAssignedIdentity(Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.devopsinfrastructure.models.VmssFabricProfile(FabricProfile, discriminator='Vmss'):
        images: List[PoolImage]
        kind: Literal["Vmss"]
        network_profile: Optional[NetworkProfile]
        os_profile: Optional[OsProfile]
        sku: DevOpsAzureSku
        storage_profile: Optional[StorageProfile]

        @overload
        def __init__(
                self, 
                *, 
                images: List[PoolImage], 
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
            ): ...

        @distributed_trace
        def list_by_image(
                self, 
                resource_group_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Iterable[ImageVersion]: ...


    class azure.mgmt.devopsinfrastructure.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.devopsinfrastructure.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> Iterable[Pool]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[Pool]: ...


    class azure.mgmt.devopsinfrastructure.operations.ResourceDetailsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Iterable[ResourceDetailsObject]: ...


    class azure.mgmt.devopsinfrastructure.operations.SkuOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_location(
                self, 
                location_name: str, 
                **kwargs: Any
            ) -> Iterable[ResourceSku]: ...


    class azure.mgmt.devopsinfrastructure.operations.SubscriptionUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def usages(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[Quota]: ...


```