```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.textanalytics

    class azure.ai.textanalytics.AnalyzeTextLROPoller(LROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AnalyzeTextLROPoller[PollingReturnType_co]: ...


    class azure.ai.textanalytics.TextAnalysisClient(AnalysisTextClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def analyze_text(
                self, 
                body: AnalyzeTextInput, 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        def analyze_text(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        def analyze_text(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        def begin_analyze_text_job(
                self, 
                *, 
                actions: list[AnalyzeTextOperationAction], 
                cancel_after: Optional[float] = ..., 
                content_type: str = "application/json", 
                default_language: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                text_input: MultiLanguageTextInput, 
                **kwargs: Any
            ) -> AnalyzeTextLROPoller[ItemPaged[TextActions]]: ...

        @overload
        def begin_analyze_text_job(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextLROPoller[ItemPaged[TextActions]]: ...

        @overload
        def begin_analyze_text_job(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextLROPoller[ItemPaged[TextActions]]: ...

        @distributed_trace
        def begin_cancel_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_job_status(
                self, 
                job_id: str, 
                *, 
                show_stats: Optional[bool] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextOperationState: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.textanalytics.aio

    class azure.ai.textanalytics.aio.AnalyzeTextAsyncLROPoller(AsyncLROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[PollingReturnType_co], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AnalyzeTextAsyncLROPoller[PollingReturnType_co]: ...


    class azure.ai.textanalytics.aio.TextAnalysisClient(AnalysisTextClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def analyze_text(
                self, 
                body: AnalyzeTextInput, 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        async def analyze_text(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        async def analyze_text(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                show_stats: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        async def begin_analyze_text_job(
                self, 
                *, 
                actions: list[AnalyzeTextOperationAction], 
                cancel_after: Optional[float] = ..., 
                content_type: str = "application/json", 
                default_language: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                text_input: MultiLanguageTextInput, 
                **kwargs: Any
            ) -> AnalyzeTextAsyncLROPoller[AsyncItemPaged[TextActions]]: ...

        @overload
        async def begin_analyze_text_job(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextAsyncLROPoller[AsyncItemPaged[TextActions]]: ...

        @overload
        async def begin_analyze_text_job(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextAsyncLROPoller[AsyncItemPaged[TextActions]]: ...

        @distributed_trace_async
        async def begin_cancel_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_job_status(
                self, 
                job_id: str, 
                *, 
                show_stats: Optional[bool] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AnalyzeTextOperationState: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.textanalytics.models

    class azure.ai.textanalytics.models.AbstractiveSummarizationActionContent(_Model):
        instruction: Optional[str]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        sentence_count: Optional[int]
        string_index_type: Optional[Union[str, StringIndexType]]
        summary_length: Optional[Union[str, SummaryLengthBucket]]

        @overload
        def __init__(
                self, 
                *, 
                instruction: Optional[str] = ..., 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                sentence_count: Optional[int] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ..., 
                summary_length: Optional[Union[str, SummaryLengthBucket]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AbstractiveSummarizationOperationAction(AnalyzeTextOperationAction, discriminator='AbstractiveSummarization'):
        action_content: Optional[AbstractiveSummarizationActionContent]
        kind: Literal[AnalyzeTextOperationActionKind.ABSTRACTIVE_SUMMARIZATION]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[AbstractiveSummarizationActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AbstractiveSummarizationOperationResult(AnalyzeTextLROResult, discriminator='AbstractiveSummarizationLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.ABSTRACTIVE_SUMMARIZATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: AbstractiveSummarizationResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: AbstractiveSummarizationResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AbstractiveSummarizationResult(_Model):
        documents: list[AbstractiveSummaryActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[AbstractiveSummaryActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AbstractiveSummary(_Model):
        contexts: Optional[list[SummaryContext]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                contexts: Optional[list[SummaryContext]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AbstractiveSummaryActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        id: str
        statistics: Optional[DocumentStatistics]
        summaries: list[AbstractiveSummary]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                summaries: list[AbstractiveSummary], 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AddressMetadata(BaseMetadata, discriminator='AddressMetadata'):
        address_lines: list[str]
        city: Optional[str]
        country_or_region: Optional[str]
        formated_address: str
        metadata_kind: Literal[MetadataKind.ADDRESS_METADATA]
        postal_code: Optional[str]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_lines: list[str], 
                city: Optional[str] = ..., 
                country_or_region: Optional[str] = ..., 
                formated_address: str, 
                postal_code: Optional[str] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AgeMetadata(BaseMetadata, discriminator='AgeMetadata'):
        metadata_kind: Literal[MetadataKind.AGE_METADATA]
        unit: Union[str, AgeUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, AgeUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AgeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        MONTH = "Month"
        UNSPECIFIED = "Unspecified"
        WEEK = "Week"
        YEAR = "Year"


    class azure.ai.textanalytics.models.AllowOverlapEntityPolicyType(EntityOverlapPolicy, discriminator='allowOverlap'):
        policy_kind: Literal[PolicyKind.ALLOW_OVERLAP]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextEntitiesResult(AnalyzeTextResult, discriminator='EntityRecognitionResults'):
        kind: Literal[AnalyzeTextResultsKind.ENTITY_RECOGNITION_RESULTS]
        results: EntitiesWithMetadataAutoResult

        @overload
        def __init__(
                self, 
                *, 
                results: EntitiesWithMetadataAutoResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextEntityLinkingResult(AnalyzeTextResult, discriminator='EntityLinkingResults'):
        kind: Literal[AnalyzeTextResultsKind.ENTITY_LINKING_RESULTS]
        results: EntityLinkingResult

        @overload
        def __init__(
                self, 
                *, 
                results: EntityLinkingResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextError(_Model):
        code: Union[str, AnalyzeTextErrorCode]
        details: Optional[list[AnalyzeTextError]]
        innererror: Optional[InnerErrorModel]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, AnalyzeTextErrorCode], 
                details: Optional[list[AnalyzeTextError]] = ..., 
                innererror: Optional[InnerErrorModel] = ..., 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_COGNITIVE_SEARCH_INDEX_LIMIT_REACHED = "AzureCognitiveSearchIndexLimitReached"
        AZURE_COGNITIVE_SEARCH_INDEX_NOT_FOUND = "AzureCognitiveSearchIndexNotFound"
        AZURE_COGNITIVE_SEARCH_NOT_FOUND = "AzureCognitiveSearchNotFound"
        AZURE_COGNITIVE_SEARCH_THROTTLING = "AzureCognitiveSearchThrottling"
        CONFLICT = "Conflict"
        FORBIDDEN = "Forbidden"
        INTERNAL_SERVER_ERROR = "InternalServerError"
        INVALID_ARGUMENT = "InvalidArgument"
        INVALID_REQUEST = "InvalidRequest"
        NOT_FOUND = "NotFound"
        OPERATION_NOT_FOUND = "OperationNotFound"
        PROJECT_NOT_FOUND = "ProjectNotFound"
        QUOTA_EXCEEDED = "QuotaExceeded"
        SERVICE_UNAVAILABLE = "ServiceUnavailable"
        TIMEOUT = "Timeout"
        TOO_MANY_REQUESTS = "TooManyRequests"
        UNAUTHORIZED = "Unauthorized"
        WARNING = "Warning"


    class azure.ai.textanalytics.models.AnalyzeTextInput(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextInputKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTITY_LINKING = "EntityLinking"
        ENTITY_RECOGNITION = "EntityRecognition"
        KEY_PHRASE_EXTRACTION = "KeyPhraseExtraction"
        LANGUAGE_DETECTION = "LanguageDetection"
        PII_ENTITY_RECOGNITION = "PiiEntityRecognition"
        SENTIMENT_ANALYSIS = "SentimentAnalysis"


    class azure.ai.textanalytics.models.AnalyzeTextKeyPhraseResult(AnalyzeTextResult, discriminator='KeyPhraseExtractionResults'):
        kind: Literal[AnalyzeTextResultsKind.KEY_PHRASE_EXTRACTION_RESULTS]
        results: KeyPhraseResult

        @overload
        def __init__(
                self, 
                *, 
                results: KeyPhraseResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextLROResult(_Model):
        kind: str
        last_update_date_time: datetime
        status: Union[str, TextActionState]
        task_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                last_update_date_time: datetime, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextLanguageDetectionResult(AnalyzeTextResult, discriminator='LanguageDetectionResults'):
        kind: Literal[AnalyzeTextResultsKind.LANGUAGE_DETECTION_RESULTS]
        results: LanguageDetectionResult

        @overload
        def __init__(
                self, 
                *, 
                results: LanguageDetectionResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextOperationAction(_Model):
        kind: str
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextOperationActionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSTRACTIVE_SUMMARIZATION = "AbstractiveSummarization"
        CUSTOM_ENTITY_RECOGNITION = "CustomEntityRecognition"
        CUSTOM_MULTI_LABEL_CLASSIFICATION = "CustomMultiLabelClassification"
        CUSTOM_SINGLE_LABEL_CLASSIFICATION = "CustomSingleLabelClassification"
        ENTITY_LINKING = "EntityLinking"
        ENTITY_RECOGNITION = "EntityRecognition"
        EXTRACTIVE_SUMMARIZATION = "ExtractiveSummarization"
        HEALTHCARE = "Healthcare"
        KEY_PHRASE_EXTRACTION = "KeyPhraseExtraction"
        PII_ENTITY_RECOGNITION = "PiiEntityRecognition"
        SENTIMENT_ANALYSIS = "SentimentAnalysis"


    class azure.ai.textanalytics.models.AnalyzeTextOperationResultsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSTRACTIVE_SUMMARIZATION_OPERATION_RESULTS = "AbstractiveSummarizationLROResults"
        CUSTOM_ENTITY_RECOGNITION_OPERATION_RESULTS = "CustomEntityRecognitionLROResults"
        CUSTOM_MULTI_LABEL_CLASSIFICATION_OPERATION_RESULTS = "CustomMultiLabelClassificationLROResults"
        CUSTOM_SINGLE_LABEL_CLASSIFICATION_OPERATION_RESULTS = "CustomSingleLabelClassificationLROResults"
        ENTITY_LINKING_OPERATION_RESULTS = "EntityLinkingLROResults"
        ENTITY_RECOGNITION_OPERATION_RESULTS = "EntityRecognitionLROResults"
        EXTRACTIVE_SUMMARIZATION_OPERATION_RESULTS = "ExtractiveSummarizationLROResults"
        HEALTHCARE_OPERATION_RESULTS = "HealthcareLROResults"
        KEY_PHRASE_EXTRACTION_OPERATION_RESULTS = "KeyPhraseExtractionLROResults"
        PII_ENTITY_RECOGNITION_OPERATION_RESULTS = "PiiEntityRecognitionLROResults"
        SENTIMENT_ANALYSIS_OPERATION_RESULTS = "SentimentAnalysisLROResults"


    class azure.ai.textanalytics.models.AnalyzeTextOperationState(_Model):
        actions: TextActions
        created_at: datetime
        display_name: Optional[str]
        errors: Optional[list[AnalyzeTextError]]
        expires_on: Optional[datetime]
        job_id: str
        last_updated_at: datetime
        next_link: Optional[str]
        statistics: Optional[RequestStatistics]
        status: Union[str, TextActionState]

        @overload
        def __init__(
                self, 
                *, 
                actions: TextActions, 
                created_at: datetime, 
                display_name: Optional[str] = ..., 
                errors: Optional[list[AnalyzeTextError]] = ..., 
                expires_on: Optional[datetime] = ..., 
                last_updated_at: datetime, 
                next_link: Optional[str] = ..., 
                statistics: Optional[RequestStatistics] = ..., 
                status: Union[str, TextActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextPiiResult(AnalyzeTextResult, discriminator='PiiEntityRecognitionResults'):
        kind: Literal[AnalyzeTextResultsKind.PII_ENTITY_RECOGNITION_RESULTS]
        results: PiiResult

        @overload
        def __init__(
                self, 
                *, 
                results: PiiResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextResult(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AnalyzeTextResultsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTITY_LINKING_RESULTS = "EntityLinkingResults"
        ENTITY_RECOGNITION_RESULTS = "EntityRecognitionResults"
        KEY_PHRASE_EXTRACTION_RESULTS = "KeyPhraseExtractionResults"
        LANGUAGE_DETECTION_RESULTS = "LanguageDetectionResults"
        PII_ENTITY_RECOGNITION_RESULTS = "PiiEntityRecognitionResults"
        SENTIMENT_ANALYSIS_RESULTS = "SentimentAnalysisResults"


    class azure.ai.textanalytics.models.AnalyzeTextSentimentResult(AnalyzeTextResult, discriminator='SentimentAnalysisResults'):
        kind: Literal[AnalyzeTextResultsKind.SENTIMENT_ANALYSIS_RESULTS]
        results: SentimentResult

        @overload
        def __init__(
                self, 
                *, 
                results: SentimentResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AreaMetadata(BaseMetadata, discriminator='AreaMetadata'):
        metadata_kind: Literal[MetadataKind.AREA_METADATA]
        unit: Union[str, AreaUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, AreaUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.AreaUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACRE = "Acre"
        SQUARE_CENTIMETER = "SquareCentimeter"
        SQUARE_DECAMETER = "SquareDecameter"
        SQUARE_DECIMETER = "SquareDecimeter"
        SQUARE_FOOT = "SquareFoot"
        SQUARE_HECTOMETER = "SquareHectometer"
        SQUARE_INCH = "SquareInch"
        SQUARE_KILOMETER = "SquareKilometer"
        SQUARE_METER = "SquareMeter"
        SQUARE_MILE = "SquareMile"
        SQUARE_MILLIMETER = "SquareMillimeter"
        SQUARE_YARD = "SquareYard"
        UNSPECIFIED = "Unspecified"


    class azure.ai.textanalytics.models.BaseMetadata(_Model):
        metadata_kind: str

        @overload
        def __init__(
                self, 
                *, 
                metadata_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.BaseRedactionPolicy(_Model):
        entity_types: Optional[list[Union[str, PiiCategoriesExclude]]]
        is_default: Optional[bool]
        policy_kind: str
        policy_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                entity_types: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                is_default: Optional[bool] = ..., 
                policy_kind: str, 
                policy_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CharacterMaskPolicyType(BaseRedactionPolicy, discriminator='characterMask'):
        entity_types: Union[list[str, PiiCategoriesExclude]]
        is_default: bool
        policy_kind: Literal[RedactionPolicyKind.CHARACTER_MASK]
        policy_name: str
        redaction_character: Optional[Union[str, RedactionCharacter]]
        unmask_from_end: Optional[bool]
        unmask_length: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                entity_types: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                is_default: Optional[bool] = ..., 
                policy_name: Optional[str] = ..., 
                redaction_character: Optional[Union[str, RedactionCharacter]] = ..., 
                unmask_from_end: Optional[bool] = ..., 
                unmask_length: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ClassificationActionResult(_Model):
        class_property: list[ClassificationResult]
        detected_language: Optional[DetectedLanguage]
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                class_property: list[ClassificationResult], 
                detected_language: Optional[DetectedLanguage] = ..., 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ClassificationResult(_Model):
        category: str
        confidence_score: float

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence_score: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ConfidenceScoreThreshold(_Model):
        default: float
        overrides: Optional[list[ConfidenceScoreThresholdOverride]]

        @overload
        def __init__(
                self, 
                *, 
                default: float, 
                overrides: Optional[list[ConfidenceScoreThresholdOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ConfidenceScoreThresholdOverride(_Model):
        entity: Union[str, PiiCategoriesExclude]
        language: Optional[str]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                entity: Union[str, PiiCategoriesExclude], 
                language: Optional[str] = ..., 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CurrencyMetadata(BaseMetadata, discriminator='CurrencyMetadata'):
        iso4217: Optional[str]
        metadata_kind: Literal[MetadataKind.CURRENCY_METADATA]
        unit: str
        value: float

        @overload
        def __init__(
                self, 
                *, 
                iso4217: Optional[str] = ..., 
                unit: str, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomEntitiesActionContent(_Model):
        deployment_name: str
        logging_opt_out: Optional[bool]
        project_name: str
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                logging_opt_out: Optional[bool] = ..., 
                project_name: str, 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomEntitiesLROTask(AnalyzeTextOperationAction, discriminator='CustomEntityRecognition'):
        kind: Literal[AnalyzeTextOperationActionKind.CUSTOM_ENTITY_RECOGNITION]
        name: str
        parameters: Optional[CustomEntitiesActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[CustomEntitiesActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomEntitiesResult(_Model):
        deployment_name: str
        documents: list[CustomEntityActionResult]
        errors: list[DocumentError]
        project_name: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                documents: list[CustomEntityActionResult], 
                errors: list[DocumentError], 
                project_name: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomEntityActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        entities: list[NamedEntity]
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                entities: list[NamedEntity], 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomEntityRecognitionOperationResult(AnalyzeTextLROResult, discriminator='CustomEntityRecognitionLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.CUSTOM_ENTITY_RECOGNITION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: CustomEntitiesResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: CustomEntitiesResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomLabelClassificationResult(_Model):
        deployment_name: str
        documents: list[ClassificationActionResult]
        errors: list[DocumentError]
        project_name: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                documents: list[ClassificationActionResult], 
                errors: list[DocumentError], 
                project_name: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomMultiLabelClassificationActionContent(_Model):
        deployment_name: str
        logging_opt_out: Optional[bool]
        project_name: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                logging_opt_out: Optional[bool] = ..., 
                project_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomMultiLabelClassificationOperationAction(AnalyzeTextOperationAction, discriminator='CustomMultiLabelClassification'):
        action_content: Optional[CustomMultiLabelClassificationActionContent]
        kind: Literal[AnalyzeTextOperationActionKind.CUSTOM_MULTI_LABEL_CLASSIFICATION]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[CustomMultiLabelClassificationActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomMultiLabelClassificationOperationResult(AnalyzeTextLROResult, discriminator='CustomMultiLabelClassificationLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.CUSTOM_MULTI_LABEL_CLASSIFICATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: CustomLabelClassificationResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: CustomLabelClassificationResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomSingleLabelClassificationActionContent(_Model):
        deployment_name: str
        logging_opt_out: Optional[bool]
        project_name: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                logging_opt_out: Optional[bool] = ..., 
                project_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomSingleLabelClassificationOperationAction(AnalyzeTextOperationAction, discriminator='CustomSingleLabelClassification'):
        action_content: Optional[CustomSingleLabelClassificationActionContent]
        kind: Literal[AnalyzeTextOperationActionKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[CustomSingleLabelClassificationActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.CustomSingleLabelClassificationOperationResult(AnalyzeTextLROResult, discriminator='CustomSingleLabelClassificationLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.CUSTOM_SINGLE_LABEL_CLASSIFICATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: CustomLabelClassificationResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: CustomLabelClassificationResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DateMetadata(BaseMetadata, discriminator='DateMetadata'):
        dates: Optional[list[DateValue]]
        metadata_kind: Literal[MetadataKind.DATE_METADATA]

        @overload
        def __init__(
                self, 
                *, 
                dates: Optional[list[DateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DateTimeMetadata(BaseMetadata, discriminator='DateTimeMetadata'):
        dates: Optional[list[DateValue]]
        metadata_kind: Literal[MetadataKind.DATE_TIME_METADATA]

        @overload
        def __init__(
                self, 
                *, 
                dates: Optional[list[DateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DateValue(_Model):
        modifier: Optional[Union[str, TemporalModifier]]
        timex: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                modifier: Optional[Union[str, TemporalModifier]] = ..., 
                timex: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DetectedLanguage(_Model):
        confidence_score: float
        iso6391_name: str
        name: str
        script_iso15924_code: Optional[Union[str, ScriptCode]]
        script_name: Optional[Union[str, ScriptKind]]

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: float, 
                iso6391_name: str, 
                name: str, 
                script_iso15924_code: Optional[Union[str, ScriptCode]] = ..., 
                script_name: Optional[Union[str, ScriptKind]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DocumentError(_Model):
        error: AnalyzeTextError
        id: str

        @overload
        def __init__(
                self, 
                *, 
                error: AnalyzeTextError, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DocumentSentiment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "mixed"
        NEGATIVE = "negative"
        NEUTRAL = "neutral"
        POSITIVE = "positive"


    class azure.ai.textanalytics.models.DocumentStatistics(_Model):
        characters_count: int
        transactions_count: int

        @overload
        def __init__(
                self, 
                *, 
                characters_count: int, 
                transactions_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.DocumentWarning(_Model):
        code: Union[str, WarningCode]
        message: str
        target_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, WarningCode], 
                message: str, 
                target_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitiesActionContent(_Model):
        exclusions: Optional[list[Union[str, EntityCategory]]]
        inclusions: Optional[list[Union[str, EntityCategory]]]
        inference_options: Optional[EntityInferenceConfig]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        overlap_policy: Optional[EntityOverlapPolicy]
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                exclusions: Optional[list[Union[str, EntityCategory]]] = ..., 
                inclusions: Optional[list[Union[str, EntityCategory]]] = ..., 
                inference_options: Optional[EntityInferenceConfig] = ..., 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                overlap_policy: Optional[EntityOverlapPolicy] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitiesLROTask(AnalyzeTextOperationAction, discriminator='EntityRecognition'):
        kind: Literal[AnalyzeTextOperationActionKind.ENTITY_RECOGNITION]
        name: str
        parameters: Optional[EntitiesActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[EntitiesActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitiesResult(_Model):
        documents: list[EntityActionResultWithMetadata]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[EntityActionResultWithMetadata], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitiesWithMetadataAutoResult(_Model):
        documents: list[EntityActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[EntityActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        entities: list[NamedEntityWithMetadata]
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                entities: list[NamedEntityWithMetadata], 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityActionResultWithMetadata(_Model):
        entities: list[NamedEntityWithMetadata]
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                entities: list[NamedEntityWithMetadata], 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS = "Address"
        AGE = "Age"
        AIRPORT = "Airport"
        AREA = "Area"
        CITY = "City"
        COMPUTING_PRODUCT = "ComputingProduct"
        CONTINENT = "Continent"
        COUNTRY_REGION = "CountryRegion"
        CULTURAL_EVENT = "CulturalEvent"
        CURRENCY = "Currency"
        DATE = "Date"
        DATE_RANGE = "DateRange"
        DATE_TIME = "DateTime"
        DATE_TIME_RANGE = "DateTimeRange"
        DIMENSION = "Dimension"
        DURATION = "Duration"
        EMAIL = "Email"
        EVENT = "Event"
        GEOLOGICAL = "Geological"
        GEO_POLITICAL_ENTITY = "GPE"
        HEIGHT = "Height"
        INFORMATION = "Information"
        IP_ADDRESS = "IP"
        LENGTH = "Length"
        LOCATION = "Location"
        NATURAL_EVENT = "NaturalEvent"
        NUMBER = "Number"
        NUMBER_RANGE = "NumberRange"
        NUMERIC = "Numeric"
        ORDINAL = "Ordinal"
        ORGANIZATION = "Organization"
        ORGANIZATION_MEDICAL = "OrganizationMedical"
        ORGANIZATION_SPORTS = "OrganizationSports"
        ORGANIZATION_STOCK_EXCHANGE = "OrganizationStockExchange"
        PERCENTAGE = "Percentage"
        PERSON = "Person"
        PERSON_TYPE = "PersonType"
        PHONE_NUMBER = "PhoneNumber"
        PRODUCT = "Product"
        SET_TEMPORAL = "SetTemporal"
        SKILL = "Skill"
        SPEED = "Speed"
        SPORTS_EVENT = "SportsEvent"
        STATE = "State"
        STRUCTURAL = "Structural"
        TEMPERATURE = "Temperature"
        TEMPORAL = "Temporal"
        TIME = "Time"
        TIME_RANGE = "TimeRange"
        URI = "URL"
        VOLUME = "Volume"
        WEIGHT = "Weight"


    class azure.ai.textanalytics.models.EntityInferenceConfig(_Model):
        exclude_normalized_values: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                exclude_normalized_values: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingActionContent(_Model):
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        entities: list[LinkedEntity]
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                entities: list[LinkedEntity], 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingLROTask(AnalyzeTextOperationAction, discriminator='EntityLinking'):
        kind: Literal[AnalyzeTextOperationActionKind.ENTITY_LINKING]
        name: str
        parameters: Optional[EntityLinkingActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[EntityLinkingActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingMatch(_Model):
        confidence_score: float
        length: int
        offset: int
        text: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: float, 
                length: int, 
                offset: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingOperationResult(AnalyzeTextLROResult, discriminator='EntityLinkingLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.ENTITY_LINKING_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: EntityLinkingResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: EntityLinkingResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityLinkingResult(_Model):
        documents: list[EntityLinkingActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[EntityLinkingActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityMaskPolicyType(BaseRedactionPolicy, discriminator='entityMask'):
        entity_types: Union[list[str, PiiCategoriesExclude]]
        is_default: bool
        policy_kind: Literal[RedactionPolicyKind.ENTITY_MASK]
        policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                entity_types: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                is_default: Optional[bool] = ..., 
                policy_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityOverlapPolicy(_Model):
        policy_kind: str

        @overload
        def __init__(
                self, 
                *, 
                policy_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityRecognitionOperationResult(AnalyzeTextLROResult, discriminator='EntityRecognitionLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.ENTITY_RECOGNITION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: EntitiesResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: EntitiesResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitySynonym(_Model):
        language: Optional[str]
        synonym: str

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                synonym: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntitySynonyms(_Model):
        entity_type: Union[str, EntityCategory]
        synonyms: list[EntitySynonym]

        @overload
        def __init__(
                self, 
                *, 
                entity_type: Union[str, EntityCategory], 
                synonyms: list[EntitySynonym]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.EntityTag(_Model):
        confidence_score: Optional[float]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: Optional[float] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ErrorResponse(_Model):
        error: AnalyzeTextError

        @overload
        def __init__(
                self, 
                *, 
                error: AnalyzeTextError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractedSummaryActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        id: str
        sentences: list[ExtractedSummarySentence]
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                id: str, 
                sentences: list[ExtractedSummarySentence], 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractedSummarySentence(_Model):
        length: int
        offset: int
        rank_score: float
        text: str

        @overload
        def __init__(
                self, 
                *, 
                length: int, 
                offset: int, 
                rank_score: float, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractiveSummarizationActionContent(_Model):
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        query: Optional[str]
        sentence_count: Optional[int]
        sort_by: Optional[Union[str, ExtractiveSummarizationSortingCriteria]]
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                query: Optional[str] = ..., 
                sentence_count: Optional[int] = ..., 
                sort_by: Optional[Union[str, ExtractiveSummarizationSortingCriteria]] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractiveSummarizationOperationAction(AnalyzeTextOperationAction, discriminator='ExtractiveSummarization'):
        action_content: Optional[ExtractiveSummarizationActionContent]
        kind: Literal[AnalyzeTextOperationActionKind.EXTRACTIVE_SUMMARIZATION]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[ExtractiveSummarizationActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractiveSummarizationOperationResult(AnalyzeTextLROResult, discriminator='ExtractiveSummarizationLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.EXTRACTIVE_SUMMARIZATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: ExtractiveSummarizationResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: ExtractiveSummarizationResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractiveSummarizationResult(_Model):
        documents: list[ExtractedSummaryActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[ExtractedSummaryActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ExtractiveSummarizationSortingCriteria(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFSET = "Offset"
        RANK = "Rank"


    class azure.ai.textanalytics.models.FhirBundle(_Model):


    class azure.ai.textanalytics.models.FhirVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENUM_4_0_1 = "4.0.1"


    class azure.ai.textanalytics.models.HealthcareActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        entities: list[HealthcareEntity]
        fhir_bundle: Optional[FhirBundle]
        id: str
        relations: list[HealthcareRelation]
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                entities: list[HealthcareEntity], 
                fhir_bundle: Optional[FhirBundle] = ..., 
                id: str, 
                relations: list[HealthcareRelation], 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareAssertion(_Model):
        association: Optional[Union[str, HealthcareAssertionAssociation]]
        certainty: Optional[Union[str, HealthcareAssertionCertainty]]
        conditionality: Optional[Union[str, HealthcareAssertionConditionality]]
        temporality: Optional[Union[str, HealthcareAssertionTemporality]]

        @overload
        def __init__(
                self, 
                *, 
                association: Optional[Union[str, HealthcareAssertionAssociation]] = ..., 
                certainty: Optional[Union[str, HealthcareAssertionCertainty]] = ..., 
                conditionality: Optional[Union[str, HealthcareAssertionConditionality]] = ..., 
                temporality: Optional[Union[str, HealthcareAssertionTemporality]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareAssertionAssociation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER = "other"
        SUBJECT = "subject"


    class azure.ai.textanalytics.models.HealthcareAssertionCertainty(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEGATIVE = "negative"
        NEGATIVE_POSSIBLE = "negativePossible"
        NEUTRAL_POSSIBLE = "neutralPossible"
        POSITIVE = "positive"
        POSITIVE_POSSIBLE = "positivePossible"


    class azure.ai.textanalytics.models.HealthcareAssertionConditionality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL = "conditional"
        HYPOTHETICAL = "hypothetical"


    class azure.ai.textanalytics.models.HealthcareAssertionTemporality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "current"
        FUTURE = "future"
        PAST = "past"


    class azure.ai.textanalytics.models.HealthcareDocumentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLINICAL_TRIAL = "ClinicalTrial"
        CONSULT = "Consult"
        DISCHARGE_SUMMARY = "DischargeSummary"
        HISTORY_AND_PHYSICAL = "HistoryAndPhysical"
        IMAGING = "Imaging"
        NONE = "None"
        PATHOLOGY = "Pathology"
        PROCEDURE_NOTE = "ProcedureNote"
        PROGRESS_NOTE = "ProgressNote"


    class azure.ai.textanalytics.models.HealthcareEntity(_Model):
        assertion: Optional[HealthcareAssertion]
        category: Union[str, HealthcareEntityCategory]
        confidence_score: float
        length: int
        links: Optional[list[HealthcareEntityLink]]
        name: Optional[str]
        offset: int
        subcategory: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                assertion: Optional[HealthcareAssertion] = ..., 
                category: Union[str, HealthcareEntityCategory], 
                confidence_score: float, 
                length: int, 
                links: Optional[list[HealthcareEntityLink]] = ..., 
                name: Optional[str] = ..., 
                offset: int, 
                subcategory: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareEntityCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMINISTRATIVE_EVENT = "AdministrativeEvent"
        AGE = "Age"
        ALLERGEN = "Allergen"
        BODY_STRUCTURE = "BodyStructure"
        CARE_ENVIRONMENT = "CareEnvironment"
        CONDITION_QUALIFIER = "ConditionQualifier"
        CONDITION_SCALE = "ConditionScale"
        COURSE = "Course"
        DATE = "Date"
        DIAGNOSIS = "Diagnosis"
        DIRECTION = "Direction"
        DOSAGE = "Dosage"
        EMPLOYMENT = "Employment"
        ETHNICITY = "Ethnicity"
        EXAMINATION_NAME = "ExaminationName"
        EXPRESSION = "Expression"
        FAMILY_RELATION = "FamilyRelation"
        FREQUENCY = "Frequency"
        GENDER = "Gender"
        GENE_OR_PROTEIN = "GeneOrProtein"
        HEALTHCARE_PROFESSION = "HealthcareProfession"
        LIVING_STATUS = "LivingStatus"
        MEASUREMENT_UNIT = "MeasurementUnit"
        MEASUREMENT_VALUE = "MeasurementValue"
        MEDICATION_CLASS = "MedicationClass"
        MEDICATION_FORM = "MedicationForm"
        MEDICATION_NAME = "MedicationName"
        MEDICATION_ROUTE = "MedicationRoute"
        MUTATION_TYPE = "MutationType"
        RELATIONAL_OPERATOR = "RelationalOperator"
        SUBSTANCE_USE = "SubstanceUse"
        SUBSTANCE_USE_AMOUNT = "SubstanceUseAmount"
        SYMPTOM_OR_SIGN = "SymptomOrSign"
        TIME = "Time"
        TREATMENT_NAME = "TreatmentName"
        VARIANT = "Variant"


    class azure.ai.textanalytics.models.HealthcareEntityLink(_Model):
        data_source: str
        id: str

        @overload
        def __init__(
                self, 
                *, 
                data_source: str, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareLROResult(AnalyzeTextLROResult, discriminator='HealthcareLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.HEALTHCARE_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: HealthcareResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: HealthcareResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareLROTask(AnalyzeTextOperationAction, discriminator='Healthcare'):
        kind: Literal[AnalyzeTextOperationActionKind.HEALTHCARE]
        name: str
        parameters: Optional[HealthcareTaskParameters]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[HealthcareTaskParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareRelation(_Model):
        confidence_score: Optional[float]
        entities: list[HealthcareRelationEntity]
        relation_type: Union[str, RelationType]

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: Optional[float] = ..., 
                entities: list[HealthcareRelationEntity], 
                relation_type: Union[str, RelationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareRelationEntity(_Model):
        ref: str
        role: str

        @overload
        def __init__(
                self, 
                *, 
                ref: str, 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareResult(_Model):
        documents: list[HealthcareActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[HealthcareActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.HealthcareTaskParameters(_Model):
        document_type: Optional[Union[str, HealthcareDocumentType]]
        fhir_version: Optional[Union[str, FhirVersion]]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                document_type: Optional[Union[str, HealthcareDocumentType]] = ..., 
                fhir_version: Optional[Union[str, FhirVersion]] = ..., 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.InformationMetadata(BaseMetadata, discriminator='InformationMetadata'):
        metadata_kind: Literal[MetadataKind.INFORMATION_METADATA]
        unit: Union[str, InformationUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, InformationUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.InformationUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIT = "Bit"
        BYTE = "Byte"
        GIGABIT = "Gigabit"
        GIGABYTE = "Gigabyte"
        KILOBIT = "Kilobit"
        KILOBYTE = "Kilobyte"
        MEGABIT = "Megabit"
        MEGABYTE = "Megabyte"
        PETABIT = "Petabit"
        PETABYTE = "Petabyte"
        TERABIT = "Terabit"
        TERABYTE = "Terabyte"
        UNSPECIFIED = "Unspecified"


    class azure.ai.textanalytics.models.InnerErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_COGNITIVE_SEARCH_NOT_FOUND = "AzureCognitiveSearchNotFound"
        AZURE_COGNITIVE_SEARCH_THROTTLING = "AzureCognitiveSearchThrottling"
        EMPTY_REQUEST = "EmptyRequest"
        EXTRACTION_FAILURE = "ExtractionFailure"
        INVALID_COUNTRY_HINT = "InvalidCountryHint"
        INVALID_DOCUMENT = "InvalidDocument"
        INVALID_DOCUMENT_BATCH = "InvalidDocumentBatch"
        INVALID_PARAMETER_VALUE = "InvalidParameterValue"
        INVALID_REQUEST = "InvalidRequest"
        INVALID_REQUEST_BODY_FORMAT = "InvalidRequestBodyFormat"
        KNOWLEDGE_BASE_NOT_FOUND = "KnowledgeBaseNotFound"
        MISSING_INPUT_DOCUMENTS = "MissingInputDocuments"
        MODEL_VERSION_INCORRECT = "ModelVersionIncorrect"
        UNSUPPORTED_LANGUAGE_CODE = "UnsupportedLanguageCode"


    class azure.ai.textanalytics.models.InnerErrorModel(_Model):
        code: Union[str, InnerErrorCode]
        details: Optional[dict[str, str]]
        innererror: Optional[InnerErrorModel]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, InnerErrorCode], 
                details: Optional[dict[str, str]] = ..., 
                innererror: Optional[InnerErrorModel] = ..., 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.KeyPhraseActionContent(_Model):
        logging_opt_out: Optional[bool]
        model_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.KeyPhraseExtractionOperationResult(AnalyzeTextLROResult, discriminator='KeyPhraseExtractionLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.KEY_PHRASE_EXTRACTION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: KeyPhraseResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: KeyPhraseResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.KeyPhraseLROTask(AnalyzeTextOperationAction, discriminator='KeyPhraseExtraction'):
        kind: Literal[AnalyzeTextOperationActionKind.KEY_PHRASE_EXTRACTION]
        name: str
        parameters: Optional[KeyPhraseActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[KeyPhraseActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.KeyPhraseResult(_Model):
        documents: list[KeyPhrasesActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[KeyPhrasesActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.KeyPhrasesActionResult(_Model):
        detected_language: Optional[DetectedLanguage]
        id: str
        key_phrases: list[str]
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                id: str, 
                key_phrases: list[str], 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LanguageDetectionActionContent(_Model):
        logging_opt_out: Optional[bool]
        model_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LanguageDetectionDocumentResult(_Model):
        detected_language: DetectedLanguage
        id: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: DetectedLanguage, 
                id: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LanguageDetectionResult(_Model):
        documents: list[LanguageDetectionDocumentResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[LanguageDetectionDocumentResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LanguageDetectionTextInput(_Model):
        language_inputs: Optional[list[LanguageInput]]

        @overload
        def __init__(
                self, 
                *, 
                language_inputs: Optional[list[LanguageInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LanguageInput(_Model):
        country_hint: Optional[str]
        id: str
        text: str

        @overload
        def __init__(
                self, 
                *, 
                country_hint: Optional[str] = ..., 
                id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LengthMetadata(BaseMetadata, discriminator='LengthMetadata'):
        metadata_kind: Literal[MetadataKind.LENGTH_METADATA]
        unit: Union[str, LengthUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, LengthUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.LengthUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CENTIMETER = "Centimeter"
        DECAMETER = "Decameter"
        DECIMETER = "Decimeter"
        FOOT = "Foot"
        HECTOMETER = "Hectometer"
        INCH = "Inch"
        KILOMETER = "Kilometer"
        LIGHT_YEAR = "LightYear"
        METER = "Meter"
        MICROMETER = "Micrometer"
        MILE = "Mile"
        MILLIMETER = "Millimeter"
        NANOMETER = "Nanometer"
        PICOMETER = "Picometer"
        POINT = "Point"
        UNSPECIFIED = "Unspecified"
        YARD = "Yard"


    class azure.ai.textanalytics.models.LinkedEntity(_Model):
        bing_id: Optional[str]
        data_source: str
        id: Optional[str]
        language: str
        matches: list[EntityLinkingMatch]
        name: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                bing_id: Optional[str] = ..., 
                data_source: str, 
                id: Optional[str] = ..., 
                language: str, 
                matches: list[EntityLinkingMatch], 
                name: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.MatchLongestEntityPolicyType(EntityOverlapPolicy, discriminator='matchLongest'):
        policy_kind: Literal[PolicyKind.MATCH_LONGEST]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.MetadataKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_METADATA = "AddressMetadata"
        AGE_METADATA = "AgeMetadata"
        AREA_METADATA = "AreaMetadata"
        CURRENCY_METADATA = "CurrencyMetadata"
        DATE_METADATA = "DateMetadata"
        DATE_TIME_METADATA = "DateTimeMetadata"
        INFORMATION_METADATA = "InformationMetadata"
        LENGTH_METADATA = "LengthMetadata"
        NUMBER_METADATA = "NumberMetadata"
        NUMERIC_RANGE_METADATA = "NumericRangeMetadata"
        ORDINAL_METADATA = "OrdinalMetadata"
        SPEED_METADATA = "SpeedMetadata"
        TEMPERATURE_METADATA = "TemperatureMetadata"
        TEMPORAL_SET_METADATA = "TemporalSetMetadata"
        TEMPORAL_SPAN_METADATA = "TemporalSpanMetadata"
        TIME_METADATA = "TimeMetadata"
        VOLUME_METADATA = "VolumeMetadata"
        WEIGHT_METADATA = "WeightMetadata"


    class azure.ai.textanalytics.models.MultiLanguageInput(_Model):
        id: str
        language: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                language: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.MultiLanguageTextInput(_Model):
        multi_language_inputs: Optional[list[MultiLanguageInput]]

        @overload
        def __init__(
                self, 
                *, 
                multi_language_inputs: Optional[list[MultiLanguageInput]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.NamedEntity(_Model):
        category: str
        confidence_score: float
        length: int
        offset: int
        subcategory: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence_score: float, 
                length: int, 
                offset: int, 
                subcategory: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.NamedEntityWithMetadata(_Model):
        category: str
        confidence_score: float
        length: int
        metadata: Optional[BaseMetadata]
        offset: int
        subcategory: Optional[str]
        tags: Optional[list[EntityTag]]
        text: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence_score: float, 
                length: int, 
                metadata: Optional[BaseMetadata] = ..., 
                offset: int, 
                subcategory: Optional[str] = ..., 
                tags: Optional[list[EntityTag]] = ..., 
                text: str, 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.NoMaskPolicyType(BaseRedactionPolicy, discriminator='noMask'):
        entity_types: Union[list[str, PiiCategoriesExclude]]
        is_default: bool
        policy_kind: Literal[RedactionPolicyKind.NO_MASK]
        policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                entity_types: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                is_default: Optional[bool] = ..., 
                policy_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.NumberKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECIMAL = "Decimal"
        FRACTION = "Fraction"
        INTEGER = "Integer"
        PERCENT = "Percent"
        POWER = "Power"
        UNSPECIFIED = "Unspecified"


    class azure.ai.textanalytics.models.NumberMetadata(BaseMetadata, discriminator='NumberMetadata'):
        metadata_kind: Literal[MetadataKind.NUMBER_METADATA]
        number_kind: Union[str, NumberKind]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                number_kind: Union[str, NumberKind], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.NumericRangeMetadata(BaseMetadata, discriminator='NumericRangeMetadata'):
        maximum: float
        metadata_kind: Literal[MetadataKind.NUMERIC_RANGE_METADATA]
        minimum: float
        range_inclusivity: Optional[Union[str, RangeInclusivity]]
        range_kind: Union[str, RangeKind]

        @overload
        def __init__(
                self, 
                *, 
                maximum: float, 
                minimum: float, 
                range_inclusivity: Optional[Union[str, RangeInclusivity]] = ..., 
                range_kind: Union[str, RangeKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.OrdinalMetadata(BaseMetadata, discriminator='OrdinalMetadata'):
        metadata_kind: Literal[MetadataKind.ORDINAL_METADATA]
        offset: str
        relative_to: Union[str, RelativeTo]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                offset: str, 
                relative_to: Union[str, RelativeTo], 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiActionContent(_Model):
        confidence_score_threshold: Optional[ConfidenceScoreThreshold]
        disable_entity_validation: Optional[bool]
        domain: Optional[Union[str, PiiDomain]]
        entity_synonyms: Optional[list[EntitySynonyms]]
        exclude_pii_categories: Optional[list[Union[str, PiiCategoriesExclude]]]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        pii_categories: Optional[list[Union[str, PiiCategory]]]
        redaction_policies: Optional[list[BaseRedactionPolicy]]
        string_index_type: Optional[Union[str, StringIndexType]]
        value_exclusion_policy: Optional[ValueExclusionPolicy]

        @overload
        def __init__(
                self, 
                *, 
                confidence_score_threshold: Optional[ConfidenceScoreThreshold] = ..., 
                disable_entity_validation: Optional[bool] = ..., 
                domain: Optional[Union[str, PiiDomain]] = ..., 
                entity_synonyms: Optional[list[EntitySynonyms]] = ..., 
                exclude_pii_categories: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                pii_categories: Optional[list[Union[str, PiiCategory]]] = ..., 
                redaction_policies: Optional[list[BaseRedactionPolicy]] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ..., 
                value_exclusion_policy: Optional[ValueExclusionPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiCategoriesExclude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABA_ROUTING_NUMBER = "ABARoutingNumber"
        ADDRESS = "Address"
        AGE = "Age"
        AIRPORT = "Airport"
        AR_NATIONAL_IDENTITY_NUMBER = "ARNationalIdentityNumber"
        AT_IDENTITY_CARD = "ATIdentityCard"
        AT_TAX_IDENTIFICATION_NUMBER = "ATTaxIdentificationNumber"
        AT_VALUE_ADDED_TAX_NUMBER = "ATValueAddedTaxNumber"
        AU_BANK_ACCOUNT_NUMBER = "AUBankAccountNumber"
        AU_BUSINESS_NUMBER = "AUBusinessNumber"
        AU_COMPANY_NUMBER = "AUCompanyNumber"
        AU_DRIVERS_LICENSE_NUMBER = "AUDriversLicenseNumber"
        AU_MEDICAL_ACCOUNT_NUMBER = "AUMedicalAccountNumber"
        AU_PASSPORT_NUMBER = "AUPassportNumber"
        AU_TAX_FILE_NUMBER = "AUTaxFileNumber"
        AZURE_DOCUMENT_DBAUTH_KEY = "AzureDocumentDBAuthKey"
        AZURE_IAAS_DATABASE_CONNECTION_AND_SQL_STRING = "AzureIAASDatabaseConnectionAndSQLString"
        AZURE_IO_T_CONNECTION_STRING = "AzureIoTConnectionString"
        AZURE_PUBLISH_SETTING_PASSWORD = "AzurePublishSettingPassword"
        AZURE_REDIS_CACHE_STRING = "AzureRedisCacheString"
        AZURE_SAS = "AzureSAS"
        AZURE_SERVICE_BUS_STRING = "AzureServiceBusString"
        AZURE_STORAGE_ACCOUNT_GENERIC = "AzureStorageAccountGeneric"
        AZURE_STORAGE_ACCOUNT_KEY = "AzureStorageAccountKey"
        BANK_ACCOUNT_NUMBER = "BankAccountNumber"
        BE_NATIONAL_NUMBER = "BENationalNumber"
        BE_NATIONAL_NUMBER_V2 = "BENationalNumberV2"
        BE_VALUE_ADDED_TAX_NUMBER = "BEValueAddedTaxNumber"
        BG_UNIFORM_CIVIL_NUMBER = "BGUniformCivilNumber"
        BR_CPF_NUMBER = "BRCPFNumber"
        BR_LEGAL_ENTITY_NUMBER = "BRLegalEntityNumber"
        BR_NATIONAL_ID_RG = "BRNationalIDRG"
        CA_BANK_ACCOUNT_NUMBER = "CABankAccountNumber"
        CA_DRIVERS_LICENSE_NUMBER = "CADriversLicenseNumber"
        CA_HEALTH_SERVICE_NUMBER = "CAHealthServiceNumber"
        CA_PASSPORT_NUMBER = "CAPassportNumber"
        CA_PERSONAL_HEALTH_IDENTIFICATION = "CAPersonalHealthIdentification"
        CA_SOCIAL_IDENTIFICATION_NUMBER = "CASocialIdentificationNumber"
        CA_SOCIAL_INSURANCE_NUMBER = "CASocialInsuranceNumber"
        CH_SOCIAL_SECURITY_NUMBER = "CHSocialSecurityNumber"
        CITY = "City"
        CL_IDENTITY_CARD_NUMBER = "CLIdentityCardNumber"
        CN_RESIDENT_IDENTITY_CARD_NUMBER = "CNResidentIdentityCardNumber"
        CREDIT_CARD_NUMBER = "CreditCardNumber"
        CVV = "CVV"
        CY_IDENTITY_CARD = "CYIdentityCard"
        CY_TAX_IDENTIFICATION_NUMBER = "CYTaxIdentificationNumber"
        CZ_PERSONAL_IDENTITY_NUMBER = "CZPersonalIdentityNumber"
        CZ_PERSONAL_IDENTITY_V2 = "CZPersonalIdentityV2"
        DATE = "Date"
        DATE_OF_BIRTH = "DateOfBirth"
        DE_DRIVERS_LICENSE_NUMBER = "DEDriversLicenseNumber"
        DE_IDENTITY_CARD_NUMBER = "DEIdentityCardNumber"
        DE_PASSPORT_NUMBER = "DEPassportNumber"
        DE_TAX_IDENTIFICATION_NUMBER = "DETaxIdentificationNumber"
        DE_VALUE_ADDED_NUMBER = "DEValueAddedNumber"
        DK_PERSONAL_IDENTIFICATION_NUMBER = "DKPersonalIdentificationNumber"
        DK_PERSONAL_IDENTIFICATION_V2 = "DKPersonalIdentificationV2"
        DRIVERS_LICENSE_NUMBER = "DriversLicenseNumber"
        DRUG_ENFORCEMENT_AGENCY_NUMBER = "DrugEnforcementAgencyNumber"
        EE_PERSONAL_IDENTIFICATION_CODE = "EEPersonalIdentificationCode"
        EMAIL = "Email"
        ES_DNI = "ESDNI"
        ES_SOCIAL_SECURITY_NUMBER = "ESSocialSecurityNumber"
        ES_TAX_IDENTIFICATION_NUMBER = "ESTaxIdentificationNumber"
        EU_DEBIT_CARD_NUMBER = "EUDebitCardNumber"
        EU_DRIVERS_LICENSE_NUMBER = "EUDriversLicenseNumber"
        EU_GPS_COORDINATES = "EUGPSCoordinates"
        EU_NATIONAL_IDENTIFICATION_NUMBER = "EUNationalIdentificationNumber"
        EU_PASSPORT_NUMBER = "EUPassportNumber"
        EU_SOCIAL_SECURITY_NUMBER = "EUSocialSecurityNumber"
        EU_TAX_IDENTIFICATION_NUMBER = "EUTaxIdentificationNumber"
        EXPIRATION_DATE = "ExpirationDate"
        FI_EUROPEAN_HEALTH_NUMBER = "FIEuropeanHealthNumber"
        FI_NATIONAL_ID = "FINationalID"
        FI_NATIONAL_ID_V2 = "FINationalIDV2"
        FI_PASSPORT_NUMBER = "FIPassportNumber"
        FR_DRIVERS_LICENSE_NUMBER = "FRDriversLicenseNumber"
        FR_HEALTH_INSURANCE_NUMBER = "FRHealthInsuranceNumber"
        FR_NATIONAL_ID = "FRNationalID"
        FR_PASSPORT_NUMBER = "FRPassportNumber"
        FR_SOCIAL_SECURITY_NUMBER = "FRSocialSecurityNumber"
        FR_TAX_IDENTIFICATION_NUMBER = "FRTaxIdentificationNumber"
        FR_VALUE_ADDED_TAX_NUMBER = "FRValueAddedTaxNumber"
        GOVERNMENT_ISSUED_ID = "GovernmentIssuedId"
        GPE = "GPE"
        GR_NATIONAL_ID_CARD = "GRNationalIDCard"
        GR_NATIONAL_ID_V2 = "GRNationalIDV2"
        GR_TAX_IDENTIFICATION_NUMBER = "GRTaxIdentificationNumber"
        HK_IDENTITY_CARD_NUMBER = "HKIdentityCardNumber"
        HR_IDENTITY_CARD_NUMBER = "HRIdentityCardNumber"
        HR_NATIONAL_ID_NUMBER = "HRNationalIDNumber"
        HR_PERSONAL_IDENTIFICATION_NUMBER = "HRPersonalIdentificationNumber"
        HR_PERSONAL_IDENTIFICATION_OIB_NUMBER_V2 = "HRPersonalIdentificationOIBNumberV2"
        HU_PERSONAL_IDENTIFICATION_NUMBER = "HUPersonalIdentificationNumber"
        HU_TAX_IDENTIFICATION_NUMBER = "HUTaxIdentificationNumber"
        HU_VALUE_ADDED_NUMBER = "HUValueAddedNumber"
        ID_IDENTITY_CARD_NUMBER = "IDIdentityCardNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER = "IEPersonalPublicServiceNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER_V2 = "IEPersonalPublicServiceNumberV2"
        IL_BANK_ACCOUNT_NUMBER = "ILBankAccountNumber"
        IL_NATIONAL_ID = "ILNationalID"
        INTERNATIONAL_BANKING_ACCOUNT_NUMBER = "InternationalBankingAccountNumber"
        IN_PERMANENT_ACCOUNT = "INPermanentAccount"
        IN_UNIQUE_IDENTIFICATION_NUMBER = "INUniqueIdentificationNumber"
        IP_ADDRESS = "IPAddress"
        IT_DRIVERS_LICENSE_NUMBER = "ITDriversLicenseNumber"
        IT_FISCAL_CODE = "ITFiscalCode"
        IT_VALUE_ADDED_TAX_NUMBER = "ITValueAddedTaxNumber"
        JP_BANK_ACCOUNT_NUMBER = "JPBankAccountNumber"
        JP_DRIVERS_LICENSE_NUMBER = "JPDriversLicenseNumber"
        JP_MY_NUMBER_CORPORATE = "JPMyNumberCorporate"
        JP_MY_NUMBER_PERSONAL = "JPMyNumberPersonal"
        JP_PASSPORT_NUMBER = "JPPassportNumber"
        JP_RESIDENCE_CARD_NUMBER = "JPResidenceCardNumber"
        JP_RESIDENT_REGISTRATION_NUMBER = "JPResidentRegistrationNumber"
        JP_SOCIAL_INSURANCE_NUMBER = "JPSocialInsuranceNumber"
        KR_DRIVERS_LICENSE_NUMBER = "KRDriversLicenseNumber"
        KR_PASSPORT_NUMBER = "KRPassportNumber"
        KR_RESIDENT_REGISTRATION_NUMBER = "KRResidentRegistrationNumber"
        KR_SOCIAL_SECURITY_NUMBER = "KRSocialSecurityNumber"
        LICENSE_PLATE = "LicensePlate"
        LOCATION = "Location"
        LT_PERSONAL_CODE = "LTPersonalCode"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NATURAL = "LUNationalIdentificationNumberNatural"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NON_NATURAL = "LUNationalIdentificationNumberNonNatural"
        LV_PERSONAL_CODE = "LVPersonalCode"
        MEDICARE_BENEFICIARY_ID = "USMedicareBeneficiaryId"
        MT_IDENTITY_CARD_NUMBER = "MTIdentityCardNumber"
        MT_TAX_ID_NUMBER = "MTTaxIDNumber"
        MY_IDENTITY_CARD_NUMBER = "MYIdentityCardNumber"
        NATIONAL_ID = "NationalId"
        NEIGHBORHOOD = "Neighborhood"
        NL_CITIZENS_SERVICE_NUMBER = "NLCitizensServiceNumber"
        NL_CITIZENS_SERVICE_NUMBER_V2 = "NLCitizensServiceNumberV2"
        NL_TAX_IDENTIFICATION_NUMBER = "NLTaxIdentificationNumber"
        NL_VALUE_ADDED_TAX_NUMBER = "NLValueAddedTaxNumber"
        NO_IDENTITY_NUMBER = "NOIdentityNumber"
        NZ_BANK_ACCOUNT_NUMBER = "NZBankAccountNumber"
        NZ_DRIVERS_LICENSE_NUMBER = "NZDriversLicenseNumber"
        NZ_INLAND_REVENUE_NUMBER = "NZInlandRevenueNumber"
        NZ_MINISTRY_OF_HEALTH_NUMBER = "NZMinistryOfHealthNumber"
        NZ_SOCIAL_WELFARE_NUMBER = "NZSocialWelfareNumber"
        ORGANIZATION = "Organization"
        PASSPORT_NUMBER = "PassportNumber"
        PASSWORD = "Password"
        PERSON = "Person"
        PHONE_NUMBER = "PhoneNumber"
        PH_UNIFIED_MULTI_PURPOSE_ID_NUMBER = "PHUnifiedMultiPurposeIDNumber"
        PIN = "PIN"
        PL_IDENTITY_CARD = "PLIdentityCard"
        PL_NATIONAL_ID = "PLNationalID"
        PL_NATIONAL_ID_V2 = "PLNationalIDV2"
        PL_PASSPORT_NUMBER = "PLPassportNumber"
        PL_REGON_NUMBER = "PLREGONNumber"
        PL_TAX_IDENTIFICATION_NUMBER = "PLTaxIdentificationNumber"
        PT_CITIZEN_CARD_NUMBER = "PTCitizenCardNumber"
        PT_CITIZEN_CARD_NUMBER_V2 = "PTCitizenCardNumberV2"
        PT_TAX_IDENTIFICATION_NUMBER = "PTTaxIdentificationNumber"
        RO_PERSONAL_NUMERICAL_CODE = "ROPersonalNumericalCode"
        RU_PASSPORT_NUMBER_DOMESTIC = "RUPassportNumberDomestic"
        RU_PASSPORT_NUMBER_INTERNATIONAL = "RUPassportNumberInternational"
        SA_NATIONAL_ID = "SANationalID"
        SE_NATIONAL_ID = "SENationalID"
        SE_NATIONAL_ID_V2 = "SENationalIDV2"
        SE_PASSPORT_NUMBER = "SEPassportNumber"
        SE_TAX_IDENTIFICATION_NUMBER = "SETaxIdentificationNumber"
        SG_NATIONAL_REGISTRATION_IDENTITY_CARD_NUMBER = "SGNationalRegistrationIdentityCardNumber"
        SI_TAX_IDENTIFICATION_NUMBER = "SITaxIdentificationNumber"
        SI_UNIQUE_MASTER_CITIZEN_NUMBER = "SIUniqueMasterCitizenNumber"
        SK_PERSONAL_NUMBER = "SKPersonalNumber"
        SORT_CODE = "SortCode"
        SQL_SERVER_CONNECTION_STRING = "SQLServerConnectionString"
        STATE = "State"
        SWIFT_CODE = "SWIFTCode"
        TH_POPULATION_IDENTIFICATION_CODE = "THPopulationIdentificationCode"
        TR_NATIONAL_IDENTIFICATION_NUMBER = "TRNationalIdentificationNumber"
        TW_NATIONAL_ID = "TWNationalID"
        TW_PASSPORT_NUMBER = "TWPassportNumber"
        TW_RESIDENT_CERTIFICATE = "TWResidentCertificate"
        UA_PASSPORT_NUMBER_DOMESTIC = "UAPassportNumberDomestic"
        UA_PASSPORT_NUMBER_INTERNATIONAL = "UAPassportNumberInternational"
        UK_DRIVERS_LICENSE_NUMBER = "UKDriversLicenseNumber"
        UK_ELECTORAL_ROLL_NUMBER = "UKElectoralRollNumber"
        UK_NATIONAL_HEALTH_NUMBER = "UKNationalHealthNumber"
        UK_NATIONAL_INSURANCE_NUMBER = "UKNationalInsuranceNumber"
        UK_UNIQUE_TAXPAYER_NUMBER = "UKUniqueTaxpayerNumber"
        URL = "URL"
        US_BANK_ACCOUNT_NUMBER = "USBankAccountNumber"
        US_DRIVERS_LICENSE_NUMBER = "USDriversLicenseNumber"
        US_INDIVIDUAL_TAXPAYER_IDENTIFICATION = "USIndividualTaxpayerIdentification"
        US_SOCIAL_SECURITY_NUMBER = "USSocialSecurityNumber"
        US_UK_PASSPORT_NUMBER = "USUKPassportNumber"
        VEHICLE_IDENTIFICATION_NUMBER = "VehicleIdentificationNumber"
        VIN = "VIN"
        ZA_IDENTIFICATION_NUMBER = "ZAIdentificationNumber"
        ZIP_CODE = "ZipCode"


    class azure.ai.textanalytics.models.PiiCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABA_ROUTING_NUMBER = "ABARoutingNumber"
        ADDRESS = "Address"
        AGE = "Age"
        AIRPORT = "Airport"
        ALL = "All"
        AR_NATIONAL_IDENTITY_NUMBER = "ARNationalIdentityNumber"
        AT_IDENTITY_CARD = "ATIdentityCard"
        AT_TAX_IDENTIFICATION_NUMBER = "ATTaxIdentificationNumber"
        AT_VALUE_ADDED_TAX_NUMBER = "ATValueAddedTaxNumber"
        AU_BANK_ACCOUNT_NUMBER = "AUBankAccountNumber"
        AU_BUSINESS_NUMBER = "AUBusinessNumber"
        AU_COMPANY_NUMBER = "AUCompanyNumber"
        AU_DRIVERS_LICENSE_NUMBER = "AUDriversLicenseNumber"
        AU_MEDICAL_ACCOUNT_NUMBER = "AUMedicalAccountNumber"
        AU_PASSPORT_NUMBER = "AUPassportNumber"
        AU_TAX_FILE_NUMBER = "AUTaxFileNumber"
        AZURE_DOCUMENT_DBAUTH_KEY = "AzureDocumentDBAuthKey"
        AZURE_IAAS_DATABASE_CONNECTION_AND_SQL_STRING = "AzureIAASDatabaseConnectionAndSQLString"
        AZURE_IO_T_CONNECTION_STRING = "AzureIoTConnectionString"
        AZURE_PUBLISH_SETTING_PASSWORD = "AzurePublishSettingPassword"
        AZURE_REDIS_CACHE_STRING = "AzureRedisCacheString"
        AZURE_SAS = "AzureSAS"
        AZURE_SERVICE_BUS_STRING = "AzureServiceBusString"
        AZURE_STORAGE_ACCOUNT_GENERIC = "AzureStorageAccountGeneric"
        AZURE_STORAGE_ACCOUNT_KEY = "AzureStorageAccountKey"
        BANK_ACCOUNT_NUMBER = "BankAccountNumber"
        BE_NATIONAL_NUMBER = "BENationalNumber"
        BE_NATIONAL_NUMBER_V2 = "BENationalNumberV2"
        BE_VALUE_ADDED_TAX_NUMBER = "BEValueAddedTaxNumber"
        BG_UNIFORM_CIVIL_NUMBER = "BGUniformCivilNumber"
        BR_CPF_NUMBER = "BRCPFNumber"
        BR_LEGAL_ENTITY_NUMBER = "BRLegalEntityNumber"
        BR_NATIONAL_ID_RG = "BRNationalIDRG"
        CA_BANK_ACCOUNT_NUMBER = "CABankAccountNumber"
        CA_DRIVERS_LICENSE_NUMBER = "CADriversLicenseNumber"
        CA_HEALTH_SERVICE_NUMBER = "CAHealthServiceNumber"
        CA_PASSPORT_NUMBER = "CAPassportNumber"
        CA_PERSONAL_HEALTH_IDENTIFICATION = "CAPersonalHealthIdentification"
        CA_SOCIAL_IDENTIFICATION_NUMBER = "CASocialIdentificationNumber"
        CA_SOCIAL_INSURANCE_NUMBER = "CASocialInsuranceNumber"
        CH_SOCIAL_SECURITY_NUMBER = "CHSocialSecurityNumber"
        CITY = "City"
        CL_IDENTITY_CARD_NUMBER = "CLIdentityCardNumber"
        CN_RESIDENT_IDENTITY_CARD_NUMBER = "CNResidentIdentityCardNumber"
        CREDIT_CARD_NUMBER = "CreditCardNumber"
        CVV = "CVV"
        CY_IDENTITY_CARD = "CYIdentityCard"
        CY_TAX_IDENTIFICATION_NUMBER = "CYTaxIdentificationNumber"
        CZ_PERSONAL_IDENTITY_NUMBER = "CZPersonalIdentityNumber"
        CZ_PERSONAL_IDENTITY_V2 = "CZPersonalIdentityV2"
        DATE = "Date"
        DATE_OF_BIRTH = "DateOfBirth"
        DEFAULT = "Default"
        DE_DRIVERS_LICENSE_NUMBER = "DEDriversLicenseNumber"
        DE_IDENTITY_CARD_NUMBER = "DEIdentityCardNumber"
        DE_PASSPORT_NUMBER = "DEPassportNumber"
        DE_TAX_IDENTIFICATION_NUMBER = "DETaxIdentificationNumber"
        DE_VALUE_ADDED_NUMBER = "DEValueAddedNumber"
        DK_PERSONAL_IDENTIFICATION_NUMBER = "DKPersonalIdentificationNumber"
        DK_PERSONAL_IDENTIFICATION_V2 = "DKPersonalIdentificationV2"
        DRIVERS_LICENSE_NUMBER = "DriversLicenseNumber"
        DRUG_ENFORCEMENT_AGENCY_NUMBER = "DrugEnforcementAgencyNumber"
        EE_PERSONAL_IDENTIFICATION_CODE = "EEPersonalIdentificationCode"
        EMAIL = "Email"
        ES_DNI = "ESDNI"
        ES_SOCIAL_SECURITY_NUMBER = "ESSocialSecurityNumber"
        ES_TAX_IDENTIFICATION_NUMBER = "ESTaxIdentificationNumber"
        EU_DEBIT_CARD_NUMBER = "EUDebitCardNumber"
        EU_DRIVERS_LICENSE_NUMBER = "EUDriversLicenseNumber"
        EU_GPS_COORDINATES = "EUGPSCoordinates"
        EU_NATIONAL_IDENTIFICATION_NUMBER = "EUNationalIdentificationNumber"
        EU_PASSPORT_NUMBER = "EUPassportNumber"
        EU_SOCIAL_SECURITY_NUMBER = "EUSocialSecurityNumber"
        EU_TAX_IDENTIFICATION_NUMBER = "EUTaxIdentificationNumber"
        EXPIRATION_DATE = "ExpirationDate"
        FI_EUROPEAN_HEALTH_NUMBER = "FIEuropeanHealthNumber"
        FI_NATIONAL_ID = "FINationalID"
        FI_NATIONAL_ID_V2 = "FINationalIDV2"
        FI_PASSPORT_NUMBER = "FIPassportNumber"
        FR_DRIVERS_LICENSE_NUMBER = "FRDriversLicenseNumber"
        FR_HEALTH_INSURANCE_NUMBER = "FRHealthInsuranceNumber"
        FR_NATIONAL_ID = "FRNationalID"
        FR_PASSPORT_NUMBER = "FRPassportNumber"
        FR_SOCIAL_SECURITY_NUMBER = "FRSocialSecurityNumber"
        FR_TAX_IDENTIFICATION_NUMBER = "FRTaxIdentificationNumber"
        FR_VALUE_ADDED_TAX_NUMBER = "FRValueAddedTaxNumber"
        GOVERNMENT_ISSUED_ID = "GovernmentIssuedId"
        GPE = "GPE"
        GR_NATIONAL_ID_CARD = "GRNationalIDCard"
        GR_NATIONAL_ID_V2 = "GRNationalIDV2"
        GR_TAX_IDENTIFICATION_NUMBER = "GRTaxIdentificationNumber"
        HK_IDENTITY_CARD_NUMBER = "HKIdentityCardNumber"
        HR_IDENTITY_CARD_NUMBER = "HRIdentityCardNumber"
        HR_NATIONAL_ID_NUMBER = "HRNationalIDNumber"
        HR_PERSONAL_IDENTIFICATION_NUMBER = "HRPersonalIdentificationNumber"
        HR_PERSONAL_IDENTIFICATION_OIB_NUMBER_V2 = "HRPersonalIdentificationOIBNumberV2"
        HU_PERSONAL_IDENTIFICATION_NUMBER = "HUPersonalIdentificationNumber"
        HU_TAX_IDENTIFICATION_NUMBER = "HUTaxIdentificationNumber"
        HU_VALUE_ADDED_NUMBER = "HUValueAddedNumber"
        ID_IDENTITY_CARD_NUMBER = "IDIdentityCardNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER = "IEPersonalPublicServiceNumber"
        IE_PERSONAL_PUBLIC_SERVICE_NUMBER_V2 = "IEPersonalPublicServiceNumberV2"
        IL_BANK_ACCOUNT_NUMBER = "ILBankAccountNumber"
        IL_NATIONAL_ID = "ILNationalID"
        INTERNATIONAL_BANKING_ACCOUNT_NUMBER = "InternationalBankingAccountNumber"
        IN_PERMANENT_ACCOUNT = "INPermanentAccount"
        IN_UNIQUE_IDENTIFICATION_NUMBER = "INUniqueIdentificationNumber"
        IP_ADDRESS = "IPAddress"
        IT_DRIVERS_LICENSE_NUMBER = "ITDriversLicenseNumber"
        IT_FISCAL_CODE = "ITFiscalCode"
        IT_VALUE_ADDED_TAX_NUMBER = "ITValueAddedTaxNumber"
        JP_BANK_ACCOUNT_NUMBER = "JPBankAccountNumber"
        JP_DRIVERS_LICENSE_NUMBER = "JPDriversLicenseNumber"
        JP_MY_NUMBER_CORPORATE = "JPMyNumberCorporate"
        JP_MY_NUMBER_PERSONAL = "JPMyNumberPersonal"
        JP_PASSPORT_NUMBER = "JPPassportNumber"
        JP_RESIDENCE_CARD_NUMBER = "JPResidenceCardNumber"
        JP_RESIDENT_REGISTRATION_NUMBER = "JPResidentRegistrationNumber"
        JP_SOCIAL_INSURANCE_NUMBER = "JPSocialInsuranceNumber"
        KR_DRIVERS_LICENSE_NUMBER = "KRDriversLicenseNumber"
        KR_PASSPORT_NUMBER = "KRPassportNumber"
        KR_RESIDENT_REGISTRATION_NUMBER = "KRResidentRegistrationNumber"
        KR_SOCIAL_SECURITY_NUMBER = "KRSocialSecurityNumber"
        LICENSE_PLATE = "LicensePlate"
        LOCATION = "Location"
        LT_PERSONAL_CODE = "LTPersonalCode"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NATURAL = "LUNationalIdentificationNumberNatural"
        LU_NATIONAL_IDENTIFICATION_NUMBER_NON_NATURAL = "LUNationalIdentificationNumberNonNatural"
        LV_PERSONAL_CODE = "LVPersonalCode"
        MEDICARE_BENEFICIARY_ID = "USMedicareBeneficiaryId"
        MT_IDENTITY_CARD_NUMBER = "MTIdentityCardNumber"
        MT_TAX_ID_NUMBER = "MTTaxIDNumber"
        MY_IDENTITY_CARD_NUMBER = "MYIdentityCardNumber"
        NATIONAL_ID = "NationalId"
        NEIGHBORHOOD = "Neighborhood"
        NL_CITIZENS_SERVICE_NUMBER = "NLCitizensServiceNumber"
        NL_CITIZENS_SERVICE_NUMBER_V2 = "NLCitizensServiceNumberV2"
        NL_TAX_IDENTIFICATION_NUMBER = "NLTaxIdentificationNumber"
        NL_VALUE_ADDED_TAX_NUMBER = "NLValueAddedTaxNumber"
        NO_IDENTITY_NUMBER = "NOIdentityNumber"
        NZ_BANK_ACCOUNT_NUMBER = "NZBankAccountNumber"
        NZ_DRIVERS_LICENSE_NUMBER = "NZDriversLicenseNumber"
        NZ_INLAND_REVENUE_NUMBER = "NZInlandRevenueNumber"
        NZ_MINISTRY_OF_HEALTH_NUMBER = "NZMinistryOfHealthNumber"
        NZ_SOCIAL_WELFARE_NUMBER = "NZSocialWelfareNumber"
        ORGANIZATION = "Organization"
        PASSPORT_NUMBER = "PassportNumber"
        PASSWORD = "Password"
        PERSON = "Person"
        PHONE_NUMBER = "PhoneNumber"
        PH_UNIFIED_MULTI_PURPOSE_ID_NUMBER = "PHUnifiedMultiPurposeIDNumber"
        PIN = "PIN"
        PL_IDENTITY_CARD = "PLIdentityCard"
        PL_NATIONAL_ID = "PLNationalID"
        PL_NATIONAL_ID_V2 = "PLNationalIDV2"
        PL_PASSPORT_NUMBER = "PLPassportNumber"
        PL_REGON_NUMBER = "PLREGONNumber"
        PL_TAX_IDENTIFICATION_NUMBER = "PLTaxIdentificationNumber"
        PT_CITIZEN_CARD_NUMBER = "PTCitizenCardNumber"
        PT_CITIZEN_CARD_NUMBER_V2 = "PTCitizenCardNumberV2"
        PT_TAX_IDENTIFICATION_NUMBER = "PTTaxIdentificationNumber"
        RO_PERSONAL_NUMERICAL_CODE = "ROPersonalNumericalCode"
        RU_PASSPORT_NUMBER_DOMESTIC = "RUPassportNumberDomestic"
        RU_PASSPORT_NUMBER_INTERNATIONAL = "RUPassportNumberInternational"
        SA_NATIONAL_ID = "SANationalID"
        SE_NATIONAL_ID = "SENationalID"
        SE_NATIONAL_ID_V2 = "SENationalIDV2"
        SE_PASSPORT_NUMBER = "SEPassportNumber"
        SE_TAX_IDENTIFICATION_NUMBER = "SETaxIdentificationNumber"
        SG_NATIONAL_REGISTRATION_IDENTITY_CARD_NUMBER = "SGNationalRegistrationIdentityCardNumber"
        SI_TAX_IDENTIFICATION_NUMBER = "SITaxIdentificationNumber"
        SI_UNIQUE_MASTER_CITIZEN_NUMBER = "SIUniqueMasterCitizenNumber"
        SK_PERSONAL_NUMBER = "SKPersonalNumber"
        SORT_CODE = "SortCode"
        SQL_SERVER_CONNECTION_STRING = "SQLServerConnectionString"
        STATE = "State"
        SWIFT_CODE = "SWIFTCode"
        TH_POPULATION_IDENTIFICATION_CODE = "THPopulationIdentificationCode"
        TR_NATIONAL_IDENTIFICATION_NUMBER = "TRNationalIdentificationNumber"
        TW_NATIONAL_ID = "TWNationalID"
        TW_PASSPORT_NUMBER = "TWPassportNumber"
        TW_RESIDENT_CERTIFICATE = "TWResidentCertificate"
        UA_PASSPORT_NUMBER_DOMESTIC = "UAPassportNumberDomestic"
        UA_PASSPORT_NUMBER_INTERNATIONAL = "UAPassportNumberInternational"
        UK_DRIVERS_LICENSE_NUMBER = "UKDriversLicenseNumber"
        UK_ELECTORAL_ROLL_NUMBER = "UKElectoralRollNumber"
        UK_NATIONAL_HEALTH_NUMBER = "UKNationalHealthNumber"
        UK_NATIONAL_INSURANCE_NUMBER = "UKNationalInsuranceNumber"
        UK_UNIQUE_TAXPAYER_NUMBER = "UKUniqueTaxpayerNumber"
        URL = "URL"
        US_BANK_ACCOUNT_NUMBER = "USBankAccountNumber"
        US_DRIVERS_LICENSE_NUMBER = "USDriversLicenseNumber"
        US_INDIVIDUAL_TAXPAYER_IDENTIFICATION = "USIndividualTaxpayerIdentification"
        US_SOCIAL_SECURITY_NUMBER = "USSocialSecurityNumber"
        US_UK_PASSPORT_NUMBER = "USUKPassportNumber"
        VEHICLE_IDENTIFICATION_NUMBER = "VehicleIdentificationNumber"
        VIN = "VIN"
        ZA_IDENTIFICATION_NUMBER = "ZAIdentificationNumber"
        ZIP_CODE = "ZipCode"


    class azure.ai.textanalytics.models.PiiDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        PHI = "phi"


    class azure.ai.textanalytics.models.PiiEntity(_Model):
        category: str
        confidence_score: float
        length: int
        mask: Optional[str]
        mask_length: Optional[int]
        mask_offset: Optional[int]
        offset: int
        subcategory: Optional[str]
        tags: Optional[list[EntityTag]]
        text: str
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence_score: float, 
                length: int, 
                mask: Optional[str] = ..., 
                mask_length: Optional[int] = ..., 
                mask_offset: Optional[int] = ..., 
                offset: int, 
                subcategory: Optional[str] = ..., 
                tags: Optional[list[EntityTag]] = ..., 
                text: str, 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiEntityRecognitionOperationResult(AnalyzeTextLROResult, discriminator='PiiEntityRecognitionLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.PII_ENTITY_RECOGNITION_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: PiiResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: PiiResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiLROTask(AnalyzeTextOperationAction, discriminator='PiiEntityRecognition'):
        kind: Literal[AnalyzeTextOperationActionKind.PII_ENTITY_RECOGNITION]
        name: str
        parameters: Optional[PiiActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[PiiActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiResult(_Model):
        documents: list[PiiResultWithDetectedLanguage]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[PiiResultWithDetectedLanguage], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PiiResultWithDetectedLanguage(_Model):
        detected_language: Optional[DetectedLanguage]
        entities: list[PiiEntity]
        id: str
        redacted_text: str
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ..., 
                entities: list[PiiEntity], 
                id: str, 
                redacted_text: str, 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.PolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_OVERLAP = "allowOverlap"
        MATCH_LONGEST = "matchLongest"


    class azure.ai.textanalytics.models.RangeInclusivity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEFT_INCLUSIVE = "LeftInclusive"
        LEFT_RIGHT_INCLUSIVE = "LeftRightInclusive"
        NONE_INCLUSIVE = "NoneInclusive"
        RIGHT_INCLUSIVE = "RightInclusive"


    class azure.ai.textanalytics.models.RangeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGE = "Age"
        AREA = "Area"
        CURRENCY = "Currency"
        INFORMATION = "Information"
        LENGTH = "Length"
        NUMBER = "Number"
        SPEED = "Speed"
        TEMPERATURE = "Temperature"
        VOLUME = "Volume"
        WEIGHT = "Weight"


    class azure.ai.textanalytics.models.RedactionCharacter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMPERSAND = "&"
        ASTERISK = "*"
        AT_SIGN = "@"
        CARET = "^"
        DOLLAR = "$"
        EQUALS = "="
        EXCLAMATION_POINT = "!"
        MINUS = "-"
        NUMBER_SIGN = "#"
        PER_CENT = "%"
        PLUS = "+"
        QUESTION_MARK = "?"
        TILDE = "~"
        UNDERSCORE = "_"


    class azure.ai.textanalytics.models.RedactionPolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHARACTER_MASK = "characterMask"
        ENTITY_MASK = "entityMask"
        NO_MASK = "noMask"
        SYNTHETIC_REPLACEMENT = "syntheticReplacement"


    class azure.ai.textanalytics.models.RelationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABBREVIATION = "Abbreviation"
        BODY_SITE_OF_CONDITION = "BodySiteOfCondition"
        BODY_SITE_OF_TREATMENT = "BodySiteOfTreatment"
        COURSE_OF_CONDITION = "CourseOfCondition"
        COURSE_OF_EXAMINATION = "CourseOfExamination"
        COURSE_OF_MEDICATION = "CourseOfMedication"
        COURSE_OF_TREATMENT = "CourseOfTreatment"
        DIRECTION_OF_BODY_STRUCTURE = "DirectionOfBodyStructure"
        DIRECTION_OF_CONDITION = "DirectionOfCondition"
        DIRECTION_OF_EXAMINATION = "DirectionOfExamination"
        DIRECTION_OF_TREATMENT = "DirectionOfTreatment"
        DOSAGE_OF_MEDICATION = "DosageOfMedication"
        EXAMINATION_FINDS_CONDITION = "ExaminationFindsCondition"
        EXPRESSION_OF_GENE = "ExpressionOfGene"
        EXPRESSION_OF_VARIANT = "ExpressionOfVariant"
        FORM_OF_MEDICATION = "FormOfMedication"
        FREQUENCY_OF_CONDITION = "FrequencyOfCondition"
        FREQUENCY_OF_MEDICATION = "FrequencyOfMedication"
        FREQUENCY_OF_TREATMENT = "FrequencyOfTreatment"
        MUTATION_TYPE_OF_GENE = "MutationTypeOfGene"
        MUTATION_TYPE_OF_VARIANT = "MutationTypeOfVariant"
        QUALIFIER_OF_CONDITION = "QualifierOfCondition"
        RELATION_OF_EXAMINATION = "RelationOfExamination"
        ROUTE_OF_MEDICATION = "RouteOfMedication"
        SCALE_OF_CONDITION = "ScaleOfCondition"
        TIME_OF_CONDITION = "TimeOfCondition"
        TIME_OF_EVENT = "TimeOfEvent"
        TIME_OF_EXAMINATION = "TimeOfExamination"
        TIME_OF_MEDICATION = "TimeOfMedication"
        TIME_OF_TREATMENT = "TimeOfTreatment"
        UNIT_OF_CONDITION = "UnitOfCondition"
        UNIT_OF_EXAMINATION = "UnitOfExamination"
        VALUE_OF_CONDITION = "ValueOfCondition"
        VALUE_OF_EXAMINATION = "ValueOfExamination"
        VARIANT_OF_GENE = "VariantOfGene"


    class azure.ai.textanalytics.models.RelativeTo(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "Current"
        END = "End"
        START = "Start"


    class azure.ai.textanalytics.models.RequestStatistics(_Model):
        documents_count: int
        erroneous_documents_count: int
        transactions_count: int
        valid_documents_count: int

        @overload
        def __init__(
                self, 
                *, 
                documents_count: int, 
                erroneous_documents_count: int, 
                transactions_count: int, 
                valid_documents_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.ScriptCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARAB = "Arab"
        ARMN = "Armn"
        BENG = "Beng"
        CANS = "Cans"
        CYRL = "Cyrl"
        DEVA = "Deva"
        ETHI = "Ethi"
        GEOR = "Geor"
        GREK = "Grek"
        GUJR = "Gujr"
        GURU = "Guru"
        HANG = "Hang"
        HANI = "Hani"
        HANS = "Hans"
        HANT = "Hant"
        HEBR = "Hebr"
        JPAN = "Jpan"
        KHMR = "Khmr"
        KNDA = "Knda"
        LAOO = "Laoo"
        LATN = "Latn"
        MLYM = "Mlym"
        MONG = "Mong"
        MTEI = "Mtei"
        MYMR = "Mymr"
        OLCK = "Olck"
        ORYA = "Orya"
        SHRD = "Shrd"
        SINH = "Sinh"
        TAML = "Taml"
        TELU = "Telu"
        THAA = "Thaa"
        THAI = "Thai"
        TIBT = "Tibt"


    class azure.ai.textanalytics.models.ScriptKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARABIC = "Arabic"
        ARMENIAN = "Armenian"
        BANGLA = "Bangla"
        CYRILLIC = "Cyrillic"
        DEVANAGARI = "Devanagari"
        ETHIOPIC = "Ethiopic"
        GEORGIAN = "Georgian"
        GREEK = "Greek"
        GUJARATI = "Gujarati"
        GURMUKHI = "Gurmukhi"
        HANGUL = "Hangul"
        HAN_LITERAL = "HanLiteral"
        HAN_SIMPLIFIED = "HanSimplified"
        HAN_TRADITIONAL = "HanTraditional"
        HEBREW = "Hebrew"
        JAPANESE = "Japanese"
        KANNADA = "Kannada"
        KHMER = "Khmer"
        LAO = "Lao"
        LATIN = "Latin"
        MALAYALAM = "Malayalam"
        MEITEI = "Meitei"
        MONGOLIAN = "Mongolian"
        MYANMAR = "Myanmar"
        ODIA = "Odia"
        SANTALI = "Santali"
        SHARADA = "Sharada"
        SINHALA = "Sinhala"
        TAMIL = "Tamil"
        TELUGU = "Telugu"
        THAANA = "Thaana"
        THAI = "Thai"
        TIBETAN = "Tibetan"
        UNIFIED_CANADIAN_ABORIGINAL_SYLLABICS = "UnifiedCanadianAboriginalSyllabics"


    class azure.ai.textanalytics.models.SentenceAssessment(_Model):
        confidence_scores: TargetConfidenceScoreLabel
        is_negated: bool
        length: int
        offset: int
        sentiment: Union[str, TokenSentiment]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_scores: TargetConfidenceScoreLabel, 
                is_negated: bool, 
                length: int, 
                offset: int, 
                sentiment: Union[str, TokenSentiment], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentenceSentiment(_Model):
        assessments: Optional[list[SentenceAssessment]]
        confidence_scores: SentimentConfidenceScores
        length: int
        offset: int
        sentiment: Union[str, SentenceSentimentValue]
        targets: Optional[list[SentenceTarget]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                assessments: Optional[list[SentenceAssessment]] = ..., 
                confidence_scores: SentimentConfidenceScores, 
                length: int, 
                offset: int, 
                sentiment: Union[str, SentenceSentimentValue], 
                targets: Optional[list[SentenceTarget]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentenceSentimentValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NEGATIVE = "negative"
        NEUTRAL = "neutral"
        POSITIVE = "positive"


    class azure.ai.textanalytics.models.SentenceTarget(_Model):
        confidence_scores: TargetConfidenceScoreLabel
        length: int
        offset: int
        relations: list[TargetRelation]
        sentiment: Union[str, TokenSentiment]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_scores: TargetConfidenceScoreLabel, 
                length: int, 
                offset: int, 
                relations: list[TargetRelation], 
                sentiment: Union[str, TokenSentiment], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentActionResult(_Model):
        confidence_scores: SentimentConfidenceScores
        detected_language: Optional[DetectedLanguage]
        id: str
        sentences: list[SentenceSentiment]
        sentiment: Union[str, DocumentSentiment]
        statistics: Optional[DocumentStatistics]
        warnings: list[DocumentWarning]

        @overload
        def __init__(
                self, 
                *, 
                confidence_scores: SentimentConfidenceScores, 
                detected_language: Optional[DetectedLanguage] = ..., 
                id: str, 
                sentences: list[SentenceSentiment], 
                sentiment: Union[str, DocumentSentiment], 
                statistics: Optional[DocumentStatistics] = ..., 
                warnings: list[DocumentWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentAnalysisActionContent(_Model):
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        opinion_mining: Optional[bool]
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                opinion_mining: Optional[bool] = ..., 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentAnalysisOperationAction(AnalyzeTextOperationAction, discriminator='SentimentAnalysis'):
        kind: Literal[AnalyzeTextOperationActionKind.SENTIMENT_ANALYSIS]
        name: str
        parameters: Optional[SentimentAnalysisActionContent]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                parameters: Optional[SentimentAnalysisActionContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentConfidenceScores(_Model):
        negative: float
        neutral: float
        positive: float

        @overload
        def __init__(
                self, 
                *, 
                negative: float, 
                neutral: float, 
                positive: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentLROResult(AnalyzeTextLROResult, discriminator='SentimentAnalysisLROResults'):
        kind: Literal[AnalyzeTextOperationResultsKind.SENTIMENT_ANALYSIS_OPERATION_RESULTS]
        last_update_date_time: datetime
        results: SentimentResult
        status: Union[str, TextActionState]
        task_name: str

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                results: SentimentResult, 
                status: Union[str, TextActionState], 
                task_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SentimentResult(_Model):
        documents: list[SentimentActionResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                documents: list[SentimentActionResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SpeedMetadata(BaseMetadata, discriminator='SpeedMetadata'):
        metadata_kind: Literal[MetadataKind.SPEED_METADATA]
        unit: Union[str, SpeedUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, SpeedUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.SpeedUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CENTIMETERS_PER_MILLISECOND = "CentimetersPerMillisecond"
        FEET_PER_MINUTE = "FeetPerMinute"
        FEET_PER_SECOND = "FeetPerSecond"
        KILOMETERS_PER_HOUR = "KilometersPerHour"
        KILOMETERS_PER_MILLISECOND = "KilometersPerMillisecond"
        KILOMETERS_PER_MINUTE = "KilometersPerMinute"
        KILOMETERS_PER_SECOND = "KilometersPerSecond"
        KNOTS = "Knots"
        METERS_PER_MILLISECOND = "MetersPerMillisecond"
        METERS_PER_SECOND = "MetersPerSecond"
        MILES_PER_HOUR = "MilesPerHour"
        UNSPECIFIED = "Unspecified"
        YARDS_PER_MINUTE = "YardsPerMinute"
        YARDS_PER_SECOND = "YardsPerSecond"


    class azure.ai.textanalytics.models.StringIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEXT_ELEMENTS_V8 = "TextElements_v8"
        UNICODE_CODE_POINT = "UnicodeCodePoint"
        UTF16_CODE_UNIT = "Utf16CodeUnit"


    class azure.ai.textanalytics.models.SummaryContext(_Model):
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


    class azure.ai.textanalytics.models.SummaryLengthBucket(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LONG = "long"
        MEDIUM = "medium"
        SHORT = "short"


    class azure.ai.textanalytics.models.SyntheticReplacementPolicyType(BaseRedactionPolicy, discriminator='syntheticReplacement'):
        entity_types: Union[list[str, PiiCategoriesExclude]]
        is_default: bool
        policy_kind: Literal[RedactionPolicyKind.SYNTHETIC_REPLACEMENT]
        policy_name: str
        preserve_data_format: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                entity_types: Optional[list[Union[str, PiiCategoriesExclude]]] = ..., 
                is_default: Optional[bool] = ..., 
                policy_name: Optional[str] = ..., 
                preserve_data_format: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TargetConfidenceScoreLabel(_Model):
        negative: float
        positive: float

        @overload
        def __init__(
                self, 
                *, 
                negative: float, 
                positive: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TargetRelation(_Model):
        ref: str
        relation_type: Union[str, TargetRelationType]

        @overload
        def __init__(
                self, 
                *, 
                ref: str, 
                relation_type: Union[str, TargetRelationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TargetRelationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSESSMENT = "assessment"
        TARGET = "target"


    class azure.ai.textanalytics.models.TemperatureMetadata(BaseMetadata, discriminator='TemperatureMetadata'):
        metadata_kind: Literal[MetadataKind.TEMPERATURE_METADATA]
        unit: Union[str, TemperatureUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, TemperatureUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TemperatureUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CELSIUS = "Celsius"
        FAHRENHEIT = "Fahrenheit"
        KELVIN = "Kelvin"
        RANKINE = "Rankine"
        UNSPECIFIED = "Unspecified"


    class azure.ai.textanalytics.models.TemporalModifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER = "After"
        AFTER_APPROX = "AfterApprox"
        AFTER_MID = "AfterMid"
        AFTER_START = "AfterStart"
        APPROX = "Approx"
        BEFORE = "Before"
        BEFORE_APPROX = "BeforeApprox"
        BEFORE_END = "BeforeEnd"
        BEFORE_START = "BeforeStart"
        END = "End"
        LESS = "Less"
        MID = "Mid"
        MORE = "More"
        REFERENCE_UNDEFINED = "ReferenceUndefined"
        SINCE = "Since"
        SINCE_END = "SinceEnd"
        START = "Start"
        UNTIL = "Until"


    class azure.ai.textanalytics.models.TemporalSetMetadata(BaseMetadata, discriminator='TemporalSetMetadata'):
        dates: Optional[list[DateValue]]
        metadata_kind: Literal[MetadataKind.TEMPORAL_SET_METADATA]

        @overload
        def __init__(
                self, 
                *, 
                dates: Optional[list[DateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TemporalSpanMetadata(BaseMetadata, discriminator='TemporalSpanMetadata'):
        metadata_kind: Literal[MetadataKind.TEMPORAL_SPAN_METADATA]
        span_values: Optional[list[TemporalSpanValues]]

        @overload
        def __init__(
                self, 
                *, 
                span_values: Optional[list[TemporalSpanValues]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TemporalSpanValues(_Model):
        begin: Optional[str]
        duration: Optional[str]
        end: Optional[str]
        modifier: Optional[Union[str, TemporalModifier]]
        timex: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                begin: Optional[str] = ..., 
                duration: Optional[str] = ..., 
                end: Optional[str] = ..., 
                modifier: Optional[Union[str, TemporalModifier]] = ..., 
                timex: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextActionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.textanalytics.models.TextActions(_Model):
        completed: int
        failed: int
        in_progress: int
        items_property: Optional[list[AnalyzeTextLROResult]]
        total: int

        @overload
        def __init__(
                self, 
                *, 
                completed: int, 
                failed: int, 
                in_progress: int, 
                items_property: Optional[list[AnalyzeTextLROResult]] = ..., 
                total: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextEntityLinkingInput(AnalyzeTextInput, discriminator='EntityLinking'):
        action_content: Optional[EntityLinkingActionContent]
        kind: Literal[AnalyzeTextInputKind.ENTITY_LINKING]
        text_input: Optional[MultiLanguageTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[EntityLinkingActionContent] = ..., 
                text_input: Optional[MultiLanguageTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextEntityRecognitionInput(AnalyzeTextInput, discriminator='EntityRecognition'):
        action_content: Optional[EntitiesActionContent]
        kind: Literal[AnalyzeTextInputKind.ENTITY_RECOGNITION]
        text_input: Optional[MultiLanguageTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[EntitiesActionContent] = ..., 
                text_input: Optional[MultiLanguageTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextKeyPhraseExtractionInput(AnalyzeTextInput, discriminator='KeyPhraseExtraction'):
        action_content: Optional[KeyPhraseActionContent]
        kind: Literal[AnalyzeTextInputKind.KEY_PHRASE_EXTRACTION]
        text_input: Optional[MultiLanguageTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[KeyPhraseActionContent] = ..., 
                text_input: Optional[MultiLanguageTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextLanguageDetectionInput(AnalyzeTextInput, discriminator='LanguageDetection'):
        action_content: Optional[LanguageDetectionActionContent]
        kind: Literal[AnalyzeTextInputKind.LANGUAGE_DETECTION]
        text_input: Optional[LanguageDetectionTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[LanguageDetectionActionContent] = ..., 
                text_input: Optional[LanguageDetectionTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextPiiEntitiesRecognitionInput(AnalyzeTextInput, discriminator='PiiEntityRecognition'):
        action_content: Optional[PiiActionContent]
        kind: Literal[AnalyzeTextInputKind.PII_ENTITY_RECOGNITION]
        text_input: Optional[MultiLanguageTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[PiiActionContent] = ..., 
                text_input: Optional[MultiLanguageTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TextSentimentAnalysisInput(AnalyzeTextInput, discriminator='SentimentAnalysis'):
        action_content: Optional[SentimentAnalysisActionContent]
        kind: Literal[AnalyzeTextInputKind.SENTIMENT_ANALYSIS]
        text_input: Optional[MultiLanguageTextInput]

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[SentimentAnalysisActionContent] = ..., 
                text_input: Optional[MultiLanguageTextInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TimeMetadata(BaseMetadata, discriminator='TimeMetadata'):
        dates: Optional[list[DateValue]]
        metadata_kind: Literal[MetadataKind.TIME_METADATA]

        @overload
        def __init__(
                self, 
                *, 
                dates: Optional[list[DateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.TokenSentiment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "mixed"
        NEGATIVE = "negative"
        POSITIVE = "positive"


    class azure.ai.textanalytics.models.ValueExclusionPolicy(_Model):
        case_sensitive: bool
        excluded_values: list[str]

        @overload
        def __init__(
                self, 
                *, 
                case_sensitive: bool, 
                excluded_values: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.VolumeMetadata(BaseMetadata, discriminator='VolumeMetadata'):
        metadata_kind: Literal[MetadataKind.VOLUME_METADATA]
        unit: Union[str, VolumeUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, VolumeUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.VolumeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BARREL = "Barrel"
        BUSHEL = "Bushel"
        CENTILITER = "Centiliter"
        CORD = "Cord"
        CUBIC_CENTIMETER = "CubicCentimeter"
        CUBIC_FOOT = "CubicFoot"
        CUBIC_INCH = "CubicInch"
        CUBIC_METER = "CubicMeter"
        CUBIC_MILE = "CubicMile"
        CUBIC_MILLIMETER = "CubicMillimeter"
        CUBIC_YARD = "CubicYard"
        CUP = "Cup"
        DECALITER = "Decaliter"
        FLUID_DRAM = "FluidDram"
        FLUID_OUNCE = "FluidOunce"
        GILL = "Gill"
        HECTOLITER = "Hectoliter"
        HOGSHEAD = "Hogshead"
        LITER = "Liter"
        MILLILITER = "Milliliter"
        MINIM = "Minim"
        PECK = "Peck"
        PINCH = "Pinch"
        PINT = "Pint"
        QUART = "Quart"
        TABLESPOON = "Tablespoon"
        TEASPOON = "Teaspoon"
        UNSPECIFIED = "Unspecified"


    class azure.ai.textanalytics.models.WarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCUMENT_TRUNCATED = "DocumentTruncated"
        LONG_WORDS_IN_DOCUMENT = "LongWordsInDocument"


    class azure.ai.textanalytics.models.WeightMetadata(BaseMetadata, discriminator='WeightMetadata'):
        metadata_kind: Literal[MetadataKind.WEIGHT_METADATA]
        unit: Union[str, WeightUnit]
        value: float

        @overload
        def __init__(
                self, 
                *, 
                unit: Union[str, WeightUnit], 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.textanalytics.models.WeightUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAM = "Dram"
        GALLON = "Gallon"
        GRAIN = "Grain"
        GRAM = "Gram"
        KILOGRAM = "Kilogram"
        LONG_TON_BRITISH = "LongTonBritish"
        METRIC_TON = "MetricTon"
        MILLIGRAM = "Milligram"
        OUNCE = "Ounce"
        PENNY_WEIGHT = "PennyWeight"
        POUND = "Pound"
        SHORT_HUNDRED_WEIGHT_US = "ShortHundredWeightUS"
        SHORT_TON_US = "ShortTonUS"
        STONE = "Stone"
        TON = "Ton"
        UNSPECIFIED = "Unspecified"


```