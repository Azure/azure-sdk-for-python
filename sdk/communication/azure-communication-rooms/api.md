```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.communication.rooms

    class azure.communication.rooms.CommunicationCloudEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOD = "DOD"
        GCCH = "GCCH"
        PUBLIC = "PUBLIC"


    @runtime_checkable
    class azure.communication.rooms.CommunicationIdentifier(Protocol):
        property kind: CommunicationIdentifierKind    # Read-only
        property properties: Mapping[str, Any]    # Read-only
        property raw_id: str    # Read-only


    class azure.communication.rooms.CommunicationIdentifierKind(str, Enum, metaclass=DeprecatedEnumMeta):
        COMMUNICATION_USER = "communication_user"
        MICROSOFT_TEAMS_APP = "microsoft_teams_app"
        MICROSOFT_TEAMS_USER = "microsoft_teams_user"
        PHONE_NUMBER = "phone_number"
        TEAMS_EXTENSION_USER = "teams_extension_user"
        UNKNOWN = "unknown"


    class azure.communication.rooms.CommunicationRoom:
        created_at: datetime
        id: str
        pstn_dial_out_enabled: bool
        valid_from: datetime
        valid_until: datetime

        def __eq__(self, other): ...

        @overload
        def __init__(
                self, 
                *, 
                pstn_dial_out_enabled: Optional[bool] = ..., 
                valid_from: Optional[datetime] = ..., 
                valid_until: Optional[datetime] = ...
            ): ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]): ...


    class azure.communication.rooms.CommunicationUserIdentifier:
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


    class azure.communication.rooms.CommunicationUserProperties(TypedDict):
        key "id": str


    class azure.communication.rooms.MicrosoftTeamsAppIdentifier:
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


    class azure.communication.rooms.MicrosoftTeamsAppProperties(TypedDict):
        key "app_id": str
        key "cloud": Union[CommunicationCloudEnvironment, str]


    class azure.communication.rooms.MicrosoftTeamsUserIdentifier:
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


    class azure.communication.rooms.MicrosoftTeamsUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "is_anonymous": bool
        key "user_id": str


    class azure.communication.rooms.ParticipantRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTENDEE = "Attendee"
        COLLABORATOR = "Collaborator"
        CONSUMER = "Consumer"
        PRESENTER = "Presenter"


    class azure.communication.rooms.PhoneNumberIdentifier:
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


    class azure.communication.rooms.PhoneNumberProperties(TypedDict):
        key "asserted_id": NotRequired[str]
        key "is_anonymous": NotRequired[bool]
        key "value": str


    class azure.communication.rooms.RoomParticipant:
        communication_identifier: CommunicationIdentifier
        role: Union[str, ParticipantRole]

        def __eq__(self, other): ...

        @overload
        def __init__(
                self, 
                *, 
                communication_identifier: CommunicationIdentifier, 
                role: Union[str, ParticipantRole] = ParticipantRole.ATTENDEE
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.communication.rooms.RoomsClient: implements ContextManager 

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
                **kwargs
            ) -> RoomsClient: ...

        @distributed_trace
        def add_or_update_participants(
                self, 
                *, 
                participants: List[RoomParticipant], 
                room_id: str, 
                **kwargs
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def create_room(
                self, 
                *, 
                participants: Optional[List[RoomParticipant]] = ..., 
                pstn_dial_out_enabled: bool = False, 
                valid_from: Optional[datetime] = ..., 
                valid_until: Optional[datetime] = ..., 
                **kwargs
            ) -> CommunicationRoom: ...

        @distributed_trace
        def delete_room(
                self, 
                room_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_room(
                self, 
                room_id: str, 
                **kwargs
            ) -> CommunicationRoom: ...

        @distributed_trace
        def list_participants(
                self, 
                room_id: str, 
                **kwargs
            ) -> ItemPaged[RoomParticipant]: ...

        @distributed_trace
        def list_rooms(self, **kwargs) -> ItemPaged[CommunicationRoom]: ...

        @distributed_trace
        def remove_participants(
                self, 
                *, 
                participants: List[Union[RoomParticipant, CommunicationIdentifier]], 
                room_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def update_room(
                self, 
                *, 
                pstn_dial_out_enabled: Optional[bool] = ..., 
                room_id: str, 
                valid_from: Optional[datetime] = ..., 
                valid_until: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> CommunicationRoom: ...


    class azure.communication.rooms.TeamsExtensionUserIdentifier:
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


    class azure.communication.rooms.TeamsExtensionUserProperties(TypedDict):
        key "cloud": Union[CommunicationCloudEnvironment, str]
        key "resource_id": str
        key "tenant_id": str
        key "user_id": str


    class azure.communication.rooms.UnknownIdentifier:
        kind: Literal[CommunicationIdentifierKind.UNKNOWN] = CommunicationIdentifierKind.UNKNOWN
        properties: Mapping[str, Any]
        raw_id: str

        def __eq__(self, other): ...

        def __init__(self, identifier: str) -> None: ...


namespace azure.communication.rooms.aio

    class azure.communication.rooms.aio.RoomsClient: implements AsyncContextManager 

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
            ) -> RoomsClient: ...

        @distributed_trace_async
        async def add_or_update_participants(
                self, 
                *, 
                participants: List[RoomParticipant], 
                room_id: str, 
                **kwargs
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def create_room(
                self, 
                *, 
                participants: Optional[List[RoomParticipant]] = ..., 
                pstn_dial_out_enabled: bool = False, 
                valid_from: Optional[datetime] = ..., 
                valid_until: Optional[datetime] = ..., 
                **kwargs
            ) -> CommunicationRoom: ...

        @distributed_trace_async
        async def delete_room(
                self, 
                room_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_room(
                self, 
                room_id: str, 
                **kwargs
            ) -> CommunicationRoom: ...

        @distributed_trace
        def list_participants(
                self, 
                room_id: str, 
                **kwargs
            ) -> AsyncItemPaged[RoomParticipant]: ...

        @distributed_trace
        def list_rooms(self, **kwargs) -> AsyncItemPaged[CommunicationRoom]: ...

        @distributed_trace_async
        async def remove_participants(
                self, 
                *, 
                participants: List[Union[RoomParticipant, CommunicationIdentifier]], 
                room_id: str, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def update_room(
                self, 
                *, 
                pstn_dial_out_enabled: Optional[bool] = ..., 
                room_id: str, 
                valid_from: Optional[datetime] = ..., 
                valid_until: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> CommunicationRoom: ...


```