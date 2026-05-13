```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.messaging.webpubsubservice

    class azure.messaging.webpubsubservice.WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                hub: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                hub: str, 
                **kwargs: Any
            ) -> WebPubSubServiceClient: ...

        @distributed_trace
        def add_connection_to_group(
                self, 
                group: str, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_connections_to_groups(
                self, 
                groups_to_add: AddToGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_connections_to_groups(
                self, 
                groups_to_add: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_connections_to_groups(
                self, 
                groups_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def add_user_to_group(
                self, 
                group: str, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def check_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        def close(self) -> None: ...

        @distributed_trace
        def close_all_connections(
                self, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def close_connection(
                self, 
                connection_id: str, 
                *, 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def close_group_connections(
                self, 
                group: str, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def close_user_connections(
                self, 
                user_id: str, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def connection_exists(
                self, 
                connection_id: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def generate_client_token(
                self, 
                *, 
                client_type: Optional[Union[str, WebPubSubClientType]] = ..., 
                group: Optional[list[str]] = ..., 
                minutes_to_expire: Optional[int] = ..., 
                role: Optional[list[str]] = ..., 
                user_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ClientTokenResponse: ...

        @distributed_trace
        def get_client_access_token(
                self, 
                *, 
                client_protocol: Optional[str] = "Default", 
                groups: list[str] = ..., 
                minutes_to_expire: int = ..., 
                roles: list[str] = ..., 
                user_id: str = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_service_status(self, **kwargs: Any) -> bool: ...

        @distributed_trace
        def grant_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def group_exists(
                self, 
                group: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def has_permission(
                self, 
                permission: str, 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list_connections(
                self, 
                *, 
                group: str, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GroupMember]: ...

        @distributed_trace
        def list_connections_in_group(
                self, 
                group: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[GroupMember]: ...

        @distributed_trace
        def remove_connection_from_all_groups(
                self, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def remove_connection_from_group(
                self, 
                group: str, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_connections_from_groups(
                self, 
                groups_to_remove: RemoveFromGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_connections_from_groups(
                self, 
                groups_to_remove: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def remove_connections_from_groups(
                self, 
                groups_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def remove_user_from_all_groups(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def remove_user_from_group(
                self, 
                group: str, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def revoke_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def send_to_all(
                self, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_all(
                self, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_all(
                self, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_connection(
                self, 
                connection_id: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_connection(
                self, 
                connection_id: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_connection(
                self, 
                connection_id: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_group(
                self, 
                group: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_user(
                self, 
                user_id: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_user(
                self, 
                user_id: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_to_user(
                self, 
                user_id: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def user_exists(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> bool: ...


namespace azure.messaging.webpubsubservice.aio

    class azure.messaging.webpubsubservice.aio.WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                hub: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                connection_string: str, 
                hub: str, 
                **kwargs: Any
            ) -> WebPubSubServiceClient: ...

        @distributed_trace_async
        async def add_connection_to_group(
                self, 
                group: str, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_connections_to_groups(
                self, 
                groups_to_add: AddToGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_connections_to_groups(
                self, 
                groups_to_add: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_connections_to_groups(
                self, 
                groups_to_add: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def add_user_to_group(
                self, 
                group: str, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def check_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def close_all_connections(
                self, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def close_connection(
                self, 
                connection_id: str, 
                *, 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def close_group_connections(
                self, 
                group: str, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def close_user_connections(
                self, 
                user_id: str, 
                *, 
                excluded: Optional[list[str]] = ..., 
                reason: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def connection_exists(
                self, 
                connection_id: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def generate_client_token(
                self, 
                *, 
                client_type: Optional[Union[str, WebPubSubClientType]] = ..., 
                group: Optional[list[str]] = ..., 
                minutes_to_expire: Optional[int] = ..., 
                role: Optional[list[str]] = ..., 
                user_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> ClientTokenResponse: ...

        @distributed_trace_async
        async def get_client_access_token(
                self, 
                *, 
                api_version: str = ..., 
                client_protocol: Optional[str] = "Default", 
                groups: Optional[List[str]] = ..., 
                jwt_headers: Dict[str, Any] = ..., 
                minutes_to_expire: Optional[int] = 60, 
                roles: Optional[List[str]] = ..., 
                user_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_service_status(self, **kwargs: Any) -> bool: ...

        @distributed_trace_async
        async def grant_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def group_exists(
                self, 
                group: str, 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace_async
        async def has_permission(
                self, 
                permission: str, 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> bool: ...

        @distributed_trace
        def list_connections(
                self, 
                *, 
                group: str, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupMember]: ...

        @distributed_trace
        def list_connections_in_group(
                self, 
                group: str, 
                *, 
                continuation_token_parameter: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[GroupMember]: ...

        @distributed_trace_async
        async def remove_connection_from_all_groups(
                self, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def remove_connection_from_group(
                self, 
                group: str, 
                connection_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_connections_from_groups(
                self, 
                groups_to_remove: RemoveFromGroupsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_connections_from_groups(
                self, 
                groups_to_remove: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def remove_connections_from_groups(
                self, 
                groups_to_remove: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def remove_user_from_all_groups(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def remove_user_from_group(
                self, 
                group: str, 
                user_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def revoke_permission(
                self, 
                permission: Union[str, WebPubSubPermission], 
                connection_id: str, 
                *, 
                target_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def send_to_all(
                self, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_all(
                self, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_all(
                self, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_connection(
                self, 
                connection_id: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_connection(
                self, 
                connection_id: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_connection(
                self, 
                connection_id: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_group(
                self, 
                group: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                excluded: Optional[List[str]] = ..., 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_user(
                self, 
                user_id: str, 
                message: Union[str, JSON], 
                *, 
                content_type: Optional[str] = "application/json", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_user(
                self, 
                user_id: str, 
                message: str, 
                *, 
                content_type: Optional[str] = "text/plain", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_to_user(
                self, 
                user_id: str, 
                message: IO, 
                *, 
                content_type: Optional[str] = "application/octet-stream", 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def user_exists(
                self, 
                user_id: str, 
                **kwargs: Any
            ) -> bool: ...


namespace azure.messaging.webpubsubservice.models

    class azure.messaging.webpubsubservice.models.AddToGroupsRequest(_Model):
        filter: Optional[str]
        groups: list[str]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                groups: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.ClientTokenResponse(_Model):
        token: str

        @overload
        def __init__(
                self, 
                *, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.ErrorDetail(_Model):
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        inner: Optional[InnerError]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorDetail]] = ..., 
                inner: Optional[InnerError] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.GroupMember(_Model):
        connection_id: str
        user_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                user_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.InnerError(_Model):
        code: Optional[str]
        inner: Optional[InnerError]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                inner: Optional[InnerError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.MessageContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_JSON = "application/json"
        APPLICATION_OCTET_STREAM = "application/octet-stream"
        TEXT_PLAIN = "text/plain"


    class azure.messaging.webpubsubservice.models.RemoveFromGroupsRequest(_Model):
        filter: Optional[str]
        groups: list[str]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                groups: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.messaging.webpubsubservice.models.ResponseContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_JSON = "application/json"
        TEXT_JSON = "text/json"
        TEXT_PLAIN = "text/plain"


    class azure.messaging.webpubsubservice.models.WebPubSubClientType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        MQTT = "MQTT"


    class azure.messaging.webpubsubservice.models.WebPubSubPermission(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JOIN_LEAVE_GROUP = "joinLeaveGroup"
        SEND_TO_GROUP = "sendToGroup"


```