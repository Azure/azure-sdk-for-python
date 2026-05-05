```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.ai.voicelive.aio

    def azure.ai.voicelive.aio.connect(
            *, 
            agent_config: Optional[AgentSessionConfig] = ..., 
            api_version: str = "2026-01-01-preview", 
            connection_options: Optional[WebsocketConnectionOptions] = ..., 
            credential: Union[AzureKeyCredential, AsyncTokenCredential], 
            endpoint: str, 
            headers: Optional[Mapping[str, Any]] = ..., 
            model: Optional[str] = ..., 
            query: Optional[Mapping[str, Any]] = ..., 
            **kwargs: Any
        ) -> AbstractAsyncContextManager[VoiceLiveConnection]: ...


    class azure.ai.voicelive.aio.AgentSessionConfig(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": NotRequired[str]
        key "authentication_identity_client_id": NotRequired[str]
        key "conversation_id": NotRequired[str]
        key "foundry_resource_override": NotRequired[str]
        key "project_name": Required[str]


    class azure.ai.voicelive.aio.ConnectionClosed(ConnectionError):

        def __init__(
                self, 
                code: int, 
                reason: str
            ) -> None: ...


    class azure.ai.voicelive.aio.ConnectionError(AzureError):


    class azure.ai.voicelive.aio.ConversationItemResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def create(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Union[ConversationRequestItem, Mapping[str, Any]], 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        async def delete(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        async def retrieve(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        async def truncate(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...


    class azure.ai.voicelive.aio.ConversationResource:
        item: ConversationItemResource

        def __init__(self, connection: VoiceLiveConnection) -> None: ...


    class azure.ai.voicelive.aio.InputAudioBufferResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def append(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        async def clear(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        async def commit(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...


    class azure.ai.voicelive.aio.OutputAudioBufferResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def clear(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...


    class azure.ai.voicelive.aio.ResponseResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def cancel(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        async def create(
                self, 
                *, 
                additional_instructions: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                response: Optional[Union[ResponseCreateParams, Mapping[str, Any]]] = ...
            ) -> None: ...


    class azure.ai.voicelive.aio.SessionResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def update(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: Union[Mapping[str, Any], RequestSession]
            ) -> None: ...


    class azure.ai.voicelive.aio.TranscriptionSessionResource:

        def __init__(self, connection: VoiceLiveConnection) -> None: ...

        async def update(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: Mapping[str, Any]
            ) -> None: ...


    class azure.ai.voicelive.aio.VoiceLiveConnection:
        conversation: ConversationResource
        input_audio_buffer: InputAudioBufferResource
        output_audio_buffer: OutputAudioBufferResource
        response: ResponseResource
        session: SessionResource
        transcription_session: TranscriptionSessionResource

        async def __aiter__(self) -> AsyncIterator[ServerEvent]: ...

        def __init__(
                self, 
                client_session: ClientSession, 
                ws: ClientWebSocketResponse
            ) -> None: ...

        async def close(
                self, 
                *, 
                code: int = 1000, 
                reason: str = ""
            ) -> None: ...

        async def recv(self) -> ServerEvent: ...

        async def recv_bytes(self) -> bytes: ...

        async def send(self, event: Union[Mapping[str, Any], ClientEvent]) -> None: ...


    class azure.ai.voicelive.aio.WebsocketConnectionOptions(TypedDict, total=False):
        key "autoclose": NotRequired[bool]
        key "autoping": NotRequired[bool]
        key "close_timeout": NotRequired[float]
        key "compression": NotRequired[Union[bool, int]]
        key "handshake_timeout": NotRequired[float]
        key "heartbeat": NotRequired[float]
        key "max_msg_size": NotRequired[int]
        key "receive_timeout": NotRequired[float]
        key "vendor_options": NotRequired[Mapping[str, Any]]


namespace azure.ai.voicelive.models

    class azure.ai.voicelive.models.AgentConfig(_Model):
        agent_id: str
        description: Optional[str]
        name: str
        thread_id: str
        type: Literal["agent"]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: str, 
                description: Optional[str] = ..., 
                name: str, 
                thread_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.Animation(_Model):
        model_name: Optional[str]
        outputs: Optional[list[Union[str, AnimationOutputType]]]

        @overload
        def __init__(
                self, 
                *, 
                model_name: Optional[str] = ..., 
                outputs: Optional[list[Union[str, AnimationOutputType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AnimationOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLENDSHAPES = "blendshapes"
        VISEME_ID = "viseme_id"


    class azure.ai.voicelive.models.AssistantMessageItem(MessageItem, discriminator='assistant'):
        content: list[MessageContentPart]
        id: str
        role: Literal[MessageRole.ASSISTANT]
        status: Union[str, ItemParamStatus]
        type: Union[str, azure.ai.voicelive.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageContentPart], 
                id: Optional[str] = ..., 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AudioEchoCancellation(_Model):
        type: Literal["server_echo_cancellation"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.voicelive.models.AudioInputTranscriptionOptions(_Model):
        custom_speech: Optional[dict[str, str]]
        language: Optional[str]
        model: Union[Literal["whisper-1"], Literal["gpt-4o-transcribe"], Literal["gpt-4o-mini-transcribe"], Literal["azure-speech"], str]
        phrase_list: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                custom_speech: Optional[dict[str, str]] = ..., 
                language: Optional[str] = ..., 
                model: Union[Literal[whisper-1], Literal[gpt-4o-transcribe], Literal[gpt-4o-mini-transcribe], Literal[azure-speech], str], 
                phrase_list: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AudioNoiseReduction(_Model):
        type: Union[Literal["azure_deep_noise_suppression"], Literal["near_field"], Literal["far_field"], str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[Literal[azure_deep_noise_suppression], Literal[near_field], Literal[far_field], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AudioTimestampType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORD = "word"


    class azure.ai.voicelive.models.AvatarConfig(_Model):
        character: str
        customized: bool
        ice_servers: Optional[list[IceServer]]
        model: Optional[Union[str, PhotoAvatarBaseModes]]
        output_audit_audio: Optional[bool]
        output_protocol: Optional[Union[str, AvatarOutputProtocol]]
        scene: Optional[Scene]
        style: Optional[str]
        type: Optional[Union[str, AvatarConfigTypes]]
        video: Optional[VideoParams]

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: bool, 
                ice_servers: Optional[list[IceServer]] = ..., 
                model: Optional[Union[str, PhotoAvatarBaseModes]] = ..., 
                output_audit_audio: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, AvatarOutputProtocol]] = ..., 
                scene: Optional[Scene] = ..., 
                style: Optional[str] = ..., 
                type: Optional[Union[str, AvatarConfigTypes]] = ..., 
                video: Optional[VideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AvatarConfigTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHOTO_AVATAR = "photo-avatar"
        VIDEO_AVATAR = "video-avatar"


    class azure.ai.voicelive.models.AvatarOutputProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"


    class azure.ai.voicelive.models.AzureCustomVoice(AzureVoice, discriminator='azure-custom'):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        endpoint_id: str
        locale: Optional[str]
        name: str
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        rate: Optional[str]
        style: Optional[str]
        temperature: Optional[float]
        type: Literal[AzureVoiceType.AZURE_CUSTOM]
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                endpoint_id: str, 
                locale: Optional[str] = ..., 
                name: str, 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzurePersonalVoice(AzureVoice, discriminator='azure-personal'):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        locale: Optional[str]
        model: Union[str, PersonalVoiceModels]
        name: str
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        rate: Optional[str]
        style: Optional[str]
        temperature: Optional[float]
        type: Literal[AzureVoiceType.AZURE_PERSONAL]
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                model: Union[str, PersonalVoiceModels], 
                name: str, 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticDetection(EouDetection, discriminator='semantic_detection_v1'):
        model: Literal["semantic_detection_v1"]
        threshold_level: Optional[Union[str, EouThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, EouThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticDetectionEn(EouDetection, discriminator='semantic_detection_v1_en'):
        model: Literal["semantic_detection_v1_en"]
        threshold_level: Optional[Union[str, EouThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, EouThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticDetectionMultilingual(EouDetection, discriminator='semantic_detection_v1_multilingual'):
        model: Literal["semantic_detection_v1_multilingual"]
        threshold_level: Optional[Union[str, EouThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, EouThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticVad(TurnDetection, discriminator='azure_semantic_vad'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[EouDetection]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[TurnDetectionType.AZURE_SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[EouDetection] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticVadEn(TurnDetection, discriminator='azure_semantic_vad_en'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[EouDetection]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[TurnDetectionType.AZURE_SEMANTIC_VAD_EN]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[EouDetection] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureSemanticVadMultilingual(TurnDetection, discriminator='azure_semantic_vad_multilingual'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[EouDetection]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[TurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[EouDetection] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureStandardVoice(AzureVoice, discriminator='azure-standard'):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        locale: Optional[str]
        name: str
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        rate: Optional[str]
        style: Optional[str]
        temperature: Optional[float]
        type: Literal[AzureVoiceType.AZURE_STANDARD]
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                name: str, 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureVoice(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.AzureVoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CUSTOM = "azure-custom"
        AZURE_PERSONAL = "azure-personal"
        AZURE_STANDARD = "azure-standard"


    class azure.ai.voicelive.models.Background(_Model):
        color: Optional[str]
        image_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                color: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.CachedTokenDetails(_Model):
        audio_tokens: int
        image_tokens: int
        text_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: int, 
                image_tokens: int, 
                text_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEvent(_Model):
        event_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventConversationItemCreate(ClientEvent, discriminator='conversation.item.create'):
        event_id: str
        item: Optional[ConversationRequestItem]
        previous_item_id: Optional[str]
        type: Literal[ClientEventType.CONVERSATION_ITEM_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Optional[ConversationRequestItem] = ..., 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventConversationItemDelete(ClientEvent, discriminator='conversation.item.delete'):
        event_id: str
        item_id: str
        type: Literal[ClientEventType.CONVERSATION_ITEM_DELETE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventConversationItemRetrieve(ClientEvent, discriminator='conversation.item.retrieve'):
        event_id: str
        item_id: str
        type: Literal[ClientEventType.CONVERSATION_ITEM_RETRIEVE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventConversationItemTruncate(ClientEvent, discriminator='conversation.item.truncate'):
        audio_end_ms: int
        content_index: int
        event_id: str
        item_id: str
        type: Literal[ClientEventType.CONVERSATION_ITEM_TRUNCATE]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioBufferAppend(ClientEvent, discriminator='input_audio_buffer.append'):
        audio: str
        event_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_BUFFER_APPEND]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioBufferClear(ClientEvent, discriminator='input_audio_buffer.clear'):
        event_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioBufferCommit(ClientEvent, discriminator='input_audio_buffer.commit'):
        event_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_BUFFER_COMMIT]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioClear(ClientEvent, discriminator='input_audio.clear'):
        event_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioTurnAppend(ClientEvent, discriminator='input_audio.turn.append'):
        audio: str
        event_id: str
        turn_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_TURN_APPEND]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ..., 
                turn_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioTurnCancel(ClientEvent, discriminator='input_audio.turn.cancel'):
        event_id: str
        turn_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_TURN_CANCEL]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                turn_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioTurnEnd(ClientEvent, discriminator='input_audio.turn.end'):
        event_id: str
        turn_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_TURN_END]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                turn_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventInputAudioTurnStart(ClientEvent, discriminator='input_audio.turn.start'):
        event_id: str
        turn_id: str
        type: Literal[ClientEventType.INPUT_AUDIO_TURN_START]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                turn_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventResponseCancel(ClientEvent, discriminator='response.cancel'):
        event_id: str
        response_id: Optional[str]
        type: Literal[ClientEventType.RESPONSE_CANCEL]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventResponseCreate(ClientEvent, discriminator='response.create'):
        additional_instructions: Optional[str]
        event_id: str
        response: Optional[ResponseCreateParams]
        type: Literal[ClientEventType.RESPONSE_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                additional_instructions: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                response: Optional[ResponseCreateParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventSessionAvatarConnect(ClientEvent, discriminator='session.avatar.connect'):
        client_sdp: str
        event_id: str
        type: Literal[ClientEventType.SESSION_AVATAR_CONNECT]

        @overload
        def __init__(
                self, 
                *, 
                client_sdp: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventSessionUpdate(ClientEvent, discriminator='session.update'):
        event_id: str
        session: RequestSession
        type: Literal[ClientEventType.SESSION_UPDATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: RequestSession
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATE = "conversation.item.create"
        CONVERSATION_ITEM_DELETE = "conversation.item.delete"
        CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
        CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
        INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
        INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
        INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
        INPUT_AUDIO_CLEAR = "input_audio.clear"
        INPUT_AUDIO_TURN_APPEND = "input_audio.turn.append"
        INPUT_AUDIO_TURN_CANCEL = "input_audio.turn.cancel"
        INPUT_AUDIO_TURN_END = "input_audio.turn.end"
        INPUT_AUDIO_TURN_START = "input_audio.turn.start"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        RESPONSE_CANCEL = "response.cancel"
        RESPONSE_CREATE = "response.create"
        SESSION_AVATAR_CONNECT = "session.avatar.connect"
        SESSION_UPDATE = "session.update"


    class azure.ai.voicelive.models.ContentPart(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ContentPartType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO = "audio"
        INPUT_AUDIO = "input_audio"
        INPUT_IMAGE = "input_image"
        INPUT_TEXT = "input_text"
        TEXT = "text"


    class azure.ai.voicelive.models.ConversationItemBase(_Model):


    class azure.ai.voicelive.models.ConversationRequestItem(_Model):
        id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.EouDetection(_Model):
        model: str

        @overload
        def __init__(
                self, 
                *, 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.EouThresholdLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.voicelive.models.ErrorResponse(_Model):
        error: VoiceLiveErrorDetails

        @overload
        def __init__(
                self, 
                *, 
                error: VoiceLiveErrorDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.FunctionCallItem(ConversationRequestItem, discriminator='function_call'):
        arguments: str
        call_id: str
        id: str
        name: str
        status: Optional[Union[str, ItemParamStatus]]
        type: Literal[ItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: str, 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.FunctionCallOutputItem(ConversationRequestItem, discriminator='function_call_output'):
        call_id: str
        id: str
        output: str
        status: Optional[Union[str, ItemParamStatus]]
        type: Literal[ItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                output: str, 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.FunctionTool(Tool, discriminator='function'):
        description: Optional[str]
        name: str
        parameters: Optional[Any]
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.IceServer(_Model):
        credential: Optional[str]
        urls: list[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[str] = ..., 
                urls: list[str], 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.InputAudioContentPart(MessageContentPart, discriminator='input_audio'):
        audio: str
        transcript: Optional[str]
        type: Literal[ContentPartType.INPUT_AUDIO]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                transcript: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.InputAudioFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G711_ALAW = "g711_alaw"
        G711_ULAW = "g711_ulaw"
        PCM16 = "pcm16"


    class azure.ai.voicelive.models.InputTextContentPart(MessageContentPart, discriminator='input_text'):
        text: str
        type: Literal[ContentPartType.INPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.InputTokenDetails(_Model):
        audio_tokens: int
        cached_tokens: int
        cached_tokens_details: CachedTokenDetails
        image_tokens: int
        text_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: int, 
                cached_tokens: int, 
                cached_tokens_details: CachedTokenDetails, 
                image_tokens: int, 
                text_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.InterimResponseConfigBase(_Model):
        latency_threshold_ms: Optional[int]
        triggers: Optional[list[Union[str, InterimResponseTrigger]]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                triggers: Optional[list[Union[str, InterimResponseTrigger]]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.InterimResponseConfigType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LLM_INTERIM_RESPONSE = "llm_interim_response"
        STATIC_INTERIM_RESPONSE = "static_interim_response"


    class azure.ai.voicelive.models.InterimResponseTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATENCY = "latency"
        TOOL = "tool"


    class azure.ai.voicelive.models.ItemParamStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"


    class azure.ai.voicelive.models.ItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.voicelive.models.LlmInterimResponseConfig(InterimResponseConfigBase, discriminator='llm_interim_response'):
        instructions: Optional[str]
        latency_threshold_ms: int
        max_completion_tokens: Optional[int]
        model: Optional[str]
        triggers: Union[list[str, InterimResponseTrigger]]
        type: Literal[InterimResponseConfigType.LLM_INTERIM_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                latency_threshold_ms: Optional[int] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                model: Optional[str] = ..., 
                triggers: Optional[list[Union[str, InterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.LogProbProperties(_Model):
        bytes: list[int]
        logprob: float
        token: str

        @overload
        def __init__(
                self, 
                *, 
                bytes: list[int], 
                logprob: float, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MCPApprovalResponseRequestItem(ConversationRequestItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: str
        type: Literal[ItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MCPApprovalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "always"
        NEVER = "never"


    class azure.ai.voicelive.models.MCPServer(Tool, discriminator='mcp'):
        allowed_tools: Optional[list[str]]
        authorization: Optional[str]
        headers: Optional[dict[str, str]]
        require_approval: Optional[Union[str, MCPApprovalType, dict[str, list[str]]]]
        server_label: str
        server_url: str
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[list[str]] = ..., 
                authorization: Optional[str] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                require_approval: Optional[Union[str, MCPApprovalType, dict[str, list[str]]]] = ..., 
                server_label: str, 
                server_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MCPTool(_Model):
        annotations: Optional[Any]
        description: Optional[str]
        input_schema: Any
        name: str

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[Any] = ..., 
                description: Optional[str] = ..., 
                input_schema: Any, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MessageContentPart(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MessageItem(ConversationRequestItem, discriminator='message'):
        content: list[MessageContentPart]
        id: str
        role: str
        status: Optional[Union[str, ItemParamStatus]]
        type: Literal[ItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageContentPart], 
                id: Optional[str] = ..., 
                role: str, 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.MessageRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.voicelive.models.Modality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANIMATION = "animation"
        AUDIO = "audio"
        AVATAR = "avatar"
        TEXT = "text"


    class azure.ai.voicelive.models.OpenAIVoice(_Model):
        name: Union[str, OpenAIVoiceName]
        type: Literal["openai"]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, OpenAIVoiceName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.OpenAIVoiceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOY = "alloy"
        ASH = "ash"
        BALLAD = "ballad"
        CEDAR = "cedar"
        CORAL = "coral"
        ECHO = "echo"
        MARIN = "marin"
        SAGE = "sage"
        SHIMMER = "shimmer"
        VERSE = "verse"


    class azure.ai.voicelive.models.OutputAudioFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G711_ALAW = "g711_alaw"
        G711_ULAW = "g711_ulaw"
        PCM16 = "pcm16"
        PCM16_16000_HZ = "pcm16_16000hz"
        PCM16_8000_HZ = "pcm16_8000hz"


    class azure.ai.voicelive.models.OutputTextContentPart(MessageContentPart, discriminator='text'):
        text: str
        type: Literal[ContentPartType.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.OutputTokenDetails(_Model):
        audio_tokens: int
        text_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: int, 
                text_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.PersonalVoiceModels(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAGON_LATEST_NEURAL = "DragonLatestNeural"
        PHOENIX_LATEST_NEURAL = "PhoenixLatestNeural"
        PHOENIX_V2_NEURAL = "PhoenixV2Neural"


    class azure.ai.voicelive.models.PhotoAvatarBaseModes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VASA1 = "vasa-1"


    class azure.ai.voicelive.models.ReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        NONE = "none"
        XHIGH = "xhigh"


    class azure.ai.voicelive.models.RequestAudioContentPart(ContentPart, discriminator='input_audio'):
        audio: str
        transcript: Optional[str]
        type: Literal[ContentPartType.INPUT_AUDIO]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                transcript: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.RequestImageContentPart(ContentPart, discriminator='input_image'):
        detail: Optional[Union[str, RequestImageContentPartDetail]]
        type: Literal[ContentPartType.INPUT_IMAGE]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                detail: Optional[Union[str, RequestImageContentPartDetail]] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.RequestImageContentPartDetail(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HIGH = "high"
        LOW = "low"


    class azure.ai.voicelive.models.RequestSession(GeneratedRequestSession):

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...

        def as_dict(self, **kwargs: Any) -> dict[str, Any]: ...


    class azure.ai.voicelive.models.RequestTextContentPart(ContentPart, discriminator='input_text'):
        text: Optional[str]
        type: Literal[ContentPartType.INPUT_TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.Response(_Model):
        conversation_id: Optional[str]
        id: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[dict[str, str]]
        modalities: Optional[list[Union[str, Modality]]]
        object: Optional[Literal["response"]]
        output: Optional[list[ResponseItem]]
        output_audio_format: Optional[Union[str, OutputAudioFormat]]
        status: Optional[Union[str, ResponseStatus]]
        status_details: Optional[ResponseStatusDetails]
        temperature: Optional[float]
        usage: Optional[TokenUsage]
        voice: Optional[Voice]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                modalities: Optional[list[Union[str, Modality]]] = ..., 
                object: Optional[Literal[response]] = ..., 
                output: Optional[list[ResponseItem]] = ..., 
                output_audio_format: Optional[Union[str, OutputAudioFormat]] = ..., 
                status: Optional[Union[str, ResponseStatus]] = ..., 
                status_details: Optional[ResponseStatusDetails] = ..., 
                temperature: Optional[float] = ..., 
                usage: Optional[TokenUsage] = ..., 
                voice: Optional[Voice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseAudioContentPart(ContentPart, discriminator='audio'):
        transcript: Optional[str]
        type: Literal[ContentPartType.AUDIO]

        @overload
        def __init__(
                self, 
                *, 
                transcript: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseCancelledDetails(ResponseStatusDetails, discriminator='cancelled'):
        reason: Union[Literal["turn_detected"], Literal["client_cancelled"], str]
        type: Literal[ResponseStatus.CANCELLED]

        @overload
        def __init__(
                self, 
                *, 
                reason: Union[Literal[turn_detected], Literal[client_cancelled], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseCreateParams(_Model):
        append_input_items: Optional[list[ConversationRequestItem]]
        cancel_previous: Optional[bool]
        commit: Optional[bool]
        input_items: Optional[list[ConversationRequestItem]]
        instructions: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[dict[str, str]]
        modalities: Optional[list[Union[str, Modality]]]
        output_audio_format: Optional[Union[str, OutputAudioFormat]]
        pre_generated_assistant_message: Optional[AssistantMessageItem]
        reasoning_effort: Optional[Union[str, ReasoningEffort]]
        temperature: Optional[float]
        tool_choice: Optional[str]
        tools: Optional[list[Tool]]
        voice: Optional[Voice]

        @overload
        def __init__(
                self, 
                *, 
                append_input_items: Optional[list[ConversationRequestItem]] = ..., 
                cancel_previous: Optional[bool] = ..., 
                commit: Optional[bool] = ..., 
                input_items: Optional[list[ConversationRequestItem]] = ..., 
                instructions: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                modalities: Optional[list[Union[str, Modality]]] = ..., 
                output_audio_format: Optional[Union[str, OutputAudioFormat]] = ..., 
                pre_generated_assistant_message: Optional[AssistantMessageItem] = ..., 
                reasoning_effort: Optional[Union[str, ReasoningEffort]] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[str] = ..., 
                tools: Optional[list[Tool]] = ..., 
                voice: Optional[Voice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseFailedDetails(ResponseStatusDetails, discriminator='failed'):
        error: Any
        type: Literal[ResponseStatus.FAILED]

        @overload
        def __init__(
                self, 
                *, 
                error: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseFunctionCallItem(ResponseItem, discriminator='function_call'):
        arguments: str
        call_id: str
        id: str
        name: str
        object: str
        status: Union[str, ResponseItemStatus]
        type: Literal[ItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                status: Union[str, ResponseItemStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseFunctionCallOutputItem(ResponseItem, discriminator='function_call_output'):
        call_id: str
        id: str
        object: str
        output: str
        type: Literal[ItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseIncompleteDetails(ResponseStatusDetails, discriminator='incomplete'):
        reason: Union[Literal["max_output_tokens"], Literal["content_filter"], str]
        type: Literal[ResponseStatus.INCOMPLETE]

        @overload
        def __init__(
                self, 
                *, 
                reason: Union[Literal[max_output_tokens], Literal[content_filter], str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseItem(_Model):
        id: Optional[str]
        object: Optional[Literal["item"]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseItemStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.voicelive.models.ResponseMCPApprovalRequestItem(ResponseItem, discriminator='mcp_approval_request'):
        arguments: Optional[str]
        id: str
        name: str
        object: str
        server_label: str
        type: Literal[ItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseMCPApprovalResponseItem(ResponseItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: str
        object: str
        reason: Optional[str]
        type: Literal[ItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseMCPCallItem(ResponseItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[Any]
        id: str
        name: str
        object: str
        output: Optional[str]
        server_label: str
        type: Literal[ItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[Any] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                output: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseMCPListToolItem(ResponseItem, discriminator='mcp_list_tools'):
        id: str
        object: str
        server_label: str
        tools: list[MCPTool]
        type: Literal[ItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                server_label: str, 
                tools: list[MCPTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseMessageItem(ResponseItem, discriminator='message'):
        content: list[ContentPart]
        id: str
        object: str
        role: Union[str, MessageRole]
        status: Union[str, ResponseItemStatus]
        type: Literal[ItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[ContentPart], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                role: Union[str, MessageRole], 
                status: Union[str, ResponseItemStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseSession(_Model):
        agent: Optional[AgentConfig]
        animation: Optional[Animation]
        avatar: Optional[AvatarConfig]
        id: Optional[str]
        input_audio_echo_cancellation: Optional[AudioEchoCancellation]
        input_audio_format: Optional[Union[str, InputAudioFormat]]
        input_audio_noise_reduction: Optional[AudioNoiseReduction]
        input_audio_sampling_rate: Optional[int]
        input_audio_transcription: Optional[AudioInputTranscriptionOptions]
        instructions: Optional[str]
        interim_response: Optional[InterimResponseConfig]
        max_response_output_tokens: Optional[Union[int, Literal["inf"]]]
        modalities: Optional[list[Union[str, Modality]]]
        model: Optional[str]
        output_audio_format: Optional[Union[str, OutputAudioFormat]]
        output_audio_timestamp_types: Optional[list[Union[str, AudioTimestampType]]]
        reasoning_effort: Optional[Union[str, ReasoningEffort]]
        temperature: Optional[float]
        tool_choice: Optional[ToolChoice]
        tools: Optional[list[Tool]]
        turn_detection: Optional[TurnDetection]
        voice: Optional[Voice]

        @overload
        def __init__(
                self, 
                *, 
                agent: Optional[AgentConfig] = ..., 
                animation: Optional[Animation] = ..., 
                avatar: Optional[AvatarConfig] = ..., 
                id: Optional[str] = ..., 
                input_audio_echo_cancellation: Optional[AudioEchoCancellation] = ..., 
                input_audio_format: Optional[Union[str, InputAudioFormat]] = ..., 
                input_audio_noise_reduction: Optional[AudioNoiseReduction] = ..., 
                input_audio_sampling_rate: Optional[int] = ..., 
                input_audio_transcription: Optional[AudioInputTranscriptionOptions] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[InterimResponseConfig] = ..., 
                max_response_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                modalities: Optional[list[Union[str, Modality]]] = ..., 
                model: Optional[str] = ..., 
                output_audio_format: Optional[Union[str, OutputAudioFormat]] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, AudioTimestampType]]] = ..., 
                reasoning_effort: Optional[Union[str, ReasoningEffort]] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[ToolChoice] = ..., 
                tools: Optional[list[Tool]] = ..., 
                turn_detection: Optional[TurnDetection] = ..., 
                voice: Optional[Voice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.voicelive.models.ResponseStatusDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ResponseTextContentPart(ContentPart, discriminator='text'):
        text: Optional[str]
        type: Literal[ContentPartType.TEXT]

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.Scene(_Model):
        amplitude: Optional[float]
        position_x: Optional[float]
        position_y: Optional[float]
        rotation_x: Optional[float]
        rotation_y: Optional[float]
        rotation_z: Optional[float]
        zoom: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                amplitude: Optional[float] = ..., 
                position_x: Optional[float] = ..., 
                position_y: Optional[float] = ..., 
                rotation_x: Optional[float] = ..., 
                rotation_y: Optional[float] = ..., 
                rotation_z: Optional[float] = ..., 
                zoom: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ServerEvent(_Model):
        event_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemCreated(ServerEvent, discriminator='conversation.item.created'):
        event_id: str
        item: Optional[ResponseItem]
        previous_item_id: Optional[str]
        type: Literal[ServerEventType.CONVERSATION_ITEM_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Optional[ResponseItem] = ..., 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemDeleted(ServerEvent, discriminator='conversation.item.deleted'):
        event_id: str
        item_id: str
        type: Literal[ServerEventType.CONVERSATION_ITEM_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemInputAudioTranscriptionCompleted(ServerEvent, discriminator='conversation.item.input_audio_transcription.completed'):
        content_index: int
        event_id: str
        item_id: str
        transcript: str
        type: Literal[ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                transcript: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemInputAudioTranscriptionDelta(ServerEvent, discriminator='conversation.item.input_audio_transcription.delta'):
        content_index: Optional[int]
        delta: Optional[str]
        event_id: str
        item_id: str
        logprobs: Optional[list[LogProbProperties]]
        type: Literal[ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: Optional[int] = ..., 
                delta: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                item_id: str, 
                logprobs: Optional[list[LogProbProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemInputAudioTranscriptionFailed(ServerEvent, discriminator='conversation.item.input_audio_transcription.failed'):
        content_index: int
        error: VoiceLiveErrorDetails
        event_id: str
        item_id: str
        type: Literal[ServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                error: VoiceLiveErrorDetails, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemRetrieved(ServerEvent, discriminator='conversation.item.retrieved'):
        event_id: str
        item: Optional[ResponseItem]
        type: Literal[ServerEventType.CONVERSATION_ITEM_RETRIEVED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Optional[ResponseItem] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventConversationItemTruncated(ServerEvent, discriminator='conversation.item.truncated'):
        audio_end_ms: int
        content_index: int
        event_id: str
        item_id: str
        type: Literal[ServerEventType.CONVERSATION_ITEM_TRUNCATED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventError(ServerEvent, discriminator='error'):
        error: ServerEventErrorDetails
        event_id: str
        type: Literal[ServerEventType.ERROR]

        @overload
        def __init__(
                self, 
                *, 
                error: ServerEventErrorDetails, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventErrorDetails(_Model):
        code: Optional[str]
        event_id: Optional[str]
        message: str
        param: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ServerEventInputAudioBufferCleared(ServerEvent, discriminator='input_audio_buffer.cleared'):
        event_id: str
        type: Literal[ServerEventType.INPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventInputAudioBufferCommitted(ServerEvent, discriminator='input_audio_buffer.committed'):
        event_id: str
        item_id: str
        previous_item_id: Optional[str]
        type: Literal[ServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventInputAudioBufferSpeechStarted(ServerEvent, discriminator='input_audio_buffer.speech_started'):
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]

        @overload
        def __init__(
                self, 
                *, 
                audio_start_ms: int, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventInputAudioBufferSpeechStopped(ServerEvent, discriminator='input_audio_buffer.speech_stopped'):
        audio_end_ms: int
        event_id: str
        item_id: str
        type: Literal[ServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventMcpListToolsCompleted(ServerEvent, discriminator='mcp_list_tools.completed'):
        event_id: str
        item_id: str
        type: Literal[ServerEventType.MCP_LIST_TOOLS_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventMcpListToolsFailed(ServerEvent, discriminator='mcp_list_tools.failed'):
        event_id: str
        item_id: str
        type: Literal[ServerEventType.MCP_LIST_TOOLS_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventMcpListToolsInProgress(ServerEvent, discriminator='mcp_list_tools.in_progress'):
        event_id: str
        item_id: str
        type: Literal[ServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAnimationBlendshapeDelta(ServerEvent, discriminator='response.animation_blendshapes.delta'):
        content_index: int
        event_id: str
        frame_index: int
        frames: Union[list[list[float]], str]
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_ANIMATION_BLENDSHAPES_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                frame_index: int, 
                frames: Union[list[list[float]], str], 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAnimationBlendshapeDone(ServerEvent, discriminator='response.animation_blendshapes.done'):
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_ANIMATION_BLENDSHAPES_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAnimationVisemeDelta(ServerEvent, discriminator='response.animation_viseme.delta'):
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_ANIMATION_VISEME_DELTA]
        viseme_id: int

        @overload
        def __init__(
                self, 
                *, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                viseme_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAnimationVisemeDone(ServerEvent, discriminator='response.animation_viseme.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_ANIMATION_VISEME_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioDelta(ServerEvent, discriminator='response.audio.delta'):
        content_index: int
        delta: bytes
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_AUDIO_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: bytes, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioDone(ServerEvent, discriminator='response.audio.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_AUDIO_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioTimestampDelta(ServerEvent, discriminator='response.audio_timestamp.delta'):
        audio_duration_ms: int
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal["word"]
        type: Literal[ServerEventType.RESPONSE_AUDIO_TIMESTAMP_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                audio_duration_ms: int, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioTimestampDone(ServerEvent, discriminator='response.audio_timestamp.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_AUDIO_TIMESTAMP_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioTranscriptDelta(ServerEvent, discriminator='response.audio_transcript.delta'):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseAudioTranscriptDone(ServerEvent, discriminator='response.audio_transcript.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        transcript: str
        type: Literal[ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                transcript: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseContentPartAdded(ServerEvent, discriminator='response.content_part.added'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: ContentPart
        response_id: str
        type: Literal[ServerEventType.RESPONSE_CONTENT_PART_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                part: ContentPart, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseContentPartDone(ServerEvent, discriminator='response.content_part.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: ContentPart
        response_id: str
        type: Literal[ServerEventType.RESPONSE_CONTENT_PART_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                part: ContentPart, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseCreated(ServerEvent, discriminator='response.created'):
        event_id: str
        response: Response
        type: Literal[ServerEventType.RESPONSE_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response: Response
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseDone(ServerEvent, discriminator='response.done'):
        event_id: str
        response: Response
        type: Literal[ServerEventType.RESPONSE_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response: Response
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseFunctionCallArgumentsDelta(ServerEvent, discriminator='response.function_call_arguments.delta'):
        call_id: str
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                delta: str, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseFunctionCallArgumentsDone(ServerEvent, discriminator='response.function_call_arguments.done'):
        arguments: str
        call_id: str
        event_id: str
        item_id: str
        name: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                name: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseMcpCallArgumentsDelta(ServerEvent, discriminator='response.mcp_call_arguments.delta'):
        delta: str
        event_id: str
        item_id: str
        obfuscation: Optional[str]
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                obfuscation: Optional[str] = ..., 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseMcpCallArgumentsDone(ServerEvent, discriminator='response.mcp_call_arguments.done'):
        arguments: Optional[str]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseMcpCallCompleted(ServerEvent, discriminator='response.mcp_call.completed'):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[ServerEventType.RESPONSE_MCP_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseMcpCallFailed(ServerEvent, discriminator='response.mcp_call.failed'):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[ServerEventType.RESPONSE_MCP_CALL_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseMcpCallInProgress(ServerEvent, discriminator='response.mcp_call.in_progress'):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[ServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseOutputItemAdded(ServerEvent, discriminator='response.output_item.added'):
        event_id: str
        item: Optional[ResponseItem]
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Optional[ResponseItem] = ..., 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseOutputItemDone(ServerEvent, discriminator='response.output_item.done'):
        event_id: str
        item: Optional[ResponseItem]
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_OUTPUT_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: Optional[ResponseItem] = ..., 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseTextDelta(ServerEvent, discriminator='response.text.delta'):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[ServerEventType.RESPONSE_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventResponseTextDone(ServerEvent, discriminator='response.text.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        type: Literal[ServerEventType.RESPONSE_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventSessionAvatarConnecting(ServerEvent, discriminator='session.avatar.connecting'):
        event_id: str
        server_sdp: str
        type: Literal[ServerEventType.SESSION_AVATAR_CONNECTING]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                server_sdp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventSessionCreated(ServerEvent, discriminator='session.created'):
        event_id: str
        session: ResponseSession
        type: Literal[ServerEventType.SESSION_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: ResponseSession
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventSessionUpdated(ServerEvent, discriminator='session.updated'):
        event_id: str
        session: ResponseSession
        type: Literal[ServerEventType.SESSION_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: ResponseSession
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATED = "conversation.item.created"
        CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
        CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
        CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
        ERROR = "error"
        INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
        INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
        INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
        INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
        MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
        MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
        MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
        RESPONSE_ANIMATION_BLENDSHAPES_DELTA = "response.animation_blendshapes.delta"
        RESPONSE_ANIMATION_BLENDSHAPES_DONE = "response.animation_blendshapes.done"
        RESPONSE_ANIMATION_VISEME_DELTA = "response.animation_viseme.delta"
        RESPONSE_ANIMATION_VISEME_DONE = "response.animation_viseme.done"
        RESPONSE_AUDIO_DELTA = "response.audio.delta"
        RESPONSE_AUDIO_DONE = "response.audio.done"
        RESPONSE_AUDIO_TIMESTAMP_DELTA = "response.audio_timestamp.delta"
        RESPONSE_AUDIO_TIMESTAMP_DONE = "response.audio_timestamp.done"
        RESPONSE_AUDIO_TRANSCRIPT_DELTA = "response.audio_transcript.delta"
        RESPONSE_AUDIO_TRANSCRIPT_DONE = "response.audio_transcript.done"
        RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
        RESPONSE_CONTENT_PART_DONE = "response.content_part.done"
        RESPONSE_CREATED = "response.created"
        RESPONSE_DONE = "response.done"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
        RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"
        RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
        RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
        RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
        RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
        RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_TEXT_DELTA = "response.text.delta"
        RESPONSE_TEXT_DONE = "response.text.done"
        SESSION_AVATAR_CONNECTING = "session.avatar.connecting"
        SESSION_CREATED = "session.created"
        SESSION_UPDATED = "session.updated"
        WARNING = "warning"


    class azure.ai.voicelive.models.ServerEventWarning(ServerEvent, discriminator='warning'):
        event_id: str
        type: Literal[ServerEventType.WARNING]
        warning: ServerEventWarningDetails

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                warning: ServerEventWarningDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        @classmethod
        def deserialize(cls, payload: dict[str, Any]) -> ServerEvent: ...


    class azure.ai.voicelive.models.ServerEventWarningDetails(_Model):
        code: Optional[str]
        message: str
        param: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ServerVad(TurnDetection, discriminator='server_vad'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[EouDetection]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[TurnDetectionType.SERVER_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[EouDetection] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.SessionBase(_Model):


    class azure.ai.voicelive.models.StaticInterimResponseConfig(InterimResponseConfigBase, discriminator='static_interim_response'):
        latency_threshold_ms: int
        texts: Optional[list[str]]
        triggers: Union[list[str, InterimResponseTrigger]]
        type: Literal[InterimResponseConfigType.STATIC_INTERIM_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                texts: Optional[list[str]] = ..., 
                triggers: Optional[list[Union[str, InterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.SystemMessageItem(MessageItem, discriminator='system'):
        content: list[MessageContentPart]
        id: str
        role: Literal[MessageRole.SYSTEM]
        status: Union[str, ItemParamStatus]
        type: Union[str, azure.ai.voicelive.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageContentPart], 
                id: Optional[str] = ..., 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.TokenUsage(_Model):
        input_token_details: InputTokenDetails
        input_tokens: int
        output_token_details: OutputTokenDetails
        output_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                input_token_details: InputTokenDetails, 
                input_tokens: int, 
                output_token_details: OutputTokenDetails, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.Tool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ToolChoiceFunctionSelection(ToolChoiceSelection, discriminator='function'):
        name: str
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ToolChoiceLiteral(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.voicelive.models.ToolChoiceSelection(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION = "function"
        MCP = "mcp"


    class azure.ai.voicelive.models.TurnDetection(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.TurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SERVER_VAD = "server_vad"


    class azure.ai.voicelive.models.UserMessageItem(MessageItem, discriminator='user'):
        content: list[MessageContentPart]
        id: str
        role: Literal[MessageRole.USER]
        status: Union[str, ItemParamStatus]
        type: Union[str, azure.ai.voicelive.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[MessageContentPart], 
                id: Optional[str] = ..., 
                status: Optional[Union[str, ItemParamStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.VideoCrop(_Model):
        bottom_right: list[int]
        top_left: list[int]

        @overload
        def __init__(
                self, 
                *, 
                bottom_right: list[int], 
                top_left: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.VideoParams(_Model):
        background: Optional[Background]
        bitrate: Optional[int]
        codec: Optional[Literal["h264"]]
        crop: Optional[VideoCrop]
        gop_size: Optional[int]
        resolution: Optional[VideoResolution]

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[Background] = ..., 
                bitrate: Optional[int] = ..., 
                codec: Optional[Literal[h264]] = ..., 
                crop: Optional[VideoCrop] = ..., 
                gop_size: Optional[int] = ..., 
                resolution: Optional[VideoResolution] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.VideoResolution(_Model):
        height: int
        width: int

        @overload
        def __init__(
                self, 
                *, 
                height: int, 
                width: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voicelive.models.VoiceLiveErrorDetails(_Model):
        code: Optional[str]
        event_id: Optional[str]
        message: str
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.voicelive.telemetry

    class azure.ai.voicelive.telemetry.VoiceLiveInstrumentor:

        def __init__(self) -> None: ...

        def instrument(self, enable_content_recording: Optional[bool] = None) -> None: ...

        def is_content_recording_enabled(self) -> bool: ...

        def is_instrumented(self) -> bool: ...

        def uninstrument(self) -> None: ...


```