```py
namespace azure.mgmt.mongodbatlas

    class azure.mgmt.mongodbatlas.MongoDBAtlasMgmtClient: implements ContextManager 
        clusters: ClustersOperations
        operations: Operations
        organizations: OrganizationsOperations
        projects: ProjectsOperations

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


namespace azure.mgmt.mongodbatlas.aio

    class azure.mgmt.mongodbatlas.aio.MongoDBAtlasMgmtClient: implements AsyncContextManager 
        clusters: ClustersOperations
        operations: Operations
        organizations: OrganizationsOperations
        projects: ProjectsOperations

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


namespace azure.mgmt.mongodbatlas.aio.operations

    class azure.mgmt.mongodbatlas.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'cluster_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'cluster_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...


    class azure.mgmt.mongodbatlas.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.mongodbatlas.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[OrganizationResource]: ...


    class azure.mgmt.mongodbatlas.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def list_cluster_tier_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> RegionsByTierResponse: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def tier_limit_reached(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> TierLimitReachedResponse: ...


namespace azure.mgmt.mongodbatlas.models

    class azure.mgmt.mongodbatlas.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.mongodbatlas.models.Cluster(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.ClusterProperties(_Model):
        backups: Optional[bool]
        cluster_name: Optional[str]
        cluster_tier: Union[str, ClusterTier]
        mongo_db_version: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        region_name: str
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_tier: Union[str, ClusterTier], 
                region_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.ClusterTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLEX = "FLEX"
        FREE = "FREE"
        M10 = "M10"
        M30 = "M30"


    class azure.mgmt.mongodbatlas.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.mongodbatlas.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.mongodbatlas.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.mongodbatlas.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.mongodbatlas.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.mongodbatlas.models.MarketplaceDetails(_Model):
        offer_details: OfferDetails
        subscription_id: str
        subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                offer_details: OfferDetails, 
                subscription_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.mongodbatlas.models.OfferDetails(_Model):
        offer_id: str
        plan_id: str
        plan_name: Optional[str]
        publisher_id: str
        term_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: str, 
                plan_id: str, 
                plan_name: Optional[str] = ..., 
                publisher_id: str, 
                term_id: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.Operation(_Model):
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


    class azure.mgmt.mongodbatlas.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.mongodbatlas.models.OrganizationProperties(_Model):
        marketplace: MarketplaceDetails
        partner_properties: Optional[PartnerProperties]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        user: UserDetails

        @overload
        def __init__(
                self, 
                *, 
                marketplace: MarketplaceDetails, 
                partner_properties: Optional[PartnerProperties] = ..., 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.OrganizationResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[OrganizationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[OrganizationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.OrganizationResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[OrganizationResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[OrganizationResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.OrganizationResourceUpdateProperties(_Model):
        partner_properties: Optional[PartnerProperties]
        user: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                partner_properties: Optional[PartnerProperties] = ..., 
                user: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.mongodbatlas.models.PartnerProperties(_Model):
        organization_id: Optional[str]
        organization_name: str
        redirect_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                organization_id: Optional[str] = ..., 
                organization_name: str, 
                redirect_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.Project(ProxyResource):
        id: str
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.ProjectLimitStatus(_Model):
        current: int
        is_reached: bool
        maximum: int
        type: Union[str, ClusterTier]

        @overload
        def __init__(
                self, 
                *, 
                current: int, 
                is_reached: bool, 
                maximum: int, 
                type: Union[str, ClusterTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.ProjectProperties(_Model):
        cluster_count: Optional[int]
        organization_id: Optional[str]
        project_id: Optional[str]
        project_name: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]


    class azure.mgmt.mongodbatlas.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.mongodbatlas.models.RegionsByTierResponse(_Model):
        organization_id: str
        project_id: str
        regions_by_tier: list[TierRegions]


    class azure.mgmt.mongodbatlas.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.mongodbatlas.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.mongodbatlas.models.SystemData(_Model):
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


    class azure.mgmt.mongodbatlas.models.TierLimitReachedResponse(_Model):
        limits: list[ProjectLimitStatus]


    class azure.mgmt.mongodbatlas.models.TierRegions(_Model):
        regions: list[str]
        tier: Union[str, ClusterTier]

        @overload
        def __init__(
                self, 
                *, 
                regions: list[str], 
                tier: Union[str, ClusterTier]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.mongodbatlas.models.TrackedResource(Resource):
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


    class azure.mgmt.mongodbatlas.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.mongodbatlas.models.UserDetails(_Model):
        company_name: Optional[str]
        email_address: str
        first_name: str
        last_name: str
        phone_number: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                company_name: Optional[str] = ..., 
                email_address: str, 
                first_name: str, 
                last_name: str, 
                phone_number: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.mongodbatlas.operations

    class azure.mgmt.mongodbatlas.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'cluster_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'cluster_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...


    class azure.mgmt.mongodbatlas.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.mongodbatlas.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[OrganizationResource]: ...


    class azure.mgmt.mongodbatlas.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list_cluster_tier_regions(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> RegionsByTierResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'organization_name', 'project_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def tier_limit_reached(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> TierLimitReachedResponse: ...


```