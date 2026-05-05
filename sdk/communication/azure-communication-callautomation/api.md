```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.callautomation

    class azure.communication.callautomation.AddParticipantResult:
        invitation_id: Optional[str]
        operation_context: Optional[str]
        participant: Optional[CallParticipant]

        def __init__(
                self, 
                *, 
                invitation_id: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                participant: Optional[CallParticipant] = ...
            ): ...


    class azure.communication.callautomation.AudioFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM16_K_MONO = "pcm16KMono"
        PCM24_K_MONO = "pcm24KMono"


    class azure.communication.callautomation.AzureBlobContainerRecordingStorage(RecordingStorage):
        container_url: str
        kind: Literal[RecordingStorageKind.AZURE_BLOB_STORAGE] = RecordingStorageKind.AZURE_BLOB_STORAGE

        def __init__(self, container_url: str): ...


    class azure.communication.callautomation.AzureCommunicationsRecordingStorage(RecordingStorage):
        kind: Literal[RecordingStorageKind.AZURE_COMMUNICATION_SERVICES] = RecordingStorageKind.AZURE_COMMUNICATION_SERVICES


    class azure.communication.callautomation.CallAutomationClient: implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: Optional[str] = ..., 
                source: Optional[CommunicationUserIdentifier] = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> CallAutomationClient: ...

        @distributed_trace
        def answer_call(
                self, 
                incoming_call_context: str, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        def close(self) -> None: ...

        @overload
        def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                server_call_id: str, 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @overload
        def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                group_call_id: str, 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @overload
        def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                room_id: str, 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace
        def create_call(
                self, 
                target_participant: Union[CommunicationIdentifier, Sequence[CommunicationIdentifier]], 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                teams_app_source: Optional[MicrosoftTeamsAppIdentifier] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace
        def create_group_call(
                self, 
                target_participants: Sequence[CommunicationIdentifier], 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                teams_app_source: Optional[MicrosoftTeamsAppIdentifier] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace
        def delete_recording(
                self, 
                recording_url: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def download_recording(
                self, 
                recording_url: str, 
                *, 
                length: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs
            ) -> Iterable[bytes]: ...

        def get_call_connection(
                self, 
                call_connection_id: str, 
                **kwargs
            ) -> CallConnectionClient: ...

        @distributed_trace
        def get_recording_properties(
                self, 
                recording_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @distributed_trace
        def pause_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def redirect_call(
                self, 
                incoming_call_context: str, 
                target_participant: CommunicationIdentifier, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def reject_call(
                self, 
                incoming_call_context: str, 
                *, 
                call_reject_reason: Optional[Union[str, CallRejectReason]] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def resume_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...

        @overload
        def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                server_call_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                group_call_id: str, 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                room_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                call_connection_id: str, 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                **kwargs
            ) -> RecordingProperties: ...

        @distributed_trace
        def stop_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...


    class azure.communication.callautomation.CallConnectionClient:

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                call_connection_id: str, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                call_connection_id: str, 
                **kwargs
            ) -> CallConnectionClient: ...

        @distributed_trace
        def add_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                invitation_timeout: Optional[int] = ..., 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                sip_headers: Optional[Mapping[str, str]] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                voip_headers: Optional[Mapping[str, str]] = ..., 
                **kwargs
            ) -> AddParticipantResult: ...

        @distributed_trace
        def cancel_add_participant_operation(
                self, 
                invitation_id: str, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> CancelAddParticipantOperationResult: ...

        @distributed_trace
        def cancel_all_media_operations(self, **kwargs) -> None: ...

        @distributed_trace
        def get_call_properties(self, **kwargs) -> CallConnectionProperties: ...

        @distributed_trace
        def get_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                **kwargs
            ) -> CallParticipant: ...

        @distributed_trace
        def hang_up(
                self, 
                is_for_everyone: bool = False, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def hold(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                play_source: Optional[Union[FileSource, TextSource, SsmlSource]] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_participants(self, **kwargs) -> ItemPaged[CallParticipant]: ...

        @distributed_trace
        def mute_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> MuteParticipantResult: ...

        @overload
        def play_media(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                play_to: Sequence[CommunicationIdentifier], 
                *, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @overload
        def play_media(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                play_to: Literal["all"] = "all", 
                *, 
                interrupt_call_media_operation: bool = False, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def play_media_to_all(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                *, 
                interrupt_call_media_operation: bool = False, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def remove_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> RemoveParticipantResult: ...

        @distributed_trace
        def send_dtmf_tones(
                self, 
                tones: Sequence[Union[str, DtmfTone]], 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> SendDtmfTonesResult: ...

        @distributed_trace
        def start_continuous_dtmf_recognition(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def start_media_streaming(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def start_recognizing_media(
                self, 
                input_type: Union[str, RecognizeInputType], 
                target_participant: CommunicationIdentifier, 
                *, 
                choices: Optional[Sequence[RecognitionChoice]] = ..., 
                dtmf_inter_tone_timeout: Optional[int] = ..., 
                dtmf_max_tones_to_collect: Optional[int] = ..., 
                dtmf_stop_tones: Optional[Sequence[Union[str, DtmfTone]]] = ..., 
                end_silence_timeout: Optional[int] = ..., 
                initial_silence_timeout: Optional[int] = ..., 
                interrupt_call_media_operation: bool = False, 
                interrupt_prompt: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                play_prompt: Optional[Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]]] = ..., 
                speech_language: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def start_transcription(
                self, 
                *, 
                locale: Optional[str] = ..., 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def stop_continuous_dtmf_recognition(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def stop_media_streaming(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def stop_transcription(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def transfer_call_to_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                sip_headers: Optional[Mapping[str, str]] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                transferee: Optional[CommunicationIdentifier] = ..., 
                voip_headers: Optional[Mapping[str, str]] = ..., 
                **kwargs
            ) -> TransferCallResult: ...

        @distributed_trace
        def unhold(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def update_transcription(
                self, 
                *, 
                locale: str, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...


    class azure.communication.callautomation.CallConnectionProperties:
        answered_by: Optional[CommunicationIdentifier]
        answered_for: Optional[PhoneNumberIdentifier]
        call_connection_id: Optional[str]
        call_connection_state: Optional[Union[str, CallConnectionState]]
        callback_url: Optional[str]
        correlation_id: Optional[str]
        media_streaming_subscription: Optional[MediaStreamingSubscription]
        server_call_id: Optional[str]
        source: Optional[CommunicationIdentifier]
        source_caller_id_number: Optional[PhoneNumberIdentifier]
        source_display_name: Optional[str]
        targets: Optional[List[CommunicationIdentifier]]
        transcription_subscription: Optional[TranscriptionSubscription]

        def __init__(
                self, 
                *, 
                answered_by: Optional[CommunicationIdentifier] = ..., 
                answered_for: Optional[PhoneNumberIdentifier] = ..., 
                call_connection_id: Optional[str] = ..., 
                call_connection_state: Optional[Union[str, CallConnectionState]] = ..., 
                callback_url: Optional[str] = ..., 
                correlation_id: Optional[str] = ..., 
                media_streaming_subscription: Optional[MediaStreamingSubscription] = ..., 
                server_call_id: Optional[str] = ..., 
                source: Optional[CommunicationIdentifier] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                targets: Optional[List[CommunicationIdentifier]] = ..., 
                transcription_subscription: Optional[TranscriptionSubscription] = ...
            ): ...


    class azure.communication.callautomation.CallConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "connected"
        CONNECTING = "connecting"
        DISCONNECTED = "disconnected"
        DISCONNECTING = "disconnecting"
        TRANSFERRING = "transferring"
        TRANSFER_ACCEPTED = "transferAccepted"
        UNKNOWN = "unknown"


    class azure.communication.callautomation.CallParticipant:
        identifier: Optional[CommunicationIdentifier]
        is_muted: Optional[bool]
        is_on_hold: Optional[bool]

        def __init__(
                self, 
                *, 
                identifier: Optional[CommunicationIdentifier] = ..., 
                is_muted: Optional[bool] = False, 
                is_on_hold: Optional[bool] = False
            ): ...


    class azure.communication.callautomation.CallRejectReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSY = "busy"
        FORBIDDEN = "forbidden"
        NONE = "none"


    class azure.communication.callautomation.CancelAddParticipantOperationResult:
        invitation_id: Optional[str]
        operation_context: Optional[str]

        def __init__(
                self, 
                *, 
                invitation_id: Optional[str] = ..., 
                operation_context: Optional[str] = ...
            ): ...


    class azure.communication.callautomation.ChannelAffinity:
        channel: int
        target_participant: CommunicationIdentifier

        def __init__(
                self, 
                target_participant: CommunicationIdentifier, 
                channel: int
            ): ...


    class azure.communication.callautomation.CommunicationCloudEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOD = "DOD"
        GCCH = "GCCH"
        PUBLIC = "PUBLIC"


    @runtime_checkable
    class azure.communication.callautomation.CommunicationIdentifier(Protocol):
        property kind: CommunicationIdentifierKind    # Read-only
        property properties: Mapping[str, Any]    # Read-only
        property raw_id: str    # Read-only


    class azure.communication.callautomation.CommunicationIdentifierKind(str, Enum, metaclass=DeprecatedEnumMeta):
        COMMUNICATION_USER = "communication_user"
        MICROSOFT_TEAMS_APP = "microsoft_teams_app"
        MICROSOFT_TEAMS_USER = "microsoft_teams_user"
        PHONE_NUMBER = "phone_number"
        TEAMS_EXTENSION_USER = "teams_extension_user"
        UNKNOWN = "unknown"


    class azure.communication.callautomation.CommunicationUserIdentifier:
        kind: Literal[CommunicationIdentifierKind.COMMUNICATION_USER] = CommunicationIdentifierKind.COMMUNICATION_USER
        properties: CommunicationUserProperties
        raw_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                id: str, 
                *, 
                raw_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.callautomation.DtmfTone(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "a"
        ASTERISK = "asterisk"
        B = "b"
        C = "c"
        D = "d"
        EIGHT = "eight"
        FIVE = "five"
        FOUR = "four"
        NINE = "nine"
        ONE = "one"
        POUND = "pound"
        SEVEN = "seven"
        SIX = "six"
        THREE = "three"
        TWO = "two"
        ZERO = "zero"


    class azure.communication.callautomation.FileSource:
        play_source_cache_id: Optional[str]
        url: str

        def __init__(
                self, 
                url: str, 
                *, 
                play_source_cache_id: Optional[str] = ...
            ): ...


    class azure.communication.callautomation.MediaStreamingAudioChannelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "mixed"
        UNMIXED = "unmixed"


    class azure.communication.callautomation.MediaStreamingContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO = "audio"


    class azure.communication.callautomation.MediaStreamingOptions:
        audio_channel_type: Union[str, MediaStreamingAudioChannelType]
        audio_format: Optional[Union[str, AudioFormat]]
        content_type: Union[str, MediaStreamingContentType]
        enable_bidirectional: Optional[bool]
        enable_dtmf_tones: Optional[bool]
        start_media_streaming: Optional[bool]
        transport_type: Union[str, StreamingTransportType]
        transport_url: str

        def __init__(
                self, 
                *, 
                audio_channel_type: Union[str, MediaStreamingAudioChannelType], 
                audio_format: Optional[Union[str, AudioFormat]] = ..., 
                content_type: Union[str, MediaStreamingContentType], 
                enable_bidirectional: Optional[bool] = ..., 
                enable_dtmf_tones: Optional[bool] = ..., 
                start_media_streaming: Optional[bool] = ..., 
                transport_type: Union[str, StreamingTransportType], 
                transport_url: str
            ): ...


    class azure.communication.callautomation.MediaStreamingSubscription:
        id: Optional[str]
        state: Optional[Union[str, MediaStreamingSubscriptionState]]
        subscribed_content_types: Optional[List[Union[str, MediaStreamingContentType]]]

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                state: Optional[Union[str, MediaStreamingSubscriptionState]] = ..., 
                subscribed_content_types: Optional[List[Union[str, MediaStreamingContentType]]] = ...
            ) -> None: ...


    class azure.communication.callautomation.MediaStreamingSubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DISABLED = "disabled"
        INACTIVE = "inactive"


    class azure.communication.callautomation.MicrosoftTeamsAppIdentifier:
        kind: Literal[CommunicationIdentifierKind.MICROSOFT_TEAMS_APP] = CommunicationIdentifierKind.MICROSOFT_TEAMS_APP
        properties: MicrosoftTeamsAppProperties
        raw_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                app_id: str, 
                *, 
                cloud: Union[str, CommunicationCloudEnvironment] = ..., 
                raw_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.callautomation.MicrosoftTeamsUserIdentifier:
        kind: Literal[CommunicationIdentifierKind.MICROSOFT_TEAMS_USER] = CommunicationIdentifierKind.MICROSOFT_TEAMS_USER
        properties: MicrosoftTeamsUserProperties
        raw_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                user_id: str, 
                *, 
                cloud: Union[str, CommunicationCloudEnvironment] = ..., 
                is_anonymous: Optional[bool] = ..., 
                raw_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.callautomation.MuteParticipantResult:
        operation_context: Optional[str]

        def __init__(
                self, 
                *, 
                operation_context: Optional[str] = ...
            ) -> None: ...


    class azure.communication.callautomation.PhoneNumberIdentifier:
        kind: Literal[CommunicationIdentifierKind.PHONE_NUMBER] = CommunicationIdentifierKind.PHONE_NUMBER
        properties: PhoneNumberProperties
        raw_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                value: str, 
                *, 
                raw_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.callautomation.RecognitionChoice:
        label: str
        phrases: List[str]
        tone: Optional[Union[str, DtmfTone]]

        def __init__(
                self, 
                *, 
                label: str, 
                phrases: List[str], 
                tone: Optional[Union[str, DtmfTone]] = ...
            ): ...


    class azure.communication.callautomation.RecognizeInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHOICES = "choices"
        DTMF = "dtmf"
        SPEECH = "speech"
        SPEECH_OR_DTMF = "speechOrDtmf"


    class azure.communication.callautomation.RecordingChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIXED = "mixed"
        UNMIXED = "unmixed"


    class azure.communication.callautomation.RecordingContent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO = "audio"
        AUDIO_VIDEO = "audioVideo"


    class azure.communication.callautomation.RecordingFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MP3 = "mp3"
        MP4 = "mp4"
        WAV = "wav"


    class azure.communication.callautomation.RecordingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_COMMUNICATION_SERVICES = "AzureCommunicationServices"
        TEAMS = "Teams"
        TEAMS_COMPLIANCE = "TeamsCompliance"


    class azure.communication.callautomation.RecordingProperties:
        recording_id: Optional[str]
        recording_kind: Optional[Union[str, RecordingKind]]
        recording_state: Optional[Union[str, RecordingState]]

        def __init__(
                self, 
                *, 
                recording_id: Optional[str] = ..., 
                recording_kind: Optional[Union[str, RecordingKind]] = ..., 
                recording_state: Optional[Union[str, RecordingState]] = ...
            ): ...


    class azure.communication.callautomation.RecordingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        INACTIVE = "inactive"


    class azure.communication.callautomation.RecordingStorageKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_BLOB_STORAGE = "AzureBlobStorage"
        AZURE_COMMUNICATION_SERVICES = "AzureCommunicationServices"


    class azure.communication.callautomation.RemoveParticipantResult:
        operation_context: Optional[str]

        def __init__(
                self, 
                *, 
                operation_context: Optional[str] = ...
            ) -> None: ...


    class azure.communication.callautomation.SendDtmfTonesResult:
        operation_context: Optional[str]

        def __init__(
                self, 
                *, 
                operation_context: Optional[str] = ...
            ) -> None: ...


    class azure.communication.callautomation.SsmlSource:
        custom_voice_endpoint_id: Optional[str]
        play_source_cache_id: Optional[str]
        ssml_text: str

        def __init__(
                self, 
                *, 
                custom_voice_endpoint_id: Optional[str] = ..., 
                play_source_cache_id: Optional[str] = ..., 
                ssml_text: str
            ): ...


    class azure.communication.callautomation.StreamingTransportType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBSOCKET = "websocket"


    class azure.communication.callautomation.TeamsExtensionUserIdentifier:
        kind: Literal[CommunicationIdentifierKind.TEAMS_EXTENSION_USER] = CommunicationIdentifierKind.TEAMS_EXTENSION_USER
        properties: TeamsExtensionUserProperties
        raw_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cloud: Union[str, CommunicationCloudEnvironment] = ..., 
                raw_id: Optional[str] = ..., 
                resource_id: str, 
                tenant_id: str, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.callautomation.TeamsExtensionUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "resource_id": str
        key "tenant_id": str
        key "user_id": str


    class azure.communication.callautomation.TextSource:
        custom_voice_endpoint_id: Optional[str]
        play_source_cache_id: Optional[str]
        source_locale: Optional[str]
        text: str
        voice_kind: Optional[Union[str, VoiceKind]]
        voice_name: Optional[str]

        def __init__(
                self, 
                *, 
                custom_voice_endpoint_id: Optional[str] = ..., 
                play_source_cache_id: Optional[str] = ..., 
                source_locale: Optional[str] = ..., 
                text: str, 
                voice_kind: Optional[Union[str, VoiceKind]] = ..., 
                voice_name: Optional[str] = ...
            ): ...


    class azure.communication.callautomation.TranscriptionOptions:
        enable_intermediate_results: Optional[bool]
        locale: str
        speech_recognition_model_endpoint_id: Optional[str]
        start_transcription: bool
        transport_type: Union[str, StreamingTransportType]
        transport_url: str

        def __init__(
                self, 
                *, 
                enable_intermediate_results: Optional[bool] = ..., 
                locale: str, 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                start_transcription: bool, 
                transport_type: Union[str, StreamingTransportType], 
                transport_url: str
            ): ...


    class azure.communication.callautomation.TranscriptionResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINAL = "final"
        INTERMEDIATE = "intermediate"


    class azure.communication.callautomation.TranscriptionSubscription:
        id: Optional[str]
        locale: Optional[str]
        state: Optional[Union[str, TranscriptionSubscriptionState]]
        subscribed_result_types: Optional[List[Union[str, TranscriptionResultType]]]

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                state: Optional[Union[str, TranscriptionSubscriptionState]] = ..., 
                subscribed_result_types: Optional[List[Union[str, TranscriptionResultType]]] = ...
            ) -> None: ...


    class azure.communication.callautomation.TranscriptionSubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DISABLED = "disabled"
        INACTIVE = "inactive"


    class azure.communication.callautomation.TransferCallResult:
        operation_context: Optional[str]

        def __init__(
                self, 
                *, 
                operation_context: Optional[str] = ...
            ) -> None: ...


    class azure.communication.callautomation.UnknownIdentifier:
        kind: Literal[CommunicationIdentifierKind.UNKNOWN] = CommunicationIdentifierKind.UNKNOWN
        properties: Mapping[str, Any]
        raw_id: str

        def __eq__(self, other): ...

        def __init__(self, identifier: str) -> None: ...


    class azure.communication.callautomation.VoiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEMALE = "female"
        MALE = "male"


namespace azure.communication.callautomation.aio

    class azure.communication.callautomation.aio.CallAutomationClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: Optional[str] = ..., 
                source: Optional[CommunicationUserIdentifier] = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> CallAutomationClient: ...

        @distributed_trace_async
        async def answer_call(
                self, 
                incoming_call_context: str, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        async def close(self) -> None: ...

        @overload
        async def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                server_call_id: str, 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @overload
        async def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                group_call_id: str, 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @overload
        async def connect_call(
                self, 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                room_id: str, 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace_async
        async def create_call(
                self, 
                target_participant: Union[CommunicationIdentifier, Sequence[CommunicationIdentifier]], 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                media_streaming: Optional[MediaStreamingOptions] = ..., 
                operation_context: Optional[str] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                teams_app_source: Optional[MicrosoftTeamsAppIdentifier] = ..., 
                transcription: Optional[TranscriptionOptions] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace_async
        async def create_group_call(
                self, 
                target_participants: Sequence[CommunicationIdentifier], 
                callback_url: str, 
                *, 
                cognitive_services_endpoint: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                teams_app_source: Optional[MicrosoftTeamsAppIdentifier] = ..., 
                **kwargs
            ) -> CallConnectionProperties: ...

        @distributed_trace_async
        async def delete_recording(
                self, 
                recording_url: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def download_recording(
                self, 
                recording_url: str, 
                *, 
                length: Optional[int] = ..., 
                offset: Optional[int] = ..., 
                **kwargs
            ) -> AsyncIterable[bytes]: ...

        def get_call_connection(
                self, 
                call_connection_id: str, 
                **kwargs
            ) -> CallConnectionClient: ...

        @distributed_trace_async
        async def get_recording_properties(
                self, 
                recording_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @distributed_trace_async
        async def pause_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def redirect_call(
                self, 
                incoming_call_context: str, 
                target_participant: CommunicationIdentifier, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def reject_call(
                self, 
                incoming_call_context: str, 
                *, 
                call_reject_reason: Optional[Union[str, CallRejectReason]] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def resume_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...

        @overload
        async def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                server_call_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        async def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                group_call_id: str, 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        async def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                room_id: str, 
                **kwargs
            ) -> RecordingProperties: ...

        @overload
        async def start_recording(
                self, 
                *, 
                audio_channel_participant_ordering: Optional[Sequence[CommunicationIdentifier]] = ..., 
                call_connection_id: str, 
                channel_affinity: Optional[Sequence[ChannelAffinity]] = ..., 
                pause_on_start: Optional[bool] = ..., 
                recording_channel_type: Optional[Union[str, RecordingChannel]] = ..., 
                recording_content_type: Optional[Union[str, RecordingContent]] = ..., 
                recording_format_type: Optional[Union[str, RecordingFormat]] = ..., 
                recording_state_callback_url: Optional[str] = ..., 
                recording_storage: Optional[Union[AzureCommunicationsRecordingStorage, AzureBlobContainerRecordingStorage]] = ..., 
                **kwargs
            ) -> RecordingProperties: ...

        @distributed_trace_async
        async def stop_recording(
                self, 
                recording_id: str, 
                **kwargs
            ) -> None: ...


    class azure.communication.callautomation.aio.CallConnectionClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                call_connection_id: str, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                call_connection_id: str, 
                **kwargs
            ) -> CallConnectionClient: ...

        @distributed_trace_async
        async def add_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                invitation_timeout: Optional[int] = ..., 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                sip_headers: Optional[Mapping[str, str]] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                source_display_name: Optional[str] = ..., 
                voip_headers: Optional[Mapping[str, str]] = ..., 
                **kwargs
            ) -> AddParticipantResult: ...

        @distributed_trace_async
        async def cancel_add_participant_operation(
                self, 
                invitation_id: str, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> CancelAddParticipantOperationResult: ...

        @distributed_trace_async
        async def cancel_all_media_operations(self, **kwargs) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_call_properties(self, **kwargs) -> CallConnectionProperties: ...

        @distributed_trace_async
        async def get_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                **kwargs
            ) -> CallParticipant: ...

        @distributed_trace_async
        async def hang_up(
                self, 
                is_for_everyone: bool = False, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def hold(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                play_source: Optional[Union[FileSource, TextSource, SsmlSource]] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_participants(self, **kwargs) -> AsyncItemPaged[CallParticipant]: ...

        @distributed_trace_async
        async def mute_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> MuteParticipantResult: ...

        @overload
        async def play_media(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                play_to: Sequence[CommunicationIdentifier], 
                *, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @overload
        async def play_media(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                play_to: Literal["all"] = "all", 
                *, 
                interrupt_call_media_operation: bool = False, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def play_media_to_all(
                self, 
                play_source: Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]], 
                *, 
                interrupt_call_media_operation: bool = False, 
                loop: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def remove_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> RemoveParticipantResult: ...

        @distributed_trace_async
        async def send_dtmf_tones(
                self, 
                tones: Sequence[Union[str, DtmfTone]], 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> SendDtmfTonesResult: ...

        @distributed_trace_async
        async def start_continuous_dtmf_recognition(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def start_media_streaming(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def start_recognizing_media(
                self, 
                input_type: Union[str, RecognizeInputType], 
                target_participant: CommunicationIdentifier, 
                *, 
                choices: Optional[Sequence[RecognitionChoice]] = ..., 
                dtmf_inter_tone_timeout: Optional[int] = ..., 
                dtmf_max_tones_to_collect: Optional[int] = ..., 
                dtmf_stop_tones: Optional[Sequence[Union[str, DtmfTone]]] = ..., 
                end_silence_timeout: Optional[int] = ..., 
                initial_silence_timeout: Optional[int] = ..., 
                interrupt_call_media_operation: bool = False, 
                interrupt_prompt: bool = False, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                play_prompt: Optional[Union[Union[FileSource, TextSource, SsmlSource], Sequence[Union[FileSource, TextSource, SsmlSource]]]] = ..., 
                speech_language: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def start_transcription(
                self, 
                *, 
                locale: Optional[str] = ..., 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def stop_continuous_dtmf_recognition(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def stop_media_streaming(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def stop_transcription(
                self, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def transfer_call_to_participant(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                sip_headers: Optional[Mapping[str, str]] = ..., 
                source_caller_id_number: Optional[PhoneNumberIdentifier] = ..., 
                transferee: Optional[CommunicationIdentifier] = ..., 
                voip_headers: Optional[Mapping[str, str]] = ..., 
                **kwargs
            ) -> TransferCallResult: ...

        @distributed_trace_async
        async def unhold(
                self, 
                target_participant: CommunicationIdentifier, 
                *, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_transcription(
                self, 
                *, 
                locale: str, 
                operation_callback_url: Optional[str] = ..., 
                operation_context: Optional[str] = ..., 
                speech_recognition_model_endpoint_id: Optional[str] = ..., 
                **kwargs
            ) -> None: ...


```