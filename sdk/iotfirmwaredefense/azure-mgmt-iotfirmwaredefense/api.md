```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.iotfirmwaredefense

    class azure.mgmt.iotfirmwaredefense.IoTFirmwareDefenseMgmtClient: implements ContextManager 
        binary_hardening: BinaryHardeningOperations
        crypto_certificates: CryptoCertificatesOperations
        crypto_keys: CryptoKeysOperations
        cves: CvesOperations
        firmwares: FirmwaresOperations
        operations: Operations
        password_hashes: PasswordHashesOperations
        sbom_components: SbomComponentsOperations
        summaries: SummariesOperations
        usage_metrics: UsageMetricsOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.iotfirmwaredefense.aio

    class azure.mgmt.iotfirmwaredefense.aio.IoTFirmwareDefenseMgmtClient: implements AsyncContextManager 
        binary_hardening: BinaryHardeningOperations
        crypto_certificates: CryptoCertificatesOperations
        crypto_keys: CryptoKeysOperations
        cves: CvesOperations
        firmwares: FirmwaresOperations
        operations: Operations
        password_hashes: PasswordHashesOperations
        sbom_components: SbomComponentsOperations
        summaries: SummariesOperations
        usage_metrics: UsageMetricsOperations
        workspaces: WorkspacesOperations

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


namespace azure.mgmt.iotfirmwaredefense.aio.operations

    class azure.mgmt.iotfirmwaredefense.aio.operations.BinaryHardeningOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[BinaryHardeningResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.CryptoCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CryptoCertificateResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.CryptoKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CryptoKeyResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.CvesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-02', params_added_on={'2025-08-02': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'firmware_id', 'accept']}, api_versions_list=['2025-08-02'])
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CveResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.FirmwaresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: Firmware, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> Firmware: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Firmware]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: FirmwareUpdateDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.PasswordHashesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PasswordHashResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.SbomComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SbomComponentResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.SummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                summary_type: Union[str, SummaryType], 
                **kwargs: Any
            ) -> SummaryResource: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SummaryResource]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.UsageMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                **kwargs: Any
            ) -> UsageMetric: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UsageMetric]: ...


    class azure.mgmt.iotfirmwaredefense.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-08-02', params_added_on={'2025-08-02': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2025-08-02'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: GenerateUploadUrlRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @overload
        async def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @overload
        async def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Workspace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.iotfirmwaredefense.models

    class azure.mgmt.iotfirmwaredefense.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.iotfirmwaredefense.models.BinaryHardeningFeatures(_Model):
        canary: Optional[bool]
        no_execute: Optional[bool]
        position_independent_executable: Optional[bool]
        relocation_read_only: Optional[bool]
        stripped: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                canary: Optional[bool] = ..., 
                no_execute: Optional[bool] = ..., 
                position_independent_executable: Optional[bool] = ..., 
                relocation_read_only: Optional[bool] = ..., 
                stripped: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.BinaryHardeningResource(ProxyResource):
        id: str
        name: str
        properties: Optional[BinaryHardeningResult]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BinaryHardeningResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.BinaryHardeningResult(_Model):
        binary_hardening_id: Optional[str]
        executable_architecture: Optional[str]
        executable_class: Optional[Union[str, ExecutableClass]]
        file_path: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rpath: Optional[str]
        runpath: Optional[str]
        security_hardening_features: Optional[BinaryHardeningFeatures]

        @overload
        def __init__(
                self, 
                *, 
                binary_hardening_id: Optional[str] = ..., 
                executable_architecture: Optional[str] = ..., 
                executable_class: Optional[Union[str, ExecutableClass]] = ..., 
                file_path: Optional[str] = ..., 
                rpath: Optional[str] = ..., 
                runpath: Optional[str] = ..., 
                security_hardening_features: Optional[BinaryHardeningFeatures] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.BinaryHardeningSummaryResource(SummaryResourceProperties, discriminator='BinaryHardening'):
        not_executable_stack_count: Optional[int]
        position_independent_executable_count: Optional[int]
        provisioning_state: Union[str, ProvisioningState]
        relocation_read_only_count: Optional[int]
        stack_canary_count: Optional[int]
        stripped_binary_count: Optional[int]
        summary_type: Literal[SummaryType.BINARY_HARDENING]
        total_files: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                not_executable_stack_count: Optional[int] = ..., 
                position_independent_executable_count: Optional[int] = ..., 
                relocation_read_only_count: Optional[int] = ..., 
                stack_canary_count: Optional[int] = ..., 
                stripped_binary_count: Optional[int] = ..., 
                total_files: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CertificateUsage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_AUTHENTICATION = "clientAuth"
        CODE_SIGNING = "codeSigning"
        CONTENT_COMMITMENT = "contentCommitment"
        CRL_SIGN = "crlSign"
        DATA_ENCIPHERMENT = "dataEncipherment"
        DECIPHER_ONLY = "decipherOnly"
        DIGITAL_SIGNATURE = "digitalSignature"
        EMAIL_PROTECTION = "emailProtection"
        ENCIPHER_ONLY = "encipherOnly"
        KEY_AGREEMENT = "keyAgreement"
        KEY_CERT_SIGN = "keyCertSign"
        KEY_ENCIPHERMENT = "keyEncipherment"
        NON_REPUDIATION = "nonRepudiation"
        OCSP_SIGNING = "ocspSigning"
        SERVER_AUTHENTICATION = "serverAuth"
        TIME_STAMPING = "timeStamping"


    class azure.mgmt.iotfirmwaredefense.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.iotfirmwaredefense.models.CryptoCertificate(_Model):
        certificate_key_algorithm: Optional[str]
        certificate_key_size: Optional[int]
        certificate_name: Optional[str]
        certificate_role: Optional[str]
        certificate_usage: Optional[List[Union[str, CertificateUsage]]]
        crypto_cert_id: Optional[str]
        encoding: Optional[str]
        expiration_date: Optional[datetime]
        file_paths: Optional[List[str]]
        fingerprint: Optional[str]
        is_expired: Optional[bool]
        is_self_signed: Optional[bool]
        is_short_key_size: Optional[bool]
        is_weak_signature: Optional[bool]
        issued_date: Optional[datetime]
        issuer: Optional[CryptoCertificateEntity]
        paired_key: Optional[PairedKey]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]
        signature_algorithm: Optional[str]
        subject: Optional[CryptoCertificateEntity]

        @overload
        def __init__(
                self, 
                *, 
                certificate_key_algorithm: Optional[str] = ..., 
                certificate_key_size: Optional[int] = ..., 
                certificate_name: Optional[str] = ..., 
                certificate_role: Optional[str] = ..., 
                certificate_usage: Optional[List[Union[str, CertificateUsage]]] = ..., 
                crypto_cert_id: Optional[str] = ..., 
                encoding: Optional[str] = ..., 
                expiration_date: Optional[datetime] = ..., 
                fingerprint: Optional[str] = ..., 
                is_expired: Optional[bool] = ..., 
                is_self_signed: Optional[bool] = ..., 
                is_short_key_size: Optional[bool] = ..., 
                is_weak_signature: Optional[bool] = ..., 
                issued_date: Optional[datetime] = ..., 
                issuer: Optional[CryptoCertificateEntity] = ..., 
                paired_key: Optional[PairedKey] = ..., 
                serial_number: Optional[str] = ..., 
                signature_algorithm: Optional[str] = ..., 
                subject: Optional[CryptoCertificateEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoCertificateEntity(_Model):
        common_name: Optional[str]
        country: Optional[str]
        organization: Optional[str]
        organizational_unit: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                common_name: Optional[str] = ..., 
                country: Optional[str] = ..., 
                organization: Optional[str] = ..., 
                organizational_unit: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoCertificateResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CryptoCertificate]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CryptoCertificate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoCertificateSummaryResource(SummaryResourceProperties, discriminator='CryptoCertificate'):
        expired_certificate_count: Optional[int]
        expiring_soon_certificate_count: Optional[int]
        paired_key_count: Optional[int]
        provisioning_state: Union[str, ProvisioningState]
        self_signed_certificate_count: Optional[int]
        short_key_size_count: Optional[int]
        summary_type: Literal[SummaryType.CRYPTO_CERTIFICATE]
        total_certificate_count: Optional[int]
        weak_signature_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                expired_certificate_count: Optional[int] = ..., 
                expiring_soon_certificate_count: Optional[int] = ..., 
                paired_key_count: Optional[int] = ..., 
                self_signed_certificate_count: Optional[int] = ..., 
                short_key_size_count: Optional[int] = ..., 
                total_certificate_count: Optional[int] = ..., 
                weak_signature_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoKey(_Model):
        crypto_key_id: Optional[str]
        crypto_key_size: Optional[int]
        file_paths: Optional[List[str]]
        is_short_key_size: Optional[bool]
        key_algorithm: Optional[str]
        key_type: Optional[Union[str, CryptoKeyType]]
        paired_key: Optional[PairedKey]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        usage: Optional[List[str]]

        @overload
        def __init__(
                self, 
                *, 
                crypto_key_id: Optional[str] = ..., 
                crypto_key_size: Optional[int] = ..., 
                is_short_key_size: Optional[bool] = ..., 
                key_algorithm: Optional[str] = ..., 
                key_type: Optional[Union[str, CryptoKeyType]] = ..., 
                paired_key: Optional[PairedKey] = ..., 
                usage: Optional[List[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoKeyResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CryptoKey]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CryptoKey] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoKeySummaryResource(SummaryResourceProperties, discriminator='CryptoKey'):
        paired_key_count: Optional[int]
        private_key_count: Optional[int]
        provisioning_state: Union[str, ProvisioningState]
        public_key_count: Optional[int]
        short_key_size_count: Optional[int]
        summary_type: Literal[SummaryType.CRYPTO_KEY]
        total_key_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                paired_key_count: Optional[int] = ..., 
                private_key_count: Optional[int] = ..., 
                public_key_count: Optional[int] = ..., 
                short_key_size_count: Optional[int] = ..., 
                total_key_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CryptoKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.iotfirmwaredefense.models.CveComponent(_Model):
        component_id: Optional[str]
        name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CveLink(_Model):
        href: Optional[str]
        label: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                href: Optional[str] = ..., 
                label: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CveResource(ProxyResource):
        id: str
        name: str
        properties: Optional[CveResult]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CveResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CveResult(_Model):
        component: Optional[CveComponent]
        component_id: Optional[str]
        component_name: Optional[str]
        component_version: Optional[str]
        cve_id: Optional[str]
        cve_name: Optional[str]
        cvss_score: Optional[str]
        cvss_scores: Optional[List[CvssScore]]
        cvss_v2_score: Optional[str]
        cvss_v3_score: Optional[str]
        cvss_version: Optional[str]
        description: Optional[str]
        effective_cvss_score: Optional[float]
        effective_cvss_version: Optional[int]
        links: Optional[List[CveLink]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        severity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component: Optional[CveComponent] = ..., 
                component_id: Optional[str] = ..., 
                component_name: Optional[str] = ..., 
                component_version: Optional[str] = ..., 
                cve_id: Optional[str] = ..., 
                cve_name: Optional[str] = ..., 
                cvss_score: Optional[str] = ..., 
                cvss_scores: Optional[List[CvssScore]] = ..., 
                cvss_v2_score: Optional[str] = ..., 
                cvss_v3_score: Optional[str] = ..., 
                cvss_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                effective_cvss_score: Optional[float] = ..., 
                effective_cvss_version: Optional[int] = ..., 
                severity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CveSummary(SummaryResourceProperties, discriminator='CommonVulnerabilitiesAndExposures'):
        critical_cve_count: Optional[int]
        high_cve_count: Optional[int]
        low_cve_count: Optional[int]
        medium_cve_count: Optional[int]
        provisioning_state: Union[str, ProvisioningState]
        summary_type: Literal[SummaryType.COMMON_VULNERABILITIES_AND_EXPOSURES]
        unknown_cve_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                critical_cve_count: Optional[int] = ..., 
                high_cve_count: Optional[int] = ..., 
                low_cve_count: Optional[int] = ..., 
                medium_cve_count: Optional[int] = ..., 
                unknown_cve_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.CvssScore(_Model):
        score: Optional[float]
        version: int

        @overload
        def __init__(
                self, 
                *, 
                score: Optional[float] = ..., 
                version: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.iotfirmwaredefense.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.iotfirmwaredefense.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.ExecutableClass(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        X64 = "x64"
        X86 = "x86"


    class azure.mgmt.iotfirmwaredefense.models.Firmware(ProxyResource):
        id: str
        name: str
        properties: Optional[FirmwareProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FirmwareProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.FirmwareProperties(_Model):
        description: Optional[str]
        file_name: Optional[str]
        file_size: Optional[int]
        model: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[Union[str, Status]]
        status_messages: Optional[List[StatusMessage]]
        vendor: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                file_size: Optional[int] = ..., 
                model: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                status_messages: Optional[List[StatusMessage]] = ..., 
                vendor: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.FirmwareSummary(SummaryResourceProperties, discriminator='Firmware'):
        analysis_time_seconds: Optional[int]
        binary_count: Optional[int]
        component_count: Optional[int]
        extracted_file_count: Optional[int]
        extracted_size: Optional[int]
        file_size: Optional[int]
        provisioning_state: Union[str, ProvisioningState]
        root_file_systems: Optional[int]
        summary_type: Literal[SummaryType.FIRMWARE]

        @overload
        def __init__(
                self, 
                *, 
                analysis_time_seconds: Optional[int] = ..., 
                binary_count: Optional[int] = ..., 
                component_count: Optional[int] = ..., 
                extracted_file_count: Optional[int] = ..., 
                extracted_size: Optional[int] = ..., 
                file_size: Optional[int] = ..., 
                root_file_systems: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.FirmwareUpdateDefinition(_Model):
        properties: Optional[FirmwareProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FirmwareProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.GenerateUploadUrlRequest(_Model):
        firmware_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                firmware_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.Operation(_Model):
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


    class azure.mgmt.iotfirmwaredefense.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.iotfirmwaredefense.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.iotfirmwaredefense.models.PairedKey(_Model):
        paired_key_id: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                paired_key_id: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.PasswordHash(_Model):
        algorithm: Optional[str]
        context: Optional[str]
        file_path: Optional[str]
        hash: Optional[str]
        password_hash_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        salt: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Optional[str] = ..., 
                context: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                hash: Optional[str] = ..., 
                password_hash_id: Optional[str] = ..., 
                salt: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.PasswordHashResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PasswordHash]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PasswordHash] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYZING = "Analyzing"
        CANCELED = "Canceled"
        EXTRACTING = "Extracting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.iotfirmwaredefense.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.iotfirmwaredefense.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.iotfirmwaredefense.models.SbomComponent(_Model):
        component_id: Optional[str]
        component_name: Optional[str]
        file_paths: Optional[List[str]]
        license: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                component_name: Optional[str] = ..., 
                file_paths: Optional[List[str]] = ..., 
                license: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.SbomComponentResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SbomComponent]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SbomComponent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.Sku(_Model):
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


    class azure.mgmt.iotfirmwaredefense.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.iotfirmwaredefense.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANALYZING = "Analyzing"
        ERROR = "Error"
        EXTRACTING = "Extracting"
        PENDING = "Pending"
        READY = "Ready"


    class azure.mgmt.iotfirmwaredefense.models.StatusMessage(_Model):
        error_code: Optional[int]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[int] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.SummaryResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SummaryResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SummaryResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.SummaryResourceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        summary_type: str

        @overload
        def __init__(
                self, 
                *, 
                summary_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.SummaryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BINARY_HARDENING = "BinaryHardening"
        COMMON_VULNERABILITIES_AND_EXPOSURES = "CommonVulnerabilitiesAndExposures"
        CRYPTO_CERTIFICATE = "CryptoCertificate"
        CRYPTO_KEY = "CryptoKey"
        FIRMWARE = "Firmware"


    class azure.mgmt.iotfirmwaredefense.models.SystemData(_Model):
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


    class azure.mgmt.iotfirmwaredefense.models.TrackedResource(Resource):
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


    class azure.mgmt.iotfirmwaredefense.models.UrlToken(_Model):
        url: Optional[str]


    class azure.mgmt.iotfirmwaredefense.models.UsageMetric(ProxyResource):
        id: str
        name: str
        properties: Optional[UsageMetricProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UsageMetricProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.UsageMetricProperties(_Model):
        monthly_firmware_upload_count: int
        provisioning_state: Optional[Union[str, ProvisioningState]]
        total_firmware_count: int


    class azure.mgmt.iotfirmwaredefense.models.Workspace(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[WorkspaceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[WorkspaceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.iotfirmwaredefense.models.WorkspaceProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.iotfirmwaredefense.models.WorkspaceUpdate(_Model):
        sku: Optional[Sku]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.iotfirmwaredefense.operations

    class azure.mgmt.iotfirmwaredefense.operations.BinaryHardeningOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[BinaryHardeningResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.CryptoCertificatesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[CryptoCertificateResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.CryptoKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[CryptoKeyResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.CvesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-02', params_added_on={'2025-08-02': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name', 'firmware_id', 'accept']}, api_versions_list=['2025-08-02'])
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[CveResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.FirmwaresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: Firmware, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> Firmware: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Firmware]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: FirmwareUpdateDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Firmware: ...


    class azure.mgmt.iotfirmwaredefense.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.iotfirmwaredefense.operations.PasswordHashesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[PasswordHashResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.SbomComponentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[SbomComponentResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.SummariesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                summary_type: Union[str, SummaryType], 
                **kwargs: Any
            ) -> SummaryResource: ...

        @distributed_trace
        def list_by_firmware(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                firmware_id: str, 
                **kwargs: Any
            ) -> ItemPaged[SummaryResource]: ...


    class azure.mgmt.iotfirmwaredefense.operations.UsageMetricsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                name: str, 
                **kwargs: Any
            ) -> UsageMetric: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UsageMetric]: ...


    class azure.mgmt.iotfirmwaredefense.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-08-02', params_added_on={'2025-08-02': ['api_version', 'subscription_id', 'resource_group_name', 'workspace_name']}, api_versions_list=['2025-08-02'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: GenerateUploadUrlRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @overload
        def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @overload
        def generate_upload_url(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UrlToken: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Workspace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: WorkspaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


```