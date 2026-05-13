```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.translation.text

    class azure.ai.translation.text.TextTranslationClient(ServiceClientGenerated): implements ContextManager 

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: TokenCredential, 
                endpoint: Optional[str] = ..., 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: AzureKeyCredential, 
                endpoint: Optional[str] = ..., 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: Union[AzureKeyCredential, TokenCredential] = ..., 
                endpoint: str, 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def close(self) -> None: ...

        def get_supported_languages(
                self, 
                *, 
                accept_language: Optional[str] = ..., 
                client_trace_id: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> GetSupportedLanguagesResult: ...

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
                body: List[str], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_language: Optional[str] = ..., 
                to_language: List[str], 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        def translate(
                self, 
                body: List[TranslateInputItem], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        def translate(
                self, 
                body: JSON, 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        def transliterate(
                self, 
                body: List[str], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...

        @overload
        def transliterate(
                self, 
                body: List[InputTextItem], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...

        @overload
        def transliterate(
                self, 
                body: JSON, 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...


namespace azure.ai.translation.text.aio

    class azure.ai.translation.text.aio.TextTranslationClient(ServiceClientGenerated): implements AsyncContextManager 

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: AsyncTokenCredential, 
                endpoint: Optional[str] = ..., 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: AzureKeyCredential, 
                endpoint: Optional[str] = ..., 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                api_version: str = "2025-10-01-preview", 
                audience: Optional[str] = ..., 
                credential: Union[AzureKeyCredential, AsyncTokenCredential] = ..., 
                endpoint: str, 
                region: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        async def close(self) -> None: ...

        async def get_supported_languages(
                self, 
                *, 
                accept_language: Optional[str] = ..., 
                client_trace_id: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> GetSupportedLanguagesResult: ...

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
                body: List[str], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_language: Optional[str] = ..., 
                to_language: List[str], 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        async def translate(
                self, 
                body: List[TranslateInputItem], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        async def translate(
                self, 
                body: JSON, 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[TranslatedTextItem]: ...

        @overload
        async def transliterate(
                self, 
                body: List[str], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...

        @overload
        async def transliterate(
                self, 
                body: List[InputTextItem], 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...

        @overload
        async def transliterate(
                self, 
                body: JSON, 
                *, 
                client_trace_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                from_script: str, 
                language: str, 
                to_script: str, 
                **kwargs: Any
            ) -> List[TransliteratedText]: ...


namespace azure.ai.translation.text.models

    class azure.ai.translation.text.models.DetectedLanguage(_Model):
        language: str
        score: float

        @overload
        def __init__(
                self, 
                *, 
                language: str, 
                score: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.ErrorDetails(_Model):
        code: str
        message: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.ErrorResponse(_Model):
        error: ErrorDetails

        @overload
        def __init__(
                self, 
                *, 
                error: ErrorDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.GetSupportedLanguagesResult(_Model):
        models: Optional[list[str]]
        translation: Optional[dict[str, TranslationLanguage]]
        transliteration: Optional[dict[str, TransliterationLanguage]]


    class azure.ai.translation.text.models.InputTextItem(_Model):
        text: str

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.LanguageDirectionality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEFT_TO_RIGHT = "ltr"
        RIGHT_TO_LEFT = "rtl"


    class azure.ai.translation.text.models.LanguageScript(_Model):
        code: str
        dir: Union[str, LanguageDirectionality]
        name: str
        native_name: str

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                dir: Union[str, LanguageDirectionality], 
                name: str, 
                native_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.ProfanityAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        MARKED = "Marked"
        NO_ACTION = "NoAction"


    class azure.ai.translation.text.models.ProfanityMarker(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASTERISK = "Asterisk"
        TAG = "Tag"


    class azure.ai.translation.text.models.ReferenceTextPair(_Model):
        source: str
        target: str

        @overload
        def __init__(
                self, 
                *, 
                source: str, 
                target: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TextType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML = "Html"
        PLAIN = "Plain"


    class azure.ai.translation.text.models.TranslateBody(_Model):
        inputs: list[TranslateInputItem]

        @overload
        def __init__(
                self, 
                *, 
                inputs: list[TranslateInputItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TranslateInputItem(_Model):
        language: Optional[str]
        script: Optional[str]
        targets: list[TranslationTarget]
        text: str
        text_type: Optional[Union[str, TextType]]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                script: Optional[str] = ..., 
                targets: list[TranslationTarget], 
                text: str, 
                text_type: Optional[Union[str, TextType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TranslatedTextItem(_Model):
        detected_language: Optional[DetectedLanguage]
        translations: list[TranslationText]

        @overload
        def __init__(
                self, 
                *, 
                detected_language: Optional[DetectedLanguage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TranslationLanguage(_Model):
        dir: Union[str, LanguageDirectionality]
        models: list[str]
        name: str
        native_name: str

        @overload
        def __init__(
                self, 
                *, 
                dir: Union[str, LanguageDirectionality], 
                name: str, 
                native_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TranslationResult(_Model):
        value: list[TranslatedTextItem]


    class azure.ai.translation.text.models.TranslationTarget(_Model):
        adaptive_dataset_id: Optional[str]
        allow_fallback: Optional[bool]
        deployment_name: Optional[str]
        gender: Optional[str]
        grade: Optional[str]
        language: str
        profanity_action: Optional[Union[str, ProfanityAction]]
        profanity_marker: Optional[Union[str, ProfanityMarker]]
        reference_text_pairs: Optional[list[ReferenceTextPair]]
        script: Optional[str]
        tone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                adaptive_dataset_id: Optional[str] = ..., 
                allow_fallback: Optional[bool] = ..., 
                deployment_name: Optional[str] = ..., 
                gender: Optional[str] = ..., 
                grade: Optional[str] = ..., 
                language: str, 
                profanity_action: Optional[Union[str, ProfanityAction]] = ..., 
                profanity_marker: Optional[Union[str, ProfanityMarker]] = ..., 
                reference_text_pairs: Optional[list[ReferenceTextPair]] = ..., 
                script: Optional[str] = ..., 
                tone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TranslationText(_Model):
        instruction_tokens: Optional[int]
        language: str
        response_tokens: Optional[int]
        source_characters: Optional[int]
        source_tokens: Optional[int]
        target_tokens: Optional[int]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                instruction_tokens: Optional[int] = ..., 
                language: str, 
                response_tokens: Optional[int] = ..., 
                source_characters: Optional[int] = ..., 
                source_tokens: Optional[int] = ..., 
                target_tokens: Optional[int] = ..., 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TransliterableScript(LanguageScript):
        code: str
        dir: Union[str, LanguageDirectionality]
        name: str
        native_name: str
        to_scripts: list[LanguageScript]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                dir: Union[str, LanguageDirectionality], 
                name: str, 
                native_name: str, 
                to_scripts: list[LanguageScript]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TransliterateBody(_Model):
        inputs: list[InputTextItem]

        @overload
        def __init__(
                self, 
                *, 
                inputs: list[InputTextItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TransliterateResult(_Model):
        value: list[TransliteratedText]


    class azure.ai.translation.text.models.TransliteratedText(_Model):
        script: str
        text: str

        @overload
        def __init__(
                self, 
                *, 
                script: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.translation.text.models.TransliterationLanguage(_Model):
        name: str
        native_name: str
        scripts: list[TransliterableScript]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                native_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```