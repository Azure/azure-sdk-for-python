```py
namespace azure.messaging.webpubsubchatservice

    class azure.messaging.webpubsubchatservice.BuiltInChatRoles:
        ROOM_MEMBER = room.member
        ROOM_OPERATOR = room.operator
        USER_NORMAL = user.normal


    class azure.messaging.webpubsubchatservice.WebPubSubChatServiceClient(WebPubSubChatServiceClientGenerated): implements ContextManager

        def __init__(
                self,
                endpoint: str,
                hub: str,
                credential: Union[TokenCredential, AzureKeyCredential],
                *,
                api_version: Optional[str] = ...,
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls,
                conn_str: str,
                hub: str,
                **kwargs: Any
            ) -> WebPubSubChatServiceClient: ...

        def close(self) -> None: ...

        @overload
        def create_or_replace_role(
                self,
                role_name: str,
                resource: ChatRole,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        def create_or_replace_role(
                self,
                role_name: str,
                resource: ChatRole,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        def create_or_replace_role(
                self,
                role_name: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        def create_or_replace_room(
                self,
                room_id: str,
                resource: ChatRoom,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        def create_or_replace_room(
                self,
                room_id: str,
                resource: ChatRoom,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        def create_or_replace_room(
                self,
                room_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: ChatRoomMember,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: ChatRoomMember,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        def create_or_replace_user(
                self,
                user_id: str,
                resource: ChatUser,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @overload
        def create_or_replace_user(
                self,
                user_id: str,
                resource: ChatUser,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @overload
        def create_or_replace_user(
                self,
                user_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @distributed_trace
        def delete_message(
                self,
                conversation_id: str,
                message_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_role(
                self,
                role_name: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_room(
                self,
                room_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_room_member(
                self,
                room_id: str,
                user_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_user(
                self,
                user_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_client_access_token(
                self,
                *,
                minutes_to_expire: int = 60,
                user_id: Optional[str] = ...,
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace
        def get_conversation(
                self,
                conversation_id: str,
                **kwargs: Any
            ) -> ChatConversation: ...

        @distributed_trace
        def get_role(
                self,
                role_name: str,
                **kwargs: Any
            ) -> ChatRole: ...

        @distributed_trace
        def get_room(
                self,
                room_id: str,
                **kwargs: Any
            ) -> ChatRoom: ...

        @distributed_trace
        def get_user(
                self,
                user_id: str,
                **kwargs: Any
            ) -> ChatUser: ...

        @distributed_trace
        def list_messages(
                self,
                conversation_id: str,
                *,
                earliest_message_id: Optional[str] = ...,
                latest_message_id: Optional[str] = ...,
                **kwargs: Any
            ) -> ItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_roles(
                self,
                *,
                continuation_token_parameter: Optional[str] = ...,
                **kwargs: Any
            ) -> ItemPaged[ChatRole]: ...

        @distributed_trace
        def list_room_members(
                self,
                room_id: str,
                *,
                continuation_token_parameter: Optional[str] = ...,
                **kwargs: Any
            ) -> ItemPaged[ChatRoomMember]: ...

        def send_request(
                self,
                request: HttpRequest,
                *,
                stream: bool = False,
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: ChatMessage,
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...

        @overload
        def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: ChatMessage,
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...

        @overload
        def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...


namespace azure.messaging.webpubsubchatservice.aio

    class azure.messaging.webpubsubchatservice.aio.WebPubSubChatServiceClient(WebPubSubChatServiceClientGenerated): implements AsyncContextManager

        def __init__(
                self,
                endpoint: str,
                hub: str,
                credential: Union[AsyncTokenCredential, AzureKeyCredential],
                *,
                api_version: Optional[str] = ...,
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls,
                conn_str: str,
                hub: str,
                **kwargs: Any
            ) -> WebPubSubChatServiceClient: ...

        async def close(self) -> None: ...

        @overload
        async def create_or_replace_role(
                self,
                role_name: str,
                resource: ChatRole,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        async def create_or_replace_role(
                self,
                role_name: str,
                resource: ChatRole,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        async def create_or_replace_role(
                self,
                role_name: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRole: ...

        @overload
        async def create_or_replace_room(
                self,
                room_id: str,
                resource: ChatRoom,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        async def create_or_replace_room(
                self,
                room_id: str,
                resource: ChatRoom,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        async def create_or_replace_room(
                self,
                room_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoom: ...

        @overload
        async def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: ChatRoomMember,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        async def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: ChatRoomMember,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        async def create_or_replace_room_member(
                self,
                room_id: str,
                user_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatRoomMember: ...

        @overload
        async def create_or_replace_user(
                self,
                user_id: str,
                resource: ChatUser,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @overload
        async def create_or_replace_user(
                self,
                user_id: str,
                resource: ChatUser,
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @overload
        async def create_or_replace_user(
                self,
                user_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatUser: ...

        @distributed_trace_async
        async def delete_message(
                self,
                conversation_id: str,
                message_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_role(
                self,
                role_name: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_room(
                self,
                room_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_room_member(
                self,
                room_id: str,
                user_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_user(
                self,
                user_id: str,
                *,
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_client_access_token(
                self,
                *,
                minutes_to_expire: int = 60,
                user_id: Optional[str] = ...,
                **kwargs: Any
            ) -> Dict[str, Any]: ...

        @distributed_trace_async
        async def get_conversation(
                self,
                conversation_id: str,
                **kwargs: Any
            ) -> ChatConversation: ...

        @distributed_trace_async
        async def get_role(
                self,
                role_name: str,
                **kwargs: Any
            ) -> ChatRole: ...

        @distributed_trace_async
        async def get_room(
                self,
                room_id: str,
                **kwargs: Any
            ) -> ChatRoom: ...

        @distributed_trace_async
        async def get_user(
                self,
                user_id: str,
                **kwargs: Any
            ) -> ChatUser: ...

        @distributed_trace
        def list_messages(
                self,
                conversation_id: str,
                *,
                earliest_message_id: Optional[str] = ...,
                latest_message_id: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_roles(
                self,
                *,
                continuation_token_parameter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncItemPaged[ChatRole]: ...

        @distributed_trace
        def list_room_members(
                self,
                room_id: str,
                *,
                continuation_token_parameter: Optional[str] = ...,
                **kwargs: Any
            ) -> AsyncItemPaged[ChatRoomMember]: ...

        def send_request(
                self,
                request: HttpRequest,
                *,
                stream: bool = False,
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: ChatMessage,
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...

        @overload
        async def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: ChatMessage,
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...

        @overload
        async def update_message(
                self,
                conversation_id: str,
                message_id: str,
                resource: IO[bytes],
                *,
                content_type: str = "application/merge-patch+json",
                etag: Optional[str] = ...,
                match_condition: Optional[MatchConditions] = ...,
                **kwargs: Any
            ) -> ChatMessage: ...


namespace azure.messaging.webpubsubchatservice.models

    class azure.messaging.webpubsubchatservice.models.ChatConversation(_Model):
        etag: str
        id: str
        parent_room: str

        @overload
        def __init__(
                self,
                *,
                parent_room: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatMessage(_Model):
        content: MessageContent
        created_at: datetime
        created_by: str
        etag: str
        id: str

        @overload
        def __init__(
                self,
                *,
                content: MessageContent,
                created_by: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ROOM_HISTORY = "room.history"
        ROOM_INVITE = "room.invite"
        ROOM_PUBLISH_MESSAGE = "room.publish_message"
        ROOM_REMOVE_USER = "room.remove_user"
        USER_CREATE_ROOM = "user.create_room"
        USER_FETCH_ALL_ROOMS = "user.fetch_all_rooms"


    class azure.messaging.webpubsubchatservice.models.ChatRole(_Model):
        etag: str
        name: str
        permissions: list[Union[str, ChatPermission]]

        @overload
        def __init__(
                self,
                *,
                permissions: list[Union[str, ChatPermission]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatRoom(_Model):
        default_conversation: str
        etag: str
        id: str
        title: str

        @overload
        def __init__(
                self,
                *,
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatRoomMember(_Model):
        etag: str
        role_name: str
        user_id: str

        @overload
        def __init__(
                self,
                *,
                role_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatUser(_Model):
        etag: str
        id: str
        kind: str
        nickname: str

        @overload
        def __init__(
                self,
                *,
                kind: str,
                nickname: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatUserKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUMAN = "Human"


    class azure.messaging.webpubsubchatservice.models.HumanChatUser(ChatUser, discriminator='Human'):
        etag: str
        id: str
        kind: Literal[ChatUserKind.HUMAN]
        nickname: str
        role_name: str

        @overload
        def __init__(
                self,
                *,
                nickname: str,
                role_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.MessageContent(_Model):
        binary: Optional[bytes]
        text: Optional[str]

        @overload
        def __init__(
                self,
                *,
                binary: Optional[bytes] = ...,
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.messaging.webpubsubchatservice.types

    class azure.messaging.webpubsubchatservice.types.ChatMessage(TypedDict, total=False):
        key "content": Required[MessageContent]
        key "createdAt": Required[str]
        key "createdBy": Required[str]
        key "etag": Required[str]
        key "id": Required[str]
        content: MessageContent
        createdAt: str
        createdBy: str
        etag: str
        id: str


    class azure.messaging.webpubsubchatservice.types.ChatRole(TypedDict, total=False):
        key "etag": Required[str]
        key "name": Required[str]
        key "permissions": Required[list[Union[str, ChatPermission]]]
        etag: str
        name: str
        permissions: list[Union[str, ChatPermission]]


    class azure.messaging.webpubsubchatservice.types.ChatRoom(TypedDict, total=False):
        key "defaultConversation": Required[str]
        key "etag": Required[str]
        key "id": Required[str]
        key "title": Required[str]
        defaultConversation: str
        etag: str
        id: str
        title: str


    class azure.messaging.webpubsubchatservice.types.ChatRoomMember(TypedDict, total=False):
        key "etag": Required[str]
        key "roleName": Required[str]
        key "userId": Required[str]
        etag: str
        roleName: str
        userId: str


    class azure.messaging.webpubsubchatservice.types.ChatUser(TypedDict, total=False):
        key "etag": Required[str]
        key "id": Required[str]
        key "kind": Required[Literal[ChatUserKind.HUMAN]]
        key "nickname": Required[str]
        key "roleName": Required[str]
        etag: str
        id: str
        kind: Literal[ChatUserKind.HUMAN]
        nickname: str
        roleName: str


    class azure.messaging.webpubsubchatservice.types.ChatUserKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUMAN = "Human"


    class azure.messaging.webpubsubchatservice.types.HumanChatUser(TypedDict, total=False):
        key "etag": Required[str]
        key "id": Required[str]
        key "kind": Required[Literal[ChatUserKind.HUMAN]]
        key "nickname": Required[str]
        key "roleName": Required[str]
        etag: str
        id: str
        kind: Literal[ChatUserKind.HUMAN]
        nickname: str
        roleName: str


    class azure.messaging.webpubsubchatservice.types.MessageContent(TypedDict, total=False):
        key "binary": str
        key "text": str
        binary: str
        text: str


```