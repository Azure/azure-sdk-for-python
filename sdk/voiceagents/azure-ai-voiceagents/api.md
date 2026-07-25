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

        def __init__(self, client: Any) -> None: ...

        def connect(
                self, 
                *, 
                agent_name: str, 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncRealtimeConnectionManager: ...


    class azure.ai.voiceagents.aio.AsyncRealtimeConnection: implements AsyncContextManager 

        def __aiter__(self) -> AsyncIterator[dict[str, Any]]: ...

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

        async def recv(self) -> dict[str, Any]: ...

        async def send(self, event: Union[Mapping[str, Any], str]) -> None: ...


    class azure.ai.voiceagents.aio.AsyncRealtimeConnectionManager: implements AsyncContextManager 

        def __init__(
                self, 
                *, 
                agent_name: str, 
                api_version: str, 
                credential: AsyncTokenCredential, 
                credential_scopes: List[str], 
                endpoint: str, 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def enter(self) -> AsyncRealtimeConnection: ...


    class azure.ai.voiceagents.aio.VoiceAgentsClient(_GeneratedVoiceAgentsClient): implements AsyncContextManager 
        property realtime: AsyncRealtime    # Read-only

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceDeletedConversation: ...

        @distributed_trace_async
        async def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace_async
        async def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def create_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        async def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace_async
        async def delete_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace_async
        async def delete_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace_async
        async def disable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def generate_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace_async
        async def get_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace_async
        async def get_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def list_voice_agent_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        async def update_voice_agent(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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


    class azure.ai.voiceagents.models.AzureVoice(_Model):
        locale: Optional[str]
        name: str
        pitch: Optional[str]
        rate: Optional[str]
        style: Optional[str]
        type: Union[str, AzureVoiceType]

        @overload
        def __init__(
                self, 
                *, 
                locale: Optional[str] = ..., 
                name: str, 
                pitch: Optional[str] = ..., 
                rate: Optional[str] = ..., 
                style: Optional[str] = ..., 
                type: Union[str, AzureVoiceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.AzureVoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVATAR_VOICE_SYNC = "avatar-voice-sync"
        AZURE_CUSTOM = "azure-custom"
        AZURE_PERSONAL = "azure-personal"
        AZURE_REALTIME_NATIVE = "azure-realtime-native"
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


    class azure.ai.voiceagents.models.DeleteAgentResponse(_Model):
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[AgentObjectType.AGENT_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.DeleteAgentVersionResponse(_Model):
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION_DELETED]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[AgentObjectType.AGENT_VERSION_DELETED], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.ai.voiceagents.models.FunctionTool(Tool, discriminator='function'):
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.InvocationsProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.InvocationsWsProtocolConfiguration(_Model):


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


    class azure.ai.voiceagents.models.PageOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


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


    class azure.ai.voiceagents.models.ResponsesProtocolConfiguration(_Model):


    class azure.ai.voiceagents.models.SemanticVadTurnDetection(VoiceTurnDetection, discriminator='semantic_vad'):
        eagerness: Optional[Union[str, VoiceTurnDetectionEagerness]]
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                eagerness: Optional[Union[str, VoiceTurnDetectionEagerness]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.ServerVadTurnDetection(VoiceTurnDetection, discriminator='server_vad'):
        create_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        threshold: Optional[float]
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]

        @overload
        def __init__(
                self, 
                *, 
                create_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[int] = ..., 
                silence_duration_ms: Optional[int] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_IQ_PREVIEW = "web_iq_preview"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


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


    class azure.ai.voiceagents.models.VoiceAgentDefinition(_Model):
        audio: Optional[VoiceAudioConfig]
        avatar: Optional[VoiceAvatarConfig]
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


    class azure.ai.voiceagents.models.VoiceAssistantMessageItem(RealtimeConversationItemMessageAssistant):
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: Optional[datetime]
        id: str
        object: str
        response_id: Optional[str]
        role: Union[str, azure.ai.voiceagents.models.ASSISTANT]
        status: Union[str, str, str]
        type: str

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
        speed: Optional[float]
        voice: Optional[Union[str, AzureVoice]]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[VoiceAudioFormat] = ..., 
                speed: Optional[float] = ..., 
                voice: Optional[Union[str, AzureVoice]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        PHOTO_AVATAR = "photo-avatar"
        VIDEO_AVATAR = "video-avatar"


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


    class azure.ai.voiceagents.models.VoiceConversationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        IN_PROGRESS = "in_progress"


    class azure.ai.voiceagents.models.VoiceDeletedConversation(_Model):
        deleted: bool
        id: str
        object: Literal["deleted"]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceFunctionCallItem(RealtimeConversationItemFunctionCall):
        arguments: str
        call_id: str
        created_at: Optional[datetime]
        id: str
        name: str
        object: str
        response_id: Optional[str]
        status: Union[str, str, str]
        type: Union[str, azure.ai.voiceagents.models.FUNCTION_CALL]

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


    class azure.ai.voiceagents.models.VoiceFunctionCallOutputItem(RealtimeConversationItemFunctionCallOutput):
        call_id: str
        created_at: Optional[datetime]
        id: str
        name: Optional[str]
        object: str
        output: str
        response_id: Optional[str]
        status: Union[str, str, str]
        type: Union[str, azure.ai.voiceagents.models.FUNCTION_CALL_OUTPUT]

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


    class azure.ai.voiceagents.models.VoiceInputTranscription(_Model):
        language: Optional[str]
        model: Optional[str]
        prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                language: Optional[str] = ..., 
                model: Optional[str] = ..., 
                prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceItemAudioResponse(_Model):
        blob_path: Optional[str]
        channels: Optional[int]
        codec: Optional[str]
        conversation_id: str
        duration_ms: Optional[int]
        format: Optional[str]
        item_id: str
        role: Optional[str]
        sample_rate: Optional[int]
        start_offset_ms: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                blob_path: Optional[str] = ..., 
                channels: Optional[int] = ..., 
                codec: Optional[str] = ..., 
                conversation_id: str, 
                duration_ms: Optional[int] = ..., 
                format: Optional[str] = ..., 
                item_id: str, 
                role: Optional[str] = ..., 
                sample_rate: Optional[int] = ..., 
                start_offset_ms: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceMcpApprovalRequestItem(RealtimeMCPApprovalRequest):
        arguments: str
        created_at: Optional[datetime]
        id: str
        name: str
        response_id: Optional[str]
        server_label: str
        type: Union[str, azure.ai.voiceagents.models.MCP_APPROVAL_REQUEST]

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


    class azure.ai.voiceagents.models.VoiceMcpApprovalResponseItem(RealtimeMCPApprovalResponse):
        approval_request_id: str
        approve: bool
        created_at: Optional[datetime]
        id: str
        reason: str
        response_id: Optional[str]
        type: Union[str, azure.ai.voiceagents.models.MCP_APPROVAL_RESPONSE]

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


    class azure.ai.voiceagents.models.VoiceMcpCallItem(RealtimeMCPToolCall):
        approval_request_id: str
        arguments: str
        created_at: Optional[datetime]
        error: RealtimeMCPError
        id: str
        name: str
        output: str
        response_id: Optional[str]
        server_label: str
        type: Union[str, azure.ai.voiceagents.models.MCP_CALL]

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


    class azure.ai.voiceagents.models.VoiceMcpListToolsItem(RealtimeMCPListTools):
        created_at: Optional[datetime]
        id: str
        response_id: Optional[str]
        server_label: str
        tools: list[MCPListToolsTool]
        type: Union[str, azure.ai.voiceagents.models.MCP_LIST_TOOLS]

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
        left: str
        right: str

        @overload
        def __init__(
                self, 
                *, 
                left: str, 
                right: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceRecordingResponse(_Model):
        blob_path: Optional[str]
        channel_layout: VoiceRecordingChannelLayout
        channels: int
        conversation_id: str
        duration_ms: int
        format: str
        sample_rate: int

        @overload
        def __init__(
                self, 
                *, 
                blob_path: Optional[str] = ..., 
                channel_layout: VoiceRecordingChannelLayout, 
                channels: int, 
                conversation_id: str, 
                duration_ms: int, 
                format: str, 
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


    class azure.ai.voiceagents.models.VoiceResponseVoice(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.voiceagents.models.VoiceSystemMessageItem(RealtimeConversationItemMessageSystem):
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: Optional[datetime]
        id: str
        object: str
        response_id: Optional[str]
        role: Union[str, azure.ai.voiceagents.models.SYSTEM]
        status: Union[str, str, str]
        type: str

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


    class azure.ai.voiceagents.models.VoiceTurnDetectionEagerness(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.voiceagents.models.VoiceTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.voiceagents.models.VoiceUserMessageItem(RealtimeConversationItemMessageUser):
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: Optional[datetime]
        id: str
        object: str
        response_id: Optional[str]
        role: Union[str, azure.ai.voiceagents.models.USER]
        status: Union[str, str, str]
        type: str

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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceDeletedConversation: ...

        @distributed_trace
        def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace
        def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace
        def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceConversationItem: ...

        @distributed_trace
        def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace
        def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def create_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @overload
        def create_voice_agent_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def delete_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace
        def delete_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace
        def disable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def generate_voice_agent(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace
        def get_voice_agent(
                self, 
                agent_name: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @distributed_trace
        def get_voice_agent_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentVersionObject: ...

        @distributed_trace
        def list_voice_agent_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
                **kwargs: Any
            ) -> VoiceAgentObject: ...

        @overload
        def update_voice_agent(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                foundry_features: Optional[Literal[AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW]] = ..., 
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


    class azure.ai.voiceagents.types.AzureVoice(TypedDict, total=False):
        key "locale": str
        key "name": Required[str]
        key "pitch": str
        key "rate": str
        key "style": str
        key "type": Required[Union[str, AzureVoiceType]]
        locale: str
        name: str
        pitch: str
        rate: str
        style: str
        type: Union[str, AzureVoiceType]


    class azure.ai.voiceagents.types.BotServiceAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]


    class azure.ai.voiceagents.types.BotServiceRbacAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]


    class azure.ai.voiceagents.types.BotServiceTenantAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]


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


    class azure.ai.voiceagents.types.FunctionTool(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Required[Optional[dict[str, Any]]]
        key "strict": Required[Optional[bool]]
        key "type": Required[Literal[ToolType.FUNCTION]]
        defer_loading: bool
        description: str
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]


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


    class azure.ai.voiceagents.types.MCPTool(TypedDict, total=False):
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


    class azure.ai.voiceagents.types.ProtocolConfiguration(TypedDict, total=False):
        key "a2a": ForwardRef('A2AProtocolConfiguration', module='types')
        key "activity": ForwardRef('ActivityProtocolConfiguration', module='types')
        key "invocations": ForwardRef('InvocationsProtocolConfiguration', module='types')
        key "invocations_ws": ForwardRef('InvocationsWsProtocolConfiguration', module='types')
        key "mcp": ForwardRef('McpProtocolConfiguration', module='types')
        key "responses": ForwardRef('ResponsesProtocolConfiguration', module='types')
        a2_a: A2AProtocolConfiguration
        activity: ActivityProtocolConfiguration
        invocations: InvocationsProtocolConfiguration
        invocations_ws: InvocationsWsProtocolConfiguration
        mcp: McpProtocolConfiguration
        responses: ResponsesProtocolConfiguration


    class azure.ai.voiceagents.types.RaiConfig(TypedDict, total=False):
        key "rai_policy_name": Required[str]
        rai_policy_name: str


    class azure.ai.voiceagents.types.ResponsesProtocolConfiguration(TypedDict, total=False):


    class azure.ai.voiceagents.types.SemanticVadTurnDetection(TypedDict, total=False):
        key "eagerness": Union[str, VoiceTurnDetectionEagerness]
        key "type": Required[Literal[VoiceTurnDetectionType.SEMANTIC_VAD]]
        eagerness: Union[str, VoiceTurnDetectionEagerness]
        type: Literal[VoiceTurnDetectionType.SEMANTIC_VAD]


    class azure.ai.voiceagents.types.ServerVadTurnDetection(TypedDict, total=False):
        key "create_response": bool
        key "prefix_padding_ms": int
        key "silence_duration_ms": int
        key "threshold": float
        key "type": Required[Literal[VoiceTurnDetectionType.SERVER_VAD]]
        create_response: bool
        prefix_padding_ms: int
        silence_duration_ms: int
        threshold: float
        type: Literal[VoiceTurnDetectionType.SERVER_VAD]


    class azure.ai.voiceagents.types.StructuredInputDefinition(TypedDict, total=False):
        key "default_value": Any
        key "description": str
        key "required": bool
        default_value: Any
        description: str
        required: bool
        schema: dict[str, Any]


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
        SHAREPOINT_GROUNDING_PREVIEW = "sharepoint_grounding_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        TOOL_SEARCH = "tool_search"
        WEB_IQ_PREVIEW = "web_iq_preview"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


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


    class azure.ai.voiceagents.types.VoiceAgentDefinition(TypedDict, total=False):
        key "audio": ForwardRef('VoiceAudioConfig', module='types')
        key "avatar": ForwardRef('VoiceAvatarConfig', module='types')
        key "instructions": Optional[str]
        key "kind": Required[Literal["voice"]]
        key "model": Required[str]
        key "model_type": Required[Union[str, VoiceModelType]]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "store": bool
        audio: VoiceAudioConfig
        avatar: VoiceAvatarConfig
        instructions: str
        kind: Literal[voice]
        model: str
        model_type: Union[str, VoiceModelType]
        output_modalities: list[Union[str, VoiceOutputModality]]
        rai_config: RaiConfig
        store: bool
        structured_inputs: dict[str, StructuredInputDefinition]
        tools: list[VoiceAgentTool]


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
        key "transcription": ForwardRef('VoiceInputTranscription', module='types')
        key "turn_detection": Optional[VoiceTurnDetection]
        format: VoiceAudioFormat
        noise_reduction: VoiceNoiseReduction
        transcription: VoiceInputTranscription
        turn_detection: VoiceTurnDetection


    class azure.ai.voiceagents.types.VoiceAudioOutputConfig(TypedDict, total=False):
        key "format": ForwardRef('VoiceAudioFormat', module='types')
        key "speed": float
        key "voice": Union[str, AzureVoice]
        format: VoiceAudioFormat
        speed: float
        voice: Union[str, AzureVoice]


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


    class azure.ai.voiceagents.types.VoiceInputTranscription(TypedDict, total=False):
        key "language": str
        key "model": str
        key "prompt": str
        language: str
        model: str
        prompt: str


    class azure.ai.voiceagents.types.VoiceNoiseReduction(TypedDict, total=False):
        key "type": Required[Union[str, VoiceNoiseReductionType]]
        type: Union[str, VoiceNoiseReductionType]


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
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


```