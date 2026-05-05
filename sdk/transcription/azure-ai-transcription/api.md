```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.transcription

    class azure.ai.transcription.TranscriptionClient(_TranscriptionClientOperationsMixin): implements ContextManager 

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
        def transcribe(
                self, 
                body: TranscriptionContent, 
                **kwargs: Any
            ) -> TranscriptionResult: ...

        @overload
        def transcribe(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> TranscriptionResult: ...

        @distributed_trace
        def transcribe_from_url(
                self, 
                audio_url: str, 
                *, 
                options: Optional[TranscriptionOptions] = ..., 
                **kwargs: Any
            ) -> TranscriptionResult: ...


namespace azure.ai.transcription.aio

    class azure.ai.transcription.aio.TranscriptionClient(_TranscriptionClientOperationsMixin): implements AsyncContextManager 

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
        async def transcribe(
                self, 
                body: TranscriptionContent, 
                **kwargs: Any
            ) -> TranscriptionResult: ...

        @overload
        async def transcribe(
                self, 
                body: JSON, 
                **kwargs: Any
            ) -> TranscriptionResult: ...

        @distributed_trace_async
        async def transcribe_from_url(
                self, 
                audio_url: str, 
                *, 
                options: Optional[TranscriptionOptions] = ..., 
                **kwargs: Any
            ) -> TranscriptionResult: ...


namespace azure.ai.transcription.models

    class azure.ai.transcription.models.ChannelCombinedPhrases(_Model):
        channel: Optional[int]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                channel: Optional[int] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.EnhancedModeProperties(_EnhancedModeProperties):
        prompt: list[str]
        target_language: str
        task: str

        def __init__(
                self, 
                *, 
                prompt: Optional[list[str]] = ..., 
                target_language: Optional[str] = ..., 
                task: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def as_dict(
                self, 
                *, 
                exclude_readonly: bool = False
            ) -> dict[str, Any]: ...


    class azure.ai.transcription.models.PhraseListProperties(_Model):
        biasing_weight: Optional[float]
        phrases: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                biasing_weight: Optional[float] = ..., 
                phrases: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.ProfanityFilterMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MASKED = "Masked"
        NONE = "None"
        REMOVED = "Removed"
        TAGS = "Tags"


    class azure.ai.transcription.models.TranscribedPhrase(_Model):
        channel: Optional[int]
        confidence: float
        duration_milliseconds: int
        locale: Optional[str]
        offset_milliseconds: int
        speaker: Optional[int]
        text: str
        words: Optional[list[TranscribedWord]]

        @overload
        def __init__(
                self, 
                *, 
                channel: Optional[int] = ..., 
                confidence: float, 
                duration_milliseconds: int, 
                locale: Optional[str] = ..., 
                offset_milliseconds: int, 
                speaker: Optional[int] = ..., 
                text: str, 
                words: Optional[list[TranscribedWord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.TranscribedWord(_Model):
        duration_milliseconds: int
        offset_milliseconds: int
        text: str

        @overload
        def __init__(
                self, 
                *, 
                duration_milliseconds: int, 
                offset_milliseconds: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.TranscriptionContent(_Model):
        audio: Optional[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]
        definition: TranscriptionOptions

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[FileType] = ..., 
                definition: TranscriptionOptions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.TranscriptionDiarizationOptions(_Model):
        enabled: Optional[bool]
        max_speakers: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_speakers: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.TranscriptionOptions(_Model):
        active_channels: Optional[list[int]]
        audio_url: Optional[str]
        diarization_options: Optional[TranscriptionDiarizationOptions]
        enhanced_mode: Optional[EnhancedModeProperties]
        locales: Optional[list[str]]
        models: Optional[dict[str, str]]
        phrase_list: Optional[PhraseListProperties]
        profanity_filter_mode: Optional[Union[str, ProfanityFilterMode]]

        @overload
        def __init__(
                self, 
                *, 
                active_channels: Optional[list[int]] = ..., 
                audio_url: Optional[str] = ..., 
                diarization_options: Optional[TranscriptionDiarizationOptions] = ..., 
                enhanced_mode: Optional[EnhancedModeProperties] = ..., 
                locales: Optional[list[str]] = ..., 
                models: Optional[dict[str, str]] = ..., 
                phrase_list: Optional[PhraseListProperties] = ..., 
                profanity_filter_mode: Optional[Union[str, ProfanityFilterMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.transcription.models.TranscriptionResult(_Model):
        combined_phrases: list[ChannelCombinedPhrases]
        duration_milliseconds: int
        phrases: list[TranscribedPhrase]

        @overload
        def __init__(
                self, 
                *, 
                combined_phrases: list[ChannelCombinedPhrases], 
                duration_milliseconds: int, 
                phrases: list[TranscribedPhrase]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```