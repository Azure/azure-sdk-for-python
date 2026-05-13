```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.messages

    class azure.communication.messages.MessageTemplateClient(MessageTemplateClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> MessageTemplateClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def list_templates(
                self, 
                channel_id: str, 
                **kwargs: Any
            ) -> Iterable[MessageTemplateItem]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.communication.messages.NotificationMessagesClient(NotificationMessagesClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> NotificationMessagesClient: ...

        def close(self) -> None: ...

        @distributed_trace
        def download_media(
                self, 
                id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def send(
                self, 
                body: NotificationContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        @overload
        def send(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        @overload
        def send(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.communication.messages.aio

    class azure.communication.messages.aio.MessageTemplateClient(MessageTemplateClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> MessageTemplateClient: ...

        async def close(self) -> None: ...

        @distributed_trace
        def list_templates(
                self, 
                channel_id: str, 
                **kwargs: Any
            ) -> AsyncIterable[MessageTemplateItem]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.communication.messages.aio.NotificationMessagesClient(NotificationMessagesClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> NotificationMessagesClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def download_media(
                self, 
                id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def send(
                self, 
                body: NotificationContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        @overload
        async def send(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        @overload
        async def send(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SendMessageResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.communication.messages.models

    class azure.communication.messages.models.ActionBindings(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ActionGroup(Model):
        items_property: List[ActionGroupItem]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                items_property: List[ActionGroupItem], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ActionGroupContent(MessageContent, discriminator='group'):
        groups: List[ActionGroup]
        kind: Literal[MessageContentKind.GROUP]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                groups: List[ActionGroup], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ActionGroupItem(Model):
        description: str
        id: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.AudioNotificationContent(NotificationContent, discriminator='audio'):
        channel_registration_id: str
        kind: Literal[CommunicationMessageKind.AUDIO]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ButtonContent(Model):
        id: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ButtonSetContent(MessageContent, discriminator='buttonSet'):
        buttons: List[ButtonContent]
        kind: Literal[MessageContentKind.BUTTON_SET]

        @overload
        def __init__(
                self, 
                *, 
                buttons: List[ButtonContent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.CommunicationMessageKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO = "audio"
        DOCUMENT = "document"
        IMAGE = "image"
        IMAGE_V0 = "image_v0"
        INTERACTIVE = "interactive"
        REACTION = "reaction"
        STICKER = "sticker"
        TEMPLATE = "template"
        TEXT = "text"
        VIDEO = "video"


    class azure.communication.messages.models.CommunicationMessagesChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WHATSAPP = "whatsApp"


    class azure.communication.messages.models.DocumentMessageContent(MessageContent, discriminator='document'):
        kind: Literal[MessageContentKind.DOCUMENT]
        media_uri: str

        @overload
        def __init__(
                self, 
                *, 
                media_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.DocumentNotificationContent(NotificationContent, discriminator='document'):
        caption: Optional[str]
        channel_registration_id: str
        file_name: Optional[str]
        kind: Literal[CommunicationMessageKind.DOCUMENT]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[str] = ..., 
                channel_registration_id: str, 
                file_name: Optional[str] = ..., 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ImageMessageContent(MessageContent, discriminator='image'):
        kind: Literal[MessageContentKind.IMAGE]
        media_uri: str

        @overload
        def __init__(
                self, 
                *, 
                media_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ImageNotificationContent(NotificationContent, discriminator='image'):
        channel_registration_id: str
        content: Optional[str]
        kind: Literal[CommunicationMessageKind.IMAGE]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                content: Optional[str] = ..., 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.InteractiveMessage(Model):
        action: ActionBindings
        body: TextMessageContent
        footer: Optional[TextMessageContent]
        header: Optional[MessageContent]

        @overload
        def __init__(
                self, 
                *, 
                action: ActionBindings, 
                body: TextMessageContent, 
                footer: Optional[TextMessageContent] = ..., 
                header: Optional[MessageContent] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.InteractiveNotificationContent(NotificationContent, discriminator='interactive'):
        channel_registration_id: str
        interactive_message: InteractiveMessage
        kind: Literal[CommunicationMessageKind.INTERACTIVE]
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                interactive_message: InteractiveMessage, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.LinkContent(MessageContent, discriminator='url'):
        kind: Literal[MessageContentKind.URL]
        title: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                title: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MediaNotificationContent(NotificationContent, discriminator='image_v0'):
        channel_registration_id: str
        content: Optional[str]
        kind: Literal[CommunicationMessageKind.IMAGE_V0]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                content: Optional[str] = ..., 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageActionBindingKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WHATS_APP_BUTTON_ACTION = "whatsAppButtonAction"
        WHATS_APP_LIST_ACTION = "whatsAppListAction"
        WHATS_APP_URL_ACTION = "whatsAppUrlAction"


    class azure.communication.messages.models.MessageContent(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageContentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUTTON_SET = "buttonSet"
        DOCUMENT = "document"
        GROUP = "group"
        IMAGE = "image"
        TEXT = "text"
        URL = "url"
        VIDEO = "video"


    class azure.communication.messages.models.MessageReceipt(Model):
        message_id: str
        to: str

        @overload
        def __init__(
                self, 
                *, 
                message_id: str, 
                to: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplate(Model):
        bindings: Optional[MessageTemplateBindings]
        language: str
        name: str
        template_values: Optional[List[MessageTemplateValue]]

        @overload
        def __init__(
                self, 
                *, 
                bindings: Optional[MessageTemplateBindings] = ..., 
                language: str, 
                name: str, 
                template_values: Optional[List[MessageTemplateValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateBindings(Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateBindingsKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WHATSAPP = "whatsApp"


    class azure.communication.messages.models.MessageTemplateDocument(MessageTemplateValue, discriminator='document'):
        caption: Optional[str]
        file_name: Optional[str]
        kind: Literal[MessageTemplateValueKind.DOCUMENT]
        name: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                name: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateImage(MessageTemplateValue, discriminator='image'):
        caption: Optional[str]
        file_name: Optional[str]
        kind: Literal[MessageTemplateValueKind.IMAGE]
        name: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                name: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateItem(Model):
        kind: str
        language: str
        name: str
        status: Union[str, MessageTemplateStatus]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                language: str, 
                status: Union[str, MessageTemplateStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateLocation(MessageTemplateValue, discriminator='location'):
        address: Optional[str]
        kind: Literal[MessageTemplateValueKind.LOCATION]
        latitude: float
        location_name: Optional[str]
        longitude: float
        name: str

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                latitude: float, 
                location_name: Optional[str] = ..., 
                longitude: float, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateQuickAction(MessageTemplateValue, discriminator='quickAction'):
        kind: Literal[MessageTemplateValueKind.QUICK_ACTION]
        name: str
        payload: Optional[str]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                payload: Optional[str] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "approved"
        PAUSED = "paused"
        PENDING = "pending"
        REJECTED = "rejected"


    class azure.communication.messages.models.MessageTemplateText(MessageTemplateValue, discriminator='text'):
        kind: Literal[MessageTemplateValueKind.TEXT]
        name: str
        text: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateValue(Model):
        kind: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.MessageTemplateValueKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOCUMENT = "document"
        IMAGE = "image"
        LOCATION = "location"
        QUICK_ACTION = "quickAction"
        TEXT = "text"
        VIDEO = "video"


    class azure.communication.messages.models.MessageTemplateVideo(MessageTemplateValue, discriminator='video'):
        caption: Optional[str]
        file_name: Optional[str]
        kind: Literal[MessageTemplateValueKind.VIDEO]
        name: str
        url: str

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                name: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.NotificationContent(Model):
        channel_registration_id: str
        kind: str
        to: List[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                kind: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.ReactionNotificationContent(NotificationContent, discriminator='reaction'):
        channel_registration_id: str
        emoji: str
        kind: Literal[CommunicationMessageKind.REACTION]
        message_id: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                emoji: str, 
                message_id: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.RepeatabilityResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "accepted"
        REJECTED = "rejected"


    class azure.communication.messages.models.SendMessageResult(Model):
        receipts: List[MessageReceipt]

        @overload
        def __init__(
                self, 
                *, 
                receipts: List[MessageReceipt]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.StickerNotificationContent(NotificationContent, discriminator='sticker'):
        channel_registration_id: str
        kind: Literal[CommunicationMessageKind.STICKER]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.TemplateNotificationContent(NotificationContent, discriminator='template'):
        channel_registration_id: str
        kind: Literal[CommunicationMessageKind.TEMPLATE]
        template: MessageTemplate
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                template: MessageTemplate, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.TextMessageContent(MessageContent, discriminator='text'):
        kind: Literal[MessageContentKind.TEXT]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.TextNotificationContent(NotificationContent, discriminator='text'):
        channel_registration_id: str
        content: str
        kind: Literal[CommunicationMessageKind.TEXT]
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                channel_registration_id: str, 
                content: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.VideoMessageContent(MessageContent, discriminator='video'):
        kind: Literal[MessageContentKind.VIDEO]
        media_uri: str

        @overload
        def __init__(
                self, 
                *, 
                media_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.VideoNotificationContent(NotificationContent, discriminator='video'):
        caption: Optional[str]
        channel_registration_id: str
        kind: Literal[CommunicationMessageKind.VIDEO]
        media_uri: str
        to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                caption: Optional[str] = ..., 
                channel_registration_id: str, 
                media_uri: str, 
                to: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppButtonActionBindings(ActionBindings, discriminator='whatsAppButtonAction'):
        content: ButtonSetContent
        kind: Literal[MessageActionBindingKind.WHATS_APP_BUTTON_ACTION]

        @overload
        def __init__(
                self, 
                *, 
                content: ButtonSetContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppListActionBindings(ActionBindings, discriminator='whatsAppListAction'):
        content: ActionGroupContent
        kind: Literal[MessageActionBindingKind.WHATS_APP_LIST_ACTION]

        @overload
        def __init__(
                self, 
                *, 
                content: ActionGroupContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppMessageButtonSubType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUICK_REPLY = "quickReply"
        URL = "url"


    class azure.communication.messages.models.WhatsAppMessageTemplateBindings(MessageTemplateBindings, discriminator='whatsApp'):
        body: Optional[List[WhatsAppMessageTemplateBindingsComponent]]
        buttons: Optional[List[WhatsAppMessageTemplateBindingsButton]]
        footer: Optional[List[WhatsAppMessageTemplateBindingsComponent]]
        header: Optional[List[WhatsAppMessageTemplateBindingsComponent]]
        kind: Literal[MessageTemplateBindingsKind.WHATSAPP]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[List[WhatsAppMessageTemplateBindingsComponent]] = ..., 
                buttons: Optional[List[WhatsAppMessageTemplateBindingsButton]] = ..., 
                footer: Optional[List[WhatsAppMessageTemplateBindingsComponent]] = ..., 
                header: Optional[List[WhatsAppMessageTemplateBindingsComponent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppMessageTemplateBindingsButton(Model):
        ref_value: str
        sub_type: Union[str, WhatsAppMessageButtonSubType]

        @overload
        def __init__(
                self, 
                *, 
                ref_value: str, 
                sub_type: Union[str, WhatsAppMessageButtonSubType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppMessageTemplateBindingsComponent(Model):
        ref_value: str

        @overload
        def __init__(
                self, 
                *, 
                ref_value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppMessageTemplateItem(MessageTemplateItem, discriminator='whatsApp'):
        content: Optional[Any]
        kind: Literal[CommunicationMessagesChannel.WHATSAPP]
        language: str
        name: str
        status: Union[str, MessageTemplateStatus]

        @overload
        def __init__(
                self, 
                *, 
                content: Optional[Any] = ..., 
                language: str, 
                status: Union[str, MessageTemplateStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.messages.models.WhatsAppUrlActionBindings(ActionBindings, discriminator='whatsAppUrlAction'):
        content: LinkContent
        kind: Literal[MessageActionBindingKind.WHATS_APP_URL_ACTION]

        @overload
        def __init__(
                self, 
                *, 
                content: LinkContent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```