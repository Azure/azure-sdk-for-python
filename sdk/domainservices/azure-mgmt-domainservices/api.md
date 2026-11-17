```py
namespace azure.mgmt.domainservices

    class azure.mgmt.domainservices.DomainServicesMgmtClient: implements ContextManager 
        domain_service_operations: DomainServiceOperationsOperations
        domain_services: DomainServicesOperations
        ou_container: OuContainerOperations

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


namespace azure.mgmt.domainservices.aio

    class azure.mgmt.domainservices.aio.DomainServicesMgmtClient: implements AsyncContextManager 
        domain_service_operations: DomainServiceOperationsOperations
        domain_services: DomainServicesOperations
        ou_container: OuContainerOperations

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


namespace azure.mgmt.domainservices.aio.operations

    class azure.mgmt.domainservices.aio.operations.DomainServiceOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationEntity]: ...


    class azure.mgmt.domainservices.aio.operations.DomainServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DomainService]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> DomainService: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DomainService]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DomainService]: ...

        @distributed_trace_async
        async def unsuspend(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> UnsuspendDomainServiceResponse: ...


    class azure.mgmt.domainservices.aio.operations.OuContainerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OuContainer]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                **kwargs: Any
            ) -> OuContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OuContainer]: ...


namespace azure.mgmt.domainservices.models

    class azure.mgmt.domainservices.models.ChannelBinding(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.CloudErrorBody(_Model):
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


    class azure.mgmt.domainservices.models.ConfigDiagnostics(_Model):
        last_executed: Optional[datetime]
        validator_results: Optional[list[ConfigDiagnosticsValidatorResult]]

        @overload
        def __init__(
                self, 
                *, 
                last_executed: Optional[datetime] = ..., 
                validator_results: Optional[list[ConfigDiagnosticsValidatorResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.ConfigDiagnosticsValidatorResult(_Model):
        issues: Optional[list[ConfigDiagnosticsValidatorResultIssue]]
        replica_set_subnet_display_name: Optional[str]
        status: Optional[Union[str, Status]]
        validator_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                issues: Optional[list[ConfigDiagnosticsValidatorResultIssue]] = ..., 
                replica_set_subnet_display_name: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                validator_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.ConfigDiagnosticsValidatorResultIssue(_Model):
        description_params: Optional[list[str]]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description_params: Optional[list[str]] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.ContainerAccount(_Model):
        account_name: Optional[str]
        password: Optional[str]
        spn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                spn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.domainservices.models.DomainSecuritySettings(_Model):
        channel_binding: Optional[Union[str, ChannelBinding]]
        kerberos_armoring: Optional[Union[str, KerberosArmoring]]
        kerberos_rc4_encryption: Optional[Union[str, KerberosRc4Encryption]]
        ldap_signing: Optional[Union[str, LdapSigning]]
        ntlm_v1: Optional[Union[str, NtlmV1]]
        sync_kerberos_passwords: Optional[Union[str, SyncKerberosPasswords]]
        sync_ntlm_passwords: Optional[Union[str, SyncNtlmPasswords]]
        sync_on_prem_passwords: Optional[Union[str, SyncOnPremPasswords]]
        sync_on_prem_sam_account_name: Optional[Union[str, SyncOnPremSamAccountName]]
        tls_v1: Optional[Union[str, TlsV1]]

        @overload
        def __init__(
                self, 
                *, 
                channel_binding: Optional[Union[str, ChannelBinding]] = ..., 
                kerberos_armoring: Optional[Union[str, KerberosArmoring]] = ..., 
                kerberos_rc4_encryption: Optional[Union[str, KerberosRc4Encryption]] = ..., 
                ldap_signing: Optional[Union[str, LdapSigning]] = ..., 
                ntlm_v1: Optional[Union[str, NtlmV1]] = ..., 
                sync_kerberos_passwords: Optional[Union[str, SyncKerberosPasswords]] = ..., 
                sync_ntlm_passwords: Optional[Union[str, SyncNtlmPasswords]] = ..., 
                sync_on_prem_passwords: Optional[Union[str, SyncOnPremPasswords]] = ..., 
                sync_on_prem_sam_account_name: Optional[Union[str, SyncOnPremSamAccountName]] = ..., 
                tls_v1: Optional[Union[str, TlsV1]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.DomainService(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[DomainServiceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DomainServiceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainservices.models.DomainServiceProperties(_Model):
        config_diagnostics: Optional[ConfigDiagnostics]
        deployment_id: Optional[str]
        domain_configuration_type: Optional[str]
        domain_name: Optional[str]
        domain_security_settings: Optional[DomainSecuritySettings]
        filtered_sync: Optional[Union[str, FilteredSync]]
        ldaps_settings: Optional[LdapsSettings]
        migration_properties: Optional[MigrationProperties]
        notification_settings: Optional[NotificationSettings]
        provisioning_state: Optional[str]
        replica_sets: Optional[list[ReplicaSet]]
        resource_forest_settings: Optional[ResourceForestSettings]
        sku: Optional[str]
        sync_application_id: Optional[str]
        sync_owner: Optional[str]
        sync_scope: Optional[Union[str, SyncScope]]
        tenant_id: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                config_diagnostics: Optional[ConfigDiagnostics] = ..., 
                domain_configuration_type: Optional[str] = ..., 
                domain_name: Optional[str] = ..., 
                domain_security_settings: Optional[DomainSecuritySettings] = ..., 
                filtered_sync: Optional[Union[str, FilteredSync]] = ..., 
                ldaps_settings: Optional[LdapsSettings] = ..., 
                notification_settings: Optional[NotificationSettings] = ..., 
                replica_sets: Optional[list[ReplicaSet]] = ..., 
                resource_forest_settings: Optional[ResourceForestSettings] = ..., 
                sku: Optional[str] = ..., 
                sync_scope: Optional[Union[str, SyncScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.ExternalAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.FilteredSync(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.ForestTrust(_Model):
        friendly_name: Optional[str]
        remote_dns_ips: Optional[str]
        trust_direction: Optional[str]
        trust_password: Optional[str]
        trusted_domain_fqdn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                friendly_name: Optional[str] = ..., 
                remote_dns_ips: Optional[str] = ..., 
                trust_direction: Optional[str] = ..., 
                trust_password: Optional[str] = ..., 
                trusted_domain_fqdn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.HealthAlert(_Model):
        id: Optional[str]
        issue: Optional[str]
        last_detected: Optional[datetime]
        name: Optional[str]
        raised: Optional[datetime]
        resolution_uri: Optional[str]
        severity: Optional[str]


    class azure.mgmt.domainservices.models.HealthMonitor(_Model):
        details: Optional[str]
        id: Optional[str]
        name: Optional[str]


    class azure.mgmt.domainservices.models.KerberosArmoring(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.KerberosRc4Encryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.LdapSigning(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.Ldaps(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.LdapsSettings(_Model):
        certificate_not_after: Optional[datetime]
        certificate_thumbprint: Optional[str]
        external_access: Optional[Union[str, ExternalAccess]]
        ldaps: Optional[Union[str, Ldaps]]
        pfx_certificate: Optional[str]
        pfx_certificate_password: Optional[str]
        public_certificate: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                external_access: Optional[Union[str, ExternalAccess]] = ..., 
                ldaps: Optional[Union[str, Ldaps]] = ..., 
                pfx_certificate: Optional[str] = ..., 
                pfx_certificate_password: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.MigrationProgress(_Model):
        completion_percentage: Optional[float]
        progress_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                completion_percentage: Optional[float] = ..., 
                progress_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.MigrationProperties(_Model):
        migration_progress: Optional[MigrationProgress]
        old_subnet_id: Optional[str]
        old_vnet_site_id: Optional[str]


    class azure.mgmt.domainservices.models.NotificationSettings(_Model):
        additional_recipients: Optional[list[str]]
        notify_dc_admins: Optional[Union[str, NotifyDcAdmins]]
        notify_global_admins: Optional[Union[str, NotifyGlobalAdmins]]

        @overload
        def __init__(
                self, 
                *, 
                additional_recipients: Optional[list[str]] = ..., 
                notify_dc_admins: Optional[Union[str, NotifyDcAdmins]] = ..., 
                notify_global_admins: Optional[Union[str, NotifyGlobalAdmins]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.NotifyDcAdmins(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.NotifyGlobalAdmins(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.NtlmV1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.OperationDisplayInfo(_Model):
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


    class azure.mgmt.domainservices.models.OperationEntity(_Model):
        display: Optional[OperationDisplayInfo]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplayInfo] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.OuContainer(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[OuContainerProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[OuContainerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.domainservices.models.OuContainerProperties(_Model):
        accounts: Optional[list[ContainerAccount]]
        container_id: Optional[str]
        deployment_id: Optional[str]
        distinguished_name: Optional[str]
        domain_name: Optional[str]
        provisioning_state: Optional[str]
        service_status: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accounts: Optional[list[ContainerAccount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.domainservices.models.ReplicaSet(_Model):
        domain_controller_ip_address: Optional[list[str]]
        external_access_ip_address: Optional[str]
        health_alerts: Optional[list[HealthAlert]]
        health_last_evaluated: Optional[datetime]
        health_monitors: Optional[list[HealthMonitor]]
        location: Optional[str]
        replica_set_id: Optional[str]
        self_unsuspend_counter: Optional[int]
        service_status: Optional[str]
        subnet_id: Optional[str]
        vnet_site_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.domainservices.models.ResourceForestSettings(_Model):
        resource_forest: Optional[str]
        settings: Optional[list[ForestTrust]]

        @overload
        def __init__(
                self, 
                *, 
                resource_forest: Optional[str] = ..., 
                settings: Optional[list[ForestTrust]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.domainservices.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "Failure"
        NONE = "None"
        OK = "OK"
        RUNNING = "Running"
        SKIPPED = "Skipped"
        WARNING = "Warning"


    class azure.mgmt.domainservices.models.SyncKerberosPasswords(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.SyncNtlmPasswords(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.SyncOnPremPasswords(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.SyncOnPremSamAccountName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.SyncScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CLOUD_ONLY = "CloudOnly"


    class azure.mgmt.domainservices.models.SystemData(_Model):
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


    class azure.mgmt.domainservices.models.TlsV1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.domainservices.models.UnsuspendDomainServiceResponse(_Model):
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.domainservices.operations

    class azure.mgmt.domainservices.operations.DomainServiceOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationEntity]: ...


    class azure.mgmt.domainservices.operations.DomainServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: DomainService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                domain_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DomainService]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> DomainService: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DomainService]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DomainService]: ...

        @distributed_trace
        def unsuspend(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> UnsuspendDomainServiceResponse: ...


    class azure.mgmt.domainservices.operations.OuContainerOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: ContainerAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                container_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OuContainer]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                ou_container_name: str, 
                **kwargs: Any
            ) -> OuContainer: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                domain_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OuContainer]: ...


namespace azure.mgmt.domainservices.types

    class azure.mgmt.domainservices.types.ConfigDiagnostics(TypedDict, total=False):
        key "lastExecuted": str
        last_executed: str
        validatorResults: list[ConfigDiagnosticsValidatorResult]
        validator_results: list[ConfigDiagnosticsValidatorResult]


    class azure.mgmt.domainservices.types.ConfigDiagnosticsValidatorResult(TypedDict, total=False):
        key "replicaSetSubnetDisplayName": str
        key "status": Union[str, Status]
        key "validatorId": str
        issues: list[ConfigDiagnosticsValidatorResultIssue]
        replica_set_subnet_display_name: str
        status: Union[str, Status]
        validator_id: str


    class azure.mgmt.domainservices.types.ConfigDiagnosticsValidatorResultIssue(TypedDict, total=False):
        key "id": str
        descriptionParams: list[str]
        description_params: list[str]
        id: str


    class azure.mgmt.domainservices.types.ContainerAccount(TypedDict, total=False):
        key "accountName": str
        key "password": str
        key "spn": str
        account_name: str
        password: str
        spn: str


    class azure.mgmt.domainservices.types.DomainSecuritySettings(TypedDict, total=False):
        key "channelBinding": Union[str, ChannelBinding]
        key "kerberosArmoring": Union[str, KerberosArmoring]
        key "kerberosRc4Encryption": Union[str, KerberosRc4Encryption]
        key "ldapSigning": Union[str, LdapSigning]
        key "ntlmV1": Union[str, NtlmV1]
        key "syncKerberosPasswords": Union[str, SyncKerberosPasswords]
        key "syncNtlmPasswords": Union[str, SyncNtlmPasswords]
        key "syncOnPremPasswords": Union[str, SyncOnPremPasswords]
        key "syncOnPremSamAccountName": Union[str, SyncOnPremSamAccountName]
        key "tlsV1": Union[str, TlsV1]
        channel_binding: Union[str, ChannelBinding]
        kerberos_armoring: Union[str, KerberosArmoring]
        kerberos_rc4_encryption: Union[str, KerberosRc4Encryption]
        ldap_signing: Union[str, LdapSigning]
        ntlm_v1: Union[str, NtlmV1]
        sync_kerberos_passwords: Union[str, SyncKerberosPasswords]
        sync_ntlm_passwords: Union[str, SyncNtlmPasswords]
        sync_on_prem_passwords: Union[str, SyncOnPremPasswords]
        sync_on_prem_sam_account_name: Union[str, SyncOnPremSamAccountName]
        tls_v1: Union[str, TlsV1]


    class azure.mgmt.domainservices.types.DomainService(ProxyResource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('DomainServiceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: DomainServiceProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.domainservices.types.DomainServiceProperties(TypedDict, total=False):
        key "configDiagnostics": ForwardRef('ConfigDiagnostics', module='types')
        key "deploymentId": str
        key "domainConfigurationType": str
        key "domainName": str
        key "domainSecuritySettings": ForwardRef('DomainSecuritySettings', module='types')
        key "filteredSync": Union[str, FilteredSync]
        key "ldapsSettings": ForwardRef('LdapsSettings', module='types')
        key "migrationProperties": ForwardRef('MigrationProperties', module='types')
        key "notificationSettings": ForwardRef('NotificationSettings', module='types')
        key "provisioningState": str
        key "resourceForestSettings": ForwardRef('ResourceForestSettings', module='types')
        key "sku": str
        key "syncApplicationId": str
        key "syncOwner": str
        key "syncScope": Union[str, SyncScope]
        key "tenantId": str
        key "version": int
        config_diagnostics: ConfigDiagnostics
        deployment_id: str
        domain_configuration_type: str
        domain_name: str
        domain_security_settings: DomainSecuritySettings
        filtered_sync: Union[str, FilteredSync]
        ldaps_settings: LdapsSettings
        migration_properties: MigrationProperties
        notification_settings: NotificationSettings
        provisioning_state: str
        replicaSets: list[ReplicaSet]
        replica_sets: list[ReplicaSet]
        resource_forest_settings: ResourceForestSettings
        sku: str
        sync_application_id: str
        sync_owner: str
        sync_scope: Union[str, SyncScope]
        tenant_id: str
        version: int


    class azure.mgmt.domainservices.types.ForestTrust(TypedDict, total=False):
        key "friendlyName": str
        key "remoteDnsIps": str
        key "trustDirection": str
        key "trustPassword": str
        key "trustedDomainFqdn": str
        friendly_name: str
        remote_dns_ips: str
        trust_direction: str
        trust_password: str
        trusted_domain_fqdn: str


    class azure.mgmt.domainservices.types.HealthAlert(TypedDict, total=False):
        key "id": str
        key "issue": str
        key "lastDetected": str
        key "name": str
        key "raised": str
        key "resolutionUri": str
        key "severity": str
        id: str
        issue: str
        last_detected: str
        name: str
        raised: str
        resolution_uri: str
        severity: str


    class azure.mgmt.domainservices.types.HealthMonitor(TypedDict, total=False):
        key "details": str
        key "id": str
        key "name": str
        details: str
        id: str
        name: str


    class azure.mgmt.domainservices.types.LdapsSettings(TypedDict, total=False):
        key "certificateNotAfter": str
        key "certificateThumbprint": str
        key "externalAccess": Union[str, ExternalAccess]
        key "ldaps": Union[str, Ldaps]
        key "pfxCertificate": str
        key "pfxCertificatePassword": str
        key "publicCertificate": str
        certificate_not_after: str
        certificate_thumbprint: str
        external_access: Union[str, ExternalAccess]
        ldaps: Union[str, Ldaps]
        pfx_certificate: str
        pfx_certificate_password: str
        public_certificate: str


    class azure.mgmt.domainservices.types.MigrationProgress(TypedDict, total=False):
        key "completionPercentage": float
        key "progressMessage": str
        completion_percentage: float
        progress_message: str


    class azure.mgmt.domainservices.types.MigrationProperties(TypedDict, total=False):
        key "migrationProgress": ForwardRef('MigrationProgress', module='types')
        key "oldSubnetId": str
        key "oldVnetSiteId": str
        migration_progress: MigrationProgress
        old_subnet_id: str
        old_vnet_site_id: str


    class azure.mgmt.domainservices.types.NotificationSettings(TypedDict, total=False):
        key "notifyDcAdmins": Union[str, NotifyDcAdmins]
        key "notifyGlobalAdmins": Union[str, NotifyGlobalAdmins]
        additionalRecipients: list[str]
        additional_recipients: list[str]
        notify_dc_admins: Union[str, NotifyDcAdmins]
        notify_global_admins: Union[str, NotifyGlobalAdmins]


    class azure.mgmt.domainservices.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.domainservices.types.ReplicaSet(TypedDict, total=False):
        key "externalAccessIpAddress": str
        key "healthLastEvaluated": str
        key "location": str
        key "replicaSetId": str
        key "selfUnsuspendCounter": int
        key "serviceStatus": str
        key "subnetId": str
        key "vnetSiteId": str
        domainControllerIpAddress: list[str]
        domain_controller_ip_address: list[str]
        external_access_ip_address: str
        healthAlerts: list[HealthAlert]
        healthMonitors: list[HealthMonitor]
        health_alerts: list[HealthAlert]
        health_last_evaluated: str
        health_monitors: list[HealthMonitor]
        location: str
        replica_set_id: str
        self_unsuspend_counter: int
        service_status: str
        subnet_id: str
        vnet_site_id: str


    class azure.mgmt.domainservices.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.domainservices.types.ResourceForestSettings(TypedDict, total=False):
        key "resourceForest": str
        resource_forest: str
        settings: list[ForestTrust]


    class azure.mgmt.domainservices.types.SystemData(TypedDict, total=False):
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


```