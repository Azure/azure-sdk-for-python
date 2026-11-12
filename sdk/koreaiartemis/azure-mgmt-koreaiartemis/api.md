```py
namespace azure.mgmt.koreaiartemis

    class azure.mgmt.koreaiartemis.KoreAIArtemisMgmtClient: implements ContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.koreaiartemis.aio

    class azure.mgmt.koreaiartemis.aio.KoreAIArtemisMgmtClient: implements AsyncContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.koreaiartemis.aio.operations

    class azure.mgmt.koreaiartemis.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.koreaiartemis.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create(
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

        @distributed_trace_async
        async def list_workspaces(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ListWorkspacesResponse: ...


    class azure.mgmt.koreaiartemis.aio.operations.SaaSOperationGroupOperations:

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
                body: ActivateSaaSParameterRequest, 
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


    class azure.mgmt.koreaiartemis.aio.operations.WorkspacesOperations:

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
                workspace_name: str, 
                resource: WorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                resource: WorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkspaceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: WorkspaceSaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: WorkspaceSaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceResource: ...

        @distributed_trace_async
        async def get_details(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceDetail: ...

        @distributed_trace
        def list_by_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkspaceResource]: ...

        @distributed_trace_async
        async def list_linked_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceLinkedSaaSListResponse: ...


namespace azure.mgmt.koreaiartemis.models

    class azure.mgmt.koreaiartemis.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.koreaiartemis.models.ActivateSaaSParameterRequest(_Model):
        publisher_id: str
        saas_guid: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: str, 
                saas_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.CompanyDetails(_Model):
        business_type: Optional[str]
        company_name: Optional[str]
        country: Optional[str]
        domain: Optional[str]
        number_of_employees: Optional[int]
        office_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                business_type: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                number_of_employees: Optional[int] = ..., 
                office_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.koreaiartemis.models.DefaultWorkspaceProperties(_Model):
        marketplace_details: list[MarketplaceDetails]
        name: str
        product: Optional[Union[str, Product]]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_details: list[MarketplaceDetails], 
                name: str, 
                product: Optional[Union[str, Product]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.DiscoveredWorkspace(_Model):
        arm_resource_id: Optional[str]
        is_default: Optional[bool]
        is_managed_by_liftr: bool
        marketplace_details: Optional[list[MarketplaceDetails]]
        name: str
        owner_email: Optional[str]
        partner_resource_id: str
        product: Optional[Union[str, Product]]
        status: Optional[Union[str, WorkspaceLifecycleStatus]]

        @overload
        def __init__(
                self, 
                *, 
                arm_resource_id: Optional[str] = ..., 
                is_default: Optional[bool] = ..., 
                is_managed_by_liftr: bool, 
                marketplace_details: Optional[list[MarketplaceDetails]] = ..., 
                name: str, 
                owner_email: Optional[str] = ..., 
                partner_resource_id: str, 
                product: Optional[Union[str, Product]] = ..., 
                status: Optional[Union[str, WorkspaceLifecycleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.koreaiartemis.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.koreaiartemis.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.ListWorkspacesResponse(_Model):
        value: list[DiscoveredWorkspace]

        @overload
        def __init__(
                self, 
                *, 
                value: list[DiscoveredWorkspace]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.MarketplaceDetails(_Model):
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


    class azure.mgmt.koreaiartemis.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.koreaiartemis.models.OfferDetails(_Model):
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


    class azure.mgmt.koreaiartemis.models.Operation(_Model):
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


    class azure.mgmt.koreaiartemis.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.koreaiartemis.models.OrganizationPartnerProperties(_Model):
        billing_email: str
        default_workspace: DefaultWorkspaceProperties
        organization_name: str
        owner_email: str
        partner_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_email: str, 
                default_workspace: DefaultWorkspaceProperties, 
                organization_name: str, 
                owner_email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.OrganizationPartnerPropertiesUpdate(_Model):
        billing_email: Optional[str]
        organization_name: Optional[str]
        owner_email: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                billing_email: Optional[str] = ..., 
                organization_name: Optional[str] = ..., 
                owner_email: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.OrganizationProperties(_Model):
        company_details: Optional[CompanyDetails]
        default_workspace_id: Optional[str]
        partner_properties: OrganizationPartnerProperties
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        single_sign_on: Optional[SingleSignOnProperties]
        user: UserDetails
        workspace_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                company_details: Optional[CompanyDetails] = ..., 
                partner_properties: OrganizationPartnerProperties, 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.OrganizationPropertiesUpdate(_Model):
        company_details: Optional[CompanyDetails]
        partner_properties: Optional[OrganizationPartnerPropertiesUpdate]
        user: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                company_details: Optional[CompanyDetails] = ..., 
                partner_properties: Optional[OrganizationPartnerPropertiesUpdate] = ..., 
                user: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.OrganizationResource(TrackedResource):
        id: str
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
                location: str, 
                properties: Optional[OrganizationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.OrganizationResourceUpdate(_Model):
        properties: Optional[OrganizationPropertiesUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OrganizationPropertiesUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.koreaiartemis.models.Product(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AIFORSERVICE = "aiforservice"
        AIFORWORK = "aiforwork"


    class azure.mgmt.koreaiartemis.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.koreaiartemis.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.koreaiartemis.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.koreaiartemis.models.SaaSResourceDetailsResponse(ProxyResource):
        id: str
        name: str
        saas_id: Optional[str]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                saas_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.SingleSignOnProperties(_Model):
        aad_domains: Optional[list[str]]
        enterprise_app_id: Optional[str]
        state: Optional[Union[str, SingleSignOnStates]]
        type: Union[str, SingleSignOnType]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_domains: Optional[list[str]] = ..., 
                enterprise_app_id: Optional[str] = ..., 
                state: Optional[Union[str, SingleSignOnStates]] = ..., 
                type: Union[str, SingleSignOnType], 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        INITIAL = "Initial"


    class azure.mgmt.koreaiartemis.models.SingleSignOnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN_ID = "OpenId"
        SAML = "Saml"


    class azure.mgmt.koreaiartemis.models.SystemData(_Model):
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


    class azure.mgmt.koreaiartemis.models.TrackedResource(Resource):
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


    class azure.mgmt.koreaiartemis.models.UserDetails(_Model):
        address: Optional[str]
        alternate_email: Optional[str]
        email_address: Optional[str]
        first_name: Optional[str]
        last_name: Optional[str]
        phone_number: Optional[str]
        upn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                alternate_email: Optional[str] = ..., 
                email_address: Optional[str] = ..., 
                first_name: Optional[str] = ..., 
                last_name: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                upn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceDetail(_Model):
        azure_resource_id: str
        created_at: datetime
        id: str
        organization_id: str
        partner_properties: WorkspaceDetailPartnerProperties
        projects: list[WorkspaceProject]
        status: Union[str, WorkspaceLifecycleStatus]
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_id: str, 
                created_at: datetime, 
                id: str, 
                organization_id: str, 
                partner_properties: WorkspaceDetailPartnerProperties, 
                projects: list[WorkspaceProject], 
                status: Union[str, WorkspaceLifecycleStatus], 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceDetailPartnerProperties(_Model):
        default: bool
        marketplace_details: list[WorkspaceMarketplaceDetails]
        name: str
        owner_email: str
        retention_days: int

        @overload
        def __init__(
                self, 
                *, 
                default: bool, 
                marketplace_details: list[WorkspaceMarketplaceDetails], 
                name: str, 
                owner_email: str, 
                retention_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceLifecycleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ARCHIVED = "archived"
        SUSPENDED = "suspended"


    class azure.mgmt.koreaiartemis.models.WorkspaceLinkedSaaSItem(_Model):
        is_hidden_saa_s: Optional[bool]
        saa_s_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                is_hidden_saa_s: Optional[bool] = ..., 
                saa_s_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceLinkedSaaSListResponse(_Model):
        value: list[WorkspaceLinkedSaaSItem]

        @overload
        def __init__(
                self, 
                *, 
                value: list[WorkspaceLinkedSaaSItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceMarketplaceDetails(_Model):
        mp_id: str
        offer_id: str
        plan_id: str
        plan_name: Optional[str]
        publisher_id: Optional[str]
        resource_id: str
        status: Optional[Union[str, WorkspaceMarketplaceStatus]]
        term_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mp_id: str, 
                offer_id: str, 
                plan_id: str, 
                plan_name: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                resource_id: str, 
                status: Optional[Union[str, WorkspaceMarketplaceStatus]] = ..., 
                term_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceMarketplaceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.koreaiartemis.models.WorkspacePartnerProperties(_Model):
        name: str
        owner_email: Optional[str]
        partner_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                owner_email: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceProject(_Model):
        agent_count: int
        created_at: datetime
        created_by: str
        description: Optional[str]
        id: str
        name: str
        status: Union[str, WorkspaceProjectStatus]
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                agent_count: int, 
                created_at: datetime, 
                created_by: str, 
                description: Optional[str] = ..., 
                id: str, 
                name: str, 
                status: Union[str, WorkspaceProjectStatus], 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceProjectStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        ARCHIVED = "archived"
        DEPLOYED = "deployed"
        IN_DEVELOPMENT = "in-development"


    class azure.mgmt.koreaiartemis.models.WorkspaceProperties(_Model):
        is_default: Optional[bool]
        marketplace_details: list[MarketplaceDetails]
        partner_properties: WorkspacePartnerProperties
        product: Optional[Union[str, Product]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        status: Optional[Union[str, WorkspaceLifecycleStatus]]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_details: list[MarketplaceDetails], 
                partner_properties: WorkspacePartnerProperties, 
                product: Optional[Union[str, Product]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceResource(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkspaceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkspaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.koreaiartemis.models.WorkspaceSaaSData(_Model):
        saa_s_resource_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.koreaiartemis.operations

    class azure.mgmt.koreaiartemis.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.koreaiartemis.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create(
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

        @distributed_trace
        def list_workspaces(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ListWorkspacesResponse: ...


    class azure.mgmt.koreaiartemis.operations.SaaSOperationGroupOperations:

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
                body: ActivateSaaSParameterRequest, 
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


    class azure.mgmt.koreaiartemis.operations.WorkspacesOperations:

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
                workspace_name: str, 
                resource: WorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                resource: WorkspaceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkspaceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: WorkspaceSaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: WorkspaceSaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceResource: ...

        @distributed_trace
        def get_details(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceDetail: ...

        @distributed_trace
        def list_by_organization(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkspaceResource]: ...

        @distributed_trace
        def list_linked_saa_s(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> WorkspaceLinkedSaaSListResponse: ...


namespace azure.mgmt.koreaiartemis.types

    class azure.mgmt.koreaiartemis.types.ActivateSaaSParameterRequest(TypedDict, total=False):
        key "publisherId": Required[str]
        key "saasGuid": Required[str]
        publisherId: str
        saasGuid: str


    class azure.mgmt.koreaiartemis.types.CompanyDetails(TypedDict, total=False):
        key "businessType": str
        key "companyName": str
        key "country": str
        key "domain": str
        key "numberOfEmployees": int
        key "officeAddress": str
        businessType: str
        companyName: str
        country: str
        domain: str
        numberOfEmployees: int
        officeAddress: str


    class azure.mgmt.koreaiartemis.types.DefaultWorkspaceProperties(TypedDict, total=False):
        key "marketplaceDetails": Required[list[MarketplaceDetails]]
        key "name": Required[str]
        key "product": Union[str, Product]
        marketplaceDetails: list[MarketplaceDetails]
        name: str
        product: Union[str, Product]


    class azure.mgmt.koreaiartemis.types.MarketplaceDetails(TypedDict, total=False):
        key "offerDetails": Required[OfferDetails]
        key "saasResourceId": str
        key "subscriptionId": str
        key "subscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        offerDetails: OfferDetails
        saasResourceId: str
        subscriptionId: str
        subscriptionStatus: Union[str, MarketplaceSubscriptionStatus]


    class azure.mgmt.koreaiartemis.types.OfferDetails(TypedDict, total=False):
        key "offerId": Required[str]
        key "planId": str
        key "planName": str
        key "publisherId": Required[str]
        key "termId": str
        key "termUnit": str
        offerId: str
        planId: str
        planName: str
        publisherId: str
        termId: str
        termUnit: str


    class azure.mgmt.koreaiartemis.types.OrganizationPartnerProperties(TypedDict, total=False):
        key "billingEmail": Required[str]
        key "defaultWorkspace": Required[DefaultWorkspaceProperties]
        key "organizationName": Required[str]
        key "ownerEmail": Required[str]
        key "partnerResourceId": str
        billingEmail: str
        defaultWorkspace: DefaultWorkspaceProperties
        organizationName: str
        ownerEmail: str
        partnerResourceId: str


    class azure.mgmt.koreaiartemis.types.OrganizationPartnerPropertiesUpdate(TypedDict, total=False):
        key "billingEmail": str
        key "organizationName": str
        key "ownerEmail": str
        billingEmail: str
        organizationName: str
        ownerEmail: str


    class azure.mgmt.koreaiartemis.types.OrganizationProperties(TypedDict, total=False):
        key "companyDetails": ForwardRef('CompanyDetails', module='types')
        key "defaultWorkspaceId": str
        key "partnerProperties": Required[OrganizationPartnerProperties]
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "singleSignOn": ForwardRef('SingleSignOnProperties', module='types')
        key "user": Required[UserDetails]
        key "workspaceCount": int
        companyDetails: CompanyDetails
        defaultWorkspaceId: str
        partnerProperties: OrganizationPartnerProperties
        provisioningState: Union[str, ResourceProvisioningState]
        singleSignOn: SingleSignOnProperties
        user: UserDetails
        workspaceCount: int


    class azure.mgmt.koreaiartemis.types.OrganizationPropertiesUpdate(TypedDict, total=False):
        key "companyDetails": ForwardRef('CompanyDetails', module='types')
        key "partnerProperties": ForwardRef('OrganizationPartnerPropertiesUpdate', module='types')
        key "user": ForwardRef('UserDetails', module='types')
        companyDetails: CompanyDetails
        partnerProperties: OrganizationPartnerPropertiesUpdate
        user: UserDetails


    class azure.mgmt.koreaiartemis.types.OrganizationResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('OrganizationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: OrganizationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.koreaiartemis.types.OrganizationResourceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('OrganizationPropertiesUpdate', module='types')
        properties: OrganizationPropertiesUpdate
        tags: dict[str, str]


    class azure.mgmt.koreaiartemis.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.koreaiartemis.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.koreaiartemis.types.SingleSignOnProperties(TypedDict, total=False):
        key "enterpriseAppId": str
        key "state": Union[str, SingleSignOnStates]
        key "type": Required[Union[str, SingleSignOnType]]
        key "url": str
        aadDomains: list[str]
        enterpriseAppId: str
        state: Union[str, SingleSignOnStates]
        type: Union[str, SingleSignOnType]
        url: str


    class azure.mgmt.koreaiartemis.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.koreaiartemis.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.koreaiartemis.types.UserDetails(TypedDict, total=False):
        key "address": str
        key "alternateEmail": str
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        key "upn": str
        address: str
        alternateEmail: str
        emailAddress: str
        firstName: str
        lastName: str
        phoneNumber: str
        upn: str


    class azure.mgmt.koreaiartemis.types.WorkspacePartnerProperties(TypedDict, total=False):
        key "name": Required[str]
        key "ownerEmail": str
        key "partnerResourceId": str
        name: str
        ownerEmail: str
        partnerResourceId: str


    class azure.mgmt.koreaiartemis.types.WorkspaceProperties(TypedDict, total=False):
        key "isDefault": bool
        key "marketplaceDetails": Required[list[MarketplaceDetails]]
        key "partnerProperties": Required[WorkspacePartnerProperties]
        key "product": Union[str, Product]
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "status": Union[str, WorkspaceLifecycleStatus]
        isDefault: bool
        marketplaceDetails: list[MarketplaceDetails]
        partnerProperties: WorkspacePartnerProperties
        product: Union[str, Product]
        provisioningState: Union[str, ResourceProvisioningState]
        status: Union[str, WorkspaceLifecycleStatus]


    class azure.mgmt.koreaiartemis.types.WorkspaceResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: WorkspaceProperties
        systemData: SystemData
        type: str


    class azure.mgmt.koreaiartemis.types.WorkspaceSaaSData(TypedDict, total=False):
        key "saaSResourceIds": Required[list[str]]
        saaSResourceIds: list[str]


```