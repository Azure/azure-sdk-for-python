```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.core

    class azure.mgmt.core.ARMPipelineClient(PipelineClient[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                base_url: str, 
                *, 
                per_call_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                per_retry_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                pipeline: Optional[Pipeline] = ..., 
                policies: Optional[list[HTTPPolicy]] = ..., 
                transport: Optional[HttpTransport] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.core.AsyncARMPipelineClient(AsyncPipelineClient[HTTPRequestType, AsyncHTTPResponseType]):

        def __init__(
                self, 
                base_url: str, 
                *, 
                per_call_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy, list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                per_retry_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy, list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                pipeline: Optional[AsyncPipeline] = ..., 
                policies: Optional[list[AsyncHTTPPolicy]] = ..., 
                transport: Optional[AsyncHttpTransport] = ..., 
                **kwargs: Any
            ): ...


namespace azure.mgmt.core.exceptions

    class azure.mgmt.core.exceptions.ARMErrorFormat(ODataV4Format):
        property error: SelfODataV4Format    # Read-only
        CODE_LABEL = code
        DETAILS_LABEL = details
        INNERERROR_LABEL = innererror
        MESSAGE_LABEL = message
        TARGET_LABEL = target

        def __init__(self, json_object: Mapping[str, Any]) -> None: ...

        def __str__(self) -> str: ...


    class azure.mgmt.core.exceptions.TypedErrorInfo:

        def __init__(
                self, 
                type: str, 
                info: Mapping[str, Any]
            ) -> None: ...

        def __str__(self) -> str: ...


namespace azure.mgmt.core.policies

    class azure.mgmt.core.policies.ARMAutoResourceProviderRegistrationPolicy(_SansIOARMAutoResourceProviderRegistrationPolicy, HTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...


    class azure.mgmt.core.policies.ARMChallengeAuthenticationPolicy(BearerTokenCredentialPolicy):


    class azure.mgmt.core.policies.ARMHttpLoggingPolicy(HttpLoggingPolicy):
        MULTI_RECORD_LOG = AZURE_SDK_LOGGING_MULTIRECORD
        REDACTED_PLACEHOLDER = REDACTED


    class azure.mgmt.core.policies.AsyncARMAutoResourceProviderRegistrationPolicy(_SansIOARMAutoResourceProviderRegistrationPolicy, AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):

        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.mgmt.core.policies.AsyncARMChallengeAuthenticationPolicy(AsyncBearerTokenCredentialPolicy):


    class azure.mgmt.core.policies.AsyncAuxiliaryAuthenticationPolicy(_AuxiliaryAuthenticationPolicyBase[AsyncTokenCredential], AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):

        def __init__(
                self, 
                auxiliary_credentials: Sequence[TokenCredentialType], 
                *scopes: str, 
                **kwargs: Any
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        async def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]
            ) -> Optional[Awaitable[None]]: ...

        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.mgmt.core.policies.AuxiliaryAuthenticationPolicy(_AuxiliaryAuthenticationPolicyBase[TokenCredential], SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                auxiliary_credentials: Sequence[TokenCredentialType], 
                *scopes: str, 
                **kwargs: Any
            ) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...


namespace azure.mgmt.core.polling.arm_polling

    class azure.mgmt.core.polling.arm_polling.ARMPolling(LROBasePolling):

        def __init__(
                self, 
                timeout: float = 30, 
                lro_algorithms: Optional[Sequence[LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]]] = None, 
                lro_options: Optional[Dict[str, Any]] = None, 
                path_format_arguments: Optional[Dict[str, str]] = None, 
                **operation_config: Any
            ) -> None: ...


    class azure.mgmt.core.polling.arm_polling.AzureAsyncOperationPolling(OperationResourcePolling[HttpRequestTypeVar, AllHttpResponseTypeVar]):

        def __init__(self, lro_options: Optional[Dict[str, Any]] = None) -> None: ...

        def get_final_get_url(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> Optional[str]: ...


    class azure.mgmt.core.polling.arm_polling.BodyContentPolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):

        def can_poll(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> bool: ...

        def get_final_get_url(self, pipeline_response: Any) -> None: ...

        def get_polling_url(self) -> str: ...

        def get_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...

        def set_initial_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...


namespace azure.mgmt.core.polling.async_arm_polling

    class azure.mgmt.core.polling.async_arm_polling.AsyncARMPolling(AsyncLROBasePolling):

        def __init__(
                self, 
                timeout: float = 30, 
                lro_algorithms: Optional[Sequence[LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]]] = None, 
                lro_options: Optional[Dict[str, Any]] = None, 
                path_format_arguments: Optional[Dict[str, str]] = None, 
                **operation_config: Any
            ) -> None: ...


namespace azure.mgmt.core.tools

    def azure.mgmt.core.tools.get_arm_endpoints(cloud_setting: AzureClouds) -> Dict[str, Any]: ...


    def azure.mgmt.core.tools.is_valid_resource_id(rid: str, exception_type: Optional[Type[BaseException]] = None) -> bool: ...


    def azure.mgmt.core.tools.is_valid_resource_name(rname: str, exception_type: Optional[Type[BaseException]] = None) -> bool: ...


    def azure.mgmt.core.tools.parse_resource_id(rid: str) -> Mapping[str, Union[str, int]]: ...


    def azure.mgmt.core.tools.resource_id(
            *, 
            child_name_{level}: Optional[str] = ..., 
            child_namespace_{level}: Optional[str] = ..., 
            child_type_{level}: Optional[str] = ..., 
            name: Optional[str] = ..., 
            namespace: Optional[str] = ..., 
            resource_group: Optional[str] = ..., 
            subscription: Optional[str] = ..., 
            type: Optional[str] = ..., 
            **kwargs: Optional[str]
        ) -> str: ...


```