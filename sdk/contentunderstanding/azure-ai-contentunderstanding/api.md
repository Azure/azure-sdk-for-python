```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.contentunderstanding

    def azure.ai.contentunderstanding.to_llm_input(
            result: AnalysisResult, 
            *, 
            include_fields: bool = True, 
            include_markdown: bool = True, 
            metadata: Optional[Dict[str, Any]] = ...
        ) -> str: ...


    class azure.ai.contentunderstanding.ContentUnderstandingClient(GeneratedClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_analyze(
                self, 
                analyzer_id: str, 
                *, 
                inputs: list[AnalysisInput], 
                model_deployments: Optional[dict[str, str]] = ..., 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeLROPoller[AnalysisResult]: ...

        @overload
        def begin_analyze(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeLROPoller[AnalysisResult]: ...

        @overload
        def begin_analyze(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeLROPoller[AnalysisResult]: ...

        @distributed_trace
        def begin_analyze_binary(
                self, 
                analyzer_id: str, 
                binary_input: bytes, 
                *, 
                content_range: Optional[str] = ..., 
                content_type: str = "application/octet-stream", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeLROPoller[AnalysisResult]: ...

        @overload
        def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                source_analyzer_id: str, 
                source_azure_resource_id: Optional[str] = ..., 
                source_region: Optional[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        @overload
        def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        @overload
        def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        @overload
        def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: ContentAnalyzer, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        @overload
        def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: JSON, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        @overload
        def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: IO[bytes], 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ContentAnalyzer]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_analyzer(
                self, 
                analyzer_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_result(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_analyzer(
                self, 
                analyzer_id: str, 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @distributed_trace
        def get_defaults(self, **kwargs: Any) -> ContentUnderstandingDefaults: ...

        @distributed_trace
        def get_result_file(
                self, 
                operation_id: str, 
                path: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                *, 
                content_type: str = "application/json", 
                target_azure_resource_id: str, 
                target_region: Optional[str] = ..., 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @overload
        def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @overload
        def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @distributed_trace
        def list_analyzers(self, **kwargs: Any) -> ItemPaged[ContentAnalyzer]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: ContentAnalyzer, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        def update_defaults(
                self, 
                *, 
                content_type: str = "application/merge-patch+json", 
                model_deployments: Optional[RecordMergePatchUpdate] = ..., 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...

        @overload
        def update_defaults(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...

        @overload
        def update_defaults(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...


namespace azure.ai.contentunderstanding.aio

    class azure.ai.contentunderstanding.aio.ContentUnderstandingClient(GeneratedClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_analyze(
                self, 
                analyzer_id: str, 
                *, 
                inputs: list[AnalysisInput], 
                model_deployments: Optional[dict[str, str]] = ..., 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeAsyncLROPoller[AnalysisResult]: ...

        @overload
        async def begin_analyze(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeAsyncLROPoller[AnalysisResult]: ...

        @overload
        async def begin_analyze(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeAsyncLROPoller[AnalysisResult]: ...

        @distributed_trace_async
        async def begin_analyze_binary(
                self, 
                analyzer_id: str, 
                binary_input: bytes, 
                *, 
                content_range: Optional[str] = ..., 
                content_type: str = "application/octet-stream", 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                **kwargs: Any
            ) -> AnalyzeAsyncLROPoller[AnalysisResult]: ...

        @overload
        async def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                source_analyzer_id: str, 
                source_azure_resource_id: Optional[str] = ..., 
                source_region: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        @overload
        async def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        @overload
        async def begin_copy_analyzer(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        @overload
        async def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: ContentAnalyzer, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        @overload
        async def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: JSON, 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        @overload
        async def begin_create_analyzer(
                self, 
                analyzer_id: str, 
                resource: IO[bytes], 
                *, 
                allow_replace: Optional[bool] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ContentAnalyzer]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_analyzer(
                self, 
                analyzer_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_result(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_analyzer(
                self, 
                analyzer_id: str, 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @distributed_trace_async
        async def get_defaults(self, **kwargs: Any) -> ContentUnderstandingDefaults: ...

        @distributed_trace_async
        async def get_result_file(
                self, 
                operation_id: str, 
                path: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                *, 
                content_type: str = "application/json", 
                target_azure_resource_id: str, 
                target_region: Optional[str] = ..., 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @overload
        async def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @overload
        async def grant_copy_authorization(
                self, 
                analyzer_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CopyAuthorization: ...

        @distributed_trace
        def list_analyzers(self, **kwargs: Any) -> AsyncItemPaged[ContentAnalyzer]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: ContentAnalyzer, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        async def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        async def update_analyzer(
                self, 
                analyzer_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentAnalyzer: ...

        @overload
        async def update_defaults(
                self, 
                *, 
                content_type: str = "application/merge-patch+json", 
                model_deployments: Optional[RecordMergePatchUpdate] = ..., 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...

        @overload
        async def update_defaults(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...

        @overload
        async def update_defaults(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ContentUnderstandingDefaults: ...


namespace azure.ai.contentunderstanding.aio.models

    class azure.ai.contentunderstanding.aio.models.AnalyzeAsyncLROPoller(AsyncLROPoller[PollingReturnType_co]):
        property operation_id: str    # Read-only
        property usage: Optional[UsageDetails]    # Read-only

        @classmethod
        async def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PollingReturnType_co]: ...

        @classmethod
        def from_poller(cls, poller: AsyncLROPoller[PollingReturnType_co]) -> AnalyzeAsyncLROPoller[PollingReturnType_co]: ...


namespace azure.ai.contentunderstanding.models

    class azure.ai.contentunderstanding.models.AnalysisContent(_Model):
        analyzer_id: Optional[str]
        category: Optional[str]
        fields: Optional[dict[str, ContentField]]
        kind: str
        markdown: Optional[str]
        mime_type: str
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                analyzer_id: Optional[str] = ..., 
                category: Optional[str] = ..., 
                fields: Optional[dict[str, ContentField]] = ..., 
                kind: str, 
                markdown: Optional[str] = ..., 
                mime_type: str, 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.AnalysisContentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO_VISUAL = "audioVisual"
        DOCUMENT = "document"


    class azure.ai.contentunderstanding.models.AnalysisInput(_Model):
        content_range: Optional[str]
        data: Optional[bytes]
        mime_type: Optional[str]
        name: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_range: Optional[str] = ..., 
                data: Optional[bytes] = ..., 
                mime_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.AnalysisResult(_Model):
        analyzer_id: Optional[str]
        api_version: Optional[str]
        contents: list[AnalysisContent]
        created_at: Optional[datetime]
        string_encoding: Optional[str]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                analyzer_id: Optional[str] = ..., 
                api_version: Optional[str] = ..., 
                contents: list[AnalysisContent], 
                created_at: Optional[datetime] = ..., 
                string_encoding: Optional[str] = ..., 
                warnings: Optional[list[ODataV4Format]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.AnalyzeLROPoller(LROPoller[PollingReturnType_co]):
        property operation_id: str    # Read-only
        property usage: Optional[UsageDetails]    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AnalyzeLROPoller: ...

        @classmethod
        def from_poller(cls, poller: LROPoller[PollingReturnType_co]) -> AnalyzeLROPoller[PollingReturnType_co]: ...


    class azure.ai.contentunderstanding.models.AnnotationFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MARKDOWN = "markdown"
        NONE = "none"


    class azure.ai.contentunderstanding.models.ArrayField(ContentField, discriminator='array'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.ARRAY]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[List[Any]]
        value_array: Optional[list[ContentField]]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_array: Optional[list[ContentField]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.AudioVisualContent(AnalysisContent, discriminator='audioVisual'):
        analyzer_id: str
        camera_shot_times_ms: Optional[list[int]]
        category: str
        end_time_ms: int
        fields: dict[str, ContentField]
        height: Optional[int]
        key_frame_times_ms: Optional[list[int]]
        kind: Literal[AnalysisContentKind.AUDIO_VISUAL]
        markdown: str
        mime_type: str
        path: str
        segments: Optional[list[AudioVisualContentSegment]]
        start_time_ms: int
        transcript_phrases: Optional[list[TranscriptPhrase]]
        width: Optional[int]

        def _patched_audio_visual_content_init(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.contentunderstanding.models.AudioVisualContentSegment(_Model):
        category: str
        end_time_ms: int
        segment_id: str
        span: ContentSpan
        start_time_ms: int

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                end_time_ms: int, 
                segment_id: str, 
                span: ContentSpan, 
                start_time_ms: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.BooleanField(ContentField, discriminator='boolean'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.BOOLEAN]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[bool]
        value_boolean: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_boolean: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ChartFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHART_JS = "chartJs"
        MARKDOWN = "markdown"


    class azure.ai.contentunderstanding.models.ContentAnalyzer(_Model):
        analyzer_id: str
        base_analyzer_id: Optional[str]
        config: Optional[ContentAnalyzerConfig]
        created_at: datetime
        description: Optional[str]
        dynamic_field_schema: Optional[bool]
        field_schema: Optional[ContentFieldSchema]
        knowledge_sources: Optional[list[KnowledgeSource]]
        last_modified_at: datetime
        models: Optional[dict[str, str]]
        processing_location: Optional[Union[str, ProcessingLocation]]
        status: Union[str, ContentAnalyzerStatus]
        supported_models: Optional[SupportedModels]
        tags: Optional[dict[str, str]]
        warnings: Optional[list[ODataV4Format]]

        @overload
        def __init__(
                self, 
                *, 
                base_analyzer_id: Optional[str] = ..., 
                config: Optional[ContentAnalyzerConfig] = ..., 
                description: Optional[str] = ..., 
                dynamic_field_schema: Optional[bool] = ..., 
                field_schema: Optional[ContentFieldSchema] = ..., 
                knowledge_sources: Optional[list[KnowledgeSource]] = ..., 
                models: Optional[dict[str, str]] = ..., 
                processing_location: Optional[Union[str, ProcessingLocation]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentAnalyzerAnalyzeOperationStatus(_Model):
        error: Optional[ODataV4Format]
        id: str
        result: Optional[AnalysisResult]
        status: Union[str, OperationState]
        usage: Optional[UsageDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[AnalysisResult] = ..., 
                status: Union[str, OperationState], 
                usage: Optional[UsageDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentAnalyzerConfig(_Model):
        annotation_format: Optional[Union[str, AnnotationFormat]]
        chart_format: Optional[Union[str, ChartFormat]]
        content_categories: Optional[dict[str, ContentCategoryDefinition]]
        disable_face_blurring: Optional[bool]
        enable_figure_analysis: Optional[bool]
        enable_figure_description: Optional[bool]
        enable_formula: Optional[bool]
        enable_layout: Optional[bool]
        enable_ocr: Optional[bool]
        enable_segment: Optional[bool]
        estimate_field_source_and_confidence: Optional[bool]
        locales: Optional[list[str]]
        omit_content: Optional[bool]
        return_details: Optional[bool]
        segment_per_page: Optional[bool]
        table_format: Optional[Union[str, TableFormat]]

        @overload
        def __init__(
                self, 
                *, 
                annotation_format: Optional[Union[str, AnnotationFormat]] = ..., 
                chart_format: Optional[Union[str, ChartFormat]] = ..., 
                content_categories: Optional[dict[str, ContentCategoryDefinition]] = ..., 
                disable_face_blurring: Optional[bool] = ..., 
                enable_figure_analysis: Optional[bool] = ..., 
                enable_figure_description: Optional[bool] = ..., 
                enable_formula: Optional[bool] = ..., 
                enable_layout: Optional[bool] = ..., 
                enable_ocr: Optional[bool] = ..., 
                enable_segment: Optional[bool] = ..., 
                estimate_field_source_and_confidence: Optional[bool] = ..., 
                locales: Optional[list[str]] = ..., 
                omit_content: Optional[bool] = ..., 
                return_details: Optional[bool] = ..., 
                segment_per_page: Optional[bool] = ..., 
                table_format: Optional[Union[str, TableFormat]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentAnalyzerOperationStatus(_Model):
        error: Optional[ODataV4Format]
        id: str
        result: Optional[ContentAnalyzer]
        status: Union[str, OperationState]
        usage: Optional[UsageDetails]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[ContentAnalyzer] = ..., 
                status: Union[str, OperationState], 
                usage: Optional[UsageDetails] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentAnalyzerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "creating"
        DELETING = "deleting"
        FAILED = "failed"
        READY = "ready"


    class azure.ai.contentunderstanding.models.ContentCategoryDefinition(_Model):
        analyzer: Optional[ContentAnalyzer]
        analyzer_id: Optional[str]
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                analyzer: Optional[ContentAnalyzer] = ..., 
                analyzer_id: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentField(_Model):
        property value: Any    # Read-only
        confidence: Optional[float]
        source: Optional[str]
        spans: Optional[list[ContentSpan]]
        type: str
        value: Any

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentFieldDefinition(_Model):
        description: Optional[str]
        enum: Optional[list[str]]
        enum_descriptions: Optional[dict[str, str]]
        estimate_source_and_confidence: Optional[bool]
        examples: Optional[list[str]]
        item_definition: Optional[ContentFieldDefinition]
        method: Optional[Union[str, GenerationMethod]]
        properties: Optional[dict[str, ContentFieldDefinition]]
        ref: Optional[str]
        type: Optional[Union[str, ContentFieldType]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enum: Optional[list[str]] = ..., 
                enum_descriptions: Optional[dict[str, str]] = ..., 
                estimate_source_and_confidence: Optional[bool] = ..., 
                examples: Optional[list[str]] = ..., 
                item_definition: Optional[ContentFieldDefinition] = ..., 
                method: Optional[Union[str, GenerationMethod]] = ..., 
                properties: Optional[dict[str, ContentFieldDefinition]] = ..., 
                ref: Optional[str] = ..., 
                type: Optional[Union[str, ContentFieldType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentFieldSchema(_Model):
        definitions: Optional[dict[str, ContentFieldDefinition]]
        description: Optional[str]
        fields: dict[str, ContentFieldDefinition]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                definitions: Optional[dict[str, ContentFieldDefinition]] = ..., 
                description: Optional[str] = ..., 
                fields: dict[str, ContentFieldDefinition], 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentFieldType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        DATE = "date"
        INTEGER = "integer"
        JSON = "json"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"
        TIME = "time"


    class azure.ai.contentunderstanding.models.ContentSpan(_Model):
        length: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                length: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ContentUnderstandingDefaults(_Model):
        model_deployments: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                model_deployments: dict[str, str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.CopyAuthorization(_Model):
        expires_at: datetime
        source: str
        target_azure_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                expires_at: datetime, 
                source: str, 
                target_azure_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DateField(ContentField, discriminator='date'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.DATE]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[str]
        value_date: Optional[date]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_date: Optional[date] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentAnnotation(_Model):
        author: Optional[str]
        comments: Optional[list[DocumentAnnotationComment]]
        created_at: Optional[datetime]
        id: str
        kind: Union[str, DocumentAnnotationKind]
        last_modified_at: Optional[datetime]
        source: Optional[str]
        spans: Optional[list[ContentSpan]]
        tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[str] = ..., 
                comments: Optional[list[DocumentAnnotationComment]] = ..., 
                created_at: Optional[datetime] = ..., 
                id: str, 
                kind: Union[str, DocumentAnnotationKind], 
                last_modified_at: Optional[datetime] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentAnnotationComment(_Model):
        author: Optional[str]
        created_at: Optional[datetime]
        last_modified_at: Optional[datetime]
        message: str
        tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                author: Optional[str] = ..., 
                created_at: Optional[datetime] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                message: str, 
                tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentAnnotationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOLD = "bold"
        CIRCLE = "circle"
        HIGHLIGHT = "highlight"
        ITALIC = "italic"
        NOTE = "note"
        STRIKETHROUGH = "strikethrough"
        UNDERLINE = "underline"


    class azure.ai.contentunderstanding.models.DocumentBarcode(_Model):
        confidence: Optional[float]
        kind: Union[str, DocumentBarcodeKind]
        source: Optional[str]
        span: Optional[ContentSpan]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                kind: Union[str, DocumentBarcodeKind], 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentBarcodeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZTEC = "Aztec"
        CODABAR = "Codabar"
        CODE128 = "Code128"
        CODE39 = "Code39"
        CODE93 = "Code93"
        DATA_BAR = "DataBar"
        DATA_BAR_EXPANDED = "DataBarExpanded"
        DATA_MATRIX = "DataMatrix"
        EAN13 = "EAN13"
        EAN8 = "EAN8"
        ITF = "ITF"
        MAXI_CODE = "MaxiCode"
        MICRO_QR_CODE = "MicroQRCode"
        PDF417 = "PDF417"
        QR_CODE = "QRCode"
        UPCA = "UPCA"
        UPCE = "UPCE"


    class azure.ai.contentunderstanding.models.DocumentCaption(_Model):
        content: str
        elements: Optional[list[str]]
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                elements: Optional[list[str]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentChartFigure(DocumentFigure, discriminator='chart'):
        caption: DocumentCaption
        content: dict[str, Any]
        description: str
        elements: list[str]
        footnotes: list[DocumentFootnote]
        id: str
        kind: Literal[DocumentFigureKind.CHART]
        role: Union[str, SemanticRole]
        source: str
        span: ContentSpan

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[DocumentCaption] = ..., 
                content: dict[str, Any], 
                description: Optional[str] = ..., 
                elements: Optional[list[str]] = ..., 
                footnotes: Optional[list[DocumentFootnote]] = ..., 
                id: str, 
                role: Optional[Union[str, SemanticRole]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentContent(AnalysisContent, discriminator='document'):
        analyzer_id: str
        annotations: Optional[list[DocumentAnnotation]]
        category: str
        end_page_number: int
        fields: dict[str, ContentField]
        figures: Optional[list[DocumentFigure]]
        hyperlinks: Optional[list[DocumentHyperlink]]
        kind: Literal[AnalysisContentKind.DOCUMENT]
        markdown: str
        mime_type: str
        pages: Optional[list[DocumentPage]]
        paragraphs: Optional[list[DocumentParagraph]]
        path: str
        sections: Optional[list[DocumentSection]]
        segments: Optional[list[DocumentContentSegment]]
        start_page_number: int
        tables: Optional[list[DocumentTable]]
        unit: Optional[Union[str, LengthUnit]]

        @overload
        def __init__(
                self, 
                *, 
                analyzer_id: Optional[str] = ..., 
                annotations: Optional[list[DocumentAnnotation]] = ..., 
                category: Optional[str] = ..., 
                end_page_number: int, 
                fields: Optional[dict[str, ContentField]] = ..., 
                figures: Optional[list[DocumentFigure]] = ..., 
                hyperlinks: Optional[list[DocumentHyperlink]] = ..., 
                markdown: Optional[str] = ..., 
                mime_type: str, 
                pages: Optional[list[DocumentPage]] = ..., 
                paragraphs: Optional[list[DocumentParagraph]] = ..., 
                path: Optional[str] = ..., 
                sections: Optional[list[DocumentSection]] = ..., 
                segments: Optional[list[DocumentContentSegment]] = ..., 
                start_page_number: int, 
                tables: Optional[list[DocumentTable]] = ..., 
                unit: Optional[Union[str, LengthUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentContentSegment(_Model):
        category: str
        end_page_number: int
        segment_id: str
        span: ContentSpan
        start_page_number: int

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                end_page_number: int, 
                segment_id: str, 
                span: ContentSpan, 
                start_page_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentFigure(_Model):
        caption: Optional[DocumentCaption]
        description: Optional[str]
        elements: Optional[list[str]]
        footnotes: Optional[list[DocumentFootnote]]
        id: str
        kind: str
        role: Optional[Union[str, SemanticRole]]
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[DocumentCaption] = ..., 
                description: Optional[str] = ..., 
                elements: Optional[list[str]] = ..., 
                footnotes: Optional[list[DocumentFootnote]] = ..., 
                id: str, 
                kind: str, 
                role: Optional[Union[str, SemanticRole]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentFigureKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHART = "chart"
        MERMAID = "mermaid"
        UNKNOWN = "unknown"


    class azure.ai.contentunderstanding.models.DocumentFootnote(_Model):
        content: str
        elements: Optional[list[str]]
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                elements: Optional[list[str]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentFormula(_Model):
        confidence: Optional[float]
        kind: Union[str, DocumentFormulaKind]
        source: Optional[str]
        span: Optional[ContentSpan]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                kind: Union[str, DocumentFormulaKind], 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentFormulaKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISPLAY = "display"
        INLINE = "inline"


    class azure.ai.contentunderstanding.models.DocumentHyperlink(_Model):
        content: str
        source: Optional[str]
        span: Optional[ContentSpan]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ..., 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentLine(_Model):
        content: str
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentMermaidFigure(DocumentFigure, discriminator='mermaid'):
        caption: DocumentCaption
        content: str
        description: str
        elements: list[str]
        footnotes: list[DocumentFootnote]
        id: str
        kind: Literal[DocumentFigureKind.MERMAID]
        role: Union[str, SemanticRole]
        source: str
        span: ContentSpan

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[DocumentCaption] = ..., 
                content: str, 
                description: Optional[str] = ..., 
                elements: Optional[list[str]] = ..., 
                footnotes: Optional[list[DocumentFootnote]] = ..., 
                id: str, 
                role: Optional[Union[str, SemanticRole]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentPage(_Model):
        angle: Optional[float]
        barcodes: Optional[list[DocumentBarcode]]
        formulas: Optional[list[DocumentFormula]]
        height: Optional[float]
        lines: Optional[list[DocumentLine]]
        page_number: int
        spans: Optional[list[ContentSpan]]
        width: Optional[float]
        words: Optional[list[DocumentWord]]

        @overload
        def __init__(
                self, 
                *, 
                angle: Optional[float] = ..., 
                barcodes: Optional[list[DocumentBarcode]] = ..., 
                formulas: Optional[list[DocumentFormula]] = ..., 
                height: Optional[float] = ..., 
                lines: Optional[list[DocumentLine]] = ..., 
                page_number: int, 
                spans: Optional[list[ContentSpan]] = ..., 
                width: Optional[float] = ..., 
                words: Optional[list[DocumentWord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentParagraph(_Model):
        content: str
        role: Optional[Union[str, SemanticRole]]
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                role: Optional[Union[str, SemanticRole]] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentSection(_Model):
        elements: Optional[list[str]]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                elements: Optional[list[str]] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentTable(_Model):
        caption: Optional[DocumentCaption]
        cells: list[DocumentTableCell]
        column_count: int
        footnotes: Optional[list[DocumentFootnote]]
        role: Optional[Union[str, SemanticRole]]
        row_count: int
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[DocumentCaption] = ..., 
                cells: list[DocumentTableCell], 
                column_count: int, 
                footnotes: Optional[list[DocumentFootnote]] = ..., 
                role: Optional[Union[str, SemanticRole]] = ..., 
                row_count: int, 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentTableCell(_Model):
        column_index: int
        column_span: Optional[int]
        content: str
        elements: Optional[list[str]]
        kind: Optional[Union[str, DocumentTableCellKind]]
        row_index: int
        row_span: Optional[int]
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                column_index: int, 
                column_span: Optional[int] = ..., 
                content: str, 
                elements: Optional[list[str]] = ..., 
                kind: Optional[Union[str, DocumentTableCellKind]] = ..., 
                row_index: int, 
                row_span: Optional[int] = ..., 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.DocumentTableCellKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLUMN_HEADER = "columnHeader"
        CONTENT = "content"
        DESCRIPTION = "description"
        ROW_HEADER = "rowHeader"
        STUB_HEAD = "stubHead"


    class azure.ai.contentunderstanding.models.DocumentWord(_Model):
        confidence: Optional[float]
        content: str
        source: Optional[str]
        span: Optional[ContentSpan]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                content: str, 
                source: Optional[str] = ..., 
                span: Optional[ContentSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.GenerationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIFY = "classify"
        EXTRACT = "extract"
        GENERATE = "generate"


    class azure.ai.contentunderstanding.models.IntegerField(ContentField, discriminator='integer'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.INTEGER]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[int]
        value_integer: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_integer: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.JsonField(ContentField, discriminator='json'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.JSON]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[Any]
        value_json: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_json: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.KnowledgeSource(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.KnowledgeSourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LABELED_DATA = "labeledData"


    class azure.ai.contentunderstanding.models.LabeledDataKnowledgeSource(KnowledgeSource, discriminator='labeledData'):
        container_url: str
        file_list_path: str
        kind: Literal[KnowledgeSourceKind.LABELED_DATA]
        prefix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_url: str, 
                file_list_path: str, 
                prefix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.LengthUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCH = "inch"
        PIXEL = "pixel"


    class azure.ai.contentunderstanding.models.NumberField(ContentField, discriminator='number'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.NUMBER]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[float]
        value_number: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_number: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.ObjectField(ContentField, discriminator='object'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.OBJECT]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[Dict[str, Any]]
        value_object: Optional[dict[str, ContentField]]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_object: Optional[dict[str, ContentField]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.contentunderstanding.models.ProcessingLocation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_ZONE = "dataZone"
        GEOGRAPHY = "geography"
        GLOBAL = "global"


    class azure.ai.contentunderstanding.models.SemanticRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOOTNOTE = "footnote"
        FORMULA_BLOCK = "formulaBlock"
        PAGE_FOOTER = "pageFooter"
        PAGE_HEADER = "pageHeader"
        PAGE_NUMBER = "pageNumber"
        SECTION_HEADING = "sectionHeading"
        TITLE = "title"


    class azure.ai.contentunderstanding.models.StringField(ContentField, discriminator='string'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.STRING]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[str]
        value_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.SupportedModels(_Model):
        completion: Optional[list[str]]
        embedding: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                completion: Optional[list[str]] = ..., 
                embedding: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.TableFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML = "html"
        MARKDOWN = "markdown"


    class azure.ai.contentunderstanding.models.TimeField(ContentField, discriminator='time'):
        property value: Any    # Read-only
        confidence: float
        field_type: Literal[ContentFieldType.TIME]
        source: str
        spans: list[ContentSpan]
        type: str
        value: Optional[str]
        value_time: Optional[time]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                source: Optional[str] = ..., 
                spans: Optional[list[ContentSpan]] = ..., 
                type: str, 
                value_time: Optional[time] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.TranscriptPhrase(_Model):
        confidence: Optional[float]
        end_time_ms: int
        locale: Optional[str]
        span: Optional[ContentSpan]
        speaker: Optional[str]
        start_time_ms: int
        text: str
        words: list[TranscriptWord]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                end_time_ms: int, 
                locale: Optional[str] = ..., 
                span: Optional[ContentSpan] = ..., 
                speaker: Optional[str] = ..., 
                start_time_ms: int, 
                text: str, 
                words: list[TranscriptWord]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.TranscriptWord(_Model):
        end_time_ms: int
        span: Optional[ContentSpan]
        start_time_ms: int
        text: str

        @overload
        def __init__(
                self, 
                *, 
                end_time_ms: int, 
                span: Optional[ContentSpan] = ..., 
                start_time_ms: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentunderstanding.models.UsageDetails(_Model):
        audio_hours: Optional[float]
        contextualization_tokens: Optional[int]
        document_pages_basic: Optional[int]
        document_pages_minimal: Optional[int]
        document_pages_standard: Optional[int]
        tokens: Optional[dict[str, int]]
        video_hours: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                audio_hours: Optional[float] = ..., 
                contextualization_tokens: Optional[int] = ..., 
                document_pages_basic: Optional[int] = ..., 
                document_pages_minimal: Optional[int] = ..., 
                document_pages_standard: Optional[int] = ..., 
                tokens: Optional[dict[str, int]] = ..., 
                video_hours: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```