```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.language.conversations

    class azure.ai.language.conversations.AnalyzeConversationLROPoller(LROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
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
            ) -> AnalyzeConversationLROPoller[PollingReturnType_co]: ...


    class azure.ai.language.conversations.ConversationAnalysisClient(AnalysisClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def analyze_conversation(
                self, 
                body: AnalyzeConversationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        def analyze_conversation(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        def analyze_conversation(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        def begin_analyze_conversation_job(
                self, 
                body: AnalyzeConversationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationLROPoller[ItemPaged[ConversationActions]]: ...

        @overload
        def begin_analyze_conversation_job(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationLROPoller[ItemPaged[ConversationActions]]: ...

        @overload
        def begin_analyze_conversation_job(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationLROPoller[ItemPaged[ConversationActions]]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2023-04-01', params_added_on={'2023-04-01': ['api_version', 'job_id']}, api_versions_list=['2023-04-01', '2024-05-01', '2024-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        def begin_cancel_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.language.conversations.aio

    class azure.ai.language.conversations.aio.AnalyzeConversationAsyncLROPoller(AsyncLROPoller[PollingReturnType_co], Generic[PollingReturnType_co]):
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
            ) -> AnalyzeConversationAsyncLROPoller[PollingReturnType_co]: ...


    class azure.ai.language.conversations.aio.ConversationAnalysisClient(AnalysisClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def analyze_conversation(
                self, 
                body: AnalyzeConversationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        async def analyze_conversation(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        async def analyze_conversation(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationActionResult: ...

        @overload
        async def begin_analyze_conversation_job(
                self, 
                body: AnalyzeConversationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]]: ...

        @overload
        async def begin_analyze_conversation_job(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]]: ...

        @overload
        async def begin_analyze_conversation_job(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeConversationAsyncLROPoller[AsyncItemPaged[ConversationActions]]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2023-04-01', params_added_on={'2023-04-01': ['api_version', 'job_id']}, api_versions_list=['2023-04-01', '2024-05-01', '2024-11-01', '2025-05-15-preview', '2025-11-15-preview'])
        async def begin_cancel_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.language.conversations.models

    class azure.ai.language.conversations.models.AgeResolution(ResolutionBase, discriminator='AgeResolution'):
        resolution_kind: Literal[ResolutionKind.AGE_RESOLUTION]
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


    class azure.ai.language.conversations.models.AgeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAY = "Day"
        MONTH = "Month"
        UNSPECIFIED = "Unspecified"
        WEEK = "Week"
        YEAR = "Year"


    class azure.ai.language.conversations.models.AnalysisConfig(_Model):
        api_version: Optional[str]
        target_project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                target_project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationActionResult(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationInput(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationInputKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        CONVERSATIONAL_AI = "ConversationalAI"


    class azure.ai.language.conversations.models.AnalyzeConversationOperationAction(_Model):
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


    class azure.ai.language.conversations.models.AnalyzeConversationOperationInput(_Model):
        actions: list[AnalyzeConversationOperationAction]
        cancel_after: Optional[float]
        conversation_input: MultiLanguageConversationInput
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[AnalyzeConversationOperationAction], 
                cancel_after: Optional[float] = ..., 
                conversation_input: MultiLanguageConversationInput, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationOperationResult(_Model):
        kind: str
        last_update_date_time: datetime
        name: Optional[str]
        status: Union[str, ConversationActionState]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                last_update_date_time: datetime, 
                name: Optional[str] = ..., 
                status: Union[str, ConversationActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationOperationResultsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_SUMMARIZATION_OPERATION_RESULTS = "customConversationalSummarizationResults"
        PII_OPERATION_RESULTS = "conversationalPIIResults"
        SUMMARIZATION_OPERATION_RESULTS = "conversationalSummarizationResults"


    class azure.ai.language.conversations.models.AnalyzeConversationOperationState(_Model):
        actions: ConversationActions
        created_date_time: datetime
        display_name: Optional[str]
        errors: Optional[list[ConversationError]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        next_link: Optional[str]
        statistics: Optional[ConversationRequestStatistics]
        status: Union[str, ConversationActionState]

        @overload
        def __init__(
                self, 
                *, 
                actions: ConversationActions, 
                created_date_time: datetime, 
                display_name: Optional[str] = ..., 
                errors: Optional[list[ConversationError]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                next_link: Optional[str] = ..., 
                statistics: Optional[ConversationRequestStatistics] = ..., 
                status: Union[str, ConversationActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationResult(_Model):
        detected_language: Optional[str]
        prediction: PredictionBase
        query: str

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[str] = ..., 
                prediction: PredictionBase, 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnalyzeConversationResultKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATIONAL_AI_RESULT = "ConversationalAIResult"
        CONVERSATION_RESULT = "ConversationResult"


    class azure.ai.language.conversations.models.AnswerSpan(_Model):
        confidence_score: Optional[float]
        length: Optional[int]
        offset: Optional[int]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: Optional[float] = ..., 
                length: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AnswersResult(_Model):
        answers: Optional[list[KnowledgeBaseAnswer]]

        @overload
        def __init__(
                self, 
                *, 
                answers: Optional[list[KnowledgeBaseAnswer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.AreaResolution(ResolutionBase, discriminator='AreaResolution'):
        resolution_kind: Literal[ResolutionKind.AREA_RESOLUTION]
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


    class azure.ai.language.conversations.models.AreaUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.AudioTiming(_Model):
        duration: Optional[int]
        offset: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                duration: Optional[int] = ..., 
                offset: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.BooleanResolution(ResolutionBase, discriminator='BooleanResolution'):
        resolution_kind: Literal[ResolutionKind.BOOLEAN_RESOLUTION]
        value: bool

        @overload
        def __init__(
                self, 
                *, 
                value: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.CharacterMaskPolicyType(BaseRedactionPolicy, discriminator='characterMask'):
        policy_kind: Literal[RedactionPolicyKind.CHARACTER_MASK]
        redaction_character: Optional[Union[str, RedactionCharacter]]

        @overload
        def __init__(
                self, 
                *, 
                redaction_character: Optional[Union[str, RedactionCharacter]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationActionContent(_Model):
        deployment_name: str
        direct_target: Optional[str]
        is_logging_enabled: Optional[bool]
        project_name: str
        string_index_type: Optional[Union[str, StringIndexType]]
        target_project_parameters: Optional[dict[str, AnalysisConfig]]
        verbose: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                direct_target: Optional[str] = ..., 
                is_logging_enabled: Optional[bool] = ..., 
                project_name: str, 
                string_index_type: Optional[Union[str, StringIndexType]] = ..., 
                target_project_parameters: Optional[dict[str, AnalysisConfig]] = ..., 
                verbose: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationActionResult(AnalyzeConversationActionResult, discriminator='ConversationResult'):
        kind: Literal[AnalyzeConversationResultKind.CONVERSATION_RESULT]
        result: AnalyzeConversationResult

        @overload
        def __init__(
                self, 
                *, 
                result: AnalyzeConversationResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationActionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.language.conversations.models.ConversationActions(_Model):
        completed: int
        failed: int
        in_progress: int
        task_results: Optional[list[AnalyzeConversationOperationResult]]
        total: int

        @overload
        def __init__(
                self, 
                *, 
                completed: int, 
                failed: int, 
                in_progress: int, 
                task_results: Optional[list[AnalyzeConversationOperationResult]] = ..., 
                total: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationAnalysisInput(_Model):
        conversation_item: TextConversationItem

        @overload
        def __init__(
                self, 
                *, 
                conversation_item: TextConversationItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationCallingConfig(_Model):
        is_logging_enabled: Optional[bool]
        language: Optional[str]
        verbose: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_logging_enabled: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                verbose: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationConfig(AnalysisConfig, discriminator='Conversation'):
        api_version: str
        calling_options: Optional[ConversationCallingConfig]
        target_project_kind: Literal[TargetProjectKind.CONVERSATION]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                calling_options: Optional[ConversationCallingConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINANCE = "finance"
        GENERIC = "generic"
        HEALTHCARE = "healthcare"


    class azure.ai.language.conversations.models.ConversationEntity(_Model):
        category: str
        confidence: float
        extra_information: Optional[list[ConversationEntityExtraInformation]]
        length: int
        offset: int
        resolutions: Optional[list[ResolutionBase]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence: float, 
                extra_information: Optional[list[ConversationEntityExtraInformation]] = ..., 
                length: int, 
                offset: int, 
                resolutions: Optional[list[ResolutionBase]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationEntityExtraInformation(_Model):
        extra_information_kind: str

        @overload
        def __init__(
                self, 
                *, 
                extra_information_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationError(_Model):
        code: Union[str, ConversationErrorCode]
        details: Optional[list[ConversationError]]
        innererror: Optional[InnerErrorModel]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, ConversationErrorCode], 
                details: Optional[list[ConversationError]] = ..., 
                innererror: Optional[InnerErrorModel] = ..., 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.ConversationInput(_Model):
        domain: Optional[Union[str, ConversationDomain]]
        id: str
        language: str
        modality: str

        @overload
        def __init__(
                self, 
                *, 
                domain: Optional[Union[str, ConversationDomain]] = ..., 
                id: str, 
                language: str, 
                modality: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationIntent(_Model):
        category: str
        confidence: float

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                confidence: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationItemRange(_Model):
        count: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationLanguageUnderstandingInput(AnalyzeConversationInput, discriminator='Conversation'):
        action_content: ConversationActionContent
        conversation_input: ConversationAnalysisInput
        kind: Literal[AnalyzeConversationInputKind.CONVERSATION]

        @overload
        def __init__(
                self, 
                *, 
                action_content: ConversationActionContent, 
                conversation_input: ConversationAnalysisInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationPiiActionContent(_Model):
        exclude_pii_categories: Optional[list[Union[str, ConversationPiiCategoryExclusions]]]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        pii_categories: Optional[list[Union[str, ConversationPiiCategories]]]
        redact_audio_timing: Optional[bool]
        redaction_character: Optional[Union[str, RedactionCharacter]]
        redaction_policy: Optional[BaseRedactionPolicy]
        redaction_source: Optional[Union[str, TranscriptContentType]]

        @overload
        def __init__(
                self, 
                *, 
                exclude_pii_categories: Optional[list[Union[str, ConversationPiiCategoryExclusions]]] = ..., 
                logging_opt_out: Optional[bool] = ..., 
                model_version: Optional[str] = ..., 
                pii_categories: Optional[list[Union[str, ConversationPiiCategories]]] = ..., 
                redact_audio_timing: Optional[bool] = ..., 
                redaction_character: Optional[Union[str, RedactionCharacter]] = ..., 
                redaction_policy: Optional[BaseRedactionPolicy] = ..., 
                redaction_source: Optional[Union[str, TranscriptContentType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationPiiItemResult(_Model):
        entities: list[NamedEntity]
        id: str
        redacted_content: RedactedTranscriptContent

        @overload
        def __init__(
                self, 
                *, 
                entities: list[NamedEntity], 
                id: str, 
                redacted_content: RedactedTranscriptContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationPiiOperationResult(AnalyzeConversationOperationResult, discriminator='conversationalPIIResults'):
        kind: Literal[AnalyzeConversationOperationResultsKind.PII_OPERATION_RESULTS]
        last_update_date_time: datetime
        name: str
        results: ConversationPiiResults
        status: Union[str, ConversationActionState]

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                name: Optional[str] = ..., 
                results: ConversationPiiResults, 
                status: Union[str, ConversationActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationPiiResults(_Model):
        conversations: list[ConversationalPiiResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[ConversationalPiiResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationPrediction(PredictionBase, discriminator='Conversation'):
        entities: list[ConversationEntity]
        intents: list[ConversationIntent]
        project_kind: Literal[ProjectKind.CONVERSATION]
        top_intent: str

        @overload
        def __init__(
                self, 
                *, 
                entities: list[ConversationEntity], 
                intents: list[ConversationIntent], 
                top_intent: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationRequestStatistics(_Model):
        conversations_count: int
        documents_count: int
        erroneous_conversations_count: int
        erroneous_documents_count: int
        transactions_count: int
        valid_conversations_count: int
        valid_documents_count: int

        @overload
        def __init__(
                self, 
                *, 
                conversations_count: int, 
                documents_count: int, 
                erroneous_conversations_count: int, 
                erroneous_documents_count: int, 
                transactions_count: int, 
                valid_conversations_count: int, 
                valid_documents_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationResult(_Model):
        detected_language: Optional[str]
        prediction: Optional[ConversationPrediction]
        query: str

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[str] = ..., 
                prediction: Optional[ConversationPrediction] = ..., 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationStatistics(_Model):
        transactions_count: int

        @overload
        def __init__(
                self, 
                *, 
                transactions_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationSummarizationActionContent(_Model):
        instruction: Optional[str]
        logging_opt_out: Optional[bool]
        model_version: Optional[str]
        sentence_count: Optional[int]
        string_index_type: Optional[Union[str, StringIndexType]]
        summary_aspects: list[Union[str, SummaryAspect]]
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
                summary_aspects: list[Union[str, SummaryAspect]], 
                summary_length: Optional[Union[str, SummaryLengthBucket]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationTargetIntentResult(TargetIntentResult, discriminator='Conversation'):
        api_version: str
        confidence: float
        result: Optional[ConversationResult]
        target_project_kind: Literal[TargetProjectKind.CONVERSATION]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                confidence: float, 
                result: Optional[ConversationResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIActionContent(_Model):
        deployment_name: str
        project_name: str
        string_index_type: Optional[Union[str, StringIndexType]]

        @overload
        def __init__(
                self, 
                *, 
                deployment_name: str, 
                project_name: str, 
                string_index_type: Optional[Union[str, StringIndexType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIAnalysis(_Model):
        entities: Optional[list[ConversationalAIEntity]]
        id: str
        intents: list[ConversationalAIIntent]

        @overload
        def __init__(
                self, 
                *, 
                entities: Optional[list[ConversationalAIEntity]] = ..., 
                id: str, 
                intents: list[ConversationalAIIntent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIAnalysisInput(_Model):
        conversations: list[TextConversation]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[TextConversation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIEntity(_Model):
        confidence_score: float
        conversation_item_id: str
        conversation_item_index: Optional[int]
        extra_information: Optional[list[ConversationEntityExtraInformation]]
        length: int
        name: str
        offset: int
        resolutions: Optional[list[ResolutionBase]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                confidence_score: float, 
                conversation_item_id: str, 
                conversation_item_index: Optional[int] = ..., 
                extra_information: Optional[list[ConversationEntityExtraInformation]] = ..., 
                length: int, 
                name: str, 
                offset: int, 
                resolutions: Optional[list[ResolutionBase]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIIntent(_Model):
        conversation_item_ranges: list[ConversationItemRange]
        entities: list[ConversationalAIEntity]
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                conversation_item_ranges: list[ConversationItemRange], 
                entities: list[ConversationalAIEntity], 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAIResult(_Model):
        conversations: list[ConversationalAIAnalysis]
        warnings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[ConversationalAIAnalysis], 
                warnings: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAITask(AnalyzeConversationInput, discriminator='ConversationalAI'):
        analysis_input: ConversationalAIAnalysisInput
        kind: Literal[AnalyzeConversationInputKind.CONVERSATIONAL_AI]
        parameters: ConversationalAIActionContent

        @overload
        def __init__(
                self, 
                *, 
                analysis_input: ConversationalAIAnalysisInput, 
                parameters: ConversationalAIActionContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalAITaskResult(AnalyzeConversationActionResult, discriminator='ConversationalAIResult'):
        kind: Literal[AnalyzeConversationResultKind.CONVERSATIONAL_AI_RESULT]
        result: ConversationalAIResult

        @overload
        def __init__(
                self, 
                *, 
                result: ConversationalAIResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationalPiiResult(_Model):
        conversation_items: list[ConversationPiiItemResult]
        id: str
        statistics: Optional[ConversationStatistics]
        warnings: list[InputWarning]

        @overload
        def __init__(
                self, 
                *, 
                conversation_items: list[ConversationPiiItemResult], 
                id: str, 
                statistics: Optional[ConversationStatistics] = ..., 
                warnings: list[InputWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ConversationsSummaryResult(_Model):
        id: str
        statistics: Optional[ConversationStatistics]
        summaries: list[SummaryResultItem]
        warnings: list[InputWarning]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                statistics: Optional[ConversationStatistics] = ..., 
                summaries: list[SummaryResultItem], 
                warnings: list[InputWarning]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.CurrencyResolution(ResolutionBase, discriminator='CurrencyResolution'):
        iso4217: Optional[str]
        resolution_kind: Literal[ResolutionKind.CURRENCY_RESOLUTION]
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


    class azure.ai.language.conversations.models.CustomSummarizationOperationResult(AnalyzeConversationOperationResult, discriminator='customConversationalSummarizationResults'):
        kind: Literal[AnalyzeConversationOperationResultsKind.CUSTOM_SUMMARIZATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        name: str
        results: CustomSummaryResult
        status: Union[str, ConversationActionState]

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                name: Optional[str] = ..., 
                results: CustomSummaryResult, 
                status: Union[str, ConversationActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.CustomSummaryResult(_Model):
        conversations: list[ConversationsSummaryResult]
        deployment_name: str
        errors: list[DocumentError]
        project_name: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[ConversationsSummaryResult], 
                deployment_name: str, 
                errors: list[DocumentError], 
                project_name: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.DateTimeResolution(ResolutionBase, discriminator='DateTimeResolution'):
        date_time_sub_kind: Union[str, DateTimeSubKind]
        modifier: Optional[Union[str, TemporalModifier]]
        resolution_kind: Literal[ResolutionKind.DATE_TIME_RESOLUTION]
        timex: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                date_time_sub_kind: Union[str, DateTimeSubKind], 
                modifier: Optional[Union[str, TemporalModifier]] = ..., 
                timex: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.DateTimeSubKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATE = "Date"
        DATE_TIME = "DateTime"
        DURATION = "Duration"
        SET = "Set"
        TIME = "Time"


    class azure.ai.language.conversations.models.DocumentError(_Model):
        error: ConversationError
        id: str

        @overload
        def __init__(
                self, 
                *, 
                error: ConversationError, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.EntityMaskTypePolicyType(BaseRedactionPolicy, discriminator='entityMask'):
        policy_kind: Literal[RedactionPolicyKind.ENTITY_MASK]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.EntitySubtype(ConversationEntityExtraInformation, discriminator='EntitySubtype'):
        extra_information_kind: Literal[ExtraInformationKind.ENTITY_SUBTYPE]
        tags: Optional[list[EntityTag]]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[list[EntityTag]] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.EntityTag(_Model):
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


    class azure.ai.language.conversations.models.ErrorResponse(_Model):
        error: ConversationError

        @overload
        def __init__(
                self, 
                *, 
                error: ConversationError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ExtraInformationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENTITY_SUBTYPE = "EntitySubtype"
        LIST_KEY = "ListKey"
        REGEX_KEY = "RegexKey"


    class azure.ai.language.conversations.models.InformationResolution(ResolutionBase, discriminator='InformationResolution'):
        resolution_kind: Literal[ResolutionKind.INFORMATION_RESOLUTION]
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


    class azure.ai.language.conversations.models.InformationUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.InnerErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.InnerErrorModel(_Model):
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


    class azure.ai.language.conversations.models.InputModality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEXT = "text"
        TRANSCRIPT = "transcript"


    class azure.ai.language.conversations.models.InputWarning(_Model):
        code: str
        message: str
        target_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                target_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ItemizedSummaryContext(_Model):
        conversation_item_id: str
        length: int
        offset: int

        @overload
        def __init__(
                self, 
                *, 
                conversation_item_id: str, 
                length: int, 
                offset: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.KnowledgeBaseAnswer(_Model):
        answer: Optional[str]
        confidence: Optional[float]
        dialog: Optional[KnowledgeBaseAnswerDialog]
        metadata: Optional[dict[str, str]]
        qna_id: Optional[int]
        questions: Optional[list[str]]
        short_answer: Optional[AnswerSpan]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                answer: Optional[str] = ..., 
                confidence: Optional[float] = ..., 
                dialog: Optional[KnowledgeBaseAnswerDialog] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                qna_id: Optional[int] = ..., 
                questions: Optional[list[str]] = ..., 
                short_answer: Optional[AnswerSpan] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.KnowledgeBaseAnswerContext(_Model):
        previous_qna_id: int
        previous_question: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                previous_qna_id: int, 
                previous_question: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.KnowledgeBaseAnswerDialog(_Model):
        is_context_only: Optional[bool]
        prompts: Optional[list[KnowledgeBaseAnswerPrompt]]

        @overload
        def __init__(
                self, 
                *, 
                is_context_only: Optional[bool] = ..., 
                prompts: Optional[list[KnowledgeBaseAnswerPrompt]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.KnowledgeBaseAnswerPrompt(_Model):
        display_order: Optional[int]
        display_text: Optional[str]
        qna_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                display_order: Optional[int] = ..., 
                display_text: Optional[str] = ..., 
                qna_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.LengthResolution(ResolutionBase, discriminator='LengthResolution'):
        resolution_kind: Literal[ResolutionKind.LENGTH_RESOLUTION]
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


    class azure.ai.language.conversations.models.LengthUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
        POINT = "Pt"
        UNSPECIFIED = "Unspecified"
        YARD = "Yard"


    class azure.ai.language.conversations.models.ListKey(ConversationEntityExtraInformation, discriminator='ListKey'):
        extra_information_kind: Literal[ExtraInformationKind.LIST_KEY]
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.LogicalOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "AND"
        OR = "OR"


    class azure.ai.language.conversations.models.LuisCallingConfig(_Model):
        bing_spell_check_subscription_key: Optional[str]
        log: Optional[bool]
        show_all_intents: Optional[bool]
        spell_check: Optional[bool]
        timezone_offset: Optional[int]
        verbose: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                bing_spell_check_subscription_key: Optional[str] = ..., 
                log: Optional[bool] = ..., 
                show_all_intents: Optional[bool] = ..., 
                spell_check: Optional[bool] = ..., 
                timezone_offset: Optional[int] = ..., 
                verbose: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.LuisConfig(AnalysisConfig, discriminator='Luis'):
        api_version: str
        calling_options: Optional[LuisCallingConfig]
        query: Optional[str]
        target_project_kind: Literal[TargetProjectKind.LUIS]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                calling_options: Optional[LuisCallingConfig] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.LuisResult(_Model):


    class azure.ai.language.conversations.models.LuisTargetIntentResult(TargetIntentResult, discriminator='Luis'):
        api_version: str
        confidence: float
        result: Optional[LuisResult]
        target_project_kind: Literal[TargetProjectKind.LUIS]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                confidence: float, 
                result: Optional[LuisResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.MetadataFilter(_Model):
        logical_operation: Optional[Union[str, LogicalOperationKind]]
        metadata: Optional[list[MetadataRecord]]

        @overload
        def __init__(
                self, 
                *, 
                logical_operation: Optional[Union[str, LogicalOperationKind]] = ..., 
                metadata: Optional[list[MetadataRecord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.MetadataRecord(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.MultiLanguageConversationInput(_Model):
        conversations: list[ConversationInput]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[ConversationInput]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.NamedEntity(_Model):
        category: str
        confidence_score: float
        length: int
        mask: Optional[str]
        mask_length: Optional[int]
        mask_offset: Optional[int]
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
                mask: Optional[str] = ..., 
                mask_length: Optional[int] = ..., 
                mask_offset: Optional[int] = ..., 
                offset: int, 
                subcategory: Optional[str] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.NoMaskPolicyType(BaseRedactionPolicy, discriminator='noMask'):
        policy_kind: Literal[RedactionPolicyKind.NO_MASK]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.NonLinkedTargetIntentResult(TargetIntentResult, discriminator='NonLinked'):
        api_version: str
        confidence: float
        result: Optional[ConversationResult]
        target_project_kind: Literal[TargetProjectKind.NON_LINKED]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                confidence: float, 
                result: Optional[ConversationResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.NumberKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECIMAL = "Decimal"
        FRACTION = "Fraction"
        INTEGER = "Integer"
        PERCENT = "Percent"
        POWER = "Power"
        UNSPECIFIED = "Unspecified"


    class azure.ai.language.conversations.models.NumberResolution(ResolutionBase, discriminator='NumberResolution'):
        number_kind: Union[str, NumberKind]
        resolution_kind: Literal[ResolutionKind.NUMBER_RESOLUTION]
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


    class azure.ai.language.conversations.models.NumericRangeResolution(ResolutionBase, discriminator='NumericRangeResolution'):
        maximum: float
        minimum: float
        range_kind: Union[str, RangeKind]
        resolution_kind: Literal[ResolutionKind.NUMERIC_RANGE_RESOLUTION]

        @overload
        def __init__(
                self, 
                *, 
                maximum: float, 
                minimum: float, 
                range_kind: Union[str, RangeKind]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.OrchestrationPrediction(PredictionBase, discriminator='Orchestration'):
        intents: dict[str, TargetIntentResult]
        project_kind: Literal[ProjectKind.ORCHESTRATION]
        top_intent: str

        @overload
        def __init__(
                self, 
                *, 
                intents: dict[str, TargetIntentResult], 
                top_intent: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.OrdinalResolution(ResolutionBase, discriminator='OrdinalResolution'):
        offset: str
        relative_to: Union[str, RelativeTo]
        resolution_kind: Literal[ResolutionKind.ORDINAL_RESOLUTION]
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


    class azure.ai.language.conversations.models.ParticipantRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        CUSTOMER = "customer"
        GENERIC = "generic"


    class azure.ai.language.conversations.models.PiiOperationAction(AnalyzeConversationOperationAction, discriminator='ConversationalPIITask'):
        action_content: Optional[ConversationPiiActionContent]
        kind: Literal[AnalyzeConversationOperationActionKind.CONVERSATIONAL_PII_TASK]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[ConversationPiiActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.PredictionBase(_Model):
        project_kind: str
        top_intent: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                project_kind: str, 
                top_intent: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ProjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        CONVERSATIONAL_AI = "ConversationalAI"
        ORCHESTRATION = "Orchestration"


    class azure.ai.language.conversations.models.QueryFilters(_Model):
        logical_operation: Optional[Union[str, LogicalOperationKind]]
        metadata_filter: Optional[MetadataFilter]
        source_filter: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                logical_operation: Optional[Union[str, LogicalOperationKind]] = ..., 
                metadata_filter: Optional[MetadataFilter] = ..., 
                source_filter: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.QuestionAnsweringConfig(AnalysisConfig, discriminator='QuestionAnswering'):
        api_version: str
        calling_options: Optional[QuestionAnswersConfig]
        target_project_kind: Literal[TargetProjectKind.QUESTION_ANSWERING]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                calling_options: Optional[QuestionAnswersConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.QuestionAnsweringTargetIntentResult(TargetIntentResult, discriminator='QuestionAnswering'):
        api_version: str
        confidence: float
        result: Optional[AnswersResult]
        target_project_kind: Literal[TargetProjectKind.QUESTION_ANSWERING]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                confidence: float, 
                result: Optional[AnswersResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.QuestionAnswersConfig(_Model):
        answer_context: Optional[KnowledgeBaseAnswerContext]
        confidence_threshold: Optional[float]
        filters: Optional[QueryFilters]
        include_unstructured_sources: Optional[bool]
        qna_id: Optional[int]
        question: Optional[str]
        ranker_kind: Optional[Union[str, RankerKind]]
        short_answer_options: Optional[ShortAnswerConfig]
        top: Optional[int]
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                answer_context: Optional[KnowledgeBaseAnswerContext] = ..., 
                confidence_threshold: Optional[float] = ..., 
                filters: Optional[QueryFilters] = ..., 
                include_unstructured_sources: Optional[bool] = ..., 
                qna_id: Optional[int] = ..., 
                question: Optional[str] = ..., 
                ranker_kind: Optional[Union[str, RankerKind]] = ..., 
                short_answer_options: Optional[ShortAnswerConfig] = ..., 
                top: Optional[int] = ..., 
                user_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.RangeKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.RankerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        QUESTION_ONLY = "QuestionOnly"


    class azure.ai.language.conversations.models.RedactedTranscriptContent(_Model):
        audio_timings: Optional[list[AudioTiming]]
        inverse_text_normalized: Optional[str]
        lexical: Optional[str]
        masked_inverse_text_normalized: Optional[str]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                audio_timings: Optional[list[AudioTiming]] = ..., 
                inverse_text_normalized: Optional[str] = ..., 
                lexical: Optional[str] = ..., 
                masked_inverse_text_normalized: Optional[str] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.RedactionCharacter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMPERSAND = "&"
        ASTERISK = "*"
        AT_SIGN = "@"
        CARET = "^"
        DOLLAR = "$"
        EQUALS = "="
        EXCLAMATION_POINT = "!"
        MINUS = "-"
        NUMBER_SIGN = "#"
        PERCENT = "%"
        PLUS = "+"
        QUESTION_MARK = "?"
        TILDE = "~"
        UNDERSCORE = "_"


    class azure.ai.language.conversations.models.RegexKey(ConversationEntityExtraInformation, discriminator='RegexKey'):
        extra_information_kind: Literal[ExtraInformationKind.REGEX_KEY]
        key: Optional[str]
        regex_pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                regex_pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.RelativeTo(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CURRENT = "Current"
        END = "End"
        START = "Start"


    class azure.ai.language.conversations.models.RequestStatistics(_Model):
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


    class azure.ai.language.conversations.models.ResolutionBase(_Model):
        resolution_kind: str

        @overload
        def __init__(
                self, 
                *, 
                resolution_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.ResolutionKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGE_RESOLUTION = "AgeResolution"
        AREA_RESOLUTION = "AreaResolution"
        BOOLEAN_RESOLUTION = "BooleanResolution"
        CURRENCY_RESOLUTION = "CurrencyResolution"
        DATE_TIME_RESOLUTION = "DateTimeResolution"
        INFORMATION_RESOLUTION = "InformationResolution"
        LENGTH_RESOLUTION = "LengthResolution"
        NUMBER_RESOLUTION = "NumberResolution"
        NUMERIC_RANGE_RESOLUTION = "NumericRangeResolution"
        ORDINAL_RESOLUTION = "OrdinalResolution"
        SPEED_RESOLUTION = "SpeedResolution"
        TEMPERATURE_RESOLUTION = "TemperatureResolution"
        TEMPORAL_SPAN_RESOLUTION = "TemporalSpanResolution"
        VOLUME_RESOLUTION = "VolumeResolution"
        WEIGHT_RESOLUTION = "WeightResolution"


    class azure.ai.language.conversations.models.ShortAnswerConfig(_Model):
        confidence_threshold: Optional[float]
        enable: Optional[bool]
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                enable: Optional[bool] = ..., 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.SpeedResolution(ResolutionBase, discriminator='SpeedResolution'):
        resolution_kind: Literal[ResolutionKind.SPEED_RESOLUTION]
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


    class azure.ai.language.conversations.models.SpeedUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CENTIMETERS_PER_MILLISECOND = "CentimetersPerMillisecond"
        FOOT_PER_MINUTE = "FootPerMinute"
        FOOT_PER_SECOND = "FootPerSecond"
        KILOMETERS_PER_HOUR = "KilometersPerHour"
        KILOMETERS_PER_MILLISECOND = "KilometersPerMillisecond"
        KILOMETERS_PER_MINUTE = "KilometersPerMinute"
        KILOMETERS_PER_SECOND = "KilometersPerSecond"
        KNOT = "Knot"
        METERS_PER_MILLISECOND = "MetersPerMillisecond"
        METERS_PER_SECOND = "MetersPerSecond"
        MILES_PER_HOUR = "MilesPerHour"
        UNSPECIFIED = "Unspecified"
        YARDS_PER_MINUTE = "YardsPerMinute"
        YARDS_PER_SECOND = "YardsPerSecond"


    class azure.ai.language.conversations.models.StringIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEXT_ELEMENTS_V8 = "TextElements_v8"
        UNICODE_CODE_POINT = "UnicodeCodePoint"
        UTF16_CODE_UNIT = "Utf16CodeUnit"


    class azure.ai.language.conversations.models.SummarizationOperationAction(AnalyzeConversationOperationAction, discriminator='ConversationalSummarizationTask'):
        action_content: Optional[ConversationSummarizationActionContent]
        kind: Literal[AnalyzeConversationOperationActionKind.CONVERSATIONAL_SUMMARIZATION_TASK]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action_content: Optional[ConversationSummarizationActionContent] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.SummarizationOperationResult(AnalyzeConversationOperationResult, discriminator='conversationalSummarizationResults'):
        kind: Literal[AnalyzeConversationOperationResultsKind.SUMMARIZATION_OPERATION_RESULTS]
        last_update_date_time: datetime
        name: str
        results: SummaryResult
        status: Union[str, ConversationActionState]

        @overload
        def __init__(
                self, 
                *, 
                last_update_date_time: datetime, 
                name: Optional[str] = ..., 
                results: SummaryResult, 
                status: Union[str, ConversationActionState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.SummaryAspect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAPTER_TITLE = "chapterTitle"
        FOLLOW_UP_TASKS = "follow-up tasks"
        ISSUE = "issue"
        NARRATIVE = "narrative"
        RECAP = "recap"
        RESOLUTION = "resolution"


    class azure.ai.language.conversations.models.SummaryLengthBucket(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LONG = "long"
        MEDIUM = "medium"
        SHORT = "short"


    class azure.ai.language.conversations.models.SummaryResult(_Model):
        conversations: list[ConversationsSummaryResult]
        errors: list[DocumentError]
        model_version: str
        statistics: Optional[RequestStatistics]

        @overload
        def __init__(
                self, 
                *, 
                conversations: list[ConversationsSummaryResult], 
                errors: list[DocumentError], 
                model_version: str, 
                statistics: Optional[RequestStatistics] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.SummaryResultItem(_Model):
        aspect: str
        contexts: Optional[list[ItemizedSummaryContext]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                aspect: str, 
                contexts: Optional[list[ItemizedSummaryContext]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.TargetIntentResult(_Model):
        api_version: Optional[str]
        confidence: float
        target_project_kind: str

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                confidence: float, 
                target_project_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.TargetProjectKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "Conversation"
        LUIS = "Luis"
        NON_LINKED = "NonLinked"
        QUESTION_ANSWERING = "QuestionAnswering"


    class azure.ai.language.conversations.models.TemperatureResolution(ResolutionBase, discriminator='TemperatureResolution'):
        resolution_kind: Literal[ResolutionKind.TEMPERATURE_RESOLUTION]
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


    class azure.ai.language.conversations.models.TemperatureUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CELSIUS = "Celsius"
        FAHRENHEIT = "Fahrenheit"
        KELVIN = "Kelvin"
        RANKINE = "Rankine"
        UNSPECIFIED = "Unspecified"


    class azure.ai.language.conversations.models.TemporalModifier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFTER = "After"
        AFTER_APPROXIMATE = "AfterApprox"
        AFTER_MID = "AfterMid"
        AFTER_START = "AfterStart"
        APPROXIMATE = "Approx"
        BEFORE = "Before"
        BEFORE_APPROXIMATE = "BeforeApprox"
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


    class azure.ai.language.conversations.models.TemporalSpanResolution(ResolutionBase, discriminator='TemporalSpanResolution'):
        begin: Optional[str]
        duration: Optional[str]
        end: Optional[str]
        modifier: Optional[Union[str, TemporalModifier]]
        resolution_kind: Literal[ResolutionKind.TEMPORAL_SPAN_RESOLUTION]
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


    class azure.ai.language.conversations.models.TextConversation(ConversationInput, discriminator='text'):
        conversation_items: list[TextConversationItem]
        domain: Union[str, ConversationDomain]
        id: str
        language: str
        modality: Literal[InputModality.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                conversation_items: list[TextConversationItem], 
                domain: Optional[Union[str, ConversationDomain]] = ..., 
                id: str, 
                language: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.TextConversationItem(_Model):
        id: str
        language: Optional[str]
        modality: Optional[Union[str, InputModality]]
        participant_id: str
        role: Optional[Union[str, ParticipantRole]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                language: Optional[str] = ..., 
                modality: Optional[Union[str, InputModality]] = ..., 
                participant_id: str, 
                role: Optional[Union[str, ParticipantRole]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.conversations.models.VolumeResolution(ResolutionBase, discriminator='VolumeResolution'):
        resolution_kind: Literal[ResolutionKind.VOLUME_RESOLUTION]
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


    class azure.ai.language.conversations.models.VolumeUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.conversations.models.WeightResolution(ResolutionBase, discriminator='WeightResolution'):
        resolution_kind: Literal[ResolutionKind.WEIGHT_RESOLUTION]
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


    class azure.ai.language.conversations.models.WeightUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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