```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.confidentialledger.certificate

    class azure.confidentialledger.certificate.ConfidentialLedgerCertificateClient(_ConfidentialLedgerCertificateClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                *, 
                api_version: str = ..., 
                certificate_endpoint: str = "https://identity.confidential-ledger.core.azure.com", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_ledger_identity(
                self, 
                ledger_id: str, 
                **kwargs: Any
            ) -> LedgerIdentityInformation: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.confidentialledger.certificate.aio

    class azure.confidentialledger.certificate.aio.ConfidentialLedgerCertificateClient(_ConfidentialLedgerCertificateClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                api_version: str = ..., 
                certificate_endpoint: str = "https://identity.confidential-ledger.core.azure.com", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_ledger_identity(
                self, 
                ledger_id: str, 
                **kwargs: Any
            ) -> LedgerIdentityInformation: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.confidentialledger.certificate.models

    class azure.confidentialledger.certificate.models.ConfidentialLedgerError(_Model):
        error: Optional[ConfidentialLedgerErrorBody]


    class azure.confidentialledger.certificate.models.ConfidentialLedgerErrorBody(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.confidentialledger.certificate.models.LedgerIdentityInformation(_Model):
        ledger_id: Optional[str]
        ledger_tls_certificate: str

        @overload
        def __init__(
                self, 
                *, 
                ledger_tls_certificate: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```