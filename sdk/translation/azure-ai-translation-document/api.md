```py
namespace azure.ai.translation.document

    class azure.ai.translation.document.DocumentStatus(GeneratedDocumentStatus):
        characters_charged: Optional[int]
        created_on: datetime
        deployment_name: Optional[str]
        error: Optional[DocumentTranslationError]
        id: str
        image_characters_detected: Optional[int]
        images_charged: Optional[int]
        last_updated_on: datetime
        source_document_url: str
        status: Union[str, Status]
        total_image_scans_failed: Optional[int]
        total_image_scans_succeeded: Optional[int]
        translated_document_url: Optional[str]
        translated_to: str
        translation_progress: float

        @overload
        def __init__(
                self, 
                *, 
                characters_charged: Optional[int] = ..., 
                created_on: datetime, 
                deployment_name: Optional[str] = ..., 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                image_characters_detected: Optional[int] = ..., 
                images_charged: Optional[int] = ..., 
                last_updated_on: datetime, 
                source_document_url: str, 
                status: Union[str, Status], 
                total_image_scans_failed: Optional[int] = ..., 
                total_image_scans_succeeded: Optional[int] = ..., 
                translated_document_url: Optional[str] = ..., 
                translated_to: str, 
                translation_progress: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V2024_05_01 = "2024-05-01"
        V2026_03_01 = "2026-03-01"


    class azure.ai.translation.document.DocumentTranslationClient(DocumentTranslationClientOperationsMixin, GeneratedDocumentTranslationClient): implements ContextManager 

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
                deployment_name: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ..., 
                translate_text_within_image: Optional[bool] = ..., 
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


    class azure.ai.translation.document.DocumentTranslationError(_Model):
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


    class azure.ai.translation.document.DocumentTranslationFileFormat(_Model):
        content_types: list[str]
        default_format_version: Optional[str]
        file_extensions: list[str]
        file_format: str
        format_versions: Optional[list[str]]
        type: Optional[Union[str, FileFormatType]]

        @overload
        def __init__(
                self, 
                *, 
                content_types: list[str], 
                default_format_version: Optional[str] = ..., 
                file_extensions: list[str], 
                file_format: str, 
                format_versions: Optional[list[str]] = ..., 
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


    class azure.ai.translation.document.SingleDocumentTranslationClient(SingleDocumentTranslationClientOperationsMixin, GeneratedSingleDocumentTranslationClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: Union[str, DocumentTranslationApiVersion] = ..., 
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
                deployment_name: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                translate_text_within_image: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def translate(
                self, 
                body: JSON, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                deployment_name: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                translate_text_within_image: Optional[bool] = ..., 
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
        property category_id: Optional[str]
        category_id: str
        deployment_name: Optional[str]
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
                deployment_name: Optional[str] = ..., 
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


    class azure.ai.translation.document.aio.DocumentTranslationClient(DocumentTranslationClientOperationsMixin, GeneratedDocumentTranslationClient): implements AsyncContextManager 

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
                deployment_name: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                prefix: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                suffix: Optional[str] = ..., 
                translate_text_within_image: Optional[bool] = ..., 
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


    class azure.ai.translation.document.aio.SingleDocumentTranslationClient(SingleDocumentTranslationClientOperationsMixin, GeneratedSingleDocumentTranslationClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: Union[str, DocumentTranslationApiVersion] = ..., 
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
                deployment_name: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                translate_text_within_image: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def translate(
                self, 
                body: JSON, 
                *, 
                allow_fallback: Optional[bool] = ..., 
                category: Optional[str] = ..., 
                deployment_name: Optional[str] = ..., 
                source_language: Optional[str] = ..., 
                target_language: str, 
                translate_text_within_image: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...


namespace azure.ai.translation.document.models

    class azure.ai.translation.document.models.BatchOptions(_Model):
        translate_text_within_image: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                translate_text_within_image: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentBatch(_Model):
        source: SourceInput
        storage_type: Optional[Union[str, StorageInputType]]
        targets: list[TranslationTarget]

        @overload
        def __init__(
                self, 
                *, 
                source: SourceInput, 
                storage_type: Optional[Union[str, StorageInputType]] = ..., 
                targets: list[TranslationTarget]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentFilter(_Model):
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
        deployment_name: Optional[str]
        error: Optional[DocumentTranslationError]
        id: str
        image_characters_detected: Optional[int]
        images_charged: Optional[int]
        last_updated_on: datetime
        source_document_url: str
        status: Union[str, Status]
        total_image_scans_failed: Optional[int]
        total_image_scans_succeeded: Optional[int]
        translated_document_url: Optional[str]
        translated_to: str
        translation_progress: float

        @overload
        def __init__(
                self, 
                *, 
                characters_charged: Optional[int] = ..., 
                created_on: datetime, 
                deployment_name: Optional[str] = ..., 
                error: Optional[DocumentTranslationError] = ..., 
                id: str, 
                image_characters_detected: Optional[int] = ..., 
                images_charged: Optional[int] = ..., 
                last_updated_on: datetime, 
                source_document_url: str, 
                status: Union[str, Status], 
                total_image_scans_failed: Optional[int] = ..., 
                total_image_scans_succeeded: Optional[int] = ..., 
                translated_document_url: Optional[str] = ..., 
                translated_to: str, 
                translation_progress: float
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.translation.document.models.DocumentTranslateContent(_Model):
        document: Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]
        glossary: Optional[list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]]

        @overload
        def __init__(
                self, 
                *, 
                document: FileType, 
                glossary: Optional[list[FileType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.DocumentTranslationError(_Model):
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


    class azure.ai.translation.document.models.DocumentTranslationFileFormat(_Model):
        content_types: list[str]
        default_format_version: Optional[str]
        file_extensions: list[str]
        file_format: str
        format_versions: Optional[list[str]]
        type: Optional[Union[str, FileFormatType]]

        @overload
        def __init__(
                self, 
                *, 
                content_types: list[str], 
                default_format_version: Optional[str] = ..., 
                file_extensions: list[str], 
                file_format: str, 
                format_versions: Optional[list[str]] = ..., 
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
        DOCUMENT = "Document"
        GLOSSARY = "Glossary"


    class azure.ai.translation.document.models.InnerTranslationError(_Model):
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


    class azure.ai.translation.document.models.SourceInput(_Model):
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


    class azure.ai.translation.document.models.StartTranslationDetails(_Model):
        inputs: list[DocumentBatch]
        options: Optional[BatchOptions]

        @overload
        def __init__(
                self, 
                *, 
                inputs: list[DocumentBatch], 
                options: Optional[BatchOptions] = ...
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


    class azure.ai.translation.document.models.TranslationStatusSummary(_Model):
        canceled: int
        failed: int
        in_progress: int
        not_yet_started: int
        success: int
        total: int
        total_characters_charged: int
        total_image_scans_failed: Optional[int]
        total_image_scans_succeeded: Optional[int]
        total_images_charged: Optional[int]

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
                total_characters_charged: int, 
                total_image_scans_failed: Optional[int] = ..., 
                total_image_scans_succeeded: Optional[int] = ..., 
                total_images_charged: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.document.models.TranslationStorageSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB = "AzureBlob"


    class azure.ai.translation.document.models.TranslationTarget(GeneratedTranslationTarget):
        property category_id: Optional[str]
        category_id: str
        deployment_name: Optional[str]
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
                deployment_name: Optional[str] = ..., 
                glossaries: Optional[List[TranslationGlossary]] = ..., 
                storage_source: Optional[Union[str, TranslationStorageSource]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


namespace azure.ai.translation.document.types

    class azure.ai.translation.document.types.BatchOptions(TypedDict, total=False):
        key "translateTextWithinImage": bool
        translate_text_within_image: bool


    class azure.ai.translation.document.types.DocumentBatch(TypedDict, total=False):
        key "source": Required[SourceInput]
        key "storageType": Union[str, StorageInputType]
        key "targets": Required[list[TranslationTarget]]
        source: SourceInput
        storage_type: Union[str, StorageInputType]
        targets: list[TranslationTarget]


    class azure.ai.translation.document.types.DocumentFilter(TypedDict, total=False):
        key "prefix": str
        key "suffix": str
        prefix: str
        suffix: str


    class azure.ai.translation.document.types.DocumentStatus(TypedDict, total=False):
        key "characterCharged": int
        key "createdDateTimeUtc": Required[str]
        key "deploymentName": str
        key "error": ForwardRef('DocumentTranslationError', module='types')
        key "id": Required[str]
        key "imageCharacterDetected": int
        key "imageCharged": int
        key "lastActionDateTimeUtc": Required[str]
        key "path": str
        key "progress": Required[float]
        key "sourcePath": Required[str]
        key "status": Required[Union[str, Status]]
        key "to": Required[str]
        key "totalImageScansFailed": int
        key "totalImageScansSucceeded": int
        characters_charged: int
        created_on: str
        deployment_name: str
        error: DocumentTranslationError
        id: str
        image_characters_detected: int
        images_charged: int
        last_updated_on: str
        source_document_url: str
        status: Union[str, Status]
        total_image_scans_failed: int
        total_image_scans_succeeded: int
        translated_document_url: str
        translated_to: str
        translation_progress: float


    class azure.ai.translation.document.types.DocumentTranslateContent(TypedDict, total=False):
        key "document": Required[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]
        document: FileType
        glossary: list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]


    class azure.ai.translation.document.types.DocumentTranslationError(TypedDict, total=False):
        key "code": Required[Union[str, TranslationErrorCode]]
        key "innerError": ForwardRef('InnerTranslationError', module='types')
        key "message": Required[str]
        key "target": str
        code: Union[str, TranslationErrorCode]
        inner_error: InnerTranslationError
        message: str
        target: str


    class azure.ai.translation.document.types.DocumentTranslationFileFormat(TypedDict, total=False):
        key "contentTypes": Required[list[str]]
        key "defaultVersion": str
        key "fileExtensions": Required[list[str]]
        key "format": Required[str]
        key "type": Union[str, FileFormatType]
        content_types: list[str]
        default_format_version: str
        file_extensions: list[str]
        file_format: str
        format_versions: list[str]
        type: Union[str, FileFormatType]
        versions: list[str]


    class azure.ai.translation.document.types.InnerTranslationError(TypedDict, total=False):
        key "code": Required[str]
        key "innerError": ForwardRef('InnerTranslationError', module='types')
        key "message": Required[str]
        key "target": str
        code: str
        inner_error: InnerTranslationError
        message: str
        target: str


    class azure.ai.translation.document.types.SourceInput(TypedDict, total=False):
        key "filter": ForwardRef('DocumentFilter', module='types')
        key "language": str
        key "sourceUrl": Required[str]
        key "storageSource": Union[str, TranslationStorageSource]
        filter: DocumentFilter
        language: str
        source_url: str
        storage_source: Union[str, TranslationStorageSource]


    class azure.ai.translation.document.types.StartTranslationDetails(TypedDict, total=False):
        key "inputs": Required[list[DocumentBatch]]
        key "options": ForwardRef('BatchOptions', module='types')
        inputs: list[DocumentBatch]
        options: BatchOptions


    class azure.ai.translation.document.types.SupportedFileFormats(TypedDict, total=False):
        key "value": Required[list[DocumentTranslationFileFormat]]
        value: list[DocumentTranslationFileFormat]


    class azure.ai.translation.document.types.TranslationGlossary(TypedDict, total=False):
        key "format": Required[str]
        key "glossaryUrl": Required[str]
        key "storageSource": Union[str, TranslationStorageSource]
        key "version": str
        file_format: str
        format_version: str
        glossary_url: str
        storage_source: Union[str, TranslationStorageSource]


    class azure.ai.translation.document.types.TranslationStatus(TypedDict, total=False):
        key "createdDateTimeUtc": Required[str]
        key "error": ForwardRef('DocumentTranslationError', module='types')
        key "id": Required[str]
        key "lastActionDateTimeUtc": Required[str]
        key "status": Required[Union[str, Status]]
        key "summary": Required[TranslationStatusSummary]
        created_on: str
        error: DocumentTranslationError
        id: str
        last_updated_on: str
        status: Union[str, Status]
        summary: TranslationStatusSummary


    class azure.ai.translation.document.types.TranslationStatusSummary(TypedDict, total=False):
        key "cancelled": Required[int]
        key "failed": Required[int]
        key "inProgress": Required[int]
        key "notYetStarted": Required[int]
        key "success": Required[int]
        key "total": Required[int]
        key "totalCharacterCharged": Required[int]
        key "totalImageCharged": int
        key "totalImageScansFailed": int
        key "totalImageScansSucceeded": int
        canceled: int
        failed: int
        in_progress: int
        not_yet_started: int
        success: int
        total: int
        total_characters_charged: int
        total_image_scans_failed: int
        total_image_scans_succeeded: int
        total_images_charged: int


    class azure.ai.translation.document.types.TranslationTarget(TypedDict, total=False):
        key "category": str
        key "deploymentName": str
        key "language": Required[str]
        key "storageSource": Union[str, TranslationStorageSource]
        key "targetUrl": Required[str]
        category: str
        deployment_name: str
        glossaries: list[TranslationGlossary]
        language: str
        storage_source: Union[str, TranslationStorageSource]
        target_url: str


```