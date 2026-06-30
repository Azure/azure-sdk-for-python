```py
namespace azure.mgmt.informaticadatamanagement

    class azure.mgmt.informaticadatamanagement.InformaticaDataMgmtClient: implements ContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        serverless_runtimes: ServerlessRuntimesOperations

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


namespace azure.mgmt.informaticadatamanagement.aio

    class azure.mgmt.informaticadatamanagement.aio.InformaticaDataMgmtClient: implements AsyncContextManager 
        operations: Operations
        organizations: OrganizationsOperations
        serverless_runtimes: ServerlessRuntimesOperations

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


namespace azure.mgmt.informaticadatamanagement.aio.operations

    class azure.mgmt.informaticadatamanagement.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.informaticadatamanagement.aio.operations.OrganizationsOperations:

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
                resource: InformaticaOrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaOrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: InformaticaOrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaOrganizationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaOrganizationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @distributed_trace_async
        async def get_all_serverless_runtimes(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResourceList: ...

        @distributed_trace_async
        async def get_serverless_metadata(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ServerlessMetadataResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InformaticaOrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[InformaticaOrganizationResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: InformaticaOrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: InformaticaOrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...


    class azure.mgmt.informaticadatamanagement.aio.operations.ServerlessRuntimesOperations:

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
                serverless_runtime_name: str, 
                resource: InformaticaServerlessRuntimeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaServerlessRuntimeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                resource: InformaticaServerlessRuntimeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaServerlessRuntimeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[InformaticaServerlessRuntimeResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def check_dependencies(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> CheckDependenciesResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @distributed_trace
        def list_by_informatica_organization_resource(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[InformaticaServerlessRuntimeResource]: ...

        @distributed_trace_async
        async def serverless_resource_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @distributed_trace_async
        async def start_failed_serverless_runtime(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: InformaticaServerlessRuntimeResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: InformaticaServerlessRuntimeResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...


namespace azure.mgmt.informaticadatamanagement.models

    class azure.mgmt.informaticadatamanagement.models.AdvancedCustomProperties(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.ApplicationConfigs(_Model):
        customized: str
        default_value: str
        name: str
        platform: str
        type: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                customized: str, 
                default_value: str, 
                name: str, 
                platform: str, 
                type: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDI = "CDI"
        CDIE = "CDIE"


    class azure.mgmt.informaticadatamanagement.models.ApplicationTypeMetadata(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.CdiConfigProps(_Model):
        application_configs: list[ApplicationConfigs]
        engine_name: str
        engine_version: str

        @overload
        def __init__(
                self, 
                *, 
                application_configs: list[ApplicationConfigs], 
                engine_name: str, 
                engine_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.CheckDependenciesResponse(_Model):
        count: int
        id: str
        references: list[ServerlessRuntimeDependency]

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                id: str, 
                references: list[ServerlessRuntimeDependency]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.CompanyDetails(_Model):
        business: Optional[str]
        company_name: Optional[str]
        country: Optional[str]
        domain: Optional[str]
        number_of_employees: Optional[int]
        office_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                business: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                number_of_employees: Optional[int] = ..., 
                office_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.CompanyDetailsUpdate(_Model):
        business: Optional[str]
        company_name: Optional[str]
        country: Optional[str]
        domain: Optional[str]
        number_of_employees: Optional[int]
        office_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                business: Optional[str] = ..., 
                company_name: Optional[str] = ..., 
                country: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                number_of_employees: Optional[int] = ..., 
                office_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ComputeUnitsMetadata(_Model):
        name: Optional[str]
        value: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.informaticadatamanagement.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.informaticadatamanagement.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.informaticadatamanagement.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InfaRuntimeResourceFetchMetaData(_Model):
        created_by: str
        created_time: str
        description: Optional[str]
        id: str
        name: str
        serverless_config_properties: InfaServerlessFetchConfigProperties
        status: str
        status_localized: str
        status_message: str
        type: Union[str, RuntimeType]
        updated_by: str
        updated_time: str

        @overload
        def __init__(
                self, 
                *, 
                created_by: str, 
                created_time: str, 
                description: Optional[str] = ..., 
                id: str, 
                name: str, 
                serverless_config_properties: InfaServerlessFetchConfigProperties, 
                status: str, 
                status_localized: str, 
                status_message: str, 
                type: Union[str, RuntimeType], 
                updated_by: str, 
                updated_time: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InfaServerlessFetchConfigProperties(_Model):
        advanced_custom_properties: Optional[str]
        application_type: Optional[str]
        compute_units: Optional[str]
        execution_timeout: Optional[str]
        platform: Optional[str]
        region: Optional[str]
        resource_group_name: Optional[str]
        serverless_arm_resource_id: Optional[str]
        serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]]
        subnet: Optional[str]
        subscription_id: Optional[str]
        supplementary_file_location: Optional[str]
        tags: Optional[str]
        tenant_id: Optional[str]
        vnet: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                advanced_custom_properties: Optional[str] = ..., 
                application_type: Optional[str] = ..., 
                compute_units: Optional[str] = ..., 
                execution_timeout: Optional[str] = ..., 
                platform: Optional[str] = ..., 
                region: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                serverless_arm_resource_id: Optional[str] = ..., 
                serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]] = ..., 
                subnet: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                supplementary_file_location: Optional[str] = ..., 
                tags: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                vnet: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaOrganizationResource(TrackedResource):
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


    class azure.mgmt.informaticadatamanagement.models.InformaticaOrganizationResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[OrganizationPropertiesCustomUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[OrganizationPropertiesCustomUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaProperties(_Model):
        informatica_region: Optional[str]
        organization_id: Optional[str]
        organization_name: Optional[str]
        single_sign_on_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                informatica_region: Optional[str] = ..., 
                organization_id: Optional[str] = ..., 
                organization_name: Optional[str] = ..., 
                single_sign_on_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaServerlessRuntimeProperties(_Model):
        advanced_custom_properties: Optional[list[AdvancedCustomProperties]]
        application_type: Optional[Union[str, ApplicationType]]
        compute_units: Optional[str]
        description: Optional[str]
        execution_timeout: Optional[str]
        platform: Optional[Union[str, PlatformType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serverless_account_location: str
        serverless_runtime_config: Optional[ServerlessRuntimeConfigProperties]
        serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]]
        serverless_runtime_network_profile: Optional[ServerlessRuntimeNetworkProfile]
        serverless_runtime_tags: Optional[list[ServerlessRuntimeTag]]
        serverless_runtime_user_context_properties: Optional[ServerlessRuntimeUserContextProperties]
        supplementary_file_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                advanced_custom_properties: Optional[list[AdvancedCustomProperties]] = ..., 
                application_type: Optional[Union[str, ApplicationType]] = ..., 
                compute_units: Optional[str] = ..., 
                description: Optional[str] = ..., 
                execution_timeout: Optional[str] = ..., 
                platform: Optional[Union[str, PlatformType]] = ..., 
                serverless_account_location: str, 
                serverless_runtime_config: Optional[ServerlessRuntimeConfigProperties] = ..., 
                serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]] = ..., 
                serverless_runtime_network_profile: Optional[ServerlessRuntimeNetworkProfile] = ..., 
                serverless_runtime_tags: Optional[list[ServerlessRuntimeTag]] = ..., 
                serverless_runtime_user_context_properties: Optional[ServerlessRuntimeUserContextProperties] = ..., 
                supplementary_file_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaServerlessRuntimeResource(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: Optional[InformaticaServerlessRuntimeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[InformaticaServerlessRuntimeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaServerlessRuntimeResourceList(_Model):
        informatica_runtime_resources: list[InfaRuntimeResourceFetchMetaData]

        @overload
        def __init__(
                self, 
                *, 
                informatica_runtime_resources: list[InfaRuntimeResourceFetchMetaData]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.InformaticaServerlessRuntimeResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ServerlessRuntimePropertiesCustomUpdate]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ServerlessRuntimePropertiesCustomUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.LinkOrganization(_Model):
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.informaticadatamanagement.models.MarketplaceDetails(_Model):
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        offer_details: OfferDetails

        @overload
        def __init__(
                self, 
                *, 
                marketplace_subscription_id: Optional[str] = ..., 
                offer_details: OfferDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.MarketplaceDetailsUpdate(_Model):
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        offer_details: Optional[OfferDetailsUpdate]

        @overload
        def __init__(
                self, 
                *, 
                marketplace_subscription_id: Optional[str] = ..., 
                offer_details: Optional[OfferDetailsUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBE = "Subscribe"
        SUSPEND = "Suspend"
        UNSUBSCRIBE = "Unsubscribe"


    class azure.mgmt.informaticadatamanagement.models.NetworkInterfaceConfiguration(_Model):
        subnet_id: str
        vnet_id: str
        vnet_resource_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: str, 
                vnet_id: str, 
                vnet_resource_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.NetworkInterfaceConfigurationUpdate(_Model):
        subnet_id: Optional[str]
        vnet_id: Optional[str]
        vnet_resource_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: Optional[str] = ..., 
                vnet_id: Optional[str] = ..., 
                vnet_resource_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.OfferDetails(_Model):
        offer_id: str
        plan_id: str
        plan_name: str
        publisher_id: str
        term_id: str
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: str, 
                plan_id: str, 
                plan_name: str, 
                publisher_id: str, 
                term_id: str, 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.OfferDetailsUpdate(_Model):
        offer_id: Optional[str]
        plan_id: Optional[str]
        plan_name: Optional[str]
        publisher_id: Optional[str]
        term_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                plan_name: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                term_id: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.OrganizationProperties(_Model):
        company_details: Optional[CompanyDetails]
        informatica_properties: Optional[InformaticaProperties]
        link_organization: Optional[LinkOrganization]
        marketplace_details: Optional[MarketplaceDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        user_details: Optional[UserDetails]

        @overload
        def __init__(
                self, 
                *, 
                company_details: Optional[CompanyDetails] = ..., 
                informatica_properties: Optional[InformaticaProperties] = ..., 
                link_organization: Optional[LinkOrganization] = ..., 
                marketplace_details: Optional[MarketplaceDetails] = ..., 
                user_details: Optional[UserDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.OrganizationPropertiesCustomUpdate(_Model):
        company_details: Optional[CompanyDetailsUpdate]
        existing_resource_id: Optional[str]
        informatica_organization_properties: Optional[InformaticaOrganizationResourceUpdate]
        marketplace_details: Optional[MarketplaceDetailsUpdate]
        user_details: Optional[UserDetailsUpdate]

        @overload
        def __init__(
                self, 
                *, 
                company_details: Optional[CompanyDetailsUpdate] = ..., 
                existing_resource_id: Optional[str] = ..., 
                informatica_organization_properties: Optional[InformaticaOrganizationResourceUpdate] = ..., 
                marketplace_details: Optional[MarketplaceDetailsUpdate] = ..., 
                user_details: Optional[UserDetailsUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.PlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "AZURE"


    class azure.mgmt.informaticadatamanagement.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.informaticadatamanagement.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.informaticadatamanagement.models.RegionsMetadata(_Model):
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.informaticadatamanagement.models.RuntimeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVERLESS = "SERVERLESS"


    class azure.mgmt.informaticadatamanagement.models.ServerlessConfigProperties(_Model):
        application_types: Optional[list[ApplicationTypeMetadata]]
        compute_units: Optional[list[ComputeUnitsMetadata]]
        execution_timeout: Optional[str]
        platform: Optional[Union[str, PlatformType]]
        regions: Optional[list[RegionsMetadata]]

        @overload
        def __init__(
                self, 
                *, 
                application_types: Optional[list[ApplicationTypeMetadata]] = ..., 
                compute_units: Optional[list[ComputeUnitsMetadata]] = ..., 
                execution_timeout: Optional[str] = ..., 
                platform: Optional[Union[str, PlatformType]] = ..., 
                regions: Optional[list[RegionsMetadata]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessMetadataResponse(_Model):
        serverless_config_properties: Optional[ServerlessConfigProperties]
        serverless_runtime_config_properties: Optional[ServerlessRuntimeConfigProperties]
        type: Optional[Union[str, RuntimeType]]

        @overload
        def __init__(
                self, 
                *, 
                serverless_config_properties: Optional[ServerlessConfigProperties] = ..., 
                serverless_runtime_config_properties: Optional[ServerlessRuntimeConfigProperties] = ..., 
                type: Optional[Union[str, RuntimeType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeConfigProperties(_Model):
        cdi_config_props: Optional[list[CdiConfigProps]]
        cdie_config_props: Optional[list[CdiConfigProps]]

        @overload
        def __init__(
                self, 
                *, 
                cdi_config_props: Optional[list[CdiConfigProps]] = ..., 
                cdie_config_props: Optional[list[CdiConfigProps]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeConfigPropertiesUpdate(_Model):
        cdi_config_props: Optional[list[CdiConfigProps]]
        cdie_config_props: Optional[list[CdiConfigProps]]

        @overload
        def __init__(
                self, 
                *, 
                cdi_config_props: Optional[list[CdiConfigProps]] = ..., 
                cdie_config_props: Optional[list[CdiConfigProps]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeDataDisk(_Model):
        mount_options: Optional[str]
        server_host_or_ip_address: Optional[str]
        source_mount: Optional[str]
        target_mount: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mount_options: Optional[str] = ..., 
                server_host_or_ip_address: Optional[str] = ..., 
                source_mount: Optional[str] = ..., 
                target_mount: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeDependency(_Model):
        app_context_id: str
        description: str
        document_type: str
        id: str
        last_updated_time: str
        path: str

        @overload
        def __init__(
                self, 
                *, 
                app_context_id: str, 
                description: str, 
                document_type: str, 
                id: str, 
                last_updated_time: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeNetworkProfile(_Model):
        network_interface_configuration: NetworkInterfaceConfiguration

        @overload
        def __init__(
                self, 
                *, 
                network_interface_configuration: NetworkInterfaceConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeNetworkProfileUpdate(_Model):
        network_interface_configuration: NetworkInterfaceConfigurationUpdate

        @overload
        def __init__(
                self, 
                *, 
                network_interface_configuration: NetworkInterfaceConfigurationUpdate
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimePropertiesCustomUpdate(_Model):
        advanced_custom_properties: Optional[list[AdvancedCustomProperties]]
        application_type: Optional[Union[str, ApplicationType]]
        compute_units: Optional[str]
        description: Optional[str]
        execution_timeout: Optional[str]
        platform: Optional[Union[str, PlatformType]]
        serverless_account_location: Optional[str]
        serverless_runtime_config: Optional[ServerlessRuntimeConfigPropertiesUpdate]
        serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]]
        serverless_runtime_network_profile: Optional[ServerlessRuntimeNetworkProfileUpdate]
        serverless_runtime_tags: Optional[list[ServerlessRuntimeTag]]
        serverless_runtime_user_context_properties: Optional[ServerlessRuntimeUserContextPropertiesUpdate]
        supplementary_file_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                advanced_custom_properties: Optional[list[AdvancedCustomProperties]] = ..., 
                application_type: Optional[Union[str, ApplicationType]] = ..., 
                compute_units: Optional[str] = ..., 
                description: Optional[str] = ..., 
                execution_timeout: Optional[str] = ..., 
                platform: Optional[Union[str, PlatformType]] = ..., 
                serverless_account_location: Optional[str] = ..., 
                serverless_runtime_config: Optional[ServerlessRuntimeConfigPropertiesUpdate] = ..., 
                serverless_runtime_data_disks: Optional[list[ServerlessRuntimeDataDisk]] = ..., 
                serverless_runtime_network_profile: Optional[ServerlessRuntimeNetworkProfileUpdate] = ..., 
                serverless_runtime_tags: Optional[list[ServerlessRuntimeTag]] = ..., 
                serverless_runtime_user_context_properties: Optional[ServerlessRuntimeUserContextPropertiesUpdate] = ..., 
                supplementary_file_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeTag(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeUserContextProperties(_Model):
        user_context_token: str

        @overload
        def __init__(
                self, 
                *, 
                user_context_token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.ServerlessRuntimeUserContextPropertiesUpdate(_Model):
        user_context_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_context_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.informaticadatamanagement.models.SystemData(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.TrackedResource(Resource):
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


    class azure.mgmt.informaticadatamanagement.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.informaticadatamanagement.models.UserDetails(_Model):
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


    class azure.mgmt.informaticadatamanagement.models.UserDetailsUpdate(_Model):
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


namespace azure.mgmt.informaticadatamanagement.operations

    class azure.mgmt.informaticadatamanagement.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...


    class azure.mgmt.informaticadatamanagement.operations.OrganizationsOperations:

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
                resource: InformaticaOrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaOrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: InformaticaOrganizationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaOrganizationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaOrganizationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @distributed_trace
        def get_all_serverless_runtimes(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResourceList: ...

        @distributed_trace
        def get_serverless_metadata(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ServerlessMetadataResponse: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InformaticaOrganizationResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[InformaticaOrganizationResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: InformaticaOrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: InformaticaOrganizationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaOrganizationResource: ...


    class azure.mgmt.informaticadatamanagement.operations.ServerlessRuntimesOperations:

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
                serverless_runtime_name: str, 
                resource: InformaticaServerlessRuntimeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaServerlessRuntimeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                resource: InformaticaServerlessRuntimeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaServerlessRuntimeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[InformaticaServerlessRuntimeResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def check_dependencies(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> CheckDependenciesResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @distributed_trace
        def list_by_informatica_organization_resource(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                **kwargs: Any
            ) -> ItemPaged[InformaticaServerlessRuntimeResource]: ...

        @distributed_trace
        def serverless_resource_by_id(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @distributed_trace
        def start_failed_serverless_runtime(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: InformaticaServerlessRuntimeResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: InformaticaServerlessRuntimeResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                organization_name: str, 
                serverless_runtime_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> InformaticaServerlessRuntimeResource: ...


namespace azure.mgmt.informaticadatamanagement.types

    class azure.mgmt.informaticadatamanagement.types.AdvancedCustomProperties(TypedDict, total=False):
        key "key": str
        key "value": str
        key: str
        value: str


    class azure.mgmt.informaticadatamanagement.types.ApplicationConfigs(TypedDict, total=False):
        key "customized": Required[str]
        key "defaultValue": Required[str]
        key "name": Required[str]
        key "platform": Required[str]
        key "type": Required[str]
        key "value": Required[str]
        customized: str
        default_value: str
        name: str
        platform: str
        type: str
        value: str


    class azure.mgmt.informaticadatamanagement.types.ApplicationTypeMetadata(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.informaticadatamanagement.types.CdiConfigProps(TypedDict, total=False):
        key "applicationConfigs": Required[list[ApplicationConfigs]]
        key "engineName": Required[str]
        key "engineVersion": Required[str]
        application_configs: list[ApplicationConfigs]
        engine_name: str
        engine_version: str


    class azure.mgmt.informaticadatamanagement.types.CheckDependenciesResponse(TypedDict, total=False):
        key "count": Required[int]
        key "id": Required[str]
        key "references": Required[list[ServerlessRuntimeDependency]]
        count: int
        id: str
        references: list[ServerlessRuntimeDependency]


    class azure.mgmt.informaticadatamanagement.types.CompanyDetails(TypedDict, total=False):
        key "business": str
        key "companyName": str
        key "country": str
        key "domain": str
        key "numberOfEmployees": int
        key "officeAddress": str
        business: str
        company_name: str
        country: str
        domain: str
        number_of_employees: int
        office_address: str


    class azure.mgmt.informaticadatamanagement.types.CompanyDetailsUpdate(TypedDict, total=False):
        key "business": str
        key "companyName": str
        key "country": str
        key "domain": str
        key "numberOfEmployees": int
        key "officeAddress": str
        business: str
        company_name: str
        country: str
        domain: str
        number_of_employees: int
        office_address: str


    class azure.mgmt.informaticadatamanagement.types.ComputeUnitsMetadata(TypedDict, total=False):
        key "name": str
        name: str
        value: list[str]


    class azure.mgmt.informaticadatamanagement.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.informaticadatamanagement.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.informaticadatamanagement.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.informaticadatamanagement.types.InfaRuntimeResourceFetchMetaData(TypedDict, total=False):
        key "createdBy": Required[str]
        key "createdTime": Required[str]
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        key "serverlessConfigProperties": Required[InfaServerlessFetchConfigProperties]
        key "status": Required[str]
        key "statusLocalized": Required[str]
        key "statusMessage": Required[str]
        key "type": Required[Union[str, RuntimeType]]
        key "updatedBy": Required[str]
        key "updatedTime": Required[str]
        created_by: str
        created_time: str
        description: str
        id: str
        name: str
        serverless_config_properties: InfaServerlessFetchConfigProperties
        status: str
        status_localized: str
        status_message: str
        type: Union[str, RuntimeType]
        updated_by: str
        updated_time: str


    class azure.mgmt.informaticadatamanagement.types.InfaServerlessFetchConfigProperties(TypedDict, total=False):
        key "advancedCustomProperties": str
        key "applicationType": str
        key "computeUnits": str
        key "executionTimeout": str
        key "platform": str
        key "region": str
        key "resourceGroupName": str
        key "serverlessArmResourceId": str
        key "subnet": str
        key "subscriptionId": str
        key "supplementaryFileLocation": str
        key "tags": str
        key "tenantId": str
        key "vnet": str
        advanced_custom_properties: str
        application_type: str
        compute_units: str
        execution_timeout: str
        platform: str
        region: str
        resource_group_name: str
        serverlessRuntimeDataDisks: list[ServerlessRuntimeDataDisk]
        serverless_arm_resource_id: str
        serverless_runtime_data_disks: list[ServerlessRuntimeDataDisk]
        subnet: str
        subscription_id: str
        supplementary_file_location: str
        tags: str
        tenant_id: str
        vnet: str


    class azure.mgmt.informaticadatamanagement.types.InformaticaOrganizationResource(TrackedResource):
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
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.informaticadatamanagement.types.InformaticaOrganizationResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('OrganizationPropertiesCustomUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: OrganizationPropertiesCustomUpdate
        tags: dict[str, str]


    class azure.mgmt.informaticadatamanagement.types.InformaticaProperties(TypedDict, total=False):
        key "informaticaRegion": str
        key "organizationId": str
        key "organizationName": str
        key "singleSignOnUrl": str
        informatica_region: str
        organization_id: str
        organization_name: str
        single_sign_on_url: str


    class azure.mgmt.informaticadatamanagement.types.InformaticaServerlessRuntimeProperties(TypedDict, total=False):
        key "applicationType": Union[str, ApplicationType]
        key "computeUnits": str
        key "description": str
        key "executionTimeout": str
        key "platform": Union[str, PlatformType]
        key "provisioningState": Union[str, ProvisioningState]
        key "serverlessAccountLocation": Required[str]
        key "serverlessRuntimeConfig": ForwardRef('ServerlessRuntimeConfigProperties', module='types')
        key "serverlessRuntimeNetworkProfile": ForwardRef('ServerlessRuntimeNetworkProfile', module='types')
        key "serverlessRuntimeUserContextProperties": ForwardRef('ServerlessRuntimeUserContextProperties', module='types')
        key "supplementaryFileLocation": str
        advancedCustomProperties: list[AdvancedCustomProperties]
        advanced_custom_properties: list[AdvancedCustomProperties]
        application_type: Union[str, ApplicationType]
        compute_units: str
        description: str
        execution_timeout: str
        platform: Union[str, PlatformType]
        provisioning_state: Union[str, ProvisioningState]
        serverlessRuntimeDataDisks: list[ServerlessRuntimeDataDisk]
        serverlessRuntimeTags: list[ServerlessRuntimeTag]
        serverless_account_location: str
        serverless_runtime_config: ServerlessRuntimeConfigProperties
        serverless_runtime_data_disks: list[ServerlessRuntimeDataDisk]
        serverless_runtime_network_profile: ServerlessRuntimeNetworkProfile
        serverless_runtime_tags: list[ServerlessRuntimeTag]
        serverless_runtime_user_context_properties: ServerlessRuntimeUserContextProperties
        supplementary_file_location: str


    class azure.mgmt.informaticadatamanagement.types.InformaticaServerlessRuntimeResource(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('InformaticaServerlessRuntimeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        name: str
        properties: InformaticaServerlessRuntimeProperties
        system_data: SystemData
        type: str


    class azure.mgmt.informaticadatamanagement.types.InformaticaServerlessRuntimeResourceList(TypedDict, total=False):
        key "informaticaRuntimeResources": Required[list[InfaRuntimeResourceFetchMetaData]]
        informatica_runtime_resources: list[InfaRuntimeResourceFetchMetaData]


    class azure.mgmt.informaticadatamanagement.types.InformaticaServerlessRuntimeResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ServerlessRuntimePropertiesCustomUpdate', module='types')
        identity: ManagedServiceIdentity
        properties: ServerlessRuntimePropertiesCustomUpdate


    class azure.mgmt.informaticadatamanagement.types.LinkOrganization(TypedDict, total=False):
        key "token": str
        token: str


    class azure.mgmt.informaticadatamanagement.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.informaticadatamanagement.types.MarketplaceDetails(TypedDict, total=False):
        key "marketplaceSubscriptionId": str
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "offerDetails": Required[OfferDetails]
        marketplace_subscription_id: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        offer_details: OfferDetails


    class azure.mgmt.informaticadatamanagement.types.MarketplaceDetailsUpdate(TypedDict, total=False):
        key "marketplaceSubscriptionId": str
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "offerDetails": ForwardRef('OfferDetailsUpdate', module='types')
        marketplace_subscription_id: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        offer_details: OfferDetailsUpdate


    class azure.mgmt.informaticadatamanagement.types.NetworkInterfaceConfiguration(TypedDict, total=False):
        key "subnetId": Required[str]
        key "vnetId": Required[str]
        key "vnetResourceGuid": str
        subnet_id: str
        vnet_id: str
        vnet_resource_guid: str


    class azure.mgmt.informaticadatamanagement.types.NetworkInterfaceConfigurationUpdate(TypedDict, total=False):
        key "subnetId": str
        key "vnetId": str
        key "vnetResourceGuid": str
        subnet_id: str
        vnet_id: str
        vnet_resource_guid: str


    class azure.mgmt.informaticadatamanagement.types.OfferDetails(TypedDict, total=False):
        key "offerId": Required[str]
        key "planId": Required[str]
        key "planName": Required[str]
        key "publisherId": Required[str]
        key "termId": Required[str]
        key "termUnit": str
        offer_id: str
        plan_id: str
        plan_name: str
        publisher_id: str
        term_id: str
        term_unit: str


    class azure.mgmt.informaticadatamanagement.types.OfferDetailsUpdate(TypedDict, total=False):
        key "offerId": str
        key "planId": str
        key "planName": str
        key "publisherId": str
        key "termId": str
        key "termUnit": str
        offer_id: str
        plan_id: str
        plan_name: str
        publisher_id: str
        term_id: str
        term_unit: str


    class azure.mgmt.informaticadatamanagement.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.informaticadatamanagement.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.informaticadatamanagement.types.OrganizationProperties(TypedDict, total=False):
        key "companyDetails": ForwardRef('CompanyDetails', module='types')
        key "informaticaProperties": ForwardRef('InformaticaProperties', module='types')
        key "linkOrganization": ForwardRef('LinkOrganization', module='types')
        key "marketplaceDetails": ForwardRef('MarketplaceDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "userDetails": ForwardRef('UserDetails', module='types')
        company_details: CompanyDetails
        informatica_properties: InformaticaProperties
        link_organization: LinkOrganization
        marketplace_details: MarketplaceDetails
        provisioning_state: Union[str, ProvisioningState]
        user_details: UserDetails


    class azure.mgmt.informaticadatamanagement.types.OrganizationPropertiesCustomUpdate(TypedDict, total=False):
        key "companyDetails": ForwardRef('CompanyDetailsUpdate', module='types')
        key "existingResourceId": str
        key "informaticaOrganizationProperties": ForwardRef('InformaticaOrganizationResourceUpdate', module='types')
        key "marketplaceDetails": ForwardRef('MarketplaceDetailsUpdate', module='types')
        key "userDetails": ForwardRef('UserDetailsUpdate', module='types')
        company_details: CompanyDetailsUpdate
        existing_resource_id: str
        informatica_organization_properties: InformaticaOrganizationResourceUpdate
        marketplace_details: MarketplaceDetailsUpdate
        user_details: UserDetailsUpdate


    class azure.mgmt.informaticadatamanagement.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.informaticadatamanagement.types.RegionsMetadata(TypedDict, total=False):
        key "id": str
        key "name": str
        id: str
        name: str


    class azure.mgmt.informaticadatamanagement.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessConfigProperties(TypedDict, total=False):
        key "executionTimeout": str
        key "platform": Union[str, PlatformType]
        applicationTypes: list[ApplicationTypeMetadata]
        application_types: list[ApplicationTypeMetadata]
        computeUnits: list[ComputeUnitsMetadata]
        compute_units: list[ComputeUnitsMetadata]
        execution_timeout: str
        platform: Union[str, PlatformType]
        regions: list[RegionsMetadata]


    class azure.mgmt.informaticadatamanagement.types.ServerlessMetadataResponse(TypedDict, total=False):
        key "serverlessConfigProperties": ForwardRef('ServerlessConfigProperties', module='types')
        key "serverlessRuntimeConfigProperties": ForwardRef('ServerlessRuntimeConfigProperties', module='types')
        key "type": Union[str, RuntimeType]
        serverless_config_properties: ServerlessConfigProperties
        serverless_runtime_config_properties: ServerlessRuntimeConfigProperties
        type: Union[str, RuntimeType]


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeConfigProperties(TypedDict, total=False):
        cdiConfigProps: list[CdiConfigProps]
        cdi_config_props: list[CdiConfigProps]
        cdieConfigProps: list[CdiConfigProps]
        cdie_config_props: list[CdiConfigProps]


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeConfigPropertiesUpdate(TypedDict, total=False):
        cdiConfigProps: list[CdiConfigProps]
        cdi_config_props: list[CdiConfigProps]
        cdieConfigProps: list[CdiConfigProps]
        cdie_config_props: list[CdiConfigProps]


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeDataDisk(TypedDict, total=False):
        key "mountOptions": str
        key "serverHostOrIpAddress": str
        key "sourceMount": str
        key "targetMount": str
        key "type": str
        mount_options: str
        server_host_or_ip_address: str
        source_mount: str
        target_mount: str
        type: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeDependency(TypedDict, total=False):
        key "appContextId": Required[str]
        key "description": Required[str]
        key "documentType": Required[str]
        key "id": Required[str]
        key "lastUpdatedTime": Required[str]
        key "path": Required[str]
        app_context_id: str
        description: str
        document_type: str
        id: str
        last_updated_time: str
        path: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeNetworkProfile(TypedDict, total=False):
        key "networkInterfaceConfiguration": Required[NetworkInterfaceConfiguration]
        network_interface_configuration: NetworkInterfaceConfiguration


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeNetworkProfileUpdate(TypedDict, total=False):
        key "networkInterfaceConfiguration": Required[NetworkInterfaceConfigurationUpdate]
        network_interface_configuration: NetworkInterfaceConfigurationUpdate


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimePropertiesCustomUpdate(TypedDict, total=False):
        key "applicationType": Union[str, ApplicationType]
        key "computeUnits": str
        key "description": str
        key "executionTimeout": str
        key "platform": Union[str, PlatformType]
        key "serverlessAccountLocation": str
        key "serverlessRuntimeConfig": ForwardRef('ServerlessRuntimeConfigPropertiesUpdate', module='types')
        key "serverlessRuntimeNetworkProfile": ForwardRef('ServerlessRuntimeNetworkProfileUpdate', module='types')
        key "serverlessRuntimeUserContextProperties": ForwardRef('ServerlessRuntimeUserContextPropertiesUpdate', module='types')
        key "supplementaryFileLocation": str
        advancedCustomProperties: list[AdvancedCustomProperties]
        advanced_custom_properties: list[AdvancedCustomProperties]
        application_type: Union[str, ApplicationType]
        compute_units: str
        description: str
        execution_timeout: str
        platform: Union[str, PlatformType]
        serverlessRuntimeDataDisks: list[ServerlessRuntimeDataDisk]
        serverlessRuntimeTags: list[ServerlessRuntimeTag]
        serverless_account_location: str
        serverless_runtime_config: ServerlessRuntimeConfigPropertiesUpdate
        serverless_runtime_data_disks: list[ServerlessRuntimeDataDisk]
        serverless_runtime_network_profile: ServerlessRuntimeNetworkProfileUpdate
        serverless_runtime_tags: list[ServerlessRuntimeTag]
        serverless_runtime_user_context_properties: ServerlessRuntimeUserContextPropertiesUpdate
        supplementary_file_location: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeTag(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeUserContextProperties(TypedDict, total=False):
        key "userContextToken": Required[str]
        user_context_token: str


    class azure.mgmt.informaticadatamanagement.types.ServerlessRuntimeUserContextPropertiesUpdate(TypedDict, total=False):
        key "userContextToken": str
        user_context_token: str


    class azure.mgmt.informaticadatamanagement.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.informaticadatamanagement.types.TrackedResource(Resource):
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


    class azure.mgmt.informaticadatamanagement.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.informaticadatamanagement.types.UserDetails(TypedDict, total=False):
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        key "upn": str
        email_address: str
        first_name: str
        last_name: str
        phone_number: str
        upn: str


    class azure.mgmt.informaticadatamanagement.types.UserDetailsUpdate(TypedDict, total=False):
        key "emailAddress": str
        key "firstName": str
        key "lastName": str
        key "phoneNumber": str
        key "upn": str
        email_address: str
        first_name: str
        last_name: str
        phone_number: str
        upn: str


```