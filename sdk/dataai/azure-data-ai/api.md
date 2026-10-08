```py
namespace azure.data.ai

    class azure.data.ai.InferenceClient(_InferenceClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def semantic_rerank(
                self, 
                request: SemanticRerankingInferenceContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        @overload
        def semantic_rerank(
                self, 
                request: SemanticRerankingInferenceContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        @overload
        def semantic_rerank(
                self, 
                request: Union[bytes, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.data.ai.aio

    class azure.data.ai.aio.InferenceClient(_InferenceClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def semantic_rerank(
                self, 
                request: SemanticRerankingInferenceContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        @overload
        async def semantic_rerank(
                self, 
                request: SemanticRerankingInferenceContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        @overload
        async def semantic_rerank(
                self, 
                request: Union[bytes, IO[bytes]], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SemanticRerankingInferenceResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.data.ai.models

    class azure.data.ai.models.InferenceErrorResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.InnerError(_Model):
        code: Optional[str]
        innererror: Optional[InnerError]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                innererror: Optional[InnerError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.LatencyResult(_Model):
        data_preprocess_duration: Optional[timedelta]
        inference_duration: Optional[timedelta]
        post_process_duration: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                data_preprocess_duration: Optional[timedelta] = ..., 
                inference_duration: Optional[timedelta] = ..., 
                post_process_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.ProblemDetails(_GeneratedProblemDetails):
        details: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                detail: Optional[str] = ..., 
                details: Optional[list[ODataV4Format]] = ..., 
                extensions: Optional[dict[str, Any]] = ..., 
                innererror: Optional[InnerError] = ..., 
                instance: Optional[str] = ..., 
                message: str, 
                status: Optional[int] = ..., 
                target: Optional[str] = ..., 
                title: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def as_dict(
                self, 
                *, 
                exclude_readonly: bool = False
            ) -> dict[str, Any]: ...


    class azure.data.ai.models.SemanticRerankingDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json"
        TEXT = "text"


    class azure.data.ai.models.SemanticRerankingInferenceContent(_Model):
        batch_size: Optional[int]
        document_type: Optional[Union[str, SemanticRerankingDocumentType]]
        documents: list[str]
        model: Optional[str]
        query: str
        return_documents: Optional[bool]
        return_sentence_score: Optional[bool]
        sort: Optional[bool]
        target_paths: Optional[str]
        top_k: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                batch_size: Optional[int] = ..., 
                document_type: Optional[Union[str, SemanticRerankingDocumentType]] = ..., 
                documents: list[str], 
                model: Optional[str] = ..., 
                query: str, 
                return_documents: Optional[bool] = ..., 
                return_sentence_score: Optional[bool] = ..., 
                sort: Optional[bool] = ..., 
                target_paths: Optional[str] = ..., 
                top_k: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.SemanticRerankingInferenceResult(_Model):
        meta: Optional[SemanticRerankingMetaResult]
        scores: Optional[list[SemanticRerankingScore]]

        @overload
        def __init__(
                self, 
                *, 
                meta: Optional[SemanticRerankingMetaResult] = ..., 
                scores: Optional[list[SemanticRerankingScore]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.SemanticRerankingMetaResult(_Model):
        latency: Optional[LatencyResult]
        model_name: Optional[str]
        model_version: Optional[str]
        token_usage: Optional[TokenUsageResult]

        @overload
        def __init__(
                self, 
                *, 
                latency: Optional[LatencyResult] = ..., 
                model_name: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                token_usage: Optional[TokenUsageResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.SemanticRerankingScore(_Model):
        document: Optional[str]
        index: Optional[int]
        score: Optional[float]
        sentence_scores: Optional[list[SentenceScore]]

        @overload
        def __init__(
                self, 
                *, 
                document: Optional[str] = ..., 
                index: Optional[int] = ..., 
                score: Optional[float] = ..., 
                sentence_scores: Optional[list[SentenceScore]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.SentenceScore(_Model):
        index: int
        score: float

        @overload
        def __init__(
                self, 
                *, 
                index: int, 
                score: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.TokenUsageResult(_Model):
        total_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                total_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.TooManyRequestsResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.data.ai.types

    class azure.data.ai.types.SemanticRerankingInferenceContent(TypedDict, total=False):
        key "batchSize": int
        key "documentType": Union[str, SemanticRerankingDocumentType]
        key "documents": Required[list[str]]
        key "model": str
        key "query": Required[str]
        key "returnDocuments": bool
        key "returnSentenceScore": bool
        key "sort": bool
        key "targetPaths": str
        key "topK": int
        batchSize: int
        documentType: Union[str, SemanticRerankingDocumentType]
        documents: list[str]
        model: str
        query: str
        returnDocuments: bool
        returnSentenceScore: bool
        sort: bool
        targetPaths: str
        topK: int


```