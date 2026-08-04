```py
namespace azure.mgmt.recoveryservices

    class azure.mgmt.recoveryservices.RecoveryServicesClient(_RecoveryServicesClientOperationsMixin): implements ContextManager 
        deleted_vaults: DeletedVaultsOperations
        operations: Operations
        private_link_resources: PrivateLinkResourcesOperations
        recovery_services: RecoveryServicesOperations
        registered_identities: RegisteredIdentitiesOperations
        replication_usages: ReplicationUsagesOperations
        usages: UsagesOperations
        vault_certificates: VaultCertificatesOperations
        vault_extended_info: VaultExtendedInfoOperations
        vaults: VaultsOperations

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

        @distributed_trace
        def get_operation_result(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[Vault]: ...

        @distributed_trace
        def get_operation_status(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.recoveryservices.aio

    class azure.mgmt.recoveryservices.aio.RecoveryServicesClient(_RecoveryServicesClientOperationsMixin): implements AsyncContextManager 
        deleted_vaults: DeletedVaultsOperations
        operations: Operations
        private_link_resources: PrivateLinkResourcesOperations
        recovery_services: RecoveryServicesOperations
        registered_identities: RegisteredIdentitiesOperations
        replication_usages: ReplicationUsagesOperations
        usages: UsagesOperations
        vault_certificates: VaultCertificatesOperations
        vault_extended_info: VaultExtendedInfoOperations
        vaults: VaultsOperations

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

        @distributed_trace_async
        async def get_operation_result(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> Optional[Vault]: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.recoveryservices.aio.operations

    class azure.mgmt.recoveryservices.aio.operations.DeletedVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: DeletedVaultUndeleteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: DeletedVaultUndeleteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        async def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'operation_id', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        async def get_operation_status(
                self, 
                location: str, 
                deleted_vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        def list_by_subscription_id(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedVault]: ...


    class azure.mgmt.recoveryservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ClientDiscoveryValueForSingleApi]: ...


    class azure.mgmt.recoveryservices.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.recoveryservices.aio.operations.RecoveryServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def capabilities(
                self, 
                location: str, 
                input: ResourceCapabilities, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        async def capabilities(
                self, 
                location: str, 
                input: ResourceCapabilities, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        async def capabilities(
                self, 
                location: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...


    class azure.mgmt.recoveryservices.aio.operations.RegisteredIdentitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                identity_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservices.aio.operations.ReplicationUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ReplicationUsage]: ...


    class azure.mgmt.recoveryservices.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_vaults(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VaultUsage]: ...


    class azure.mgmt.recoveryservices.aio.operations.VaultCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: CertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: CertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...


    class azure.mgmt.recoveryservices.aio.operations.VaultExtendedInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...


    class azure.mgmt.recoveryservices.aio.operations.VaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: Vault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: Vault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: PatchVault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: PatchVault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> Vault: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Vault]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> AsyncItemPaged[Vault]: ...


namespace azure.mgmt.recoveryservices.models

    class azure.mgmt.recoveryservices.models.AlertsState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservices.models.AssociatedIdentity(_Model):
        operation_identity_type: Optional[Union[str, IdentityType]]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                operation_identity_type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.AuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ACCESS_CONTROL_SERVICE = "AccessControlService"
        ACS = "ACS"
        AZURE_ACTIVE_DIRECTORY = "AzureActiveDirectory"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservices.models.AzureMonitorAlertSettings(_Model):
        alerts_for_all_failover_issues: Optional[Union[str, AlertsState]]
        alerts_for_all_job_failures: Optional[Union[str, AlertsState]]
        alerts_for_all_replication_issues: Optional[Union[str, AlertsState]]

        @overload
        def __init__(
                self, 
                *, 
                alerts_for_all_failover_issues: Optional[Union[str, AlertsState]] = ..., 
                alerts_for_all_job_failures: Optional[Union[str, AlertsState]] = ..., 
                alerts_for_all_replication_issues: Optional[Union[str, AlertsState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.BCDRSecurityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCELLENT = "Excellent"
        FAIR = "Fair"
        GOOD = "Good"
        POOR = "Poor"


    class azure.mgmt.recoveryservices.models.BackupStorageVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNASSIGNED = "Unassigned"
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.recoveryservices.models.CapabilitiesProperties(_Model):
        dns_zones: Optional[list[DNSZone]]

        @overload
        def __init__(
                self, 
                *, 
                dns_zones: Optional[list[DNSZone]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CapabilitiesResponse(ResourceCapabilitiesBase):
        properties: Optional[CapabilitiesResponseProperties]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilitiesResponseProperties] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CapabilitiesResponseProperties(_Model):
        dns_zones: Optional[list[DNSZoneResponse]]

        @overload
        def __init__(
                self, 
                *, 
                dns_zones: Optional[list[DNSZoneResponse]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CertificateRequest(_Model):
        properties: Optional[RawCertificateData]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RawCertificateData] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CheckNameAvailabilityParameters(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ClassicAlertSettings(_Model):
        alerts_for_critical_operations: Optional[Union[str, AlertsState]]
        email_notifications_for_site_recovery: Optional[Union[str, AlertsState]]

        @overload
        def __init__(
                self, 
                *, 
                alerts_for_critical_operations: Optional[Union[str, AlertsState]] = ..., 
                email_notifications_for_site_recovery: Optional[Union[str, AlertsState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ClientDiscoveryDisplay(_Model):
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


    class azure.mgmt.recoveryservices.models.ClientDiscoveryForLogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ClientDiscoveryForProperties(_Model):
        service_specification: Optional[ClientDiscoveryForServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ClientDiscoveryForServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ClientDiscoveryForServiceSpecification(_Model):
        log_specifications: Optional[list[ClientDiscoveryForLogSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[ClientDiscoveryForLogSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ClientDiscoveryValueForSingleApi(_Model):
        display: Optional[ClientDiscoveryDisplay]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[ClientDiscoveryForProperties]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[ClientDiscoveryDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[ClientDiscoveryForProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CloudError(_Model):
        error: Optional[Error]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[Error] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CmkKekIdentity(_Model):
        use_system_assigned_identity: Optional[bool]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                use_system_assigned_identity: Optional[bool] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CmkKeyVaultProperties(_Model):
        key_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CostManagementSettings(_Model):
        granularity_level: Optional[Union[str, GranularityLevel]]

        @overload
        def __init__(
                self, 
                *, 
                granularity_level: Optional[Union[str, GranularityLevel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.recoveryservices.models.CrossRegionRestore(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservices.models.CrossSubscriptionRestoreSettings(_Model):
        cross_subscription_restore_state: Optional[Union[str, CrossSubscriptionRestoreState]]

        @overload
        def __init__(
                self, 
                *, 
                cross_subscription_restore_state: Optional[Union[str, CrossSubscriptionRestoreState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.CrossSubscriptionRestoreState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        PERMANENTLY_DISABLED = "PermanentlyDisabled"


    class azure.mgmt.recoveryservices.models.DNSZone(_Model):
        sub_resource: Optional[Union[str, VaultSubResourceType]]

        @overload
        def __init__(
                self, 
                *, 
                sub_resource: Optional[Union[str, VaultSubResourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.DNSZoneResponse(DNSZone):
        required_zone_names: Optional[list[str]]
        sub_resource: Union[str, VaultSubResourceType]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ..., 
                sub_resource: Optional[Union[str, VaultSubResourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.DeletedVault(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedVaultProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.DeletedVaultProperties(_Model):
        purge_at: Optional[datetime]
        vault_deletion_time: Optional[datetime]
        vault_id: Optional[str]


    class azure.mgmt.recoveryservices.models.DeletedVaultUndeleteInput(_Model):
        properties: DeletedVaultUndeleteInputProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: DeletedVaultUndeleteInputProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.DeletedVaultUndeleteInputProperties(_Model):
        recovery_resource_group_id: str

        @overload
        def __init__(
                self, 
                *, 
                recovery_resource_group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.EnhancedSecurityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS_ON = "AlwaysON"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservices.models.Error(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[Error]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.recoveryservices.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.recoveryservices.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.recoveryservices.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.GranularityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED_ITEM_LEVEL = "ProtectedItemLevel"
        PROTECTED_ITEM_WITH_PARENT_TAG = "ProtectedItemWithParentTag"
        VAULT_LEVEL = "VaultLevel"


    class azure.mgmt.recoveryservices.models.IdentityData(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ResourceIdentityType]
        user_assigned_identities: Optional[dict[str, UserIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ResourceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.recoveryservices.models.ImmutabilityConfiguration(_Model):
        duration_in_days: Optional[int]
        type: Optional[Union[str, ImmutabilityType]]

        @overload
        def __init__(
                self, 
                *, 
                duration_in_days: Optional[int] = ..., 
                type: Optional[Union[str, ImmutabilityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ImmutabilitySettings(_Model):
        configuration: Optional[ImmutabilityConfiguration]
        state: Optional[Union[str, ImmutabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[ImmutabilityConfiguration] = ..., 
                state: Optional[Union[str, ImmutabilityState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ImmutabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


    class azure.mgmt.recoveryservices.models.ImmutabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AS_PER_POLICY = "AsPerPolicy"
        TIME_BASED = "TimeBased"


    class azure.mgmt.recoveryservices.models.InfrastructureEncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservices.models.JobsSummary(_Model):
        failed_jobs: Optional[int]
        in_progress_jobs: Optional[int]
        suspended_jobs: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failed_jobs: Optional[int] = ..., 
                in_progress_jobs: Optional[int] = ..., 
                suspended_jobs: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.MonitoringSettings(_Model):
        azure_monitor_alert_settings: Optional[AzureMonitorAlertSettings]
        classic_alert_settings: Optional[ClassicAlertSettings]

        @overload
        def __init__(
                self, 
                *, 
                azure_monitor_alert_settings: Optional[AzureMonitorAlertSettings] = ..., 
                classic_alert_settings: Optional[ClassicAlertSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.MonitoringSummary(_Model):
        deprecated_provider_count: Optional[int]
        events_count: Optional[int]
        supported_provider_count: Optional[int]
        un_healthy_provider_count: Optional[int]
        un_healthy_vm_count: Optional[int]
        unsupported_provider_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deprecated_provider_count: Optional[int] = ..., 
                events_count: Optional[int] = ..., 
                supported_provider_count: Optional[int] = ..., 
                un_healthy_provider_count: Optional[int] = ..., 
                un_healthy_vm_count: Optional[int] = ..., 
                unsupported_provider_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.MultiUserAuthorization(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservices.models.NameInfo(_Model):
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


    class azure.mgmt.recoveryservices.models.OperationResource(_Model):
        end_time: Optional[datetime]
        error: Optional[Error]
        id: Optional[str]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[Error] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                start_time: Optional[datetime] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.PatchTrackedResource(Resource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.PatchVault(PatchTrackedResource):
        etag: str
        id: str
        identity: Optional[IdentityData]
        location: str
        name: str
        properties: Optional[VaultProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[IdentityData] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[VaultProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.recoveryservices.models.PrivateEndpointConnection(_Model):
        group_ids: Optional[list[Union[str, VaultSubResourceType]]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[Union[str, VaultSubResourceType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.PrivateEndpointConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.recoveryservices.models.PrivateEndpointConnectionVaultProperties(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: Optional[PrivateEndpointConnection]
        type: Optional[str]


    class azure.mgmt.recoveryservices.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.recoveryservices.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.recoveryservices.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointConnectionStatus]]


    class azure.mgmt.recoveryservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.recoveryservices.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.recoveryservices.models.RawCertificateData(_Model):
        auth_type: Optional[Union[str, AuthType]]
        certificate: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                certificate: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ReplicationUsage(_Model):
        jobs_summary: Optional[JobsSummary]
        monitoring_summary: Optional[MonitoringSummary]
        protected_item_count: Optional[int]
        recovery_plan_count: Optional[int]
        recovery_services_provider_auth_type: Optional[int]
        registered_servers_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                jobs_summary: Optional[JobsSummary] = ..., 
                monitoring_summary: Optional[MonitoringSummary] = ..., 
                protected_item_count: Optional[int] = ..., 
                recovery_plan_count: Optional[int] = ..., 
                recovery_services_provider_auth_type: Optional[int] = ..., 
                registered_servers_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.recoveryservices.models.ResourceCapabilities(ResourceCapabilitiesBase):
        properties: Optional[CapabilitiesProperties]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilitiesProperties] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ResourceCapabilitiesBase(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ResourceCertificateAndAadDetails(ResourceCertificateDetails, discriminator='AzureActiveDirectory'):
        aad_audience: Optional[str]
        aad_authority: str
        aad_tenant_id: str
        auth_type: Literal["AzureActiveDirectory"]
        azure_management_endpoint_audience: str
        certificate: bytes
        friendly_name: str
        issuer: str
        resource_id: int
        service_principal_client_id: str
        service_principal_object_id: str
        service_resource_id: Optional[str]
        subject: str
        thumbprint: str
        valid_from: datetime
        valid_to: datetime

        @overload
        def __init__(
                self, 
                *, 
                aad_audience: Optional[str] = ..., 
                aad_authority: str, 
                aad_tenant_id: str, 
                azure_management_endpoint_audience: str, 
                certificate: Optional[bytes] = ..., 
                friendly_name: Optional[str] = ..., 
                issuer: Optional[str] = ..., 
                resource_id: Optional[int] = ..., 
                service_principal_client_id: str, 
                service_principal_object_id: str, 
                service_resource_id: Optional[str] = ..., 
                subject: Optional[str] = ..., 
                thumbprint: Optional[str] = ..., 
                valid_from: Optional[datetime] = ..., 
                valid_to: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ResourceCertificateAndAcsDetails(ResourceCertificateDetails, discriminator='AccessControlService'):
        auth_type: Literal["AccessControlService"]
        certificate: bytes
        friendly_name: str
        global_acs_host_name: str
        global_acs_namespace: str
        global_acs_rp_realm: str
        issuer: str
        resource_id: int
        subject: str
        thumbprint: str
        valid_from: datetime
        valid_to: datetime

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[bytes] = ..., 
                friendly_name: Optional[str] = ..., 
                global_acs_host_name: str, 
                global_acs_namespace: str, 
                global_acs_rp_realm: str, 
                issuer: Optional[str] = ..., 
                resource_id: Optional[int] = ..., 
                subject: Optional[str] = ..., 
                thumbprint: Optional[str] = ..., 
                valid_from: Optional[datetime] = ..., 
                valid_to: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ResourceCertificateDetails(_Model):
        auth_type: str
        certificate: Optional[bytes]
        friendly_name: Optional[str]
        issuer: Optional[str]
        resource_id: Optional[int]
        subject: Optional[str]
        thumbprint: Optional[str]
        valid_from: Optional[datetime]
        valid_to: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: str, 
                certificate: Optional[bytes] = ..., 
                friendly_name: Optional[str] = ..., 
                issuer: Optional[str] = ..., 
                resource_id: Optional[int] = ..., 
                subject: Optional[str] = ..., 
                thumbprint: Optional[str] = ..., 
                valid_from: Optional[datetime] = ..., 
                valid_to: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.recoveryservices.models.ResourceMoveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMIT_FAILED = "CommitFailed"
        COMMIT_TIMEDOUT = "CommitTimedout"
        CRITICAL_FAILURE = "CriticalFailure"
        FAILURE = "Failure"
        IN_PROGRESS = "InProgress"
        MOVE_SUCCEEDED = "MoveSucceeded"
        PARTIAL_SUCCESS = "PartialSuccess"
        PREPARE_FAILED = "PrepareFailed"
        PREPARE_TIMEDOUT = "PrepareTimedout"
        UNKNOWN = "Unknown"


    class azure.mgmt.recoveryservices.models.RestoreSettings(_Model):
        cross_subscription_restore_settings: Optional[CrossSubscriptionRestoreSettings]

        @overload
        def __init__(
                self, 
                *, 
                cross_subscription_restore_settings: Optional[CrossSubscriptionRestoreSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.SecureScoreLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADEQUATE = "Adequate"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"


    class azure.mgmt.recoveryservices.models.SecuritySettings(_Model):
        immutability_settings: Optional[ImmutabilitySettings]
        multi_user_authorization: Optional[Union[str, MultiUserAuthorization]]
        soft_delete_settings: Optional[SoftDeleteSettings]
        source_scan_configuration: Optional[SourceScanConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                immutability_settings: Optional[ImmutabilitySettings] = ..., 
                soft_delete_settings: Optional[SoftDeleteSettings] = ..., 
                source_scan_configuration: Optional[SourceScanConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.Sku(_Model):
        capacity: Optional[str]
        family: Optional[str]
        name: Union[str, SkuName]
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[str] = ..., 
                family: Optional[str] = ..., 
                name: Union[str, SkuName], 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RS0 = "RS0"
        STANDARD = "Standard"


    class azure.mgmt.recoveryservices.models.SoftDeleteSettings(_Model):
        enhanced_security_state: Optional[Union[str, EnhancedSecurityState]]
        soft_delete_retention_period_in_days: Optional[int]
        soft_delete_state: Optional[Union[str, SoftDeleteState]]

        @overload
        def __init__(
                self, 
                *, 
                enhanced_security_state: Optional[Union[str, EnhancedSecurityState]] = ..., 
                soft_delete_retention_period_in_days: Optional[int] = ..., 
                soft_delete_state: Optional[Union[str, SoftDeleteState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.SoftDeleteState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS_ON = "AlwaysON"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservices.models.SourceScanConfiguration(_Model):
        source_scan_identity: Optional[AssociatedIdentity]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                source_scan_identity: Optional[AssociatedIdentity] = ..., 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.StandardTierStorageRedundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_REDUNDANT = "GeoRedundant"
        INVALID = "Invalid"
        LOCALLY_REDUNDANT = "LocallyRedundant"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.recoveryservices.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        INVALID = "Invalid"


    class azure.mgmt.recoveryservices.models.SystemData(_Model):
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


    class azure.mgmt.recoveryservices.models.TrackedResource(Resource):
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


    class azure.mgmt.recoveryservices.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORCED_UPGRADE = "ForcedUpgrade"
        USER_TRIGGERED = "UserTriggered"


    class azure.mgmt.recoveryservices.models.UpgradeDetails(_Model):
        end_time_utc: Optional[datetime]
        last_updated_time_utc: Optional[datetime]
        message: Optional[str]
        operation_id: Optional[str]
        previous_resource_id: Optional[str]
        start_time_utc: Optional[datetime]
        status: Optional[Union[str, VaultUpgradeState]]
        trigger_type: Optional[Union[str, TriggerType]]
        upgraded_resource_id: Optional[str]


    class azure.mgmt.recoveryservices.models.UsagesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.recoveryservices.models.UserIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.recoveryservices.models.Vault(TrackedResource):
        etag: Optional[str]
        id: str
        identity: Optional[IdentityData]
        location: str
        name: str
        properties: Optional[VaultProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[IdentityData] = ..., 
                location: str, 
                properties: Optional[VaultProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultCertificateResponse(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ResourceCertificateDetails]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ResourceCertificateDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultExtendedInfo(_Model):
        algorithm: Optional[str]
        encryption_key: Optional[str]
        encryption_key_thumbprint: Optional[str]
        integrity_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Optional[str] = ..., 
                encryption_key: Optional[str] = ..., 
                encryption_key_thumbprint: Optional[str] = ..., 
                integrity_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultExtendedInfoResource(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[VaultExtendedInfo]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[VaultExtendedInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultPrivateEndpointState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLED = "Enabled"
        NONE = "None"


    class azure.mgmt.recoveryservices.models.VaultProperties(_Model):
        backup_storage_version: Optional[Union[str, BackupStorageVersion]]
        bcdr_security_level: Optional[Union[str, BCDRSecurityLevel]]
        cost_management_settings: Optional[CostManagementSettings]
        encryption: Optional[VaultPropertiesEncryption]
        monitoring_settings: Optional[MonitoringSettings]
        move_details: Optional[VaultPropertiesMoveDetails]
        move_state: Optional[Union[str, ResourceMoveState]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnectionVaultProperties]]
        private_endpoint_state_for_backup: Optional[Union[str, VaultPrivateEndpointState]]
        private_endpoint_state_for_site_recovery: Optional[Union[str, VaultPrivateEndpointState]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        redundancy_settings: Optional[VaultPropertiesRedundancySettings]
        resource_guard_operation_requests: Optional[list[str]]
        restore_settings: Optional[RestoreSettings]
        secure_score: Optional[Union[str, SecureScoreLevel]]
        security_settings: Optional[SecuritySettings]
        upgrade_details: Optional[UpgradeDetails]

        @overload
        def __init__(
                self, 
                *, 
                cost_management_settings: Optional[CostManagementSettings] = ..., 
                encryption: Optional[VaultPropertiesEncryption] = ..., 
                monitoring_settings: Optional[MonitoringSettings] = ..., 
                move_details: Optional[VaultPropertiesMoveDetails] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                redundancy_settings: Optional[VaultPropertiesRedundancySettings] = ..., 
                resource_guard_operation_requests: Optional[list[str]] = ..., 
                restore_settings: Optional[RestoreSettings] = ..., 
                security_settings: Optional[SecuritySettings] = ..., 
                upgrade_details: Optional[UpgradeDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultPropertiesEncryption(_Model):
        infrastructure_encryption: Optional[Union[str, InfrastructureEncryptionState]]
        kek_identity: Optional[CmkKekIdentity]
        key_vault_properties: Optional[CmkKeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                infrastructure_encryption: Optional[Union[str, InfrastructureEncryptionState]] = ..., 
                kek_identity: Optional[CmkKekIdentity] = ..., 
                key_vault_properties: Optional[CmkKeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultPropertiesMoveDetails(_Model):
        completion_time_utc: Optional[datetime]
        operation_id: Optional[str]
        source_resource_id: Optional[str]
        start_time_utc: Optional[datetime]
        target_resource_id: Optional[str]


    class azure.mgmt.recoveryservices.models.VaultPropertiesRedundancySettings(_Model):
        cross_region_restore: Optional[Union[str, CrossRegionRestore]]
        standard_tier_storage_redundancy: Optional[Union[str, StandardTierStorageRedundancy]]

        @overload
        def __init__(
                self, 
                *, 
                cross_region_restore: Optional[Union[str, CrossRegionRestore]] = ..., 
                standard_tier_storage_redundancy: Optional[Union[str, StandardTierStorageRedundancy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.VaultSubResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BACKUP = "AzureBackup"
        AZURE_BACKUP_SECONDARY = "AzureBackup_secondary"
        AZURE_SITE_RECOVERY = "AzureSiteRecovery"


    class azure.mgmt.recoveryservices.models.VaultUpgradeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        UNKNOWN = "Unknown"
        UPGRADED = "Upgraded"


    class azure.mgmt.recoveryservices.models.VaultUsage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        name: Optional[NameInfo]
        next_reset_time: Optional[datetime]
        quota_period: Optional[str]
        unit: Optional[Union[str, UsagesUnit]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[NameInfo] = ..., 
                next_reset_time: Optional[datetime] = ..., 
                quota_period: Optional[str] = ..., 
                unit: Optional[Union[str, UsagesUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.recoveryservices.operations

    class azure.mgmt.recoveryservices.operations.DeletedVaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: DeletedVaultUndeleteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: DeletedVaultUndeleteInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_undelete(
                self, 
                location: str, 
                deleted_vault_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'operation_id', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        def get_operation_status(
                self, 
                location: str, 
                deleted_vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-08-01', '2026-01-01', '2026-02-01', '2026-03-31-preview', '2026-05-01'])
        def list_by_subscription_id(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[DeletedVault]: ...


    class azure.mgmt.recoveryservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ClientDiscoveryValueForSingleApi]: ...


    class azure.mgmt.recoveryservices.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.recoveryservices.operations.RecoveryServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def capabilities(
                self, 
                location: str, 
                input: ResourceCapabilities, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        def capabilities(
                self, 
                location: str, 
                input: ResourceCapabilities, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        def capabilities(
                self, 
                location: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CapabilitiesResponse: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: CheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                location: str, 
                input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...


    class azure.mgmt.recoveryservices.operations.RegisteredIdentitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                identity_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.recoveryservices.operations.ReplicationUsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ReplicationUsage]: ...


    class azure.mgmt.recoveryservices.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_vaults(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VaultUsage]: ...


    class azure.mgmt.recoveryservices.operations.VaultCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: CertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: CertificateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                certificate_name: str, 
                certificate_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultCertificateResponse: ...


    class azure.mgmt.recoveryservices.operations.VaultExtendedInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: VaultExtendedInfoResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                resource_extended_info_details: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultExtendedInfoResource: ...


    class azure.mgmt.recoveryservices.operations.VaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: Vault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: Vault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: PatchVault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: PatchVault, 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                vault: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                x_ms_authorization_auxiliary: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> Vault: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Vault]: ...

        @distributed_trace
        def list_by_subscription_id(self, **kwargs: Any) -> ItemPaged[Vault]: ...


namespace azure.mgmt.recoveryservices.types

    class azure.mgmt.recoveryservices.types.AssociatedIdentity(TypedDict, total=False):
        key "operationIdentityType": Union[str, IdentityType]
        key "userAssignedIdentity": str
        operation_identity_type: Union[str, IdentityType]
        user_assigned_identity: str


    class azure.mgmt.recoveryservices.types.AzureMonitorAlertSettings(TypedDict, total=False):
        key "alertsForAllFailoverIssues": Union[str, AlertsState]
        key "alertsForAllJobFailures": Union[str, AlertsState]
        key "alertsForAllReplicationIssues": Union[str, AlertsState]
        alerts_for_all_failover_issues: Union[str, AlertsState]
        alerts_for_all_job_failures: Union[str, AlertsState]
        alerts_for_all_replication_issues: Union[str, AlertsState]


    class azure.mgmt.recoveryservices.types.CapabilitiesProperties(TypedDict, total=False):
        dnsZones: list[DNSZone]
        dns_zones: list[DNSZone]


    class azure.mgmt.recoveryservices.types.CapabilitiesResponse(ResourceCapabilitiesBase):
        key "properties": ForwardRef('CapabilitiesResponseProperties', module='types')
        key "type": Required[str]
        properties: CapabilitiesResponseProperties
        type: str


    class azure.mgmt.recoveryservices.types.CapabilitiesResponseProperties(TypedDict, total=False):
        dnsZones: list[DNSZoneResponse]
        dns_zones: list[DNSZoneResponse]


    class azure.mgmt.recoveryservices.types.CertificateRequest(TypedDict, total=False):
        key "properties": ForwardRef('RawCertificateData', module='types')
        properties: RawCertificateData


    class azure.mgmt.recoveryservices.types.CheckNameAvailabilityParameters(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.recoveryservices.types.CheckNameAvailabilityResult(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": str
        message: str
        name_available: bool
        reason: str


    class azure.mgmt.recoveryservices.types.ClassicAlertSettings(TypedDict, total=False):
        key "alertsForCriticalOperations": Union[str, AlertsState]
        key "emailNotificationsForSiteRecovery": Union[str, AlertsState]
        alerts_for_critical_operations: Union[str, AlertsState]
        email_notifications_for_site_recovery: Union[str, AlertsState]


    class azure.mgmt.recoveryservices.types.ClientDiscoveryDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.recoveryservices.types.ClientDiscoveryForLogSpecification(TypedDict, total=False):
        key "blobDuration": str
        key "displayName": str
        key "name": str
        blob_duration: str
        display_name: str
        name: str


    class azure.mgmt.recoveryservices.types.ClientDiscoveryForProperties(TypedDict, total=False):
        key "serviceSpecification": ForwardRef('ClientDiscoveryForServiceSpecification', module='types')
        service_specification: ClientDiscoveryForServiceSpecification


    class azure.mgmt.recoveryservices.types.ClientDiscoveryForServiceSpecification(TypedDict, total=False):
        logSpecifications: list[ClientDiscoveryForLogSpecification]
        log_specifications: list[ClientDiscoveryForLogSpecification]


    class azure.mgmt.recoveryservices.types.ClientDiscoveryValueForSingleApi(TypedDict, total=False):
        key "display": ForwardRef('ClientDiscoveryDisplay', module='types')
        key "name": str
        key "origin": str
        key "properties": ForwardRef('ClientDiscoveryForProperties', module='types')
        display: ClientDiscoveryDisplay
        name: str
        origin: str
        properties: ClientDiscoveryForProperties


    class azure.mgmt.recoveryservices.types.CloudError(TypedDict, total=False):
        key "error": ForwardRef('Error', module='types')
        error: Error


    class azure.mgmt.recoveryservices.types.CmkKekIdentity(TypedDict, total=False):
        key "useSystemAssignedIdentity": bool
        key "userAssignedIdentity": str
        use_system_assigned_identity: bool
        user_assigned_identity: str


    class azure.mgmt.recoveryservices.types.CmkKeyVaultProperties(TypedDict, total=False):
        key "keyUri": str
        key_uri: str


    class azure.mgmt.recoveryservices.types.CostManagementSettings(TypedDict, total=False):
        key "granularityLevel": Union[str, GranularityLevel]
        granularity_level: Union[str, GranularityLevel]


    class azure.mgmt.recoveryservices.types.CrossSubscriptionRestoreSettings(TypedDict, total=False):
        key "crossSubscriptionRestoreState": Union[str, CrossSubscriptionRestoreState]
        cross_subscription_restore_state: Union[str, CrossSubscriptionRestoreState]


    class azure.mgmt.recoveryservices.types.DNSZone(TypedDict, total=False):
        key "subResource": Union[str, VaultSubResourceType]
        sub_resource: Union[str, VaultSubResourceType]


    class azure.mgmt.recoveryservices.types.DNSZoneResponse(DNSZone):
        key "subResource": Union[str, VaultSubResourceType]
        requiredZoneNames: list[str]
        required_zone_names: list[str]
        sub_resource: Union[str, VaultSubResourceType]


    class azure.mgmt.recoveryservices.types.DeletedVault(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeletedVaultProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DeletedVaultProperties
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.types.DeletedVaultProperties(TypedDict, total=False):
        key "purgeAt": str
        key "vaultDeletionTime": str
        key "vaultId": str
        purge_at: str
        vault_deletion_time: str
        vault_id: str


    class azure.mgmt.recoveryservices.types.DeletedVaultUndeleteInput(TypedDict, total=False):
        key "properties": Required[DeletedVaultUndeleteInputProperties]
        properties: DeletedVaultUndeleteInputProperties


    class azure.mgmt.recoveryservices.types.DeletedVaultUndeleteInputProperties(TypedDict, total=False):
        key "recoveryResourceGroupId": Required[str]
        recovery_resource_group_id: str


    class azure.mgmt.recoveryservices.types.Error(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[Error]
        message: str
        target: str


    class azure.mgmt.recoveryservices.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.recoveryservices.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.recoveryservices.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.recoveryservices.types.IdentityData(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ResourceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserIdentity]
        user_assigned_identities: dict[str, UserIdentity]


    class azure.mgmt.recoveryservices.types.ImmutabilityConfiguration(TypedDict, total=False):
        key "durationInDays": int
        key "type": Union[str, ImmutabilityType]
        duration_in_days: int
        type: Union[str, ImmutabilityType]


    class azure.mgmt.recoveryservices.types.ImmutabilitySettings(TypedDict, total=False):
        key "configuration": ForwardRef('ImmutabilityConfiguration', module='types')
        key "state": Union[str, ImmutabilityState]
        configuration: ImmutabilityConfiguration
        state: Union[str, ImmutabilityState]


    class azure.mgmt.recoveryservices.types.JobsSummary(TypedDict, total=False):
        key "failedJobs": int
        key "inProgressJobs": int
        key "suspendedJobs": int
        failed_jobs: int
        in_progress_jobs: int
        suspended_jobs: int


    class azure.mgmt.recoveryservices.types.MonitoringSettings(TypedDict, total=False):
        key "azureMonitorAlertSettings": ForwardRef('AzureMonitorAlertSettings', module='types')
        key "classicAlertSettings": ForwardRef('ClassicAlertSettings', module='types')
        azure_monitor_alert_settings: AzureMonitorAlertSettings
        classic_alert_settings: ClassicAlertSettings


    class azure.mgmt.recoveryservices.types.MonitoringSummary(TypedDict, total=False):
        key "deprecatedProviderCount": int
        key "eventsCount": int
        key "supportedProviderCount": int
        key "unHealthyProviderCount": int
        key "unHealthyVmCount": int
        key "unsupportedProviderCount": int
        deprecated_provider_count: int
        events_count: int
        supported_provider_count: int
        un_healthy_provider_count: int
        un_healthy_vm_count: int
        unsupported_provider_count: int


    class azure.mgmt.recoveryservices.types.NameInfo(TypedDict, total=False):
        key "localizedValue": str
        key "value": str
        localized_value: str
        value: str


    class azure.mgmt.recoveryservices.types.OperationResource(TypedDict, total=False):
        key "endTime": str
        key "error": ForwardRef('Error', module='types')
        key "id": str
        key "name": str
        key "startTime": str
        key "status": str
        end_time: str
        error: Error
        id: str
        name: str
        start_time: str
        status: str


    class azure.mgmt.recoveryservices.types.PatchTrackedResource(Resource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservices.types.PatchVault(PatchTrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('IdentityData', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('VaultProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: IdentityData
        location: str
        name: str
        properties: VaultProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservices.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.recoveryservices.types.PrivateEndpointConnection(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        groupIds: list[Union[str, VaultSubResourceType]]
        group_ids: list[Union[str, VaultSubResourceType]]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.recoveryservices.types.PrivateEndpointConnectionVaultProperties(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnection', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PrivateEndpointConnection
        type: str


    class azure.mgmt.recoveryservices.types.PrivateLinkResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.recoveryservices.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointConnectionStatus]
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointConnectionStatus]


    class azure.mgmt.recoveryservices.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.types.RawCertificateData(TypedDict, total=False):
        key "authType": Union[str, AuthType]
        key "certificate": str
        auth_type: Union[str, AuthType]
        certificate: str


    class azure.mgmt.recoveryservices.types.ReplicationUsage(TypedDict, total=False):
        key "jobsSummary": ForwardRef('JobsSummary', module='types')
        key "monitoringSummary": ForwardRef('MonitoringSummary', module='types')
        key "protectedItemCount": int
        key "recoveryPlanCount": int
        key "recoveryServicesProviderAuthType": int
        key "registeredServersCount": int
        jobs_summary: JobsSummary
        monitoring_summary: MonitoringSummary
        protected_item_count: int
        recovery_plan_count: int
        recovery_services_provider_auth_type: int
        registered_servers_count: int


    class azure.mgmt.recoveryservices.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.types.ResourceCapabilities(ResourceCapabilitiesBase):
        key "properties": ForwardRef('CapabilitiesProperties', module='types')
        key "type": Required[str]
        properties: CapabilitiesProperties
        type: str


    class azure.mgmt.recoveryservices.types.ResourceCapabilitiesBase(TypedDict, total=False):
        key "type": Required[str]
        type: str


    class azure.mgmt.recoveryservices.types.ResourceCertificateAndAadDetails(TypedDict, total=False):
        key "aadAudience": str
        key "aadAuthority": Required[str]
        key "aadTenantId": Required[str]
        key "authType": Required[Literal["AzureActiveDirectory"]]
        key "azureManagementEndpointAudience": Required[str]
        key "certificate": str
        key "friendlyName": str
        key "issuer": str
        key "resourceId": int
        key "servicePrincipalClientId": Required[str]
        key "servicePrincipalObjectId": Required[str]
        key "serviceResourceId": str
        key "subject": str
        key "thumbprint": str
        key "validFrom": str
        key "validTo": str
        aad_audience: str
        aad_authority: str
        aad_tenant_id: str
        auth_type: Literal[AzureActiveDirectory]
        azure_management_endpoint_audience: str
        certificate: str
        friendly_name: str
        issuer: str
        resource_id: int
        service_principal_client_id: str
        service_principal_object_id: str
        service_resource_id: str
        subject: str
        thumbprint: str
        valid_from: str
        valid_to: str


    class azure.mgmt.recoveryservices.types.ResourceCertificateAndAcsDetails(TypedDict, total=False):
        key "authType": Required[Literal["AccessControlService"]]
        key "certificate": str
        key "friendlyName": str
        key "globalAcsHostName": Required[str]
        key "globalAcsNamespace": Required[str]
        key "globalAcsRPRealm": Required[str]
        key "issuer": str
        key "resourceId": int
        key "subject": str
        key "thumbprint": str
        key "validFrom": str
        key "validTo": str
        auth_type: Literal[AccessControlService]
        certificate: str
        friendly_name: str
        global_acs_host_name: str
        global_acs_namespace: str
        global_acs_rp_realm: str
        issuer: str
        resource_id: int
        subject: str
        thumbprint: str
        valid_from: str
        valid_to: str


    class azure.mgmt.recoveryservices.types.RestoreSettings(TypedDict, total=False):
        key "crossSubscriptionRestoreSettings": ForwardRef('CrossSubscriptionRestoreSettings', module='types')
        cross_subscription_restore_settings: CrossSubscriptionRestoreSettings


    class azure.mgmt.recoveryservices.types.SecuritySettings(TypedDict, total=False):
        key "immutabilitySettings": ForwardRef('ImmutabilitySettings', module='types')
        key "multiUserAuthorization": Union[str, MultiUserAuthorization]
        key "softDeleteSettings": ForwardRef('SoftDeleteSettings', module='types')
        key "sourceScanConfiguration": ForwardRef('SourceScanConfiguration', module='types')
        immutability_settings: ImmutabilitySettings
        multi_user_authorization: Union[str, MultiUserAuthorization]
        soft_delete_settings: SoftDeleteSettings
        source_scan_configuration: SourceScanConfiguration


    class azure.mgmt.recoveryservices.types.Sku(TypedDict, total=False):
        key "capacity": str
        key "family": str
        key "name": Required[Union[str, SkuName]]
        key "size": str
        key "tier": str
        capacity: str
        family: str
        name: Union[str, SkuName]
        size: str
        tier: str


    class azure.mgmt.recoveryservices.types.SoftDeleteSettings(TypedDict, total=False):
        key "enhancedSecurityState": Union[str, EnhancedSecurityState]
        key "softDeleteRetentionPeriodInDays": int
        key "softDeleteState": Union[str, SoftDeleteState]
        enhanced_security_state: Union[str, EnhancedSecurityState]
        soft_delete_retention_period_in_days: int
        soft_delete_state: Union[str, SoftDeleteState]


    class azure.mgmt.recoveryservices.types.SourceScanConfiguration(TypedDict, total=False):
        key "sourceScanIdentity": ForwardRef('AssociatedIdentity', module='types')
        key "state": Union[str, State]
        source_scan_identity: AssociatedIdentity
        state: Union[str, State]


    class azure.mgmt.recoveryservices.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.recoveryservices.types.TrackedResource(Resource):
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


    class azure.mgmt.recoveryservices.types.UpgradeDetails(TypedDict, total=False):
        key "endTimeUtc": str
        key "lastUpdatedTimeUtc": str
        key "message": str
        key "operationId": str
        key "previousResourceId": str
        key "startTimeUtc": str
        key "status": Union[str, VaultUpgradeState]
        key "triggerType": Union[str, TriggerType]
        key "upgradedResourceId": str
        end_time_utc: str
        last_updated_time_utc: str
        message: str
        operation_id: str
        previous_resource_id: str
        start_time_utc: str
        status: Union[str, VaultUpgradeState]
        trigger_type: Union[str, TriggerType]
        upgraded_resource_id: str


    class azure.mgmt.recoveryservices.types.UserIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.recoveryservices.types.Vault(TrackedResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('IdentityData', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('VaultProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: IdentityData
        location: str
        name: str
        properties: VaultProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.recoveryservices.types.VaultCertificateResponse(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ResourceCertificateDetails', module='types')
        key "type": str
        id: str
        name: str
        properties: ResourceCertificateDetails
        type: str


    class azure.mgmt.recoveryservices.types.VaultExtendedInfo(TypedDict, total=False):
        key "algorithm": str
        key "encryptionKey": str
        key "encryptionKeyThumbprint": str
        key "integrityKey": str
        algorithm: str
        encryption_key: str
        encryption_key_thumbprint: str
        integrity_key: str


    class azure.mgmt.recoveryservices.types.VaultExtendedInfoResource(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('VaultExtendedInfo', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: VaultExtendedInfo
        system_data: SystemData
        type: str


    class azure.mgmt.recoveryservices.types.VaultProperties(TypedDict, total=False):
        key "backupStorageVersion": Union[str, BackupStorageVersion]
        key "bcdrSecurityLevel": Union[str, BCDRSecurityLevel]
        key "costManagementSettings": ForwardRef('CostManagementSettings', module='types')
        key "encryption": ForwardRef('VaultPropertiesEncryption', module='types')
        key "monitoringSettings": ForwardRef('MonitoringSettings', module='types')
        key "moveDetails": ForwardRef('VaultPropertiesMoveDetails', module='types')
        key "moveState": Union[str, ResourceMoveState]
        key "privateEndpointStateForBackup": Union[str, VaultPrivateEndpointState]
        key "privateEndpointStateForSiteRecovery": Union[str, VaultPrivateEndpointState]
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "redundancySettings": ForwardRef('VaultPropertiesRedundancySettings', module='types')
        key "restoreSettings": ForwardRef('RestoreSettings', module='types')
        key "secureScore": Union[str, SecureScoreLevel]
        key "securitySettings": ForwardRef('SecuritySettings', module='types')
        key "upgradeDetails": ForwardRef('UpgradeDetails', module='types')
        backup_storage_version: Union[str, BackupStorageVersion]
        bcdr_security_level: Union[str, BCDRSecurityLevel]
        cost_management_settings: CostManagementSettings
        encryption: VaultPropertiesEncryption
        monitoring_settings: MonitoringSettings
        move_details: VaultPropertiesMoveDetails
        move_state: Union[str, ResourceMoveState]
        privateEndpointConnections: list[PrivateEndpointConnectionVaultProperties]
        private_endpoint_connections: list[PrivateEndpointConnectionVaultProperties]
        private_endpoint_state_for_backup: Union[str, VaultPrivateEndpointState]
        private_endpoint_state_for_site_recovery: Union[str, VaultPrivateEndpointState]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        redundancy_settings: VaultPropertiesRedundancySettings
        resourceGuardOperationRequests: list[str]
        resource_guard_operation_requests: list[str]
        restore_settings: RestoreSettings
        secure_score: Union[str, SecureScoreLevel]
        security_settings: SecuritySettings
        upgrade_details: UpgradeDetails


    class azure.mgmt.recoveryservices.types.VaultPropertiesEncryption(TypedDict, total=False):
        key "infrastructureEncryption": Union[str, InfrastructureEncryptionState]
        key "kekIdentity": ForwardRef('CmkKekIdentity', module='types')
        key "keyVaultProperties": ForwardRef('CmkKeyVaultProperties', module='types')
        infrastructure_encryption: Union[str, InfrastructureEncryptionState]
        kek_identity: CmkKekIdentity
        key_vault_properties: CmkKeyVaultProperties


    class azure.mgmt.recoveryservices.types.VaultPropertiesMoveDetails(TypedDict, total=False):
        key "completionTimeUtc": str
        key "operationId": str
        key "sourceResourceId": str
        key "startTimeUtc": str
        key "targetResourceId": str
        completion_time_utc: str
        operation_id: str
        source_resource_id: str
        start_time_utc: str
        target_resource_id: str


    class azure.mgmt.recoveryservices.types.VaultPropertiesRedundancySettings(TypedDict, total=False):
        key "crossRegionRestore": Union[str, CrossRegionRestore]
        key "standardTierStorageRedundancy": Union[str, StandardTierStorageRedundancy]
        cross_region_restore: Union[str, CrossRegionRestore]
        standard_tier_storage_redundancy: Union[str, StandardTierStorageRedundancy]


    class azure.mgmt.recoveryservices.types.VaultUsage(TypedDict, total=False):
        key "currentValue": int
        key "limit": int
        key "name": ForwardRef('NameInfo', module='types')
        key "nextResetTime": str
        key "quotaPeriod": str
        key "unit": Union[str, UsagesUnit]
        current_value: int
        limit: int
        name: NameInfo
        next_reset_time: str
        quota_period: str
        unit: Union[str, UsagesUnit]


```