```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.identity

    def azure.identity.get_bearer_token_provider(credential: TokenProvider, *scopes: str) -> Callable[[], str]: ...


    class azure.identity.AuthenticationRecord:
        property authority: str    # Read-only
        property client_id: str    # Read-only
        property home_account_id: str    # Read-only
        property tenant_id: str    # Read-only
        property username: str    # Read-only

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                authority: str, 
                home_account_id: str, 
                username: str
            ) -> None: ...

        @classmethod
        def deserialize(cls, data: str) -> AuthenticationRecord: ...

        def serialize(self) -> str: ...


    class azure.identity.AuthenticationRequiredError(CredentialUnavailableError):
        property claims: Optional[str]    # Read-only
        property scopes: Iterable[str]    # Read-only

        def __init__(
                self, 
                scopes: Iterable[str], 
                message: Optional[str] = None, 
                claims: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...


    class azure.identity.AuthorizationCodeCredential(GetTokenMixin): implements ContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                authorization_code: str, 
                redirect_uri: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.AzureAuthorityHosts(metaclass=AzureAuthorityHostsMeta):
        AZURE_CHINA = login.chinacloudapi.cn
        AZURE_GOVERNMENT = login.microsoftonline.us
        AZURE_PUBLIC_CLOUD = login.microsoftonline.com


    class azure.identity.AzureCliCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                subscription: Optional[str] = ..., 
                tenant_id: str = ""
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.AzureDeveloperCliCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                tenant_id: str = ""
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.AzurePipelinesCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_id: str, 
                service_connection_id: str, 
                system_access_token: str, 
                tenant_id: str, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.AzurePowerShellCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                tenant_id: str = ""
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.CertificateCredential(ClientCredentialBase): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                certificate_path: Optional[str] = None, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                certificate_data: Optional[bytes] = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                password: Union[str, bytes] = ..., 
                send_certificate_chain: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.ChainedTokenCredential: implements ContextManager 

        def __init__(self, *credentials: TokenProvider) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.ClientAssertionCredential(GetTokenMixin): implements ContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                func: Callable[[], str], 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.ClientSecretCredential(ClientCredentialBase): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                client_secret: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.CredentialUnavailableError(ClientAuthenticationError):


    class azure.identity.DefaultAzureCredential(ChainedTokenCredential): implements ContextManager 

        def __init__(
                self, 
                *, 
                authority: Optional[str] = ..., 
                broker_client_id: Optional[str] = ..., 
                broker_tenant_id: Optional[str] = ..., 
                exclude_broker_credential: Optional[bool] = ..., 
                exclude_cli_credential: Optional[bool] = ..., 
                exclude_developer_cli_credential: Optional[bool] = ..., 
                exclude_environment_credential: Optional[bool] = ..., 
                exclude_interactive_browser_credential: Optional[bool] = ..., 
                exclude_managed_identity_credential: Optional[bool] = ..., 
                exclude_powershell_credential: Optional[bool] = ..., 
                exclude_shared_token_cache_credential: Optional[bool] = ..., 
                exclude_visual_studio_code_credential: Optional[bool] = ..., 
                exclude_workload_identity_credential: Optional[bool] = ..., 
                interactive_browser_client_id: Optional[str] = ..., 
                interactive_browser_tenant_id: Optional[str] = ..., 
                managed_identity_client_id: Optional[str] = ..., 
                process_timeout: Optional[int] = ..., 
                require_envvar: Optional[bool] = ..., 
                shared_cache_tenant_id: Optional[str] = ..., 
                shared_cache_username: Optional[str] = ..., 
                visual_studio_code_tenant_id: Optional[str] = ..., 
                workload_identity_client_id: Optional[str] = ..., 
                workload_identity_tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.DeviceCodeCredential(InteractiveCredential): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                client_id: str = DEVELOPER_SIGN_ON_CLIENT_ID, 
                *, 
                authentication_record: Optional[AuthenticationRecord] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                disable_automatic_authentication: Optional[bool] = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                enable_support_logging: Optional[bool] = ..., 
                prompt_callback: Optional[Callable[[str, str, datetime], None]] = ..., 
                tenant_id: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def authenticate(
                self, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                scopes: Optional[Iterable[str]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AuthenticationRecord: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.EnvironmentCredential: implements ContextManager 

        def __init__(self, **kwargs: Any) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.InteractiveBrowserCredential(InteractiveCredential): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                *, 
                authentication_record: Optional[AuthenticationRecord] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                client_id: Optional[str] = ..., 
                disable_automatic_authentication: Optional[bool] = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                enable_support_logging: Optional[bool] = ..., 
                login_hint: Optional[str] = ..., 
                redirect_uri: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def authenticate(
                self, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                scopes: Optional[Iterable[str]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AuthenticationRecord: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.KnownAuthorities(AzureAuthorityHosts):
        AZURE_CHINA = login.chinacloudapi.cn
        AZURE_GOVERNMENT = login.microsoftonline.us
        AZURE_PUBLIC_CLOUD = login.microsoftonline.com


    class azure.identity.ManagedIdentityCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                identity_config: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.OnBehalfOfCredential(MsalCredential, GetTokenMixin): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_assertion_func: Optional[Callable[[], str]] = ..., 
                client_certificate: Optional[bytes] = ..., 
                client_secret: Optional[str] = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                password: Optional[Union[bytes, str]] = ..., 
                send_certificate_chain: bool = False, 
                user_assertion: str, 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.SharedTokenCacheCredential: implements ContextManager 

        def __init__(
                self, 
                username: Optional[str] = None, 
                *, 
                authentication_record: Optional[AuthenticationRecord] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token
        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...

        @staticmethod
        def supported() -> bool: ...


    class azure.identity.TokenCachePersistenceOptions:

        def __init__(
                self, 
                *, 
                allow_unencrypted_storage: bool = False, 
                name: str = "msal.cache", 
                **kwargs: Any
            ) -> None: ...


    class azure.identity.UsernamePasswordCredential(InteractiveCredential): implements ContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                client_id: str, 
                username: str, 
                password: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                enable_support_logging: Optional[bool] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def authenticate(
                self, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                scopes: Optional[Iterable[str]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AuthenticationRecord: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.VisualStudioCodeCredential: implements ContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @log_get_token
        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.WorkloadIdentityCredential(ClientAssertionCredential, TokenFileMixin): implements ContextManager 

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                token_file_path: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


namespace azure.identity.aio

    def azure.identity.aio.get_bearer_token_provider(credential: AsyncTokenProvider, *scopes: str) -> Callable[[], Coroutine[Any, Any, str]]: ...


    class azure.identity.aio.AuthorizationCodeCredential(AsyncContextManager, GetTokenMixin): implements AsyncContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                authorization_code: str, 
                redirect_uri: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.AzureCliCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                subscription: Optional[str] = ..., 
                tenant_id: str = ""
            ) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.AzureDeveloperCliCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                tenant_id: str = ""
            ) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.AzurePipelinesCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_id: str, 
                service_connection_id: str, 
                system_access_token: str, 
                tenant_id: str, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.AzurePowerShellCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                process_timeout: int = 10, 
                tenant_id: str = ""
            ) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.CertificateCredential(AsyncContextManager, GetTokenMixin): implements AsyncContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                certificate_path: Optional[str] = None, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                certificate_data: Optional[bytes] = ..., 
                password: Union[str, bytes] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.ChainedTokenCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(self, *credentials: AsyncTokenProvider) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.ClientAssertionCredential(AsyncContextManager, GetTokenMixin): implements AsyncContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                func: Callable[[], str], 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.ClientSecretCredential(AsyncContextManager, GetTokenMixin): implements AsyncContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                client_secret: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.DefaultAzureCredential(ChainedTokenCredential): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                authority: Optional[str] = ..., 
                exclude_cli_credential: Optional[bool] = ..., 
                exclude_developer_cli_credential: Optional[bool] = ..., 
                exclude_environment_credential: Optional[bool] = ..., 
                exclude_managed_identity_credential: Optional[bool] = ..., 
                exclude_powershell_credential: Optional[bool] = ..., 
                exclude_shared_token_cache_credential: Optional[bool] = ..., 
                exclude_visual_studio_code_credential: Optional[bool] = ..., 
                exclude_workload_identity_credential: Optional[bool] = ..., 
                managed_identity_client_id: Optional[str] = ..., 
                process_timeout: Optional[int] = ..., 
                require_envvar: Optional[bool] = ..., 
                shared_cache_tenant_id: Optional[str] = ..., 
                shared_cache_username: Optional[str] = ..., 
                visual_studio_code_tenant_id: Optional[str] = ..., 
                workload_identity_client_id: Optional[str] = ..., 
                workload_identity_tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.EnvironmentCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(self, **kwargs: Any) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.ManagedIdentityCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                identity_config: Optional[Mapping[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.OnBehalfOfCredential(AsyncContextManager, GetTokenMixin): implements AsyncContextManager 

        def __init__(
                self, 
                tenant_id: str, 
                client_id: str, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                authority: Optional[str] = ..., 
                client_assertion_func: Optional[Callable[[], str]] = ..., 
                client_certificate: Optional[bytes] = ..., 
                client_secret: Optional[str] = ..., 
                password: Optional[Union[str, bytes]] = ..., 
                user_assertion: str, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.SharedTokenCacheCredential(SharedTokenCacheBase, AsyncContextManager): implements AsyncContextManager 

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                username: Optional[str] = None, 
                *, 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @log_get_token_async
        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...

        @staticmethod
        def supported() -> bool: ...


    class azure.identity.aio.VisualStudioCodeCredential(AsyncContextManager): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                additionally_allowed_tenants: Optional[List[str]] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @log_get_token_async
        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    class azure.identity.aio.WorkloadIdentityCredential(ClientAssertionCredential, TokenFileMixin): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                token_file_path: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


```