```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.monitor.ingestion

    class azure.monitor.ingestion.LogsIngestionClient(GeneratedClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        def upload(
                self, 
                rule_id: str, 
                stream_name: str, 
                logs: Union[List[JSON], IO[bytes]], 
                *, 
                on_error: Optional[Callable[[LogsUploadError], None]] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.monitor.ingestion.LogsUploadError:
        error: Exception
        failed_logs: List[Mapping[str, Any]]

        def __init__(
                self, 
                error: Exception, 
                failed_logs: List[JSON]
            ) -> None: ...


namespace azure.monitor.ingestion.aio

    class azure.monitor.ingestion.aio.LogsIngestionClient(GeneratedClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        async def upload(
                self, 
                rule_id: str, 
                stream_name: str, 
                logs: Union[List[JSON], IO[bytes]], 
                *, 
                on_error: Optional[Callable[[LogsUploadError], Awaitable[None]]] = ..., 
                **kwargs: Any
            ) -> None: ...


```