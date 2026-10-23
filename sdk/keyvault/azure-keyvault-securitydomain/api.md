```py
namespace azure.keyvault.securitydomain

    class azure.keyvault.securitydomain.SecurityDomainClient(_SecurityDomainClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                vault_base_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_download_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace
        def get_transfer_key(self, **kwargs: Any) -> TransferKey: ...

        @distributed_trace
        def get_upload_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.keyvault.securitydomain.aio

    class azure.keyvault.securitydomain.aio.SecurityDomainClient(_SecurityDomainClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                vault_base_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_download_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace_async
        async def get_transfer_key(self, **kwargs: Any) -> TransferKey: ...

        @distributed_trace_async
        async def get_upload_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.keyvault.securitydomain.models

    class azure.keyvault.securitydomain.models.CertificateInfo(_Model):
        certificates: list[SecurityDomainJsonWebKey]
        required: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                certificates: list[SecurityDomainJsonWebKey], 
                required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.keyvault.securitydomain.models.KeyVaultError(_Model):
        error: Optional[KeyVaultErrorError]


    class azure.keyvault.securitydomain.models.KeyVaultErrorError(_Model):
        code: Optional[str]
        inner_error: Optional[KeyVaultErrorError]
        message: Optional[str]


    class azure.keyvault.securitydomain.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCESS = "Success"


    class azure.keyvault.securitydomain.models.SecurityDomain(_Model):
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.keyvault.securitydomain.models.SecurityDomainJsonWebKey(_Model):
        alg: str
        e: str
        key_ops: list[str]
        kid: str
        kty: str
        n: str
        use: Optional[str]
        x5_c: list[str]
        x5_t: Optional[str]
        x5_t_s256: str

        @overload
        def __init__(
                self, 
                *, 
                alg: str, 
                e: str, 
                key_ops: list[str], 
                kid: str, 
                kty: str, 
                n: str, 
                use: Optional[str] = ..., 
                x5_c: list[str], 
                x5_t: Optional[str] = ..., 
                x5_t_s256: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.keyvault.securitydomain.models.SecurityDomainOperationStatus(_Model):
        status: Optional[Union[str, OperationStatus]]
        status_details: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, OperationStatus]] = ..., 
                status_details: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.keyvault.securitydomain.models.TransferKey(_Model):
        key_format: Optional[str]
        transfer_key: SecurityDomainJsonWebKey

        @overload
        def __init__(
                self, 
                *, 
                key_format: Optional[str] = ..., 
                transfer_key: SecurityDomainJsonWebKey
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.keyvault.securitydomain.types

    class azure.keyvault.securitydomain.types.CertificateInfo(TypedDict, total=False):
        key "certificates": Required[list[SecurityDomainJsonWebKey]]
        key "required": int
        certificates: list[SecurityDomainJsonWebKey]
        required: int


    class azure.keyvault.securitydomain.types.SecurityDomain(TypedDict, total=False):
        key "value": Required[str]
        value: str


    class azure.keyvault.securitydomain.types.SecurityDomainJsonWebKey(TypedDict):
        key "alg": Required[str]
        key "e": Required[str]
        key "key_ops": Required[list[str]]
        key "kid": Required[str]
        key "kty": Required[str]
        key "n": Required[str]
        key "use": str
        key "x5c": Required[list[str]]
        key "x5t": str
        key "x5t#S256": Required[str]
        alg: str
        e: str
        key_ops: list[str]
        kid: str
        kty: str
        n: str
        use: str
        x5c: list[str]
        x5t: str
        x5t#S256: str


```