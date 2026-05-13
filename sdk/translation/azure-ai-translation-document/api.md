```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.translation.document

    class azure.ai.translation.document.DocumentStatus(GeneratedDocumentStatus):
        characters_charged: Optional[int]
        created_on: datetime
        error: Optional[DocumentTranslationError]
        id: str
        last_updated_on: datetime
        source_document_url: str
        status: Union[str, Status]
        translated_document_url: Optional[str]
        translated_to: str
        translation_progress: float

        @overload
        def __init__(
                self, 
                *, 
                characters_charged: Optional[int] = ..., 
                created_on: datetime, 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                last_updated_on: datetime, 
                source_document_url: str, 
                status: Union[str, Status], 
                translated_document_url: Optional[str] = ..., 
                translated_to: str, 
                translation_progress: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2024_05_01 = "2024-05-01"


    class azure.ai.translation.document.DocumentTranslationClient(GeneratedDocumentTranslationClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, DocumentTranslationApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_translation(
                self, 
                source_url: str, 
                target_url: str, 
                target_language: str, 
                *, 
                category_id: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ..., 
                **kwargs: Any
            ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]: ...

        @overload
        def begin_translation(
                self, 
                inputs: StartTranslationDetails, 
                **kwargs: Any
            ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]: ...

        @overload
        def begin_translation(
                self, 
                inputs: JSON, 
                **kwargs: Any
            ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]: ...

        @overload
        def begin_translation(
                self, 
                inputs: IO[bytes], 
                **kwargs: Any
            ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]: ...

        @overload
        def begin_translation(
                self, 
                inputs: List[DocumentTranslationInput], 
                **kwargs: Any
            ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]: ...

        @distributed_trace
        def cancel_translation(
                self, 
                translation_id: str, 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_document_status(
                self, 
                translation_id: str, 
                document_id: str, 
                **kwargs: Any
            ) -> DocumentStatus: ...

        @distributed_trace
        def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]: ...

        @distributed_trace
        def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]: ...

        @distributed_trace
        def get_translation_status(
                self, 
                translation_id: str, 
                **kwargs: Any
            ) -> TranslationStatus: ...

        @distributed_trace
        def list_document_statuses(
                self, 
                translation_id: str, 
                *, 
                created_after: Optional[Union[str, datetime]] = ..., 
                created_before: Optional[Union[str, datetime]] = ..., 
                document_ids: Optional[List[str]] = ..., 
                order_by: Optional[List[str]] = ..., 
                skip: Optional[int] = ..., 
                statuses: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DocumentStatus]: ...

        @distributed_trace
        def list_translation_statuses(
                self, 
                *, 
                created_after: Optional[Union[str, datetime]] = ..., 
                created_before: Optional[Union[str, datetime]] = ..., 
                order_by: Optional[List[str]] = ..., 
                skip: Optional[int] = ..., 
                statuses: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                translation_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TranslationStatus]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.translation.document.DocumentTranslationError(Model):
        code: Union[str, TranslationErrorCode]
        inner_error: Optional[InnerTranslationError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, TranslationErrorCode], 
                inner_error: Optional[InnerTranslationError] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.DocumentTranslationFileFormat(Model):
        content_types: List[str]
        default_format_version: Optional[str]
        file_extensions: List[str]
        file_format: str
        format_versions: Optional[List[str]]
        type: Optional[Union[str, FileFormatType]]

        @overload
        def __init__(
                self, 
                *, 
                content_types: List[str], 
                default_format_version: Optional[str] = ..., 
                file_extensions: List[str], 
                file_format: str, 
                format_versions: Optional[List[str]] = ..., 
                type: Optional[Union[str, FileFormatType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.DocumentTranslationInput:
        prefix: Optional[str]
        source_language: Optional[str]
        source_url: str
        storage_source: Optional[str]
        storage_type: Optional[Union[str, StorageInputType]]
        suffix: Optional[str]
        targets: List[TranslationTarget]

        def __init__(
                self, 
                source_url: str, 
                targets: List[TranslationTarget], 
                *, 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_source: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.ai.translation.document.DocumentTranslationLROPoller(LROPoller[PollingReturnType_co]):
        property details: TranslationStatus    # Read-only
        property id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method, 
                continuation_token, 
                **kwargs: Any
            ): ...


    class azure.ai.translation.document.SingleDocumentTranslationClient(SingleDocumentTranslationClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
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

        @overload
        def translate(
                self, 
                body: DocumentTranslateContent, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def translate(
                self, 
                body: JSON, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...


    class azure.ai.translation.document.StorageInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "File"
        FOLDER = "Folder"


    class azure.ai.translation.document.TranslationGlossary(GeneratedTranslationGlossary):
        file_format: str
        format_version: Optional[str]
        glossary_url: str
        storage_source: Optional[Union[str, TranslationStorageSource]]

        @overload
        def __init__(
                self, 
                glossary_url: str, 
                file_format: str, 
                *, 
                format_version: Optional[str] = ..., 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.TranslationStatus(GeneratedTranslationStatus):
        created_on: datetime
        error: Optional[DocumentTranslationError]
        id: str
        last_updated_on: datetime
        status: Union[str, Status]
        summary: TranslationStatusSummary

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                last_updated_on: datetime, 
                status: Union[str, Status], 
                summary: TranslationStatusSummary
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.TranslationTarget(GeneratedTranslationTarget):
        category_id: Optional[str]
        glossaries: Optional[List[TranslationGlossary]]
        language: str
        storage_source: Optional[Union[str, TranslationStorageSource]]
        target_url: str

        @overload
        def __init__(
                self, 
                target_url: str, 
                language: str, 
                *, 
                category_id: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


namespace azure.ai.translation.document.aio

    class azure.ai.translation.document.aio.AsyncDocumentTranslationLROPoller(AsyncLROPoller[PollingReturnType_co]):
        property details: TranslationStatus    # Read-only
        property id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method, 
                continuation_token, 
                **kwargs
            ): ...


    class azure.ai.translation.document.aio.DocumentTranslationClient(GeneratedDocumentTranslationClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, DocumentTranslationApiVersion] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_translation(
                self, 
                source_url: str, 
                target_url: str, 
                target_language: str, 
                *, 
                category_id: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]: ...

        @overload
        async def begin_translation(
                self, 
                inputs: StartTranslationDetails, 
                **kwargs: Any
            ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]: ...

        @overload
        async def begin_translation(
                self, 
                inputs: JSON, 
                **kwargs: Any
            ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]: ...

        @overload
        async def begin_translation(
                self, 
                inputs: IO[bytes], 
                **kwargs: Any
            ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]: ...

        @overload
        async def begin_translation(
                self, 
                inputs: List[DocumentTranslationInput], 
                **kwargs: Any
            ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]: ...

        @distributed_trace_async
        async def cancel_translation(
                self, 
                translation_id: str, 
                **kwargs: Any
            ) -> TranslationStatus: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_document_status(
                self, 
                translation_id: str, 
                document_id: str, 
                **kwargs: Any
            ) -> DocumentStatus: ...

        @distributed_trace_async
        async def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]: ...

        @distributed_trace_async
        async def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]: ...

        @distributed_trace_async
        async def get_translation_status(
                self, 
                translation_id: str, 
                **kwargs: Any
            ) -> TranslationStatus: ...

        @distributed_trace
        def list_document_statuses(
                self, 
                translation_id: str, 
                *, 
                created_after: Optional[Union[str, datetime]] = ..., 
                created_before: Optional[Union[str, datetime]] = ..., 
                document_ids: Optional[List[str]] = ..., 
                order_by: Optional[List[str]] = ..., 
                skip: Optional[int] = ..., 
                statuses: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DocumentStatus]: ...

        @distributed_trace
        def list_translation_statuses(
                self, 
                *, 
                created_after: Optional[Union[str, datetime]] = ..., 
                created_before: Optional[Union[str, datetime]] = ..., 
                order_by: Optional[List[str]] = ..., 
                skip: Optional[int] = ..., 
                statuses: Optional[List[str]] = ..., 
                top: Optional[int] = ..., 
                translation_ids: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TranslationStatus]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.translation.document.aio.SingleDocumentTranslationClient(SingleDocumentTranslationClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
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

        @overload
        async def translate(
                self, 
                body: DocumentTranslateContent, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def translate(
                self, 
                body: JSON, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...


namespace azure.ai.translation.document.models

    class azure.ai.translation.document.models.DocumentBatch(Model):
        source: SourceInput
        storage_type: Optional[Union[str, StorageInputType]]
        targets: List[TranslationTarget]

        @overload
        def __init__(
                self, 
                *, 
                source: SourceInput, 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                targets: List[TranslationTarget]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentFilter(Model):
        prefix: Optional[str]
        suffix: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                prefix: Optional[str] = ..., 
                suffix: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentStatus(GeneratedDocumentStatus):
        characters_charged: Optional[int]
        created_on: datetime
        error: Optional[DocumentTranslationError]
        id: str
        last_updated_on: datetime
        source_document_url: str
        status: Union[str, Status]
        translated_document_url: Optional[str]
        translated_to: str
        translation_progress: float

        @overload
        def __init__(
                self, 
                *, 
                characters_charged: Optional[int] = ..., 
                created_on: datetime, 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                last_updated_on: datetime, 
                source_document_url: str, 
                status: Union[str, Status], 
                translated_document_url: Optional[str] = ..., 
                translated_to: str, 
                translation_progress: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.models.DocumentTranslateContent(Model):
        document: Union[str, bytes, IO[str], IO[bytes], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]
        glossary: Optional[List[Union[str, bytes, IO[str], IO[bytes], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], Tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]]

        @overload
        def __init__(
                self, 
                *, 
                document: FileType, 
                glossary: Optional[List[FileType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentTranslationError(Model):
        code: Union[str, TranslationErrorCode]
        inner_error: Optional[InnerTranslationError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, TranslationErrorCode], 
                inner_error: Optional[InnerTranslationError] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentTranslationFileFormat(Model):
        content_types: List[str]
        default_format_version: Optional[str]
        file_extensions: List[str]
        file_format: str
        format_versions: Optional[List[str]]
        type: Optional[Union[str, FileFormatType]]

        @overload
        def __init__(
                self, 
                *, 
                content_types: List[str], 
                default_format_version: Optional[str] = ..., 
                file_extensions: List[str], 
                file_format: str, 
                format_versions: Optional[List[str]] = ..., 
                type: Optional[Union[str, FileFormatType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentTranslationInput:
        prefix: Optional[str]
        source_language: Optional[str]
        source_url: str
        storage_source: Optional[str]
        storage_type: Optional[Union[str, StorageInputType]]
        suffix: Optional[str]
        targets: List[TranslationTarget]

        def __init__(
                self, 
                source_url: str, 
                targets: List[TranslationTarget], 
                *, 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_source: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ...
            ) -> None: ...

        def __repr__(self) -> str: ...


    class azure.ai.translation.document.models.FileFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCUMENT = "document"
        GLOSSARY = "glossary"


    class azure.ai.translation.document.models.InnerTranslationError(Model):
        code: str
        inner_error: Optional[InnerTranslationError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                inner_error: Optional[InnerTranslationError] = ..., 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.SourceInput(Model):
        filter: Optional[DocumentFilter]
        language: Optional[str]
        source_url: str
        storage_source: Optional[Union[str, TranslationStorageSource]]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[DocumentFilter] = ..., 
                language: Optional[str] = ..., 
                source_url: str, 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.StartTranslationDetails(Model):
        inputs: List[DocumentBatch]

        @overload
        def __init__(
                self, 
                *, 
                inputs: List[DocumentBatch]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Cancelled"
        CANCELING = "Cancelling"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        VALIDATION_FAILED = "ValidationFailed"


    class azure.ai.translation.document.models.StorageInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "File"
        FOLDER = "Folder"


    class azure.ai.translation.document.models.TranslationErrorCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL_SERVER_ERROR = "InternalServerError"
        INVALID_ARGUMENT = "InvalidArgument"
        INVALID_REQUEST = "InvalidRequest"
        REQUEST_RATE_TOO_HIGH = "RequestRateTooHigh"
        RESOURCE_NOT_FOUND = "ResourceNotFound"
        SERVICE_UNAVAILABLE = "ServiceUnavailable"
        UNAUTHORIZED = "Unauthorized"


    class azure.ai.translation.document.models.TranslationGlossary(GeneratedTranslationGlossary):
        file_format: str
        format_version: Optional[str]
        glossary_url: str
        storage_source: Optional[Union[str, TranslationStorageSource]]

        @overload
        def __init__(
                self, 
                glossary_url: str, 
                file_format: str, 
                *, 
                format_version: Optional[str] = ..., 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.models.TranslationStatus(GeneratedTranslationStatus):
        created_on: datetime
        error: Optional[DocumentTranslationError]
        id: str
        last_updated_on: datetime
        status: Union[str, Status]
        summary: TranslationStatusSummary

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                created_on: datetime, 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                last_updated_on: datetime, 
                status: Union[str, Status], 
                summary: TranslationStatusSummary
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.models.TranslationStatusSummary(Model):
        canceled: int
        failed: int
        in_progress: int
        not_yet_started: int
        success: int
        total: int
        total_characters_charged: int

        @overload
        def __init__(
                self, 
                *, 
                canceled: int, 
                failed: int, 
                in_progress: int, 
                not_yet_started: int, 
                success: int, 
                total: int, 
                total_characters_charged: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.TranslationStorageSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"


    class azure.ai.translation.document.models.TranslationTarget(GeneratedTranslationTarget):
        category_id: Optional[str]
        glossaries: Optional[List[TranslationGlossary]]
        language: str
        storage_source: Optional[Union[str, TranslationStorageSource]]
        target_url: str

        @overload
        def __init__(
                self, 
                target_url: str, 
                language: str, 
                *, 
                category_id: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


```