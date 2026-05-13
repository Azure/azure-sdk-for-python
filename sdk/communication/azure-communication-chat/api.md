```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.chat

    def azure.communication.chat.identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier: ...


    class azure.communication.chat.ChatAttachment:
        attachment_type: Union[str, ChatAttachmentType]
        id: str
        name: Union[str, None]
        preview_url: Union[str, None]
        url: Union[str, None]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.communication.chat.ChatAttachmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE = "file"
        IMAGE = "image"


    class azure.communication.chat.ChatClient: implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: CommunicationTokenCredential, 
                **kwargs
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_chat_thread(
                self, 
                topic: str, 
                *, 
                idempotency_token: str = ..., 
                thread_participants: List[ChatParticipant] = ..., 
                **kwargs
            ) -> CreateChatThreadResult: ...

        @distributed_trace
        def delete_chat_thread(
                self, 
                thread_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_chat_thread_client(
                self, 
                thread_id: str, 
                **kwargs
            ) -> ChatThreadClient: ...

        @distributed_trace
        def list_chat_threads(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ) -> ItemPaged[ChatThreadItem]: ...


    class azure.communication.chat.ChatError(Model):
        code: str
        details: list[ChatError]
        inner_error: ChatError
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.chat.ChatMessage:
        content: Union[ChatMessageContent, None]
        created_on: datetime
        deleted_on: Union[datetime, None]
        edited_on: Union[datetime, None]
        id: str
        metadata: Union[dict[str, str], None]
        sender: Union[CommunicationIdentifier, None]
        sender_display_name: Union[str, None]
        sequence_id: str
        type: Union[str, ChatMessageType]
        version: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.communication.chat.ChatMessageContent:
        attachments: List[ChatAttachment]
        initiator: Union[CommunicationIdentifier, None]
        message: Union[str, None]
        participants: List[ChatParticipant]
        topic: Union[str, None]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.communication.chat.ChatMessageReadReceipt:
        chat_message_id: str
        read_on: datetime
        sender: CommunicationIdentifier

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.communication.chat.ChatMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTML = "html"
        PARTICIPANT_ADDED = "participantAdded"
        PARTICIPANT_REMOVED = "participantRemoved"
        TEXT = "text"
        TOPIC_UPDATED = "topicUpdated"


    class azure.communication.chat.ChatParticipant:
        display_name: Union[str, None]
        identifier: CommunicationIdentifier
        share_history_time: Union[datetime, None]

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                identifier: CommunicationIdentifier, 
                share_history_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.chat.ChatThreadClient: implements ContextManager 
        property thread_id: str    # Read-only
        thread_id: str

        def __init__(
                self, 
                endpoint: str, 
                credential: CommunicationTokenCredential, 
                thread_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def add_participants(
                self, 
                thread_participants: List[ChatParticipant], 
                **kwargs
            ) -> List[Tuple[ChatParticipant, ChatError]]: ...

        def close(self) -> None: ...

        @distributed_trace
        def delete_message(
                self, 
                message_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_message(
                self, 
                message_id: str, 
                **kwargs
            ) -> ChatMessage: ...

        @distributed_trace
        def get_properties(self, **kwargs) -> ChatThreadProperties: ...

        @distributed_trace
        def list_messages(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs
            ) -> ItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_participants(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                skip: Optional[int] = ..., 
                **kwargs
            ) -> ItemPaged[ChatParticipant]: ...

        @distributed_trace
        def list_read_receipts(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                skip: Optional[int] = ..., 
                **kwargs
            ) -> ItemPaged[ChatMessageReadReceipt]: ...

        @distributed_trace
        def remove_participant(
                self, 
                identifier: CommunicationIdentifier, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def send_message(
                self, 
                content: str, 
                *, 
                chat_message_type: Union[str, ChatMessageType] = ..., 
                sender_display_name: Optional[str] = ..., 
                **kwargs
            ) -> SendChatMessageResult: ...

        @distributed_trace
        def send_read_receipt(
                self, 
                message_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def send_typing_notification(
                self, 
                *, 
                sender_display_name: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def update_message(
                self, 
                message_id: str, 
                content: Optional[str] = None, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def update_topic(
                self, 
                topic: Optional[str] = None, 
                **kwargs
            ) -> None: ...


    class azure.communication.chat.ChatThreadItem(Model):
        deleted_on: datetime
        id: str
        last_message_received_on: datetime
        topic: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deleted_on: Optional[datetime] = ..., 
                id: str, 
                topic: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.chat.ChatThreadProperties:
        created_by: CommunicationIdentifier
        created_on: datetime
        id: str
        topic: str

        def __init__(self, **kwargs: Any) -> None: ...


    @runtime_checkable
    class azure.communication.chat.CommunicationIdentifier(Protocol):
        property kind: CommunicationIdentifierKind    # Read-only
        property properties: Mapping[str, Any]    # Read-only
        property raw_id: str    # Read-only


    class azure.communication.chat.CommunicationIdentifierKind(str, Enum, metaclass=DeprecatedEnumMeta):
        COMMUNICATION_USER = "communication_user"
        MICROSOFT_TEAMS_APP = "microsoft_teams_app"
        MICROSOFT_TEAMS_USER = "microsoft_teams_user"
        PHONE_NUMBER = "phone_number"
        TEAMS_EXTENSION_USER = "teams_extension_user"
        UNKNOWN = "unknown"


    class azure.communication.chat.CommunicationTokenCredential: implements ContextManager 

        @overload
        def __init__(
                self, 
                token: str, 
                *, 
                proactive_refresh: bool = False, 
                resource_endpoint: Optional[str] = ..., 
                scopes: Optional[list[str]] = ..., 
                token_credential: TokenCredential = ..., 
                token_refresher: Optional[Callable[[], AccessToken]] = ..., 
                **kwargs: Any
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                proactive_refresh: Optional[bool] = ..., 
                resource_endpoint: str, 
                scopes: Optional[list[str]] = ..., 
                token_credential: TokenCredential, 
                token_refresher: Callable[[], AccessToken] = ..., 
                **kwargs: Any
            ): ...

        def close(self) -> None: ...

        def get_token(
                self, 
                *scopes: any, 
                **kwargs
            ) -> AccessToken: ...


    class azure.communication.chat.CommunicationUserIdentifier:
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


    class azure.communication.chat.CommunicationUserProperties(TypedDict):
        key "id": str


    class azure.communication.chat.CreateChatThreadResult:
        chat_thread: ChatThreadProperties
        errors: Union[List[Tuple[ChatParticipant, ChatError]], None]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.communication.chat.MicrosoftTeamsAppIdentifier:
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


    class azure.communication.chat.MicrosoftTeamsAppProperties(TypedDict):
        key "app_id": str
        key "cloud": Union[CommunicationCloudEnvironment, str]


    class azure.communication.chat.MicrosoftTeamsUserIdentifier:
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


    class azure.communication.chat.MicrosoftTeamsUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "is_anonymous": bool
        key "user_id": str


    class azure.communication.chat.PhoneNumberIdentifier:
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


    class azure.communication.chat.PhoneNumberProperties(TypedDict):
        key "asserted_id": NotRequired[str]
        key "is_anonymous": NotRequired[bool]
        key "value": str


    class azure.communication.chat.SendChatMessageResult(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.communication.chat.TeamsExtensionUserIdentifier:
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


    class azure.communication.chat.TeamsExtensionUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "resource_id": str
        key "tenant_id": str
        key "user_id": str


    class azure.communication.chat.UnknownIdentifier:
        kind: Literal[CommunicationIdentifierKind.UNKNOWN] = CommunicationIdentifierKind.UNKNOWN
        properties: Mapping[str, Any]
        raw_id: str

        def __eq__(self, other): ...

        def __init__(self, identifier: str) -> None: ...


namespace azure.communication.chat.aio

    class azure.communication.chat.aio.ChatClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: CommunicationTokenCredential, 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_chat_thread(
                self, 
                topic: str, 
                *, 
                idempotency_token: str = ..., 
                thread_participants: List[ChatParticipant] = ..., 
                **kwargs
            ) -> CreateChatThreadResult: ...

        @distributed_trace_async
        async def delete_chat_thread(
                self, 
                thread_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_chat_thread_client(
                self, 
                thread_id: str, 
                **kwargs: Any
            ) -> ChatThreadClient: ...

        @distributed_trace
        def list_chat_threads(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatThreadItem]: ...


    class azure.communication.chat.aio.ChatThreadClient: implements AsyncContextManager 
        property thread_id: str    # Read-only
        thread_id: str

        def __init__(
                self, 
                endpoint: str, 
                credential: CommunicationTokenCredential, 
                thread_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def add_participants(
                self, 
                thread_participants: List[ChatParticipant], 
                **kwargs
            ) -> List[Tuple[ChatParticipant, ChatError]]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def delete_message(
                self, 
                message_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_message(
                self, 
                message_id: str, 
                **kwargs
            ) -> ChatMessage: ...

        @distributed_trace_async
        async def get_properties(self, **kwargs) -> ChatThreadProperties: ...

        @distributed_trace
        def list_messages(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                start_time: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_participants(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                skip: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatParticipant]: ...

        @distributed_trace
        def list_read_receipts(
                self, 
                *, 
                results_per_page: Optional[int] = ..., 
                skip: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatMessageReadReceipt]: ...

        @distributed_trace_async
        async def remove_participant(
                self, 
                identifier: CommunicationIdentifier, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def send_message(
                self, 
                content: str, 
                *, 
                chat_message_type: Union[str, ChatMessageType] = ..., 
                metadata: Dict[str, str] = ..., 
                sender_display_name: Optional[str] = ..., 
                **kwargs
            ) -> SendChatMessageResult: ...

        @distributed_trace_async
        async def send_read_receipt(
                self, 
                message_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def send_typing_notification(
                self, 
                *, 
                sender_display_name: Optional[str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_message(
                self, 
                message_id: str, 
                content: str = None, 
                *, 
                metadata: Dict[str, str] = ..., 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_topic(
                self, 
                topic: str = None, 
                **kwargs
            ) -> None: ...


    class azure.communication.chat.aio.CommunicationTokenCredential: implements AsyncContextManager 

        @overload
        def __init__(
                self, 
                token: str, 
                *, 
                proactive_refresh: bool = False, 
                resource_endpoint: Optional[str] = ..., 
                scopes: Optional[list[str]] = ..., 
                token_credential: AsyncTokenCredential = ..., 
                token_refresher: Optional[Callable[[], Awaitable[Any]]] = ..., 
                **kwargs: Any
            ): ...

        @overload
        def __init__(
                self, 
                *, 
                proactive_refresh: Optional[bool] = ..., 
                resource_endpoint: str, 
                scopes: Optional[list[str]] = ..., 
                token_credential: AsyncTokenCredential, 
                token_refresher: Callable[[], Awaitable[AccessToken]] = ..., 
                **kwargs: Any
            ): ...

        async def close(self) -> None: ...

        async def get_token(
                self, 
                *scopes: any, 
                **kwargs
            ) -> AccessToken: ...


```