```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.contentsafety

    class azure.ai.contentsafety.BlocklistClient(BlocklistClientOperationsMixin): implements ContextManager 

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
                options: JSON, 
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
                options: JSON, 
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
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace
        def get_text_blocklist_item(
                self, 
                blocklist_name: str, 
                blocklist_item_id: str, 
                *, 
                stream: Optional[bool] = ..., 
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
            ) -> Iterable[TextBlocklistItem]: ...

        @distributed_trace
        def list_text_blocklists(self, **kwargs: Any) -> Iterable[TextBlocklist]: ...

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
                options: JSON, 
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


    class azure.ai.contentsafety.ContentSafetyClient(ContentSafetyClientOperationsMixin): implements ContextManager 

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
                options: JSON, 
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
                options: JSON, 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.contentsafety.aio

    class azure.ai.contentsafety.aio.BlocklistClient(BlocklistClientOperationsMixin): implements AsyncContextManager 

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
                options: JSON, 
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
                options: JSON, 
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
                *, 
                stream: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TextBlocklist: ...

        @distributed_trace_async
        async def get_text_blocklist_item(
                self, 
                blocklist_name: str, 
                blocklist_item_id: str, 
                *, 
                stream: Optional[bool] = ..., 
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
            ) -> AsyncIterable[TextBlocklistItem]: ...

        @distributed_trace
        def list_text_blocklists(self, **kwargs: Any) -> AsyncIterable[TextBlocklist]: ...

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
                options: JSON, 
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


    class azure.ai.contentsafety.aio.ContentSafetyClient(ContentSafetyClientOperationsMixin): implements AsyncContextManager 

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
                options: JSON, 
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
                options: JSON, 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.contentsafety.models

    class azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsOptions(Model):
        blocklist_items: List[TextBlocklistItem]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_items: List[TextBlocklistItem]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.AddOrUpdateTextBlocklistItemsResult(Model):
        blocklist_items: List[TextBlocklistItem]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_items: List[TextBlocklistItem]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.AnalyzeImageOptions(Model):
        categories: Optional[List[Union[str, ImageCategory]]]
        image: ImageData
        output_type: Optional[Union[str, AnalyzeImageOutputType]]

        @overload
        def __init__(
                self, 
                *, 
                categories: Optional[List[Union[str, ImageCategory]]] = ..., 
                image: ImageData, 
                output_type: Optional[Union[str, AnalyzeImageOutputType]] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.AnalyzeImageOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR_SEVERITY_LEVELS = "FourSeverityLevels"


    class azure.ai.contentsafety.models.AnalyzeImageResult(Model):
        categories_analysis: List[ImageCategoriesAnalysis]

        @overload
        def __init__(
                self, 
                *, 
                categories_analysis: List[ImageCategoriesAnalysis]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.AnalyzeTextOptions(Model):
        blocklist_names: Optional[List[str]]
        categories: Optional[List[Union[str, TextCategory]]]
        halt_on_blocklist_hit: Optional[bool]
        output_type: Optional[Union[str, AnalyzeTextOutputType]]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                blocklist_names: Optional[List[str]] = ..., 
                categories: Optional[List[Union[str, TextCategory]]] = ..., 
                halt_on_blocklist_hit: Optional[bool] = ..., 
                output_type: Optional[Union[str, AnalyzeTextOutputType]] = ..., 
                text: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.AnalyzeTextOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EIGHT_SEVERITY_LEVELS = "EightSeverityLevels"
        FOUR_SEVERITY_LEVELS = "FourSeverityLevels"


    class azure.ai.contentsafety.models.AnalyzeTextResult(Model):
        blocklists_match: Optional[List[TextBlocklistMatch]]
        categories_analysis: List[TextCategoriesAnalysis]

        @overload
        def __init__(
                self, 
                *, 
                blocklists_match: Optional[List[TextBlocklistMatch]] = ..., 
                categories_analysis: List[TextCategoriesAnalysis]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.ImageCategoriesAnalysis(Model):
        category: Union[str, ImageCategory]
        severity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, ImageCategory], 
                severity: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.ImageCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HATE = "Hate"
        SELF_HARM = "SelfHarm"
        SEXUAL = "Sexual"
        VIOLENCE = "Violence"


    class azure.ai.contentsafety.models.ImageData(Model):
        blob_url: Optional[str]
        content: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                blob_url: Optional[str] = ..., 
                content: Optional[bytes] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.RemoveTextBlocklistItemsOptions(Model):
        blocklist_item_ids: List[str]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_item_ids: List[str]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.TextBlocklist(Model):
        blocklist_name: str
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blocklist_name: str, 
                description: Optional[str] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.TextBlocklistItem(Model):
        blocklist_item_id: str
        description: Optional[str]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                text: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.TextBlocklistMatch(Model):
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
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.TextCategoriesAnalysis(Model):
        category: Union[str, TextCategory]
        severity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, TextCategory], 
                severity: Optional[int] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.contentsafety.models.TextCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HATE = "Hate"
        SELF_HARM = "SelfHarm"
        SEXUAL = "Sexual"
        VIOLENCE = "Violence"


```