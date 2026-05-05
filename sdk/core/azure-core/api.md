```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.core

    class azure.core.AsyncPipelineClient(PipelineClientBase, AsyncContextManager[AsyncPipelineClient], Generic[HTTPRequestType, AsyncHTTPResponseType]): implements AsyncContextManager 

        def __init__(
                self, 
                base_url: str, 
                *, 
                config: Optional[Configuration[HTTPRequestType, AsyncHTTPResponseType]] = ..., 
                per_call_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy, list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                per_retry_policies: Union[AsyncHTTPPolicy, SansIOHTTPPolicy, list[AsyncHTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                pipeline: Optional[AsyncPipeline[HTTPRequestType, AsyncHTTPResponseType]] = ..., 
                policies: Optional[list[AsyncHTTPPolicy]] = ..., 
                transport: Optional[AsyncHttpTransport] = ..., 
                **kwargs: Any
            ) -> AsyncPipeline: ...

        async def close(self) -> None: ...

        def delete(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def format_url(
                self, 
                url_template: str, 
                **kwargs: Any
            ) -> str: ...

        def get(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def head(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def merge(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def options(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                *, 
                content: Optional[Union[bytes, str, Dict[Any, Any]]] = ..., 
                form_content: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ) -> HttpRequest: ...

        def patch(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def post(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def put(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def send_request(
                self, 
                request: HTTPRequestType, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHTTPResponseType]: ...


    class azure.core.AzureClouds(str, Enum):
        AZURE_CHINA_CLOUD = "AZURE_CHINA_CLOUD"
        AZURE_PUBLIC_CLOUD = "AZURE_PUBLIC_CLOUD"
        AZURE_US_GOVERNMENT = "AZURE_US_GOVERNMENT"


    class azure.core.CaseInsensitiveEnumMeta(EnumMeta):

        def __getattr__(cls, name: str) -> Enum: ...

        def __getitem__(cls, name: str) -> Any: ...


    class azure.core.MatchConditions(Enum):
        IfMissing = 5
        IfModified = 3
        IfNotModified = 2
        IfPresent = 4
        Unconditionally = 1


    class azure.core.PipelineClient(PipelineClientBase, Generic[HTTPRequestType, HTTPResponseType]): implements ContextManager 

        def __init__(
                self, 
                base_url: str, 
                *, 
                config: Optional[Configuration[HTTPRequestType, HTTPResponseType]] = ..., 
                per_call_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                per_retry_policies: Union[HTTPPolicy, SansIOHTTPPolicy, list[HTTPPolicy], list[SansIOHTTPPolicy]] = ..., 
                pipeline: Optional[Pipeline[HTTPRequestType, HTTPResponseType]] = ..., 
                policies: Optional[list[HTTPPolicy]] = ..., 
                transport: Optional[HttpTransport] = ..., 
                **kwargs: Any
            ) -> Pipeline: ...

        def close(self) -> None: ...

        def delete(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def format_url(
                self, 
                url_template: str, 
                **kwargs: Any
            ) -> str: ...

        def get(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def head(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def merge(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None
            ) -> HttpRequest: ...

        def options(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                *, 
                content: Optional[Union[bytes, str, Dict[Any, Any]]] = ..., 
                form_content: Optional[Dict[Any, Any]] = ..., 
                **kwargs: Any
            ) -> HttpRequest: ...

        def patch(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def post(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def put(
                self, 
                url: str, 
                params: Optional[Dict[str, str]] = None, 
                headers: Optional[Dict[str, str]] = None, 
                content: Any = None, 
                form_content: Optional[Dict[str, Any]] = None, 
                stream_content: Any = None
            ) -> HttpRequest: ...

        def send_request(
                self, 
                request: HTTPRequestType, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HTTPResponseType: ...


namespace azure.core.async_paging

    class azure.core.async_paging.AsyncItemPaged(AsyncIterator[ReturnType]):

        async def __anext__(self) -> ReturnType: ...

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def by_page(self, continuation_token: Optional[str] = None) -> AsyncIterator[AsyncIterator[ReturnType]]: ...


    class azure.core.async_paging.AsyncPageIterator(AsyncIterator[AsyncIterator[ReturnType]]):

        async def __anext__(self) -> AsyncIterator[ReturnType]: ...

        def __init__(
                self, 
                get_next: Callable[[Optional[str]], Awaitable[ResponseType]], 
                extract_data: Callable[[ResponseType], Awaitable[Tuple[str, AsyncIterator[ReturnType]]]], 
                continuation_token: Optional[str] = None
            ) -> None: ...


namespace azure.core.configuration

    class azure.core.configuration.Configuration(Generic[HTTPRequestType, HTTPResponseType]):
        authentication_policy
        custom_hook_policy
        headers_policy
        http_logging_policy
        logging_policy
        proxy_policy
        redirect_policy
        request_id_policy
        retry_policy
        user_agent_policy

        def __init__(
                self, 
                *, 
                polling_interval = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.core.configuration.ConnectionConfiguration:

        def __init__(
                self, 
                *, 
                connection_cert: Optional[str] = ..., 
                connection_data_block_size: int = 4096, 
                connection_timeout: float = 300, 
                connection_verify: Union[bool, str] = True, 
                read_timeout: float = 300, 
                **kwargs: Any
            ) -> None: ...


namespace azure.core.credentials

    class azure.core.credentials.AccessToken(NamedTuple):
        expires_on: int
        token: str


    class azure.core.credentials.AccessTokenInfo:
        expires_on: int
        refresh_on: Optional[int]
        token: str
        token_type: str

        def __init__(
                self, 
                token: str, 
                expires_on: int, 
                *, 
                refresh_on: Optional[int] = ..., 
                token_type: str = "Bearer"
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.core.credentials.AzureKeyCredential:
        property key: str    # Read-only

        def __init__(self, key: str) -> None: ...

        def update(self, key: str) -> None: ...


    class azure.core.credentials.AzureNamedKeyCredential:
        property named_key: AzureNamedKey    # Read-only

        def __init__(
                self, 
                name: str, 
                key: str
            ) -> None: ...

        def update(
                self, 
                name: str, 
                key: str
            ) -> None: ...


    class azure.core.credentials.AzureSasCredential:
        property signature: str    # Read-only

        def __init__(self, signature: str) -> None: ...

        def update(self, signature: str) -> None: ...


    @runtime_checkable
    class azure.core.credentials.SupportsTokenInfo(Protocol, ContextManager[SupportsTokenInfo]):

        def close(self) -> None: ...

        def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    @runtime_checkable
    class azure.core.credentials.TokenCredential(Protocol):

        def get_token(
                self, 
                *scopes: str, 
                *, 
                claims: Optional[str] = ..., 
                enable_cae: bool = False, 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...


    class azure.core.credentials.TokenRequestOptions(TypedDict, total=False):
        key "claims": str
        key "enable_cae": bool
        key "tenant_id": str


namespace azure.core.credentials_async

    @runtime_checkable
    class azure.core.credentials_async.AsyncSupportsTokenInfo(Protocol, AsyncContextManager[AsyncSupportsTokenInfo]):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
            ) -> None: ...

        async def close(self) -> None: ...

        async def get_token_info(
                self, 
                *scopes: str, 
                *, 
                options: Optional[TokenRequestOptions] = ..., 
            ) -> AccessTokenInfo: ...


    @runtime_checkable
    class azure.core.credentials_async.AsyncTokenCredential(Protocol, AsyncContextManager[AsyncTokenCredential]):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
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


namespace azure.core.exceptions

    class azure.core.exceptions.AzureError(Exception):
        continuation_token: str
        exc_msg
        exc_traceback
        exc_type
        exc_value
        inner_exception: Exception
        message: str

        def __init__(
                self, 
                message: Optional[object], 
                *args: Any, 
                *, 
                error: Exception = ..., 
                **kwargs: Any
            ) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ClientAuthenticationError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.DecodeError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.DeserializationError(ValueError):


    class azure.core.exceptions.HttpResponseError(AzureError):
        error: ODataV4Format
        model: Model
        reason: str
        response: Union[HttpResponse, AsyncHttpResponse]
        status_code: int

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ODataV4Error(HttpResponseError):
        details: list[ODataV4Format]
        innererror: dict
        message: str
        odata_json: dict
        target: str
        ~.code: str

        def __init__(
                self, 
                response: _HttpResponseCommonAPI, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ODataV4Format:
        property error: SelfODataV4Format    # Read-only
        CODE_LABEL = code
        DETAILS_LABEL = details
        INNERERROR_LABEL = innererror
        MESSAGE_LABEL = message
        TARGET_LABEL = target
        code: str
        details: list[ODataV4Format]
        innererror: dict
        message: str
        target: str

        def __init__(self, json_object: Mapping[str, Any]) -> None: ...

        def __str__(self) -> str: ...

        def message_details(self) -> str: ...


    class azure.core.exceptions.ResourceExistsError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ResourceModifiedError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ResourceNotFoundError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ResourceNotModifiedError(HttpResponseError):

        def __init__(
                self, 
                message: Optional[object] = None, 
                response: Optional[_HttpResponseCommonAPI] = None, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ResponseNotReadError(AzureError):

        def __init__(self, response: _HttpResponseCommonAPI) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.SerializationError(ValueError):


    class azure.core.exceptions.ServiceRequestError(AzureError):

        def __init__(
                self, 
                message: Optional[object], 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.ServiceResponseError(AzureError):

        def __init__(
                self, 
                message: Optional[object], 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.StreamClosedError(AzureError):

        def __init__(self, response: _HttpResponseCommonAPI) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.StreamConsumedError(AzureError):

        def __init__(self, response: _HttpResponseCommonAPI) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.exceptions.TooManyRedirectsError(HttpResponseError, Generic[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                history: List[RequestHistory[HTTPRequestType, HTTPResponseType]], 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def __str__(self) -> str: ...

        def raise_with_traceback(self) -> None: ...


namespace azure.core.instrumentation

    def azure.core.instrumentation.get_tracer(
            *, 
            attributes: Optional[Mapping[str, Union[str, bool, int, float]]] = ..., 
            library_name: Optional[str] = ..., 
            library_version: Optional[str] = ..., 
            schema_url: Optional[str] = ...
        ) -> Optional[OpenTelemetryTracer]: ...


namespace azure.core.messaging

    class azure.core.messaging.CloudEvent(Generic[DataType]):
        data: Optional[DataType]
        datacontenttype: Optional[str]
        dataschema: Optional[str]
        extensions: Optional[Dict[str, Any]]
        id: str
        source: str
        specversion: str = "1.0"
        subject: Optional[str]
        time: Optional[datetime]
        type: str

        def __init__(
                self, 
                source: str, 
                type: str, 
                *, 
                data: Optional[DataType] = ..., 
                datacontenttype: Optional[str] = ..., 
                dataschema: Optional[str] = ..., 
                extensions: Optional[Dict[str, Any]] = ..., 
                id: Optional[str] = ..., 
                specversion: Optional[str] = ..., 
                subject: Optional[str] = ..., 
                time: Optional[datetime] = _Unset, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def from_dict(cls, event: Dict[str, Any]) -> CloudEvent[DataType]: ...

        @classmethod
        def from_json(cls, event: Any) -> CloudEvent[DataType]: ...


namespace azure.core.paging

    class azure.core.paging.AzureError(Exception):
        continuation_token: str
        exc_msg
        exc_traceback
        exc_type
        exc_value
        inner_exception: Exception
        message: str

        def __init__(
                self, 
                message: Optional[object], 
                *args: Any, 
                *, 
                error: Exception = ..., 
                **kwargs: Any
            ) -> None: ...

        def raise_with_traceback(self) -> None: ...


    class azure.core.paging.ItemPaged(Iterator[ReturnType]): implements Iterator 

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def __repr__(self) -> str: ...

        def by_page(self, continuation_token: Optional[str] = None) -> Iterator[Iterator[ReturnType]]: ...


    class azure.core.paging.PageIterator(Iterator[Iterator[ReturnType]]): implements Iterator 

        def __init__(
                self, 
                get_next: Callable[[Optional[str]], ResponseType], 
                extract_data: Callable[[ResponseType], Tuple[str, Iterable[ReturnType]]], 
                continuation_token: Optional[str] = None
            ): ...


namespace azure.core.pipeline

    class azure.core.pipeline.AsyncPipeline(AsyncContextManager[AsyncPipeline], Generic[HTTPRequestType, AsyncHTTPResponseType]): implements AsyncContextManager 

        def __init__(
                self, 
                transport: AsyncHttpTransport[HTTPRequestType, AsyncHTTPResponseType], 
                policies: Optional[Iterable[Union[AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType], SansIOHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]]]] = None
            ) -> None: ...

        async def run(
                self, 
                request: HTTPRequestType, 
                **kwargs: Any
            ) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.core.pipeline.Pipeline(ContextManager[Pipeline], Generic[HTTPRequestType, HTTPResponseType]): implements ContextManager 

        def __init__(
                self, 
                transport: HttpTransport[HTTPRequestType, HTTPResponseType], 
                policies: Optional[Iterable[Union[HTTPPolicy[HTTPRequestType, HTTPResponseType], SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]]]] = None
            ) -> None: ...

        def run(
                self, 
                request: HTTPRequestType, 
                **kwargs: Any
            ) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...


    class azure.core.pipeline.PipelineContext(Dict[str, Any]):

        def __delitem__(self, key: str) -> None: ...

        def __getstate__(self) -> Dict[str, Any]: ...

        def __init__(
                self, 
                transport: Optional[TransportType], 
                **kwargs: Any
            ) -> None: ...

        def __reduce__(self) -> Tuple[Any, ]: ...

        def __setitem__(
                self, 
                key: str, 
                item: Any
            ) -> None: ...

        def __setstate__(self, state: Dict[str, Any]) -> None: ...

        def clear(self) -> None: ...

        @overload
        def pop(self, __key: str) -> Any: ...

        @overload
        def pop(
                self, 
                __key: str, 
                __default: Optional[Any]
            ) -> Any: ...

        def update(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.core.pipeline.PipelineRequest(Generic[HTTPRequestType]):

        def __init__(
                self, 
                http_request: HTTPRequestType, 
                context: PipelineContext
            ) -> None: ...


    class azure.core.pipeline.PipelineResponse(Generic[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                http_request: HTTPRequestType, 
                http_response: HTTPResponseType, 
                context: PipelineContext
            ) -> None: ...


namespace azure.core.pipeline.policies

    class azure.core.pipeline.policies.AsyncBearerTokenCredentialPolicy(AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):

        def __init__(
                self, 
                credential: AsyncTokenProvider, 
                *scopes: str, 
                *, 
                enable_cae: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def authorize_request(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                *scopes: str, 
                **kwargs: Any
            ) -> None: ...

        async def on_challenge(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]
            ) -> bool: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        async def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]
            ) -> Optional[Awaitable[None]]: ...

        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.core.pipeline.policies.AsyncHTTPPolicy(abc.ABC, Generic[HTTPRequestType, AsyncHTTPResponseType]):
        next: AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]

        @abc.abstractmethod
        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.core.pipeline.policies.AsyncRedirectPolicy(RedirectPolicyBase, AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):

        def __init__(
                self, 
                *, 
                permit_redirects: Optional[bool] = ..., 
                redirect_max: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def no_redirects(cls: Type[ClsRedirectPolicy]) -> ClsRedirectPolicy: ...

        def configure_redirects(self, options: Dict[str, Any]) -> Dict[str, Any]: ...

        def get_redirect_location(self, response: PipelineResponse[Any, AllHttpResponseType]) -> Union[str, None, Literal[False]]: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                response: PipelineResponse[Any, AllHttpResponseType], 
                redirect_location: str
            ) -> bool: ...

        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...


    class azure.core.pipeline.policies.AsyncRetryPolicy(RetryPolicyBase, AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType]):
        BACKOFF_MAX = 120

        def __init__(
                self, 
                *, 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[int] = ..., 
                retry_connect: Optional[int] = ..., 
                retry_read: Optional[int] = ..., 
                retry_status: Optional[int] = ..., 
                retry_total: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def no_retries(cls: Type[ClsRetryPolicy]) -> ClsRetryPolicy: ...

        def configure_retries(self, options: Dict[str, Any]) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def get_retry_after(self, response: PipelineResponse[Any, AllHttpResponseType]) -> Optional[float]: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                response: Optional[Union[PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, AllHttpResponseType]]] = None, 
                error: Optional[Exception] = None
            ) -> bool: ...

        def is_exhausted(self, settings: Dict[str, Any]) -> bool: ...

        def is_retry(
                self, 
                settings: Dict[str, Any], 
                response: PipelineResponse[HTTPRequestType, AllHttpResponseType]
            ) -> bool: ...

        def parse_retry_after(self, retry_after: str) -> float: ...

        async def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]: ...

        async def sleep(
                self, 
                settings: Dict[str, Any], 
                transport: AsyncHttpTransport[HTTPRequestType, AsyncHTTPResponseType], 
                response: Optional[PipelineResponse[HTTPRequestType, AsyncHTTPResponseType]] = None
            ) -> None: ...

        def update_context(
                self, 
                context: PipelineContext, 
                retry_settings: Dict[str, Any]
            ) -> None: ...


    class azure.core.pipeline.policies.AzureKeyCredentialPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                credential: AzureKeyCredential, 
                name: str, 
                *, 
                prefix: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.AzureSasCredentialPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                credential: AzureSasCredential, 
                **kwargs: Any
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.BearerTokenCredentialPolicy(_BearerTokenCredentialPolicyBase, HTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                credential: TokenProvider, 
                *scopes: str, 
                *, 
                enable_cae: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def authorize_request(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                *scopes: str, 
                **kwargs: Any
            ) -> None: ...

        def on_challenge(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> bool: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...

        def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...


    class azure.core.pipeline.policies.ContentDecodePolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
        CONTEXT_NAME = deserialized_data

        def __init__(
                self, 
                response_encoding: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def deserialize_from_http_generics(
                cls, 
                response: HTTPResponseType, 
                encoding: Optional[str] = None
            ) -> Any: ...

        @classmethod
        def deserialize_from_text(
                cls, 
                data: Optional[Union[AnyStr, IO[AnyStr]]], 
                mime_type: Optional[str] = None, 
                response: Optional[HTTPResponseType] = None
            ) -> Any: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...


    class azure.core.pipeline.policies.CustomHookPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                *, 
                raw_request_hook: Optional[callback] = ..., 
                raw_response_hook: Optional[callback] = ..., 
                **kwargs: Any
            ): ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...


    class azure.core.pipeline.policies.DistributedTracingPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
        DEFAULT_QUERY_PARAMS_ALLOWLIST: set[str]
        TRACING_CONTEXT = TRACING_CONTEXT

        def __init__(
                self, 
                *, 
                additional_allowed_query_params: Optional[Iterable[str]] = ..., 
                instrumentation_config: Optional[Mapping[str, Any]] = ..., 
                network_span_namer = ..., 
                tracing_attributes = ..., 
                **kwargs: Any
            ): ...

        def end_span(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: Optional[HTTPResponseType] = None, 
                exc_info: Optional[OptExcInfo] = None
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...


    class azure.core.pipeline.policies.HTTPPolicy(abc.ABC, Generic[HTTPRequestType, HTTPResponseType]):
        next: HTTPPolicy[HTTPRequestType, HTTPResponseType]

        @abc.abstractmethod
        def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...


    class azure.core.pipeline.policies.HeadersPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
        property headers: Dict[str, str]    # Read-only

        def __init__(
                self, 
                base_headers: Optional[Dict[str, str]] = None, 
                **kwargs: Any
            ) -> None: ...

        def add_header(
                self, 
                key: str, 
                value: str
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.HttpLoggingPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
        DEFAULT_HEADERS_ALLOWLIST: Set[str]
        DEFAULT_QUERY_PARAMS_ALLOWLIST: Set[str]
        MULTI_RECORD_LOG: str = "AZURE_SDK_LOGGING_MULTIRECORD"
        REDACTED_PLACEHOLDER: str = "REDACTED"

        def __init__(
                self, 
                logger: Optional[Logger] = None, 
                *, 
                additional_allowed_query_params: Optional[Iterable[str]] = ..., 
                http_logging_level: int = logging.INFO, 
                **kwargs: Any
            ): ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...


    class azure.core.pipeline.policies.NetworkTraceLoggingPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                logging_enable: bool = False, 
                **kwargs: Any
            ): ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> None: ...


    class azure.core.pipeline.policies.ProxyPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                proxies: Optional[MutableMapping[str, str]] = None, 
                **kwargs: Any
            ): ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.RedirectPolicy(RedirectPolicyBase, HTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                *, 
                permit_redirects: Optional[bool] = ..., 
                redirect_max: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def no_redirects(cls: Type[ClsRedirectPolicy]) -> ClsRedirectPolicy: ...

        def configure_redirects(self, options: Dict[str, Any]) -> Dict[str, Any]: ...

        def get_redirect_location(self, response: PipelineResponse[Any, AllHttpResponseType]) -> Union[str, None, Literal[False]]: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                response: PipelineResponse[Any, AllHttpResponseType], 
                redirect_location: str
            ) -> bool: ...

        def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...


    class azure.core.pipeline.policies.RequestHistory(Generic[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                http_request: HTTPRequestType, 
                http_response: Optional[HTTPResponseType] = None, 
                error: Optional[Exception] = None, 
                context: Optional[Dict[str, Any]] = None
            ) -> None: ...


    class azure.core.pipeline.policies.RequestIdPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                *, 
                auto_request_id: bool = True, 
                request_id: Union[str, Any] = _Unset, 
                request_id_header_name: str = "x-ms-client-request-id", 
                **kwargs: Any
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...

        def set_request_id(self, value: str) -> None: ...


    class azure.core.pipeline.policies.RetryMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        Exponential = "exponential"
        Fixed = "fixed"


    class azure.core.pipeline.policies.RetryPolicy(RetryPolicyBase, HTTPPolicy[HTTPRequestType, HTTPResponseType]):
        BACKOFF_MAX = 120

        def __init__(
                self, 
                *, 
                retry_backoff_factor: Optional[float] = ..., 
                retry_backoff_max: Optional[int] = ..., 
                retry_connect: Optional[int] = ..., 
                retry_mode: Optional[RetryMode] = ..., 
                retry_read: Optional[int] = ..., 
                retry_status: Optional[int] = ..., 
                retry_total: Optional[int] = ..., 
                timeout: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def no_retries(cls: Type[ClsRetryPolicy]) -> ClsRetryPolicy: ...

        def configure_retries(self, options: Dict[str, Any]) -> Dict[str, Any]: ...

        def get_backoff_time(self, settings: Dict[str, Any]) -> float: ...

        def get_retry_after(self, response: PipelineResponse[Any, AllHttpResponseType]) -> Optional[float]: ...

        def increment(
                self, 
                settings: Dict[str, Any], 
                response: Optional[Union[PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, AllHttpResponseType]]] = None, 
                error: Optional[Exception] = None
            ) -> bool: ...

        def is_exhausted(self, settings: Dict[str, Any]) -> bool: ...

        def is_retry(
                self, 
                settings: Dict[str, Any], 
                response: PipelineResponse[HTTPRequestType, AllHttpResponseType]
            ) -> bool: ...

        def parse_retry_after(self, retry_after: str) -> float: ...

        def send(self, request: PipelineRequest[HTTPRequestType]) -> PipelineResponse[HTTPRequestType, HTTPResponseType]: ...

        def sleep(
                self, 
                settings: Dict[str, Any], 
                transport: HttpTransport[HTTPRequestType, HTTPResponseType], 
                response: Optional[PipelineResponse[HTTPRequestType, HTTPResponseType]] = None
            ) -> None: ...

        def update_context(
                self, 
                context: PipelineContext, 
                retry_settings: Dict[str, Any]
            ) -> None: ...


    class azure.core.pipeline.policies.SansIOHTTPPolicy(Generic[HTTPRequestType, HTTPResponseType]):

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> Union[None, Awaitable[None]]: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.SensitiveHeaderCleanupPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):

        def __init__(
                self, 
                *, 
                blocked_redirect_headers: Optional[List[str]] = ..., 
                disable_redirect_cleanup: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


    class azure.core.pipeline.policies.UserAgentPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
        property user_agent: str    # Read-only

        def __init__(
                self, 
                base_user_agent: Optional[str] = None, 
                *, 
                sdk_moniker: Optional[str] = ..., 
                user_agent: Optional[str] = ..., 
                user_agent_overwrite: Optional[bool] = ..., 
                user_agent_use_env: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def add_user_agent(self, value: str) -> None: ...

        def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None: ...

        def on_response(
                self, 
                request: PipelineRequest[HTTPRequestType], 
                response: PipelineResponse[HTTPRequestType, HTTPResponseType]
            ) -> Union[None, Awaitable[None]]: ...


namespace azure.core.pipeline.transport

    class azure.core.pipeline.transport.AioHttpTransport(AsyncHttpTransport): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                loop = ..., 
                session: Optional[ClientSession] = ..., 
                session_owner: bool = True, 
                use_env_settings: Optional[bool] = ..., 
                **kwargs
            ): ...

        async def close(self): ...

        async def open(self): ...

        @overload
        async def send(
                self, 
                request: HttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                stream: bool = False, 
                **config: Any
            ) -> AsyncHttpResponse: ...

        @overload
        async def send(
                self, 
                request: RestHttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                stream: bool = False, 
                **config: Any
            ) -> RestAsyncHttpResponse: ...

        async def sleep(self, duration: float) -> None: ...


    class azure.core.pipeline.transport.AioHttpTransportResponse(AsyncHttpResponse):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
            ) -> None: ...

        def __getstate__(self): ...

        def __init__(
                self, 
                request: HttpRequest, 
                aiohttp_response: ClientResponse, 
                block_size: Optional[int] = None, 
                *, 
                decompress: bool = True
            ) -> None: ...

        def __repr__(self) -> str: ...

        def body(self) -> bytes: ...

        async def load_body(self) -> None: ...

        def parts(self) -> AsyncIterator[AsyncHttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: AsyncPipeline[HttpRequest, AsyncHttpResponse], 
                *, 
                decompress: bool = True, 
                **kwargs
            ) -> AsyncIteratorType[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.pipeline.transport.AsyncHttpResponse(_HttpResponseBase, AsyncContextManager[AsyncHttpResponse]):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
            ) -> None: ...

        def __init__(
                self, 
                request: HttpRequest, 
                internal_response: Any, 
                block_size: Optional[int] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        def body(self) -> bytes: ...

        def parts(self) -> AsyncIterator[AsyncHttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: AsyncPipeline[HttpRequest, AsyncHttpResponse], 
                *, 
                decompress: bool = True, 
                **kwargs: Any
            ) -> AsyncIteratorType[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.pipeline.transport.AsyncHttpTransport(AsyncContextManager[AsyncHttpTransport], abc.ABC, Generic[HTTPRequestType, AsyncHTTPResponseType]):

        @abc.abstractmethod
        async def close(self) -> None: ...

        @abc.abstractmethod
        async def open(self) -> None: ...

        @abc.abstractmethod
        async def send(
                self, 
                request: HTTPRequestType, 
                **kwargs: Any
            ) -> AsyncHTTPResponseType: ...

        async def sleep(self, duration: float) -> None: ...


    class azure.core.pipeline.transport.AsyncioRequestsTransport(RequestsAsyncTransportBase): implements ContextManager , AsyncContextManager 

        def __init__(self, **kwargs) -> None: ...

        def close(self): ...

        def open(self): ...

        @overload
        async def send(
                self, 
                request: HttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs: Any
            ) -> AsyncHttpResponse: ...

        @overload
        async def send(
                self, 
                request: RestHttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs: Any
            ) -> RestAsyncHttpResponse: ...

        async def sleep(self, duration): ...


    class azure.core.pipeline.transport.AsyncioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
            ) -> None: ...

        def __init__(
                self, 
                request, 
                requests_response, 
                block_size = None
            ): ...

        def __repr__(self) -> str: ...

        def body(self): ...

        def parts(self) -> AsyncIterator[AsyncHttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: AsyncPipeline, 
                **kwargs
            ) -> AsyncIteratorType[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.pipeline.transport.HttpRequest:
        property body: Optional[DataType]
        property query: Dict[str, str]    # Read-only

        def __deepcopy__(self, memo: Optional[Dict[int, Any]] = None) -> HttpRequest: ...

        def __init__(
                self, 
                method: str, 
                url: str, 
                headers: Optional[Mapping[str, str]] = None, 
                files: Optional[Any] = None, 
                data: Optional[DataType] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        def format_parameters(self, params: Dict[str, str]) -> None: ...

        def prepare_multipart_body(self, content_index: int = 0) -> int: ...

        def serialize(self) -> bytes: ...

        def set_bytes_body(self, data: bytes) -> None: ...

        def set_formdata_body(self, data: Optional[Dict[str, str]] = None) -> None: ...

        def set_json_body(self, data: Any) -> None: ...

        def set_multipart_mixed(
                self, 
                *requests: HttpRequest, 
                *, 
                boundary: Optional[str] = ..., 
                policies: Optional[List[SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def set_streamed_data_body(self, data: Any) -> None: ...

        def set_text_body(self, data: str) -> None: ...

        def set_xml_body(self, data: Any) -> None: ...


    class azure.core.pipeline.transport.HttpResponse(_HttpResponseBase):

        def __init__(
                self, 
                request: HttpRequest, 
                internal_response: Any, 
                block_size: Optional[int] = None
            ) -> None: ...

        def __repr__(self) -> str: ...

        def body(self) -> bytes: ...

        def parts(self) -> Iterator[HttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: Pipeline[HttpRequest, HttpResponse], 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.pipeline.transport.HttpTransport(ContextManager[HttpTransport], abc.ABC, Generic[HTTPRequestType, HTTPResponseType]):

        @abc.abstractmethod
        def close(self) -> None: ...

        @abc.abstractmethod
        def open(self) -> None: ...

        @abc.abstractmethod
        def send(
                self, 
                request: HTTPRequestType, 
                **kwargs: Any
            ) -> HTTPResponseType: ...

        def sleep(self, duration: float) -> None: ...


    class azure.core.pipeline.transport.RequestsTransport(HttpTransport): implements ContextManager 

        def __init__(
                self, 
                *, 
                session: Optional[Session] = ..., 
                session_owner: Optional[bool] = ..., 
                use_env_settings: Optional[bool] = ..., 
                **kwargs
            ) -> None: ...

        def close(self): ...

        def open(self): ...

        @overload
        def send(
                self, 
                request: HttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs
            ) -> HttpResponse: ...

        @overload
        def send(
                self, 
                request: RestHttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs
            ) -> RestHttpResponse: ...

        def sleep(self, duration: float) -> None: ...


    class azure.core.pipeline.transport.RequestsTransportResponse(HttpResponse, _RequestsTransportResponseBase):

        def __init__(
                self, 
                request, 
                requests_response, 
                block_size = None
            ): ...

        def __repr__(self) -> str: ...

        def body(self): ...

        def parts(self) -> Iterator[HttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: PipelineType, 
                **kwargs
            ) -> Iterator[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.pipeline.transport.TrioRequestsTransport(RequestsAsyncTransportBase): implements ContextManager , AsyncContextManager 

        def __init__(self, **kwargs) -> None: ...

        def close(self): ...

        def open(self): ...

        @overload
        async def send(
                self, 
                request: HttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs: Any
            ) -> AsyncHttpResponse: ...

        @overload
        async def send(
                self, 
                request: RestHttpRequest, 
                *, 
                proxies: Optional[MutableMapping[str, str]] = ..., 
                **kwargs: Any
            ) -> RestAsyncHttpResponse: ...

        async def sleep(self, duration): ...


    class azure.core.pipeline.transport.TrioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):

        async def __aexit__(
                self, 
                exc_type: Optional[Type[BaseException]] = None, 
                exc_value: Optional[BaseException] = None, 
                traceback: Optional[TracebackType] = None
            ) -> None: ...

        def __init__(
                self, 
                request, 
                requests_response, 
                block_size = None
            ): ...

        def __repr__(self) -> str: ...

        def body(self): ...

        def parts(self) -> AsyncIterator[AsyncHttpResponse]: ...

        def raise_for_status(self) -> None: ...

        def stream_download(
                self, 
                pipeline: AsyncPipeline, 
                **kwargs
            ) -> AsyncIteratorType[bytes]: ...

        def text(self, encoding: Optional[str] = None) -> str: ...


namespace azure.core.polling

    async def azure.core.polling.async_poller:async(
            client: Any, 
            initial_response: Any, 
            deserialization_callback: Callable[[Any], PollingReturnType_co], 
            polling_method: AsyncPollingMethod[PollingReturnType_co]
        ) -> PollingReturnType_co: ...


    class azure.core.polling.AsyncLROPoller(Generic[PollingReturnType_co], Awaitable[PollingReturnType_co]): implements Awaitable 

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Callable[[Any], PollingReturnType_co], 
                polling_method: AsyncPollingMethod[PollingReturnType_co]
            ): ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PollingReturnType_co]: ...

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        def polling_method(self) -> AsyncPollingMethod[PollingReturnType_co]: ...

        async def result(self) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        async def wait(self) -> None: ...


    class azure.core.polling.AsyncNoPolling(_SansIONoPolling[PollingReturnType_co], AsyncPollingMethod[PollingReturnType_co]):

        def __init__(self): ...

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                _: Any, 
                initial_response: Any, 
                deserialization_callback: Callable[[Any], PollingReturnType_co]
            ) -> None: ...

        def resource(self) -> PollingReturnType_co: ...

        async def run(self) -> None: ...

        def status(self) -> str: ...


    class azure.core.polling.AsyncPollingMethod(Generic[PollingReturnType_co]):

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, DeserializationCallbackType]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: DeserializationCallbackType
            ) -> None: ...

        def resource(self) -> PollingReturnType_co: ...

        async def run(self) -> None: ...

        def status(self) -> str: ...


    class azure.core.polling.LROPoller(Generic[PollingReturnType_co]):

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Callable[[Any], PollingReturnType_co], 
                polling_method: PollingMethod[PollingReturnType_co]
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> LROPoller[PollingReturnType_co]: ...

        def add_done_callback(self, func: Callable) -> None: ...

        def continuation_token(self) -> str: ...

        def done(self) -> bool: ...

        def polling_method(self) -> PollingMethod[PollingReturnType_co]: ...

        def remove_done_callback(self, func: Callable) -> None: ...

        def result(self, timeout: Optional[float] = None) -> PollingReturnType_co: ...

        def status(self) -> str: ...

        @distributed_trace
        def wait(self, timeout: Optional[float] = None) -> None: ...


    class azure.core.polling.NoPolling(_SansIONoPolling[PollingReturnType_co], PollingMethod[PollingReturnType_co]):

        def __init__(self): ...

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                _: Any, 
                initial_response: Any, 
                deserialization_callback: Callable[[Any], PollingReturnType_co]
            ) -> None: ...

        def resource(self) -> PollingReturnType_co: ...

        def run(self) -> None: ...

        def status(self) -> str: ...


    class azure.core.polling.PollingMethod(Generic[PollingReturnType_co]):

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, DeserializationCallbackType]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: DeserializationCallbackType
            ) -> None: ...

        def resource(self) -> PollingReturnType_co: ...

        def run(self) -> None: ...

        def status(self) -> str: ...


namespace azure.core.polling.async_base_polling

    class azure.core.polling.async_base_polling.AsyncLROBasePolling(_SansIOLROBasePolling[PollingReturnType_co, AsyncPipelineClient[HttpRequestTypeVar, AsyncHttpResponseTypeVar], HttpRequestTypeVar, AsyncHttpResponseTypeVar], AsyncPollingMethod[PollingReturnType_co]):

        def __init__(
                self, 
                timeout: float = 30, 
                lro_algorithms: Optional[Sequence[LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]]] = None, 
                lro_options: Optional[Dict[str, Any]] = None, 
                path_format_arguments: Optional[Dict[str, str]] = None, 
                **operation_config: Any
            ): ...

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                client: PipelineClientType, 
                initial_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar], 
                deserialization_callback: Callable[[PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]], PollingReturnType_co]
            ) -> None: ...

        async def request_status(self, status_link: str) -> PipelineResponse[HttpRequestTypeVar, AsyncHttpResponseTypeVar]: ...

        def resource(self) -> PollingReturnType_co: ...

        async def run(self) -> None: ...

        def status(self) -> str: ...

        async def update_status(self) -> None: ...


namespace azure.core.polling.base_polling

    class azure.core.polling.base_polling.BadResponse(Exception):


    class azure.core.polling.base_polling.BadStatus(Exception):


    class azure.core.polling.base_polling.LROBasePolling(_SansIOLROBasePolling[PollingReturnType_co, PipelineClient[HttpRequestTypeVar, HttpResponseTypeVar], HttpRequestTypeVar, HttpResponseTypeVar], PollingMethod[PollingReturnType_co]):

        def __getattribute__(self, name: str) -> Any: ...

        def __init__(
                self, 
                timeout: float = 30, 
                lro_algorithms: Optional[Sequence[LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]]] = None, 
                lro_options: Optional[Dict[str, Any]] = None, 
                path_format_arguments: Optional[Dict[str, str]] = None, 
                **operation_config: Any
            ): ...

        @classmethod
        def from_continuation_token(
                cls, 
                continuation_token: str, 
                **kwargs: Any
            ) -> Tuple[Any, Any, Callable[[Any], PollingReturnType_co]]: ...

        def finished(self) -> bool: ...

        def get_continuation_token(self) -> str: ...

        def initialize(
                self, 
                client: PipelineClientType, 
                initial_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar], 
                deserialization_callback: Callable[[PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]], PollingReturnType_co]
            ) -> None: ...

        def request_status(self, status_link: str) -> PipelineResponse[HttpRequestTypeVar, HttpResponseTypeVar]: ...

        def resource(self) -> PollingReturnType_co: ...

        def run(self) -> None: ...

        def status(self) -> str: ...

        def update_status(self) -> None: ...


    class azure.core.polling.base_polling.LocationPolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):

        def can_poll(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> bool: ...

        def get_final_get_url(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> Optional[str]: ...

        def get_polling_url(self) -> str: ...

        def get_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...

        def set_initial_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...


    class azure.core.polling.base_polling.LongRunningOperation(ABC, Generic[HTTPRequestType_co, HTTPResponseType_co]):

        @abc.abstractmethod
        def can_poll(self, pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co]) -> bool: ...

        @abc.abstractmethod
        def get_final_get_url(self, pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co]) -> Optional[str]: ...

        @abc.abstractmethod
        def get_polling_url(self) -> str: ...

        @abc.abstractmethod
        def get_status(self, pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co]) -> str: ...

        @abc.abstractmethod
        def set_initial_status(self, pipeline_response: PipelineResponse[HTTPRequestType_co, HTTPResponseType_co]) -> str: ...


    class azure.core.polling.base_polling.OperationFailed(Exception):


    class azure.core.polling.base_polling.OperationResourcePolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):

        def __init__(
                self, 
                operation_location_header: str = "operation-location", 
                *, 
                lro_options: Optional[Dict[str, Any]] = ...
            ): ...

        def can_poll(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> bool: ...

        def get_final_get_url(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> Optional[str]: ...

        def get_polling_url(self) -> str: ...

        def get_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...

        def set_initial_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...


    class azure.core.polling.base_polling.StatusCheckPolling(LongRunningOperation[HttpRequestTypeVar, AllHttpResponseTypeVar]):

        def can_poll(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> bool: ...

        def get_final_get_url(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> Optional[str]: ...

        def get_polling_url(self) -> str: ...

        def get_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...

        def set_initial_status(self, pipeline_response: PipelineResponse[HttpRequestTypeVar, AllHttpResponseTypeVar]) -> str: ...


namespace azure.core.rest

    class azure.core.rest.AsyncHttpResponse(_HttpResponseBase, AsyncContextManager[AsyncHttpResponse]):
        property content: bytes    # Read-only
        property content_type: Optional[str]    # Read-only
        property encoding: Optional[str]
        property headers: MutableMapping[str, str]    # Read-only
        property is_closed: bool    # Read-only
        property is_stream_consumed: bool    # Read-only
        property reason: str    # Read-only
        property request: HttpRequest    # Read-only
        property status_code: int    # Read-only
        property url: str    # Read-only

        @abc.abstractmethod
        async def close(self) -> None: ...

        @abc.abstractmethod
        async def iter_bytes(self, **kwargs: Any) -> AsyncIterator[bytes]: ...

        @abc.abstractmethod
        async def iter_raw(self, **kwargs: Any) -> AsyncIterator[bytes]: ...

        @abc.abstractmethod
        def json(self) -> Any: ...

        @abc.abstractmethod
        def raise_for_status(self) -> None: ...

        @abc.abstractmethod
        async def read(self) -> bytes: ...

        @abc.abstractmethod
        def text(self, encoding: Optional[str] = None) -> str: ...


    class azure.core.rest.HttpRequest(HttpRequestBackcompatMixin):
        property content: Any    # Read-only
        content: any
        headers: mapping
        method: str
        url: str

        def __deepcopy__(self, memo: Optional[Dict[int, Any]] = None) -> HttpRequest: ...

        def __getattr__(self, attr: str) -> Any: ...

        def __init__(
                self, 
                method: str, 
                url: str, 
                *, 
                content: Optional[ContentType] = ..., 
                data: Optional[Dict[str, Any]] = ..., 
                files: Optional[FilesType] = ..., 
                headers: Optional[MutableMapping[str, str]] = ..., 
                json: Any = ..., 
                params: Optional[ParamsType] = ..., 
                **kwargs: Any
            ): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                attr: str, 
                value: Any
            ) -> None: ...


    class azure.core.rest.HttpResponse(_HttpResponseBase): implements ContextManager 
        property content: bytes    # Read-only
        property content_type: Optional[str]    # Read-only
        property encoding: Optional[str]
        property headers: MutableMapping[str, str]    # Read-only
        property is_closed: bool    # Read-only
        property is_stream_consumed: bool    # Read-only
        property reason: str    # Read-only
        property request: HttpRequest    # Read-only
        property status_code: int    # Read-only
        property url: str    # Read-only

        def __repr__(self) -> str: ...

        @abc.abstractmethod
        def close(self) -> None: ...

        @abc.abstractmethod
        def iter_bytes(self, **kwargs: Any) -> Iterator[bytes]: ...

        @abc.abstractmethod
        def iter_raw(self, **kwargs: Any) -> Iterator[bytes]: ...

        @abc.abstractmethod
        def json(self) -> Any: ...

        @abc.abstractmethod
        def raise_for_status(self) -> None: ...

        @abc.abstractmethod
        def read(self) -> bytes: ...

        @abc.abstractmethod
        def text(self, encoding: Optional[str] = None) -> str: ...


namespace azure.core.serialization

    def azure.core.serialization.as_attribute_dict(
            obj: Any, 
            *, 
            exclude_readonly: bool = False
        ) -> Dict[str, Any]: ...


    def azure.core.serialization.attribute_list(obj: Any) -> List[str]: ...


    def azure.core.serialization.get_backcompat_attr_name(model: Any, attr_name: str) -> str: ...


    def azure.core.serialization.is_generated_model(obj: Any) -> bool: ...


    class azure.core.serialization.AzureJSONEncoder(JSONEncoder):
        item_separator = , 
        key_separator = : 

        def default(self, o: Any) -> Any: ...


    class azure.core.serialization.TypeHandlerRegistry:

        def __init__(self) -> None: ...

        def get_deserializer(self, cls: Type) -> Optional[Callable[[Dict[str, Any]], Any]]: ...

        def get_serializer(self, obj: Any) -> Optional[Callable[[Any], Dict[str, Any]]]: ...

        def register_deserializer(self, condition: Union[Type, Callable[[Any], bool]]) -> Callable[[Callable[[Type, Dict[str, Any]], Any]], Callable[[Type, Dict[str, Any]], Any]]: ...

        def register_serializer(self, condition: Union[Type, Callable[[Any], bool]]) -> Callable[[Callable[[Any], Dict[str, Any]]], Callable[[Any], Dict[str, Any]]]: ...


namespace azure.core.settings

    class azure.core.settings.Settings:
        property current: Tuple[Any, ]    # Read-only
        property defaults: Tuple[Any, ]    # Read-only
        property defaults_only: bool
        azure_cloud: PrioritizedSetting
        log_level: PrioritizedSetting
        tracing_enabled: PrioritizedSetting
        tracing_implementation: PrioritizedSetting

        def __init__(self) -> None: ...

        def config(self, **kwargs: Any) -> Tuple[Any, ]: ...


namespace azure.core.tracing

    @runtime_checkable
    class azure.core.tracing.AbstractSpan(Protocol, Generic[SpanType]): implements ContextManager 
        property kind: Optional[SpanKind]
        property span_instance: SpanType    # Read-only

        def __init__(
                self, 
                span: Optional[SpanType] = None, 
                name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def change_context(cls, span: SpanType) -> ContextManager[SpanType]: ...

        @classmethod
        def get_current_span(cls) -> SpanType: ...

        @classmethod
        def get_current_tracer(cls) -> Any: ...

        @classmethod
        def link(
                cls, 
                traceparent: str, 
                attributes: Optional[Attributes] = None
            ) -> None: ...

        @classmethod
        def link_from_headers(
                cls, 
                headers: Dict[str, str], 
                attributes: Optional[Attributes] = None
            ) -> None: ...

        @classmethod
        def set_current_span(cls, span: SpanType) -> None: ...

        @classmethod
        def set_current_tracer(cls, tracer: Any) -> None: ...

        @classmethod
        def with_current_context(cls, func: Callable) -> Callable: ...

        def add_attribute(
                self, 
                key: str, 
                value: Union[str, int]
            ) -> None: ...

        def finish(self) -> None: ...

        def get_trace_parent(self) -> str: ...

        def set_http_attributes(
                self, 
                request: HttpRequestType, 
                response: Optional[HttpResponseType] = None
            ) -> None: ...

        def span(
                self, 
                name: str = "child_span", 
                **kwargs: Any
            ) -> AbstractSpan[SpanType]: ...

        def start(self) -> None: ...

        def to_header(self) -> Dict[str, str]: ...


    class azure.core.tracing.HttpSpanMixin:

        def set_http_attributes(
                self: AbstractSpan, 
                request: HttpRequestType, 
                response: Optional[HttpResponseType] = None
            ) -> None: ...


    class azure.core.tracing.Link:

        def __init__(
                self, 
                headers: Dict[str, str], 
                attributes: Optional[Attributes] = None
            ) -> None: ...


    class azure.core.tracing.SpanKind(Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = 3
        CONSUMER = 5
        INTERNAL = 6
        PRODUCER = 4
        SERVER = 2
        UNSPECIFIED = 1


    class azure.core.tracing.TracingOptions(TypedDict, total=False):
        key "attributes": Mapping[str, Union[str, bool, int, float, Sequence[str], Sequence[bool], Sequence[int], Sequence[float]]]
        key "enabled": bool


namespace azure.core.tracing.common

    @contextmanager
    def azure.core.tracing.common.change_context(span: Optional[AbstractSpan]) -> Generator: ...


    def azure.core.tracing.common.with_current_context(func: Callable) -> Any: ...


namespace azure.core.tracing.decorator

    @contextmanager
    def azure.core.tracing.decorator.change_context(span: Optional[AbstractSpan]) -> Generator: ...


    @overload
    def azure.core.tracing.decorator.distributed_trace(__func: Callable[P, T]) -> Callable[P, T]: ...


    @overload
    def azure.core.tracing.decorator.distributed_trace(
            *, 
            kind: Optional[SpanKind] = ..., 
            name_of_span: Optional[str] = ..., 
            tracing_attributes: Optional[Mapping[str, Any]] = ..., 
            **kwargs: Any
        ) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


namespace azure.core.tracing.decorator_async

    @contextmanager
    def azure.core.tracing.decorator_async.change_context(span: Optional[AbstractSpan]) -> Generator: ...


    @overload
    def azure.core.tracing.decorator_async.distributed_trace_async(__func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]: ...


    @overload
    def azure.core.tracing.decorator_async.distributed_trace_async(
            *, 
            kind: Optional[SpanKind] = ..., 
            name_of_span: Optional[str] = ..., 
            tracing_attributes: Optional[Mapping[str, Any]] = ..., 
            **kwargs: Any
        ) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]: ...


namespace azure.core.tracing.opentelemetry

    class azure.core.tracing.opentelemetry.OpenTelemetryTracer:

        def __init__(
                self, 
                *, 
                attributes: Optional[Attributes] = ..., 
                library_name: Optional[str] = ..., 
                library_version: Optional[str] = ..., 
                schema_url: Optional[str] = ...
            ) -> None: ...

        @classmethod
        def get_current_span(cls) -> Span: ...

        @classmethod
        def get_trace_context(cls) -> Dict[str, str]: ...

        @classmethod
        @contextmanager
        def use_span(
                cls, 
                span: Span, 
                *, 
                end_on_exit: bool = True
            ) -> Iterator[Span]: ...

        @classmethod
        def with_current_context(cls, func: Callable) -> Callable: ...

        @staticmethod
        def set_span_error_status(span: Span, description: Optional[str] = None) -> None: ...

        @contextmanager
        def start_as_current_span(
                self, 
                name: str, 
                *, 
                attributes: Optional[Attributes] = ..., 
                context: Optional[Dict[str, Any]] = ..., 
                end_on_exit: bool = True, 
                kind: SpanKind = _SpanKind.INTERNAL, 
                links: Optional[Sequence[Link]] = ..., 
                start_time: Optional[int] = ...
            ) -> Iterator[Span]: ...

        def start_span(
                self, 
                name: str, 
                *, 
                attributes: Optional[Attributes] = ..., 
                context: Optional[Dict[str, Any]] = ..., 
                kind: SpanKind = _SpanKind.INTERNAL, 
                links: Optional[Sequence[Link]] = ..., 
                start_time: Optional[int] = ...
            ) -> Span: ...


namespace azure.core.utils

    def azure.core.utils.case_insensitive_dict(*args: Optional[Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]], **kwargs: Any) -> MutableMapping[str, Any]: ...


    def azure.core.utils.parse_connection_string(conn_str: str, case_sensitive_keys: bool = False) -> Mapping[str, str]: ...


    class azure.core.utils.CaseInsensitiveDict(MutableMapping[str, Any]):

        def __delitem__(self, key: str) -> None: ...

        def __eq__(self, other: Any) -> bool: ...

        def __getitem__(self, key: str) -> Any: ...

        def __init__(
                self, 
                data: Optional[Union[Mapping[str, Any], Iterable[Tuple[str, Any]]]] = None, 
                **kwargs: Any
            ) -> None: ...

        def __iter__(self) -> Iterator[str]: ...

        def __len__(self) -> int: ...

        def __repr__(self) -> str: ...

        def __setitem__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...

        def copy(self) -> CaseInsensitiveDict: ...

        def lowerkey_items(self) -> Iterator[Tuple[str, Any]]: ...


```