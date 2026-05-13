```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.lambdatesthyperexecute

    class azure.mgmt.lambdatesthyperexecute.LambdaTestHyperExecuteMgmtClient: implements ContextManager 
        operations: Operations
        organizations: OrganizationsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
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


namespace azure.mgmt.lambdatesthyperexecute.aio

    class azure.mgmt.lambdatesthyperexecute.aio.LambdaTestHyperExecuteMgmtClient: implements AsyncContextManager 
        operations: Operations
        organizations: OrganizationsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
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


namespace azure.mgmt.lambdatesthyperexecute.aio.operations

    class azure.mgmt.lambdatesthyperexecute.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.lambdatesthyperexecute.aio.operations.OrganizationsOperations:

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
                resource: JSON, 
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

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[OrganizationResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...


namespace azure.mgmt.lambdatesthyperexecute.models

    class azure.mgmt.lambdatesthyperexecute.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.lambdatesthyperexecute.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.lambdatesthyperexecute.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.lambdatesthyperexecute.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.lambdatesthyperexecute.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.lambdatesthyperexecute.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.lambdatesthyperexecute.models.MarketplaceDetails(_Model):
        offer_details: OfferDetails
        subscription_id: Optional[str]
        subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                offer_details: OfferDetails, 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.lambdatesthyperexecute.models.OfferDetails(_Model):
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


    class azure.mgmt.lambdatesthyperexecute.models.Operation(_Model):
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


    class azure.mgmt.lambdatesthyperexecute.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.lambdatesthyperexecute.models.OrganizationProperties(_Model):
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


    class azure.mgmt.lambdatesthyperexecute.models.OrganizationResource(TrackedResource):
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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.OrganizationResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.lambdatesthyperexecute.models.PartnerProperties(_Model):
        licenses_subscribed: int

        @overload
        def __init__(
                self, 
                *, 
                licenses_subscribed: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.lambdatesthyperexecute.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.lambdatesthyperexecute.models.SingleSignOnPropertiesV2(_Model):
        aad_domains: Optional[List[str]]
        enterprise_app_id: Optional[str]
        state: Optional[Union[str, SingleSignOnStates]]
        type: Union[str, SingleSignOnType]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_domains: Optional[List[str]] = ..., 
                enterprise_app_id: Optional[str] = ..., 
                state: Optional[Union[str, SingleSignOnStates]] = ..., 
                type: Union[str, SingleSignOnType], 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.lambdatesthyperexecute.models.SingleSignOnStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"
        INITIAL = "Initial"


    class azure.mgmt.lambdatesthyperexecute.models.SingleSignOnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPEN_ID = "OpenId"
        SAML = "Saml"


    class azure.mgmt.lambdatesthyperexecute.models.SystemData(_Model):
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


    class azure.mgmt.lambdatesthyperexecute.models.TrackedResource(Resource):
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


    class azure.mgmt.lambdatesthyperexecute.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.lambdatesthyperexecute.models.UserDetails(_Model):
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


namespace azure.mgmt.lambdatesthyperexecute.operations

    class azure.mgmt.lambdatesthyperexecute.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.lambdatesthyperexecute.operations.OrganizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                resource: JSON, 
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

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[OrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[OrganizationResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: OrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organizationname: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OrganizationResource: ...


```