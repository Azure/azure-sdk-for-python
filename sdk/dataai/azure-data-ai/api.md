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
        def get_embeddings(
                self, 
                *, 
                content_type: str = "application/json", 
                delivery: Optional[Union[str, EmbeddingDelivery]] = ..., 
                dimensions: Optional[int] = ..., 
                encoding_format: Optional[Union[str, EmbeddingEncodingFormat]] = ..., 
                inputs: list[dict[str, Any]], 
                max_vector_count: Optional[int] = ..., 
                model: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                multi_dimensions: Optional[int] = ..., 
                output_data_kind: Optional[Union[str, EmbeddingOutputDataKind]] = ..., 
                vector_kind: Optional[Union[str, EmbeddingVectorKind]] = ..., 
                **kwargs: Any
            ) -> EmbeddingResult: ...

        @overload
        def get_embeddings(
                self, 
                body: EmbedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmbeddingResult: ...

        @overload
        def get_embeddings(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmbeddingResult: ...

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
        async def get_embeddings(
                self, 
                *, 
                content_type: str = "application/json", 
                delivery: Optional[Union[str, EmbeddingDelivery]] = ..., 
                dimensions: Optional[int] = ..., 
                encoding_format: Optional[Union[str, EmbeddingEncodingFormat]] = ..., 
                inputs: list[dict[str, Any]], 
                max_vector_count: Optional[int] = ..., 
                model: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                multi_dimensions: Optional[int] = ..., 
                output_data_kind: Optional[Union[str, EmbeddingOutputDataKind]] = ..., 
                vector_kind: Optional[Union[str, EmbeddingVectorKind]] = ..., 
                **kwargs: Any
            ) -> EmbeddingResult: ...

        @overload
        async def get_embeddings(
                self, 
                body: EmbedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmbeddingResult: ...

        @overload
        async def get_embeddings(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EmbeddingResult: ...

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

    class azure.data.ai.models.EmbeddingBadGatewayResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingBadRequestResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingContentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        QUERY = "query"
        TEXT = "text"


    class azure.data.ai.models.EmbeddingData(_Model):
        id: Optional[str]
        index: int
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                index: int, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingDataKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTIMODAL_DENSE = "multimodal_dense"
        MULTIMODAL_DENSE_AND_MULTI_VECTOR = "multimodal_dense_multi"
        MULTIMODAL_MULTI_VECTOR = "multimodal_multi"


    class azure.data.ai.models.EmbeddingDelivery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        LINK = "link"


    class azure.data.ai.models.EmbeddingEncodingFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE64 = "base64"
        FLOAT = "float"


    class azure.data.ai.models.EmbeddingForbiddenResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingGatewayTimeoutResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingImageFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GIF = "gif"
        JPEG = "jpeg"
        PNG = "png"
        WEBP = "webp"


    class azure.data.ai.models.EmbeddingOutputDataKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLOAT16 = "float16"
        FLOAT32 = "float32"


    class azure.data.ai.models.EmbeddingPayloadTooLargeResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingResult(_Model):
        data: list[EmbeddingData]
        model: str
        model_version: str
        object: Literal["list"]
        output: Optional[MultimodalEmbeddingOutput]
        output_data_kind: Union[str, EmbeddingOutputDataKind]
        usage: EmbeddingUsage
        warnings: Optional[list[MultimodalEmbeddingWarning]]

        @overload
        def __init__(
                self, 
                *, 
                data: list[EmbeddingData], 
                model: str, 
                model_version: str, 
                output: Optional[MultimodalEmbeddingOutput] = ..., 
                output_data_kind: Union[str, EmbeddingOutputDataKind], 
                usage: EmbeddingUsage, 
                warnings: Optional[list[MultimodalEmbeddingWarning]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingServiceUnavailableResult(_Model):
        error: ProblemDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ProblemDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingUsage(_Model):
        kind: str
        prompt_tokens: Optional[int]
        total_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                prompt_tokens: Optional[int] = ..., 
                total_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingUsageKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTIMODAL = "multimodal"


    class azure.data.ai.models.EmbeddingVectorKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DENSE = "dense"
        DENSE_AND_MULTI = "dense_multi"
        MULTI = "multi"


    class azure.data.ai.models.EmbeddingWarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INPUT_TRUNCATED = "EMBEDDING_INPUT_TRUNCATED"
        SAS_LONG_LIVED = "EMBEDDING_SAS_LONG_LIVED"


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


    class azure.data.ai.models.MultimodalDenseAndMultiVectorEmbedding(EmbeddingData, discriminator='multimodal_dense_multi'):
        content_kind: Union[str, EmbeddingContentKind]
        embedding: EmbeddingVector
        format: Optional[Union[str, EmbeddingImageFormat]]
        height: Optional[int]
        id: str
        index: int
        input_tokens: Optional[int]
        kind: Literal[EmbeddingDataKind.MULTIMODAL_DENSE_AND_MULTI_VECTOR]
        multi_embedding: MultiEmbeddingVector
        shape: list[int]
        tokens: Optional[int]
        truncated: Optional[bool]
        vector_kind: Literal[EmbeddingVectorKind.DENSE_AND_MULTI]
        visual_tokens: Optional[int]
        width: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                content_kind: Union[str, EmbeddingContentKind], 
                embedding: EmbeddingVector, 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                multi_embedding: MultiEmbeddingVector, 
                shape: list[int], 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                vector_kind: Literal[EmbeddingVectorKind.DENSE_AND_MULTI], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalDenseEmbedding(EmbeddingData, discriminator='multimodal_dense'):
        content_kind: Union[str, EmbeddingContentKind]
        embedding: EmbeddingVector
        format: Optional[Union[str, EmbeddingImageFormat]]
        height: Optional[int]
        id: str
        index: int
        input_tokens: Optional[int]
        kind: Literal[EmbeddingDataKind.MULTIMODAL_DENSE]
        tokens: Optional[int]
        truncated: Optional[bool]
        vector_kind: Literal[EmbeddingVectorKind.DENSE]
        visual_tokens: Optional[int]
        width: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                content_kind: Union[str, EmbeddingContentKind], 
                embedding: EmbeddingVector, 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                vector_kind: Literal[EmbeddingVectorKind.DENSE], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingOutput(_Model):
        content_type: str
        expires_at: datetime
        id: str
        record_count: int
        sas_token: str
        sha256: str
        size_in_bytes: int
        url: str

        @overload
        def __init__(
                self, 
                *, 
                content_type: str, 
                expires_at: datetime, 
                id: str, 
                record_count: int, 
                sas_token: str, 
                sha256: str, 
                size_in_bytes: int, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingUsage(EmbeddingUsage, discriminator='multimodal'):
        image_count: int
        kind: Literal[EmbeddingUsageKind.MULTIMODAL]
        prompt_tokens: int
        text_tokens: Optional[int]
        total_tokens: int
        visual_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                image_count: int, 
                prompt_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ..., 
                total_tokens: Optional[int] = ..., 
                visual_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingWarning(_Model):
        code: Union[str, EmbeddingWarningCode]
        code_number: Optional[int]
        index: int
        input_tokens: Optional[int]
        message: str
        tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, EmbeddingWarningCode], 
                code_number: Optional[int] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                message: str, 
                tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalMultiVectorEmbedding(EmbeddingData, discriminator='multimodal_multi'):
        content_kind: Union[str, EmbeddingContentKind]
        format: Optional[Union[str, EmbeddingImageFormat]]
        height: Optional[int]
        id: str
        index: int
        input_tokens: Optional[int]
        kind: Literal[EmbeddingDataKind.MULTIMODAL_MULTI_VECTOR]
        multi_embedding: MultiEmbeddingVector
        shape: list[int]
        tokens: Optional[int]
        truncated: Optional[bool]
        vector_kind: Literal[EmbeddingVectorKind.MULTI]
        visual_tokens: Optional[int]
        width: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                content_kind: Union[str, EmbeddingContentKind], 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                multi_embedding: MultiEmbeddingVector, 
                shape: list[int], 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                vector_kind: Literal[EmbeddingVectorKind.MULTI], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
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
                details: Optional[list[ODataV4Format]] = ..., 
                explanation: Optional[str] = ..., 
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
        target_paths: Optional[list[str]]
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
                target_paths: Optional[list[str]] = ..., 
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

    class azure.data.ai.types.EmbedRequest(TypedDict, total=False):
        key "delivery": Union[str, EmbeddingDelivery]
        key "dimensions": int
        key "encodingFormat": Union[str, EmbeddingEncodingFormat]
        key "inputs": Required[list[dict[str, Any]]]
        key "maxVectorCount": int
        key "model": str
        key "modelVersion": str
        key "multiDimensions": int
        key "outputDataKind": Union[str, EmbeddingOutputDataKind]
        key "vectorKind": Union[str, EmbeddingVectorKind]
        delivery: Union[str, EmbeddingDelivery]
        dimensions: int
        encodingFormat: Union[str, EmbeddingEncodingFormat]
        inputs: list[dict[str, Any]]
        maxVectorCount: int
        model: str
        modelVersion: str
        multiDimensions: int
        outputDataKind: Union[str, EmbeddingOutputDataKind]
        vectorKind: Union[str, EmbeddingVectorKind]


    class azure.data.ai.types.SemanticRerankingInferenceContent(TypedDict, total=False):
        key "batchSize": int
        key "documentType": Union[str, SemanticRerankingDocumentType]
        key "documents": Required[list[str]]
        key "model": str
        key "query": Required[str]
        key "returnDocuments": bool
        key "returnSentenceScore": bool
        key "sort": bool
        key "topK": int
        batchSize: int
        documentType: Union[str, SemanticRerankingDocumentType]
        documents: list[str]
        model: str
        query: str
        returnDocuments: bool
        returnSentenceScore: bool
        sort: bool
        targetPaths: list[str]
        topK: int


```