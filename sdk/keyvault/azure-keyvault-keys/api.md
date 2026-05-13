```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.keyvault.keys

    class azure.keyvault.keys.ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2016_10_01 = "2016-10-01"
        V7_0 = "7.0"
        V7_1 = "7.1"
        V7_2 = "7.2"
        V7_3 = "7.3"
        V7_4 = "7.4"
        V7_5 = "7.5"
        V7_6 = "7.6"


    class azure.keyvault.keys.DeletedKey(KeyVaultKey):
        property deleted_date: Optional[datetime]    # Read-only
        property id: str    # Read-only
        property key: JsonWebKey    # Read-only
        property key_operations: List[Union[str, KeyOperation]]    # Read-only
        property key_type: Union[str, KeyType]    # Read-only
        property name: str    # Read-only
        property properties: KeyProperties    # Read-only
        property recovery_id: Optional[str]    # Read-only
        property scheduled_purge_date: Optional[datetime]    # Read-only

        def __init__(
                self, 
                properties: KeyProperties, 
                deleted_date: Optional[datetime] = None, 
                recovery_id: Optional[str] = None, 
                scheduled_purge_date: Optional[datetime] = None, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.keys.JsonWebKey:

        def __init__(
                self, 
                *, 
                crv: Union[KeyCurveName, str] = ..., 
                d: Optional[bytes] = ..., 
                dp: Optional[bytes] = ..., 
                dq: Optional[bytes] = ..., 
                e: Optional[bytes] = ..., 
                k: Optional[bytes] = ..., 
                key_ops: Union[list[str, KeyOperation]] = ..., 
                kid: Optional[str] = ..., 
                kty: Union[KeyType, str] = ..., 
                n: Optional[bytes] = ..., 
                p: Optional[bytes] = ..., 
                q: Optional[bytes] = ..., 
                qi: Optional[bytes] = ..., 
                t: Optional[bytes] = ..., 
                x: Optional[bytes] = ..., 
                y: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.keyvault.keys.KeyAttestation:
        certificate_pem_file: Union[bytes, None]
        private_key_attestation: Union[bytes, None]
        public_key_attestation: Union[bytes, None]
        version: Union[str, None]

        def __init__(
                self, 
                *, 
                certificate_pem_file: Optional[bytes] = ..., 
                private_key_attestation: Optional[bytes] = ..., 
                public_key_attestation: Optional[bytes] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.keys.KeyClient(KeyVaultClientBase): implements ContextManager 
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
        def backup_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> bytes: ...

        @distributed_trace
        def begin_delete_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[DeletedKey]: ...

        @distributed_trace
        def begin_recover_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[KeyVaultKey]: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_ec_key(
                self, 
                name: str, 
                *, 
                curve: Optional[Union[str, KeyCurveName]] = ..., 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def create_key(
                self, 
                name: str, 
                key_type: Union[str, KeyType], 
                *, 
                curve: Optional[Union[str, KeyCurveName]] = ..., 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                public_exponent: Optional[int] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def create_oct_key(
                self, 
                name: str, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def create_rsa_key(
                self, 
                name: str, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                public_exponent: Optional[int] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        def get_cryptography_client(
                self, 
                key_name: str, 
                *, 
                key_version: Optional[str] = ..., 
                **kwargs
            ) -> CryptographyClient: ...

        @distributed_trace
        def get_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeletedKey: ...

        @distributed_trace
        def get_key(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def get_key_attestation(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def get_key_rotation_policy(
                self, 
                key_name: str, 
                **kwargs: Any
            ) -> KeyRotationPolicy: ...

        @distributed_trace
        def get_random_bytes(
                self, 
                count: int, 
                **kwargs: Any
            ) -> bytes: ...

        @distributed_trace
        def import_key(
                self, 
                name: str, 
                key: JsonWebKey, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def list_deleted_keys(self, **kwargs: Any) -> ItemPaged[DeletedKey]: ...

        @distributed_trace
        def list_properties_of_key_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[KeyProperties]: ...

        @distributed_trace
        def list_properties_of_keys(self, **kwargs: Any) -> ItemPaged[KeyProperties]: ...

        @distributed_trace
        def purge_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def release_key(
                self, 
                name: str, 
                target_attestation_token: str, 
                *, 
                algorithm: Optional[Union[str, KeyExportEncryptionAlgorithm]] = ..., 
                nonce: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReleaseKeyResult: ...

        @distributed_trace
        def restore_key_backup(
                self, 
                backup: bytes, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def rotate_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def update_key_properties(
                self, 
                name: str, 
                version: Optional[str] = None, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def update_key_rotation_policy(
                self, 
                key_name: str, 
                policy: KeyRotationPolicy, 
                *, 
                expires_in: Optional[str] = ..., 
                lifetime_actions: Optional[List[KeyRotationLifetimeAction]] = ..., 
                **kwargs: Any
            ) -> KeyRotationPolicy: ...


    class azure.keyvault.keys.KeyCurveName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        p_256 = "P-256"
        p_256_k = "P-256K"
        p_384 = "P-384"
        p_521 = "P-521"


    class azure.keyvault.keys.KeyExportEncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ckm_rsa_aes_key_wrap = "CKM_RSA_AES_KEY_WRAP"
        rsa_aes_key_wrap_256 = "RSA_AES_KEY_WRAP_256"
        rsa_aes_key_wrap_384 = "RSA_AES_KEY_WRAP_384"


    class azure.keyvault.keys.KeyOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        decrypt = "decrypt"
        encrypt = "encrypt"
        export = "export"
        import_key = "import"
        sign = "sign"
        unwrap_key = "unwrapKey"
        verify = "verify"
        wrap_key = "wrapKey"


    class azure.keyvault.keys.KeyProperties:
        property attestation: Optional[KeyAttestation]    # Read-only
        property created_on: Optional[datetime]    # Read-only
        property enabled: Optional[bool]    # Read-only
        property expires_on: Optional[datetime]    # Read-only
        property exportable: Optional[bool]    # Read-only
        property hsm_platform: Optional[str]    # Read-only
        property id: str    # Read-only
        property managed: Optional[bool]    # Read-only
        property name: str    # Read-only
        property not_before: Optional[datetime]    # Read-only
        property recoverable_days: Optional[int]    # Read-only
        property recovery_level: Optional[str]    # Read-only
        property release_policy: Optional[KeyReleasePolicy]    # Read-only
        property tags: Dict[str, str]    # Read-only
        property updated_on: Optional[datetime]    # Read-only
        property vault_url: str    # Read-only
        property version: Optional[str]    # Read-only

        def __init__(
                self, 
                key_id: str, 
                attributes: Optional[KeyAttributes] = None, 
                *, 
                managed: Optional[bool] = ..., 
                release_policy: Union[KeyReleasePolicy, None] = ..., 
                tags: Union[dict[str, str], None] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.keys.KeyReleasePolicy:

        def __init__(
                self, 
                encoded_policy: bytes, 
                *, 
                content_type: Optional[str] = ..., 
                immutable: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.keyvault.keys.KeyRotationLifetimeAction:

        def __init__(
                self, 
                action: Union[KeyRotationPolicyAction, str], 
                *, 
                time_after_create: Union[str, None] = ..., 
                time_before_expiry: Union[str, None] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.keyvault.keys.KeyRotationPolicy:
        created_on: Union[datetime, None]
        expires_in: Union[str, None]
        id: Union[str, None]
        lifetime_actions: list[KeyRotationLifetimeAction]
        updated_on: Union[datetime, None]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.keyvault.keys.KeyRotationPolicyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        notify = "Notify"
        rotate = "Rotate"


    class azure.keyvault.keys.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ec = "EC"
        ec_hsm = "EC-HSM"
        oct = "oct"
        oct_hsm = "oct-HSM"
        rsa = "RSA"
        rsa_hsm = "RSA-HSM"


    class azure.keyvault.keys.KeyVaultKey:
        property id: str    # Read-only
        property key: JsonWebKey    # Read-only
        property key_operations: List[Union[str, KeyOperation]]    # Read-only
        property key_type: Union[str, KeyType]    # Read-only
        property name: str    # Read-only
        property properties: KeyProperties    # Read-only

        def __init__(
                self, 
                key_id: str, 
                jwk: Optional[Dict[str, Any]] = None, 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.keyvault.keys.KeyVaultKeyIdentifier:
        property name: str    # Read-only
        property source_id: str    # Read-only
        property vault_url: str    # Read-only
        property version: Optional[str]    # Read-only

        def __init__(self, source_id: str) -> None: ...


    class azure.keyvault.keys.ReleaseKeyResult:
        value: str

        def __init__(self, value: str) -> None: ...


namespace azure.keyvault.keys.aio

    class azure.keyvault.keys.aio.KeyClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
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
        async def backup_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> bytes: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_ec_key(
                self, 
                name: str, 
                *, 
                curve: Optional[Union[str, KeyCurveName]] = ..., 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def create_key(
                self, 
                name: str, 
                key_type: Union[str, KeyType], 
                *, 
                curve: Optional[Union[str, KeyCurveName]] = ..., 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                public_exponent: Optional[int] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def create_oct_key(
                self, 
                name: str, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def create_rsa_key(
                self, 
                name: str, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = False, 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                public_exponent: Optional[int] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                size: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def delete_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeletedKey: ...

        def get_cryptography_client(
                self, 
                key_name: str, 
                *, 
                key_version: Optional[str] = ..., 
                **kwargs
            ) -> CryptographyClient: ...

        @distributed_trace_async
        async def get_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeletedKey: ...

        @distributed_trace_async
        async def get_key(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def get_key_attestation(
                self, 
                name: str, 
                version: Optional[str] = None, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def get_key_rotation_policy(
                self, 
                key_name: str, 
                **kwargs: Any
            ) -> KeyRotationPolicy: ...

        @distributed_trace_async
        async def get_random_bytes(
                self, 
                count: int, 
                **kwargs: Any
            ) -> bytes: ...

        @distributed_trace_async
        async def import_key(
                self, 
                name: str, 
                key: JsonWebKey, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                exportable: Optional[bool] = ..., 
                hardware_protected: Optional[bool] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace
        def list_deleted_keys(self, **kwargs: Any) -> AsyncItemPaged[DeletedKey]: ...

        @distributed_trace
        def list_properties_of_key_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[KeyProperties]: ...

        @distributed_trace
        def list_properties_of_keys(self, **kwargs: Any) -> AsyncItemPaged[KeyProperties]: ...

        @distributed_trace_async
        async def purge_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def recover_deleted_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def release_key(
                self, 
                name: str, 
                target_attestation_token: str, 
                *, 
                algorithm: Optional[Union[str, KeyExportEncryptionAlgorithm]] = ..., 
                nonce: Optional[str] = ..., 
                version: Optional[str] = ..., 
                **kwargs: Any
            ) -> ReleaseKeyResult: ...

        @distributed_trace_async
        async def restore_key_backup(
                self, 
                backup: bytes, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def rotate_key(
                self, 
                name: str, 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def update_key_properties(
                self, 
                name: str, 
                version: Optional[str] = None, 
                *, 
                enabled: Optional[bool] = ..., 
                expires_on: Optional[datetime] = ..., 
                key_operations: Optional[List[Union[str, KeyOperation]]] = ..., 
                not_before: Optional[datetime] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> KeyVaultKey: ...

        @distributed_trace_async
        async def update_key_rotation_policy(
                self, 
                key_name: str, 
                policy: KeyRotationPolicy, 
                *, 
                expires_in: Optional[str] = ..., 
                lifetime_actions: Optional[List[KeyRotationLifetimeAction]] = ..., 
                **kwargs: Any
            ) -> KeyRotationPolicy: ...


namespace azure.keyvault.keys.crypto

    class azure.keyvault.keys.crypto.CryptographyClient(KeyVaultClientBase): implements ContextManager 
        property key_id: Optional[str]    # Read-only
        property vault_url: Optional[str]    # Read-only

        def __init__(
                self, 
                key: Union[KeyVaultKey, str], 
                credential: TokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_jwk(cls, jwk: Union[JsonWebKey, Dict[str, Any]]) -> CryptographyClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_rsa_private_key(self) -> KeyVaultRSAPrivateKey: ...

        @distributed_trace
        def create_rsa_public_key(self) -> KeyVaultRSAPublicKey: ...

        @distributed_trace
        def decrypt(
                self, 
                algorithm: EncryptionAlgorithm, 
                ciphertext: bytes, 
                *, 
                additional_authenticated_data: Optional[bytes] = ..., 
                authentication_tag: Optional[bytes] = ..., 
                iv: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> DecryptResult: ...

        @distributed_trace
        def encrypt(
                self, 
                algorithm: EncryptionAlgorithm, 
                plaintext: bytes, 
                *, 
                additional_authenticated_data: Optional[bytes] = ..., 
                iv: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> EncryptResult: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def sign(
                self, 
                algorithm: SignatureAlgorithm, 
                digest: bytes, 
                **kwargs: Any
            ) -> SignResult: ...

        @distributed_trace
        def unwrap_key(
                self, 
                algorithm: KeyWrapAlgorithm, 
                encrypted_key: bytes, 
                **kwargs: Any
            ) -> UnwrapResult: ...

        @distributed_trace
        def verify(
                self, 
                algorithm: SignatureAlgorithm, 
                digest: bytes, 
                signature: bytes, 
                **kwargs: Any
            ) -> VerifyResult: ...

        @distributed_trace
        def wrap_key(
                self, 
                algorithm: KeyWrapAlgorithm, 
                key: bytes, 
                **kwargs: Any
            ) -> WrapResult: ...


    class azure.keyvault.keys.crypto.DecryptResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                algorithm: EncryptionAlgorithm, 
                plaintext: bytes
            ) -> None: ...


    class azure.keyvault.keys.crypto.EncryptResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                algorithm: EncryptionAlgorithm, 
                ciphertext: bytes, 
                *, 
                additional_authenticated_data: Optional[bytes] = ..., 
                authentication_tag: Optional[bytes] = ..., 
                iv: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.keyvault.keys.crypto.EncryptionAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        a128_cbc = "A128CBC"
        a128_cbcpad = "A128CBCPAD"
        a128_gcm = "A128GCM"
        a192_cbc = "A192CBC"
        a192_cbcpad = "A192CBCPAD"
        a192_gcm = "A192GCM"
        a256_cbc = "A256CBC"
        a256_cbcpad = "A256CBCPAD"
        a256_gcm = "A256GCM"
        rsa1_5 = "RSA1_5"
        rsa_oaep = "RSA-OAEP"
        rsa_oaep_256 = "RSA-OAEP-256"


    class azure.keyvault.keys.crypto.KeyVaultRSAPrivateKey(RSAPrivateKey):
        property key_size: int    # Read-only

        def __copy__(self) -> KeyVaultRSAPrivateKey: ...

        def __init__(
                self, 
                client: CryptographyClient, 
                key_material: Optional[JsonWebKey]
            ) -> None: ...

        def decrypt(
                self, 
                ciphertext: bytes, 
                padding: AsymmetricPadding
            ) -> bytes: ...

        def private_bytes(
                self, 
                encoding: Encoding, 
                format: PrivateFormat, 
                encryption_algorithm: KeySerializationEncryption
            ) -> bytes: ...

        def private_numbers(self) -> RSAPrivateNumbers: ...

        def public_key(self) -> KeyVaultRSAPublicKey: ...

        def sign(
                self, 
                data: bytes, 
                padding: AsymmetricPadding, 
                algorithm: Union[Prehashed, HashAlgorithm]
            ) -> bytes: ...

        def signer(
                self, 
                padding: AsymmetricPadding, 
                algorithm: HashAlgorithm
            ) -> NoReturn: ...


    class azure.keyvault.keys.crypto.KeyVaultRSAPublicKey(RSAPublicKey):
        property key_size: int    # Read-only

        def __copy__(self) -> KeyVaultRSAPublicKey: ...

        def __eq__(self, other: object) -> bool: ...

        def __init__(
                self, 
                client: CryptographyClient, 
                key_material: Optional[JsonWebKey] = None
            ) -> None: ...

        def encrypt(
                self, 
                plaintext: bytes, 
                padding: AsymmetricPadding
            ) -> bytes: ...

        def public_bytes(
                self, 
                encoding: Encoding, 
                format: PublicFormat
            ) -> bytes: ...

        def public_numbers(self) -> RSAPublicNumbers: ...

        def recover_data_from_signature(
                self, 
                signature: bytes, 
                padding: AsymmetricPadding, 
                algorithm: Optional[HashAlgorithm]
            ) -> bytes: ...

        def verifier(
                self, 
                signature: bytes, 
                padding: AsymmetricPadding, 
                algorithm: HashAlgorithm
            ) -> NoReturn: ...

        def verify(
                self, 
                signature: bytes, 
                data: bytes, 
                padding: AsymmetricPadding, 
                algorithm: Union[Prehashed, HashAlgorithm]
            ) -> None: ...


    class azure.keyvault.keys.crypto.KeyWrapAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        aes_128 = "A128KW"
        aes_192 = "A192KW"
        aes_256 = "A256KW"
        ckm_aes_key_wrap = "CKM_AES_KEY_WRAP"
        ckm_aes_key_wrap_pad = "CKM_AES_KEY_WRAP_PAD"
        rsa1_5 = "RSA1_5"
        rsa_oaep = "RSA-OAEP"
        rsa_oaep_256 = "RSA-OAEP-256"


    class azure.keyvault.keys.crypto.SignResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                algorithm: SignatureAlgorithm, 
                signature: bytes
            ) -> None: ...


    class azure.keyvault.keys.crypto.SignatureAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        es256 = "ES256"
        es256_k = "ES256K"
        es384 = "ES384"
        es512 = "ES512"
        hs256 = "HS256"
        hs384 = "HS384"
        hs512 = "HS512"
        ps256 = "PS256"
        ps384 = "PS384"
        ps512 = "PS512"
        rs256 = "RS256"
        rs384 = "RS384"
        rs512 = "RS512"


    class azure.keyvault.keys.crypto.UnwrapResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                algorithm: KeyWrapAlgorithm, 
                key: bytes
            ) -> None: ...


    class azure.keyvault.keys.crypto.VerifyResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                is_valid: bool = False, 
                algorithm: SignatureAlgorithm
            ) -> None: ...


    class azure.keyvault.keys.crypto.WrapResult:

        def __init__(
                self, 
                key_id: Optional[str], 
                algorithm: KeyWrapAlgorithm, 
                encrypted_key: bytes
            ) -> None: ...


namespace azure.keyvault.keys.crypto.aio

    class azure.keyvault.keys.crypto.aio.CryptographyClient(AsyncKeyVaultClientBase): implements AsyncContextManager 
        property key_id: Optional[str]    # Read-only
        property vault_url: Optional[str]    # Read-only

        def __init__(
                self, 
                key: Union[KeyVaultKey, str], 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Union[ApiVersion, str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_jwk(cls, jwk: Union[JsonWebKey, Dict[str, Any]]) -> CryptographyClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def decrypt(
                self, 
                algorithm: EncryptionAlgorithm, 
                ciphertext: bytes, 
                *, 
                additional_authenticated_data: Optional[bytes] = ..., 
                authentication_tag: Optional[bytes] = ..., 
                iv: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> DecryptResult: ...

        @distributed_trace_async
        async def encrypt(
                self, 
                algorithm: EncryptionAlgorithm, 
                plaintext: bytes, 
                *, 
                additional_authenticated_data: Optional[bytes] = ..., 
                iv: Optional[bytes] = ..., 
                **kwargs: Any
            ) -> EncryptResult: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def sign(
                self, 
                algorithm: SignatureAlgorithm, 
                digest: bytes, 
                **kwargs: Any
            ) -> SignResult: ...

        @distributed_trace_async
        async def unwrap_key(
                self, 
                algorithm: KeyWrapAlgorithm, 
                encrypted_key: bytes, 
                **kwargs: Any
            ) -> UnwrapResult: ...

        @distributed_trace_async
        async def verify(
                self, 
                algorithm: SignatureAlgorithm, 
                digest: bytes, 
                signature: bytes, 
                **kwargs: Any
            ) -> VerifyResult: ...

        @distributed_trace_async
        async def wrap_key(
                self, 
                algorithm: KeyWrapAlgorithm, 
                key: bytes, 
                **kwargs: Any
            ) -> WrapResult: ...


```