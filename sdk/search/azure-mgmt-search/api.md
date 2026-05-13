```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.search

    class azure.mgmt.search.SearchManagementClient(_SearchManagementClientOperationsMixin): implements ContextManager 
        admin_keys: AdminKeysOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        offerings: OfferingsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        query_keys: QueryKeysOperations
        services: ServicesOperations
        shared_private_link_resources: SharedPrivateLinkResourcesOperations
        usages: UsagesOperations

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

        @distributed_trace
        def usage_by_subscription_sku(
                self, 
                location: str, 
                sku_name: str, 
                **kwargs: Any
            ) -> QuotaUsageResult: ...


namespace azure.mgmt.search.aio

    class azure.mgmt.search.aio.SearchManagementClient(_SearchManagementClientOperationsMixin): implements AsyncContextManager 
        admin_keys: AdminKeysOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        offerings: OfferingsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        query_keys: QueryKeysOperations
        services: ServicesOperations
        shared_private_link_resources: SharedPrivateLinkResourcesOperations
        usages: UsagesOperations

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

        @distributed_trace_async
        async def usage_by_subscription_sku(
                self, 
                location: str, 
                sku_name: str, 
                **kwargs: Any
            ) -> QuotaUsageResult: ...


namespace azure.mgmt.search.aio.operations

    class azure.mgmt.search.aio.operations.AdminKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AdminKeyResult: ...

        @distributed_trace_async
        async def regenerate(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                key_kind: Union[str, AdminKeyKind], 
                **kwargs: Any
            ) -> AdminKeyResult: ...


    class azure.mgmt.search.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                nsp_config_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                nsp_config_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.search.aio.operations.OfferingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def list(self, **kwargs: Any) -> OfferingsListResult: ...


    class azure.mgmt.search.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.search.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> Optional[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.search.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_supported(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.search.aio.operations.QueryKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                name: str, 
                **kwargs: Any
            ) -> QueryKey: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_by_search_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QueryKey]: ...


    class azure.mgmt.search.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: SearchService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SearchService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SearchService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SearchService]: ...

        @distributed_trace_async
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[SearchService]: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> SearchService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SearchService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SearchService]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: SearchServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...


    class azure.mgmt.search.aio.operations.SharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.search.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[QuotaUsageResult]: ...


namespace azure.mgmt.search.models

    class azure.mgmt.search.models.AadAuthFailureMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP401_WITH_BEARER_CHALLENGE = "http401WithBearerChallenge"
        HTTP403 = "http403"


    class azure.mgmt.search.models.AccessRule(_Model):
        name: Optional[str]
        properties: Optional[AccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[AccessRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.AccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.search.models.AccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, AccessRuleDirection]]
        email_addresses: Optional[list[str]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        phone_numbers: Optional[list[str]]
        subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, AccessRuleDirection]] = ..., 
                email_addresses: Optional[list[str]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeter]] = ..., 
                phone_numbers: Optional[list[str]] = ..., 
                subscriptions: Optional[list[AccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.AccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.search.models.AdminKeyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.search.models.AdminKeyResult(_Model):
        primary_key: Optional[str]
        secondary_key: Optional[str]


    class azure.mgmt.search.models.AzureActiveDirectoryApplicationCredentials(_Model):
        application_id: Optional[str]
        application_secret: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                application_secret: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.CheckNameAvailabilityInput(_Model):
        name: str
        type: Literal["searchServices"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.CheckNameAvailabilityOutput(_Model):
        is_name_available: Optional[bool]
        message: Optional[str]
        reason: Optional[Union[str, UnavailableNameReason]]


    class azure.mgmt.search.models.CloudError(_Model):
        error: Optional[CloudErrorBody]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.ComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIDENTIAL = "Confidential"
        DEFAULT = "Default"


    class azure.mgmt.search.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.search.models.DataIdentity(_Model):
        odata_type: str

        @overload
        def __init__(
                self, 
                *, 
                odata_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.DataNoneIdentity(DataIdentity, discriminator='#Microsoft.Azure.Search.DataNoneIdentity'):
        odata_type: Literal["#DataNoneIdentity"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.DataPlaneAadOrApiKeyAuthOption(_Model):
        aad_auth_failure_mode: Optional[Union[str, AadAuthFailureMode]]

        @overload
        def __init__(
                self, 
                *, 
                aad_auth_failure_mode: Optional[Union[str, AadAuthFailureMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.DataPlaneAuthOptions(_Model):
        aad_or_api_key: Optional[DataPlaneAadOrApiKeyAuthOption]
        api_key_only: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                aad_or_api_key: Optional[DataPlaneAadOrApiKeyAuthOption] = ..., 
                api_key_only: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.DataUserAssignedIdentity(DataIdentity, discriminator='#Microsoft.Azure.Search.DataUserAssignedIdentity'):
        federated_identity_client_id: Optional[str]
        odata_type: Literal["#DataUserAssignedIdentity"]
        user_assigned_identity: str

        @overload
        def __init__(
                self, 
                *, 
                federated_identity_client_id: Optional[str] = ..., 
                user_assigned_identity: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.EncryptionWithCmk(_Model):
        encryption_compliance_status: Optional[Union[str, SearchEncryptionComplianceStatus]]
        enforcement: Optional[Union[str, SearchEncryptionWithCmk]]
        service_level_encryption_key: Optional[SearchResourceEncryptionKey]

        @overload
        def __init__(
                self, 
                *, 
                enforcement: Optional[Union[str, SearchEncryptionWithCmk]] = ..., 
                service_level_encryption_key: Optional[SearchResourceEncryptionKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.FeatureOffering(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.HostingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        HIGH_DENSITY = "HighDensity"


    class azure.mgmt.search.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.search.models.IpRule(_Model):
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.IssueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURATION_PROPAGATION_FAILURE = "ConfigurationPropagationFailure"
        MISSING_IDENTITY_CONFIGURATION = "MissingIdentityConfiguration"
        MISSING_PERIMETER_CONFIGURATION = "MissingPerimeterConfiguration"
        UNKNOWN = "Unknown"


    class azure.mgmt.search.models.KnowledgeRetrieval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "free"
        STANDARD = "standard"


    class azure.mgmt.search.models.NetworkRuleSet(_Model):
        bypass: Optional[Union[str, SearchBypass]]
        ip_rules: Optional[list[IpRule]]

        @overload
        def __init__(
                self, 
                *, 
                bypass: Optional[Union[str, SearchBypass]] = ..., 
                ip_rules: Optional[list[IpRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[ResourceAssociation]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityProfile] = ..., 
                resource_association: Optional[ResourceAssociation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.search.models.NetworkSecurityProfile(_Model):
        access_rules: Optional[list[AccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[AccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.OfferingsByRegion(_Model):
        features: Optional[list[FeatureOffering]]
        region_name: Optional[str]
        skus: Optional[list[SkuOffering]]

        @overload
        def __init__(
                self, 
                *, 
                features: Optional[list[FeatureOffering]] = ..., 
                region_name: Optional[str] = ..., 
                skus: Optional[list[SkuOffering]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.OfferingsListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[OfferingsByRegion]]


    class azure.mgmt.search.models.Operation(_Model):
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


    class azure.mgmt.search.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.search.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.search.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.PrivateEndpointConnectionProperties(_Model):
        group_id: Optional[str]
        private_endpoint: Optional[PrivateEndpointConnectionPropertiesPrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateEndpointConnectionPropertiesPrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, PrivateLinkServiceConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_endpoint: Optional[PrivateEndpointConnectionPropertiesPrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateEndpointConnectionPropertiesPrivateLinkServiceConnectionState] = ..., 
                provisioning_state: Optional[Union[str, PrivateLinkServiceConnectionProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.PrivateEndpointConnectionPropertiesPrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.PrivateEndpointConnectionPropertiesPrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateLinkServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateLinkServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str


    class azure.mgmt.search.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]
        shareable_private_link_resource_types: Optional[list[ShareablePrivateLinkResourceType]]


    class azure.mgmt.search.models.PrivateLinkServiceConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        INCOMPLETE = "Incomplete"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.search.models.PrivateLinkServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.search.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]


    class azure.mgmt.search.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[Union[str, IssueType]]
        severity: Optional[Union[str, Severity]]
        suggested_access_rules: Optional[list[AccessRule]]
        suggested_resource_ids: Optional[list[str]]


    class azure.mgmt.search.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        PROVISIONING = "provisioning"
        SUCCEEDED = "succeeded"


    class azure.mgmt.search.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.search.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.search.models.QueryKey(_Model):
        key: Optional[str]
        name: Optional[str]


    class azure.mgmt.search.models.QuotaUsageResult(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[QuotaUsageResultName]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.QuotaUsageResultName(_Model):
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


    class azure.mgmt.search.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.search.models.ResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"
        LEARNING = "Learning"


    class azure.mgmt.search.models.SearchBypass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_PORTAL = "AzurePortal"
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.search.models.SearchDataExfiltrationProtection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK_ALL = "BlockAll"


    class azure.mgmt.search.models.SearchEncryptionComplianceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "NonCompliant"


    class azure.mgmt.search.models.SearchEncryptionWithCmk(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.search.models.SearchResourceEncryptionKey(_Model):
        access_credentials: Optional[AzureActiveDirectoryApplicationCredentials]
        identity: Optional[DataIdentity]
        key_name: Optional[str]
        key_version: Optional[str]
        vault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_credentials: Optional[AzureActiveDirectoryApplicationCredentials] = ..., 
                identity: Optional[DataIdentity] = ..., 
                key_name: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SearchSemanticSearch(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        FREE = "free"
        STANDARD = "standard"


    class azure.mgmt.search.models.SearchService(TrackedResource):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[SearchServiceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[SearchServiceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.search.models.SearchServiceProperties(_Model):
        auth_options: Optional[DataPlaneAuthOptions]
        compute_type: Optional[Union[str, ComputeType]]
        data_exfiltration_protections: Optional[list[Union[str, SearchDataExfiltrationProtection]]]
        disable_local_auth: Optional[bool]
        e_tag: Optional[str]
        encryption_with_cmk: Optional[EncryptionWithCmk]
        endpoint: Optional[str]
        hosting_mode: Optional[Union[str, HostingMode]]
        knowledge_retrieval: Optional[Union[str, KnowledgeRetrieval]]
        network_rule_set: Optional[NetworkRuleSet]
        partition_count: Optional[int]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        replica_count: Optional[int]
        semantic_search: Optional[Union[str, SearchSemanticSearch]]
        service_upgraded_at: Optional[datetime]
        shared_private_link_resources: Optional[list[SharedPrivateLinkResource]]
        status: Optional[Union[str, SearchServiceStatus]]
        status_details: Optional[str]
        upgrade_available: Optional[Union[str, UpgradeAvailable]]

        @overload
        def __init__(
                self, 
                *, 
                auth_options: Optional[DataPlaneAuthOptions] = ..., 
                compute_type: Optional[Union[str, ComputeType]] = ..., 
                data_exfiltration_protections: Optional[list[Union[str, SearchDataExfiltrationProtection]]] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption_with_cmk: Optional[EncryptionWithCmk] = ..., 
                endpoint: Optional[str] = ..., 
                hosting_mode: Optional[Union[str, HostingMode]] = ..., 
                knowledge_retrieval: Optional[Union[str, KnowledgeRetrieval]] = ..., 
                network_rule_set: Optional[NetworkRuleSet] = ..., 
                partition_count: Optional[int] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                replica_count: Optional[int] = ..., 
                semantic_search: Optional[Union[str, SearchSemanticSearch]] = ..., 
                upgrade_available: Optional[Union[str, UpgradeAvailable]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SearchServiceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "degraded"
        DELETING = "deleting"
        DISABLED = "disabled"
        ERROR = "error"
        PROVISIONING = "provisioning"
        RUNNING = "running"
        STOPPED = "stopped"


    class azure.mgmt.search.models.SearchServiceUpdate(Resource):
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[SearchServiceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SearchServiceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.search.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.search.models.ShareablePrivateLinkResourceProperties(_Model):
        description: Optional[str]
        group_id: Optional[str]
        type: Optional[str]


    class azure.mgmt.search.models.ShareablePrivateLinkResourceType(_Model):
        name: Optional[str]
        properties: Optional[ShareablePrivateLinkResourceProperties]


    class azure.mgmt.search.models.SharedPrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SharedPrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SharedPrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SharedPrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        private_link_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, SharedPrivateLinkResourceProvisioningState]]
        request_message: Optional[str]
        resource_region: Optional[str]
        status: Optional[Union[str, SharedPrivateLinkResourceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                provisioning_state: Optional[Union[str, SharedPrivateLinkResourceProvisioningState]] = ..., 
                request_message: Optional[str] = ..., 
                resource_region: Optional[str] = ..., 
                status: Optional[Union[str, SharedPrivateLinkResourceStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SharedPrivateLinkResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        INCOMPLETE = "Incomplete"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.search.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.search.models.Sku(_Model):
        name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SkuLimits(_Model):
        indexers: Optional[int]
        indexes: Optional[int]
        partition_storage_in_gigabytes: Optional[float]
        partition_vector_storage_in_gigabytes: Optional[float]
        partitions: Optional[int]
        replicas: Optional[int]
        search_units: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                indexers: Optional[int] = ..., 
                indexes: Optional[int] = ..., 
                partition_storage_in_gigabytes: Optional[float] = ..., 
                partition_vector_storage_in_gigabytes: Optional[float] = ..., 
                partitions: Optional[int] = ..., 
                replicas: Optional[int] = ..., 
                search_units: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "basic"
        FREE = "free"
        SERVERLESS = "serverless"
        STANDARD = "standard"
        STANDARD2 = "standard2"
        STANDARD3 = "standard3"
        STORAGE_OPTIMIZED_L1 = "storage_optimized_l1"
        STORAGE_OPTIMIZED_L2 = "storage_optimized_l2"


    class azure.mgmt.search.models.SkuOffering(_Model):
        limits: Optional[SkuLimits]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[SkuLimits] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.search.models.SystemData(_Model):
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


    class azure.mgmt.search.models.TrackedResource(Resource):
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


    class azure.mgmt.search.models.UnavailableNameReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.search.models.UpgradeAvailable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        NOT_AVAILABLE = "notAvailable"


    class azure.mgmt.search.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.search.operations

    class azure.mgmt.search.operations.AdminKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> AdminKeyResult: ...

        @distributed_trace
        def regenerate(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                key_kind: Union[str, AdminKeyKind], 
                **kwargs: Any
            ) -> AdminKeyResult: ...


    class azure.mgmt.search.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                nsp_config_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                nsp_config_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.search.operations.OfferingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list(self, **kwargs: Any) -> OfferingsListResult: ...


    class azure.mgmt.search.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.search.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> Optional[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                private_endpoint_connection_name: str, 
                private_endpoint_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.search.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_supported(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.search.operations.QueryKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                name: str, 
                **kwargs: Any
            ) -> QueryKey: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                key: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_by_search_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[QueryKey]: ...


    class azure.mgmt.search.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: SearchService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SearchService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SearchService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SearchService]: ...

        @distributed_trace
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[SearchService]: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> SearchService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SearchService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SearchService]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: SearchServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SearchService: ...


    class azure.mgmt.search.operations.SharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                shared_private_link_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list_by_service(
                self, 
                resource_group_name: str, 
                search_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SharedPrivateLinkResource]: ...


    class azure.mgmt.search.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[QuotaUsageResult]: ...


```