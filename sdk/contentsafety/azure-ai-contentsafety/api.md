```py
namespace azure.ai.contentsafety

    class azure.ai.contentsafety.BlocklistClient(_BlocklistClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: AddOrUpdateTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        @overload
        def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: AddOrUpdateTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        @overload
        def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        def close(self) -> None: ...

        @overload
        def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: TextBlocklist, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @overload
        def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: TextBlocklist, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @overload
        def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace
        def delete_text_blocklist(
                self, 
                blocklist_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_text_blocklist(
                self, 
                blocklist_name: str, 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace
        def get_text_blocklist_item(
                self, 
                blocklist_name: str, 
                blocklist_item_id: str, 
                **kwargs: Any
            ) -> TextBlocklistItem: ...

        @distributed_trace
        def list_text_blocklist_items(
                self, 
                blocklist_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TextBlocklistItem]: ...

        @distributed_trace
        def list_text_blocklists(self, **kwargs: Any) -> ItemPaged[TextBlocklist]: ...

        @overload
        def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: RemoveTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: RemoveTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.contentsafety.ContentProvenanceClient(_ContentProvenanceClientOperationsMixin): implements ContextManager 

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
        def begin_detect(
                self, 
                options: DetectProvenanceOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DetectProvenanceResult]: ...

        @overload
        def begin_detect(
                self, 
                options: DetectProvenanceOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DetectProvenanceResult]: ...

        @overload
        def begin_detect(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DetectProvenanceResult]: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> ProvenanceDetectOperation: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.contentsafety.ContentSafetyClient(_ContentSafetyClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def analyze_image(
                self, 
                options: AnalyzeImageOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        def analyze_image(
                self, 
                options: AnalyzeImageOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        def analyze_image(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        def analyze_text(
                self, 
                options: AnalyzeTextOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        def analyze_text(
                self, 
                options: AnalyzeTextOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        def analyze_text(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        def close(self) -> None: ...

        @overload
        def detect_text_protected_material(
                self, 
                options: DetectTextProtectedMaterialOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        @overload
        def detect_text_protected_material(
                self, 
                options: DetectTextProtectedMaterialOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        @overload
        def detect_text_protected_material(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def shield_prompt(
                self, 
                options: ShieldPromptOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...

        @overload
        def shield_prompt(
                self, 
                options: ShieldPromptOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...

        @overload
        def shield_prompt(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...


namespace azure.ai.contentsafety.aio

    class azure.ai.contentsafety.aio.BlocklistClient(_BlocklistClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: AddOrUpdateTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        @overload
        async def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: AddOrUpdateTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        @overload
        async def add_or_update_blocklist_items(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AddOrUpdateTextBlocklistItemsResult: ...

        async def close(self) -> None: ...

        @overload
        async def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: TextBlocklist, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @overload
        async def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: TextBlocklist, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @overload
        async def create_or_update_text_blocklist(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace_async
        async def delete_text_blocklist(
                self, 
                blocklist_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_text_blocklist(
                self, 
                blocklist_name: str, 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace_async
        async def get_text_blocklist_item(
                self, 
                blocklist_name: str, 
                blocklist_item_id: str, 
                **kwargs: Any
            ) -> TextBlocklistItem: ...

        @distributed_trace
        def list_text_blocklist_items(
                self, 
                blocklist_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TextBlocklistItem]: ...

        @distributed_trace
        def list_text_blocklists(self, **kwargs: Any) -> AsyncItemPaged[TextBlocklist]: ...

        @overload
        async def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: RemoveTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: RemoveTextBlocklistItemsOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_blocklist_items(
                self, 
                blocklist_name: str, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.contentsafety.aio.ContentProvenanceClient(_ContentProvenanceClientOperationsMixin): implements AsyncContextManager 

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
        async def begin_detect(
                self, 
                options: DetectProvenanceOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DetectProvenanceResult]: ...

        @overload
        async def begin_detect(
                self, 
                options: DetectProvenanceOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DetectProvenanceResult]: ...

        @overload
        async def begin_detect(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DetectProvenanceResult]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_operation_status(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> ProvenanceDetectOperation: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.contentsafety.aio.ContentSafetyClient(_ContentSafetyClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def analyze_image(
                self, 
                options: AnalyzeImageOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        async def analyze_image(
                self, 
                options: AnalyzeImageOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        async def analyze_image(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeImageResult: ...

        @overload
        async def analyze_text(
                self, 
                options: AnalyzeTextOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        async def analyze_text(
                self, 
                options: AnalyzeTextOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        @overload
        async def analyze_text(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AnalyzeTextResult: ...

        async def close(self) -> None: ...

        @overload
        async def detect_text_protected_material(
                self, 
                options: DetectTextProtectedMaterialOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        @overload
        async def detect_text_protected_material(
                self, 
                options: DetectTextProtectedMaterialOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        @overload
        async def detect_text_protected_material(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DetectTextProtectedMaterialResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def shield_prompt(
                self, 
                options: ShieldPromptOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...

        @overload
        async def shield_prompt(
                self, 
                options: ShieldPromptOptions, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...

        @overload
        async def shield_prompt(
                self, 
                options: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ShieldPromptResult: ...


namespace azure.ai.contentsafety.models

    class azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsOptions(_Model):
        blocklist_items: list[TextBlocklistItem]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_items: list[TextBlocklistItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsResult(_Model):
        blocklist_items: list[TextBlocklistItem]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_items: list[TextBlocklistItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.AnalyzeImageOptions(_Model):
        categories: Optional[list[Union[str, ImageCategory]]]
        image: ImageData
        output_type: Optional[Union[str, AnalyzeImageOutputType]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[list[Union[str, ImageCategory]]] = ..., 
                image: ImageData, 
                output_type: Optional[Union[str, AnalyzeImageOutputType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.AnalyzeImageOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR_SEVERITY_LEVELS = "FourSeverityLevels"


    class azure.ai.contentsafety.models.AnalyzeImageResult(_Model):
        categories_analysis: list[ImageCategoriesAnalysis]

        @overload
        def __init__(
                self, 
                *, 
                categories_analysis: list[ImageCategoriesAnalysis]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.AnalyzeTextOptions(_Model):
        blocklist_names: Optional[list[str]]
        categories: Optional[list[Union[str, TextCategory]]]
        halt_on_blocklist_hit: Optional[bool]
        output_type: Optional[Union[str, AnalyzeTextOutputType]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                blocklist_names: Optional[list[str]] = ..., 
                categories: Optional[list[Union[str, TextCategory]]] = ..., 
                halt_on_blocklist_hit: Optional[bool] = ..., 
                output_type: Optional[Union[str, AnalyzeTextOutputType]] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.AnalyzeTextOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EIGHT_SEVERITY_LEVELS = "EightSeverityLevels"
        FOUR_SEVERITY_LEVELS = "FourSeverityLevels"


    class azure.ai.contentsafety.models.AnalyzeTextResult(_Model):
        blocklists_match: Optional[list[TextBlocklistMatch]]
        categories_analysis: list[TextCategoriesAnalysis]

        @overload
        def __init__(
                self, 
                *, 
                blocklists_match: Optional[list[TextBlocklistMatch]] = ..., 
                categories_analysis: list[TextCategoriesAnalysis]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectOutcome(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_PROVENANCE_DETECTED = "NoProvenanceDetected"
        PROVENANCE_DETECTED = "ProvenanceDetected"


    class azure.ai.contentsafety.models.DetectProvenanceOptions(_Model):
        content: ProvenanceContent

        @overload
        def __init__(
                self, 
                *, 
                content: ProvenanceContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectProvenanceResult(_Model):
        outcome: Union[str, DetectOutcome]
        results: Optional[list[DetectedProvenance]]

        @overload
        def __init__(
                self, 
                *, 
                outcome: Union[str, DetectOutcome], 
                results: Optional[list[DetectedProvenance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectTextProtectedMaterialOptions(_Model):
        text: str

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectTextProtectedMaterialResult(_Model):
        protected_material_analysis: TextProtectedMaterialAnalysisResult

        @overload
        def __init__(
                self, 
                *, 
                protected_material_analysis: TextProtectedMaterialAnalysisResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectedProvenance(_Model):
        model_name: Optional[str]
        provider: Optional[str]
        timestamp: Optional[datetime]
        type: Optional[Union[str, DetectedProvenanceType]]

        @overload
        def __init__(
                self, 
                *, 
                model_name: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                type: Optional[Union[str, DetectedProvenanceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.DetectedProvenanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        C2_PA = "C2PA"
        WATERMARK = "Watermark"


    class azure.ai.contentsafety.models.DocumentInjectionAnalysisResult(_Model):
        attack_detected: bool

        @overload
        def __init__(
                self, 
                *, 
                attack_detected: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ImageCategoriesAnalysis(_Model):
        category: Union[str, ImageCategory]
        severity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, ImageCategory], 
                severity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ImageCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HATE = "Hate"
        SELF_HARM = "SelfHarm"
        SEXUAL = "Sexual"
        VIOLENCE = "Violence"


    class azure.ai.contentsafety.models.ImageData(_Model):
        blob_url: Optional[str]
        content: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                blob_url: Optional[str] = ..., 
                content: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.contentsafety.models.ProvenanceContent(_Model):
        uri: str

        @overload
        def __init__(
                self, 
                *, 
                uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ProvenanceDetectOperation(_Model):
        created_at: Optional[datetime]
        error: Optional[ODataV4Format]
        id: str
        kind: Union[str, ProvenanceOperationKind]
        last_updated_at: Optional[datetime]
        result: Optional[DetectProvenanceResult]
        status: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ODataV4Format] = ..., 
                id: str, 
                result: Optional[DetectProvenanceResult] = ..., 
                status: Union[str, OperationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ProvenanceOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETECT = "Detect"


    class azure.ai.contentsafety.models.RemoveTextBlocklistItemsOptions(_Model):
        blocklist_item_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_item_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ShieldPromptOptions(_Model):
        documents: Optional[list[str]]
        user_prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                documents: Optional[list[str]] = ..., 
                user_prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.ShieldPromptResult(_Model):
        documents_analysis: Optional[list[DocumentInjectionAnalysisResult]]
        user_prompt_analysis: Optional[UserPromptInjectionAnalysisResult]

        @overload
        def __init__(
                self, 
                *, 
                documents_analysis: Optional[list[DocumentInjectionAnalysisResult]] = ..., 
                user_prompt_analysis: Optional[UserPromptInjectionAnalysisResult] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.TextBlocklist(_Model):
        blocklist_name: str
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_name: str, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.TextBlocklistItem(_Model):
        blocklist_item_id: str
        description: Optional[str]
        is_regex: Optional[bool]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_regex: Optional[bool] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.TextBlocklistMatch(_Model):
        blocklist_item_id: str
        blocklist_item_text: str
        blocklist_name: str

        @overload
        def __init__(
                self, 
                *, 
                blocklist_item_id: str, 
                blocklist_item_text: str, 
                blocklist_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.TextCategoriesAnalysis(_Model):
        category: Union[str, TextCategory]
        severity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, TextCategory], 
                severity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.TextCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HATE = "Hate"
        SELF_HARM = "SelfHarm"
        SEXUAL = "Sexual"
        VIOLENCE = "Violence"


    class azure.ai.contentsafety.models.TextProtectedMaterialAnalysisResult(_Model):
        detected: bool

        @overload
        def __init__(
                self, 
                *, 
                detected: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.contentsafety.models.UserPromptInjectionAnalysisResult(_Model):
        attack_detected: bool

        @overload
        def __init__(
                self, 
                *, 
                attack_detected: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.contentsafety.types

    class azure.ai.contentsafety.types.AddOrUpdateTextBlocklistItemsOptions(TypedDict, total=False):
        key "blocklistItems": Required[list[TextBlocklistItem]]
        blocklist_items: list[TextBlocklistItem]


    class azure.ai.contentsafety.types.AnalyzeImageOptions(TypedDict, total=False):
        key "image": Required[ImageData]
        key "outputType": Union[str, AnalyzeImageOutputType]
        categories: list[Union[str, ImageCategory]]
        image: ImageData
        output_type: Union[str, AnalyzeImageOutputType]


    class azure.ai.contentsafety.types.AnalyzeTextOptions(TypedDict, total=False):
        key "haltOnBlocklistHit": bool
        key "outputType": Union[str, AnalyzeTextOutputType]
        key "text": Required[str]
        blocklistNames: list[str]
        blocklist_names: list[str]
        categories: list[Union[str, TextCategory]]
        halt_on_blocklist_hit: bool
        output_type: Union[str, AnalyzeTextOutputType]
        text: str


    class azure.ai.contentsafety.types.DetectProvenanceOptions(TypedDict, total=False):
        key "content": Required[ProvenanceContent]
        content: ProvenanceContent


    class azure.ai.contentsafety.types.DetectTextProtectedMaterialOptions(TypedDict, total=False):
        key "text": Required[str]
        text: str


    class azure.ai.contentsafety.types.ImageData(TypedDict, total=False):
        key "blobUrl": str
        key "content": str
        blob_url: str
        content: str


    class azure.ai.contentsafety.types.ProvenanceContent(TypedDict, total=False):
        key "uri": Required[str]
        uri: str


    class azure.ai.contentsafety.types.RemoveTextBlocklistItemsOptions(TypedDict, total=False):
        key "blocklistItemIds": Required[list[str]]
        blocklist_item_ids: list[str]


    class azure.ai.contentsafety.types.ShieldPromptOptions(TypedDict, total=False):
        key "userPrompt": str
        documents: list[str]
        user_prompt: str


    class azure.ai.contentsafety.types.TextBlocklist(TypedDict, total=False):
        key "blocklistName": Required[str]
        key "description": str
        blocklist_name: str
        description: str


    class azure.ai.contentsafety.types.TextBlocklistItem(TypedDict, total=False):
        key "blocklistItemId": Required[str]
        key "description": str
        key "isRegex": bool
        key "text": Required[str]
        blocklist_item_id: str
        description: str
        is_regex: bool
        text: str


```