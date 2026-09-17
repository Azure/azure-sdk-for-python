```py
namespace azure.data.ai

    class azure.data.ai.InferenceServiceClient: implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[str, AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = API_VERSION, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def semantic_rerank(
                self, 
                request: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...


namespace azure.data.ai.aio

    class azure.data.ai.aio.InferenceServiceClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[str, AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = API_VERSION, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def semantic_rerank(
                self, 
                request: dict[str, Any], 
                **kwargs: Any
            ) -> dict[str, Any]: ...


```