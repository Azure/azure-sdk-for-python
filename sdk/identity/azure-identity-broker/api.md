```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.identity.broker

    class azure.identity.broker.InteractiveBrowserBrokerCredential(_InteractiveBrowserCredential):

        def __init__(
                self, 
                *, 
                authority: Optional[str] = ..., 
                cache_persistence_options: TokenCachePersistenceOptions = ..., 
                client_id: Optional[str] = ..., 
                disable_instance_discovery: Optional[bool] = ..., 
                enable_msa_passthrough: Optional[bool] = ..., 
                enable_support_logging: Optional[bool] = ..., 
                login_hint: Optional[str] = ..., 
                parent_window_handle: Optional[int] = ..., 
                tenant_id: Optional[str] = ..., 
                timeout: Optional[int] = ..., 
                use_default_broker_account: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.identity.broker.PopTokenRequestOptions(TokenRequestOptions):
        key "claims": str
        key "enable_cae": bool
        key "pop": Union[bool, Mapping[str, str]]
        key "tenant_id": str


```