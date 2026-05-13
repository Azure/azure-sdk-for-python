```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.keyvault.securitydomain

    class azure.keyvault.securitydomain.SecurityDomainClient(KeyVaultClient): implements ContextManager 
        property vault_url: str    # Read-only

        def __init__(
                self, 
                vault_url: str, 
                credential: TokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_download(
                self, 
                certificate_info: CertificateInfo, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[SecurityDomain]: ...

        @overload
        def begin_download(
                self, 
                certificate_info: JSON, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[SecurityDomain]: ...

        @overload
        def begin_download(
                self, 
                certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[SecurityDomain]: ...

        @overload
        @distributed_trace
        def begin_upload(
                self, 
                security_domain: SecurityDomain, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        @distributed_trace
        def begin_upload(
                self, 
                security_domain: JSON, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        @distributed_trace
        def begin_upload(
                self, 
                security_domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_download_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace
        def get_transfer_key(self, **kwargs: Any) -> TransferKey: ...

        @distributed_trace
        def get_upload_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.keyvault.securitydomain.aio

    class azure.keyvault.securitydomain.aio.SecurityDomainClient(KeyVaultClient): implements AsyncContextManager 

        def __init__(
                self, 
                vault_url: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
                polling_interval: Optional[int] = ..., 
                verify_challenge_resource: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_download(
                self, 
                certificate_info: CertificateInfo, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityDomain]: ...

        @overload
        async def begin_download(
                self, 
                certificate_info: JSON, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityDomain]: ...

        @overload
        async def begin_download(
                self, 
                certificate_info: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityDomain]: ...

        @overload
        @distributed_trace_async
        async def begin_upload(
                self, 
                security_domain: SecurityDomain, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        @distributed_trace_async
        async def begin_upload(
                self, 
                security_domain: JSON, 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        @distributed_trace_async
        async def begin_upload(
                self, 
                security_domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                skip_activation_polling: bool = False, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_download_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace_async
        async def get_transfer_key(self, **kwargs: Any) -> TransferKey: ...

        @distributed_trace_async
        async def get_upload_status(self, **kwargs: Any) -> SecurityDomainOperationStatus: ...

        @distributed_trace_async
        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.keyvault.securitydomain.models

    class azure.keyvault.securitydomain.models.CertificateInfo(_Model):
        certificates: List[SecurityDomainJsonWebKey]
        required: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                certificates: List[SecurityDomainJsonWebKey], 
                required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.keyvault.securitydomain.models.Error(_Model):
        code: Optional[str]
        inner_error: Optional[Error]
        message: Optional[str]


    class azure.keyvault.securitydomain.models.KeyVaultError(_Model):
        error: Optional[Error]


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
        key_ops: List[str]
        kid: str
        kty: str
        n: str
        use: Optional[str]
        x5_c: List[str]
        x5_t: Optional[str]
        x5_t_s256: str

        @overload
        def __init__(
                self, 
                *, 
                alg: str, 
                e: str, 
                key_ops: List[str], 
                kid: str, 
                kty: str, 
                n: str, 
                use: Optional[str] = ..., 
                x5_c: List[str], 
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


```