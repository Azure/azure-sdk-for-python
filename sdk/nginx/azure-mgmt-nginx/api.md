```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.nginx

    class azure.mgmt.nginx.NginxManagementClient: implements ContextManager 
        api_keys: ApiKeysOperations
        certificates: CertificatesOperations
        configurations: ConfigurationsOperations
        default_waf_policy: DefaultWafPolicyOperations
        deployments: DeploymentsOperations
        nginx_deployment_waf_policies: NginxDeploymentWafPoliciesOperations
        operations: Operations
        waf_policy: WafPolicyOperations

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


namespace azure.mgmt.nginx.aio

    class azure.mgmt.nginx.aio.NginxManagementClient: implements AsyncContextManager 
        api_keys: ApiKeysOperations
        certificates: CertificatesOperations
        configurations: ConfigurationsOperations
        default_waf_policy: DefaultWafPolicyOperations
        deployments: DeploymentsOperations
        nginx_deployment_waf_policies: NginxDeploymentWafPoliciesOperations
        operations: Operations
        waf_policy: WafPolicyOperations

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


namespace azure.mgmt.nginx.aio.operations

    class azure.mgmt.nginx.aio.operations.ApiKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[NginxDeploymentApiKeyRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NginxDeploymentApiKeyResponse]: ...


    class azure.mgmt.nginx.aio.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[NginxCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxCertificate]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxCertificate]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> NginxCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NginxCertificate]: ...


    class azure.mgmt.nginx.aio.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[AnalysisCreate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[NginxConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxConfigurationResponse]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxConfigurationResponse]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxConfigurationResponse]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> NginxConfigurationResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NginxConfigurationResponse]: ...


    class azure.mgmt.nginx.aio.operations.DefaultWafPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentDefaultWafPolicyListResponse: ...


    class azure.mgmt.nginx.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[NginxDeployment] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[NginxDeploymentUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeployment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> NginxDeployment: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[NginxDeployment]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NginxDeployment]: ...


    class azure.mgmt.nginx.aio.operations.NginxDeploymentWafPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[NginxDeploymentWafPolicyAnalysisCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...

        @overload
        async def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...


    class azure.mgmt.nginx.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.nginx.aio.operations.WafPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[NginxDeploymentWafPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeploymentWafPolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeploymentWafPolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NginxDeploymentWafPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NginxDeploymentWafPolicyMetadata]: ...


namespace azure.mgmt.nginx.models

    class azure.mgmt.nginx.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.nginx.models.ActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.nginx.models.AnalysisCreate(_Model):
        config: AnalysisCreateConfig

        @overload
        def __init__(
                self, 
                *, 
                config: AnalysisCreateConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.AnalysisCreateConfig(_Model):
        files: Optional[list[NginxConfigurationFile]]
        package: Optional[NginxConfigurationPackage]
        protected_files: Optional[list[NginxConfigurationProtectedFileRequest]]
        root_file: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[NginxConfigurationFile]] = ..., 
                package: Optional[NginxConfigurationPackage] = ..., 
                protected_files: Optional[list[NginxConfigurationProtectedFileRequest]] = ..., 
                root_file: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.AnalysisDiagnostic(_Model):
        description: str
        directive: str
        file: str
        id: Optional[str]
        line: float
        message: str
        rule: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                directive: str, 
                file: str, 
                id: Optional[str] = ..., 
                line: float, 
                message: str, 
                rule: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.AnalysisResult(_Model):
        data: Optional[AnalysisResultData]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[AnalysisResultData] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.AnalysisResultData(_Model):
        diagnostics: Optional[list[DiagnosticItem]]
        errors: Optional[list[AnalysisDiagnostic]]

        @overload
        def __init__(
                self, 
                *, 
                diagnostics: Optional[list[DiagnosticItem]] = ..., 
                errors: Optional[list[AnalysisDiagnostic]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.AutoUpgradeProfile(_Model):
        upgrade_channel: str

        @overload
        def __init__(
                self, 
                *, 
                upgrade_channel: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.nginx.models.DiagnosticItem(_Model):
        category: Optional[str]
        description: str
        directive: str
        file: str
        id: Optional[str]
        level: Union[str, Level]
        line: float
        message: str
        rule: str

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[str] = ..., 
                description: str, 
                directive: str, 
                file: str, 
                id: Optional[str] = ..., 
                level: Union[str, Level], 
                line: float, 
                message: str, 
                rule: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.nginx.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.nginx.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.IdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, IdentityType]]
        user_assigned_identities: Optional[dict[str, UserIdentityProperties]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserIdentityProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.nginx.models.Level(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INFO = "Info"
        WARNING = "Warning"


    class azure.mgmt.nginx.models.NginxCertificate(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[NginxCertificateProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[NginxCertificateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxCertificateErrorResponseBody(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxCertificateProperties(_Model):
        certificate_error: Optional[NginxCertificateErrorResponseBody]
        certificate_virtual_path: Optional[str]
        key_vault_secret_created: Optional[datetime]
        key_vault_secret_id: Optional[str]
        key_vault_secret_version: Optional[str]
        key_virtual_path: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sha1_thumbprint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_error: Optional[NginxCertificateErrorResponseBody] = ..., 
                certificate_virtual_path: Optional[str] = ..., 
                key_vault_secret_id: Optional[str] = ..., 
                key_virtual_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationFile(_Model):
        content: Optional[str]
        virtual_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                virtual_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationPackage(_Model):
        data: Optional[str]
        protected_files: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[str] = ..., 
                protected_files: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationProtectedFileRequest(_Model):
        content: Optional[str]
        content_hash: Optional[str]
        virtual_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                content_hash: Optional[str] = ..., 
                virtual_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationProtectedFileResponse(_Model):
        content_hash: Optional[str]
        virtual_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_hash: Optional[str] = ..., 
                virtual_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationRequest(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[NginxConfigurationRequestProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxConfigurationRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationRequestProperties(_Model):
        files: Optional[list[NginxConfigurationFile]]
        package: Optional[NginxConfigurationPackage]
        protected_files: Optional[list[NginxConfigurationProtectedFileRequest]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        root_file: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[NginxConfigurationFile]] = ..., 
                package: Optional[NginxConfigurationPackage] = ..., 
                protected_files: Optional[list[NginxConfigurationProtectedFileRequest]] = ..., 
                root_file: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationResponse(ProxyResource):
        id: str
        name: str
        properties: Optional[NginxConfigurationResponseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxConfigurationResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxConfigurationResponseProperties(_Model):
        files: Optional[list[NginxConfigurationFile]]
        package: Optional[NginxConfigurationPackage]
        protected_files: Optional[list[NginxConfigurationProtectedFileResponse]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        root_file: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                files: Optional[list[NginxConfigurationFile]] = ..., 
                package: Optional[NginxConfigurationPackage] = ..., 
                protected_files: Optional[list[NginxConfigurationProtectedFileResponse]] = ..., 
                root_file: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeployment(TrackedResource):
        id: str
        identity: Optional[IdentityProperties]
        location: str
        name: str
        properties: Optional[NginxDeploymentProperties]
        sku: Optional[ResourceSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: str, 
                properties: Optional[NginxDeploymentProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentApiKeyRequest(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[NginxDeploymentApiKeyRequestProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxDeploymentApiKeyRequestProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentApiKeyRequestProperties(_Model):
        end_date_time: Optional[datetime]
        secret_text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_date_time: Optional[datetime] = ..., 
                secret_text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentApiKeyResponse(ProxyResource):
        id: str
        name: str
        properties: Optional[NginxDeploymentApiKeyResponseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxDeploymentApiKeyResponseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentApiKeyResponseProperties(_Model):
        end_date_time: Optional[datetime]
        hint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentDefaultWafPolicyListResponse(_Model):
        next_link: Optional[str]
        value: Optional[list[NginxDeploymentDefaultWafPolicyProperties]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[NginxDeploymentDefaultWafPolicyProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentDefaultWafPolicyProperties(_Model):
        content: Optional[bytes]
        filepath: Optional[str]


    class azure.mgmt.nginx.models.NginxDeploymentProperties(_Model):
        auto_upgrade_profile: Optional[AutoUpgradeProfile]
        dataplane_api_endpoint: Optional[str]
        enable_diagnostics_support: Optional[bool]
        ip_address: Optional[str]
        logging: Optional[NginxLogging]
        network_profile: Optional[NginxNetworkProfile]
        nginx_app_protect: Optional[NginxDeploymentPropertiesNginxAppProtect]
        nginx_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scaling_properties: Optional[NginxDeploymentScalingProperties]
        user_profile: Optional[NginxDeploymentUserProfile]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_profile: Optional[AutoUpgradeProfile] = ..., 
                enable_diagnostics_support: Optional[bool] = ..., 
                logging: Optional[NginxLogging] = ..., 
                network_profile: Optional[NginxNetworkProfile] = ..., 
                nginx_app_protect: Optional[NginxDeploymentPropertiesNginxAppProtect] = ..., 
                scaling_properties: Optional[NginxDeploymentScalingProperties] = ..., 
                user_profile: Optional[NginxDeploymentUserProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentPropertiesNginxAppProtect(_Model):
        web_application_firewall_settings: WebApplicationFirewallSettings
        web_application_firewall_status: Optional[WebApplicationFirewallStatus]

        @overload
        def __init__(
                self, 
                *, 
                web_application_firewall_settings: WebApplicationFirewallSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentScalingProperties(_Model):
        auto_scale_settings: Optional[NginxDeploymentScalingPropertiesAutoScaleSettings]
        capacity: Optional[int]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_settings: Optional[NginxDeploymentScalingPropertiesAutoScaleSettings] = ..., 
                capacity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentScalingPropertiesAutoScaleSettings(_Model):
        profiles: list[ScaleProfile]

        @overload
        def __init__(
                self, 
                *, 
                profiles: list[ScaleProfile]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentUpdateParameters(_Model):
        identity: Optional[IdentityProperties]
        location: Optional[str]
        properties: Optional[NginxDeploymentUpdateProperties]
        sku: Optional[ResourceSku]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[IdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[NginxDeploymentUpdateProperties] = ..., 
                sku: Optional[ResourceSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentUpdateProperties(_Model):
        auto_upgrade_profile: Optional[AutoUpgradeProfile]
        enable_diagnostics_support: Optional[bool]
        logging: Optional[NginxLogging]
        network_profile: Optional[NginxNetworkProfile]
        nginx_app_protect: Optional[NginxDeploymentUpdatePropertiesNginxAppProtect]
        scaling_properties: Optional[NginxDeploymentScalingProperties]
        user_profile: Optional[NginxDeploymentUserProfile]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_profile: Optional[AutoUpgradeProfile] = ..., 
                enable_diagnostics_support: Optional[bool] = ..., 
                logging: Optional[NginxLogging] = ..., 
                network_profile: Optional[NginxNetworkProfile] = ..., 
                nginx_app_protect: Optional[NginxDeploymentUpdatePropertiesNginxAppProtect] = ..., 
                scaling_properties: Optional[NginxDeploymentScalingProperties] = ..., 
                user_profile: Optional[NginxDeploymentUserProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentUpdatePropertiesNginxAppProtect(_Model):
        web_application_firewall_settings: Optional[WebApplicationFirewallSettings]

        @overload
        def __init__(
                self, 
                *, 
                web_application_firewall_settings: Optional[WebApplicationFirewallSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentUserProfile(_Model):
        preferred_email: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                preferred_email: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[NginxDeploymentWafPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxDeploymentWafPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyAnalysisCreateRequest(_Model):
        content: Optional[bytes]
        filepath: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[bytes] = ..., 
                filepath: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyAnalysisData(_Model):
        errors: Optional[list[NginxDeploymentWafPolicyError]]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[NginxDeploymentWafPolicyError]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyAnalysisResponse(_Model):
        data: Optional[NginxDeploymentWafPolicyAnalysisData]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[NginxDeploymentWafPolicyAnalysisData] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyApplyingStatus(_Model):
        code: Optional[Union[str, NginxDeploymentWafPolicyApplyingStatusCode]]
        display_status: Optional[str]
        time: Optional[str]


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyApplyingStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLYING = "Applying"
        FAILED = "Failed"
        NOT_APPLIED = "NotApplied"
        REMOVING = "Removing"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyCompilingStatus(_Model):
        code: Optional[Union[str, NginxDeploymentWafPolicyCompilingStatusCode]]
        display_status: Optional[str]
        time: Optional[str]


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyCompilingStatusCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyError(_Model):
        code: Optional[str]
        field: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                field: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyMetadata(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[NginxDeploymentWafPolicyMetadataProperties]
        system_data: Optional[SystemData]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NginxDeploymentWafPolicyMetadataProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyMetadataProperties(_Model):
        applying_state: Optional[NginxDeploymentWafPolicyApplyingStatus]
        compiling_state: Optional[NginxDeploymentWafPolicyCompilingStatus]
        filepath: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.nginx.models.NginxDeploymentWafPolicyProperties(_Model):
        applying_state: Optional[NginxDeploymentWafPolicyApplyingStatus]
        compiling_state: Optional[NginxDeploymentWafPolicyCompilingStatus]
        content: Optional[bytes]
        filepath: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[bytes] = ..., 
                filepath: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxFrontendIPConfiguration(_Model):
        private_ip_addresses: Optional[list[NginxPrivateIPAddress]]
        public_ip_addresses: Optional[list[NginxPublicIPAddress]]

        @overload
        def __init__(
                self, 
                *, 
                private_ip_addresses: Optional[list[NginxPrivateIPAddress]] = ..., 
                public_ip_addresses: Optional[list[NginxPublicIPAddress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxLogging(_Model):
        storage_account: Optional[NginxStorageAccount]

        @overload
        def __init__(
                self, 
                *, 
                storage_account: Optional[NginxStorageAccount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxNetworkInterfaceConfiguration(_Model):
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxNetworkProfile(_Model):
        front_end_ip_configuration: Optional[NginxFrontendIPConfiguration]
        network_interface_configuration: Optional[NginxNetworkInterfaceConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                front_end_ip_configuration: Optional[NginxFrontendIPConfiguration] = ..., 
                network_interface_configuration: Optional[NginxNetworkInterfaceConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxPrivateIPAddress(_Model):
        private_ip_address: Optional[str]
        private_ip_allocation_method: Optional[Union[str, NginxPrivateIPAllocationMethod]]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_ip_address: Optional[str] = ..., 
                private_ip_allocation_method: Optional[Union[str, NginxPrivateIPAllocationMethod]] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxPrivateIPAllocationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC = "Dynamic"
        STATIC = "Static"


    class azure.mgmt.nginx.models.NginxPublicIPAddress(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.NginxStorageAccount(_Model):
        account_name: Optional[str]
        container_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                container_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.Operation(_Model):
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


    class azure.mgmt.nginx.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.nginx.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.nginx.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.nginx.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.nginx.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.nginx.models.ResourceSku(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.ScaleProfile(_Model):
        capacity: ScaleProfileCapacity
        name: str

        @overload
        def __init__(
                self, 
                *, 
                capacity: ScaleProfileCapacity, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.ScaleProfileCapacity(_Model):
        max: int
        min: int

        @overload
        def __init__(
                self, 
                *, 
                max: int, 
                min: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.SystemData(_Model):
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


    class azure.mgmt.nginx.models.TrackedResource(Resource):
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


    class azure.mgmt.nginx.models.UserIdentityProperties(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.nginx.models.WebApplicationFirewallComponentVersions(_Model):
        waf_engine_version: str
        waf_nginx_version: str

        @overload
        def __init__(
                self, 
                *, 
                waf_engine_version: str, 
                waf_nginx_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.WebApplicationFirewallPackage(_Model):
        revision_datetime: datetime
        version: str

        @overload
        def __init__(
                self, 
                *, 
                revision_datetime: datetime, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.WebApplicationFirewallSettings(_Model):
        activation_state: Optional[Union[str, ActivationState]]

        @overload
        def __init__(
                self, 
                *, 
                activation_state: Optional[Union[str, ActivationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.nginx.models.WebApplicationFirewallStatus(_Model):
        attack_signatures_package: Optional[WebApplicationFirewallPackage]
        bot_signatures_package: Optional[WebApplicationFirewallPackage]
        component_versions: Optional[WebApplicationFirewallComponentVersions]
        threat_campaigns_package: Optional[WebApplicationFirewallPackage]
        waf_release: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                waf_release: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.nginx.operations

    class azure.mgmt.nginx.operations.ApiKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[NginxDeploymentApiKeyRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                api_key_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentApiKeyResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NginxDeploymentApiKeyResponse]: ...


    class azure.mgmt.nginx.operations.CertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[NginxCertificate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxCertificate]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxCertificate]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                certificate_name: str, 
                **kwargs: Any
            ) -> NginxCertificate: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NginxCertificate]: ...


    class azure.mgmt.nginx.operations.ConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[AnalysisCreate] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalysisResult: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[NginxConfigurationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxConfigurationResponse]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxConfigurationResponse]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxConfigurationResponse]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> NginxConfigurationResponse: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NginxConfigurationResponse]: ...


    class azure.mgmt.nginx.operations.DefaultWafPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentDefaultWafPolicyListResponse: ...


    class azure.mgmt.nginx.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[NginxDeployment] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[NginxDeploymentUpdateParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeployment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> NginxDeployment: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[NginxDeployment]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NginxDeployment]: ...


    class azure.mgmt.nginx.operations.NginxDeploymentWafPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[NginxDeploymentWafPolicyAnalysisCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...

        @overload
        def analysis(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicyAnalysisResponse: ...


    class azure.mgmt.nginx.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.nginx.operations.WafPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[NginxDeploymentWafPolicy] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeploymentWafPolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeploymentWafPolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NginxDeploymentWafPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                waf_policy_name: str, 
                **kwargs: Any
            ) -> NginxDeploymentWafPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NginxDeploymentWafPolicyMetadata]: ...


```