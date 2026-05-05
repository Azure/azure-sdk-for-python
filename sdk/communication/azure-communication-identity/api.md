```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.identity

    def azure.communication.identity.identifier_from_raw_id(raw_id: str) -> CommunicationIdentifier: ...


    class azure.communication.identity.CommunicationCloudEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOD = "DOD"
        GCCH = "GCCH"
        PUBLIC = "PUBLIC"


    @runtime_checkable
    class azure.communication.identity.CommunicationIdentifier(Protocol):
        property kind: CommunicationIdentifierKind    # Read-only
        property properties: Mapping[str, Any]    # Read-only
        property raw_id: str    # Read-only


    class azure.communication.identity.CommunicationIdentifierKind(str, Enum, metaclass=DeprecatedEnumMeta):
        COMMUNICATION_USER = "communication_user"
        MICROSOFT_TEAMS_APP = "microsoft_teams_app"
        MICROSOFT_TEAMS_USER = "microsoft_teams_user"
        PHONE_NUMBER = "phone_number"
        TEAMS_EXTENSION_USER = "teams_extension_user"
        UNKNOWN = "unknown"


    class azure.communication.identity.CommunicationIdentityClient:

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[TokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs: Any
            ) -> CommunicationIdentityClient: ...

        @distributed_trace
        def create_user(self, **kwargs) -> CommunicationUserIdentifier: ...

        @distributed_trace
        def create_user_and_token(
                self, 
                scopes: List[Union[str, CommunicationTokenScope]], 
                *, 
                token_expires_in: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> Tuple[CommunicationUserIdentifier, AccessToken]: ...

        @distributed_trace
        def delete_user(
                self, 
                user: CommunicationUserIdentifier, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_token(
                self, 
                user: CommunicationUserIdentifier, 
                scopes: List[Union[str, CommunicationTokenScope]], 
                *, 
                token_expires_in: Optional[timedelta] = ..., 
                **kwargs: Any
            ) -> AccessToken: ...

        @distributed_trace
        def get_token_for_teams_user(
                self, 
                aad_token: str, 
                client_id: str, 
                user_object_id: str, 
                **kwargs: Any
            ) -> AccessToken: ...

        @distributed_trace
        def revoke_tokens(
                self, 
                user: CommunicationUserIdentifier, 
                **kwargs: Any
            ) -> None: ...


    class azure.communication.identity.CommunicationTokenScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT = "chat"
        CHAT_JOIN = "chat.join"
        CHAT_JOIN_LIMITED = "chat.join.limited"
        VOIP = "voip"
        VOIP_JOIN = "voip.join"


    class azure.communication.identity.CommunicationUserIdentifier:
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


    class azure.communication.identity.CommunicationUserProperties(TypedDict):
        key "id": str


    class azure.communication.identity.MicrosoftTeamsAppIdentifier:
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


    class azure.communication.identity.MicrosoftTeamsAppProperties(TypedDict):
        key "app_id": str
        key "cloud": Union[CommunicationCloudEnvironment, str]


    class azure.communication.identity.MicrosoftTeamsUserIdentifier:
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


    class azure.communication.identity.MicrosoftTeamsUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "is_anonymous": bool
        key "user_id": str


    class azure.communication.identity.PhoneNumberIdentifier:
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


    class azure.communication.identity.PhoneNumberProperties(TypedDict):
        key "asserted_id": NotRequired[str]
        key "is_anonymous": NotRequired[bool]
        key "value": str


    class azure.communication.identity.TeamsExtensionUserIdentifier:
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


    class azure.communication.identity.TeamsExtensionUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "resource_id": str
        key "tenant_id": str
        key "user_id": str


    class azure.communication.identity.UnknownIdentifier:
        kind: Literal[CommunicationIdentifierKind.UNKNOWN] = CommunicationIdentifierKind.UNKNOWN
        properties: Mapping[str, Any]
        raw_id: str

        def __eq__(self, other): ...

        def __init__(self, identifier: str) -> None: ...


namespace azure.communication.identity.aio

    class azure.communication.identity.aio.CommunicationIdentityClient: implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: Union[AsyncTokenCredential, AzureKeyCredential], 
                *, 
                api_version: str = ..., 
                **kwargs
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                **kwargs
            ) -> CommunicationIdentityClient: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_user(self, **kwargs) -> CommunicationUserIdentifier: ...

        @distributed_trace_async
        async def create_user_and_token(
                self, 
                scopes: List[Union[str, CommunicationTokenScope]], 
                *, 
                token_expires_in: Optional[timedelta] = ..., 
                **kwargs
            ) -> Tuple[CommunicationUserIdentifier, AccessToken]: ...

        @distributed_trace_async
        async def delete_user(
                self, 
                user: CommunicationUserIdentifier, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_token(
                self, 
                user: CommunicationUserIdentifier, 
                scopes: List[Union[str, CommunicationTokenScope]], 
                *, 
                token_expires_in: Optional[timedelta] = ..., 
                **kwargs
            ) -> AccessToken: ...

        @distributed_trace_async
        async def get_token_for_teams_user(
                self, 
                aad_token: str, 
                client_id: str, 
                user_object_id: str, 
                **kwargs
            ) -> AccessToken: ...

        @distributed_trace_async
        async def revoke_tokens(
                self, 
                user: CommunicationUserIdentifier, 
                **kwargs
            ) -> None: ...


```