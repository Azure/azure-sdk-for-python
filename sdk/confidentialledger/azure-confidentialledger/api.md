```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.confidentialledger

    class azure.confidentialledger.ConfidentialLedgerCertificateCredential:
        property certificate_path: Union[bytes, str, PathLike]    # Read-only

        def __init__(self, certificate_path: Union[bytes, str, PathLike]): ...


    class azure.confidentialledger.ConfidentialLedgerClient(GeneratedClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[ConfidentialLedgerCertificateCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                ledger_certificate_path: Union[bytes, str, PathLike], 
                **kwargs: Any
            ) -> None: ...

        def begin_create_ledger_entry(
                self, 
                entry: Union[LedgerEntry, JSON, IO[bytes]], 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[TransactionStatus]: ...

        def begin_get_ledger_entry(
                self, 
                transaction_id: str, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[LedgerQueryResult]: ...

        def begin_get_receipt(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> LROPoller[TransactionReceipt]: ...

        def begin_wait_for_commit(
                self, 
                transaction_id: str, 
                **kwargs
            ) -> LROPoller[TransactionStatus]: ...

        def close(self) -> None: ...

        def create_ledger_entry(
                self, 
                entry: Union[LedgerEntry, JSON, IO[bytes]], 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerWriteResult: ...

        @overload
        def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: LedgerUserMultipleRoles, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        def create_or_update_user(
                self, 
                user_id: str, 
                user_details: LedgerUser, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        def create_or_update_user(
                self, 
                user_id: str, 
                user_details: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        def create_or_update_user(
                self, 
                user_id: str, 
                user_details: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        def create_user_defined_endpoint(
                self, 
                bundle: Bundle, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_user_defined_endpoint(
                self, 
                bundle: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_user_defined_endpoint(
                self, 
                bundle: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: UserDefinedFunction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        def create_user_defined_role(
                self, 
                body: Roles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_user_defined_role(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create_user_defined_role(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_ledger_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user_defined_function(
                self, 
                function_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user_defined_role(
                self, 
                *, 
                role_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[UserDefinedFunctionExecutionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @overload
        def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @overload
        def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @distributed_trace
        def get_constitution(self, **kwargs: Any) -> Constitution: ...

        @distributed_trace
        def get_current_ledger_entry(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerEntry: ...

        @distributed_trace
        def get_enclave_quotes(self, **kwargs: Any) -> ConfidentialLedgerEnclaves: ...

        @distributed_trace
        def get_ledger_entry(
                self, 
                transaction_id: str, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerQueryResult: ...

        @distributed_trace
        def get_ledger_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @distributed_trace
        def get_receipt(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> TransactionReceipt: ...

        @distributed_trace
        def get_runtime_options(self, **kwargs: Any) -> JsRuntimeOptions: ...

        @distributed_trace
        def get_transaction_status(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> TransactionStatus: ...

        @distributed_trace
        def get_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> LedgerUser: ...

        @distributed_trace
        def get_user_defined_endpoint(self, **kwargs: Any) -> Bundle: ...

        @distributed_trace
        def get_user_defined_endpoints_module(
                self, 
                *, 
                module_name: str, 
                **kwargs: Any
            ) -> ModuleDef: ...

        @distributed_trace
        def get_user_defined_function(
                self, 
                function_id: str, 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @distributed_trace
        def get_user_defined_role(
                self, 
                *, 
                role_name: str, 
                **kwargs: Any
            ) -> Roles: ...

        @distributed_trace
        def list_collections(self, **kwargs: Any) -> ItemPaged[Collection]: ...

        @distributed_trace
        def list_consortium_members(self, **kwargs: Any) -> ItemPaged[ConsortiumMember]: ...

        @distributed_trace
        def list_ledger_entries(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                from_transaction_id: Optional[str] = ..., 
                tag: Optional[str] = ..., 
                to_transaction_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[LedgerEntry]: ...

        @distributed_trace
        def list_ledger_users(self, **kwargs: Any) -> ItemPaged[LedgerUserMultipleRoles]: ...

        @distributed_trace
        def list_user_defined_functions(self, **kwargs: Any) -> ItemPaged[UserDefinedFunction]: ...

        @distributed_trace
        def list_users(self, **kwargs: Any) -> ItemPaged[LedgerUser]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_runtime_options(
                self, 
                js_runtime_options: JsRuntimeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        def update_runtime_options(
                self, 
                js_runtime_options: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        def update_runtime_options(
                self, 
                js_runtime_options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        def update_user_defined_role(
                self, 
                body: Roles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_user_defined_role(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_user_defined_role(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.confidentialledger.aio

    class azure.confidentialledger.aio.ConfidentialLedgerClient(GeneratedClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[ConfidentialLedgerCertificateCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                ledger_certificate_path: Union[bytes, str, PathLike], 
                **kwargs: Any
            ) -> None: ...

        async def begin_create_ledger_entry(
                self, 
                entry: Union[LedgerEntry, JSON, IO[bytes]], 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[TransactionStatus]: ...

        async def begin_get_ledger_entry(
                self, 
                transaction_id: str, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[LedgerQueryResult]: ...

        async def begin_get_receipt(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TransactionReceipt]: ...

        async def begin_wait_for_commit(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[TransactionStatus]: ...

        async def close(self) -> None: ...

        async def create_ledger_entry(
                self, 
                entry: Union[LedgerEntry, JSON, IO[bytes]], 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerWriteResult: ...

        @overload
        async def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: LedgerUserMultipleRoles, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        async def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        async def create_or_update_ledger_user(
                self, 
                user_id: str, 
                user_multiple_roles: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @overload
        async def create_or_update_user(
                self, 
                user_id: str, 
                user_details: LedgerUser, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        async def create_or_update_user(
                self, 
                user_id: str, 
                user_details: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        async def create_or_update_user(
                self, 
                user_id: str, 
                user_details: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LedgerUser: ...

        @overload
        async def create_user_defined_endpoint(
                self, 
                bundle: Bundle, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_user_defined_endpoint(
                self, 
                bundle: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_user_defined_endpoint(
                self, 
                bundle: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: UserDefinedFunction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        async def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        async def create_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @overload
        async def create_user_defined_role(
                self, 
                body: Roles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_user_defined_role(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create_user_defined_role(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_ledger_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user_defined_function(
                self, 
                function_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user_defined_role(
                self, 
                *, 
                role_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[UserDefinedFunctionExecutionProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @overload
        async def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @overload
        async def execute_user_defined_function(
                self, 
                function_id: str, 
                user_defined_function_execution_properties: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UserDefinedFunctionExecutionResponse: ...

        @distributed_trace_async
        async def get_constitution(self, **kwargs: Any) -> Constitution: ...

        @distributed_trace_async
        async def get_current_ledger_entry(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerEntry: ...

        @distributed_trace_async
        async def get_enclave_quotes(self, **kwargs: Any) -> ConfidentialLedgerEnclaves: ...

        @distributed_trace_async
        async def get_ledger_entry(
                self, 
                transaction_id: str, 
                *, 
                collection_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LedgerQueryResult: ...

        @distributed_trace_async
        async def get_ledger_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> LedgerUserMultipleRoles: ...

        @distributed_trace_async
        async def get_receipt(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> TransactionReceipt: ...

        @distributed_trace_async
        async def get_runtime_options(self, **kwargs: Any) -> JsRuntimeOptions: ...

        @distributed_trace_async
        async def get_transaction_status(
                self, 
                transaction_id: str, 
                **kwargs: Any
            ) -> TransactionStatus: ...

        @distributed_trace_async
        async def get_user(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> LedgerUser: ...

        @distributed_trace_async
        async def get_user_defined_endpoint(self, **kwargs: Any) -> Bundle: ...

        @distributed_trace_async
        async def get_user_defined_endpoints_module(
                self, 
                *, 
                module_name: str, 
                **kwargs: Any
            ) -> ModuleDef: ...

        @distributed_trace_async
        async def get_user_defined_function(
                self, 
                function_id: str, 
                **kwargs: Any
            ) -> UserDefinedFunction: ...

        @distributed_trace_async
        async def get_user_defined_role(
                self, 
                *, 
                role_name: str, 
                **kwargs: Any
            ) -> Roles: ...

        @distributed_trace
        def list_collections(self, **kwargs: Any) -> AsyncItemPaged[Collection]: ...

        @distributed_trace
        def list_consortium_members(self, **kwargs: Any) -> AsyncItemPaged[ConsortiumMember]: ...

        @distributed_trace
        def list_ledger_entries(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                from_transaction_id: Optional[str] = ..., 
                tag: Optional[str] = ..., 
                to_transaction_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[LedgerEntry]: ...

        @distributed_trace
        def list_ledger_users(self, **kwargs: Any) -> AsyncItemPaged[LedgerUserMultipleRoles]: ...

        @distributed_trace
        def list_user_defined_functions(self, **kwargs: Any) -> AsyncItemPaged[UserDefinedFunction]: ...

        @distributed_trace
        def list_users(self, **kwargs: Any) -> AsyncItemPaged[LedgerUser]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_runtime_options(
                self, 
                js_runtime_options: JsRuntimeOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        async def update_runtime_options(
                self, 
                js_runtime_options: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        async def update_runtime_options(
                self, 
                js_runtime_options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JsRuntimeOptions: ...

        @overload
        async def update_user_defined_role(
                self, 
                body: Roles, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_user_defined_role(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_user_defined_role(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.confidentialledger.models

    class azure.confidentialledger.models.ApplicationClaim(_Model):
        digest: Optional[ClaimDigest]
        kind: Union[str, ApplicationClaimKind]
        ledger_entry: Optional[LedgerEntryClaim]

        @overload
        def __init__(
                self, 
                *, 
                digest: Optional[ClaimDigest] = ..., 
                kind: Union[str, ApplicationClaimKind], 
                ledger_entry: Optional[LedgerEntryClaim] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ApplicationClaimKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLAIM_DIGEST = "ClaimDigest"
        LEDGER_ENTRY = "LedgerEntry"


    class azure.confidentialledger.models.ApplicationClaimProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEDGER_ENTRY_V1 = "LedgerEntryV1"


    class azure.confidentialledger.models.Bundle(_Model):
        metadata: Metadata
        modules: list[ModuleDef]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Metadata, 
                modules: list[ModuleDef]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ClaimDigest(_Model):
        protocol: Union[str, ApplicationClaimProtocol]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                protocol: Union[str, ApplicationClaimProtocol], 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.Collection(_Model):
        collection_id: str

        @overload
        def __init__(
                self, 
                *, 
                collection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ConfidentialLedgerEnclaves(_Model):
        current_node_id: str
        enclave_quotes: dict[str, EnclaveQuote]

        @overload
        def __init__(
                self, 
                *, 
                current_node_id: str, 
                enclave_quotes: dict[str, EnclaveQuote]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ConfidentialLedgerError(_Model):
        error: Optional[ConfidentialLedgerErrorBody]


    class azure.confidentialledger.models.ConfidentialLedgerErrorBody(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.confidentialledger.models.ConfidentialLedgerQueryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOADING = "Loading"
        READY = "Ready"


    class azure.confidentialledger.models.ConfidentialLedgerUserRoleName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATOR = "Administrator"
        CONTRIBUTOR = "Contributor"
        READER = "Reader"


    class azure.confidentialledger.models.ConsortiumMember(_Model):
        certificate: str
        id: str

        @overload
        def __init__(
                self, 
                *, 
                certificate: str, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.Constitution(_Model):
        digest: str
        script: str

        @overload
        def __init__(
                self, 
                *, 
                digest: str, 
                script: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.EnclaveQuote(_Model):
        mrenclave: Optional[str]
        node_id: str
        quote_version: str
        raw: str

        @overload
        def __init__(
                self, 
                *, 
                mrenclave: Optional[str] = ..., 
                node_id: str, 
                quote_version: str, 
                raw: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.EndpointProperties(_Model):
        authn_policies: list[dict[str, Any]]
        forwarding_required: Union[str, ForwardingRequired]
        interpreter_reuse: Optional[InterpreterReusePolicy]
        js_function: Optional[str]
        js_module: Optional[str]
        mode: Optional[Union[str, Mode]]
        openapi: Optional[dict[str, Any]]
        openapi_hidden: Optional[bool]
        redirection_strategy: Optional[Union[str, RedirectionStrategy]]

        @overload
        def __init__(
                self, 
                *, 
                authn_policies: list[dict[str, Any]], 
                forwarding_required: Union[str, ForwardingRequired], 
                interpreter_reuse: Optional[InterpreterReusePolicy] = ..., 
                js_function: Optional[str] = ..., 
                js_module: Optional[str] = ..., 
                mode: Optional[Union[str, Mode]] = ..., 
                openapi: Optional[dict[str, Any]] = ..., 
                openapi_hidden: Optional[bool] = ..., 
                redirection_strategy: Optional[Union[str, RedirectionStrategy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ForwardingRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "always"
        NEVER = "never"
        SOMETIMES = "sometimes"


    class azure.confidentialledger.models.InterpreterReusePolicy(_Model):
        key: str

        @overload
        def __init__(
                self, 
                *, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.JsRuntimeOptions(_Model):
        log_exception_details: Optional[bool]
        max_cached_interpreters: Optional[int]
        max_execution_time_ms: Optional[int]
        max_heap_bytes: Optional[int]
        max_stack_bytes: Optional[int]
        return_exception_details: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                log_exception_details: Optional[bool] = ..., 
                max_cached_interpreters: Optional[int] = ..., 
                max_execution_time_ms: Optional[int] = ..., 
                max_heap_bytes: Optional[int] = ..., 
                max_stack_bytes: Optional[int] = ..., 
                return_exception_details: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerEntry(_Model):
        collection_id: Optional[str]
        contents: str
        post_hooks: Optional[list[UserDefinedFunctionHook]]
        pre_hooks: Optional[list[UserDefinedFunctionHook]]
        transaction_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                contents: str, 
                post_hooks: Optional[list[UserDefinedFunctionHook]] = ..., 
                pre_hooks: Optional[list[UserDefinedFunctionHook]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerEntryClaim(_Model):
        collection_id: Optional[str]
        contents: Optional[str]
        protocol: Union[str, ApplicationClaimProtocol]
        secret_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                contents: Optional[str] = ..., 
                protocol: Union[str, ApplicationClaimProtocol], 
                secret_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerQueryResult(_Model):
        entry: Optional[LedgerEntry]
        state: Union[str, ConfidentialLedgerQueryState]

        @overload
        def __init__(
                self, 
                *, 
                entry: Optional[LedgerEntry] = ..., 
                state: Union[str, ConfidentialLedgerQueryState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerUser(_Model):
        assigned_role: Union[str, ConfidentialLedgerUserRoleName]
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_role: Union[str, ConfidentialLedgerUserRoleName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerUserMultipleRoles(_Model):
        assigned_roles: list[Union[str, ConfidentialLedgerUserRoleName]]
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assigned_roles: list[Union[str, ConfidentialLedgerUserRoleName]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.LedgerWriteResult(_Model):
        collection_id: str

        @overload
        def __init__(
                self, 
                *, 
                collection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.Metadata(_Model):
        endpoints: dict[str, MethodToEndpointProperties]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: dict[str, MethodToEndpointProperties]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.MethodToEndpointProperties(_Model):
        delete: Optional[EndpointProperties]
        get_property: Optional[EndpointProperties]
        patch: Optional[EndpointProperties]
        put: Optional[EndpointProperties]

        @overload
        def __init__(
                self, 
                *, 
                delete: Optional[EndpointProperties] = ..., 
                get_property: Optional[EndpointProperties] = ..., 
                patch: Optional[EndpointProperties] = ..., 
                put: Optional[EndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HISTORICAL = "historical"
        READONLY = "readonly"
        READWRITE = "readwrite"


    class azure.confidentialledger.models.ModuleDef(_Model):
        module: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                module: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ReceiptContents(_Model):
        cert: Optional[str]
        leaf: Optional[str]
        leaf_components: Optional[ReceiptLeafComponents]
        node_id: str
        proof: list[ReceiptElement]
        root: Optional[str]
        service_endorsements: Optional[list[str]]
        signature: str

        @overload
        def __init__(
                self, 
                *, 
                cert: Optional[str] = ..., 
                leaf: Optional[str] = ..., 
                leaf_components: Optional[ReceiptLeafComponents] = ..., 
                node_id: str, 
                proof: list[ReceiptElement], 
                root: Optional[str] = ..., 
                service_endorsements: Optional[list[str]] = ..., 
                signature: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ReceiptElement(_Model):
        left: Optional[str]
        right: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                left: Optional[str] = ..., 
                right: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.ReceiptLeafComponents(_Model):
        claims_digest: Optional[str]
        commit_evidence: Optional[str]
        write_set_digest: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                claims_digest: Optional[str] = ..., 
                commit_evidence: Optional[str] = ..., 
                write_set_digest: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.RedirectionStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        TO_BACKUP = "to_backup"
        TO_PRIMARY = "to_primary"


    class azure.confidentialledger.models.Role(_Model):
        role_actions: Optional[list[str]]
        role_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                role_actions: Optional[list[str]] = ..., 
                role_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.Roles(_Model):
        roles: list[Role]

        @overload
        def __init__(
                self, 
                *, 
                roles: list[Role]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.TransactionReceipt(_Model):
        application_claims: Optional[list[ApplicationClaim]]
        receipt: Optional[ReceiptContents]
        state: Union[str, ConfidentialLedgerQueryState]
        transaction_id: str

        @overload
        def __init__(
                self, 
                *, 
                application_claims: Optional[list[ApplicationClaim]] = ..., 
                receipt: Optional[ReceiptContents] = ..., 
                state: Union[str, ConfidentialLedgerQueryState], 
                transaction_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.TransactionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITTED = "Committed"
        PENDING = "Pending"


    class azure.confidentialledger.models.TransactionStatus(_Model):
        state: Union[str, TransactionState]
        transaction_id: str

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, TransactionState], 
                transaction_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunction(_Model):
        code: str
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunctionExecutionError(_Model):
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunctionExecutionProperties(_Model):
        arguments: Optional[list[str]]
        exported_function_name: Optional[str]
        runtime_options: Optional[JsRuntimeOptions]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[list[str]] = ..., 
                exported_function_name: Optional[str] = ..., 
                runtime_options: Optional[JsRuntimeOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunctionExecutionResponse(_Model):
        error: Optional[UserDefinedFunctionExecutionError]
        result: Optional[UserDefinedFunctionExecutionResult]
        status: Union[str, UserDefinedFunctionExecutionStatus]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[UserDefinedFunctionExecutionError] = ..., 
                result: Optional[UserDefinedFunctionExecutionResult] = ..., 
                status: Union[str, UserDefinedFunctionExecutionStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunctionExecutionResult(_Model):
        return_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                return_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.confidentialledger.models.UserDefinedFunctionExecutionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.confidentialledger.models.UserDefinedFunctionHook(_Model):
        function_id: str
        properties: Optional[UserDefinedFunctionExecutionProperties]

        @overload
        def __init__(
                self, 
                *, 
                function_id: str, 
                properties: Optional[UserDefinedFunctionExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.confidentialledger.receipt

    def azure.confidentialledger.receipt.compute_claims_digest(application_claims: List[Dict[str, Any]]) -> str: ...


    def azure.confidentialledger.receipt.verify_receipt(
            receipt: Dict[str, Any], 
            service_cert: str, 
            *, 
            application_claims: Optional[List[Dict[str, Any]]] = ...
        ) -> None: ...


```