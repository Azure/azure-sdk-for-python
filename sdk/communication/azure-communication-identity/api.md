```py
namespace azure.communication.identity

    class azure.communication.identity.IdentityClient: implements ContextManager 
        identity_operations: IdentityOperationsOperations
        teams_extension_operations: TeamsExtensionOperationsOperations
        teams_user_operations: TeamsUserOperationsOperations

        def __init__(
                self, 
                endpoint: str, 
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


namespace azure.communication.identity.aio

    class azure.communication.identity.aio.IdentityClient: implements AsyncContextManager 
        identity_operations: IdentityOperationsOperations
        teams_extension_operations: TeamsExtensionOperationsOperations
        teams_user_operations: TeamsUserOperationsOperations

        def __init__(
                self, 
                endpoint: str, 
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


namespace azure.communication.identity.aio.operations

    class azure.communication.identity.aio.operations.IdentityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                body: Optional[CommunicationIdentityCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        async def create(
                self, 
                body: Optional[CommunicationIdentityCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        async def create(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def issue_access_token(
                self, 
                id: str, 
                body: CommunicationIdentityAccessTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        async def issue_access_token(
                self, 
                id: str, 
                body: CommunicationIdentityAccessTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        async def issue_access_token(
                self, 
                id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @distributed_trace_async
        async def revoke_access_tokens(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.identity.aio.operations.TeamsExtensionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def exchange_token(
                self, 
                body: TeamsExtensionExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        async def exchange_token(
                self, 
                body: TeamsExtensionExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        async def exchange_token(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @distributed_trace_async
        async def get_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        async def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: TeamsExtensionAssignmentCreateOrUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        async def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: TeamsExtensionAssignmentCreateOrUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        async def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...


    class azure.communication.identity.aio.operations.TeamsUserOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def exchange_teams_user_access_token(
                self, 
                body: TeamsUserExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        async def exchange_teams_user_access_token(
                self, 
                body: TeamsUserExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        async def exchange_teams_user_access_token(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...


namespace azure.communication.identity.models

    class azure.communication.identity.models.CommunicationError(_Model):
        code: str
        details: Optional[list[CommunicationError]]
        inner_error: Optional[CommunicationError]
        message: str
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationErrorResponse(_Model):
        error: CommunicationError

        @overload
        def __init__(
                self, 
                *, 
                error: CommunicationError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentity(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentityAccessToken(_Model):
        expires_on: datetime
        token: str

        @overload
        def __init__(
                self, 
                *, 
                expires_on: datetime, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentityAccessTokenRequest(_Model):
        expires_in_minutes: Optional[int]
        scopes: list[Union[str, CommunicationIdentityTokenScope]]

        @overload
        def __init__(
                self, 
                *, 
                expires_in_minutes: Optional[int] = ..., 
                scopes: list[Union[str, CommunicationIdentityTokenScope]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentityAccessTokenResult(_Model):
        access_token: Optional[CommunicationIdentityAccessToken]
        identity: CommunicationIdentity

        @overload
        def __init__(
                self, 
                *, 
                access_token: Optional[CommunicationIdentityAccessToken] = ..., 
                identity: CommunicationIdentity
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentityCreateRequest(_Model):
        create_token_with_scopes: Optional[list[Union[str, CommunicationIdentityTokenScope]]]
        expires_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                create_token_with_scopes: Optional[list[Union[str, CommunicationIdentityTokenScope]]] = ..., 
                expires_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.CommunicationIdentityTokenScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT = "chat"
        CHAT_JOIN = "chat.join"
        CHAT_JOIN_LIMITED = "chat.join.limited"
        VOIP = "voip"
        VOIP_JOIN = "voip.join"


    class azure.communication.identity.models.TeamsExtensionAssignmentCreateOrUpdateRequest(_Model):
        client_ids: Optional[list[str]]
        principal_type: Union[str, TeamsExtensionPrincipalType]

        @overload
        def __init__(
                self, 
                *, 
                client_ids: Optional[list[str]] = ..., 
                principal_type: Union[str, TeamsExtensionPrincipalType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.TeamsExtensionAssignmentResponse(_Model):
        client_ids: Optional[list[str]]
        object_id: str
        principal_type: Union[str, TeamsExtensionPrincipalType]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_ids: Optional[list[str]] = ..., 
                object_id: str, 
                principal_type: Union[str, TeamsExtensionPrincipalType], 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.identity.models.TeamsExtensionExchangeTokenRequest(_Model):


    class azure.communication.identity.models.TeamsExtensionPrincipalType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE_ACCOUNT = "resourceAccount"
        USER = "user"


    class azure.communication.identity.models.TeamsUserExchangeTokenRequest(_Model):
        app_id: str
        token: str
        user_id: str

        @overload
        def __init__(
                self, 
                *, 
                app_id: str, 
                token: str, 
                user_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.communication.identity.operations

    class azure.communication.identity.operations.IdentityOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                body: Optional[CommunicationIdentityCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        def create(
                self, 
                body: Optional[CommunicationIdentityCreateRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        def create(
                self, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def issue_access_token(
                self, 
                id: str, 
                body: CommunicationIdentityAccessTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        def issue_access_token(
                self, 
                id: str, 
                body: CommunicationIdentityAccessTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        def issue_access_token(
                self, 
                id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @distributed_trace
        def revoke_access_tokens(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.identity.operations.TeamsExtensionOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def exchange_token(
                self, 
                body: TeamsExtensionExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        def exchange_token(
                self, 
                body: TeamsExtensionExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @overload
        def exchange_token(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessTokenResult: ...

        @distributed_trace
        def get_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: TeamsExtensionAssignmentCreateOrUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: TeamsExtensionAssignmentCreateOrUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...

        @overload
        def upsert_assignment(
                self, 
                tenant_id: str, 
                object_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TeamsExtensionAssignmentResponse: ...


    class azure.communication.identity.operations.TeamsUserOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def exchange_teams_user_access_token(
                self, 
                body: TeamsUserExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        def exchange_teams_user_access_token(
                self, 
                body: TeamsUserExchangeTokenRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...

        @overload
        def exchange_teams_user_access_token(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommunicationIdentityAccessToken: ...


namespace azure.communication.identity.types

    class azure.communication.identity.types.CommunicationIdentityAccessTokenRequest(TypedDict, total=False):
        key "expiresInMinutes": int
        key "scopes": Required[list[Union[str, CommunicationIdentityTokenScope]]]
        expiresInMinutes: int
        scopes: list[Union[str, CommunicationIdentityTokenScope]]


    class azure.communication.identity.types.CommunicationIdentityCreateRequest(TypedDict, total=False):
        key "expiresInMinutes": int
        createTokenWithScopes: list[Union[str, CommunicationIdentityTokenScope]]
        expiresInMinutes: int


    class azure.communication.identity.types.TeamsExtensionAssignmentCreateOrUpdateRequest(TypedDict, total=False):
        key "principalType": Required[Union[str, TeamsExtensionPrincipalType]]
        clientIds: list[str]
        principalType: Union[str, TeamsExtensionPrincipalType]


    class azure.communication.identity.types.TeamsExtensionExchangeTokenRequest(TypedDict, total=False):


    class azure.communication.identity.types.TeamsUserExchangeTokenRequest(TypedDict, total=False):
        key "appId": Required[str]
        key "token": Required[str]
        key "userId": Required[str]
        appId: str
        token: str
        userId: str


```