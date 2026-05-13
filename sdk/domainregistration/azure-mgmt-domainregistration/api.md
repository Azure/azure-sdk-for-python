```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.domainregistration

    class azure.mgmt.domainregistration.DomainRegistrationMgmtClient: implements ContextManager 
        domain_registration_provider: DomainRegistrationProviderOperations
        domains: DomainsOperations
        top_level_domains: TopLevelDomainsOperations

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


namespace azure.mgmt.domainregistration.aio

    class azure.mgmt.domainregistration.aio.DomainRegistrationMgmtClient: implements AsyncContextManager 
        domain_registration_provider: DomainRegistrationProviderOperations
        domains: DomainsOperations
        top_level_domains: TopLevelDomainsOperations

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


namespace azure.mgmt.domainregistration.aio.operations

    class azure.mgmt.domainregistration.aio.operations.DomainRegistrationProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[CsmOperationDescription]: ...


    class azure.mgmt.domainregistration.aio.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Domain]: ...

        @overload
        async def check_availability(
                self, 
                identifier: NameIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        async def check_availability(
                self, 
                identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        async def check_availability(
                self, 
                identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        async def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: DomainOwnershipIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        async def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        async def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                force_hard_delete_domain: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace_async
        async def get_control_center_sso_request(self, **kwargs: Any) -> DomainControlCenterSsoRequest: ...

        @distributed_trace_async
        async def get_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Domain]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Domain]: ...

        @distributed_trace
        def list_ownership_identifiers(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DomainOwnershipIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: DomainRecommendationSearchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[NameIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[NameIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[NameIdentifier]: ...

        @distributed_trace_async
        async def renew(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def transfer_out(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: DomainPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        async def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: DomainOwnershipIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        async def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        async def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...


    class azure.mgmt.domainregistration.aio.operations.TopLevelDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> TopLevelDomain: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[TopLevelDomain]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: TopLevelDomainAgreementOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TldLegalAgreement]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TldLegalAgreement]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncItemPaged[TldLegalAgreement]: ...


namespace azure.mgmt.domainregistration.models

    class azure.mgmt.domainregistration.models.Address(_Model):
        address1: str
        address2: Optional[str]
        city: str
        country: str
        postal_code: str
        state: str

        @overload
        def __init__(
                self, 
                *, 
                address1: str, 
                address2: Optional[str] = ..., 
                city: str, 
                country: str, 
                postal_code: str, 
                state: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.AzureResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRAFFIC_MANAGER = "TrafficManager"
        WEBSITE = "Website"


    class azure.mgmt.domainregistration.models.Contact(_Model):
        address_mailing: Optional[Address]
        email: str
        fax: Optional[str]
        job_title: Optional[str]
        name_first: str
        name_last: str
        name_middle: Optional[str]
        organization: Optional[str]
        phone: str

        @overload
        def __init__(
                self, 
                *, 
                address_mailing: Optional[Address] = ..., 
                email: str, 
                fax: Optional[str] = ..., 
                job_title: Optional[str] = ..., 
                name_first: str, 
                name_last: str, 
                name_middle: Optional[str] = ..., 
                organization: Optional[str] = ..., 
                phone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.domainregistration.models.CsmOperationDescription(_Model):
        display: Optional[CsmOperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[CsmOperationDescriptionProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[CsmOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[CsmOperationDescriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.CsmOperationDescriptionProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.CsmOperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.CustomHostNameDnsRecordType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"
        C_NAME = "CName"


    class azure.mgmt.domainregistration.models.DefaultErrorResponse(_Model):
        error: Optional[DefaultErrorResponseError]


    class azure.mgmt.domainregistration.models.DefaultErrorResponseError(_Model):
        code: Optional[str]
        details: Optional[list[DefaultErrorResponseErrorDetailsItem]]
        innererror: Optional[str]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[list[DefaultErrorResponseErrorDetailsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DefaultErrorResponseErrorDetailsItem(_Model):
        code: Optional[str]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.domainregistration.models.Dimension(_Model):
        display_name: Optional[str]
        internal_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DnsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DNS = "AzureDns"
        DEFAULT_DOMAIN_REGISTRAR_DNS = "DefaultDomainRegistrarDns"


    class azure.mgmt.domainregistration.models.Domain(TrackedResource):
        id: str
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[DomainProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                location: str, 
                properties: Optional[DomainProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainregistration.models.DomainAvailabilityCheckResult(_Model):
        available: Optional[bool]
        domain_type: Optional[Union[str, DomainType]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                available: Optional[bool] = ..., 
                domain_type: Optional[Union[str, DomainType]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainControlCenterSsoRequest(_Model):
        post_parameter_key: Optional[str]
        post_parameter_value: Optional[str]
        url: Optional[str]


    class azure.mgmt.domainregistration.models.DomainOwnershipIdentifier(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[DomainOwnershipIdentifierProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[DomainOwnershipIdentifierProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainregistration.models.DomainOwnershipIdentifierProperties(_Model):
        ownership_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ownership_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainPatchResource(ProxyOnlyResource):
        id: str
        kind: str
        name: str
        properties: Optional[DomainPatchResourceProperties]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[DomainPatchResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainregistration.models.DomainPatchResourceProperties(_Model):
        auth_code: Optional[str]
        auto_renew: Optional[bool]
        consent: DomainPurchaseConsent
        contact_admin: Contact
        contact_billing: Contact
        contact_registrant: Contact
        contact_tech: Contact
        created_time: Optional[datetime]
        dns_type: Optional[Union[str, DnsType]]
        dns_zone_id: Optional[str]
        domain_not_renewable_reasons: Optional[list[Union[str, ResourceNotRenewableReason]]]
        expiration_time: Optional[datetime]
        last_renewed_time: Optional[datetime]
        managed_host_names: Optional[list[HostName]]
        name_servers: Optional[list[str]]
        privacy: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        ready_for_dns_record_management: Optional[bool]
        registration_status: Optional[Union[str, DomainStatus]]
        target_dns_type: Optional[Union[str, DnsType]]

        @overload
        def __init__(
                self, 
                *, 
                auth_code: Optional[str] = ..., 
                auto_renew: Optional[bool] = ..., 
                consent: DomainPurchaseConsent, 
                contact_admin: Contact, 
                contact_billing: Contact, 
                contact_registrant: Contact, 
                contact_tech: Contact, 
                dns_type: Optional[Union[str, DnsType]] = ..., 
                dns_zone_id: Optional[str] = ..., 
                privacy: Optional[bool] = ..., 
                target_dns_type: Optional[Union[str, DnsType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainProperties(_Model):
        auth_code: Optional[str]
        auto_renew: Optional[bool]
        consent: DomainPurchaseConsent
        contact_admin: Contact
        contact_billing: Contact
        contact_registrant: Contact
        contact_tech: Contact
        created_time: Optional[datetime]
        dns_type: Optional[Union[str, DnsType]]
        dns_zone_id: Optional[str]
        domain_not_renewable_reasons: Optional[list[Union[str, ResourceNotRenewableReason]]]
        expiration_time: Optional[datetime]
        last_renewed_time: Optional[datetime]
        managed_host_names: Optional[list[HostName]]
        name_servers: Optional[list[str]]
        privacy: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        ready_for_dns_record_management: Optional[bool]
        registration_status: Optional[Union[str, DomainStatus]]
        target_dns_type: Optional[Union[str, DnsType]]

        @overload
        def __init__(
                self, 
                *, 
                auth_code: Optional[str] = ..., 
                auto_renew: Optional[bool] = ..., 
                consent: DomainPurchaseConsent, 
                contact_admin: Contact, 
                contact_billing: Contact, 
                contact_registrant: Contact, 
                contact_tech: Contact, 
                dns_type: Optional[Union[str, DnsType]] = ..., 
                dns_zone_id: Optional[str] = ..., 
                privacy: Optional[bool] = ..., 
                target_dns_type: Optional[Union[str, DnsType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainPurchaseConsent(_Model):
        agreed_at: Optional[datetime]
        agreed_by: Optional[str]
        agreement_keys: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                agreed_at: Optional[datetime] = ..., 
                agreed_by: Optional[str] = ..., 
                agreement_keys: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainRecommendationSearchParameters(_Model):
        keywords: Optional[str]
        max_domain_recommendations: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                keywords: Optional[str] = ..., 
                max_domain_recommendations: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.DomainStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        AWAITING = "Awaiting"
        CANCELLED = "Cancelled"
        CONFISCATED = "Confiscated"
        DISABLED = "Disabled"
        EXCLUDED = "Excluded"
        EXPIRED = "Expired"
        FAILED = "Failed"
        HELD = "Held"
        JSON_CONVERTER_FAILED = "JsonConverterFailed"
        LOCKED = "Locked"
        PARKED = "Parked"
        PENDING = "Pending"
        RESERVED = "Reserved"
        REVERTED = "Reverted"
        SUSPENDED = "Suspended"
        TRANSFERRED = "Transferred"
        UNKNOWN = "Unknown"
        UNLOCKED = "Unlocked"
        UNPARKED = "Unparked"
        UPDATED = "Updated"


    class azure.mgmt.domainregistration.models.DomainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SOFT_DELETED = "SoftDeleted"


    class azure.mgmt.domainregistration.models.HostName(_Model):
        azure_resource_name: Optional[str]
        azure_resource_type: Optional[Union[str, AzureResourceType]]
        custom_host_name_dns_record_type: Optional[Union[str, CustomHostNameDnsRecordType]]
        host_name_type: Optional[Union[str, HostNameType]]
        name: Optional[str]
        site_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                azure_resource_name: Optional[str] = ..., 
                azure_resource_type: Optional[Union[str, AzureResourceType]] = ..., 
                custom_host_name_dns_record_type: Optional[Union[str, CustomHostNameDnsRecordType]] = ..., 
                host_name_type: Optional[Union[str, HostNameType]] = ..., 
                name: Optional[str] = ..., 
                site_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.HostNameType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        VERIFIED = "Verified"


    class azure.mgmt.domainregistration.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        log_filter_pattern: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                log_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.MetricAvailability(_Model):
        blob_duration: Optional[str]
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        availabilities: Optional[list[MetricAvailability]]
        category: Optional[str]
        dimensions: Optional[list[Dimension]]
        display_description: Optional[str]
        display_name: Optional[str]
        enable_regional_mdm_account: Optional[bool]
        fill_gap_with_zero: Optional[bool]
        is_internal: Optional[bool]
        metric_filter_pattern: Optional[str]
        name: Optional[str]
        source_mdm_account: Optional[str]
        source_mdm_namespace: Optional[str]
        supported_aggregation_types: Optional[list[str]]
        supported_time_grain_types: Optional[list[str]]
        supports_instance_level_aggregation: Optional[bool]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[list[MetricAvailability]] = ..., 
                category: Optional[str] = ..., 
                dimensions: Optional[list[Dimension]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[bool] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                is_internal: Optional[bool] = ..., 
                metric_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                source_mdm_account: Optional[str] = ..., 
                source_mdm_namespace: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                supports_instance_level_aggregation: Optional[bool] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.NameIdentifier(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.domainregistration.models.ProxyOnlyResource(_Model):
        id: Optional[str]
        kind: Optional[str]
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.domainregistration.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.domainregistration.models.ResourceNotRenewableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRATION_NOT_IN_RENEWAL_TIME_RANGE = "ExpirationNotInRenewalTimeRange"
        REGISTRATION_STATUS_NOT_SUPPORTED_FOR_RENEWAL = "RegistrationStatusNotSupportedForRenewal"
        SUBSCRIPTION_NOT_ACTIVE = "SubscriptionNotActive"


    class azure.mgmt.domainregistration.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.SystemData(_Model):
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


    class azure.mgmt.domainregistration.models.TldLegalAgreement(_Model):
        agreement_key: str
        content: str
        title: str
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agreement_key: str, 
                content: str, 
                title: str, 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.TopLevelDomain(ProxyResource):
        id: str
        kind: Optional[str]
        name: str
        properties: Optional[TopLevelDomainProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                properties: Optional[TopLevelDomainProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainregistration.models.TopLevelDomainAgreementOption(_Model):
        for_transfer: Optional[bool]
        include_privacy: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                for_transfer: Optional[bool] = ..., 
                include_privacy: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.TopLevelDomainProperties(_Model):
        privacy: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                privacy: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainregistration.models.TrackedResource(Resource):
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


namespace azure.mgmt.domainregistration.operations

    class azure.mgmt.domainregistration.operations.DomainRegistrationProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[CsmOperationDescription]: ...


    class azure.mgmt.domainregistration.operations.DomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: Domain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Domain]: ...

        @overload
        def check_availability(
                self, 
                identifier: NameIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        def check_availability(
                self, 
                identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        def check_availability(
                self, 
                identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailabilityCheckResult: ...

        @overload
        def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: DomainOwnershipIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        def create_or_update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                *, 
                force_hard_delete_domain: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @distributed_trace
        def get_control_center_sso_request(self, **kwargs: Any) -> DomainControlCenterSsoRequest: ...

        @distributed_trace
        def get_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Domain]: ...

        @distributed_trace
        def list_ownership_identifiers(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DomainOwnershipIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: DomainRecommendationSearchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[NameIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[NameIdentifier]: ...

        @overload
        def list_recommendations(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[NameIdentifier]: ...

        @distributed_trace
        def renew(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def transfer_out(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: DomainPatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Domain: ...

        @overload
        def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: DomainOwnershipIdentifier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...

        @overload
        def update_ownership_identifier(
                self, 
                resource_group_name: str, 
                domain_name: str, 
                name: str, 
                domain_ownership_identifier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainOwnershipIdentifier: ...


    class azure.mgmt.domainregistration.operations.TopLevelDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> TopLevelDomain: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[TopLevelDomain]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: TopLevelDomainAgreementOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TldLegalAgreement]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TldLegalAgreement]: ...

        @overload
        def list_agreements(
                self, 
                name: str, 
                agreement_option: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ItemPaged[TldLegalAgreement]: ...


```