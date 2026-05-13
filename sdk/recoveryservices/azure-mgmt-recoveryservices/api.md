```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                body: JSON, 
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
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-08-01'])
        async def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'operation_id', 'accept']}, api_versions_list=['2025-08-01'])
        async def get_operation_status(
                self, 
                location: str, 
                deleted_vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-08-01'])
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
                input: JSON, 
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
                input: JSON, 
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
                certificate_request: JSON, 
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
                resource_extended_info_details: JSON, 
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
                resource_extended_info_details: JSON, 
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
                vault: JSON, 
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
                vault: JSON, 
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


    class azure.mgmt.recoveryservices.models.ImmutabilitySettings(_Model):
        state: Optional[Union[str, ImmutabilityState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, ImmutabilityState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.recoveryservices.models.ImmutabilityState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        LOCKED = "Locked"
        UNLOCKED = "Unlocked"


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
                body: JSON, 
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
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'accept']}, api_versions_list=['2025-08-01'])
        def get(
                self, 
                location: str, 
                deleted_vault_name: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'deleted_vault_name', 'operation_id', 'accept']}, api_versions_list=['2025-08-01'])
        def get_operation_status(
                self, 
                location: str, 
                deleted_vault_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-01', params_added_on={'2025-08-01': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2025-08-01'])
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
                input: JSON, 
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
                input: JSON, 
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
                certificate_request: JSON, 
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
                resource_extended_info_details: JSON, 
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
                resource_extended_info_details: JSON, 
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
                vault: JSON, 
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
                vault: JSON, 
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


```