```py
namespace azure.mgmt.napsteromniagentapi

    class azure.mgmt.napsteromniagentapi.NapsterOmniAgentApiMgmtClient: implements ContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations

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


namespace azure.mgmt.napsteromniagentapi.aio

    class azure.mgmt.napsteromniagentapi.aio.NapsterOmniAgentApiMgmtClient: implements AsyncContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        saa_soperation_group: SaaSOperationGroupOperations

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


namespace azure.mgmt.napsteromniagentapi.aio.operations

    class azure.mgmt.napsteromniagentapi.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.napsteromniagentapi.aio.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OrganizationResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace_async
        async def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[OrganizationResource]: ...


    class azure.mgmt.napsteromniagentapi.aio.operations.SaaSOperationGroupOperations:

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


namespace azure.mgmt.napsteromniagentapi.models

    class azure.mgmt.napsteromniagentapi.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.napsteromniagentapi.models.ActivateSaaSParameterRequest(_Model):
        publisher_id: Optional[str]
        saas_guid: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: Optional[str] = ..., 
                saas_guid: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.napsteromniagentapi.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.napsteromniagentapi.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.napsteromniagentapi.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.napsteromniagentapi.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.napsteromniagentapi.models.LatestLinkedSaaSResponse(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.napsteromniagentapi.models.MarketplaceDetails(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.napsteromniagentapi.models.OfferDetails(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.Operation(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.napsteromniagentapi.models.OrganizationProperties(_Model):
        marketplace: MarketplaceDetails
        partner_properties: PartnerProperties
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        single_sign_on_properties: Optional[SingleSignOnPropertiesV2]
        user: UserDetails

        @overload
        def __init__(
                self, 
                *, 
                marketplace: MarketplaceDetails, 
                partner_properties: PartnerProperties, 
                single_sign_on_properties: Optional[SingleSignOnPropertiesV2] = ..., 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.napsteromniagentapi.models.OrganizationResource(TrackedResource):
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


    class azure.mgmt.napsteromniagentapi.models.OrganizationResourceUpdate(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.napsteromniagentapi.models.PartnerProperties(_Model):
        application: str

        @overload
        def __init__(
                self, 
                *, 
                application: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.napsteromniagentapi.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.napsteromniagentapi.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.napsteromniagentapi.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.napsteromniagentapi.models.SaaSData(_Model):
        saa_s_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                saa_s_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.napsteromniagentapi.models.SaaSResourceDetailsResponse(ProxyResource):
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


    class azure.mgmt.napsteromniagentapi.models.SingleSignOnPropertiesV2(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        INITIAL = "Initial"


    class azure.mgmt.napsteromniagentapi.models.SingleSignOnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN_ID = "OpenId"
        SAML = "Saml"


    class azure.mgmt.napsteromniagentapi.models.SystemData(_Model):
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


    class azure.mgmt.napsteromniagentapi.models.TrackedResource(Resource):
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


    class azure.mgmt.napsteromniagentapi.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.napsteromniagentapi.models.UserDetails(_Model):
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


namespace azure.mgmt.napsteromniagentapi.operations

    class azure.mgmt.napsteromniagentapi.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.napsteromniagentapi.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: OrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: SaaSData, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_link_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OrganizationResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def latest_linked_saa_s(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> LatestLinkedSaaSResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[OrganizationResource]: ...


    class azure.mgmt.napsteromniagentapi.operations.SaaSOperationGroupOperations:

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


namespace azure.mgmt.napsteromniagentapi.types

    class azure.mgmt.napsteromniagentapi.types.ActivateSaaSParameterRequest(TypedDict, total=False):
        key "publisherId": str
        key "saasGuid": Required[str]
        publisherId: str
        saasGuid: str


    class azure.mgmt.napsteromniagentapi.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.napsteromniagentapi.types.MarketplaceDetails(TypedDict, total=False):
        key "offerDetails": Required[OfferDetails]
        key "saasResourceId": str
        key "subscriptionId": str
        key "subscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        offerDetails: OfferDetails
        saasResourceId: str
        subscriptionId: str
        subscriptionStatus: Union[str, MarketplaceSubscriptionStatus]


    class azure.mgmt.napsteromniagentapi.types.OfferDetails(TypedDict, total=False):
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


    class azure.mgmt.napsteromniagentapi.types.OrganizationProperties(TypedDict, total=False):
        key "marketplace": Required[MarketplaceDetails]
        key "partnerProperties": Required[PartnerProperties]
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "singleSignOnProperties": ForwardRef('SingleSignOnPropertiesV2', module='types')
        key "user": Required[UserDetails]
        marketplace: MarketplaceDetails
        partnerProperties: PartnerProperties
        provisioningState: Union[str, ResourceProvisioningState]
        singleSignOnProperties: SingleSignOnPropertiesV2
        user: UserDetails


    class azure.mgmt.napsteromniagentapi.types.OrganizationResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('OrganizationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: OrganizationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.napsteromniagentapi.types.OrganizationResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.napsteromniagentapi.types.PartnerProperties(TypedDict, total=False):
        key "application": Required[str]
        application: str


    class azure.mgmt.napsteromniagentapi.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.napsteromniagentapi.types.SaaSData(TypedDict, total=False):
        key "saaSResourceId": str
        saaSResourceId: str


    class azure.mgmt.napsteromniagentapi.types.SingleSignOnPropertiesV2(TypedDict, total=False):
        key "enterpriseAppId": str
        key "state": Union[str, SingleSignOnStates]
        key "type": Required[Union[str, SingleSignOnType]]
        key "url": str
        aadDomains: list[str]
        enterpriseAppId: str
        state: Union[str, SingleSignOnStates]
        type: Union[str, SingleSignOnType]
        url: str


    class azure.mgmt.napsteromniagentapi.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.napsteromniagentapi.types.TrackedResource(Resource):
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


    class azure.mgmt.napsteromniagentapi.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.napsteromniagentapi.types.UserDetails(TypedDict, total=False):
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        key "upn": str
        emailAddress: str
        firstName: str
        lastName: str
        phoneNumber: str
        upn: str


```