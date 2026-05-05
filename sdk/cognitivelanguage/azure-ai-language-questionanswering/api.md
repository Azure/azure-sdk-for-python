```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.language.questionanswering

    class azure.ai.language.questionanswering.QuestionAnsweringClient(_QuestionAnsweringClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def get_answers(
                self, 
                options: AnswersOptions, 
                *, 
                deployment_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AnswersResult: ...

        @overload
        def get_answers(
                self, 
                *, 
                answer_context: Optional[KnowledgeBaseAnswerContext] = ..., 
                confidence_threshold: Optional[float] = ..., 
                deployment_name: str, 
                filters: Optional[QueryFilters] = ..., 
                include_unstructured_sources: Optional[bool] = ..., 
                project_name: str, 
                qna_id: Optional[int] = ..., 
                question: Optional[str] = ..., 
                ranker_kind: Optional[str] = ..., 
                short_answer_options: Optional[ShortAnswerOptions] = ..., 
                top: Optional[int] = ..., 
                user_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AnswersResult: ...

        @overload
        def get_answers_from_text(
                self, 
                options: AnswersFromTextOptions, 
                **kwargs: Any
            ) -> AnswersFromTextResult: ...

        @overload
        def get_answers_from_text(
                self, 
                *, 
                language: Optional[str] = ..., 
                question: str, 
                text_documents: List[Union[str, TextDocument]], 
                **kwargs: Any
            ) -> AnswersFromTextResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.language.questionanswering.aio

    class azure.ai.language.questionanswering.aio.QuestionAnsweringClient(_QuestionAnsweringClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def get_answers(
                self, 
                options: AnswersOptions, 
                *, 
                deployment_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AnswersResult: ...

        @overload
        async def get_answers(
                self, 
                *, 
                answer_context: Optional[KnowledgeBaseAnswerContext] = ..., 
                confidence_threshold: Optional[float] = ..., 
                deployment_name: str, 
                filters: Optional[QueryFilters] = ..., 
                include_unstructured_sources: Optional[bool] = ..., 
                project_name: str, 
                qna_id: Optional[int] = ..., 
                question: Optional[str] = ..., 
                ranker_kind: Optional[str] = ..., 
                short_answer_options: Optional[ShortAnswerOptions] = ..., 
                top: Optional[int] = ..., 
                user_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AnswersResult: ...

        @overload
        async def get_answers_from_text(
                self, 
                options: AnswersFromTextOptions, 
                **kwargs: Any
            ) -> AnswersFromTextResult: ...

        @overload
        async def get_answers_from_text(
                self, 
                *, 
                language: Optional[str] = ..., 
                question: str, 
                text_documents: List[Union[str, TextDocument]], 
                **kwargs: Any
            ) -> AnswersFromTextResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.language.questionanswering.models

    class azure.ai.language.questionanswering.models.AnswerSpan(_Model):
        confidence: Optional[float]
        length: Optional[int]
        offset: Optional[int]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                length: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.AnswersFromTextOptions(AnswersFromTextOptionsGenerated):
        language: str
        question: str
        text_documents: Union[list[str, TextDocument]]

        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                question: str, 
                text_documents: List[Union[str, TextDocument]], 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.language.questionanswering.models.AnswersFromTextResult(_Model):
        answers: Optional[list[TextAnswer]]

        @overload
        def __init__(
                self, 
                *, 
                answers: Optional[list[TextAnswer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.AnswersOptions(_Model):
        answer_context: Optional[KnowledgeBaseAnswerContext]
        confidence_threshold: Optional[float]
        filters: Optional[QueryFilters]
        include_unstructured_sources: Optional[bool]
        qna_id: Optional[int]
        query_preferences: Optional[QueryPreferences]
        question: Optional[str]
        ranker_kind: Optional[Union[str, RankerKind]]
        short_answer_options: Optional[ShortAnswerOptions]
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
                query_preferences: Optional[QueryPreferences] = ..., 
                question: Optional[str] = ..., 
                ranker_kind: Optional[Union[str, RankerKind]] = ..., 
                short_answer_options: Optional[ShortAnswerOptions] = ..., 
                top: Optional[int] = ..., 
                user_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.AnswersResult(_Model):
        answers: Optional[list[KnowledgeBaseAnswer]]

        @overload
        def __init__(
                self, 
                *, 
                answers: Optional[list[KnowledgeBaseAnswer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.Error(_Model):
        code: Union[str, ErrorCode]
        details: Optional[list[Error]]
        innererror: Optional[InnerErrorModel]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, ErrorCode], 
                details: Optional[list[Error]] = ..., 
                innererror: Optional[InnerErrorModel] = ..., 
                message: str, 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.ErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.questionanswering.models.ErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.InnerErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.questionanswering.models.InnerErrorModel(_Model):
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


    class azure.ai.language.questionanswering.models.KnowledgeBaseAnswer(_Model):
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


    class azure.ai.language.questionanswering.models.KnowledgeBaseAnswerContext(_Model):
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


    class azure.ai.language.questionanswering.models.KnowledgeBaseAnswerDialog(_Model):
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


    class azure.ai.language.questionanswering.models.KnowledgeBaseAnswerPrompt(_Model):
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


    class azure.ai.language.questionanswering.models.LogicalOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AND = "AND"
        OR = "OR"


    class azure.ai.language.questionanswering.models.MatchingPolicy(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.MatchingPolicyFieldsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSWER = "Answer"
        QUESTIONS = "Questions"


    class azure.ai.language.questionanswering.models.MatchingPolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREBUILT = "Prebuilt"


    class azure.ai.language.questionanswering.models.MetadataFilter(MetadataFilterGenerated):
        logical_operation: str
        metadata: Union[list[tuple[str, str]], list[MetadataRecord]]

        @overload
        def __init__(
                self, 
                *, 
                logical_operation: Optional[str] = ..., 
                metadata: Optional[List[Tuple[str, str]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(
                self, 
                *, 
                logical_operation: Optional[str] = ..., 
                metadata: Optional[List[MetadataRecord]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.MetadataRecord(_Model):
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


    class azure.ai.language.questionanswering.models.PrebuiltQueryMatchingPolicy(MatchingPolicy, discriminator='Prebuilt'):
        disable_full_match: Optional[bool]
        fields: Optional[list[Union[str, MatchingPolicyFieldsType]]]
        kind: Literal[MatchingPolicyKind.PREBUILT]

        @overload
        def __init__(
                self, 
                *, 
                disable_full_match: Optional[bool] = ..., 
                fields: Optional[list[Union[str, MatchingPolicyFieldsType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.QueryFilters(_Model):
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


    class azure.ai.language.questionanswering.models.QueryPreferences(_Model):
        matching_policy: Optional[MatchingPolicy]
        scorer: Optional[Union[str, Scorer]]

        @overload
        def __init__(
                self, 
                *, 
                matching_policy: Optional[MatchingPolicy] = ..., 
                scorer: Optional[Union[str, Scorer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.RankerKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        QUESTION_ONLY = "QuestionOnly"


    class azure.ai.language.questionanswering.models.Scorer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIC = "Classic"
        SEMANTIC = "Semantic"
        TRANSFORMER = "Transformer"


    class azure.ai.language.questionanswering.models.ShortAnswerOptions(_Model):
        confidence_threshold: Optional[float]
        enable: bool
        top: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                confidence_threshold: Optional[float] = ..., 
                enable: bool, 
                top: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.StringIndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEXT_ELEMENTS_V8 = "TextElements_v8"
        UNICODE_CODE_POINT = "UnicodeCodePoint"
        UTF16_CODE_UNIT = "Utf16CodeUnit"


    class azure.ai.language.questionanswering.models.TextAnswer(_Model):
        answer: Optional[str]
        confidence: Optional[float]
        id: Optional[str]
        length: Optional[int]
        offset: Optional[int]
        short_answer: Optional[AnswerSpan]

        @overload
        def __init__(
                self, 
                *, 
                answer: Optional[str] = ..., 
                confidence: Optional[float] = ..., 
                id: Optional[str] = ..., 
                length: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                short_answer: Optional[AnswerSpan] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.models.TextDocument(_Model):
        id: str
        text: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```