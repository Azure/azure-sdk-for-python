```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.appconfiguration.provider

    @overload
    def azure.appconfiguration.provider.load(
            endpoint: str, 
            credential: TokenCredential, 
            *, 
            feature_flag_enabled: bool = False, 
            feature_flag_refresh_enabled: bool = False, 
            feature_flag_selectors: Optional[List[SettingSelector]] = ..., 
            key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = ..., 
            keyvault_client_configs: Optional[Mapping[str, JSON]] = ..., 
            keyvault_credential: Optional[TokenCredential] = ..., 
            on_refresh_error: Optional[Callable[[Exception], None]] = ..., 
            on_refresh_success: Optional[Callable] = ..., 
            refresh_enabled: Optional[bool] = ..., 
            refresh_interval: int = 30, 
            refresh_on: Optional[List[Tuple[str, str]]] = ..., 
            secret_resolver: Optional[Callable[[str], str]] = ..., 
            selects: Optional[List[SettingSelector]] = ..., 
            startup_timeout: int = DEFAULT_STARTUP_TIMEOUT, 
            trim_prefixes: Optional[List[str]] = ..., 
            **kwargs
        ) -> AzureAppConfigurationProvider: ...


    @overload
    def azure.appconfiguration.provider.load(
            *, 
            connection_string: str, 
            feature_flag_enabled: bool = False, 
            feature_flag_refresh_enabled: bool = False, 
            feature_flag_selectors: Optional[List[SettingSelector]] = ..., 
            key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = ..., 
            keyvault_client_configs: Optional[Mapping[str, JSON]] = ..., 
            keyvault_credential: Optional[TokenCredential] = ..., 
            on_refresh_error: Optional[Callable[[Exception], None]] = ..., 
            on_refresh_success: Optional[Callable] = ..., 
            refresh_enabled: Optional[bool] = ..., 
            refresh_interval: int = 30, 
            refresh_on: Optional[List[Tuple[str, str]]] = ..., 
            secret_resolver: Optional[Callable[[str], str]] = ..., 
            selects: Optional[List[SettingSelector]] = ..., 
            startup_timeout: int = DEFAULT_STARTUP_TIMEOUT, 
            trim_prefixes: Optional[List[str]] = ..., 
            **kwargs
        ) -> AzureAppConfigurationProvider: ...


    class azure.appconfiguration.provider.AzureAppConfigurationKeyVaultOptions:

        def __init__(
                self, 
                *, 
                client_configs: Optional[Mapping[str, Mapping[str, Any]]] = ..., 
                credential: Optional[Union[TokenCredential, AsyncTokenCredential]] = ..., 
                secret_resolver: Optional[Union[Callable[[str], str], Callable[[str], Awaitable[str]]]] = ...
            ): ...


    class azure.appconfiguration.provider.AzureAppConfigurationProvider(AzureAppConfigurationProviderBase): implements ContextManager , Collection , Mapping 

        def __init__(self, **kwargs: Any) -> None: ...

        def close(self) -> None: ...

        def refresh(self, **kwargs) -> None: ...


    class azure.appconfiguration.provider.SettingSelector:

        def __init__(
                self, 
                *, 
                key_filter: Optional[str] = ..., 
                label_filter: Optional[str] = NULL_CHAR, 
                snapshot_name: Optional[str] = ..., 
                tag_filters: Optional[List[str]] = ...
            ): ...


    class azure.appconfiguration.provider.WatchKey(NamedTuple):
        key: str
        label: str


namespace azure.appconfiguration.provider.aio

    @overload
    async def azure.appconfiguration.provider.aio.load:async(
            endpoint: str, 
            credential: AsyncTokenCredential, 
            *, 
            feature_flag_enabled: bool = False, 
            feature_flag_refresh_enabled: bool = False, 
            feature_flag_selectors: Optional[List[SettingSelector]] = ..., 
            key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = ..., 
            keyvault_client_configs: Optional[Mapping[str, JSON]] = ..., 
            keyvault_credential: Optional[AsyncTokenCredential] = ..., 
            on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]] = ..., 
            on_refresh_success: Optional[Callable] = ..., 
            refresh_enabled: Optional[bool] = ..., 
            refresh_interval: int = 30, 
            refresh_on: Optional[List[Tuple[str, str]]] = ..., 
            secret_resolver: Optional[Callable[[str], str]] = ..., 
            selects: Optional[List[SettingSelector]] = ..., 
            startup_timeout: int = DEFAULT_STARTUP_TIMEOUT, 
            trim_prefixes: Optional[List[str]] = ..., 
            **kwargs
        ) -> AzureAppConfigurationProvider: ...


    @overload
    async def azure.appconfiguration.provider.aio.load:async(
            *, 
            connection_string: str, 
            feature_flag_enabled: bool = False, 
            feature_flag_refresh_enabled: bool = False, 
            feature_flag_selectors: Optional[List[SettingSelector]] = ..., 
            key_vault_options: Optional[AzureAppConfigurationKeyVaultOptions] = ..., 
            keyvault_client_configs: Optional[Mapping[str, JSON]] = ..., 
            keyvault_credential: Optional[AsyncTokenCredential] = ..., 
            on_refresh_error: Optional[Callable[[Exception], Awaitable[None]]] = ..., 
            on_refresh_success: Optional[Callable] = ..., 
            refresh_enabled: Optional[bool] = ..., 
            refresh_interval: int = 30, 
            refresh_on: Optional[List[Tuple[str, str]]] = ..., 
            secret_resolver: Optional[Callable[[str], str]] = ..., 
            selects: Optional[List[SettingSelector]] = ..., 
            startup_timeout: int = DEFAULT_STARTUP_TIMEOUT, 
            trim_prefixes: Optional[List[str]] = ..., 
            **kwargs
        ) -> AzureAppConfigurationProvider: ...


    class azure.appconfiguration.provider.aio.AzureAppConfigurationProvider(AzureAppConfigurationProviderBase): implements AsyncContextManager , Collection , Mapping 

        def __init__(self, **kwargs: Any) -> None: ...

        async def close(self) -> None: ...

        async def refresh(self, **kwargs) -> None: ...


```