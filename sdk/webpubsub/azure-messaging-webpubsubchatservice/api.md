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
                resource: ChatRoleCreateOrReplace,
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
                resource: ChatRoleCreateOrReplace,
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
                resource: ChatRoomCreateOrReplace,
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
                resource: ChatRoomCreateOrReplace,
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
                resource: ChatRoomMemberCreateOrReplace,
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
                resource: ChatRoomMemberCreateOrReplace,
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
        def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicCreateOrReplace,
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicCreateOrReplace,
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        def create_or_replace_user(
                self, 
                user_id: str, 
                resource: ChatUserCreateOrReplace,
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
                resource: ChatUserCreateOrReplace,
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
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'topic_id', 'etag', 'match_condition']}, api_versions_list=['2026-08-01-preview'])
        def delete_topic(
                self, 
                room_id: str, 
                topic_id: str, 
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
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'topic_id', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def get_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                **kwargs: Any
            ) -> ChatTopic: ...

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
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_roles(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatRole]: ...

        @distributed_trace
        def list_room_members(
                self, 
                room_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatRoomMember]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_rooms(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatRoom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'user_id', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_rooms_for_user(
                self, 
                user_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatUserRoom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_topics(
                self, 
                room_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatTopic]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_users(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ChatUser]: ...

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
                resource: ChatMessageUpdate,
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
                resource: ChatMessageUpdate,
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

        @overload
        def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicUpdate,
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicUpdate,
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...


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
                resource: ChatRoleCreateOrReplace,
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
                resource: ChatRoleCreateOrReplace,
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
                resource: ChatRoomCreateOrReplace,
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
                resource: ChatRoomCreateOrReplace,
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
                resource: ChatRoomMemberCreateOrReplace,
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
                resource: ChatRoomMemberCreateOrReplace,
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
        async def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicCreateOrReplace,
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        async def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicCreateOrReplace,
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        async def create_or_replace_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        async def create_or_replace_user(
                self, 
                user_id: str, 
                resource: ChatUserCreateOrReplace,
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
                resource: ChatUserCreateOrReplace,
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
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'topic_id', 'etag', 'match_condition']}, api_versions_list=['2026-08-01-preview'])
        async def delete_topic(
                self, 
                room_id: str, 
                topic_id: str, 
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
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'topic_id', 'accept']}, api_versions_list=['2026-08-01-preview'])
        async def get_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                **kwargs: Any
            ) -> ChatTopic: ...

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
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatMessage]: ...

        @distributed_trace
        def list_roles(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatRole]: ...

        @distributed_trace
        def list_room_members(
                self, 
                room_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatRoomMember]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_rooms(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatRoom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'user_id', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_rooms_for_user(
                self, 
                user_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatUserRoom]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'room_id', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_topics(
                self, 
                room_id: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatTopic]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-08-01-preview', params_added_on={'2026-08-01-preview': ['api_version', 'hub', 'max_page_size', 'continuation_token_parameter', 'accept']}, api_versions_list=['2026-08-01-preview'])
        def list_users(
                self, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                max_page_size: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ChatUser]: ...

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
                resource: ChatMessageUpdate,
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
                resource: ChatMessageUpdate,
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

        @overload
        async def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicUpdate,
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        async def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: ChatTopicUpdate,
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...

        @overload
        async def update_topic(
                self, 
                room_id: str, 
                topic_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ChatTopic: ...


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


    class azure.messaging.webpubsubchatservice.models.ChatMessageUpdate(_Model):
        content: Optional[MessageContent]
        created_by: Optional[str]

        @overload
        def __init__(
                self,
                *,
                content: Optional[MessageContent] = ...,
                created_by: Optional[str] = ...
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


    class azure.messaging.webpubsubchatservice.models.ChatRoleCreateOrReplace(_Model):
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


    class azure.messaging.webpubsubchatservice.models.ChatRoomCreateOrReplace(_Model):
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


    class azure.messaging.webpubsubchatservice.models.ChatRoomMemberCreateOrReplace(_Model):
        role_name: str

        @overload
        def __init__(
                self,
                *,
                role_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatTopic(_Model):
        conversation_id: str
        created_at: datetime
        created_by: str
        etag: str
        id: str
        state: Union[str, ChatTopicState]
        title: str

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, ChatTopicState], 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatTopicCreateOrReplace(_Model):
        state: Optional[Union[str, ChatTopicState]]
        title: str

        @overload
        def __init__(
                self,
                *,
                state: Optional[Union[str, ChatTopicState]] = ...,
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubchatservice.models.ChatTopicState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARCHIVED = "Archived"
        NORMAL = "Normal"
        SOFT_DELETED = "SoftDeleted"


    class azure.messaging.webpubsubchatservice.models.ChatTopicUpdate(_Model):
        state: Optional[Union[str, ChatTopicState]]
        title: Optional[str]

        @overload
        def __init__(
                self,
                *,
                state: Optional[Union[str, ChatTopicState]] = ...,
                title: Optional[str] = ...
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


    class azure.messaging.webpubsubchatservice.models.ChatUserCreateOrReplace(_Model):
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


    class azure.messaging.webpubsubchatservice.models.ChatUserRoom(_Model):
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


    class azure.messaging.webpubsubchatservice.models.HumanChatUserCreateOrReplace(ChatUserCreateOrReplace, discriminator='Human'):
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

    class azure.messaging.webpubsubchatservice.types.ChatMessageUpdate(TypedDict, total=False):
        key "content": ForwardRef('MessageContent', module='types')
        key "createdBy": str
        content: MessageContent
        createdBy: str


    class azure.messaging.webpubsubchatservice.types.ChatRoleCreateOrReplace(TypedDict, total=False):
        key "permissions": Required[list[Union[str, ChatPermission]]]
        permissions: list[Union[str, ChatPermission]]


    class azure.messaging.webpubsubchatservice.types.ChatRoomCreateOrReplace(TypedDict, total=False):
        key "title": Required[str]
        title: str


    class azure.messaging.webpubsubchatservice.types.ChatRoomMemberCreateOrReplace(TypedDict, total=False):
        key "roleName": Required[str]
        roleName: str


    class azure.messaging.webpubsubchatservice.types.ChatTopicCreateOrReplace(TypedDict, total=False):
        key "state": Union[str, ChatTopicState]
        key "title": Required[str]
        state: Union[str, ChatTopicState]
        title: str


    class azure.messaging.webpubsubchatservice.types.ChatTopicUpdate(TypedDict, total=False):
        key "state": Union[str, ChatTopicState]
        key "title": str
        state: Union[str, ChatTopicState]
        title: str


    class azure.messaging.webpubsubchatservice.types.ChatUserCreateOrReplace(TypedDict, total=False):
        key "kind": Required[Literal[ChatUserKind.HUMAN]]
        key "nickname": Required[str]
        key "roleName": Required[str]
        kind: Literal[ChatUserKind.HUMAN]
        nickname: str
        roleName: str


    class azure.messaging.webpubsubchatservice.types.ChatUserKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUMAN = "Human"


    class azure.messaging.webpubsubchatservice.types.HumanChatUserCreateOrReplace(TypedDict, total=False):
        key "kind": Required[Literal[ChatUserKind.HUMAN]]
        key "nickname": Required[str]
        key "roleName": Required[str]
        kind: Literal[ChatUserKind.HUMAN]
        nickname: str
        roleName: str


    class azure.messaging.webpubsubchatservice.types.MessageContent(TypedDict, total=False):
        key "binary": str
        key "text": str
        binary: str
        text: str


```
