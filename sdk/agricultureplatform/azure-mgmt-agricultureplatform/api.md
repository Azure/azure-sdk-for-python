```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


namespace azure.mgmt.agricultureplatform

    class azure.mgmt.agricultureplatform.AgriculturePlatformMgmtClient: implements ContextManager 
        agri_service: AgriServiceOperations
        operations: Operations

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


namespace azure.mgmt.agricultureplatform.aio

    class azure.mgmt.agricultureplatform.aio.AgriculturePlatformMgmtClient: implements AsyncContextManager 
        agri_service: AgriServiceOperations
        operations: Operations

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


namespace azure.mgmt.agricultureplatform.aio.operations

    class azure.mgmt.agricultureplatform.aio.operations.AgriServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: AgriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: AgriServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgriServiceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> AgriServiceResource: ...

        @distributed_trace_async
        async def list_available_solutions(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> AvailableAgriSolutionListResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgriServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AgriServiceResource]: ...


    class azure.mgmt.agricultureplatform.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.agricultureplatform.models

    class azure.mgmt.agricultureplatform.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.agricultureplatform.models.AgriServiceConfig(_Model):
        app_service_resource_id: Optional[str]
        cosmos_db_resource_id: Optional[str]
        instance_uri: Optional[str]
        key_vault_resource_id: Optional[str]
        redis_cache_resource_id: Optional[str]
        storage_account_resource_id: Optional[str]
        version: Optional[str]


    class azure.mgmt.agricultureplatform.models.AgriServiceResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AgriServiceResourceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AgriServiceResourceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.AgriServiceResourceProperties(_Model):
        config: Optional[AgriServiceConfig]
        data_connector_credentials: Optional[list[DataConnectorCredentialMap]]
        installed_solutions: Optional[list[InstalledSolutionMap]]
        managed_on_behalf_of_configuration: Optional[ManagedOnBehalfOfConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[AgriServiceConfig] = ..., 
                data_connector_credentials: Optional[list[DataConnectorCredentialMap]] = ..., 
                installed_solutions: Optional[list[InstalledSolutionMap]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.AgriServiceResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AgriServiceResourceUpdateProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AgriServiceResourceUpdateProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.AgriServiceResourceUpdateProperties(_Model):
        config: Optional[AgriServiceConfig]
        data_connector_credentials: Optional[list[DataConnectorCredentialMap]]
        installed_solutions: Optional[list[InstalledSolutionMap]]

        @overload
        def __init__(
                self, 
                *, 
                config: Optional[AgriServiceConfig] = ..., 
                data_connector_credentials: Optional[list[DataConnectorCredentialMap]] = ..., 
                installed_solutions: Optional[list[InstalledSolutionMap]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.AuthCredentialsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY_AUTH_CREDENTIALS = "ApiKeyAuthCredentials"
        O_AUTH_CLIENT_CREDENTIALS = "OAuthClientCredentials"


    class azure.mgmt.agricultureplatform.models.AvailableAgriSolutionListResult(_Model):
        solutions: list[DataManagerForAgricultureSolution]

        @overload
        def __init__(
                self, 
                *, 
                solutions: list[DataManagerForAgricultureSolution]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.agricultureplatform.models.DataConnectorCredentialMap(_Model):
        key: str
        value: DataConnectorCredentials

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: DataConnectorCredentials
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.DataConnectorCredentials(_Model):
        client_id: Optional[str]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]
        kind: Optional[Union[str, AuthCredentialsKind]]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                kind: Optional[Union[str, AuthCredentialsKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.DataManagerForAgricultureSolution(_Model):
        access_azure_data_manager_for_agriculture_application_id: str
        access_azure_data_manager_for_agriculture_application_name: str
        data_access_scopes: list[str]
        is_validate_input: bool
        market_place_offer_details: MarketPlaceOfferDetails
        partner_id: str
        partner_tenant_id: str
        saas_application_id: str
        solution_id: str

        @overload
        def __init__(
                self, 
                *, 
                access_azure_data_manager_for_agriculture_application_id: str, 
                access_azure_data_manager_for_agriculture_application_name: str, 
                data_access_scopes: list[str], 
                is_validate_input: bool, 
                market_place_offer_details: MarketPlaceOfferDetails, 
                partner_id: str, 
                partner_tenant_id: str, 
                saas_application_id: str, 
                solution_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.agricultureplatform.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.agricultureplatform.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.InstalledSolutionMap(_Model):
        key: str
        value: Solution

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: Solution
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.ManagedOnBehalfOfConfiguration(_Model):
        mobo_broker_resources: list[MoboBrokerResource]


    class azure.mgmt.agricultureplatform.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.agricultureplatform.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.agricultureplatform.models.MarketPlaceOfferDetails(_Model):
        publisher_id: str
        saas_offer_id: str

        @overload
        def __init__(
                self, 
                *, 
                publisher_id: str, 
                saas_offer_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.MoboBrokerResource(_Model):
        id: str


    class azure.mgmt.agricultureplatform.models.Operation(_Model):
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


    class azure.mgmt.agricultureplatform.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.agricultureplatform.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.agricultureplatform.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.agricultureplatform.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.agricultureplatform.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.agricultureplatform.models.Solution(_Model):
        application_name: Optional[str]
        market_place_publisher_id: Optional[str]
        partner_id: Optional[str]
        plan_id: Optional[str]
        saas_subscription_id: Optional[str]
        saas_subscription_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_name: Optional[str] = ..., 
                market_place_publisher_id: Optional[str] = ..., 
                partner_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                saas_subscription_id: Optional[str] = ..., 
                saas_subscription_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.agricultureplatform.models.SystemData(_Model):
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


    class azure.mgmt.agricultureplatform.models.TrackedResource(Resource):
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


    class azure.mgmt.agricultureplatform.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.agricultureplatform.operations

    class azure.mgmt.agricultureplatform.operations.AgriServiceOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: AgriServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: AgriServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgriServiceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> AgriServiceResource: ...

        @distributed_trace
        def list_available_solutions(
                self, 
                resource_group_name: str, 
                agri_service_resource_name: str, 
                **kwargs: Any
            ) -> AvailableAgriSolutionListResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgriServiceResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AgriServiceResource]: ...


    class azure.mgmt.agricultureplatform.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```