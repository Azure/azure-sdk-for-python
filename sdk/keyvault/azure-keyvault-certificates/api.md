```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.keyvault.certificates

    class azure.keyvault.certificates.AdministratorContact:
        property email: Optional[str]    # Read-only
        property first_name: Optional[str]    # Read-only
        property last_name: Optional[str]    # Read-only
        property phone: Optional[str]    # Read-only

        def __init__(
                self, 
                first_name: Optional[str] = None, 
                last_name: Optional[str] = None, 
                email: Optional[str] = None, 
                phone: Optional[str] = None
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2016_10_01 = "2016-10-01"
        V2025_07_01 = "2025-07-01"
        V7_0 = "7.0"
        V7_1 = "7.1"
        V7_2 = "7.2"
        V7_3 = "7.3"
        V7_4 = "7.4"
        V7_5 = "7.5"
        V7_6 = "7.6"


    class azure.keyvault.certificates.CertificateClient(KeyVaultClientBase): implements ContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def backup_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> bytes: ...

        @distributed_trace
        def begin_create_certificate(
                self, 
                certificate_name: str, 
                policy: CertificatePolicy, 
                *, 
                enabled: Optional[bool] = ..., 
                preserve_order: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> LROPoller[Union[KeyVaultCertificate, CertificateOperation]]: ...

        @distributed_trace
        def begin_delete_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[DeletedCertificate]: ...

        @distributed_trace
        def begin_recover_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> LROPoller[KeyVaultCertificate]: ...

        @distributed_trace
        def cancel_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_issuer(
                self, 
                issuer_name: str, 
                provider: str, 
                *, 
                account_id: Optional[str] = ..., 
                admin_contacts: Optional[List[AdministratorContact]] = ..., 
                enabled: Optional[bool] = ..., 
                organization_id: Optional[str] = ..., 
                password: Optional[str] = ..., 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace
        def delete_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        @distributed_trace
        def delete_contacts(self, **kwargs: Any) -> List[CertificateContact]: ...

        @distributed_trace
        def delete_issuer(
                self, 
                issuer_name: str, 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace
        def get_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def get_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        @distributed_trace
        def get_certificate_policy(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace
        def get_certificate_version(
                self, 
                certificate_name: str, 
                version: str, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def get_contacts(self, **kwargs: Any) -> List[CertificateContact]: ...

        @distributed_trace
        def get_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> DeletedCertificate: ...

        @distributed_trace
        def get_issuer(
                self, 
                issuer_name: str, 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace
        def import_certificate(
                self, 
                certificate_name: str, 
                certificate_bytes: bytes, 
                *, 
                enabled: Optional[bool] = ..., 
                password: Optional[str] = ..., 
                policy: Optional[CertificatePolicy] = ..., 
                preserve_order: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def list_deleted_certificates(
                self, 
                *, 
                include_pending: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DeletedCertificate]: ...

        @distributed_trace
        def list_properties_of_certificate_versions(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificateProperties]: ...

        @distributed_trace
        def list_properties_of_certificates(
                self, 
                *, 
                include_pending: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CertificateProperties]: ...

        @distributed_trace
        def list_properties_of_issuers(self, **kwargs: Any) -> ItemPaged[IssuerProperties]: ...

        @distributed_trace
        def merge_certificate(
                self, 
                certificate_name: str, 
                x509_certificates: List[bytes], 
                *, 
                enabled: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def purge_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def restore_certificate_backup(
                self, 
                backup: bytes, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def set_contacts(
                self, 
                contacts: List[CertificateContact], 
                **kwargs: Any
            ) -> List[CertificateContact]: ...

        @distributed_trace
        def update_certificate_policy(
                self, 
                certificate_name: str, 
                policy: CertificatePolicy, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace
        def update_certificate_properties(
                self, 
                certificate_name: str, 
                version: Optional[str] = None, 
                *, 
                enabled: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def update_issuer(
                self, 
                issuer_name: str, 
                *, 
                account_id: Optional[str] = ..., 
                admin_contacts: Optional[List[AdministratorContact]] = ..., 
                enabled: Optional[bool] = ..., 
                organization_id: Optional[str] = ..., 
                password: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                **kwargs: Any
            ) -> CertificateIssuer: ...


    class azure.keyvault.certificates.CertificateContact:
        property email: Optional[str]    # Read-only
        property name: Optional[str]    # Read-only
        property phone: Optional[str]    # Read-only

        def __init__(
                self, 
                email: Optional[str] = None, 
                name: Optional[str] = None, 
                phone: Optional[str] = None
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.CertificateContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        pem = "application/x-pem-file"
        pkcs12 = "application/x-pkcs12"


    class azure.keyvault.certificates.CertificateIssuer:
        property account_id: Optional[str]    # Read-only
        property admin_contacts: Optional[List[AdministratorContact]]    # Read-only
        property created_on: Optional[datetime]    # Read-only
        property enabled: Optional[bool]    # Read-only
        property id: Optional[str]    # Read-only
        property name: Optional[str]    # Read-only
        property organization_id: Optional[str]    # Read-only
        property password: Optional[str]    # Read-only
        property provider: Optional[str]    # Read-only
        property updated_on: Optional[datetime]    # Read-only

        def __init__(
                self, 
                provider: Optional[str], 
                attributes: Optional[IssuerAttributes] = None, 
                account_id: Optional[str] = None, 
                password: Optional[str] = None, 
                organization_id: Optional[str] = None, 
                admin_contacts: Optional[List[AdministratorContact]] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.CertificateOperation:
        property cancellation_requested: Optional[bool]    # Read-only
        property certificate_transparency: Optional[bool]    # Read-only
        property certificate_type: Optional[str]    # Read-only
        property csr: Optional[bytes]    # Read-only
        property error: Optional[CertificateOperationError]    # Read-only
        property id: Optional[str]    # Read-only
        property issuer_name: Union[str, WellKnownIssuerNames, None]    # Read-only
        property name: Optional[str]    # Read-only
        property preserve_order: Optional[bool]    # Read-only
        property request_id: Optional[str]    # Read-only
        property status: Optional[str]    # Read-only
        property status_details: Optional[str]    # Read-only
        property target: Optional[str]    # Read-only
        property vault_url: Optional[str]    # Read-only

        def __init__(
                self, 
                cert_operation_id: Optional[str] = None, 
                issuer_name: Optional[Union[str, WellKnownIssuerNames]] = None, 
                certificate_type: Optional[str] = None, 
                certificate_transparency: Optional[bool] = False, 
                csr: Optional[bytes] = None, 
                cancellation_requested: Optional[bool] = False, 
                status: Optional[str] = None, 
                status_details: Optional[str] = None, 
                error: Optional[CertificateOperationError] = None, 
                target: Optional[str] = None, 
                request_id: Optional[str] = None, 
                preserve_order: Optional[bool] = False
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.CertificateOperationError:
        property code: str    # Read-only
        property inner_error: Optional[CertificateOperationError]    # Read-only
        property message: str    # Read-only

        def __init__(
                self, 
                code: str, 
                message: str, 
                inner_error: Optional[CertificateOperationError] = None
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.CertificatePolicy:
        property certificate_transparency: Optional[bool]    # Read-only
        property certificate_type: Optional[str]    # Read-only
        property content_type: Optional[CertificateContentType]    # Read-only
        property created_on: Optional[datetime]    # Read-only
        property enabled: Optional[bool]    # Read-only
        property enhanced_key_usage: Optional[List[str]]    # Read-only
        property exportable: Optional[bool]    # Read-only
        property issuer_name: Optional[str]    # Read-only
        property key_curve_name: Optional[KeyCurveName]    # Read-only
        property key_size: Optional[int]    # Read-only
        property key_type: Optional[KeyType]    # Read-only
        property key_usage: Optional[List[KeyUsageType]]    # Read-only
        property lifetime_actions: Optional[List[LifetimeAction]]    # Read-only
        property reuse_key: Optional[bool]    # Read-only
        property san_dns_names: Optional[List[str]]    # Read-only
        property san_emails: Optional[List[str]]    # Read-only
        property san_ip_addresses: Optional[List[str]]    # Read-only
        property san_uris: Optional[List[str]]    # Read-only
        property san_user_principal_names: Optional[List[str]]    # Read-only
        property subject: Optional[str]    # Read-only
        property updated_on: Optional[datetime]    # Read-only
        property validity_in_months: Optional[int]    # Read-only

        def __init__(
                self, 
                issuer_name: Optional[str] = None, 
                *, 
                certificate_transparency: Union[bool, None] = ..., 
                certificate_type: Union[str, None] = ..., 
                content_type: Union[str, CertificateContentType, None] = ..., 
                enhanced_key_usage: Union[list[str], None] = ..., 
                exportable: Union[bool, None] = ..., 
                key_curve_name: Union[str, KeyCurveName, None] = ..., 
                key_size: Union[int, None] = ..., 
                key_type: Union[str, KeyType, None] = ..., 
                key_usage: Union[list[str, KeyUsageType], None] = ..., 
                lifetime_actions: Union[list[LifetimeAction], None] = ..., 
                reuse_key: Union[bool, None] = ..., 
                san_dns_names: Union[list[str], None] = ..., 
                san_emails: Union[list[str], None] = ..., 
                san_ip_addresses: Union[list[str], None] = ..., 
                san_uris: Union[list[str], None] = ..., 
                san_user_principal_names: Union[list[str], None] = ..., 
                subject: Union[str, None] = ..., 
                validity_in_months: Union[int, None] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def get_default(cls) -> CertificatePolicy: ...


    class azure.keyvault.certificates.CertificatePolicyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        auto_renew = "AutoRenew"
        email_contacts = "EmailContacts"


    class azure.keyvault.certificates.CertificateProperties:
        property created_on: Optional[datetime]    # Read-only
        property enabled: Optional[bool]    # Read-only
        property expires_on: Optional[datetime]    # Read-only
        property id: str    # Read-only
        property name: str    # Read-only
        property not_before: Optional[datetime]    # Read-only
        property preserve_order: Optional[bool]    # Read-only
        property recoverable_days: Optional[int]    # Read-only
        property recovery_level: Optional[DeletionRecoveryLevel]    # Read-only
        property tags: Optional[Dict[str, str]]    # Read-only
        property updated_on: Optional[datetime]    # Read-only
        property vault_url: str    # Read-only
        property version: Optional[str]    # Read-only
        property x509_thumbprint: bytes    # Read-only

        def __init__(self, **kwargs: Any) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.DeletedCertificate(KeyVaultCertificate):
        property cer: Optional[bytearray]    # Read-only
        property deleted_on: Optional[datetime]    # Read-only
        property id: Optional[str]    # Read-only
        property key_id: Optional[str]    # Read-only
        property name: Optional[str]    # Read-only
        property policy: Optional[CertificatePolicy]    # Read-only
        property properties: Optional[CertificateProperties]    # Read-only
        property recovery_id: Optional[str]    # Read-only
        property scheduled_purge_date: Optional[datetime]    # Read-only
        property secret_id: Optional[str]    # Read-only

        def __init__(
                self, 
                properties: Optional[CertificateProperties] = None, 
                policy: Optional[CertificatePolicy] = None, 
                cer: Optional[bytearray] = None, 
                *, 
                deleted_on: Union[datetime, None] = ..., 
                recovery_id: Union[str, None] = ..., 
                scheduled_purge_date: Union[datetime, None] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.IssuerProperties:
        property id: Optional[str]    # Read-only
        property name: Optional[str]    # Read-only
        property provider: Optional[str]    # Read-only

        def __init__(
                self, 
                provider: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.KeyCurveName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        p_256 = "P-256"
        p_256_k = "P-256K"
        p_384 = "P-384"
        p_521 = "P-521"


    class azure.keyvault.certificates.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ec = "EC"
        ec_hsm = "EC-HSM"
        oct = "oct"
        oct_hsm = "oct-HSM"
        rsa = "RSA"
        rsa_hsm = "RSA-HSM"


    class azure.keyvault.certificates.KeyUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        crl_sign = "cRLSign"
        data_encipherment = "dataEncipherment"
        decipher_only = "decipherOnly"
        digital_signature = "digitalSignature"
        encipher_only = "encipherOnly"
        key_agreement = "keyAgreement"
        key_cert_sign = "keyCertSign"
        key_encipherment = "keyEncipherment"
        non_repudiation = "nonRepudiation"


    class azure.keyvault.certificates.KeyVaultCertificate:
        property cer: Optional[bytearray]    # Read-only
        property id: Optional[str]    # Read-only
        property key_id: Optional[str]    # Read-only
        property name: Optional[str]    # Read-only
        property policy: Optional[CertificatePolicy]    # Read-only
        property properties: Optional[CertificateProperties]    # Read-only
        property secret_id: Optional[str]    # Read-only

        def __init__(
                self, 
                policy: Optional[CertificatePolicy] = None, 
                properties: Optional[CertificateProperties] = None, 
                cer: Optional[bytearray] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.KeyVaultCertificateIdentifier:
        property name: str    # Read-only
        property source_id: str    # Read-only
        property vault_url: str    # Read-only
        property version: Optional[str]    # Read-only

        def __init__(self, source_id: str) -> None: ...


    class azure.keyvault.certificates.LifetimeAction:
        property action: Union[str, CertificatePolicyAction, None]    # Read-only
        property days_before_expiry: Optional[int]    # Read-only
        property lifetime_percentage: Optional[int]    # Read-only

        def __init__(
                self, 
                action: Union[str, CertificatePolicyAction, None], 
                lifetime_percentage: Optional[int] = None, 
                days_before_expiry: Optional[int] = None
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.certificates.WellKnownIssuerNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        self = "Self"
        unknown = "Unknown"


namespace azure.keyvault.certificates.aio

    class azure.keyvault.certificates.aio.CertificateClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def backup_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> bytes: ...

        @distributed_trace_async
        async def cancel_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_certificate(
                self, 
                certificate_name: str, 
                policy: CertificatePolicy, 
                *, 
                enabled: Optional[bool] = ..., 
                preserve_order: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> Union[KeyVaultCertificate, CertificateOperation]: ...

        @distributed_trace_async
        async def create_issuer(
                self, 
                issuer_name: str, 
                provider: str, 
                *, 
                account_id: Optional[str] = ..., 
                admin_contacts: Optional[List[AdministratorContact]] = ..., 
                enabled: Optional[bool] = ..., 
                organization_id: Optional[str] = ..., 
                password: Optional[str] = ..., 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace_async
        async def delete_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> DeletedCertificate: ...

        @distributed_trace_async
        async def delete_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        @distributed_trace_async
        async def delete_contacts(self, **kwargs: Any) -> List[CertificateContact]: ...

        @distributed_trace_async
        async def delete_issuer(
                self, 
                issuer_name: str, 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace_async
        async def get_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        async def get_certificate_operation(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificateOperation: ...

        @distributed_trace_async
        async def get_certificate_policy(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace_async
        async def get_certificate_version(
                self, 
                certificate_name: str, 
                version: str, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        async def get_contacts(self, **kwargs: Any) -> List[CertificateContact]: ...

        @distributed_trace_async
        async def get_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> DeletedCertificate: ...

        @distributed_trace_async
        async def get_issuer(
                self, 
                issuer_name: str, 
                **kwargs: Any
            ) -> CertificateIssuer: ...

        @distributed_trace_async
        async def import_certificate(
                self, 
                certificate_name: str, 
                certificate_bytes: bytes, 
                *, 
                enabled: Optional[bool] = ..., 
                password: Optional[str] = ..., 
                policy: Optional[CertificatePolicy] = ..., 
                preserve_order: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace
        def list_deleted_certificates(
                self, 
                *, 
                include_pending: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DeletedCertificate]: ...

        @distributed_trace
        def list_properties_of_certificate_versions(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateProperties]: ...

        @distributed_trace
        def list_properties_of_certificates(
                self, 
                *, 
                include_pending: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateProperties]: ...

        @distributed_trace
        def list_properties_of_issuers(self, **kwargs: Any) -> AsyncItemPaged[IssuerProperties]: ...

        @distributed_trace_async
        async def merge_certificate(
                self, 
                certificate_name: str, 
                x509_certificates: List[bytes], 
                *, 
                enabled: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        async def purge_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def recover_deleted_certificate(
                self, 
                certificate_name: str, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        async def restore_certificate_backup(
                self, 
                backup: bytes, 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def set_contacts(
                self, 
                contacts: List[CertificateContact], 
                **kwargs: Any
            ) -> List[CertificateContact]: ...

        @distributed_trace_async
        async def update_certificate_policy(
                self, 
                certificate_name: str, 
                policy: CertificatePolicy, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace_async
        async def update_certificate_properties(
                self, 
                certificate_name: str, 
                version: Optional[str] = None, 
                *, 
                enabled: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultCertificate: ...

        @distributed_trace_async
        async def update_issuer(
                self, 
                issuer_name: str, 
                *, 
                account_id: Optional[str] = ..., 
                admin_contacts: Optional[List[AdministratorContact]] = ..., 
                enabled: Optional[bool] = ..., 
                organization_id: Optional[str] = ..., 
                password: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                **kwargs: Any
            ) -> CertificateIssuer: ...


```