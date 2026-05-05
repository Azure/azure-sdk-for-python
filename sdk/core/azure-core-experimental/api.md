```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.core.experimental.transport

    class azure.core.experimental.transport.AsyncHttpXTransport(AsyncHttpTransport): implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                client: Optional[AsyncClient] = ..., 
                client_owner: bool = True, 
                use_env_settings: bool = True, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        async def open(self) -> None: ...

        async def send(
                self, 
                request: Union[HttpRequest, LegacyHttpRequest], 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> AsyncHttpXTransportResponse: ...


    class azure.core.experimental.transport.HttpXTransport(HttpTransport): implements ContextManager 

        def __init__(
                self, 
                *, 
                client: Optional[Client] = ..., 
                client_owner: bool = True, 
                use_env_settings: bool = True, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def open(self) -> None: ...

        def send(
                self, 
                request: Union[HttpRequest, LegacyHttpRequest], 
                *, 
                stream: bool = False, 
                **kwargs
            ) -> HttpXTransportResponse: ...


    class azure.core.experimental.transport.PyodideTransport(AsyncioRequestsTransport):

        async def send(
                self, 
                request: HttpRequest, 
                **kwargs
            ) -> PyodideTransportResponse: ...


    class azure.core.experimental.transport.Urllib3Transport(HttpTransport[RestHttpRequest, RestHttpResponse]): implements ContextManager 

        def __init__(
                self, 
                *, 
                pool: Optional[PoolManager] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def open(self) -> None: ...

        def send(
                self, 
                request: RestHttpRequest, 
                **kwargs: Any
            ) -> RestHttpResponse: ...


```