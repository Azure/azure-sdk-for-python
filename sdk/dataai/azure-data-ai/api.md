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
        def multi_modal_embed(
                self, 
                *, 
                content_type: str = "application/json", 
                contents: list[EmbeddingContentItem], 
                delivery: Optional[Union[str, EmbeddingDelivery]] = ..., 
                dimensions: Optional[int] = ..., 
                encoding_format: Optional[Union[str, EmbeddingEncodingFormat]] = ..., 
                max_num_vectors: Optional[int] = ..., 
                model: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                multi_dimensions: Optional[int] = ..., 
                output_data_type: Optional[Union[str, EmbeddingOutputDataType]] = ..., 
                vector_type: Optional[Union[str, EmbeddingVectorType]] = ..., 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

        @overload
        def multi_modal_embed(
                self, 
                body: MultiModalEmbedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

        @overload
        def multi_modal_embed(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

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
        async def multi_modal_embed(
                self, 
                *, 
                content_type: str = "application/json", 
                contents: list[EmbeddingContentItem], 
                delivery: Optional[Union[str, EmbeddingDelivery]] = ..., 
                dimensions: Optional[int] = ..., 
                encoding_format: Optional[Union[str, EmbeddingEncodingFormat]] = ..., 
                max_num_vectors: Optional[int] = ..., 
                model: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                multi_dimensions: Optional[int] = ..., 
                output_data_type: Optional[Union[str, EmbeddingOutputDataType]] = ..., 
                vector_type: Optional[Union[str, EmbeddingVectorType]] = ..., 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

        @overload
        async def multi_modal_embed(
                self, 
                body: MultiModalEmbedRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

        @overload
        async def multi_modal_embed(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MultimodalEmbeddingResult: ...

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

    class azure.data.ai.models.EmbeddingContentItem(_Model):
        content: Optional[str]
        id: Optional[str]
        sas_token: Optional[str]
        type: Union[str, EmbeddingContentType]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[str] = ..., 
                id: Optional[str] = ..., 
                sas_token: Optional[str] = ..., 
                type: Union[str, EmbeddingContentType], 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        QUERY = "query"
        TEXT = "text"


    class azure.data.ai.models.EmbeddingDelivery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        LINK = "link"


    class azure.data.ai.models.EmbeddingEncodingFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASE64 = "base64"
        FLOAT = "float"


    class azure.data.ai.models.EmbeddingError(_Model):
        code: Union[str, EmbeddingErrorCode]
        details: Optional[str]
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, EmbeddingErrorCode], 
                details: Optional[str] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.EmbeddingErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_READ_FAILED = "EMBEDDING_BLOB_READ_FAILED"
        DELIVERY_NOT_SUPPORTED = "EMBEDDING_DELIVERY_NOT_SUPPORTED"
        INPUT_INVALID = "EMBEDDING_INPUT_INVALID"
        INVALID_REQUEST = "InvalidRequest"
        INVALID_REQUEST_BODY = "InvalidRequestBody"
        OUTPUT_WRITE_FAILED = "EMBEDDING_OUTPUT_WRITE_FAILED"
        URL_NOT_ALLOWED = "EMBEDDING_URL_NOT_ALLOWED"


    class azure.data.ai.models.EmbeddingImageFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GIF = "gif"
        JPEG = "jpeg"
        PNG = "png"
        WEBP = "webp"


    class azure.data.ai.models.EmbeddingOutputDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FLOAT16 = "float16"
        FLOAT32 = "float32"


    class azure.data.ai.models.EmbeddingVectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTH = "both"
        DENSE = "dense"
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


    class azure.data.ai.models.MultimodalDenseAndMultiVectorEmbedding(MultimodalEmbeddingData, discriminator='both'):
        embedding: EmbeddingVector
        format: Union[str, EmbeddingImageFormat]
        height: int
        id: str
        index: int
        input_tokens: int
        kind: Literal[EmbeddingVectorType.BOTH]
        multi_embedding: MultiEmbeddingVector
        shape: list[int]
        tokens: int
        truncated: bool
        type: Union[str, EmbeddingContentType]
        visual_tokens: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
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
                type: Union[str, EmbeddingContentType], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalDenseEmbedding(MultimodalEmbeddingData, discriminator='dense'):
        embedding: EmbeddingVector
        format: Union[str, EmbeddingImageFormat]
        height: int
        id: str
        index: int
        input_tokens: int
        kind: Literal[EmbeddingVectorType.DENSE]
        tokens: int
        truncated: bool
        type: Union[str, EmbeddingContentType]
        visual_tokens: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                embedding: EmbeddingVector, 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                type: Union[str, EmbeddingContentType], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingData(_Model):
        format: Optional[Union[str, EmbeddingImageFormat]]
        height: Optional[int]
        id: Optional[str]
        index: int
        input_tokens: Optional[int]
        kind: str
        tokens: Optional[int]
        truncated: Optional[bool]
        type: Union[str, EmbeddingContentType]
        visual_tokens: Optional[int]
        width: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                kind: str, 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                type: Union[str, EmbeddingContentType], 
                visual_tokens: Optional[int] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingOutput(_Model):
        bytes: int
        content_type: str
        expires_at: datetime
        id: str
        records: int
        sas_token: str
        sha256: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                bytes: int, 
                content_type: str, 
                expires_at: datetime, 
                id: str, 
                records: int, 
                sas_token: str, 
                sha256: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingResult(_Model):
        data: list[MultimodalEmbeddingData]
        model: str
        model_version: str
        object: Literal["list"]
        output: Optional[MultimodalEmbeddingOutput]
        output_data_type: Union[str, EmbeddingOutputDataType]
        usage: MultimodalEmbeddingUsage
        warnings: Optional[list[MultimodalEmbeddingWarning]]

        @overload
        def __init__(
                self, 
                *, 
                data: list[MultimodalEmbeddingData], 
                model: str, 
                model_version: str, 
                output: Optional[MultimodalEmbeddingOutput] = ..., 
                output_data_type: Union[str, EmbeddingOutputDataType], 
                usage: MultimodalEmbeddingUsage, 
                warnings: Optional[list[MultimodalEmbeddingWarning]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalEmbeddingUsage(_Model):
        image_count: int
        prompt_tokens: Optional[int]
        text_tokens: Optional[int]
        total_tokens: Optional[int]
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
        index: int
        input_tokens: Optional[int]
        message: str
        number: Optional[int]
        tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, EmbeddingWarningCode], 
                index: int, 
                input_tokens: Optional[int] = ..., 
                message: str, 
                number: Optional[int] = ..., 
                tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.data.ai.models.MultimodalMultiVectorEmbedding(MultimodalEmbeddingData, discriminator='multi'):
        format: Union[str, EmbeddingImageFormat]
        height: int
        id: str
        index: int
        input_tokens: int
        kind: Literal[EmbeddingVectorType.MULTI]
        multi_embedding: MultiEmbeddingVector
        shape: list[int]
        tokens: int
        truncated: bool
        type: Union[str, EmbeddingContentType]
        visual_tokens: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[Union[str, EmbeddingImageFormat]] = ..., 
                height: Optional[int] = ..., 
                id: Optional[str] = ..., 
                index: int, 
                input_tokens: Optional[int] = ..., 
                multi_embedding: MultiEmbeddingVector, 
                shape: list[int], 
                tokens: Optional[int] = ..., 
                truncated: Optional[bool] = ..., 
                type: Union[str, EmbeddingContentType], 
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

    class azure.data.ai.types.EmbeddingContentItem(TypedDict, total=False):
        key "content": str
        key "id": str
        key "sasToken": str
        key "type": Required[Union[str, EmbeddingContentType]]
        key "url": str
        content: str
        id: str
        sasToken: str
        type: Union[str, EmbeddingContentType]
        url: str


    class azure.data.ai.types.MultiModalEmbedRequest(TypedDict, total=False):
        key "contents": Required[list[EmbeddingContentItem]]
        key "delivery": Union[str, EmbeddingDelivery]
        key "dimensions": int
        key "encodingFormat": Union[str, EmbeddingEncodingFormat]
        key "maxNumVectors": int
        key "model": str
        key "modelVersion": str
        key "multiDimensions": int
        key "outputDtype": Union[str, EmbeddingOutputDataType]
        key "vectorType": Union[str, EmbeddingVectorType]
        contents: list[EmbeddingContentItem]
        delivery: Union[str, EmbeddingDelivery]
        dimensions: int
        encodingFormat: Union[str, EmbeddingEncodingFormat]
        maxNumVectors: int
        model: str
        modelVersion: str
        multiDimensions: int
        outputDtype: Union[str, EmbeddingOutputDataType]
        vectorType: Union[str, EmbeddingVectorType]


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