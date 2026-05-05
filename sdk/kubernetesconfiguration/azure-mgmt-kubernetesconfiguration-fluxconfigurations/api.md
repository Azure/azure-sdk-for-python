```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.kubernetesconfiguration.fluxconfigurations

    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.KubernetesConfigurationFluxConfigurationsMgmtClient: implements ContextManager 
        flux_config_operation_status: FluxConfigOperationStatusOperations
        flux_configurations: FluxConfigurationsOperations

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


namespace azure.mgmt.kubernetesconfiguration.fluxconfigurations.aio

    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.aio.KubernetesConfigurationFluxConfigurationsMgmtClient: implements AsyncContextManager 
        flux_config_operation_status: FluxConfigOperationStatusOperations
        flux_configurations: FluxConfigurationsOperations

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


namespace azure.mgmt.kubernetesconfiguration.fluxconfigurations.aio.operations

    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.aio.operations.FluxConfigOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.aio.operations.FluxConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: FluxConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: FluxConfigurationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FluxConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                **kwargs: Any
            ) -> FluxConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FluxConfiguration]: ...


namespace azure.mgmt.kubernetesconfiguration.fluxconfigurations.models

    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.AzureBlobDefinition(_Model):
        account_key: Optional[str]
        container_name: Optional[str]
        local_auth_ref: Optional[str]
        managed_identity: Optional[ManagedIdentityDefinition]
        sas_token: Optional[str]
        service_principal: Optional[ServicePrincipalDefinition]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                local_auth_ref: Optional[str] = ..., 
                managed_identity: Optional[ManagedIdentityDefinition] = ..., 
                sas_token: Optional[str] = ..., 
                service_principal: Optional[ServicePrincipalDefinition] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.AzureBlobPatchDefinition(_Model):
        account_key: Optional[str]
        container_name: Optional[str]
        local_auth_ref: Optional[str]
        managed_identity: Optional[ManagedIdentityPatchDefinition]
        sas_token: Optional[str]
        service_principal: Optional[ServicePrincipalPatchDefinition]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                container_name: Optional[str] = ..., 
                local_auth_ref: Optional[str] = ..., 
                managed_identity: Optional[ManagedIdentityPatchDefinition] = ..., 
                sas_token: Optional[str] = ..., 
                service_principal: Optional[ServicePrincipalPatchDefinition] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.BucketDefinition(_Model):
        access_key: Optional[str]
        bucket_name: Optional[str]
        insecure: Optional[bool]
        local_auth_ref: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_key: Optional[str] = ..., 
                bucket_name: Optional[str] = ..., 
                insecure: Optional[bool] = ..., 
                local_auth_ref: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.BucketPatchDefinition(_Model):
        access_key: Optional[str]
        bucket_name: Optional[str]
        insecure: Optional[bool]
        local_auth_ref: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_key: Optional[str] = ..., 
                bucket_name: Optional[str] = ..., 
                insecure: Optional[bool] = ..., 
                local_auth_ref: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.FluxComplianceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        NON_COMPLIANT = "Non-Compliant"
        PENDING = "Pending"
        SUSPENDED = "Suspended"
        UNKNOWN = "Unknown"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.FluxConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[FluxConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FluxConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.FluxConfigurationPatch(_Model):
        properties: Optional[FluxConfigurationPatchProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FluxConfigurationPatchProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.FluxConfigurationPatchProperties(_Model):
        azure_blob: Optional[AzureBlobPatchDefinition]
        bucket: Optional[BucketPatchDefinition]
        configuration_protected_settings: Optional[dict[str, str]]
        git_repository: Optional[GitRepositoryPatchDefinition]
        kustomizations: Optional[dict[str, KustomizationPatchDefinition]]
        oci_repository: Optional[OCIRepositoryPatchDefinition]
        source_kind: Optional[Union[str, SourceKindType]]
        suspend: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob: Optional[AzureBlobPatchDefinition] = ..., 
                bucket: Optional[BucketPatchDefinition] = ..., 
                configuration_protected_settings: Optional[dict[str, str]] = ..., 
                git_repository: Optional[GitRepositoryPatchDefinition] = ..., 
                kustomizations: Optional[dict[str, KustomizationPatchDefinition]] = ..., 
                oci_repository: Optional[OCIRepositoryPatchDefinition] = ..., 
                source_kind: Optional[Union[str, SourceKindType]] = ..., 
                suspend: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.FluxConfigurationProperties(_Model):
        azure_blob: Optional[AzureBlobDefinition]
        bucket: Optional[BucketDefinition]
        compliance_state: Optional[Union[str, FluxComplianceState]]
        configuration_protected_settings: Optional[dict[str, str]]
        error_message: Optional[str]
        git_repository: Optional[GitRepositoryDefinition]
        kustomizations: Optional[dict[str, KustomizationDefinition]]
        namespace: Optional[str]
        oci_repository: Optional[OCIRepositoryDefinition]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        reconciliation_wait_duration: Optional[str]
        repository_public_key: Optional[str]
        scope: Optional[Union[str, ScopeType]]
        source_kind: Optional[Union[str, SourceKindType]]
        source_synced_commit_id: Optional[str]
        source_updated_at: Optional[datetime]
        status_updated_at: Optional[datetime]
        statuses: Optional[list[ObjectStatusDefinition]]
        suspend: Optional[bool]
        wait_for_reconciliation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                azure_blob: Optional[AzureBlobDefinition] = ..., 
                bucket: Optional[BucketDefinition] = ..., 
                configuration_protected_settings: Optional[dict[str, str]] = ..., 
                git_repository: Optional[GitRepositoryDefinition] = ..., 
                kustomizations: Optional[dict[str, KustomizationDefinition]] = ..., 
                namespace: Optional[str] = ..., 
                oci_repository: Optional[OCIRepositoryDefinition] = ..., 
                reconciliation_wait_duration: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                source_kind: Optional[Union[str, SourceKindType]] = ..., 
                suspend: Optional[bool] = ..., 
                wait_for_reconciliation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.GitRepositoryDefinition(_Model):
        https_ca_cert: Optional[str]
        https_user: Optional[str]
        local_auth_ref: Optional[str]
        provider: Optional[Union[str, ProviderType]]
        repository_ref: Optional[RepositoryRefDefinition]
        ssh_known_hosts: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                https_ca_cert: Optional[str] = ..., 
                https_user: Optional[str] = ..., 
                local_auth_ref: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderType]] = ..., 
                repository_ref: Optional[RepositoryRefDefinition] = ..., 
                ssh_known_hosts: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.GitRepositoryPatchDefinition(_Model):
        https_ca_cert: Optional[str]
        https_user: Optional[str]
        local_auth_ref: Optional[str]
        provider: Optional[Union[str, ProviderType]]
        repository_ref: Optional[RepositoryRefDefinition]
        ssh_known_hosts: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                https_ca_cert: Optional[str] = ..., 
                https_user: Optional[str] = ..., 
                local_auth_ref: Optional[str] = ..., 
                provider: Optional[Union[str, ProviderType]] = ..., 
                repository_ref: Optional[RepositoryRefDefinition] = ..., 
                ssh_known_hosts: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.HelmReleasePropertiesDefinition(_Model):
        failure_count: Optional[int]
        helm_chart_ref: Optional[ObjectReferenceDefinition]
        install_failure_count: Optional[int]
        last_revision_applied: Optional[int]
        upgrade_failure_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                failure_count: Optional[int] = ..., 
                helm_chart_ref: Optional[ObjectReferenceDefinition] = ..., 
                install_failure_count: Optional[int] = ..., 
                last_revision_applied: Optional[int] = ..., 
                upgrade_failure_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.KustomizationDefinition(_Model):
        depends_on: Optional[list[str]]
        force: Optional[bool]
        name: Optional[str]
        path: Optional[str]
        post_build: Optional[PostBuildDefinition]
        prune: Optional[bool]
        retry_interval_in_seconds: Optional[int]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        wait: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                depends_on: Optional[list[str]] = ..., 
                force: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                post_build: Optional[PostBuildDefinition] = ..., 
                prune: Optional[bool] = ..., 
                retry_interval_in_seconds: Optional[int] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                wait: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.KustomizationPatchDefinition(_Model):
        depends_on: Optional[list[str]]
        force: Optional[bool]
        path: Optional[str]
        post_build: Optional[PostBuildPatchDefinition]
        prune: Optional[bool]
        retry_interval_in_seconds: Optional[int]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        wait: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                depends_on: Optional[list[str]] = ..., 
                force: Optional[bool] = ..., 
                path: Optional[str] = ..., 
                post_build: Optional[PostBuildPatchDefinition] = ..., 
                prune: Optional[bool] = ..., 
                retry_interval_in_seconds: Optional[int] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                wait: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.LayerSelectorDefinition(_Model):
        media_type: Optional[str]
        operation: Optional[Union[str, OperationType]]

        @overload
        def __init__(
                self, 
                *, 
                media_type: Optional[str] = ..., 
                operation: Optional[Union[str, OperationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.LayerSelectorPatchDefinition(_Model):
        media_type: Optional[str]
        operation: Optional[Union[str, OperationType]]

        @overload
        def __init__(
                self, 
                *, 
                media_type: Optional[str] = ..., 
                operation: Optional[Union[str, OperationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ManagedIdentityDefinition(_Model):
        client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ManagedIdentityPatchDefinition(_Model):
        client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.MatchOidcIdentityDefinition(_Model):
        issuer: Optional[str]
        subject: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                issuer: Optional[str] = ..., 
                subject: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.MatchOidcIdentityPatchDefinition(_Model):
        issuer: Optional[str]
        subject: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                issuer: Optional[str] = ..., 
                subject: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OCIRepositoryDefinition(_Model):
        insecure: Optional[bool]
        layer_selector: Optional[LayerSelectorDefinition]
        local_auth_ref: Optional[str]
        repository_ref: Optional[OCIRepositoryRefDefinition]
        service_account_name: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        tls_config: Optional[TlsConfigDefinition]
        url: Optional[str]
        use_workload_identity: Optional[bool]
        verify: Optional[VerifyDefinition]

        @overload
        def __init__(
                self, 
                *, 
                insecure: Optional[bool] = ..., 
                layer_selector: Optional[LayerSelectorDefinition] = ..., 
                local_auth_ref: Optional[str] = ..., 
                repository_ref: Optional[OCIRepositoryRefDefinition] = ..., 
                service_account_name: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                tls_config: Optional[TlsConfigDefinition] = ..., 
                url: Optional[str] = ..., 
                use_workload_identity: Optional[bool] = ..., 
                verify: Optional[VerifyDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OCIRepositoryPatchDefinition(_Model):
        insecure: Optional[bool]
        layer_selector: Optional[LayerSelectorPatchDefinition]
        local_auth_ref: Optional[str]
        repository_ref: Optional[OCIRepositoryRefPatchDefinition]
        service_account_name: Optional[str]
        sync_interval_in_seconds: Optional[int]
        timeout_in_seconds: Optional[int]
        tls_config: Optional[TlsConfigPatchDefinition]
        url: Optional[str]
        use_workload_identity: Optional[bool]
        verify: Optional[VerifyPatchDefinition]

        @overload
        def __init__(
                self, 
                *, 
                insecure: Optional[bool] = ..., 
                layer_selector: Optional[LayerSelectorPatchDefinition] = ..., 
                local_auth_ref: Optional[str] = ..., 
                repository_ref: Optional[OCIRepositoryRefPatchDefinition] = ..., 
                service_account_name: Optional[str] = ..., 
                sync_interval_in_seconds: Optional[int] = ..., 
                timeout_in_seconds: Optional[int] = ..., 
                tls_config: Optional[TlsConfigPatchDefinition] = ..., 
                url: Optional[str] = ..., 
                use_workload_identity: Optional[bool] = ..., 
                verify: Optional[VerifyPatchDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OCIRepositoryRefDefinition(_Model):
        digest: Optional[str]
        semver: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                semver: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OCIRepositoryRefPatchDefinition(_Model):
        digest: Optional[str]
        semver: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[str] = ..., 
                semver: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ObjectReferenceDefinition(_Model):
        name: Optional[str]
        namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ObjectStatusConditionDefinition(_Model):
        last_transition_time: Optional[datetime]
        message: Optional[str]
        reason: Optional[str]
        status: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_transition_time: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                status: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ObjectStatusDefinition(_Model):
        applied_by: Optional[ObjectReferenceDefinition]
        compliance_state: Optional[Union[str, FluxComplianceState]]
        helm_release_properties: Optional[HelmReleasePropertiesDefinition]
        kind: Optional[str]
        name: Optional[str]
        namespace: Optional[str]
        status_conditions: Optional[list[ObjectStatusConditionDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                applied_by: Optional[ObjectReferenceDefinition] = ..., 
                compliance_state: Optional[Union[str, FluxComplianceState]] = ..., 
                helm_release_properties: Optional[HelmReleasePropertiesDefinition] = ..., 
                kind: Optional[str] = ..., 
                name: Optional[str] = ..., 
                namespace: Optional[str] = ..., 
                status_conditions: Optional[list[ObjectStatusConditionDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OperationStatusResult(_Model):
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[dict[str, str]]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.OperationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPY = "copy"
        EXTRACT = "extract"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.PostBuildDefinition(_Model):
        substitute: Optional[dict[str, str]]
        substitute_from: Optional[list[SubstituteFromDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                substitute: Optional[dict[str, str]] = ..., 
                substitute_from: Optional[list[SubstituteFromDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.PostBuildPatchDefinition(_Model):
        substitute: Optional[dict[str, str]]
        substitute_from: Optional[list[SubstituteFromPatchDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                substitute: Optional[dict[str, str]] = ..., 
                substitute_from: Optional[list[SubstituteFromPatchDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        GENERIC = "Generic"
        GIT_HUB = "GitHub"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.RepositoryRefDefinition(_Model):
        branch: Optional[str]
        commit: Optional[str]
        semver: Optional[str]
        tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                commit: Optional[str] = ..., 
                semver: Optional[str] = ..., 
                tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "cluster"
        NAMESPACE = "namespace"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ServicePrincipalDefinition(_Model):
        client_certificate: Optional[str]
        client_certificate_password: Optional[str]
        client_certificate_send_chain: Optional[bool]
        client_id: Optional[str]
        client_secret: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_certificate: Optional[str] = ..., 
                client_certificate_password: Optional[str] = ..., 
                client_certificate_send_chain: Optional[bool] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.ServicePrincipalPatchDefinition(_Model):
        client_certificate: Optional[str]
        client_certificate_password: Optional[str]
        client_certificate_send_chain: Optional[bool]
        client_id: Optional[str]
        client_secret: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_certificate: Optional[str] = ..., 
                client_certificate_password: Optional[str] = ..., 
                client_certificate_send_chain: Optional[bool] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.SourceKindType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"
        BUCKET = "Bucket"
        GIT_REPOSITORY = "GitRepository"
        OCI_REPOSITORY = "OCIRepository"


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.SubstituteFromDefinition(_Model):
        kind: Optional[str]
        name: Optional[str]
        optional: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                name: Optional[str] = ..., 
                optional: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.SubstituteFromPatchDefinition(_Model):
        kind: Optional[str]
        name: Optional[str]
        optional: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                name: Optional[str] = ..., 
                optional: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.SystemData(_Model):
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


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.TlsConfigDefinition(_Model):
        ca_certificate: Optional[str]
        client_certificate: Optional[str]
        private_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ca_certificate: Optional[str] = ..., 
                client_certificate: Optional[str] = ..., 
                private_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.TlsConfigPatchDefinition(_Model):
        ca_certificate: Optional[str]
        client_certificate: Optional[str]
        private_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                ca_certificate: Optional[str] = ..., 
                client_certificate: Optional[str] = ..., 
                private_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.VerifyDefinition(_Model):
        match_oidc_identity: Optional[list[MatchOidcIdentityDefinition]]
        provider: Optional[str]
        verification_config: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                match_oidc_identity: Optional[list[MatchOidcIdentityDefinition]] = ..., 
                provider: Optional[str] = ..., 
                verification_config: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.models.VerifyPatchDefinition(_Model):
        match_oidc_identity: Optional[list[MatchOidcIdentityPatchDefinition]]
        provider: Optional[str]
        verification_config: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                match_oidc_identity: Optional[list[MatchOidcIdentityPatchDefinition]] = ..., 
                provider: Optional[str] = ..., 
                verification_config: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.kubernetesconfiguration.fluxconfigurations.operations

    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.operations.FluxConfigOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.kubernetesconfiguration.fluxconfigurations.operations.FluxConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: FluxConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: FluxConfigurationPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                flux_configuration_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FluxConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                flux_configuration_name: str, 
                **kwargs: Any
            ) -> FluxConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FluxConfiguration]: ...


```