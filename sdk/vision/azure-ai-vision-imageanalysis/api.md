```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.vision.imageanalysis

    class azure.ai.vision.imageanalysis.ImageAnalysisClient(ImageAnalysisClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def analyze(
                self, 
                image_data: bytes, 
                visual_features: List[VisualFeatures], 
                *, 
                gender_neutral_caption: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                smart_crops_aspect_ratios: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> ImageAnalysisResult: ...

        @distributed_trace
        def analyze_from_url(
                self, 
                image_url: str, 
                visual_features: List[VisualFeatures], 
                *, 
                gender_neutral_caption: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                smart_crops_aspect_ratios: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> ImageAnalysisResult: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.ai.vision.imageanalysis.aio

    class azure.ai.vision.imageanalysis.aio.ImageAnalysisClient(ImageAnalysisClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def analyze(
                self, 
                image_data: bytes, 
                visual_features: List[VisualFeatures], 
                *, 
                gender_neutral_caption: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                smart_crops_aspect_ratios: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> ImageAnalysisResult: ...

        @distributed_trace_async
        async def analyze_from_url(
                self, 
                image_url: str, 
                visual_features: List[VisualFeatures], 
                *, 
                gender_neutral_caption: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                model_version: Optional[str] = ..., 
                smart_crops_aspect_ratios: Optional[List[float]] = ..., 
                **kwargs: Any
            ) -> ImageAnalysisResult: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.ai.vision.imageanalysis.models

    class azure.ai.vision.imageanalysis.models.CaptionResult(Model):
        confidence: float
        text: str

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                text: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.CropRegion(Model):
        aspect_ratio: float
        bounding_box: ImageBoundingBox

        @overload
        def __init__(
                self, 
                *, 
                aspect_ratio: float, 
                bounding_box: ImageBoundingBox
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DenseCaption(Model):
        bounding_box: ImageBoundingBox
        confidence: float
        text: str

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: ImageBoundingBox, 
                confidence: float, 
                text: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DenseCaptionsResult(Model):
        list: List[DenseCaption]

        @overload
        def __init__(
                self, 
                *, 
                list: List[DenseCaption]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DetectedObject(Model):
        bounding_box: ImageBoundingBox
        tags: List[DetectedTag]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: ImageBoundingBox, 
                tags: List[DetectedTag]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DetectedPerson(Model):
        bounding_box: ImageBoundingBox
        confidence: float


    class azure.ai.vision.imageanalysis.models.DetectedTag(Model):
        confidence: float
        name: str

        @overload
        def __init__(
                self, 
                *, 
                confidence: float, 
                name: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DetectedTextBlock(Model):
        lines: List[DetectedTextLine]

        @overload
        def __init__(
                self, 
                *, 
                lines: List[DetectedTextLine]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DetectedTextLine(Model):
        bounding_polygon: List[ImagePoint]
        text: str
        words: List[DetectedTextWord]

        @overload
        def __init__(
                self, 
                *, 
                bounding_polygon: List[ImagePoint], 
                text: str, 
                words: List[DetectedTextWord]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.DetectedTextWord(Model):
        bounding_polygon: List[ImagePoint]
        confidence: float
        text: str

        @overload
        def __init__(
                self, 
                *, 
                bounding_polygon: List[ImagePoint], 
                confidence: float, 
                text: str
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ImageAnalysisResult(Model):
        caption: Optional[CaptionResult]
        dense_captions: Optional[DenseCaptionsResult]
        metadata: ImageMetadata
        model_version: str
        objects: Optional[ObjectsResult]
        people: Optional[PeopleResult]
        read: Optional[ReadResult]
        smart_crops: Optional[SmartCropsResult]
        tags: Optional[TagsResult]

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[CaptionResult] = ..., 
                dense_captions: Optional[DenseCaptionsResult] = ..., 
                metadata: ImageMetadata, 
                model_version: str, 
                objects: Optional[ObjectsResult] = ..., 
                people: Optional[PeopleResult] = ..., 
                read: Optional[ReadResult] = ..., 
                smart_crops: Optional[SmartCropsResult] = ..., 
                tags: Optional[TagsResult] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ImageBoundingBox(Model):
        height: int
        width: int
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                height: int, 
                width: int, 
                x: int, 
                y: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ImageMetadata(Model):
        height: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                height: int, 
                width: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ImagePoint(Model):
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                x: int, 
                y: int
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ObjectsResult(Model):
        list: List[DetectedObject]

        @overload
        def __init__(
                self, 
                *, 
                list: List[DetectedObject]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.PeopleResult(Model):
        list: List[DetectedPerson]

        @overload
        def __init__(
                self, 
                *, 
                list: List[DetectedPerson]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.ReadResult(Model):
        blocks: List[DetectedTextBlock]

        @overload
        def __init__(
                self, 
                *, 
                blocks: List[DetectedTextBlock]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.SmartCropsResult(Model):
        list: List[CropRegion]

        @overload
        def __init__(
                self, 
                *, 
                list: List[CropRegion]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.TagsResult(Model):
        list: List[DetectedTag]

        @overload
        def __init__(
                self, 
                *, 
                list: List[DetectedTag]
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.ai.vision.imageanalysis.models.VisualFeatures(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPTION = "caption"
        DENSE_CAPTIONS = "denseCaptions"
        OBJECTS = "objects"
        PEOPLE = "people"
        READ = "read"
        SMART_CROPS = "smartCrops"
        TAGS = "tags"


```