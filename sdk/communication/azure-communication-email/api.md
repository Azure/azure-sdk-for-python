```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.email

    class azure.communication.email.EmailClient(EmailClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> EmailClient: ...

        @overload
        def begin_send(
                self, 
                message: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        @overload
        def begin_send(
                self, 
                message: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[JSON]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.communication.email.aio

    class azure.communication.email.aio.EmailClient(EmailClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> EmailClient: ...

        @overload
        async def begin_send(
                self, 
                message: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        @overload
        async def begin_send(
                self, 
                message: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[JSON]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


```