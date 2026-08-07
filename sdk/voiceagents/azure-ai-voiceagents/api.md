```py
namespace azure.ai.voiceagents

    class azure.ai.voiceagents.VoiceAgentsClient: implements ContextManager 
        agent_endpoint_conversations: AgentEndpointConversationsOperations
        voice_agents: VoiceAgentsOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
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


namespace azure.ai.voiceagents.aio

    class azure.ai.voiceagents.aio.AsyncRealtime:

        def __init__(self, client: VoiceAgentsClient) -> None: ...

        def connect(
                self, 
                *, 
                agent_name: str, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                api_version: Optional[str] = ..., 
                connection_url: Optional[str] = ..., 
                credential_scopes: Optional[List[str]] = ..., 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: Union[str, AgentDefinitionOptInKeys] = _models.AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncRealtimeConnectionManager: ...


    class azure.ai.voiceagents.aio.AsyncRealtimeConnection: implements AsyncContextManager 

        def __aiter__(self) -> AsyncIterator[ServerEvent]: ...

        def __init__(
                self, 
                connection: ClientWebSocketResponse, 
                session: ClientSession
            ) -> None: ...

        async def close(
                self, 
                *, 
                code: int = 1000, 
                reason: str = ""
            ) -> None: ...

        async def recv(self) -> ServerEvent: ...

        async def send(self, event: ClientEvent) -> None: ...


    class azure.ai.voiceagents.aio.AsyncRealtimeConnectionManager: implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                api_version: str, 
                connection_url: Optional[str] = ..., 
                credential: AsyncTokenCredential, 
                credential_scopes: List[str], 
                endpoint: str, 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: Union[str, AgentDefinitionOptInKeys], 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def enter(self) -> AsyncRealtimeConnection: ...


    class azure.ai.voiceagents.aio.VoiceAgentsClient(_GeneratedVoiceAgentsClient): implements AsyncContextManager 
        property realtime: AsyncRealtime    # Read-only

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: Optional[str] = ..., 
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


namespace azure.ai.voiceagents.aio.operations

    class azure.ai.voiceagents.aio.operations.AgentEndpointConversationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace_async
        async def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceResponse]: ...


    class azure.ai.voiceagents.aio.operations.VoiceAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_voice_agent(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                state: Optional[Union[str, AgentState]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def create_voice_agent(
                self, 
                body: CreateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def create_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def create_voice_agent_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        async def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: CreateVoiceAgentVersionRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        async def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace_async
        async def delete_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def generate_voice_agent(
                self, 
                *, 
                agent_type: Union[str, VoiceAgentType], 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                goal: str, 
                model: str, 
                model_type: Union[str, VoiceModelType], 
                name: str, 
                tools: Optional[list[VoiceAgentTool]] = ..., 
                use_case: Union[str, VoiceAgentUseCase], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def generate_voice_agent(
                self, 
                body: GenerateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def generate_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace_async
        async def get_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace_async
        async def get_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def list_voice_agent_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceAgentVersionObject]: ...

        @distributed_trace
        def list_voice_agents(
                self, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceAgentObject]: ...

        @overload
        async def update_voice_agent(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def update_voice_agent(
                self, 
                agent_name: str, 
                body: UpdateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def update_voice_agent(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...


namespace azure.ai.voiceagents.models

    class azure.ai.voiceagents.models.A2AProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.ActivityProtocolConfiguration(_Model):
        enable_m365_public_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_m365_public_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentBlueprintReference(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentBlueprintReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_AGENT_IDENTITY_BLUEPRINT = "ManagedAgentIdentityBlueprint"


    class azure.ai.voiceagents.models.AgentCard(_Model):
        description: Optional[str]
        skills: list[AgentCardSkill]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                skills: list[AgentCardSkill], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentCardSkill(_Model):
        description: Optional[str]
        examples: Optional[list[str]]
        id: str
        name: str
        tags: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                examples: Optional[list[str]] = ..., 
                id: str, 
                name: str, 
                tags: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentDefinitionOptInKeys(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAFT_AGENTS_V1_PREVIEW = "DraftAgents=V1Preview"
        EXTERNAL_AGENTS_V1_PREVIEW = "ExternalAgents=V1Preview"
        VOICE_AGENTS_V1_PREVIEW = "VoiceAgents=V1Preview"
        WORKFLOW_AGENTS_V1_PREVIEW = "WorkflowAgents=V1Preview"


    class azure.ai.voiceagents.models.AgentEndpointAuthorizationScheme(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentEndpointAuthorizationSchemeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT_SERVICE = "BotService"
        BOT_SERVICE_RBAC = "BotServiceRbac"
        BOT_SERVICE_TENANT = "BotServiceTenant"
        ENTRA = "Entra"


    class azure.ai.voiceagents.models.AgentEndpointConfig(_Model):
        authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]]
        protocol_configuration: Optional[ProtocolConfiguration]
        version_selector: Optional[VersionSelector]

        @overload
        def __init__(
                self, 
                *, 
                authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]] = ..., 
                protocol_configuration: Optional[ProtocolConfiguration] = ..., 
                version_selector: Optional[VersionSelector] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentIdentity(_Model):
        client_id: str
        principal_id: str
        status: Optional[Union[str, AgentIdentityStatus]]

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                principal_id: str, 
                status: Optional[Union[str, AgentIdentityStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AgentIdentityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DISABLED = "disabled"


    class azure.ai.voiceagents.models.AgentObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        AGENT_CONTAINER = "agent.container"
        AGENT_DELETED = "agent.deleted"
        AGENT_VERSION = "agent.version"
        AGENT_VERSION_DELETED = "agent.version.deleted"


    class azure.ai.voiceagents.models.AgentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.ai.voiceagents.models.AgentStateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_BLUEPRINT = "agent_blueprint"
        AGENT_INSTANCE_IDENTITY = "agent_instance_identity"


    class azure.ai.voiceagents.models.AgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETED = "deleted"
        DELETING = "deleting"
        FAILED = "failed"


    class azure.ai.voiceagents.models.ApiErrorResponse(_Model):
        error: Error

        @overload
        def __init__(
                self, 
                *, 
                error: Error
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AzureAvatarVoiceSyncVoice(AzureVoice, discriminator='avatar-voice-sync'):
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        model: Union[str, PersonalVoiceModel]
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AVATAR_VOICE_SYNC]
        volume: str

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                model: Union[str, PersonalVoiceModel], 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AzureCustomVoice(AzureVoice, discriminator='azure-custom'):
        custom_lexicon_url: str
        custom_text_normalization_url: str
        endpoint_id: str
        locale: str
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_CUSTOM]
        volume: str

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


    class azure.ai.voiceagents.models.AzurePersonalVoice(AzureVoice, discriminator='azure-personal'):
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        model: Union[str, PersonalVoiceModel]
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_PERSONAL]
        volume: str

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                model: Union[str, PersonalVoiceModel], 
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


    class azure.ai.voiceagents.models.AzureRealtimeNativeVoice(_Model):
        name: Union[str, AzureRealtimeNativeVoiceName]
        type: Literal["azure-realtime-native"]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, AzureRealtimeNativeVoiceName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AzureRealtimeNativeVoiceName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AARTI = "aarti"
        ALVARO = "alvaro"
        ANDREW = "andrew"
        ANTONIO = "antonio"
        AVA = "ava"
        CLARA = "clara"
        DALIA = "dalia"
        DENISE = "denise"
        DIEGO = "diego"
        DIYA = "diya"
        ELSA = "elsa"
        EMMA = "emma"
        FLORIAN = "florian"
        FRANCISCA = "francisca"
        HYUNSU = "hyunsu"
        JORGE = "jorge"
        KEITA = "keita"
        LIAM = "liam"
        MEERA = "meera"
        NANAMI = "nanami"
        NATASHA = "natasha"
        NIWAT = "niwat"
        PREMWADEE = "premwadee"
        REMY = "remy"
        RYAN = "ryan"
        SERAPHINA = "seraphina"
        SONIA = "sonia"
        SUNHI = "sunhi"
        SYLVIE = "sylvie"
        THIERRY = "thierry"
        WILLIAM = "william"
        XIAOXIAO = "xiaoxiao"
        XIMENA = "ximena"
        YUNXI = "yunxi"


    class azure.ai.voiceagents.models.AzureStandardVoice(AzureVoice, discriminator='azure-standard'):
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        multi_talker_speaker_name: Optional[str]
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_STANDARD]
        volume: str

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                multi_talker_speaker_name: Optional[str] = ..., 
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


    class azure.ai.voiceagents.models.AzureVoice(_Model):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        locale: Optional[str]
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        rate: Optional[str]
        style: Optional[str]
        temperature: Optional[float]
        type: str
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                locale: Optional[str] = ..., 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                type: str, 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AzureVoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVATAR_VOICE_SYNC = "avatar-voice-sync"
        AZURE_CUSTOM = "azure-custom"
        AZURE_PERSONAL = "azure-personal"
        AZURE_STANDARD = "azure-standard"


    class azure.ai.voiceagents.models.BotServiceAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotService'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.BotServiceRbacAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceRbac'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.BotServiceTenantAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceTenant'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.CallableToolAllowedCaller(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "direct"
        PROGRAMMATIC = "programmatic"


    class azure.ai.voiceagents.models.CreateTranscriptionResponseJsonUsage(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.CreateTranscriptionResponseJsonUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DURATION = "duration"
        TOKENS = "tokens"


    class azure.ai.voiceagents.models.EntraAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='Entra'):
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.Error(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[Error]]
        message: str
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[dict[str, Any]] = ..., 
                code: str, 
                debug_info: Optional[dict[str, Any]] = ..., 
                details: Optional[list[Error]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.FixedRatioVersionSelectionRule(VersionSelectionRule, discriminator='FixedRatio'):
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str, 
                traffic_percentage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.InvocationsProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.InvocationsWsProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.LlmGeneratedVoiceGreetingConfig(VoiceGreetingConfig, discriminator='llm_generated'):
        fallback_text: Optional[str]
        prompt: str
        tool_choice: Optional[Union[str, VoiceGreetingToolChoice]]
        type: Literal["llm_generated"]

        @overload
        def __init__(
                self, 
                *, 
                fallback_text: Optional[str] = ..., 
                prompt: str, 
                tool_choice: Optional[Union[str, VoiceGreetingToolChoice]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.LogProbProperties(_Model):
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


    class azure.ai.voiceagents.models.MCPListToolsTool(_Model):
        annotations: Optional[MCPListToolsToolAnnotations]
        description: Optional[str]
        input_schema: MCPListToolsToolInputSchema
        name: str

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[MCPListToolsToolAnnotations] = ..., 
                description: Optional[str] = ..., 
                input_schema: MCPListToolsToolInputSchema, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.MCPListToolsToolAnnotations(_Model):


    class azure.ai.voiceagents.models.MCPListToolsToolInputSchema(_Model):


    class azure.ai.voiceagents.models.MCPTool(Tool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        connector_id: Optional[Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]]
        defer_loading: Optional[bool]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        tunnel_id: Optional[str]
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                connector_id: Optional[Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams, connector_outlookcalendar, connector_outlookemail, connector_sharepoint]] = ..., 
                defer_loading: Optional[bool] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                tunnel_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.MCPToolFilter(_Model):
        read_only: Optional[bool]
        tool_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                read_only: Optional[bool] = ..., 
                tool_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.MCPToolRequireApproval(_Model):
        always: Optional[MCPToolFilter]
        never: Optional[MCPToolFilter]

        @overload
        def __init__(
                self, 
                *, 
                always: Optional[MCPToolFilter] = ..., 
                never: Optional[MCPToolFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ManagedAgentIdentityBlueprintReference(AgentBlueprintReference, discriminator='ManagedAgentIdentityBlueprint'):
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]

        @overload
        def __init__(
                self, 
                *, 
                blueprint_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.McpProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.Metadata(_Model):


    class azure.ai.voiceagents.models.OpenAIVoice(_Model):
        name: Union[str, VoiceIdsShared]
        type: Literal["openai"]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, VoiceIdsShared]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.PageOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.ai.voiceagents.models.PersonalVoiceModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAGON_HD_OMNI_LATEST_NEURAL = "DragonHDOmniLatestNeural"
        DRAGON_LATEST_NEURAL = "DragonLatestNeural"
        MAI_VOICE = "MAI-Voice"


    class azure.ai.voiceagents.models.ProtocolConfiguration(_Model):
        a2_a: Optional[A2AProtocolConfiguration]
        activity: Optional[ActivityProtocolConfiguration]
        invocations: Optional[InvocationsProtocolConfiguration]
        invocations_ws: Optional[InvocationsWsProtocolConfiguration]
        mcp: Optional[McpProtocolConfiguration]
        responses: Optional[ResponsesProtocolConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                a2_a: Optional[A2AProtocolConfiguration] = ..., 
                activity: Optional[ActivityProtocolConfiguration] = ..., 
                invocations: Optional[InvocationsProtocolConfiguration] = ..., 
                invocations_ws: Optional[InvocationsWsProtocolConfiguration] = ..., 
                mcp: Optional[McpProtocolConfiguration] = ..., 
                responses: Optional[ResponsesProtocolConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RaiConfig(_Model):
        rai_policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                rai_policy_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeAudioFormats(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeAudioFormatsAudioPcm(RealtimeAudioFormats, discriminator='audio/pcm'):
        rate: Optional[Literal[24000]]
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCM]

        @overload
        def __init__(
                self, 
                *, 
                rate: Optional[Literal[24000]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeAudioFormatsAudioPcma(RealtimeAudioFormats, discriminator='audio/pcma'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeAudioFormatsAudioPcmu(RealtimeAudioFormats, discriminator='audio/pcmu'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMU]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeAudioFormatsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO_PCM = "audio/pcm"
        AUDIO_PCMA = "audio/pcma"
        AUDIO_PCMU = "audio/pcmu"


    class azure.ai.voiceagents.models.RealtimeClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATE = "conversation.item.create"
        CONVERSATION_ITEM_DELETE = "conversation.item.delete"
        CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
        CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
        INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
        INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
        INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
        OUTPUT_AUDIO_BUFFER_CLEAR = "output_audio_buffer.clear"
        RESPONSE_CANCEL = "response.cancel"
        RESPONSE_CREATE = "response.create"
        SESSION_UPDATE = "session.update"


    class azure.ai.voiceagents.models.RealtimeConversationItem(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemFunctionCall(RealtimeConversationItem, discriminator='function_call'):
        arguments: str
        call_id: Optional[str]
        id: Optional[str]
        name: str
        object: Optional[Literal["item"]]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemFunctionCallOutput(RealtimeConversationItem, discriminator='function_call_output'):
        call_id: str
        id: Optional[str]
        object: Optional[Literal["item"]]
        output: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str, 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessage(_Model):
        role: str

        @overload
        def __init__(
                self, 
                *, 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageAssistant(RealtimeConversationItemMessage, discriminator='assistant'):
        content: list[RealtimeConversationItemMessageAssistantContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageAssistantContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageAssistantContent(_Model):
        audio: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["output_text", "output_audio"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[output_text, output_audio]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageSystem(RealtimeConversationItemMessage, discriminator='system'):
        content: list[RealtimeConversationItemMessageSystemContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageSystemContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageSystemContent(_Model):
        text: Optional[str]
        type: Optional[Literal["input_text"]]

        @overload
        def __init__(
                self, 
                *, 
                text: Optional[str] = ..., 
                type: Optional[Literal[input_text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageUser(RealtimeConversationItemMessage, discriminator='user'):
        content: list[RealtimeConversationItemMessageUserContent]
        id: Optional[str]
        object: Optional[Literal["item"]]
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal["message"]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageUserContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemMessageUserContent(_Model):
        audio: Optional[str]
        detail: Optional[Literal["auto", "low", "high"]]
        image_url: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["input_text", "input_audio", "input_image"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                detail: Optional[Literal[auto, low, high]] = ..., 
                image_url: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[input_text, input_audio, input_image]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"


    class azure.ai.voiceagents.models.RealtimeFunctionTool(_Model):
        description: Optional[str]
        name: Optional[str]
        parameters: Optional[RealtimeFunctionToolParameters]
        type: Optional[Literal["function"]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[RealtimeFunctionToolParameters] = ..., 
                type: Optional[Literal[function]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeFunctionToolParameters(_Model):


    class azure.ai.voiceagents.models.RealtimeMCPApprovalRequest(RealtimeConversationItem, discriminator='mcp_approval_request'):
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                id: str, 
                name: str, 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPApprovalResponse(RealtimeConversationItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        id: str
        reason: Optional[str]
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                id: str, 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPError(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPHTTPError(RealtimeMCPError, discriminator='http_error'):
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.HTTP_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                code: int, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPListTools(RealtimeConversationItem, discriminator='mcp_list_tools'):
        id: Optional[str]
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPProtocolError(RealtimeMCPError, discriminator='protocol_error'):
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                code: int, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPToolCall(RealtimeConversationItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        error: Optional[RealtimeMCPError]
        id: str
        name: str
        output: Optional[str]
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                error: Optional[RealtimeMCPError] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMCPToolExecutionError(RealtimeMCPError, discriminator='tool_execution_error'):
        message: str
        type: Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeMcpErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP_ERROR = "http_error"
        PROTOCOL_ERROR = "protocol_error"
        TOOL_EXECUTION_ERROR = "tool_execution_error"


    class azure.ai.voiceagents.models.RealtimeReasoning(_Model):
        effort: Optional[Union[str, RealtimeReasoningEffort]]

        @overload
        def __init__(
                self, 
                *, 
                effort: Optional[Union[str, RealtimeReasoningEffort]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        XHIGH = "xhigh"


    class azure.ai.voiceagents.models.RealtimeResponseStatusDetails(_Model):
        error: Optional[RealtimeResponseStatusDetailsError]
        reason: Optional[Literal["turn_detected", "client_cancelled", "max_output_tokens", "content_filter"]]
        type: Optional[Literal["completed", "cancelled", "failed", "incomplete"]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[RealtimeResponseStatusDetailsError] = ..., 
                reason: Optional[Literal[turn_detected, client_cancelled, max_output_tokens, content_filter]] = ..., 
                type: Optional[Literal[completed, cancelled, failed, incomplete]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeResponseStatusDetailsError(_Model):
        code: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeResponseUsage(_Model):
        input_token_details: Optional[RealtimeResponseUsageInputTokenDetails]
        input_tokens: Optional[int]
        output_token_details: Optional[RealtimeResponseUsageOutputTokenDetails]
        output_tokens: Optional[int]
        total_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                input_token_details: Optional[RealtimeResponseUsageInputTokenDetails] = ..., 
                input_tokens: Optional[int] = ..., 
                output_token_details: Optional[RealtimeResponseUsageOutputTokenDetails] = ..., 
                output_tokens: Optional[int] = ..., 
                total_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeResponseUsageInputTokenDetails(_Model):
        audio_tokens: Optional[int]
        cached_tokens: Optional[int]
        cached_tokens_details: Optional[RealtimeResponseUsageInputTokenDetailsCachedTokensDetails]
        image_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                cached_tokens: Optional[int] = ..., 
                cached_tokens_details: Optional[RealtimeResponseUsageInputTokenDetailsCachedTokensDetails] = ..., 
                image_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeResponseUsageInputTokenDetailsCachedTokensDetails(_Model):
        audio_tokens: Optional[int]
        image_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                image_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeResponseUsageOutputTokenDetails(_Model):
        audio_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEvent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEventConversationItemInputAudioTranscriptionFailedError(_Model):
        code: Optional[str]
        message: Optional[str]
        param: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEventRateLimitsUpdatedRateLimits(_Model):
        limit: Optional[int]
        name: Optional[Literal["requests", "tokens"]]
        remaining: Optional[int]
        reset_seconds: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                name: Optional[Literal[requests, tokens]] = ..., 
                remaining: Optional[int] = ..., 
                reset_seconds: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEventResponseContentPartAdded(RealtimeServerEvent, discriminator='response.content_part.added'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                part: RealtimeServerEventResponseContentPartAddedPart, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEventResponseContentPartAddedPart(_Model):
        audio: Optional[str]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["audio", "text"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[audio, text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.RealtimeServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_CREATED = "conversation.created"
        CONVERSATION_ITEM_ADDED = "conversation.item.added"
        CONVERSATION_ITEM_CREATED = "conversation.item.created"
        CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
        CONVERSATION_ITEM_DONE = "conversation.item.done"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT = "conversation.item.input_audio_transcription.segment"
        CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
        CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
        ERROR = "error"
        INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
        INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
        INPUT_AUDIO_BUFFER_DTMF_EVENT_RECEIVED = "input_audio_buffer.dtmf_event_received"
        INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
        INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
        INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED = "input_audio_buffer.timeout_triggered"
        MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
        MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
        MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
        OUTPUT_AUDIO_BUFFER_CLEARED = "output_audio_buffer.cleared"
        OUTPUT_AUDIO_BUFFER_STARTED = "output_audio_buffer.started"
        OUTPUT_AUDIO_BUFFER_STOPPED = "output_audio_buffer.stopped"
        RATE_LIMITS_UPDATED = "rate_limits.updated"
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
        RESPONSE_OUTPUT_AUDIO_DELTA = "response.output_audio.delta"
        RESPONSE_OUTPUT_AUDIO_DONE = "response.output_audio.done"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA = "response.output_audio_transcript.delta"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE = "response.output_audio_transcript.done"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        SESSION_CREATED = "session.created"
        SESSION_UPDATED = "session.updated"


    class azure.ai.voiceagents.models.RealtimeToolChoiceFunction(_Model):
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Literal[ToolChoiceParamType.FUNCTION]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ResponsesProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.StructuredInputDefinition(_Model):
        default_value: Optional[Any]
        description: Optional[str]
        required: Optional[bool]
        schema: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                default_value: Optional[Any] = ..., 
                description: Optional[str] = ..., 
                required: Optional[bool] = ..., 
                schema: Optional[dict[str, Any]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.TemplateVoiceGreetingConfig(VoiceGreetingConfig, discriminator='template'):
        text: str
        type: Literal["template"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.Tool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ToolChoiceFunction(ToolChoiceParam, discriminator='function'):
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ToolChoiceMCP(ToolChoiceParam, discriminator='mcp'):
        name: Optional[str]
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ToolChoiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.voiceagents.models.ToolChoiceParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_TOOLS = "allowed_tools"
        APPLY_PATCH = "apply_patch"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE = "computer_use"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        MCP = "mcp"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHELL = "shell"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WEB_SEARCH_PREVIEW2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.voiceagents.models.ToolConfig(_Model):
        additional_search_text: Optional[str]
        pin: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                additional_search_text: Optional[str] = ..., 
                pin: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A_PREVIEW = "a2a_preview"
        APPLY_PATCH = "apply_patch"
        AZURE_AI_SEARCH = "azure_ai_search"
        AZURE_FUNCTION = "azure_function"
        BING_CUSTOM_SEARCH_PREVIEW = "bing_custom_search_preview"
        BING_GROUNDING = "bing_grounding"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CAPTURE_STRUCTURED_OUTPUTS = "capture_structured_outputs"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FABRIC_DATAAGENT_PREVIEW = "fabric_dataagent_preview"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        LOCAL_SHELL = "local_shell"
        MCP = "mcp"
        MEMORY_SEARCH_PREVIEW = "memory_search_preview"
        NAMESPACE = "namespace"
        OPENAPI = "openapi"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.voiceagents.models.TranscriptTextUsageDuration(CreateTranscriptionResponseJsonUsage, discriminator='duration'):
        seconds: timedelta
        type: Literal[CreateTranscriptionResponseJsonUsageType.DURATION]

        @overload
        def __init__(
                self, 
                *, 
                seconds: timedelta
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.TranscriptTextUsageTokens(CreateTranscriptionResponseJsonUsage, discriminator='tokens'):
        input_token_details: Optional[TranscriptTextUsageTokensInputTokenDetails]
        input_tokens: int
        output_tokens: int
        total_tokens: int
        type: Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]

        @overload
        def __init__(
                self, 
                *, 
                input_token_details: Optional[TranscriptTextUsageTokensInputTokenDetails] = ..., 
                input_tokens: int, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.TranscriptTextUsageTokensInputTokenDetails(_Model):
        audio_tokens: Optional[int]
        text_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                audio_tokens: Optional[int] = ..., 
                text_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VersionSelectionRule(_Model):
        agent_version: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VersionSelector(_Model):
        version_selection_rules: list[VersionSelectionRule]

        @overload
        def __init__(
                self, 
                *, 
                version_selection_rules: list[VersionSelectionRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VersionSelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.ai.voiceagents.models.VoiceAgentAnimationConfig(_Model):
        model_name: Optional[str]
        outputs: Optional[list[Union[str, VoiceAgentAnimationOutputType]]]

        @overload
        def __init__(
                self, 
                *, 
                model_name: Optional[str] = ..., 
                outputs: Optional[list[Union[str, VoiceAgentAnimationOutputType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentAnimationOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLENDSHAPES = "blendshapes"
        VISEME_ID = "viseme_id"


    class azure.ai.voiceagents.models.VoiceAgentAvatarIceServer(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentAvatarOutputProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"
        WEBSOCKET_BINARY = "websocket-binary"


    class azure.ai.voiceagents.models.VoiceAgentAvatarScene(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentAvatarType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHOTO_AVATAR = "photo_avatar"
        VIDEO_AVATAR = "video_avatar"


    class azure.ai.voiceagents.models.VoiceAgentAvatarVideoBackground(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentAvatarVideoCrop(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentAvatarVideoParams(_Model):
        background: Optional[VoiceAgentAvatarVideoBackground]
        bitrate: Optional[int]
        codec: Optional[Literal["h264"]]
        crop: Optional[VoiceAgentAvatarVideoCrop]
        gop_size: Optional[int]
        resolution: Optional[VoiceAgentAvatarVideoResolution]

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[VoiceAgentAvatarVideoBackground] = ..., 
                bitrate: Optional[int] = ..., 
                codec: Optional[Literal[h264]] = ..., 
                crop: Optional[VoiceAgentAvatarVideoCrop] = ..., 
                gop_size: Optional[int] = ..., 
                resolution: Optional[VoiceAgentAvatarVideoResolution] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentAvatarVideoResolution(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentAzureMultilingualSemanticVadTurnDetection(_Model):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[int] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ..., 
                type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentAzureSemanticVadTurnDetection(_Model):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Union[str, VoiceAgentAzureSemanticVadType]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[int] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ..., 
                type: Union[str, VoiceAgentAzureSemanticVadType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentAzureSemanticVadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "azure_semantic_vad"
        ENGLISH = "azure_semantic_vad_en"


    class azure.ai.voiceagents.models.VoiceAgentClientEventConversationItemCreate(_Model):
        event_id: Optional[str]
        item: VoiceAgentCreateConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: VoiceAgentCreateConversationItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventConversationItemDelete(_Model):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventConversationItemRetrieve(_Model):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventConversationItemTruncate(_Model):
        audio_end_ms: int
        content_index: int
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventInputAudioBufferAppend(_Model):
        audio: str
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventInputAudioBufferClear(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventInputAudioBufferCommit(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventOutputAudioBufferClear(_Model):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventResponseCancel(_Model):
        event_id: Optional[str]
        response_id: Optional[str]
        type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventResponseCreate(_Model):
        event_id: Optional[str]
        response: Optional[VoiceAgentResponseCreateParams]
        type: Literal[RealtimeClientEventType.RESPONSE_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response: Optional[VoiceAgentResponseCreateParams] = ..., 
                type: Literal[RealtimeClientEventType.RESPONSE_CREATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventSessionAvatarConnect(_Model):
        client_sdp: str
        event_id: Optional[str]
        type: Literal["connect"]

        @overload
        def __init__(
                self, 
                *, 
                client_sdp: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentClientEventSessionUpdate(_Model):
        event_id: Optional[str]
        session: VoiceAgentSessionUpdateConfig
        type: Literal[RealtimeClientEventType.SESSION_UPDATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                session: VoiceAgentSessionUpdateConfig, 
                type: Literal[RealtimeClientEventType.SESSION_UPDATE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentDefinition(_Model):
        audio: Optional[VoiceAudioConfig]
        avatar: Optional[VoiceAvatarConfig]
        greeting: Optional[VoiceGreetingConfig]
        instructions: Optional[str]
        kind: Literal["voice"]
        model: str
        model_type: Union[str, VoiceModelType]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        rai_config: Optional[RaiConfig]
        store: Optional[bool]
        structured_inputs: Optional[dict[str, StructuredInputDefinition]]
        tools: Optional[list[VoiceAgentTool]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceAudioConfig] = ..., 
                avatar: Optional[VoiceAvatarConfig] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                instructions: Optional[str] = ..., 
                model: str, 
                model_type: Union[str, VoiceModelType], 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                store: Optional[bool] = ..., 
                structured_inputs: Optional[dict[str, StructuredInputDefinition]] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentEchoCancellation(_Model):
        channels: Optional[int]
        reference_source: Optional[Union[str, VoiceAgentEchoCancellationReferenceSource]]
        type: Literal["server_echo_cancellation"]

        @overload
        def __init__(
                self, 
                *, 
                channels: Optional[int] = ..., 
                reference_source: Optional[Union[str, VoiceAgentEchoCancellationReferenceSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentEchoCancellationReferenceSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = "client"
        SERVER = "server"


    class azure.ai.voiceagents.models.VoiceAgentEndOfUtteranceDetection(_Model):
        model: Union[str, VoiceAgentEndOfUtteranceModel]
        threshold: Optional[float]
        threshold_level: Optional[Union[str, VoiceAgentEndOfUtteranceThresholdLevel]]
        timeout: Optional[float]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                model: Union[str, VoiceAgentEndOfUtteranceModel], 
                threshold: Optional[float] = ..., 
                threshold_level: Optional[Union[str, VoiceAgentEndOfUtteranceThresholdLevel]] = ..., 
                timeout: Optional[float] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentEndOfUtteranceModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_DETECTION_V1 = "semantic_detection_v1"
        SEMANTIC_DETECTION_V1_EN = "semantic_detection_v1_en"
        SEMANTIC_DETECTION_V1_MULTILINGUAL = "semantic_detection_v1_multilingual"
        SMART_END_OF_TURN_DETECTION = "smart_end_of_turn_detection"


    class azure.ai.voiceagents.models.VoiceAgentEndOfUtteranceThresholdLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.voiceagents.models.VoiceAgentEstimatedCost(_Model):
        amount: float
        byom_model_amount: Optional[float]
        byom_model_price_version: Optional[str]
        currency: Optional[Literal["USD"]]
        input_cost: Optional[float]
        output_cost: Optional[float]
        price_version: str
        status: Union[str, VoiceAgentEstimatedCostStatus]
        unpriced_components: Optional[list[str]]
        voice_live_amount: float

        @overload
        def __init__(
                self, 
                *, 
                amount: float, 
                byom_model_amount: Optional[float] = ..., 
                byom_model_price_version: Optional[str] = ..., 
                currency: Optional[Literal[USD]] = ..., 
                input_cost: Optional[float] = ..., 
                output_cost: Optional[float] = ..., 
                price_version: str, 
                status: Union[str, VoiceAgentEstimatedCostStatus], 
                unpriced_components: Optional[list[str]] = ..., 
                voice_live_amount: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentEstimatedCostStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "complete"
        PARTIAL = "partial"
        UNAVAILABLE = "unavailable"


    class azure.ai.voiceagents.models.VoiceAgentFileSearchCallItem(_Model):
        id: str
        queries: Optional[list[str]]
        results: Optional[list[VoiceAgentFileSearchResult]]
        status: Union[str, VoiceAgentFileSearchCallStatus]
        type: Literal["file_search_call"]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                queries: Optional[list[str]] = ..., 
                results: Optional[list[VoiceAgentFileSearchResult]] = ..., 
                status: Union[str, VoiceAgentFileSearchCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentFileSearchCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"
        SEARCHING = "searching"


    class azure.ai.voiceagents.models.VoiceAgentFileSearchResult(_Model):
        attributes: Optional[dict[str, VoiceAgentFileSearchAttributeValue]]
        file_id: Optional[str]
        filename: Optional[str]
        score: Optional[float]
        text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, VoiceAgentFileSearchAttributeValue]] = ..., 
                file_id: Optional[str] = ..., 
                filename: Optional[str] = ..., 
                score: Optional[float] = ..., 
                text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffAbortReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "error"
        USER_INTERRUPTION = "user_interruption"


    class azure.ai.voiceagents.models.VoiceAgentHandoffEdgeConfig(_Model):
        cancel_on_interruption: Optional[bool]
        delay_ms: Optional[int]
        description: str
        id: str
        source: str
        target: str
        target_response: Optional[Union[str, VoiceAgentHandoffTargetResponse]]
        transfer_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cancel_on_interruption: Optional[bool] = ..., 
                delay_ms: Optional[int] = ..., 
                description: str, 
                id: str, 
                source: str, 
                target: str, 
                target_response: Optional[Union[str, VoiceAgentHandoffTargetResponse]] = ..., 
                transfer_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffEdgeState(_Model):
        cancel_on_interruption: Optional[bool]
        delay_ms: Optional[int]
        id: str
        source: str
        target: str
        target_response: Optional[Union[str, VoiceAgentHandoffTargetResponse]]
        transfer_message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cancel_on_interruption: Optional[bool] = ..., 
                delay_ms: Optional[int] = ..., 
                id: str, 
                source: str, 
                target: str, 
                target_response: Optional[Union[str, VoiceAgentHandoffTargetResponse]] = ..., 
                transfer_message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffGraphConfig(_Model):
        edges: list[VoiceAgentHandoffEdgeConfig]
        max_attempts: Optional[int]
        max_transfers: Optional[int]
        nodes: list[VoiceAgentHandoffNodeConfig]

        @overload
        def __init__(
                self, 
                *, 
                edges: list[VoiceAgentHandoffEdgeConfig], 
                max_attempts: Optional[int] = ..., 
                max_transfers: Optional[int] = ..., 
                nodes: list[VoiceAgentHandoffNodeConfig]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffNodeConfig(_Model):
        config: VoiceAgentHandoffNodeSessionConfig
        description: str
        id: str

        @overload
        def __init__(
                self, 
                *, 
                config: VoiceAgentHandoffNodeSessionConfig, 
                description: str, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffNodeSessionConfig(_Model):
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_response_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        model: Optional[str]
        parallel_tool_calls: Optional[bool]
        reasoning_effort: Optional[Union[str, VoiceAgentHandoffReasoningEffort]]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentSessionTool]]
        voice: Optional[VoiceAgentVoice]
        voice_adaptation: Optional[VoiceAgentVoiceAdaptation]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_response_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                model: Optional[str] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning_effort: Optional[Union[str, VoiceAgentHandoffReasoningEffort]] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentSessionTool]] = ..., 
                voice: Optional[VoiceAgentVoice] = ..., 
                voice_adaptation: Optional[VoiceAgentVoiceAdaptation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffNodeState(_Model):
        description: str
        id: str
        implicit: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                implicit: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        NONE = "none"
        XHIGH = "xhigh"


    class azure.ai.voiceagents.models.VoiceAgentHandoffState(_Model):
        active_node_id: str
        attempt_count: int
        available_edge_ids: list[str]
        edges: list[VoiceAgentHandoffEdgeState]
        node_generation: int
        nodes: list[VoiceAgentHandoffNodeState]
        pipeline_family: Union[str, VoiceAgentPipelineFamily]
        transfer_count: int
        transfer_tool: RealtimeFunctionTool

        @overload
        def __init__(
                self, 
                *, 
                active_node_id: str, 
                attempt_count: int, 
                available_edge_ids: list[str], 
                edges: list[VoiceAgentHandoffEdgeState], 
                node_generation: int, 
                nodes: list[VoiceAgentHandoffNodeState], 
                pipeline_family: Union[str, VoiceAgentPipelineFamily], 
                transfer_count: int, 
                transfer_tool: RealtimeFunctionTool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentHandoffTargetResponse(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"


    class azure.ai.voiceagents.models.VoiceAgentInterimResponseConfig(_Model):
        latency_threshold_ms: Optional[int]
        triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentInterimResponseTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATENCY = "latency"
        TOOL = "tool"


    class azure.ai.voiceagents.models.VoiceAgentLlmInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='llm_interim_response'):
        instructions: Optional[str]
        latency_threshold_ms: int
        max_completion_tokens: Optional[int]
        model: Optional[str]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["llm_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                latency_threshold_ms: Optional[int] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                model: Optional[str] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentMcpApprovalMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALWAYS = "always"
        NEVER_REQUIRE = "never"


    class azure.ai.voiceagents.models.VoiceAgentMcpAssignedManagedIdentity(_Model):
        audience: str
        client_id: Optional[str]
        type: Literal["assigned_managed_identity"]

        @overload
        def __init__(
                self, 
                *, 
                audience: str, 
                client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentMcpResponseScheduling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERRUPT = "interrupt"
        SILENT = "silent"
        SKIP_IF_BUSY = "skip_if_busy"
        WHEN_IDLE = "when_idle"


    class azure.ai.voiceagents.models.VoiceAgentMcpTool(_Model):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        defer_loading: Optional[bool]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        response_scheduling: Optional[Union[str, VoiceAgentMcpResponseScheduling]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                defer_loading: Optional[bool] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                response_scheduling: Optional[Union[str, VoiceAgentMcpResponseScheduling]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                type: Literal[ToolType.MCP]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentObject(_Model):
        agent_card: Optional[AgentCard]
        agent_endpoint: Optional[AgentEndpointConfig]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        id: str
        instance_identity: Optional[AgentIdentity]
        name: str
        object: Literal[AgentObjectType.AGENT]
        state: Union[str, AgentState]
        state_source: Optional[Union[str, AgentStateSource]]
        versions: VoiceAgentObjectVersions

        @overload
        def __init__(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                id: str, 
                name: str, 
                object: Literal[AgentObjectType.AGENT], 
                versions: VoiceAgentObjectVersions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentObjectVersions(_Model):
        latest: VoiceAgentVersionObject

        @overload
        def __init__(
                self, 
                *, 
                latest: VoiceAgentVersionObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentPipelineFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASCADED = "cascaded"
        REALTIME = "realtime"


    class azure.ai.voiceagents.models.VoiceAgentRealtimeResponse(_Model):
        conversation_id: Optional[str]
        estimated_cost: Optional[VoiceAgentEstimatedCost]
        id: str
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        modalities: Optional[list[Union[str, VoiceOutputModality]]]
        object: Literal["response"]
        output: list[VoiceAgentResponseItem]
        output_audio_format: Optional[Union[str, VoiceAgentResponseAudioFormat]]
        status: Union[str, VoiceAgentResponseStatus]
        status_details: RealtimeResponseStatusDetails
        temperature: Optional[float]
        usage: RealtimeResponseUsage
        voice: Optional[VoiceAgentVoice]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                estimated_cost: Optional[VoiceAgentEstimatedCost] = ..., 
                id: str, 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                output: list[VoiceAgentResponseItem], 
                output_audio_format: Optional[Union[str, VoiceAgentResponseAudioFormat]] = ..., 
                status: Union[str, VoiceAgentResponseStatus], 
                status_details: RealtimeResponseStatusDetails, 
                temperature: Optional[float] = ..., 
                usage: RealtimeResponseUsage, 
                voice: Optional[VoiceAgentVoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentResponseAudioFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G711_ALAW = "g711_alaw"
        G711_ULAW = "g711_ulaw"
        MP3 = "mp3"
        MP3_24_KHZ160_KBPS = "mp3_24khz_160kbps"
        MP3_24_KHZ48_KBPS = "mp3_24khz_48kbps"
        MP3_24_KHZ96_KBPS = "mp3_24khz_96kbps"
        PCM16 = "pcm16"
        PCM16_16000_HZ = "pcm16_16000hz"
        PCM16_22050_HZ = "pcm16_22050hz"
        PCM16_24000_HZ = "pcm16_24000hz"
        PCM16_44100_HZ = "pcm16_44100hz"
        PCM16_48000_HZ = "pcm16_48000hz"
        PCM16_8000_HZ = "pcm16_8000hz"


    class azure.ai.voiceagents.models.VoiceAgentResponseCreateAudio(_Model):
        output: Optional[VoiceAgentSessionUpdateAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceAgentSessionUpdateAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentResponseCreateParams(_Model):
        audio: Optional[VoiceAgentResponseCreateAudio]
        conversation: Optional[Union[Literal["auto"], Literal["none"], str]]
        input: Optional[list[RealtimeConversationItem]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[Metadata]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        pre_generated_assistant_message: Optional[RealtimeConversationItemMessageAssistant]
        reasoning: Optional[RealtimeReasoning]
        tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]]
        tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceAgentResponseCreateAudio] = ..., 
                conversation: Optional[Union[Literal[auto], Literal[none], str]] = ..., 
                input: Optional[list[RealtimeConversationItem]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                pre_generated_assistant_message: Optional[RealtimeConversationItemMessageAssistant] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]] = ..., 
                tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentResponseEventAudioContentPart(_Model):
        annotations: Optional[Any]
        audio: Optional[str]
        format: Optional[VoiceAudioFormat]
        transcript: str
        type: Literal["audio"]

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[Any] = ..., 
                audio: Optional[str] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                transcript: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentResponseEventTextContentPart(_Model):
        text: str
        type: Literal["text"]

        @overload
        def __init__(
                self, 
                *, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentResponseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.voiceagents.models.VoiceAgentSemanticVadTurnDetection(_Model):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        eagerness: Optional[Literal["low", "medium", "high", "auto"]]
        interrupt_response: Optional[bool]
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                eagerness: Optional[Literal[low, medium, high, auto]] = ..., 
                interrupt_response: Optional[bool] = ..., 
                type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationCreated(_Model):
        conversation_id: str
        type: Literal["created"]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemAdded(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemCreated(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemDeleted(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemDone(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted(_Model):
        content_index: int
        event_id: str
        item_id: str
        logprobs: Optional[list[LogProbProperties]]
        phrases: Optional[list[VoiceAgentTranscriptionPhrase]]
        transcript: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]
        usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                logprobs: Optional[list[LogProbProperties]] = ..., 
                phrases: Optional[list[VoiceAgentTranscriptionPhrase]] = ..., 
                transcript: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED], 
                usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionDelta(_Model):
        content_index: Optional[int]
        delta: Optional[str]
        event_id: str
        item_id: str
        logprobs: Optional[list[LogProbProperties]]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: Optional[int] = ..., 
                delta: Optional[str] = ..., 
                event_id: str, 
                item_id: str, 
                logprobs: Optional[list[LogProbProperties]] = ..., 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionFailed(_Model):
        content_index: int
        error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemInputAudioTranscriptionSegment(_Model):
        content_index: int
        end: float
        event_id: str
        id: str
        item_id: str
        speaker: str
        start: float
        text: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                end: float, 
                event_id: str, 
                id: str, 
                item_id: str, 
                speaker: str, 
                start: float, 
                text: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemRetrieved(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventConversationItemTruncated(_Model):
        audio_end_ms: int
        content_index: int
        event_id: str
        item: Optional[RealtimeConversationItemMessageAssistant]
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: str, 
                item: Optional[RealtimeConversationItemMessageAssistant] = ..., 
                item_id: str, 
                type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventError(_Model):
        error: VoiceAgentServerEventErrorDetails
        event_id: str
        type: Literal["error"]

        @overload
        def __init__(
                self, 
                *, 
                error: VoiceAgentServerEventErrorDetails, 
                event_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventErrorDetails(_Model):
        code: Optional[str]
        event_id: Optional[str]
        message: str
        param: Optional[str]
        tool_label: Optional[str]
        tool_type: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                tool_label: Optional[str] = ..., 
                tool_type: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventFileSearchCallCompleted(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["completed"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventFileSearchCallInProgress(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["in_progress"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventFileSearchCallSearching(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["searching"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventInputAudioBufferCleared(_Model):
        event_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventInputAudioBufferCommitted(_Model):
        event_id: str
        item_id: str
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                previous_item_id: Optional[str] = ..., 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventInputAudioBufferSpeechStarted(_Model):
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]

        @overload
        def __init__(
                self, 
                *, 
                audio_start_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventInputAudioBufferSpeechStopped(_Model):
        audio_end_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventInputAudioBufferTimeoutTriggered(_Model):
        audio_end_ms: int
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                audio_start_ms: int, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventMcpListToolsCompleted(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventMcpListToolsFailed(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventMcpListToolsInProgress(_Model):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventOutputAudioBufferCleared(_Model):
        event_id: str
        response_id: str
        type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventRateLimitsUpdated(_Model):
        event_id: str
        rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
        type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits], 
                type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAnimationBlendshapesDelta(_Model):
        content_index: int
        event_id: str
        frame_index: int
        frames: Union[list[list[float]], str]
        item_id: str
        output_index: int
        response_id: str
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                frame_index: int, 
                frames: Union[list[list[float]], str], 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAnimationBlendshapesDone(_Model):
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAnimationVisemeDelta(_Model):
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["delta"]
        viseme_id: int

        @overload
        def __init__(
                self, 
                *, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                viseme_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAnimationVisemeDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioDelta(_Model):
        content_index: int
        delta: bytes
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: bytes, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioTimestampDelta(_Model):
        audio_duration_ms: int
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal["word"]
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                audio_duration_ms: int, 
                audio_offset_ms: int, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioTimestampDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal["done"]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioTranscriptDelta(_Model):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseAudioTranscriptDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        transcript: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                transcript: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseContentPartDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: VoiceAgentResponseEventContentPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                part: VoiceAgentResponseEventContentPart, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseCreated(_Model):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse, 
                type: Literal[RealtimeServerEventType.RESPONSE_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseDone(_Model):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse, 
                type: Literal[RealtimeServerEventType.RESPONSE_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseFunctionCallArgumentsDelta(_Model):
        call_id: str
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseFunctionCallArgumentsDone(_Model):
        arguments: str
        call_id: str
        event_id: str
        item_id: str
        name: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: str, 
                event_id: str, 
                item_id: str, 
                name: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseMcpCallArgumentsDelta(_Model):
        delta: str
        event_id: str
        item_id: str
        obfuscation: Optional[str]
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                obfuscation: Optional[str] = ..., 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseMcpCallArgumentsDone(_Model):
        arguments: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseMcpCallCompleted(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseMcpCallFailed(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseMcpCallInProgress(_Model):
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseOutputItemAdded(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseOutputItemDone(_Model):
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: VoiceAgentResponseItem, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseTextDelta(_Model):
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                delta: str, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseTextDone(_Model):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str, 
                type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventResponseVideoDelta(_Model):
        codec: str
        delta: str
        event_id: str
        output_index: int
        type: Literal["delta"]

        @overload
        def __init__(
                self, 
                *, 
                codec: str, 
                delta: str, 
                event_id: str, 
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionAvatarConnecting(_Model):
        event_id: str
        server_sdp: str
        type: Literal["connecting"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                server_sdp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionAvatarSwitchToIdle(_Model):
        event_id: str
        turn_id: Optional[str]
        type: Literal["switch_to_idle"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking(_Model):
        event_id: str
        turn_id: Optional[str]
        type: Literal["switch_to_speaking"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionCreated(_Model):
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig, 
                type: Literal[RealtimeServerEventType.SESSION_CREATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionHandoffAborted(_Model):
        edge_id: str
        error: Optional[VoiceAgentServerEventErrorDetails]
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        reason: Union[str, VoiceAgentHandoffAbortReason]
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal["aborted"]

        @overload
        def __init__(
                self, 
                *, 
                edge_id: str, 
                error: Optional[VoiceAgentServerEventErrorDetails] = ..., 
                event_id: str, 
                from_model: str, 
                from_node_id: str, 
                handoff_id: str, 
                node_generation: int, 
                reason: Union[str, VoiceAgentHandoffAbortReason], 
                to_model: str, 
                to_node_id: str, 
                tool_call_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionHandoffCompleted(_Model):
        duration_ms: int
        edge_id: str
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        prepare_duration_ms: int
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal["completed"]

        @overload
        def __init__(
                self, 
                *, 
                duration_ms: int, 
                edge_id: str, 
                event_id: str, 
                from_model: str, 
                from_node_id: str, 
                handoff_id: str, 
                node_generation: int, 
                prepare_duration_ms: int, 
                to_model: str, 
                to_node_id: str, 
                tool_call_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionHandoffStarted(_Model):
        edge_id: str
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal["started"]

        @overload
        def __init__(
                self, 
                *, 
                edge_id: str, 
                event_id: str, 
                from_model: str, 
                from_node_id: str, 
                handoff_id: str, 
                node_generation: int, 
                to_model: str, 
                to_node_id: str, 
                tool_call_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventSessionUpdated(_Model):
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig, 
                type: Literal[RealtimeServerEventType.SESSION_UPDATED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventWarning(_Model):
        event_id: str
        type: Literal["warning"]
        warning: VoiceAgentServerEventWarningDetails

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                warning: VoiceAgentServerEventWarningDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventWarningDetails(_Model):
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


    class azure.ai.voiceagents.models.VoiceAgentServerEventWebSearchCallCompleted(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["completed"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventWebSearchCallInProgress(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["in_progress"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerEventWebSearchCallSearching(_Model):
        event_id: Optional[str]
        item_id: str
        output_index: int
        response_id: Optional[str]
        sequence_number: int
        type: Literal["searching"]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str, 
                output_index: int, 
                response_id: Optional[str] = ..., 
                sequence_number: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentServerVadTurnDetection(_Model):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[int] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ..., 
                type: Literal[VoiceTurnDetectionType.SERVER_VAD]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionAvatarConfig(_Model):
        character: str
        customized: Optional[bool]
        ice_servers: Optional[list[VoiceAgentAvatarIceServer]]
        model: Optional[str]
        output_audit_audio: Optional[bool]
        output_protocol: Optional[Union[str, VoiceAgentAvatarOutputProtocol]]
        scene: Optional[VoiceAgentAvatarScene]
        style: Optional[str]
        type: Optional[Union[str, VoiceAgentAvatarType]]
        video: Optional[VoiceAgentAvatarVideoParams]

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: Optional[bool] = ..., 
                ice_servers: Optional[list[VoiceAgentAvatarIceServer]] = ..., 
                model: Optional[str] = ..., 
                output_audit_audio: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, VoiceAgentAvatarOutputProtocol]] = ..., 
                scene: Optional[VoiceAgentAvatarScene] = ..., 
                style: Optional[str] = ..., 
                type: Optional[Union[str, VoiceAgentAvatarType]] = ..., 
                video: Optional[VoiceAgentAvatarVideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionIncludeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_SEARCH_CALL_RESULTS = "file_search_call.results"
        INPUT_AUDIO_TRANSCRIPTION_LOGPROBS = "item.input_audio_transcription.logprobs"
        INPUT_AUDIO_TRANSCRIPTION_PHRASES = "item.input_audio_transcription.phrases"


    class azure.ai.voiceagents.models.VoiceAgentSessionMcpTool(_Model):
        allowed_tools: Optional[list[str]]
        authorization: Optional[Union[str, VoiceAgentMcpAssignedManagedIdentity]]
        headers: Optional[dict[str, str]]
        require_approval: Optional[VoiceAgentMcpApprovalPolicy]
        response_scheduling: Optional[Union[str, VoiceAgentMcpResponseScheduling]]
        server_label: str
        server_url: str
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[list[str]] = ..., 
                authorization: Optional[Union[str, VoiceAgentMcpAssignedManagedIdentity]] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                require_approval: Optional[VoiceAgentMcpApprovalPolicy] = ..., 
                response_scheduling: Optional[Union[str, VoiceAgentMcpResponseScheduling]] = ..., 
                server_label: str, 
                server_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionResponseAudio(_Model):
        input: Optional[VoiceAgentSessionResponseAudioInput]
        output: Optional[VoiceAgentSessionResponseAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[VoiceAgentSessionResponseAudioInput] = ..., 
                output: Optional[VoiceAgentSessionResponseAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionResponseAudioInput(_Model):
        echo_cancellation: Optional[VoiceAgentEchoCancellation]
        format: Optional[VoiceAudioFormat]
        noise_reduction: Optional[VoiceNoiseReduction]
        transcription: Optional[VoiceInputTranscription]
        turn_detection: Optional[VoiceAgentTurnDetection]

        @overload
        def __init__(
                self, 
                *, 
                echo_cancellation: Optional[VoiceAgentEchoCancellation] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                noise_reduction: Optional[VoiceNoiseReduction] = ..., 
                transcription: Optional[VoiceInputTranscription] = ..., 
                turn_detection: Optional[VoiceAgentTurnDetection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionResponseAudioOutput(_Model):
        format: Optional[VoiceAudioFormat]
        output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]]
        speed: Optional[float]
        voice: Optional[VoiceAgentVoice]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[VoiceAudioFormat] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]] = ..., 
                speed: Optional[float] = ..., 
                voice: Optional[VoiceAgentVoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionResponseConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAgentSessionResponseAudio]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        expires_at: Optional[datetime]
        greeting: Optional[VoiceGreetingConfig]
        handoff: Optional[VoiceAgentHandoffState]
        id: str
        idle_timeout: Optional[int]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        model: str
        object: Literal["session"]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        response_delimiter: Optional[str]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentSessionTool]]
        type: Literal["realtime"]
        voice_adaptation: Optional[VoiceAgentVoiceAdaptation]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAgentSessionResponseAudio] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                expires_at: Optional[datetime] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                handoff: Optional[VoiceAgentHandoffState] = ..., 
                id: str, 
                idle_timeout: Optional[int] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                model: str, 
                output_modalities: list[Union[str, VoiceOutputModality]], 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                response_delimiter: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentSessionTool]] = ..., 
                voice_adaptation: Optional[VoiceAgentVoiceAdaptation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionUpdateAudio(_Model):
        input: Optional[VoiceAgentSessionUpdateAudioInput]
        output: Optional[VoiceAgentSessionUpdateAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[VoiceAgentSessionUpdateAudioInput] = ..., 
                output: Optional[VoiceAgentSessionUpdateAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionUpdateAudioInput(_Model):
        echo_cancellation: Optional[VoiceAgentEchoCancellation]
        format: Optional[VoiceAudioFormat]
        noise_reduction: Optional[VoiceNoiseReduction]
        transcription: Optional[VoiceInputTranscription]
        turn_detection: Optional[VoiceAgentTurnDetection]

        @overload
        def __init__(
                self, 
                *, 
                echo_cancellation: Optional[VoiceAgentEchoCancellation] = ..., 
                format: Optional[VoiceAudioFormat] = ..., 
                noise_reduction: Optional[VoiceNoiseReduction] = ..., 
                transcription: Optional[VoiceInputTranscription] = ..., 
                turn_detection: Optional[VoiceAgentTurnDetection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionUpdateAudioOutput(_Model):
        format: Optional[VoiceAudioFormat]
        output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]]
        speed: Optional[float]
        voice: Optional[VoiceAgentVoice]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[VoiceAudioFormat] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]] = ..., 
                speed: Optional[float] = ..., 
                voice: Optional[VoiceAgentVoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentSessionUpdateConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAgentSessionUpdateAudio]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        greeting: Optional[VoiceGreetingConfig]
        handoff: Optional[VoiceAgentHandoffGraphConfig]
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponse]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        response_delimiter: Optional[str]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentSessionTool]]
        type: Literal["realtime"]
        voice_adaptation: Optional[VoiceAgentVoiceAdaptation]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAgentSessionUpdateAudio] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                greeting: Optional[VoiceGreetingConfig] = ..., 
                handoff: Optional[VoiceAgentHandoffGraphConfig] = ..., 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponse] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                response_delimiter: Optional[str] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentSessionTool]] = ..., 
                voice_adaptation: Optional[VoiceAgentVoiceAdaptation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentStaticInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='static_interim_response'):
        latency_threshold_ms: int
        texts: Optional[list[str]]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["static_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[int] = ..., 
                texts: Optional[list[str]] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentTranscriptionPhrase(_Model):
        confidence: Optional[float]
        duration_milliseconds: int
        locale: Optional[str]
        offset_milliseconds: int
        text: str
        words: Optional[list[VoiceAgentTranscriptionWord]]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                duration_milliseconds: int, 
                locale: Optional[str] = ..., 
                offset_milliseconds: int, 
                text: str, 
                words: Optional[list[VoiceAgentTranscriptionWord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentTranscriptionWord(_Model):
        duration_milliseconds: int
        offset_milliseconds: int
        text: str

        @overload
        def __init__(
                self, 
                *, 
                duration_milliseconds: int, 
                offset_milliseconds: int, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUSINESS = "business"
        PERSONAL = "personal"


    class azure.ai.voiceagents.models.VoiceAgentUseCase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALL_CENTER = "call_center"
        CUSTOMER_SUPPORT = "customer_support"
        IN_CAR = "in_car"
        LEARNING = "learning"
        OUTREACH = "outreach"
        PERSONAL_ASSISTANT = "personal_assistant"
        RECEPTION = "reception"
        SALES = "sales"
        TRAVEL_ASSISTANT = "travel_assistant"


    class azure.ai.voiceagents.models.VoiceAgentVersionObject(_Model):
        agent_guid: Optional[str]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        created_at: datetime
        definition: VoiceAgentDefinition
        description: Optional[str]
        draft: Optional[bool]
        id: str
        instance_identity: Optional[AgentIdentity]
        metadata: dict[str, str]
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION]
        status: Optional[Union[str, AgentVersionStatus]]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                id: str, 
                metadata: dict[str, str], 
                name: str, 
                object: Literal[AgentObjectType.AGENT_VERSION], 
                status: Optional[Union[str, AgentVersionStatus]] = ..., 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentVoiceAdaptation(_Model):
        type: Literal["auto"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSearchActionFind(_Model):
        pattern: str
        type: Literal["find"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                pattern: str, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSearchActionOpenPage(_Model):
        type: Literal["open_page"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSearchActionSearch(_Model):
        query: str
        sources: Optional[list[VoiceAgentWebSearchSource]]
        type: Literal["search"]

        @overload
        def __init__(
                self, 
                *, 
                query: str, 
                sources: Optional[list[VoiceAgentWebSearchSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSearchCallItem(_Model):
        action: Optional[VoiceAgentWebSearchAction]
        id: str
        status: Union[str, VoiceAgentWebSearchCallStatus]
        type: Literal["web_search_call"]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[VoiceAgentWebSearchAction] = ..., 
                id: str, 
                status: Union[str, VoiceAgentWebSearchCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSearchCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        SEARCHING = "searching"


    class azure.ai.voiceagents.models.VoiceAgentWebSearchSource(_Model):
        type: Literal["url"]
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAgentWebSocketSubprotocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REALTIME = "realtime"


    class azure.ai.voiceagents.models.VoiceAgentWorkflowActionItem(_Model):
        action_id: str
        id: str
        kind: Optional[str]
        object: Optional[Literal["item"]]
        parent_action_id: Optional[str]
        previous_action_id: Optional[str]
        status: str
        type: Literal["workflow_action"]

        @overload
        def __init__(
                self, 
                *, 
                action_id: str, 
                id: str, 
                kind: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                parent_action_id: Optional[str] = ..., 
                previous_action_id: Optional[str] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAssistantMessageItem(VoiceMessageItem, discriminator='assistant'):
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.voiceagents.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageAssistantContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAudioCodec(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM16 = "pcm16"
        PCMA = "pcma"
        PCMU = "pcmu"


    class azure.ai.voiceagents.models.VoiceAudioConfig(_Model):
        input: Optional[VoiceAudioInputConfig]
        output: Optional[VoiceAudioOutputConfig]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[VoiceAudioInputConfig] = ..., 
                output: Optional[VoiceAudioOutputConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAudioContainerFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAV = "wav"


    class azure.ai.voiceagents.models.VoiceAudioFormat(_Model):
        rate: Optional[int]
        type: Union[str, VoiceAudioFormatType]

        @overload
        def __init__(
                self, 
                *, 
                rate: Optional[int] = ..., 
                type: Union[str, VoiceAudioFormatType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAudioFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM = "audio/pcm"
        PCMA = "audio/pcma"
        PCMU = "audio/pcmu"


    class azure.ai.voiceagents.models.VoiceAudioInputConfig(_Model):
        format: Optional[VoiceAudioFormat]
        noise_reduction: Optional[VoiceNoiseReduction]
        transcription: Optional[VoiceInputTranscription]
        turn_detection: Optional[VoiceTurnDetection]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[VoiceAudioFormat] = ..., 
                noise_reduction: Optional[VoiceNoiseReduction] = ..., 
                transcription: Optional[VoiceInputTranscription] = ..., 
                turn_detection: Optional[VoiceTurnDetection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAudioOutputConfig(_Model):
        format: Optional[VoiceAudioFormat]
        output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]]
        speed: Optional[float]
        voice: Optional[VoiceAgentVoice]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[VoiceAudioFormat] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, VoiceAudioTimestampType]]] = ..., 
                speed: Optional[float] = ..., 
                voice: Optional[VoiceAgentVoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAudioRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        USER = "user"


    class azure.ai.voiceagents.models.VoiceAudioTimestampType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORD = "word"


    class azure.ai.voiceagents.models.VoiceAvatarConfig(_Model):
        character: str
        customized: Optional[bool]
        output_protocol: Optional[Union[str, VoiceAvatarOutputProtocol]]
        style: Optional[str]
        type: Union[str, VoiceAvatarType]

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, VoiceAvatarOutputProtocol]] = ..., 
                style: Optional[str] = ..., 
                type: Union[str, VoiceAvatarType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAvatarOutputProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"


    class azure.ai.voiceagents.models.VoiceAvatarType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHOTO_AVATAR = "photo_avatar"
        VIDEO_AVATAR = "video_avatar"


    class azure.ai.voiceagents.models.VoiceAzureSemanticDetection(VoiceEndOfUtteranceDetection, discriminator='semantic_detection_v1'):
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1]
        threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAzureSemanticDetectionEn(VoiceEndOfUtteranceDetection, discriminator='semantic_detection_v1_en'):
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_EN]
        threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAzureSemanticDetectionMultilingual(VoiceEndOfUtteranceDetection, discriminator='semantic_detection_v1_multilingual'):
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_MULTILINGUAL]
        threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]]
        timeout_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                threshold_level: Optional[Union[str, VoiceEndOfUtteranceThresholdLevel]] = ..., 
                timeout_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAzureSemanticVadEnTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad_en'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                speech_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceAzureSemanticVadMultilingualTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad_multilingual'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
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


    class azure.ai.voiceagents.models.VoiceAzureSemanticVadTurnDetection(VoiceTurnDetection, discriminator='azure_semantic_vad'):
        auto_truncate: Optional[bool]
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[int]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceEndOfUtteranceDetection] = ..., 
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


    class azure.ai.voiceagents.models.VoiceConversation(_Model):
        completed_at: Optional[datetime]
        created_at: datetime
        id: str
        metadata: Optional[dict[str, str]]
        object: Literal["conversation"]
        status: Union[str, VoiceConversationStatus]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                created_at: datetime, 
                id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                status: Union[str, VoiceConversationStatus], 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceConversationItem(_Model):
        created_at: Optional[datetime]
        response_id: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                response_id: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.voiceagents.models.VoiceConversationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        IN_PROGRESS = "in_progress"


    class azure.ai.voiceagents.models.VoiceEndOfUtteranceDetection(_Model):
        model: str

        @overload
        def __init__(
                self, 
                *, 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceEndOfUtteranceDetectionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_DETECTION_V1 = "semantic_detection_v1"
        SEMANTIC_DETECTION_V1_EN = "semantic_detection_v1_en"
        SEMANTIC_DETECTION_V1_MULTILINGUAL = "semantic_detection_v1_multilingual"


    class azure.ai.voiceagents.models.VoiceEndOfUtteranceThresholdLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.voiceagents.models.VoiceFunctionCallItem(VoiceConversationItem, discriminator='function_call'):
        arguments: str
        call_id: Optional[str]
        created_at: datetime
        id: Optional[str]
        name: str
        object: Optional[Literal["item"]]
        response_id: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                call_id: Optional[str] = ..., 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceFunctionCallOutputItem(VoiceConversationItem, discriminator='function_call_output'):
        call_id: str
        created_at: datetime
        id: Optional[str]
        name: Optional[str]
        object: Optional[Literal["item"]]
        output: str
        response_id: str
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str, 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceGreetingConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceGreetingToolChoice(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.voiceagents.models.VoiceIdsShared(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.ai.voiceagents.models.VoiceInputTranscription(_Model):
        custom_speech: Optional[dict[str, str]]
        delay: Optional[Literal["minimal", "low", "medium", "high", "xhigh"]]
        language: Optional[str]
        model: Union[str, VoiceInputTranscriptionModel]
        phrase_list: Optional[list[str]]
        prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_speech: Optional[dict[str, str]] = ..., 
                delay: Optional[Literal[minimal, low, medium, high, xhigh]] = ..., 
                language: Optional[str] = ..., 
                model: Union[str, VoiceInputTranscriptionModel], 
                phrase_list: Optional[list[str]] = ..., 
                prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceInputTranscriptionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SPEECH = "azure-speech"
        GPT4_O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
        GPT4_O_TRANSCRIBE = "gpt-4o-transcribe"
        GPT4_O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"
        GPT_LIVE_TRANSCRIBE = "gpt-live-transcribe"
        GPT_REALTIME_WHISPER = "gpt-realtime-whisper"
        GPT_TRANSCRIBE = "gpt-transcribe"
        MAI_TRANSCRIBE = "mai-transcribe"
        WHISPER1 = "whisper-1"


    class azure.ai.voiceagents.models.VoiceItemAudioResponse(_Model):
        blob_uri: Optional[str]
        channels: Optional[int]
        codec: Optional[Union[str, VoiceAudioCodec]]
        conversation_id: str
        duration_ms: Optional[timedelta]
        format: Optional[Union[str, VoiceAudioContainerFormat]]
        item_id: str
        role: Optional[Union[str, VoiceAudioRole]]
        sample_rate: Optional[int]
        start_offset_ms: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                channels: Optional[int] = ..., 
                codec: Optional[Union[str, VoiceAudioCodec]] = ..., 
                conversation_id: str, 
                duration_ms: Optional[timedelta] = ..., 
                format: Optional[Union[str, VoiceAudioContainerFormat]] = ..., 
                item_id: str, 
                role: Optional[Union[str, VoiceAudioRole]] = ..., 
                sample_rate: Optional[int] = ..., 
                start_offset_ms: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMcpApprovalRequestItem(VoiceConversationItem, discriminator='mcp_approval_request'):
        arguments: str
        created_at: datetime
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]

        @overload
        def __init__(
                self, 
                *, 
                arguments: str, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                name: str, 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMcpApprovalResponseItem(VoiceConversationItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        created_at: datetime
        id: str
        reason: Optional[str]
        response_id: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: str, 
                approve: bool, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                reason: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMcpCallItem(VoiceConversationItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        created_at: datetime
        error: Optional[RealtimeMCPError]
        id: str
        name: str
        output: Optional[str]
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_CALL]

        @overload
        def __init__(
                self, 
                *, 
                approval_request_id: Optional[str] = ..., 
                arguments: str, 
                created_at: Optional[datetime] = ..., 
                error: Optional[RealtimeMCPError] = ..., 
                id: str, 
                name: str, 
                output: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                server_label: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMcpListToolsItem(VoiceConversationItem, discriminator='mcp_list_tools'):
        created_at: datetime
        id: Optional[str]
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[VoiceConversationItemType.MCP_LIST_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                response_id: Optional[str] = ..., 
                server_label: str, 
                tools: list[MCPListToolsTool]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMessageItem(VoiceConversationItem, discriminator='message'):
        created_at: datetime
        response_id: str
        role: str
        type: Literal[VoiceConversationItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                response_id: Optional[str] = ..., 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "managed"
        SELF_DEPLOYED = "self_deployed"


    class azure.ai.voiceagents.models.VoiceNoiseReduction(_Model):
        type: Union[str, VoiceNoiseReductionType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, VoiceNoiseReductionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceNoiseReductionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEEP_NOISE_SUPPRESSION = "azure_deep_noise_suppression"
        FAR_FIELD = "far_field"
        NEAR_FIELD = "near_field"


    class azure.ai.voiceagents.models.VoiceOutputModality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANIMATION = "animation"
        AUDIO = "audio"
        AVATAR = "avatar"
        TEXT = "text"


    class azure.ai.voiceagents.models.VoiceRecordingChannelLayout(_Model):
        left: Literal["user"]
        right: Literal["agent"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.voiceagents.models.VoiceRecordingResponse(_Model):
        blob_uri: Optional[str]
        channel_layout: VoiceRecordingChannelLayout
        channels: int
        conversation_id: str
        duration_ms: timedelta
        format: Union[str, VoiceAudioContainerFormat]
        sample_rate: int

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                channel_layout: VoiceRecordingChannelLayout, 
                channels: int, 
                conversation_id: str, 
                duration_ms: timedelta, 
                format: Union[str, VoiceAudioContainerFormat], 
                sample_rate: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceResponse(_Model):
        audio: Optional[VoiceResponseAudio]
        completed_at: Optional[datetime]
        conversation_id: str
        created_at: Optional[datetime]
        id: str
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        object: Literal["response"]
        output: Optional[list[VoiceConversationItem]]
        output_modalities: Optional[list[Literal["text", "audio"]]]
        status: Union[str, VoiceResponseStatus]
        status_details: Optional[RealtimeResponseStatusDetails]
        temperature: Optional[float]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceResponseAudio] = ..., 
                completed_at: Optional[datetime] = ..., 
                conversation_id: str, 
                created_at: Optional[datetime] = ..., 
                id: str, 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                output: Optional[list[VoiceConversationItem]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Union[str, VoiceResponseStatus], 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                temperature: Optional[float] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceResponseAudio(_Model):
        output: Optional[VoiceResponseAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceResponseAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceResponseAudioOutput(_Model):
        format: Optional[RealtimeAudioFormats]
        voice: Optional[VoiceResponseVoice]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[RealtimeAudioFormats] = ..., 
                voice: Optional[VoiceResponseVoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceResponseStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        COMPLETED = "completed"
        FAILED = "failed"
        INCOMPLETE = "incomplete"
        IN_PROGRESS = "in_progress"


    class azure.ai.voiceagents.models.VoiceSemanticVadTurnDetection(VoiceTurnDetection, discriminator='semantic_vad'):
        create_response: Optional[bool]
        eagerness: Optional[Literal["low", "medium", "high", "auto"]]
        interrupt_response: Optional[bool]
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                create_response: Optional[bool] = ..., 
                eagerness: Optional[Literal[low, medium, high, auto]] = ..., 
                interrupt_response: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceServerVadTurnDetection(VoiceTurnDetection, discriminator='server_vad'):
        create_response: Optional[bool]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]

        @overload
        def __init__(
                self, 
                *, 
                create_response: Optional[bool] = ..., 
                idle_timeout_ms: Optional[int] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceSystemMessageItem(VoiceMessageItem, discriminator='system'):
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.voiceagents.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageSystemContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceSystemTool(_Model):
        description: Optional[str]
        name: Union[str, VoiceSystemToolName]
        type: Literal["system"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Union[str, VoiceSystemToolName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceSystemToolName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        END_CONVERSATION = "end_conversation"


    class azure.ai.voiceagents.models.VoiceToolboxTool(_Model):
        toolbox_name: str
        toolbox_version: str
        type: Literal["toolbox"]

        @overload
        def __init__(
                self, 
                *, 
                toolbox_name: str, 
                toolbox_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceTurnDetection(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.voiceagents.models.VoiceUserMessageItem(VoiceMessageItem, discriminator='user'):
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: datetime
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.voiceagents.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageUserContent], 
                created_at: Optional[datetime] = ..., 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                response_id: Optional[str] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.voiceagents.operations

    class azure.ai.voiceagents.operations.AgentEndpointConversationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def delete_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace
        def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace
        def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace
        def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace
        def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceResponse]: ...


    class azure.ai.voiceagents.operations.VoiceAgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_voice_agent(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                state: Optional[Union[str, AgentState]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def create_voice_agent(
                self, 
                body: CreateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def create_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def create_voice_agent_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: CreateVoiceAgentVersionRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def delete_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def generate_voice_agent(
                self, 
                *, 
                agent_type: Union[str, VoiceAgentType], 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                goal: str, 
                model: str, 
                model_type: Union[str, VoiceModelType], 
                name: str, 
                tools: Optional[list[VoiceAgentTool]] = ..., 
                use_case: Union[str, VoiceAgentUseCase], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def generate_voice_agent(
                self, 
                body: GenerateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def generate_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace
        def get_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace
        def get_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def list_voice_agent_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceAgentVersionObject]: ...

        @distributed_trace
        def list_voice_agents(
                self, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceAgentObject]: ...

        @overload
        def update_voice_agent(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: VoiceAgentDefinition, 
                description: Optional[str] = ..., 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def update_voice_agent(
                self, 
                agent_name: str, 
                body: UpdateVoiceAgentRequest, 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def update_voice_agent(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW], 
                **kwargs: Any
            ) -> VoiceAgentObject: ...


namespace azure.ai.voiceagents.types

    class azure.ai.voiceagents.types.A2AProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.ActivityProtocolConfiguration(TypedDict, total=False):
        key "enable_m365_public_endpoint": bool
        enable_m365_public_endpoint: bool


    class azure.ai.voiceagents.types.AgentBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.voiceagents.types.AgentBlueprintReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_AGENT_IDENTITY_BLUEPRINT = "ManagedAgentIdentityBlueprint"


    class azure.ai.voiceagents.types.AgentCard(TypedDict, total=False):
        key "description": str
        key "skills": Required[list[AgentCardSkill]]
        key "version": Required[str]
        description: str
        skills: list[AgentCardSkill]
        version: str


    class azure.ai.voiceagents.types.AgentCardSkill(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        description: str
        examples: list[str]
        id: str
        name: str
        tags: list[str]


    class azure.ai.voiceagents.types.AgentEndpointAuthorizationSchemeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT_SERVICE = "BotService"
        BOT_SERVICE_RBAC = "BotServiceRbac"
        BOT_SERVICE_TENANT = "BotServiceTenant"
        ENTRA = "Entra"


    class azure.ai.voiceagents.types.AgentEndpointConfig(TypedDict, total=False):
        key "protocol_configuration": ForwardRef('ProtocolConfiguration', module='types')
        key "version_selector": ForwardRef('VersionSelector', module='types')
        authorization_schemes: list[AgentEndpointAuthorizationScheme]
        protocol_configuration: ProtocolConfiguration
        version_selector: VersionSelector


    class azure.ai.voiceagents.types.AzureAvatarVoiceSyncVoice(TypedDict, total=False):
        key "custom_lexicon_url": str
        key "custom_text_normalization_url": str
        key "locale": str
        key "model": Required[Union[str, PersonalVoiceModel]]
        key "pitch": str
        key "rate": str
        key "style": str
        key "temperature": float
        key "type": Required[Literal[AzureVoiceType.AVATAR_VOICE_SYNC]]
        key "volume": str
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        model: Union[str, PersonalVoiceModel]
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AVATAR_VOICE_SYNC]
        volume: str


    class azure.ai.voiceagents.types.AzureCustomVoice(TypedDict, total=False):
        key "custom_lexicon_url": str
        key "custom_text_normalization_url": str
        key "endpoint_id": Required[str]
        key "locale": str
        key "name": Required[str]
        key "pitch": str
        key "rate": str
        key "style": str
        key "temperature": float
        key "type": Required[Literal[AzureVoiceType.AZURE_CUSTOM]]
        key "volume": str
        custom_lexicon_url: str
        custom_text_normalization_url: str
        endpoint_id: str
        locale: str
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_CUSTOM]
        volume: str


    class azure.ai.voiceagents.types.AzurePersonalVoice(TypedDict, total=False):
        key "custom_lexicon_url": str
        key "custom_text_normalization_url": str
        key "locale": str
        key "model": Required[Union[str, PersonalVoiceModel]]
        key "name": Required[str]
        key "pitch": str
        key "rate": str
        key "style": str
        key "temperature": float
        key "type": Required[Literal[AzureVoiceType.AZURE_PERSONAL]]
        key "volume": str
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        model: Union[str, PersonalVoiceModel]
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_PERSONAL]
        volume: str


    class azure.ai.voiceagents.types.AzureRealtimeNativeVoice(TypedDict, total=False):
        key "name": Required[Union[str, AzureRealtimeNativeVoiceName]]
        key "type": Required[Literal["azure-realtime-native"]]
        name: Union[str, AzureRealtimeNativeVoiceName]
        type: Literal[azure-realtime-native]


    class azure.ai.voiceagents.types.AzureStandardVoice(TypedDict, total=False):
        key "custom_lexicon_url": str
        key "custom_text_normalization_url": str
        key "locale": str
        key "multi_talker_speaker_name": str
        key "name": Required[str]
        key "pitch": str
        key "rate": str
        key "style": str
        key "temperature": float
        key "type": Required[Literal[AzureVoiceType.AZURE_STANDARD]]
        key "volume": str
        custom_lexicon_url: str
        custom_text_normalization_url: str
        locale: str
        multi_talker_speaker_name: str
        name: str
        pitch: str
        prefer_locales: list[str]
        rate: str
        style: str
        temperature: float
        type: Literal[AzureVoiceType.AZURE_STANDARD]
        volume: str


    class azure.ai.voiceagents.types.AzureVoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVATAR_VOICE_SYNC = "avatar-voice-sync"
        AZURE_CUSTOM = "azure-custom"
        AZURE_PERSONAL = "azure-personal"
        AZURE_STANDARD = "azure-standard"


    class azure.ai.voiceagents.types.BotServiceAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]


    class azure.ai.voiceagents.types.BotServiceRbacAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]


    class azure.ai.voiceagents.types.BotServiceTenantAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]


    class azure.ai.voiceagents.types.CreateTranscriptionResponseJsonUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DURATION = "duration"
        TOKENS = "tokens"


    class azure.ai.voiceagents.types.CreateVoiceAgentRequest(TypedDict, total=False):
        key "agent_card": ForwardRef('AgentCard', module='types')
        key "agent_endpoint": ForwardRef('AgentEndpointConfig', module='types')
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "definition": Required[VoiceAgentDefinition]
        key "description": str
        key "draft": bool
        key "name": Required[str]
        key "state": Union[str, AgentState]
        agent_card: AgentCard
        agent_endpoint: AgentEndpointConfig
        blueprint_reference: AgentBlueprintReference
        definition: VoiceAgentDefinition
        description: str
        draft: bool
        metadata: dict[str, str]
        name: str
        state: Union[str, AgentState]


    class azure.ai.voiceagents.types.CreateVoiceAgentVersionRequest(TypedDict, total=False):
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "definition": Required[VoiceAgentDefinition]
        key "description": str
        key "draft": bool
        blueprint_reference: AgentBlueprintReference
        definition: VoiceAgentDefinition
        description: str
        draft: bool
        metadata: dict[str, str]


    class azure.ai.voiceagents.types.EntraAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.ENTRA]]
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]


    class azure.ai.voiceagents.types.FixedRatioVersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[VersionSelectorType.FIXED_RATIO]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.voiceagents.types.GenerateVoiceAgentRequest(TypedDict, total=False):
        key "agent_type": Required[Union[str, VoiceAgentType]]
        key "description": str
        key "draft": bool
        key "goal": Required[str]
        key "model": Required[str]
        key "model_type": Required[Union[str, VoiceModelType]]
        key "name": Required[str]
        key "use_case": Required[Union[str, VoiceAgentUseCase]]
        agent_type: Union[str, VoiceAgentType]
        description: str
        draft: bool
        goal: str
        model: str
        model_type: Union[str, VoiceModelType]
        name: str
        tools: list[VoiceAgentTool]
        use_case: Union[str, VoiceAgentUseCase]


    class azure.ai.voiceagents.types.InvocationsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.InvocationsWsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.LlmGeneratedVoiceGreetingConfig(TypedDict, total=False):
        key "fallback_text": str
        key "prompt": Required[str]
        key "tool_choice": Union[str, VoiceGreetingToolChoice]
        key "type": Required[Literal["llm_generated"]]
        fallback_text: str
        prompt: str
        tool_choice: Union[str, VoiceGreetingToolChoice]
        type: Literal[llm_generated]


    class azure.ai.voiceagents.types.LogProbProperties(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        bytes: list[int]
        logprob: float
        token: str


    class azure.ai.voiceagents.types.MCPListToolsTool(TypedDict, total=False):
        key "annotations": Optional[MCPListToolsToolAnnotations]
        key "description": Optional[str]
        key "input_schema": Required[MCPListToolsToolInputSchema]
        key "name": Required[str]
        annotations: MCPListToolsToolAnnotations
        description: str
        input_schema: MCPListToolsToolInputSchema
        name: str


    class azure.ai.voiceagents.types.MCPListToolsToolAnnotations(TypedDict, total=False):


    class azure.ai.voiceagents.types.MCPListToolsToolInputSchema(TypedDict, total=False):


    class azure.ai.voiceagents.types.MCPTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "connector_id": Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]
        key "defer_loading": bool
        key "headers": Optional[dict[str, str]]
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "tunnel_id": str
        key "type": Required[Literal[ToolType.MCP]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        connector_id: Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams,
        defer_loading: bool
        headers: dict[str, str]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        tunnel_id: str
        type: Literal[ToolType.MCP]


    class azure.ai.voiceagents.types.MCPToolFilter(TypedDict, total=False):
        key "read_only": bool
        read_only: bool
        tool_names: list[str]


    class azure.ai.voiceagents.types.MCPToolRequireApproval(TypedDict, total=False):
        key "always": ForwardRef('MCPToolFilter', module='types')
        key "never": ForwardRef('MCPToolFilter', module='types')
        always: MCPToolFilter
        never: MCPToolFilter


    class azure.ai.voiceagents.types.ManagedAgentIdentityBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.voiceagents.types.McpProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.Metadata(TypedDict, total=False):


    class azure.ai.voiceagents.types.OpenAIVoice(TypedDict, total=False):
        key "name": Required[Union[str, VoiceIdsShared]]
        key "type": Required[Literal["openai"]]
        name: Union[str, VoiceIdsShared]
        type: Literal[openai]


    class azure.ai.voiceagents.types.ProtocolConfiguration(TypedDict, total=False):
        key "a2a": ForwardRef('A2AProtocolConfiguration', module='types')
        key "activity": ForwardRef('ActivityProtocolConfiguration', module='types')
        key "invocations": ForwardRef('InvocationsProtocolConfiguration', module='types')
        key "invocations_ws": ForwardRef('InvocationsWsProtocolConfiguration', module='types')
        key "mcp": ForwardRef('McpProtocolConfiguration', module='types')
        key "responses": ForwardRef('ResponsesProtocolConfiguration', module='types')
        a2a: A2AProtocolConfiguration
        activity: ActivityProtocolConfiguration
        invocations: InvocationsProtocolConfiguration
        invocations_ws: InvocationsWsProtocolConfiguration
        mcp: McpProtocolConfiguration
        responses: ResponsesProtocolConfiguration


    class azure.ai.voiceagents.types.RaiConfig(TypedDict, total=False):
        key "rai_policy_name": Required[str]
        rai_policy_name: str


    class azure.ai.voiceagents.types.RealtimeClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_ITEM_CREATE = "conversation.item.create"
        CONVERSATION_ITEM_DELETE = "conversation.item.delete"
        CONVERSATION_ITEM_RETRIEVE = "conversation.item.retrieve"
        CONVERSATION_ITEM_TRUNCATE = "conversation.item.truncate"
        INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer.append"
        INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer.clear"
        INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer.commit"
        OUTPUT_AUDIO_BUFFER_CLEAR = "output_audio_buffer.clear"
        RESPONSE_CANCEL = "response.cancel"
        RESPONSE_CREATE = "response.create"
        SESSION_UPDATE = "session.update"


    class azure.ai.voiceagents.types.RealtimeConversationItemFunctionCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": str
        key "id": str
        key "name": Required[str]
        key "object": Literal["item"]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[RealtimeConversationItemType.FUNCTION_CALL]]
        arguments: str
        call_id: str
        id: str
        name: str
        object: Literal[item]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL]


    class azure.ai.voiceagents.types.RealtimeConversationItemFunctionCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "object": Literal["item"]
        key "output": Required[str]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]]
        call_id: str
        id: str
        object: Literal[item]
        output: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageAssistant(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageAssistantContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.ASSISTANT]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageAssistantContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageAssistantContent(TypedDict, total=False):
        key "audio": str
        key "text": str
        key "transcript": str
        key "type": Literal["output_text", "output_audio"]
        audio: str
        text: str
        transcript: str
        type: Literal[output_text, output_audio]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageSystem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageSystemContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.SYSTEM]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageSystemContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageSystemContent(TypedDict, total=False):
        key "text": str
        key "type": Literal["input_text"]
        text: str
        type: Literal[input_text]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageUser(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageUserContent]]
        key "id": str
        key "object": Literal["item"]
        key "role": Required[Literal[RealtimeConversationItemMessageType.USER]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal["message"]]
        content: list[RealtimeConversationItemMessageUserContent]
        id: str
        object: Literal[item]
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[message]


    class azure.ai.voiceagents.types.RealtimeConversationItemMessageUserContent(TypedDict, total=False):
        key "audio": str
        key "detail": Literal["auto", "low", "high"]
        key "image_url": str
        key "text": str
        key "transcript": str
        key "type": Literal["input_text", "input_audio", "input_image"]
        audio: str
        detail: Literal[auto, low, high]
        image_url: str
        text: str
        transcript: str
        type: Literal[input_text, input_audio, input_image]


    class azure.ai.voiceagents.types.RealtimeConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"


    class azure.ai.voiceagents.types.RealtimeFunctionTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "parameters": ForwardRef('RealtimeFunctionToolParameters', module='types')
        key "type": Literal["function"]
        description: str
        name: str
        parameters: RealtimeFunctionToolParameters
        type: Literal[function]


    class azure.ai.voiceagents.types.RealtimeFunctionToolParameters(TypedDict, total=False):


    class azure.ai.voiceagents.types.RealtimeMCPApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.voiceagents.types.RealtimeMCPApprovalResponse(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[RealtimeConversationItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.voiceagents.types.RealtimeMCPHTTPError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.HTTP_ERROR]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.HTTP_ERROR]


    class azure.ai.voiceagents.types.RealtimeMCPListTools(TypedDict, total=False):
        key "id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]]
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[RealtimeConversationItemType.MCP_LIST_TOOLS]


    class azure.ai.voiceagents.types.RealtimeMCPProtocolError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]


    class azure.ai.voiceagents.types.RealtimeMCPToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[RealtimeConversationItemType.MCP_CALL]]
        approval_request_id: str
        arguments: str
        error: RealtimeMCPError
        id: str
        name: str
        output: str
        server_label: str
        type: Literal[RealtimeConversationItemType.MCP_CALL]


    class azure.ai.voiceagents.types.RealtimeMCPToolExecutionError(TypedDict, total=False):
        key "message": Required[str]
        key "type": Required[Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]]
        message: str
        type: Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]


    class azure.ai.voiceagents.types.RealtimeMcpErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP_ERROR = "http_error"
        PROTOCOL_ERROR = "protocol_error"
        TOOL_EXECUTION_ERROR = "tool_execution_error"


    class azure.ai.voiceagents.types.RealtimeReasoning(TypedDict, total=False):
        key "effort": Union[str, RealtimeReasoningEffort]
        effort: Union[str, RealtimeReasoningEffort]


    class azure.ai.voiceagents.types.RealtimeResponseStatusDetails(TypedDict, total=False):
        key "error": ForwardRef('RealtimeResponseStatusDetailsError', module='types')
        key "reason": Literal["turn_detected", "client_cancelled", "max_output_tokens", "content_filter"]
        key "type": Literal["completed", "cancelled", "failed", "incomplete"]
        error: RealtimeResponseStatusDetailsError
        reason: Literal[turn_detected, client_cancelled, max_output_tokens, content_filter]
        type: Literal[completed, cancelled, failed, incomplete]


    class azure.ai.voiceagents.types.RealtimeResponseStatusDetailsError(TypedDict, total=False):
        key "code": str
        key "type": str
        code: str
        type: str


    class azure.ai.voiceagents.types.RealtimeResponseUsage(TypedDict, total=False):
        key "input_token_details": ForwardRef('RealtimeResponseUsageInputTokenDetails', module='types')
        key "input_tokens": int
        key "output_token_details": ForwardRef('RealtimeResponseUsageOutputTokenDetails', module='types')
        key "output_tokens": int
        key "total_tokens": int
        input_token_details: RealtimeResponseUsageInputTokenDetails
        input_tokens: int
        output_token_details: RealtimeResponseUsageOutputTokenDetails
        output_tokens: int
        total_tokens: int


    class azure.ai.voiceagents.types.RealtimeResponseUsageInputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "cached_tokens": int
        key "cached_tokens_details": ForwardRef('RealtimeResponseUsageInputTokenDetailsCachedTokensDetails', module='types')
        key "image_tokens": int
        key "text_tokens": int
        audio_tokens: int
        cached_tokens: int
        cached_tokens_details: RealtimeResponseUsageInputTokenDetailsCachedTokensDetails
        image_tokens: int
        text_tokens: int


    class azure.ai.voiceagents.types.RealtimeResponseUsageInputTokenDetailsCachedTokensDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "image_tokens": int
        key "text_tokens": int
        audio_tokens: int
        image_tokens: int
        text_tokens: int


    class azure.ai.voiceagents.types.RealtimeResponseUsageOutputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "text_tokens": int
        audio_tokens: int
        text_tokens: int


    class azure.ai.voiceagents.types.RealtimeServerEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[RealtimeServerEventResponseContentPartAddedPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]


    class azure.ai.voiceagents.types.RealtimeServerEventConversationItemInputAudioTranscriptionFailedError(TypedDict, total=False):
        key "code": str
        key "message": str
        key "param": str
        key "type": str
        code: str
        message: str
        param: str
        type: str


    class azure.ai.voiceagents.types.RealtimeServerEventRateLimitsUpdatedRateLimits(TypedDict, total=False):
        key "limit": int
        key "name": Literal["requests", "tokens"]
        key "remaining": int
        key "reset_seconds": float
        limit: int
        name: Literal[requests, tokens]
        remaining: int
        reset_seconds: float


    class azure.ai.voiceagents.types.RealtimeServerEventResponseContentPartAdded(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[RealtimeServerEventResponseContentPartAddedPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartAddedPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_ADDED]


    class azure.ai.voiceagents.types.RealtimeServerEventResponseContentPartAddedPart(TypedDict, total=False):
        key "audio": str
        key "text": str
        key "transcript": str
        key "type": Literal["audio", "text"]
        audio: str
        text: str
        transcript: str
        type: Literal[audio, text]


    class azure.ai.voiceagents.types.RealtimeServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION_CREATED = "conversation.created"
        CONVERSATION_ITEM_ADDED = "conversation.item.added"
        CONVERSATION_ITEM_CREATED = "conversation.item.created"
        CONVERSATION_ITEM_DELETED = "conversation.item.deleted"
        CONVERSATION_ITEM_DONE = "conversation.item.done"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = "conversation.item.input_audio_transcription.completed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA = "conversation.item.input_audio_transcription.delta"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = "conversation.item.input_audio_transcription.failed"
        CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT = "conversation.item.input_audio_transcription.segment"
        CONVERSATION_ITEM_RETRIEVED = "conversation.item.retrieved"
        CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
        ERROR = "error"
        INPUT_AUDIO_BUFFER_CLEARED = "input_audio_buffer.cleared"
        INPUT_AUDIO_BUFFER_COMMITTED = "input_audio_buffer.committed"
        INPUT_AUDIO_BUFFER_DTMF_EVENT_RECEIVED = "input_audio_buffer.dtmf_event_received"
        INPUT_AUDIO_BUFFER_SPEECH_STARTED = "input_audio_buffer.speech_started"
        INPUT_AUDIO_BUFFER_SPEECH_STOPPED = "input_audio_buffer.speech_stopped"
        INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED = "input_audio_buffer.timeout_triggered"
        MCP_LIST_TOOLS_COMPLETED = "mcp_list_tools.completed"
        MCP_LIST_TOOLS_FAILED = "mcp_list_tools.failed"
        MCP_LIST_TOOLS_IN_PROGRESS = "mcp_list_tools.in_progress"
        OUTPUT_AUDIO_BUFFER_CLEARED = "output_audio_buffer.cleared"
        OUTPUT_AUDIO_BUFFER_STARTED = "output_audio_buffer.started"
        OUTPUT_AUDIO_BUFFER_STOPPED = "output_audio_buffer.stopped"
        RATE_LIMITS_UPDATED = "rate_limits.updated"
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
        RESPONSE_OUTPUT_AUDIO_DELTA = "response.output_audio.delta"
        RESPONSE_OUTPUT_AUDIO_DONE = "response.output_audio.done"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA = "response.output_audio_transcript.delta"
        RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE = "response.output_audio_transcript.done"
        RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
        RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
        RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
        RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"
        SESSION_CREATED = "session.created"
        SESSION_UPDATED = "session.updated"


    class azure.ai.voiceagents.types.RealtimeToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.FUNCTION]]
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]


    class azure.ai.voiceagents.types.ResponsesProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.StructuredInputDefinition(TypedDict, total=False):
        key "default_value": Any
        key "description": str
        key "required": bool
        default_value: Any
        description: str
        required: bool
        schema: dict[str, Any]


    class azure.ai.voiceagents.types.TemplateVoiceGreetingConfig(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["template"]]
        text: str
        type: Literal[template]


    class azure.ai.voiceagents.types.Tool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "connector_id": Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]
        key "defer_loading": bool
        key "headers": Optional[dict[str, str]]
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "tunnel_id": str
        key "type": Required[Literal[ToolType.MCP]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        connector_id: Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams,
        defer_loading: bool
        headers: dict[str, str]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        tunnel_id: str
        type: Literal[ToolType.MCP]


    class azure.ai.voiceagents.types.ToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.FUNCTION]]
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]


    class azure.ai.voiceagents.types.ToolChoiceMCP(TypedDict, total=False):
        key "name": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[ToolChoiceParamType.MCP]]
        name: str
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]


    class azure.ai.voiceagents.types.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_TOOLS = "allowed_tools"
        APPLY_PATCH = "apply_patch"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE = "computer_use"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        MCP = "mcp"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHELL = "shell"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WEB_SEARCH_PREVIEW2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.voiceagents.types.ToolConfig(TypedDict, total=False):
        key "additional_search_text": str
        key "pin": bool
        additional_search_text: str
        pin: bool


    class azure.ai.voiceagents.types.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A_PREVIEW = "a2a_preview"
        APPLY_PATCH = "apply_patch"
        AZURE_AI_SEARCH = "azure_ai_search"
        AZURE_FUNCTION = "azure_function"
        BING_CUSTOM_SEARCH_PREVIEW = "bing_custom_search_preview"
        BING_GROUNDING = "bing_grounding"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CAPTURE_STRUCTURED_OUTPUTS = "capture_structured_outputs"
        CODE_INTERPRETER = "code_interpreter"
        COMPUTER = "computer"
        COMPUTER_USE_PREVIEW = "computer_use_preview"
        CUSTOM = "custom"
        FABRIC_DATAAGENT_PREVIEW = "fabric_dataagent_preview"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        FUNCTION = "function"
        IMAGE_GENERATION = "image_generation"
        LOCAL_SHELL = "local_shell"
        MCP = "mcp"
        MEMORY_SEARCH_PREVIEW = "memory_search_preview"
        NAMESPACE = "namespace"
        OPENAPI = "openapi"
        PROGRAMMATIC_TOOL_CALLING = "programmatic_tool_calling"
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.voiceagents.types.TranscriptTextUsageDuration(TypedDict, total=False):
        key "seconds": Required[str]
        key "type": Required[Literal[CreateTranscriptionResponseJsonUsageType.DURATION]]
        seconds: str
        type: Literal[CreateTranscriptionResponseJsonUsageType.DURATION]


    class azure.ai.voiceagents.types.TranscriptTextUsageTokens(TypedDict, total=False):
        key "input_token_details": ForwardRef('TranscriptTextUsageTokensInputTokenDetails', module='types')
        key "input_tokens": Required[int]
        key "output_tokens": Required[int]
        key "total_tokens": Required[int]
        key "type": Required[Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]]
        input_token_details: TranscriptTextUsageTokensInputTokenDetails
        input_tokens: int
        output_tokens: int
        total_tokens: int
        type: Literal[CreateTranscriptionResponseJsonUsageType.TOKENS]


    class azure.ai.voiceagents.types.TranscriptTextUsageTokensInputTokenDetails(TypedDict, total=False):
        key "audio_tokens": int
        key "text_tokens": int
        audio_tokens: int
        text_tokens: int


    class azure.ai.voiceagents.types.UpdateVoiceAgentRequest(TypedDict, total=False):
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "definition": Required[VoiceAgentDefinition]
        key "description": str
        blueprint_reference: AgentBlueprintReference
        definition: VoiceAgentDefinition
        description: str
        metadata: dict[str, str]


    class azure.ai.voiceagents.types.VersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[VersionSelectorType.FIXED_RATIO]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.voiceagents.types.VersionSelector(TypedDict, total=False):
        key "version_selection_rules": Required[list[VersionSelectionRule]]
        version_selection_rules: list[VersionSelectionRule]


    class azure.ai.voiceagents.types.VersionSelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.ai.voiceagents.types.VoiceAgentAnimationConfig(TypedDict, total=False):
        key "model_name": str
        model_name: str
        outputs: list[Union[str, VoiceAgentAnimationOutputType]]


    class azure.ai.voiceagents.types.VoiceAgentAvatarIceServer(TypedDict, total=False):
        key "credential": Optional[str]
        key "urls": Required[list[str]]
        key "username": Optional[str]
        credential: str
        urls: list[str]
        username: str


    class azure.ai.voiceagents.types.VoiceAgentAvatarScene(TypedDict, total=False):
        key "amplitude": float
        key "position_x": float
        key "position_y": float
        key "rotation_x": float
        key "rotation_y": float
        key "rotation_z": float
        key "zoom": float
        amplitude: float
        position_x: float
        position_y: float
        rotation_x: float
        rotation_y: float
        rotation_z: float
        zoom: float


    class azure.ai.voiceagents.types.VoiceAgentAvatarVideoBackground(TypedDict, total=False):
        key "color": Optional[str]
        key "image_url": Optional[str]
        color: str
        image_url: str


    class azure.ai.voiceagents.types.VoiceAgentAvatarVideoCrop(TypedDict, total=False):
        key "bottom_right": Required[list[int]]
        key "top_left": Required[list[int]]
        bottom_right: list[int]
        top_left: list[int]


    class azure.ai.voiceagents.types.VoiceAgentAvatarVideoParams(TypedDict, total=False):
        key "background": Optional[VoiceAgentAvatarVideoBackground]
        key "bitrate": int
        key "codec": Literal["h264"]
        key "crop": Optional[VoiceAgentAvatarVideoCrop]
        key "gop_size": int
        key "resolution": Optional[VoiceAgentAvatarVideoResolution]
        background: VoiceAgentAvatarVideoBackground
        bitrate: int
        codec: Literal[h264]
        crop: VoiceAgentAvatarVideoCrop
        gop_size: int
        resolution: VoiceAgentAvatarVideoResolution


    class azure.ai.voiceagents.types.VoiceAgentAvatarVideoResolution(TypedDict, total=False):
        key "height": Required[int]
        key "width": Required[int]
        height: int
        width: int


    class azure.ai.voiceagents.types.VoiceAgentAzureMultilingualSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceAgentEndOfUtteranceDetection]
        key "idle_timeout_ms": Optional[int]
        key "interrupt_response": bool
        key "languages": Optional[list[str]]
        key "prefix_padding_ms": Optional[int]
        key "remove_filler_words": bool
        key "silence_duration_ms": Optional[int]
        key "speech_duration_ms": Optional[int]
        key "threshold": Optional[float]
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceAgentEndOfUtteranceDetection
        idle_timeout_ms: int
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: int
        remove_filler_words: bool
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]


    class azure.ai.voiceagents.types.VoiceAgentAzureSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceAgentEndOfUtteranceDetection]
        key "idle_timeout_ms": Optional[int]
        key "interrupt_response": bool
        key "languages": Optional[list[str]]
        key "prefix_padding_ms": Optional[int]
        key "remove_filler_words": bool
        key "silence_duration_ms": Optional[int]
        key "speech_duration_ms": Optional[int]
        key "threshold": Optional[float]
        key "type": Required[Union[str, VoiceAgentAzureSemanticVadType]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceAgentEndOfUtteranceDetection
        idle_timeout_ms: int
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: int
        remove_filler_words: bool
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Union[str, VoiceAgentAzureSemanticVadType]


    class azure.ai.voiceagents.types.VoiceAgentClientEventConversationItemCreate(TypedDict, total=False):
        key "event_id": str
        key "item": Required[VoiceAgentCreateConversationItem]
        key "previous_item_id": str
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]]
        event_id: str
        item: VoiceAgentCreateConversationItem
        previous_item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]


    class azure.ai.voiceagents.types.VoiceAgentClientEventConversationItemDelete(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]]
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]


    class azure.ai.voiceagents.types.VoiceAgentClientEventConversationItemRetrieve(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]]
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]


    class azure.ai.voiceagents.types.VoiceAgentClientEventConversationItemTruncate(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": str
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]]
        audio_end_ms: int
        content_index: int
        event_id: str
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_TRUNCATE]


    class azure.ai.voiceagents.types.VoiceAgentClientEventInputAudioBufferAppend(TypedDict, total=False):
        key "audio": Required[str]
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]]
        audio: str
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]


    class azure.ai.voiceagents.types.VoiceAgentClientEventInputAudioBufferClear(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]]
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]


    class azure.ai.voiceagents.types.VoiceAgentClientEventInputAudioBufferCommit(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]]
        event_id: str
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]


    class azure.ai.voiceagents.types.VoiceAgentClientEventOutputAudioBufferClear(TypedDict, total=False):
        key "event_id": str
        key "type": Required[Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]]
        event_id: str
        type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]


    class azure.ai.voiceagents.types.VoiceAgentClientEventResponseCancel(TypedDict, total=False):
        key "event_id": str
        key "response_id": str
        key "type": Required[Literal[RealtimeClientEventType.RESPONSE_CANCEL]]
        event_id: str
        response_id: str
        type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]


    class azure.ai.voiceagents.types.VoiceAgentClientEventResponseCreate(TypedDict, total=False):
        key "event_id": str
        key "response": ForwardRef('VoiceAgentResponseCreateParams', module='types')
        key "type": Required[Literal[RealtimeClientEventType.RESPONSE_CREATE]]
        event_id: str
        response: VoiceAgentResponseCreateParams
        type: Literal[RealtimeClientEventType.RESPONSE_CREATE]


    class azure.ai.voiceagents.types.VoiceAgentClientEventSessionAvatarConnect(TypedDict, total=False):
        key "client_sdp": Required[str]
        key "event_id": str
        key "type": Required[Literal["connect"]]
        client_sdp: str
        event_id: str
        type: Literal[connect]


    class azure.ai.voiceagents.types.VoiceAgentClientEventSessionUpdate(TypedDict, total=False):
        key "event_id": str
        key "session": Required[VoiceAgentSessionUpdateConfig]
        key "type": Required[Literal[RealtimeClientEventType.SESSION_UPDATE]]
        event_id: str
        session: VoiceAgentSessionUpdateConfig
        type: Literal[RealtimeClientEventType.SESSION_UPDATE]


    class azure.ai.voiceagents.types.VoiceAgentDefinition(TypedDict, total=False):
        key "audio": ForwardRef('VoiceAudioConfig', module='types')
        key "avatar": ForwardRef('VoiceAvatarConfig', module='types')
        key "greeting": ForwardRef('VoiceGreetingConfig', module='types')
        key "instructions": str
        key "kind": Required[Literal["voice"]]
        key "model": Required[str]
        key "model_type": Required[Union[str, VoiceModelType]]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "store": bool
        audio: VoiceAudioConfig
        avatar: VoiceAvatarConfig
        greeting: VoiceGreetingConfig
        instructions: str
        kind: Literal[voice]
        model: str
        model_type: Union[str, VoiceModelType]
        output_modalities: list[Union[str, VoiceOutputModality]]
        rai_config: RaiConfig
        store: bool
        structured_inputs: dict[str, StructuredInputDefinition]
        tools: list[VoiceAgentTool]


    class azure.ai.voiceagents.types.VoiceAgentEchoCancellation(TypedDict, total=False):
        key "channels": int
        key "reference_source": Union[str, VoiceAgentEchoCancellationReferenceSource]
        key "type": Required[Literal["server_echo_cancellation"]]
        channels: int
        reference_source: Union[str, VoiceAgentEchoCancellationReferenceSource]
        type: Literal[server_echo_cancellation]


    class azure.ai.voiceagents.types.VoiceAgentEndOfUtteranceDetection(TypedDict, total=False):
        key "model": Required[Union[str, VoiceAgentEndOfUtteranceModel]]
        key "threshold": Optional[float]
        key "threshold_level": Optional[Union[str, VoiceAgentEndOfUtteranceThresholdLevel]]
        key "timeout": Optional[float]
        key "timeout_ms": Optional[int]
        model: Union[str, VoiceAgentEndOfUtteranceModel]
        threshold: float
        threshold_level: Union[str, VoiceAgentEndOfUtteranceThresholdLevel]
        timeout: float
        timeout_ms: int


    class azure.ai.voiceagents.types.VoiceAgentEstimatedCost(TypedDict, total=False):
        key "amount": Required[Optional[float]]
        key "byom_model_amount": Optional[float]
        key "byom_model_price_version": Optional[str]
        key "currency": Literal["USD"]
        key "input_cost": Optional[float]
        key "output_cost": Optional[float]
        key "price_version": Required[str]
        key "status": Required[Union[str, VoiceAgentEstimatedCostStatus]]
        key "voice_live_amount": Required[float]
        amount: float
        byom_model_amount: float
        byom_model_price_version: str
        currency: Literal[USD]
        input_cost: float
        output_cost: float
        price_version: str
        status: Union[str, VoiceAgentEstimatedCostStatus]
        unpriced_components: list[str]
        voice_live_amount: float


    class azure.ai.voiceagents.types.VoiceAgentFileSearchCallItem(TypedDict, total=False):
        key "id": Required[str]
        key "queries": Optional[list[str]]
        key "results": Optional[list[VoiceAgentFileSearchResult]]
        key "status": Required[Union[str, VoiceAgentFileSearchCallStatus]]
        key "type": Required[Literal["file_search_call"]]
        id: str
        queries: list[str]
        results: list[VoiceAgentFileSearchResult]
        status: Union[str, VoiceAgentFileSearchCallStatus]
        type: Literal[file_search_call]


    class azure.ai.voiceagents.types.VoiceAgentFileSearchResult(TypedDict, total=False):
        key "attributes": Optional[dict[str, VoiceAgentFileSearchAttributeValue]]
        key "file_id": Optional[str]
        key "filename": Optional[str]
        key "score": Optional[float]
        key "text": Optional[str]
        attributes: dict[str, VoiceAgentFileSearchAttributeValue]
        file_id: str
        filename: str
        score: float
        text: str


    class azure.ai.voiceagents.types.VoiceAgentHandoffEdgeConfig(TypedDict, total=False):
        key "cancel_on_interruption": bool
        key "delay_ms": int
        key "description": Required[str]
        key "id": Required[str]
        key "source": Required[str]
        key "target": Required[str]
        key "target_response": Union[str, VoiceAgentHandoffTargetResponse]
        key "transfer_message": Optional[str]
        cancel_on_interruption: bool
        delay_ms: int
        description: str
        id: str
        source: str
        target: str
        target_response: Union[str, VoiceAgentHandoffTargetResponse]
        transfer_message: str


    class azure.ai.voiceagents.types.VoiceAgentHandoffEdgeState(TypedDict, total=False):
        key "cancel_on_interruption": bool
        key "delay_ms": int
        key "id": Required[str]
        key "source": Required[str]
        key "target": Required[str]
        key "target_response": Union[str, VoiceAgentHandoffTargetResponse]
        key "transfer_message": Optional[str]
        cancel_on_interruption: bool
        delay_ms: int
        id: str
        source: str
        target: str
        target_response: Union[str, VoiceAgentHandoffTargetResponse]
        transfer_message: str


    class azure.ai.voiceagents.types.VoiceAgentHandoffGraphConfig(TypedDict, total=False):
        key "edges": Required[list[VoiceAgentHandoffEdgeConfig]]
        key "max_attempts": Optional[int]
        key "max_transfers": int
        key "nodes": Required[list[VoiceAgentHandoffNodeConfig]]
        edges: list[VoiceAgentHandoffEdgeConfig]
        max_attempts: int
        max_transfers: int
        nodes: list[VoiceAgentHandoffNodeConfig]


    class azure.ai.voiceagents.types.VoiceAgentHandoffNodeConfig(TypedDict, total=False):
        key "config": Required[VoiceAgentHandoffNodeSessionConfig]
        key "description": Required[str]
        key "id": Required[str]
        config: VoiceAgentHandoffNodeSessionConfig
        description: str
        id: str


    class azure.ai.voiceagents.types.VoiceAgentHandoffNodeSessionConfig(TypedDict, total=False):
        key "instructions": Optional[str]
        key "interim_response": Optional[VoiceAgentInterimResponse]
        key "max_response_output_tokens": Optional[VoiceAgentMaxOutputTokens]
        key "model": Optional[str]
        key "parallel_tool_calls": bool
        key "reasoning_effort": Optional[Union[str, VoiceAgentHandoffReasoningEffort]]
        key "temperature": Optional[float]
        key "tool_choice": Optional[VoiceAgentToolChoice]
        key "tools": Optional[list[VoiceAgentSessionTool]]
        key "voice": Optional[VoiceAgentVoice]
        key "voice_adaptation": Optional[VoiceAgentVoiceAdaptation]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_response_output_tokens: VoiceAgentMaxOutputTokens
        model: str
        parallel_tool_calls: bool
        reasoning_effort: Union[str, VoiceAgentHandoffReasoningEffort]
        temperature: float
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentSessionTool]
        voice: VoiceAgentVoice
        voice_adaptation: VoiceAgentVoiceAdaptation


    class azure.ai.voiceagents.types.VoiceAgentHandoffNodeState(TypedDict, total=False):
        key "description": Required[str]
        key "id": Required[str]
        key "implicit": bool
        description: str
        id: str
        implicit: bool


    class azure.ai.voiceagents.types.VoiceAgentHandoffState(TypedDict, total=False):
        key "active_node_id": Required[str]
        key "attempt_count": Required[int]
        key "available_edge_ids": Required[list[str]]
        key "edges": Required[list[VoiceAgentHandoffEdgeState]]
        key "node_generation": Required[int]
        key "nodes": Required[list[VoiceAgentHandoffNodeState]]
        key "pipeline_family": Required[Union[str, VoiceAgentPipelineFamily]]
        key "transfer_count": Required[int]
        key "transfer_tool": Required[Optional[RealtimeFunctionTool]]
        active_node_id: str
        attempt_count: int
        available_edge_ids: list[str]
        edges: list[VoiceAgentHandoffEdgeState]
        node_generation: int
        nodes: list[VoiceAgentHandoffNodeState]
        pipeline_family: Union[str, VoiceAgentPipelineFamily]
        transfer_count: int
        transfer_tool: RealtimeFunctionTool


    class azure.ai.voiceagents.types.VoiceAgentLlmInterimResponseConfig(TypedDict, total=False):
        key "instructions": str
        key "latency_threshold_ms": int
        key "max_completion_tokens": int
        key "model": str
        key "type": Required[Literal["llm_interim_response"]]
        instructions: str
        latency_threshold_ms: int
        max_completion_tokens: int
        model: str
        triggers: list[Union[str, VoiceAgentInterimResponseTrigger]]
        type: Literal[llm_interim_response]


    class azure.ai.voiceagents.types.VoiceAgentMcpAssignedManagedIdentity(TypedDict, total=False):
        key "audience": Required[str]
        key "client_id": str
        key "type": Required[Literal["assigned_managed_identity"]]
        audience: str
        client_id: str
        type: Literal[assigned_managed_identity]


    class azure.ai.voiceagents.types.VoiceAgentMcpTool(TypedDict, total=False):
        key "allowed_callers": Optional[list[Union[str, CallableToolAllowedCaller]]]
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "defer_loading": bool
        key "headers": Optional[dict[str, str]]
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "response_scheduling": Union[str, VoiceAgentMcpResponseScheduling]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "type": Required[Literal[ToolType.MCP]]
        allowed_callers: list[Union[str, CallableToolAllowedCaller]]
        allowed_tools: Union[list[str], MCPToolFilter]
        defer_loading: bool
        headers: dict[str, str]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        response_scheduling: Union[str, VoiceAgentMcpResponseScheduling]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.MCP]


    class azure.ai.voiceagents.types.VoiceAgentRealtimeResponse(TypedDict, total=False):
        key "conversation_id": Optional[str]
        key "estimated_cost": ForwardRef('VoiceAgentEstimatedCost', module='types')
        key "id": Required[str]
        key "max_output_tokens": Optional[VoiceAgentMaxOutputTokens]
        key "metadata": Optional[dict[str, str]]
        key "modalities": Optional[list[Union[str, VoiceOutputModality]]]
        key "object": Required[Literal["response"]]
        key "output": Required[list[VoiceAgentResponseItem]]
        key "output_audio_format": Optional[Union[str, VoiceAgentResponseAudioFormat]]
        key "status": Required[Union[str, VoiceAgentResponseStatus]]
        key "status_details": Required[Optional[RealtimeResponseStatusDetails]]
        key "temperature": Optional[float]
        key "usage": Required[Optional[RealtimeResponseUsage]]
        key "voice": Optional[VoiceAgentVoice]
        conversation_id: str
        estimated_cost: VoiceAgentEstimatedCost
        id: str
        max_output_tokens: VoiceAgentMaxOutputTokens
        metadata: dict[str, str]
        modalities: list[Union[str, VoiceOutputModality]]
        object: Literal[response]
        output: list[VoiceAgentResponseItem]
        output_audio_format: Union[str, VoiceAgentResponseAudioFormat]
        status: Union[str, VoiceAgentResponseStatus]
        status_details: RealtimeResponseStatusDetails
        temperature: float
        usage: RealtimeResponseUsage
        voice: VoiceAgentVoice


    class azure.ai.voiceagents.types.VoiceAgentResponseCreateAudio(TypedDict, total=False):
        key "output": Optional[VoiceAgentSessionUpdateAudioOutput]
        output: VoiceAgentSessionUpdateAudioOutput


    class azure.ai.voiceagents.types.VoiceAgentResponseCreateParams(TypedDict, total=False):
        key "audio": ForwardRef('VoiceAgentResponseCreateAudio', module='types')
        key "conversation": Union[Literal["auto"], Literal["none"], str]
        key "instructions": str
        key "interim_response": Optional[VoiceAgentInterimResponse]
        key "max_output_tokens": Union[int, Literal["inf"]]
        key "metadata": Optional[Metadata]
        key "parallel_tool_calls": bool
        key "pre_generated_assistant_message": Optional[RealtimeConversationItemMessageAssistant]
        key "reasoning": ForwardRef('RealtimeReasoning', module='types')
        key "tool_choice": Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]
        audio: VoiceAgentResponseCreateAudio
        conversation: Union[Literal[auto], Literal[none], str]
        input: list[RealtimeConversationItem]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: Union[int, Literal[inf]]
        metadata: Metadata
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        pre_generated_assistant_message: RealtimeConversationItemMessageAssistant
        reasoning: RealtimeReasoning
        tool_choice: Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]
        tools: list[Union[RealtimeFunctionTool, MCPTool]]


    class azure.ai.voiceagents.types.VoiceAgentResponseEventAudioContentPart(TypedDict, total=False):
        key "annotations": Any
        key "audio": str
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "transcript": Required[Optional[str]]
        key "type": Required[Literal["audio"]]
        annotations: Any
        audio: str
        format: VoiceAudioFormat
        transcript: str
        type: Literal[audio]


    class azure.ai.voiceagents.types.VoiceAgentResponseEventTextContentPart(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["text"]]
        text: str
        type: Literal[text]


    class azure.ai.voiceagents.types.VoiceAgentSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "eagerness": Literal["low", "medium", "high", "auto"]
        key "interrupt_response": bool
        key "type": Required[Literal[VoiceTurnDetectionType.SEMANTIC_VAD]]
        auto_truncate: bool
        create_response: bool
        eagerness: Literal[low, medium, high, auto]
        interrupt_response: bool
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationCreated(TypedDict, total=False):
        key "conversation_id": Required[str]
        key "type": Required[Literal["created"]]
        conversation_id: str
        type: Literal[created]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemAdded(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemDeleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]]
        event_id: str
        item: VoiceAgentResponseItem
        previous_item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionCompleted(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "logprobs": Optional[list[LogProbProperties]]
        key "phrases": Optional[list[VoiceAgentTranscriptionPhrase]]
        key "transcript": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]]
        key "usage": Required[Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]]
        content_index: int
        event_id: str
        item_id: str
        logprobs: list[LogProbProperties]
        phrases: list[VoiceAgentTranscriptionPhrase]
        transcript: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED]
        usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionDelta(TypedDict, total=False):
        key "content_index": int
        key "delta": str
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "logprobs": Optional[list[LogProbProperties]]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        logprobs: list[LogProbProperties]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionFailed(TypedDict, total=False):
        key "content_index": Required[int]
        key "error": Required[RealtimeServerEventConversationItemInputAudioTranscriptionFailedError]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]]
        content_index: int
        error: RealtimeServerEventConversationItemInputAudioTranscriptionFailedError
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemInputAudioTranscriptionSegment(TypedDict, total=False):
        key "content_index": Required[int]
        key "end": Required[float]
        key "event_id": Required[str]
        key "id": Required[str]
        key "item_id": Required[str]
        key "speaker": Required[str]
        key "start": Required[float]
        key "text": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]]
        content_index: int
        end: float
        event_id: str
        id: str
        item_id: str
        speaker: str
        start: float
        text: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_SEGMENT]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemRetrieved(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]]
        event_id: str
        item: VoiceAgentResponseItem
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventConversationItemTruncated(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item": ForwardRef('RealtimeConversationItemMessageAssistant', module='types')
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]]
        audio_end_ms: int
        content_index: int
        event_id: str
        item: RealtimeConversationItemMessageAssistant
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventError(TypedDict, total=False):
        key "error": Required[VoiceAgentServerEventErrorDetails]
        key "event_id": Required[str]
        key "type": Required[Literal["error"]]
        error: VoiceAgentServerEventErrorDetails
        event_id: str
        type: Literal[error]


    class azure.ai.voiceagents.types.VoiceAgentServerEventErrorDetails(TypedDict, total=False):
        key "code": Optional[str]
        key "event_id": Optional[str]
        key "message": Required[str]
        key "param": Optional[str]
        key "tool_label": str
        key "tool_type": str
        key "type": Required[str]
        code: str
        event_id: str
        message: str
        param: str
        tool_label: str
        tool_type: str
        type: str


    class azure.ai.voiceagents.types.VoiceAgentServerEventFileSearchCallCompleted(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[completed]


    class azure.ai.voiceagents.types.VoiceAgentServerEventFileSearchCallInProgress(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.voiceagents.types.VoiceAgentServerEventFileSearchCallSearching(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["searching"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[searching]


    class azure.ai.voiceagents.types.VoiceAgentServerEventInputAudioBufferCleared(TypedDict, total=False):
        key "event_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]]
        event_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventInputAudioBufferCommitted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "previous_item_id": Optional[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]]
        event_id: str
        item_id: str
        previous_item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_COMMITTED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventInputAudioBufferSpeechStarted(TypedDict, total=False):
        key "audio_start_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]]
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventInputAudioBufferSpeechStopped(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]]
        audio_end_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_SPEECH_STOPPED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventInputAudioBufferTimeoutTriggered(TypedDict, total=False):
        key "audio_end_ms": Required[int]
        key "audio_start_ms": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]]
        audio_end_ms: int
        audio_start_ms: int
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_TIMEOUT_TRIGGERED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventMcpListToolsCompleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventMcpListToolsFailed(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventMcpListToolsInProgress(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]]
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]


    class azure.ai.voiceagents.types.VoiceAgentServerEventOutputAudioBufferCleared(TypedDict, total=False):
        key "event_id": Required[str]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]]
        event_id: str
        response_id: str
        type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventRateLimitsUpdated(TypedDict, total=False):
        key "event_id": Required[str]
        key "rate_limits": Required[list[RealtimeServerEventRateLimitsUpdatedRateLimits]]
        key "type": Required[Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]]
        event_id: str
        rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
        type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAnimationBlendshapesDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "frame_index": Required[int]
        key "frames": Required[Union[list[list[float]], str]]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["delta"]]
        content_index: int
        event_id: str
        frame_index: int
        frames: Union[list[list[float]], str]
        item_id: str
        output_index: int
        response_id: str
        type: Literal[delta]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAnimationBlendshapesDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAnimationVisemeDelta(TypedDict, total=False):
        key "audio_offset_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["delta"]]
        key "viseme_id": Required[int]
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[delta]
        viseme_id: int


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAnimationVisemeDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioTimestampDelta(TypedDict, total=False):
        key "audio_duration_ms": Required[int]
        key "audio_offset_ms": Required[int]
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "text": Required[str]
        key "timestamp_type": Required[Literal["word"]]
        key "type": Required[Literal["delta"]]
        audio_duration_ms: int
        audio_offset_ms: int
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal[word]
        type: Literal[delta]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioTimestampDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal["done"]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[done]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioTranscriptDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseAudioTranscriptDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "transcript": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        transcript: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_AUDIO_TRANSCRIPT_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseContentPartDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[VoiceAgentResponseEventContentPart]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: VoiceAgentResponseEventContentPart
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_CONTENT_PART_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "response": Required[VoiceAgentRealtimeResponse]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_CREATED]]
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_CREATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "response": Required[VoiceAgentRealtimeResponse]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_DONE]]
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseFunctionCallArgumentsDelta(TypedDict, total=False):
        key "call_id": Required[str]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]]
        call_id: str
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseFunctionCallArgumentsDone(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "name": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]]
        arguments: str
        call_id: str
        event_id: str
        item_id: str
        name: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseMcpCallArgumentsDelta(TypedDict, total=False):
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "obfuscation": Optional[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]]
        delta: str
        event_id: str
        item_id: str
        obfuscation: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseMcpCallArgumentsDone(TypedDict, total=False):
        key "arguments": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]]
        arguments: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseMcpCallCompleted(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_COMPLETED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseMcpCallFailed(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_FAILED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseMcpCallInProgress(TypedDict, total=False):
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]]
        event_id: str
        item_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_MCP_CALL_IN_PROGRESS]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseOutputItemAdded(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]]
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseOutputItemDone(TypedDict, total=False):
        key "event_id": Required[str]
        key "item": Required[VoiceAgentResponseItem]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]]
        event_id: str
        item: VoiceAgentResponseItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseTextDelta(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]]
        content_index: int
        delta: str
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DELTA]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseTextDone(TypedDict, total=False):
        key "content_index": Required[int]
        key "event_id": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": Required[str]
        key "text": Required[str]
        key "type": Required[Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]]
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_TEXT_DONE]


    class azure.ai.voiceagents.types.VoiceAgentServerEventResponseVideoDelta(TypedDict, total=False):
        key "codec": Required[str]
        key "delta": Required[str]
        key "event_id": Required[str]
        key "output_index": Required[int]
        key "type": Required[Literal["delta"]]
        codec: str
        delta: str
        event_id: str
        output_index: int
        type: Literal[delta]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionAvatarConnecting(TypedDict, total=False):
        key "event_id": Required[str]
        key "server_sdp": Required[str]
        key "type": Required[Literal["connecting"]]
        event_id: str
        server_sdp: str
        type: Literal[connecting]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionAvatarSwitchToIdle(TypedDict, total=False):
        key "event_id": Required[str]
        key "turn_id": str
        key "type": Required[Literal["switch_to_idle"]]
        event_id: str
        turn_id: str
        type: Literal[switch_to_idle]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionAvatarSwitchToSpeaking(TypedDict, total=False):
        key "event_id": Required[str]
        key "turn_id": str
        key "type": Required[Literal["switch_to_speaking"]]
        event_id: str
        turn_id: str
        type: Literal[switch_to_speaking]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionCreated(TypedDict, total=False):
        key "event_id": Required[str]
        key "session": Required[VoiceAgentSessionResponseConfig]
        key "type": Required[Literal[RealtimeServerEventType.SESSION_CREATED]]
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_CREATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionHandoffAborted(TypedDict, total=False):
        key "edge_id": Required[str]
        key "error": ForwardRef('VoiceAgentServerEventErrorDetails', module='types')
        key "event_id": Required[str]
        key "from_model": Required[str]
        key "from_node_id": Required[str]
        key "handoff_id": Required[str]
        key "node_generation": Required[int]
        key "reason": Required[Union[str, VoiceAgentHandoffAbortReason]]
        key "to_model": Required[str]
        key "to_node_id": Required[str]
        key "tool_call_id": Required[str]
        key "type": Required[Literal["aborted"]]
        edge_id: str
        error: VoiceAgentServerEventErrorDetails
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        reason: Union[str, VoiceAgentHandoffAbortReason]
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal[aborted]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionHandoffCompleted(TypedDict, total=False):
        key "duration_ms": Required[int]
        key "edge_id": Required[str]
        key "event_id": Required[str]
        key "from_model": Required[str]
        key "from_node_id": Required[str]
        key "handoff_id": Required[str]
        key "node_generation": Required[int]
        key "prepare_duration_ms": Required[int]
        key "to_model": Required[str]
        key "to_node_id": Required[str]
        key "tool_call_id": Required[str]
        key "type": Required[Literal["completed"]]
        duration_ms: int
        edge_id: str
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        prepare_duration_ms: int
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal[completed]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionHandoffStarted(TypedDict, total=False):
        key "edge_id": Required[str]
        key "event_id": Required[str]
        key "from_model": Required[str]
        key "from_node_id": Required[str]
        key "handoff_id": Required[str]
        key "node_generation": Required[int]
        key "to_model": Required[str]
        key "to_node_id": Required[str]
        key "tool_call_id": Required[str]
        key "type": Required[Literal["started"]]
        edge_id: str
        event_id: str
        from_model: str
        from_node_id: str
        handoff_id: str
        node_generation: int
        to_model: str
        to_node_id: str
        tool_call_id: str
        type: Literal[started]


    class azure.ai.voiceagents.types.VoiceAgentServerEventSessionUpdated(TypedDict, total=False):
        key "event_id": Required[str]
        key "session": Required[VoiceAgentSessionResponseConfig]
        key "type": Required[Literal[RealtimeServerEventType.SESSION_UPDATED]]
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_UPDATED]


    class azure.ai.voiceagents.types.VoiceAgentServerEventWarning(TypedDict, total=False):
        key "event_id": Required[str]
        key "type": Required[Literal["warning"]]
        key "warning": Required[VoiceAgentServerEventWarningDetails]
        event_id: str
        type: Literal[warning]
        warning: VoiceAgentServerEventWarningDetails


    class azure.ai.voiceagents.types.VoiceAgentServerEventWarningDetails(TypedDict, total=False):
        key "code": str
        key "message": Required[str]
        key "param": str
        code: str
        message: str
        param: str


    class azure.ai.voiceagents.types.VoiceAgentServerEventWebSearchCallCompleted(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["completed"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[completed]


    class azure.ai.voiceagents.types.VoiceAgentServerEventWebSearchCallInProgress(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["in_progress"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[in_progress]


    class azure.ai.voiceagents.types.VoiceAgentServerEventWebSearchCallSearching(TypedDict, total=False):
        key "event_id": str
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "response_id": str
        key "sequence_number": Required[int]
        key "type": Required[Literal["searching"]]
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        sequence_number: int
        type: Literal[searching]


    class azure.ai.voiceagents.types.VoiceAgentServerVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": Optional[VoiceAgentEndOfUtteranceDetection]
        key "idle_timeout_ms": Optional[int]
        key "interrupt_response": bool
        key "prefix_padding_ms": Optional[int]
        key "silence_duration_ms": Optional[int]
        key "speech_duration_ms": Optional[int]
        key "threshold": Optional[float]
        key "type": Required[Literal[VoiceTurnDetectionType.SERVER_VAD]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceAgentEndOfUtteranceDetection
        idle_timeout_ms: int
        interrupt_response: bool
        prefix_padding_ms: int
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]


    class azure.ai.voiceagents.types.VoiceAgentSessionAvatarConfig(TypedDict, total=False):
        key "character": Required[str]
        key "customized": bool
        key "ice_servers": Optional[list[VoiceAgentAvatarIceServer]]
        key "model": Optional[str]
        key "output_audit_audio": bool
        key "output_protocol": Union[str, VoiceAgentAvatarOutputProtocol]
        key "scene": Optional[VoiceAgentAvatarScene]
        key "style": Optional[str]
        key "type": Union[str, VoiceAgentAvatarType]
        key "video": Optional[VoiceAgentAvatarVideoParams]
        character: str
        customized: bool
        ice_servers: list[VoiceAgentAvatarIceServer]
        model: str
        output_audit_audio: bool
        output_protocol: Union[str, VoiceAgentAvatarOutputProtocol]
        scene: VoiceAgentAvatarScene
        style: str
        type: Union[str, VoiceAgentAvatarType]
        video: VoiceAgentAvatarVideoParams


    class azure.ai.voiceagents.types.VoiceAgentSessionMcpTool(TypedDict, total=False):
        key "authorization": Optional[Union[str, VoiceAgentMcpAssignedManagedIdentity]]
        key "require_approval": ForwardRef('VoiceAgentMcpApprovalPolicy', module='types')
        key "response_scheduling": Union[str, VoiceAgentMcpResponseScheduling]
        key "server_label": Required[str]
        key "server_url": Required[str]
        key "type": Required[Literal["mcp"]]
        allowed_tools: list[str]
        authorization: Union[str, VoiceAgentMcpAssignedManagedIdentity]
        headers: dict[str, str]
        require_approval: VoiceAgentMcpApprovalPolicy
        response_scheduling: Union[str, VoiceAgentMcpResponseScheduling]
        server_label: str
        server_url: str
        type: Literal[mcp]


    class azure.ai.voiceagents.types.VoiceAgentSessionResponseAudio(TypedDict, total=False):
        key "input": Optional[VoiceAgentSessionResponseAudioInput]
        key "output": Optional[VoiceAgentSessionResponseAudioOutput]
        input: VoiceAgentSessionResponseAudioInput
        output: VoiceAgentSessionResponseAudioOutput


    class azure.ai.voiceagents.types.VoiceAgentSessionResponseAudioInput(TypedDict, total=False):
        key "echo_cancellation": Optional[VoiceAgentEchoCancellation]
        key "format": Optional[VoiceAudioFormat]
        key "noise_reduction": Optional[VoiceNoiseReduction]
        key "transcription": Optional[VoiceInputTranscription]
        key "turn_detection": Optional[VoiceAgentTurnDetection]
        echo_cancellation: VoiceAgentEchoCancellation
        format: VoiceAudioFormat
        noise_reduction: VoiceNoiseReduction
        transcription: VoiceInputTranscription
        turn_detection: VoiceAgentTurnDetection


    class azure.ai.voiceagents.types.VoiceAgentSessionResponseAudioOutput(TypedDict, total=False):
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "speed": Optional[float]
        key "voice": ForwardRef('VoiceAgentVoice', module='types')
        format: VoiceAudioFormat
        output_audio_timestamp_types: list[Union[str, VoiceAudioTimestampType]]
        speed: float
        voice: VoiceAgentVoice


    class azure.ai.voiceagents.types.VoiceAgentSessionResponseConfig(TypedDict, total=False):
        key "animation": Optional[VoiceAgentAnimationConfig]
        key "audio": Optional[VoiceAgentSessionResponseAudio]
        key "avatar": Optional[VoiceAgentSessionAvatarConfig]
        key "expires_at": Optional[int]
        key "greeting": Optional[VoiceGreetingConfig]
        key "handoff": Optional[VoiceAgentHandoffState]
        key "id": Required[str]
        key "idle_timeout": Optional[int]
        key "instructions": Optional[str]
        key "interim_response": Optional[VoiceAgentInterimResponse]
        key "max_output_tokens": Optional[VoiceAgentMaxOutputTokens]
        key "model": Required[str]
        key "object": Required[Literal["session"]]
        key "output_modalities": Required[list[Union[str, VoiceOutputModality]]]
        key "parallel_tool_calls": bool
        key "reasoning": Optional[RealtimeReasoning]
        key "response_delimiter": str
        key "temperature": Optional[float]
        key "tool_choice": Optional[VoiceAgentToolChoice]
        key "tools": Optional[list[VoiceAgentSessionTool]]
        key "type": Required[Literal["realtime"]]
        key "voice_adaptation": Optional[VoiceAgentVoiceAdaptation]
        animation: VoiceAgentAnimationConfig
        audio: VoiceAgentSessionResponseAudio
        avatar: VoiceAgentSessionAvatarConfig
        expires_at: int
        greeting: VoiceGreetingConfig
        handoff: VoiceAgentHandoffState
        id: str
        idle_timeout: int
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: VoiceAgentMaxOutputTokens
        model: str
        object: Literal[session]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        reasoning: RealtimeReasoning
        response_delimiter: str
        temperature: float
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentSessionTool]
        type: Literal[realtime]
        voice_adaptation: VoiceAgentVoiceAdaptation


    class azure.ai.voiceagents.types.VoiceAgentSessionUpdateAudio(TypedDict, total=False):
        key "input": Optional[VoiceAgentSessionUpdateAudioInput]
        key "output": Optional[VoiceAgentSessionUpdateAudioOutput]
        input: VoiceAgentSessionUpdateAudioInput
        output: VoiceAgentSessionUpdateAudioOutput


    class azure.ai.voiceagents.types.VoiceAgentSessionUpdateAudioInput(TypedDict, total=False):
        key "echo_cancellation": Optional[VoiceAgentEchoCancellation]
        key "format": Optional[VoiceAudioFormat]
        key "noise_reduction": Optional[VoiceNoiseReduction]
        key "transcription": Optional[VoiceInputTranscription]
        key "turn_detection": Optional[VoiceAgentTurnDetection]
        echo_cancellation: VoiceAgentEchoCancellation
        format: VoiceAudioFormat
        noise_reduction: VoiceNoiseReduction
        transcription: VoiceInputTranscription
        turn_detection: VoiceAgentTurnDetection


    class azure.ai.voiceagents.types.VoiceAgentSessionUpdateAudioOutput(TypedDict, total=False):
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "speed": Optional[float]
        key "voice": ForwardRef('VoiceAgentVoice', module='types')
        format: VoiceAudioFormat
        output_audio_timestamp_types: list[Union[str, VoiceAudioTimestampType]]
        speed: float
        voice: VoiceAgentVoice


    class azure.ai.voiceagents.types.VoiceAgentSessionUpdateConfig(TypedDict, total=False):
        key "animation": Optional[VoiceAgentAnimationConfig]
        key "audio": Optional[VoiceAgentSessionUpdateAudio]
        key "avatar": Optional[VoiceAgentSessionAvatarConfig]
        key "greeting": Optional[VoiceGreetingConfig]
        key "handoff": Optional[VoiceAgentHandoffGraphConfig]
        key "include": Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        key "instructions": Optional[str]
        key "interim_response": Optional[VoiceAgentInterimResponse]
        key "max_output_tokens": Optional[VoiceAgentMaxOutputTokens]
        key "metadata": Optional[dict[str, str]]
        key "output_modalities": Optional[list[Union[str, VoiceOutputModality]]]
        key "parallel_tool_calls": bool
        key "reasoning": Optional[RealtimeReasoning]
        key "response_delimiter": str
        key "temperature": Optional[float]
        key "tool_choice": Optional[VoiceAgentToolChoice]
        key "tools": Optional[list[VoiceAgentSessionTool]]
        key "type": Required[Literal["realtime"]]
        key "voice_adaptation": Optional[VoiceAgentVoiceAdaptation]
        animation: VoiceAgentAnimationConfig
        audio: VoiceAgentSessionUpdateAudio
        avatar: VoiceAgentSessionAvatarConfig
        greeting: VoiceGreetingConfig
        handoff: VoiceAgentHandoffGraphConfig
        include: list[Union[str, VoiceAgentSessionIncludeOption]]
        instructions: str
        interim_response: VoiceAgentInterimResponse
        max_output_tokens: VoiceAgentMaxOutputTokens
        metadata: dict[str, str]
        output_modalities: list[Union[str, VoiceOutputModality]]
        parallel_tool_calls: bool
        reasoning: RealtimeReasoning
        response_delimiter: str
        temperature: float
        tool_choice: VoiceAgentToolChoice
        tools: list[VoiceAgentSessionTool]
        type: Literal[realtime]
        voice_adaptation: VoiceAgentVoiceAdaptation


    class azure.ai.voiceagents.types.VoiceAgentStaticInterimResponseConfig(TypedDict, total=False):
        key "latency_threshold_ms": int
        key "type": Required[Literal["static_interim_response"]]
        latency_threshold_ms: int
        texts: list[str]
        triggers: list[Union[str, VoiceAgentInterimResponseTrigger]]
        type: Literal[static_interim_response]


    class azure.ai.voiceagents.types.VoiceAgentTranscriptionPhrase(TypedDict, total=False):
        key "confidence": Optional[float]
        key "duration_milliseconds": Required[int]
        key "locale": Optional[str]
        key "offset_milliseconds": Required[int]
        key "text": Required[str]
        key "words": Optional[list[VoiceAgentTranscriptionWord]]
        confidence: float
        duration_milliseconds: int
        locale: str
        offset_milliseconds: int
        text: str
        words: list[VoiceAgentTranscriptionWord]


    class azure.ai.voiceagents.types.VoiceAgentTranscriptionWord(TypedDict, total=False):
        key "duration_milliseconds": Required[int]
        key "offset_milliseconds": Required[int]
        key "text": Required[str]
        duration_milliseconds: int
        offset_milliseconds: int
        text: str


    class azure.ai.voiceagents.types.VoiceAgentVoiceAdaptation(TypedDict, total=False):
        key "type": Required[Literal["auto"]]
        type: Literal[auto]


    class azure.ai.voiceagents.types.VoiceAgentWebSearchActionFind(TypedDict, total=False):
        key "pattern": Required[str]
        key "type": Required[Literal["find"]]
        key "url": Required[str]
        pattern: str
        type: Literal[find]
        url: str


    class azure.ai.voiceagents.types.VoiceAgentWebSearchActionOpenPage(TypedDict, total=False):
        key "type": Required[Literal["open_page"]]
        key "url": Required[str]
        type: Literal[open_page]
        url: str


    class azure.ai.voiceagents.types.VoiceAgentWebSearchActionSearch(TypedDict, total=False):
        key "query": Required[Optional[str]]
        key "sources": Optional[list[VoiceAgentWebSearchSource]]
        key "type": Required[Literal["search"]]
        query: str
        sources: list[VoiceAgentWebSearchSource]
        type: Literal[search]


    class azure.ai.voiceagents.types.VoiceAgentWebSearchCallItem(TypedDict, total=False):
        key "action": Optional[VoiceAgentWebSearchAction]
        key "id": Required[str]
        key "status": Required[Union[str, VoiceAgentWebSearchCallStatus]]
        key "type": Required[Literal["web_search_call"]]
        action: VoiceAgentWebSearchAction
        id: str
        status: Union[str, VoiceAgentWebSearchCallStatus]
        type: Literal[web_search_call]


    class azure.ai.voiceagents.types.VoiceAgentWebSearchSource(TypedDict, total=False):
        key "type": Required[Literal["url"]]
        key "url": Required[str]
        type: Literal[url]
        url: str


    class azure.ai.voiceagents.types.VoiceAgentWorkflowActionItem(TypedDict, total=False):
        key "action_id": Required[str]
        key "id": Required[Optional[str]]
        key "kind": Optional[str]
        key "object": Literal["item"]
        key "parent_action_id": Optional[str]
        key "previous_action_id": Optional[str]
        key "status": Required[str]
        key "type": Required[Literal["workflow_action"]]
        action_id: str
        id: str
        kind: str
        object: Literal[item]
        parent_action_id: str
        previous_action_id: str
        status: str
        type: Literal[workflow_action]


    class azure.ai.voiceagents.types.VoiceAssistantMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageAssistantContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.ASSISTANT]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


    class azure.ai.voiceagents.types.VoiceAudioConfig(TypedDict, total=False):
        key "input": ForwardRef('VoiceAudioInputConfig', module='types')
        key "output": ForwardRef('VoiceAudioOutputConfig', module='types')
        input: VoiceAudioInputConfig
        output: VoiceAudioOutputConfig


    class azure.ai.voiceagents.types.VoiceAudioFormat(TypedDict, total=False):
        key "rate": int
        key "type": Required[Union[str, VoiceAudioFormatType]]
        rate: int
        type: Union[str, VoiceAudioFormatType]


    class azure.ai.voiceagents.types.VoiceAudioInputConfig(TypedDict, total=False):
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "noise_reduction": Optional[VoiceNoiseReduction]
        key "transcription": Optional[VoiceInputTranscription]
        key "turn_detection": Optional[VoiceTurnDetection]
        format: VoiceAudioFormat
        noise_reduction: VoiceNoiseReduction
        transcription: VoiceInputTranscription
        turn_detection: VoiceTurnDetection


    class azure.ai.voiceagents.types.VoiceAudioOutputConfig(TypedDict, total=False):
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "speed": float
        key "voice": ForwardRef('VoiceAgentVoice', module='types')
        format: VoiceAudioFormat
        output_audio_timestamp_types: list[Union[str, VoiceAudioTimestampType]]
        speed: float
        voice: VoiceAgentVoice


    class azure.ai.voiceagents.types.VoiceAvatarConfig(TypedDict, total=False):
        key "character": Required[str]
        key "customized": bool
        key "output_protocol": Union[str, VoiceAvatarOutputProtocol]
        key "style": str
        key "type": Required[Union[str, VoiceAvatarType]]
        character: str
        customized: bool
        output_protocol: Union[str, VoiceAvatarOutputProtocol]
        style: str
        type: Union[str, VoiceAvatarType]


    class azure.ai.voiceagents.types.VoiceAzureSemanticDetection(TypedDict, total=False):
        key "model": Required[Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1]]
        key "threshold_level": Union[str, VoiceEndOfUtteranceThresholdLevel]
        key "timeout_ms": int
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1]
        threshold_level: Union[str, VoiceEndOfUtteranceThresholdLevel]
        timeout_ms: int


    class azure.ai.voiceagents.types.VoiceAzureSemanticDetectionEn(TypedDict, total=False):
        key "model": Required[Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_EN]]
        key "threshold_level": Union[str, VoiceEndOfUtteranceThresholdLevel]
        key "timeout_ms": int
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_EN]
        threshold_level: Union[str, VoiceEndOfUtteranceThresholdLevel]
        timeout_ms: int


    class azure.ai.voiceagents.types.VoiceAzureSemanticDetectionMultilingual(TypedDict, total=False):
        key "model": Required[Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_MULTILINGUAL]]
        key "threshold_level": Union[str, VoiceEndOfUtteranceThresholdLevel]
        key "timeout_ms": int
        model: Literal[VoiceEndOfUtteranceDetectionModel.SEMANTIC_DETECTION_V1_MULTILINGUAL]
        threshold_level: Union[str, VoiceEndOfUtteranceThresholdLevel]
        timeout_ms: int


    class azure.ai.voiceagents.types.VoiceAzureSemanticVadEnTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": ForwardRef('VoiceEndOfUtteranceDetection', module='types')
        key "interrupt_response": bool
        key "prefix_padding_ms": int
        key "remove_filler_words": bool
        key "silence_duration_ms": int
        key "speech_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        interrupt_response: bool
        prefix_padding_ms: int
        remove_filler_words: bool
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_EN]


    class azure.ai.voiceagents.types.VoiceAzureSemanticVadMultilingualTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": ForwardRef('VoiceEndOfUtteranceDetection', module='types')
        key "interrupt_response": bool
        key "prefix_padding_ms": int
        key "remove_filler_words": bool
        key "silence_duration_ms": int
        key "speech_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: int
        remove_filler_words: bool
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]


    class azure.ai.voiceagents.types.VoiceAzureSemanticVadTurnDetection(TypedDict, total=False):
        key "auto_truncate": bool
        key "create_response": bool
        key "end_of_utterance_detection": ForwardRef('VoiceEndOfUtteranceDetection', module='types')
        key "interrupt_response": bool
        key "prefix_padding_ms": int
        key "remove_filler_words": bool
        key "silence_duration_ms": int
        key "speech_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]]
        auto_truncate: bool
        create_response: bool
        end_of_utterance_detection: VoiceEndOfUtteranceDetection
        interrupt_response: bool
        languages: list[str]
        prefix_padding_ms: int
        remove_filler_words: bool
        silence_duration_ms: int
        speech_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.AZURE_SEMANTIC_VAD]


    class azure.ai.voiceagents.types.VoiceConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.voiceagents.types.VoiceEndOfUtteranceDetectionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_DETECTION_V1 = "semantic_detection_v1"
        SEMANTIC_DETECTION_V1_EN = "semantic_detection_v1_en"
        SEMANTIC_DETECTION_V1_MULTILINGUAL = "semantic_detection_v1_multilingual"


    class azure.ai.voiceagents.types.VoiceFunctionCallItem(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": str
        key "created_at": int
        key "id": str
        key "name": Required[str]
        key "object": Literal["item"]
        key "response_id": str
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.FUNCTION_CALL]]
        arguments: str
        call_id: str
        created_at: int
        id: str
        name: str
        object: Literal[item]
        response_id: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL]


    class azure.ai.voiceagents.types.VoiceFunctionCallOutputItem(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_at": int
        key "id": str
        key "name": str
        key "object": Literal["item"]
        key "output": Required[str]
        key "response_id": str
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]]
        call_id: str
        created_at: int
        id: str
        name: str
        object: Literal[item]
        output: str
        response_id: str
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.voiceagents.types.VoiceInputTranscription(TypedDict, total=False):
        key "delay": Literal["minimal", "low", "medium", "high", "xhigh"]
        key "language": str
        key "model": Required[Union[str, VoiceInputTranscriptionModel]]
        key "prompt": str
        custom_speech: dict[str, str]
        delay: Literal[minimal, low, medium, high, xhigh]
        language: str
        model: Union[str, VoiceInputTranscriptionModel]
        phrase_list: list[str]
        prompt: str


    class azure.ai.voiceagents.types.VoiceMcpApprovalRequestItem(TypedDict, total=False):
        key "arguments": Required[str]
        key "created_at": int
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]]
        arguments: str
        created_at: int
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.voiceagents.types.VoiceMcpApprovalResponseItem(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "created_at": int
        key "id": Required[str]
        key "reason": Optional[str]
        key "response_id": str
        key "type": Required[Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]]
        approval_request_id: str
        approve: bool
        created_at: int
        id: str
        reason: str
        response_id: str
        type: Literal[VoiceConversationItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.voiceagents.types.VoiceMcpCallItem(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "created_at": int
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[VoiceConversationItemType.MCP_CALL]]
        approval_request_id: str
        arguments: str
        created_at: int
        error: RealtimeMCPError
        id: str
        name: str
        output: str
        response_id: str
        server_label: str
        type: Literal[VoiceConversationItemType.MCP_CALL]


    class azure.ai.voiceagents.types.VoiceMcpListToolsItem(TypedDict, total=False):
        key "created_at": int
        key "id": str
        key "response_id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[VoiceConversationItemType.MCP_LIST_TOOLS]]
        created_at: int
        id: str
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[VoiceConversationItemType.MCP_LIST_TOOLS]


    class azure.ai.voiceagents.types.VoiceNoiseReduction(TypedDict, total=False):
        key "type": Required[Union[str, VoiceNoiseReductionType]]
        type: Union[str, VoiceNoiseReductionType]


    class azure.ai.voiceagents.types.VoiceSemanticVadTurnDetection(TypedDict, total=False):
        key "create_response": bool
        key "eagerness": Literal["low", "medium", "high", "auto"]
        key "interrupt_response": bool
        key "type": Required[Literal[VoiceTurnDetectionType.SEMANTIC_VAD]]
        create_response: bool
        eagerness: Literal[low, medium, high, auto]
        interrupt_response: bool
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]


    class azure.ai.voiceagents.types.VoiceServerVadTurnDetection(TypedDict, total=False):
        key "create_response": bool
        key "idle_timeout_ms": Optional[int]
        key "interrupt_response": bool
        key "prefix_padding_ms": int
        key "silence_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.SERVER_VAD]]
        create_response: bool
        idle_timeout_ms: int
        interrupt_response: bool
        prefix_padding_ms: int
        silence_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]


    class azure.ai.voiceagents.types.VoiceSystemMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageSystemContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.SYSTEM]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


    class azure.ai.voiceagents.types.VoiceSystemTool(TypedDict, total=False):
        key "description": str
        key "name": Required[Union[str, VoiceSystemToolName]]
        key "type": Required[Literal["system"]]
        description: str
        name: Union[str, VoiceSystemToolName]
        type: Literal[system]


    class azure.ai.voiceagents.types.VoiceToolboxTool(TypedDict, total=False):
        key "toolbox_name": Required[str]
        key "toolbox_version": Required[str]
        key "type": Required[Literal["toolbox"]]
        toolbox_name: str
        toolbox_version: str
        type: Literal[toolbox]


    class azure.ai.voiceagents.types.VoiceTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.voiceagents.types.VoiceUserMessageItem(TypedDict, total=False):
        key "content": Required[list[RealtimeConversationItemMessageUserContent]]
        key "created_at": int
        key "id": str
        key "object": Literal["item"]
        key "response_id": str
        key "role": Required[Literal[RealtimeConversationItemMessageType.USER]]
        key "status": Literal["completed", "incomplete", "in_progress"]
        key "type": Required[Literal[VoiceConversationItemType.MESSAGE]]
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: int
        id: str
        object: Literal[item]
        response_id: str
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Literal[completed, incomplete, in_progress]
        type: Literal[VoiceConversationItemType.MESSAGE]


```