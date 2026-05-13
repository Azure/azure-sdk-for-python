```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.language.questionanswering.authoring

    class azure.ai.language.questionanswering.authoring.QuestionAnsweringAuthoringClient(_QuestionAnsweringAuthoringClientOperationsMixin): implements ContextManager 

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
        def add_feedback(
                self, 
                project_name: str, 
                body: ActiveLearningFeedback, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_feedback(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_feedback(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_delete_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_deploy_project(
                self, 
                project_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_export(
                self, 
                project_name: str, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[ImportJobOptions] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[JSON] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_from_files(
                self, 
                project_name: str, 
                body: ImportFiles, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_import_from_files(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_qnas(
                self, 
                project_name: str, 
                qnas: list[UpdateQnaRecord], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_qnas(
                self, 
                project_name: str, 
                qnas: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_sources(
                self, 
                project_name: str, 
                sources: list[UpdateSourceRecord], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_sources(
                self, 
                project_name: str, 
                sources: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_sources_from_files(
                self, 
                project_name: str, 
                body: UpdateSourceFiles, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_sources_from_files(
                self, 
                project_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        def close(self) -> None: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                options: QuestionAnsweringProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                options: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @overload
        def create_project(
                self, 
                project_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @distributed_trace
        def get_project_details(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @distributed_trace
        def list_deployments(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectDeployment]: ...

        @distributed_trace
        def list_projects(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QuestionAnsweringProject]: ...

        @distributed_trace
        def list_qnas(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                source: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RetrieveQnaRecord]: ...

        @distributed_trace
        def list_sources(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[QnaSourceRecord]: ...

        @distributed_trace
        def list_synonyms(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[WordAlterations]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_synonyms(
                self, 
                project_name: str, 
                synonyms: SynonymAssets, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_synonyms(
                self, 
                project_name: str, 
                synonyms: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update_synonyms(
                self, 
                project_name: str, 
                synonyms: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.language.questionanswering.authoring.aio

    class azure.ai.language.questionanswering.authoring.aio.QuestionAnsweringAuthoringClient(_QuestionAnsweringAuthoringClientOperationsMixin): implements AsyncContextManager 

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
        async def add_feedback(
                self, 
                project_name: str, 
                body: ActiveLearningFeedback, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_feedback(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_feedback(
                self, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete_project(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_deploy_project(
                self, 
                project_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_export(
                self, 
                project_name: str, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[ImportJobOptions] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[JSON] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_assets(
                self, 
                project_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                content_type: str = "application/json", 
                file_format: Optional[Union[str, Format]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_from_files(
                self, 
                project_name: str, 
                body: ImportFiles, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_import_from_files(
                self, 
                project_name: str, 
                body: JSON, 
                *, 
                asset_kind: Optional[Union[str, AssetKind]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_qnas(
                self, 
                project_name: str, 
                qnas: list[UpdateQnaRecord], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_qnas(
                self, 
                project_name: str, 
                qnas: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_sources(
                self, 
                project_name: str, 
                sources: list[UpdateSourceRecord], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_sources(
                self, 
                project_name: str, 
                sources: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_sources_from_files(
                self, 
                project_name: str, 
                body: UpdateSourceFiles, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_sources_from_files(
                self, 
                project_name: str, 
                body: JSON, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        async def close(self) -> None: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                options: QuestionAnsweringProject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                options: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @overload
        async def create_project(
                self, 
                project_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @distributed_trace_async
        async def get_project_details(
                self, 
                project_name: str, 
                **kwargs: Any
            ) -> QuestionAnsweringProject: ...

        @distributed_trace
        def list_deployments(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectDeployment]: ...

        @distributed_trace
        def list_projects(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[QuestionAnsweringProject]: ...

        @distributed_trace
        def list_qnas(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                source: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RetrieveQnaRecord]: ...

        @distributed_trace
        def list_sources(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[QnaSourceRecord]: ...

        @distributed_trace
        def list_synonyms(
                self, 
                project_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[WordAlterations]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_synonyms(
                self, 
                project_name: str, 
                synonyms: SynonymAssets, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_synonyms(
                self, 
                project_name: str, 
                synonyms: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update_synonyms(
                self, 
                project_name: str, 
                synonyms: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


namespace azure.ai.language.questionanswering.authoring.models

    class azure.ai.language.questionanswering.authoring.models.ActiveLearningFeedback(_Model):
        records: Optional[list[FeedbackRecord]]

        @overload
        def __init__(
                self, 
                *, 
                records: Optional[list[FeedbackRecord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.AssetKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QNAS = "qnas"
        SYNONYMS = "synonyms"


    class azure.ai.language.questionanswering.authoring.models.Assets(_Model):
        qnas: Optional[list[ImportQnaRecord]]
        synonyms: Optional[list[WordAlterations]]

        @overload
        def __init__(
                self, 
                *, 
                qnas: Optional[list[ImportQnaRecord]] = ..., 
                synonyms: Optional[list[WordAlterations]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.Error(_Model):
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


    class azure.ai.language.questionanswering.authoring.models.ErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.questionanswering.authoring.models.ErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.FeedbackRecord(_Model):
        qna_id: Optional[int]
        user_id: Optional[str]
        user_question: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                qna_id: Optional[int] = ..., 
                user_id: Optional[str] = ..., 
                user_question: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCEL = "excel"
        JSON = "json"
        TSV = "tsv"


    class azure.ai.language.questionanswering.authoring.models.ImportFiles(_Model):
        files: list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]

        @overload
        def __init__(
                self, 
                *, 
                files: list[FileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.ImportJobOptions(_Model):
        assets: Optional[Assets]
        file_uri: Optional[str]
        metadata: Optional[QuestionAnsweringProject]

        @overload
        def __init__(
                self, 
                *, 
                assets: Optional[Assets] = ..., 
                file_uri: Optional[str] = ..., 
                metadata: Optional[QuestionAnsweringProject] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.ImportQnaRecord(_Model):
        active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]]
        answer: Optional[str]
        dialog: Optional[QnaDialog]
        id: int
        last_updated_date_time: Optional[datetime]
        metadata: Optional[dict[str, str]]
        questions: Optional[list[str]]
        source: Optional[str]
        source_display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]] = ..., 
                answer: Optional[str] = ..., 
                dialog: Optional[QnaDialog] = ..., 
                id: int, 
                last_updated_date_time: Optional[datetime] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                questions: Optional[list[str]] = ..., 
                source: Optional[str] = ..., 
                source_display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.InnerErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.language.questionanswering.authoring.models.InnerErrorModel(_Model):
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


    class azure.ai.language.questionanswering.authoring.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        CANCELLING = "cancelling"
        FAILED = "failed"
        NOT_STARTED = "notStarted"
        PARTIALLY_COMPLETED = "partiallyCompleted"
        RUNNING = "running"
        SUCCEEDED = "succeeded"


    class azure.ai.language.questionanswering.authoring.models.ProjectDeployment(_Model):
        deployment_name: str
        last_deployed_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                last_deployed_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.ProjectSettings(_Model):
        default_answer: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_answer: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QnaDialog(_Model):
        is_context_only: Optional[bool]
        prompts: Optional[list[QnaPrompt]]

        @overload
        def __init__(
                self, 
                *, 
                is_context_only: Optional[bool] = ..., 
                prompts: Optional[list[QnaPrompt]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QnaPrompt(_Model):
        display_order: Optional[int]
        display_text: Optional[str]
        qna: Optional[QnaRecord]
        qna_id: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                display_order: Optional[int] = ..., 
                display_text: Optional[str] = ..., 
                qna: Optional[QnaRecord] = ..., 
                qna_id: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QnaRecord(_Model):
        active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]]
        answer: Optional[str]
        dialog: Optional[QnaDialog]
        id: int
        metadata: Optional[dict[str, str]]
        questions: Optional[list[str]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]] = ..., 
                answer: Optional[str] = ..., 
                dialog: Optional[QnaDialog] = ..., 
                id: int, 
                metadata: Optional[dict[str, str]] = ..., 
                questions: Optional[list[str]] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QnaSourceRecord(_Model):
        content_structure_kind: Optional[Union[str, SourceContentStructureKind]]
        display_name: Optional[str]
        last_updated_date_time: Optional[datetime]
        source: str
        source_kind: Union[str, SourceKind]
        source_uri: str

        @overload
        def __init__(
                self, 
                *, 
                content_structure_kind: Optional[Union[str, SourceContentStructureKind]] = ..., 
                display_name: Optional[str] = ..., 
                last_updated_date_time: Optional[datetime] = ..., 
                source: str, 
                source_kind: Union[str, SourceKind], 
                source_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringExportJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        result_url: str
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                result_url: str, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringImportJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringProjectDeletionJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringProjectDeploymentJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringUpdateQnasJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringAuthoringUpdateSourcesJobState(_Model):
        created_date_time: datetime
        errors: Optional[list[ODataV4Format]]
        expiration_date_time: Optional[datetime]
        job_id: str
        last_updated_date_time: datetime
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                created_date_time: datetime, 
                errors: Optional[list[ODataV4Format]] = ..., 
                expiration_date_time: Optional[datetime] = ..., 
                last_updated_date_time: datetime, 
                status: Union[str, JobStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.QuestionAnsweringProject(_Model):
        configure_semantic_ranking: Optional[bool]
        created_date_time: Optional[datetime]
        description: Optional[str]
        language: Optional[str]
        last_deployed_date_time: Optional[datetime]
        last_modified_date_time: Optional[datetime]
        multilingual_resource: Optional[bool]
        project_name: str
        settings: Optional[ProjectSettings]

        @overload
        def __init__(
                self, 
                *, 
                configure_semantic_ranking: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                language: Optional[str] = ..., 
                multilingual_resource: Optional[bool] = ..., 
                settings: Optional[ProjectSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.RetrieveQnaRecord(_Model):
        active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]]
        answer: Optional[str]
        dialog: Optional[QnaDialog]
        id: int
        last_updated_date_time: Optional[datetime]
        metadata: Optional[dict[str, str]]
        questions: Optional[list[str]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                active_learning_suggestions: Optional[list[SuggestedQuestionsCluster]] = ..., 
                answer: Optional[str] = ..., 
                dialog: Optional[QnaDialog] = ..., 
                id: int, 
                last_updated_date_time: Optional[datetime] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                questions: Optional[list[str]] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.SourceContentStructureKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        UNSTRUCTURED = "unstructured"


    class azure.ai.language.questionanswering.authoring.models.SourceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "file"
        URL = "url"


    class azure.ai.language.questionanswering.authoring.models.SuggestedQuestion(_Model):
        auto_suggested_count: Optional[int]
        question: Optional[str]
        user_suggested_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_suggested_count: Optional[int] = ..., 
                question: Optional[str] = ..., 
                user_suggested_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.SuggestedQuestionsCluster(_Model):
        cluster_head: Optional[str]
        suggested_questions: Optional[list[SuggestedQuestion]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_head: Optional[str] = ..., 
                suggested_questions: Optional[list[SuggestedQuestion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.SynonymAssets(_Model):
        next_link: Optional[str]
        value: list[WordAlterations]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[WordAlterations]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.UpdateOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "add"
        DELETE = "delete"
        REPLACE = "replace"


    class azure.ai.language.questionanswering.authoring.models.UpdateQnaRecord(_Model):
        op: Union[str, UpdateOperationKind]
        value: QnaRecord

        @overload
        def __init__(
                self, 
                *, 
                op: Union[str, UpdateOperationKind], 
                value: QnaRecord
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.UpdateQnaSourceRecord(_Model):
        content_structure_kind: Optional[Union[str, SourceContentStructureKind]]
        display_name: Optional[str]
        refresh: Optional[bool]
        source: str
        source_kind: Union[str, SourceKind]
        source_uri: str

        @overload
        def __init__(
                self, 
                *, 
                content_structure_kind: Optional[Union[str, SourceContentStructureKind]] = ..., 
                display_name: Optional[str] = ..., 
                refresh: Optional[bool] = ..., 
                source: str, 
                source_kind: Union[str, SourceKind], 
                source_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.UpdateSourceFiles(_Model):
        file_operations: list[UpdateSourceFromFileOperationRecord]
        files: list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]

        @overload
        def __init__(
                self, 
                *, 
                file_operations: list[UpdateSourceFromFileOperationRecord], 
                files: list[FileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.UpdateSourceFromFileOperationRecord(_Model):
        file_display_name: Optional[str]
        file_name: str
        operation: Union[str, UpdateOperationKind]
        refresh: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                file_display_name: Optional[str] = ..., 
                file_name: str, 
                operation: Union[str, UpdateOperationKind], 
                refresh: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.UpdateSourceRecord(_Model):
        op: Union[str, UpdateOperationKind]
        value: UpdateQnaSourceRecord

        @overload
        def __init__(
                self, 
                *, 
                op: Union[str, UpdateOperationKind], 
                value: UpdateQnaSourceRecord
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.language.questionanswering.authoring.models.WordAlterations(_Model):
        alterations: list[str]

        @overload
        def __init__(
                self, 
                *, 
                alterations: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```