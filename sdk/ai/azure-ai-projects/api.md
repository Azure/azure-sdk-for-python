```py
namespace azure.ai.projects

    class azure.ai.projects.AIProjectClient(AIProjectClientGenerated): implements ContextManager 
        property realtime: Realtime    # Read-only
        agents: AgentsOperations
        beta: BetaOperations
        connections: ConnectionsOperations
        datasets: DatasetsOperations
        deployments: DeploymentsOperations
        evaluation_rules: EvaluationRulesOperations
        indexes: IndexesOperations
        toolboxes: ToolboxesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_openai_client(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> OpenAI: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.ai.projects.Realtime:

        def __init__(self, client: AIProjectClient) -> None: ...

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
                foundry_features: str = _VOICE_AGENT_FEATURE_HEADER, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> RealtimeConnectionManager: ...


    class azure.ai.projects.RealtimeConnection: implements ContextManager 
        property closed: bool    # Read-only

        def __init__(self, connection: ClientConnection) -> None: ...

        def __iter__(self) -> Iterator[ServerEvent]: ...

        def __repr__(self) -> str: ...

        def close(
                self, 
                *, 
                code: int = 1000, 
                reason: str = ""
            ) -> None: ...

        def recv(
                self, 
                *, 
                timeout: Optional[float] = ...
            ) -> ServerEvent: ...

        def send(self, event: ClientEvent) -> None: ...


    class azure.ai.projects.RealtimeConnectionManager: implements ContextManager 

        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_session_id: Optional[str] = ..., 
                agent_version_override: Optional[str] = ..., 
                api_version: str, 
                connection_url: Optional[str] = ..., 
                credential: TokenCredential, 
                credential_scopes: List[str], 
                endpoint: str, 
                extra_headers: Optional[Mapping[str, str]] = ..., 
                extra_query: Optional[Mapping[str, str]] = ..., 
                foundry_features: str, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def enter(self) -> RealtimeConnection: ...


namespace azure.ai.projects.aio

    class azure.ai.projects.aio.AIProjectClient(AIProjectClientGenerated): implements AsyncContextManager 
        property realtime: AsyncRealtime    # Read-only
        agents: AgentsOperations
        beta: BetaOperations
        connections: ConnectionsOperations
        datasets: DatasetsOperations
        deployments: DeploymentsOperations
        evaluation_rules: EvaluationRulesOperations
        indexes: IndexesOperations
        toolboxes: ToolboxesOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                allow_preview: bool = False, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace
        def get_openai_client(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncOpenAI: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


    class azure.ai.projects.aio.AsyncRealtime:

        def __init__(self, client: AIProjectClient) -> None: ...

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
                foundry_features: str = _VOICE_AGENT_FEATURE_HEADER, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncRealtimeConnectionManager: ...


    class azure.ai.projects.aio.AsyncRealtimeConnection: implements AsyncContextManager 
        property closed: bool    # Read-only

        def __aiter__(self) -> AsyncIterator[ServerEvent]: ...

        def __init__(
                self, 
                connection: ClientWebSocketResponse, 
                session: ClientSession
            ) -> None: ...

        def __repr__(self) -> str: ...

        async def close(
                self, 
                *, 
                code: int = 1000, 
                reason: str = ""
            ) -> None: ...

        async def recv(self) -> ServerEvent: ...

        async def send(self, event: ClientEvent) -> None: ...


    class azure.ai.projects.aio.AsyncRealtimeConnectionManager: implements AsyncContextManager 

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
                foundry_features: str, 
                structured_inputs: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def enter(self) -> AsyncRealtimeConnection: ...


namespace azure.ai.projects.aio.operations

    class azure.ai.projects.aio.operations.AgentEndpointConversationsOperations(GeneratedAgentEndpointConversationsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_agent_conversation_item_generated_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceGeneratedItemAudioResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_item_generated_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...


    class azure.ai.projects.aio.operations.AgentsOperations(GeneratedAgentsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                version_indicator: VersionIndicator, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        async def create_telephony_binding(
                self, 
                agent_name: str, 
                body: CreateTelephonyBindingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def create_telephony_binding(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def create_telephony_binding(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace_async
        async def create_version_from_code(
                self, 
                agent_name: str, 
                *, 
                code: IO[bytes], 
                code_zip_sha256: Optional[str] = ..., 
                definition: HostedAgentDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                manifest_id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                parameter_values: dict[str, Any], 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        async def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace_async
        async def delete(
                self, 
                agent_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace_async
        async def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace_async
        async def disable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def download_code(
                self, 
                agent_name: str, 
                *, 
                agent_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def download_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def enable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def end_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @distributed_trace_async
        async def generate_agent(
                self, 
                body: GenerateVoiceAgentRequest, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace_async
        async def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def get_microsoft365_package(
                self, 
                agent_name: str, 
                *, 
                access_boundaries: Optional[List[Union[str, ActivityProtocolAccessBoundary]]] = ..., 
                agent_display_name: Optional[str] = ..., 
                app_version: Optional[str] = ..., 
                bot_service_arm_id: Optional[str] = ..., 
                can_respond_without_mention: Optional[bool] = ..., 
                color_icon_base64: Optional[str] = ..., 
                content_type: str = "application/json", 
                developer_name: Optional[str] = ..., 
                developer_website_url: Optional[str] = ..., 
                full_description: Optional[str] = ..., 
                optional_permission_scopes: Optional[List[Microsoft365PermissionScopes]] = ..., 
                outline_icon_base64: Optional[str] = ..., 
                privacy_url: Optional[str] = ..., 
                publish_as_autopilot: Optional[bool] = ..., 
                publish_scope: Union[str, Microsoft365PublishScope], 
                short_description: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def get_microsoft365_package(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def get_microsoft365_package(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_microsoft365_publish_defaults(
                self, 
                agent_name: str, 
                *, 
                publish_as_digital_worker: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Microsoft365PublishDefaults: ...

        @distributed_trace_async
        async def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace_async
        async def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

        @distributed_trace_async
        async def get_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @distributed_trace_async
        async def get_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @distributed_trace_async
        async def get_telephony_transfer_targets(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @distributed_trace_async
        async def get_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                kind: Optional[Union[str, AgentKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentDetails]: ...

        @distributed_trace
        def list_session_files(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                path: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SessionDirectoryEntry]: ...

        @distributed_trace
        def list_sessions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentSessionResource]: ...

        @distributed_trace
        def list_telephony_bindings(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                provider: Optional[Union[str, TelephonyProvider]] = ..., 
                status: Optional[Union[str, TelephonyBindingStatus]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TelephonyBindingListItem]: ...

        @distributed_trace
        def list_telephony_calls(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                provider: Optional[Union[str, TelephonyProvider]] = ..., 
                started_after: Optional[datetime] = ..., 
                started_before: Optional[datetime] = ..., 
                status: Optional[Union[str, TelephonyCallStatus]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TelephonyCallSummary]: ...

        @distributed_trace
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentVersionDetails]: ...

        @overload
        async def publish_to_microsoft365(
                self, 
                agent_name: str, 
                *, 
                access_boundaries: Optional[List[Union[str, ActivityProtocolAccessBoundary]]] = ..., 
                agent_display_name: Optional[str] = ..., 
                app_version: Optional[str] = ..., 
                bot_service_arm_id: Optional[str] = ..., 
                can_respond_without_mention: Optional[bool] = ..., 
                color_icon_base64: Optional[str] = ..., 
                content_type: str = "application/json", 
                developer_name: Optional[str] = ..., 
                developer_website_url: Optional[str] = ..., 
                full_description: Optional[str] = ..., 
                optional_permission_scopes: Optional[List[Microsoft365PermissionScopes]] = ..., 
                outline_icon_base64: Optional[str] = ..., 
                privacy_url: Optional[str] = ..., 
                publish_as_autopilot: Optional[bool] = ..., 
                publish_scope: Union[str, Microsoft365PublishScope], 
                short_description: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        async def publish_to_microsoft365(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        async def publish_to_microsoft365(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        async def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                transfer_targets: List[TelephonyTransferTarget], 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @overload
        async def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @overload
        async def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @distributed_trace_async
        async def stop_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                *, 
                content_type: str = "application/json", 
                target: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        async def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        async def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def update_details(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        async def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: UpdateTelephonyBindingRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        async def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...

        @overload
        async def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: IO[bytes], 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.aio.operations.BetaAgentEndpointConversationsOperations:

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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace_async
        async def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> RealtimeConversationItem: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace_async
        async def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RealtimeConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RealtimeConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceResponse]: ...

        @distributed_trace
        def list_agent_conversations(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[VoiceConversation]: ...


    class azure.ai.projects.aio.operations.BetaAgentInsightMonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_run(
                self, 
                monitor_id: str, 
                run: AgentInsightRunCreate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentInsightRunResult]: ...

        @overload
        async def begin_create_run(
                self, 
                monitor_id: str, 
                run: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentInsightRunResult]: ...

        @overload
        async def begin_create_run(
                self, 
                monitor_id: str, 
                run: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentInsightRunResult]: ...

        @distributed_trace_async
        async def cancel_run(
                self, 
                monitor_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> AgentInsightRun: ...

        @overload
        async def create(
                self, 
                monitor: AgentInsightMonitorCreate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        async def create(
                self, 
                monitor: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        async def create(
                self, 
                monitor: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @distributed_trace_async
        async def delete(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @distributed_trace_async
        async def get_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                *, 
                include_details: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AgentInsight: ...

        @distributed_trace_async
        async def get_run(
                self, 
                monitor_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> AgentInsightRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentInsightMonitorListItem]: ...

        @distributed_trace
        def list_insights(
                self, 
                monitor_id: str, 
                *, 
                before: Optional[str] = ..., 
                category: Optional[str] = ..., 
                include_details: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                severity: Optional[Union[str, AgentInsightSeverity]] = ..., 
                status: Optional[Union[str, AgentInsightStatus]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentInsight]: ...

        @distributed_trace
        def list_runs(
                self, 
                monitor_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                trigger: Optional[Union[str, AgentInsightRunTrigger]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentInsightRun]: ...

        @distributed_trace_async
        async def reset(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                monitor_id: str, 
                monitor: AgentInsightMonitorUpdate, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        async def update(
                self, 
                monitor_id: str, 
                monitor: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        async def update(
                self, 
                monitor_id: str, 
                monitor: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        async def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: AgentInsightUpdate, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...

        @overload
        async def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...

        @overload
        async def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...


    class azure.ai.projects.aio.operations.BetaAgentsOperations(BetaAgentsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncAgentOptimizationLROPoller: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncAgentOptimizationLROPoller: ...

        @overload
        async def begin_create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncAgentOptimizationLROPoller: ...

        @distributed_trace_async
        async def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace_async
        async def delete_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def list_optimization_jobs(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentOptimizationJobListItem]: ...


    class azure.ai.projects.aio.operations.BetaDatasetsOperations(BetaDatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncDatasetGenerationLROPoller: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncDatasetGenerationLROPoller: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncDatasetGenerationLROPoller: ...

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace_async
        async def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DataGenerationJob]: ...


    class azure.ai.projects.aio.operations.BetaEvaluationTaxonomiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def create(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                input_name: Optional[str] = ..., 
                input_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluationTaxonomy]: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        async def update(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...


    class azure.ai.projects.aio.operations.BetaEvaluatorsOperations(BetaEvaluatorsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncEvaluatorGenerationLROPoller: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncEvaluatorGenerationLROPoller: ...

        @overload
        async def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncEvaluatorGenerationLROPoller: ...

        @distributed_trace_async
        async def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace_async
        async def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace_async
        async def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorVersion]: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorGenerationJob]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluatorVersion]: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        async def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...


    class azure.ai.projects.aio.operations.BetaInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def generate(
                self, 
                insight: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        async def generate(
                self, 
                insight: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace_async
        async def get(
                self, 
                insight_id: str, 
                *, 
                include_coordinates: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                include_coordinates: Optional[bool] = ..., 
                run_id: Optional[str] = ..., 
                type: Optional[Union[str, InsightType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Insight]: ...


    class azure.ai.projects.aio.operations.BetaMemoryStoresOperations(GenerateBetaMemoryStoresOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                previous_update_id: Optional[str] = ..., 
                scope: str, 
                update_delay: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def begin_update_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...

        @overload
        async def create(
                self, 
                *, 
                content_type: str = "application/json", 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                kind: Union[str, MemoryItemKind], 
                scope: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def create_memory(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

        @distributed_trace_async
        async def delete_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> DeleteMemoryResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        async def delete_scope(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @distributed_trace_async
        async def get_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryStoreDetails]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MemoryItem]: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                options: Optional[MemorySearchOptions] = ..., 
                previous_search_id: Optional[str] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def search_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        async def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...


    class azure.ai.projects.aio.operations.BetaModelsOperations(BetaModelsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[True] = True, 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def create(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[False], 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ModelVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelVersion]: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        async def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...


    class azure.ai.projects.aio.operations.BetaOperations(GeneratedBetaOperations):
        agent_endpoint_conversations: BetaAgentEndpointConversationsOperations
        agent_insight_monitors: BetaAgentInsightMonitorsOperations
        agents: BetaAgentsOperations
        datasets: BetaDatasetsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        models: BetaModelsOperations
        red_teams: BetaRedTeamsOperations
        routines: BetaRoutinesOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.aio.operations.BetaRedTeamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        async def create(
                self, 
                red_team: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        async def create(
                self, 
                red_team: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[RedTeam]: ...


    class azure.ai.projects.aio.operations.BetaRoutinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                *, 
                action: Optional[RoutineAction] = ..., 
                authorization: Optional[RoutineAuthorization] = ..., 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def create_or_update(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace_async
        async def delete(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                *, 
                content_type: str = "application/json", 
                payload: Optional[RoutineDispatchPayload] = ..., 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        async def dispatch(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @distributed_trace_async
        async def enable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace_async
        async def get(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                after: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Routine]: ...

        @distributed_trace
        def list_runs(
                self, 
                routine_name: str, 
                *, 
                after: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[RoutineRun]: ...


    class azure.ai.projects.aio.operations.BetaSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        async def create_or_update(
                self, 
                schedule_id: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace_async
        async def get_run(
                self, 
                schedule_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScheduleRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Schedule]: ...

        @distributed_trace
        def list_runs(
                self, 
                schedule_id: str, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ScheduleRun]: ...


    class azure.ai.projects.aio.operations.BetaSkillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default: Optional[bool] = ..., 
                inline_content: Optional[SkillInlineContent] = ..., 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        async def create_from_files(
                self, 
                name: str, 
                content: JSON, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResult: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DeleteSkillVersionResult: ...

        @distributed_trace_async
        async def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def download_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkillDetails]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkillVersion]: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...


    class azure.ai.projects.aio.operations.ConnectionsOperations(ConnectionsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace_async
        async def get_default(
                self, 
                connection_type: Union[str, ConnectionType], 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                *, 
                connection_type: Optional[Union[str, ConnectionType]] = ..., 
                default_connection: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Connection]: ...


    class azure.ai.projects.aio.operations.DatasetsOperations(DatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace_async
        async def get_credentials(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DatasetVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatasetVersion]: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        async def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @distributed_trace_async
        async def upload_file(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_path: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FileDatasetVersion: ...

        @distributed_trace_async
        async def upload_folder(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_pattern: Optional[Pattern] = ..., 
                folder: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FolderDatasetVersion: ...


    class azure.ai.projects.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                deployment_type: Optional[Union[str, DeploymentType]] = ..., 
                model_name: Optional[str] = ..., 
                model_publisher: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...


    class azure.ai.projects.aio.operations.EvaluationRulesOperations(GeneratedEvaluationRulesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: EvaluationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        async def create_or_update(
                self, 
                id: str, 
                evaluation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def list(
                self, 
                *, 
                action_type: Optional[Union[str, EvaluationRuleActionType]] = ..., 
                agent_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EvaluationRule]: ...


    class azure.ai.projects.aio.operations.IndexesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        async def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Index]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Index]: ...


    class azure.ai.projects.aio.operations.TelemetryOperations:

        def __init__(self, outer_instance: AIProjectClient) -> None: ...

        @distributed_trace_async
        async def get_application_insights_connection_string(self) -> str: ...


    class azure.ai.projects.aio.operations.ToolboxesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[List[ToolboxSkill]] = ..., 
                tools: List[ToolboxTool], 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        async def create_version(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace_async
        async def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @distributed_trace_async
        async def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ToolboxObject]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ToolboxVersionObject]: ...

        @overload
        async def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        async def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...


namespace azure.ai.projects.models

    class azure.ai.projects.models.A2APreviewTool(Tool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        type: Literal[ToolType.A2A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.A2APreviewToolboxTool(ToolboxTool, discriminator='a2a_preview'):
        agent_card_path: Optional[str]
        base_url: Optional[str]
        description: str
        name: str
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.A2A_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.A2AProtocolConfiguration(_Model):


    class azure.ai.projects.models.A2AProtocolVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1_0 = "1.0"


    class azure.ai.projects.models.A2ATool(Tool, discriminator='a2a'):
        a2a_version: Union[str, A2AProtocolVersion]
        agent_card_path: Optional[str]
        base_url: Optional[str]
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        type: Literal[ToolType.A2_A]

        @overload
        def __init__(
                self, 
                *, 
                a2a_version: Union[str, A2AProtocolVersion], 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.A2AToolboxTool(ToolboxTool, discriminator='a2a'):
        a2a_version: Union[str, A2AProtocolVersion]
        agent_card_path: Optional[str]
        base_url: Optional[str]
        description: str
        name: str
        project_connection_id: Optional[str]
        send_credentials_for_agent_card: Optional[bool]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.A2_A]

        @overload
        def __init__(
                self, 
                *, 
                a2a_version: Union[str, A2AProtocolVersion], 
                agent_card_path: Optional[str] = ..., 
                base_url: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                send_credentials_for_agent_card: Optional[bool] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AISearchIndexResource(_Model):
        filter: Optional[str]
        index_asset_id: Optional[str]
        index_name: Optional[str]
        project_connection_id: Optional[str]
        query_type: Optional[Union[str, AzureAISearchQueryType]]
        top_k: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                filter: Optional[str] = ..., 
                index_asset_id: Optional[str] = ..., 
                index_name: Optional[str] = ..., 
                project_connection_id: Optional[str] = ..., 
                query_type: Optional[Union[str, AzureAISearchQueryType]] = ..., 
                top_k: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ActivityProtocolAccessBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ1_ON1_ALLOWLISTED = "read.1on1.allowlisted"
        READ1_ON1_DEVELOPERS = "read.1on1.developers"
        READ1_ON1_MANAGER = "read.1on1.manager"
        READ1_ON1_TENANT = "read.1on1.tenant"
        READ_GROUP_ALLOWLISTED = "read.group.allowlisted"
        READ_GROUP_DEVELOPERS = "read.group.developers"
        READ_GROUP_MANAGER_INVITED = "read.group.manager-invited"
        READ_GROUP_MANAGER_PRESENT = "read.group.manager-present"
        READ_GROUP_TENANT = "read.group.tenant"
        WRITE1_ON1_ALLOWLISTED = "write.1on1.allowlisted"
        WRITE1_ON1_DEVELOPERS = "write.1on1.developers"
        WRITE1_ON1_MANAGER = "write.1on1.manager"
        WRITE1_ON1_TENANT = "write.1on1.tenant"
        WRITE_GROUP_ALLOWLISTED = "write.group.allowlisted"
        WRITE_GROUP_DEVELOPERS = "write.group.developers"
        WRITE_GROUP_MANAGER_INVITED = "write.group.manager-invited"
        WRITE_GROUP_MANAGER_PRESENT = "write.group.manager-present"
        WRITE_GROUP_TENANT = "write.group.tenant"


    class azure.ai.projects.models.ActivityProtocolConfiguration(_Model):
        access_boundaries: Optional[list[Union[str, ActivityProtocolAccessBoundary]]]
        enable_m365_public_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enable_m365_public_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentBlueprintReference(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentBlueprintReferenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_AGENT_IDENTITY_BLUEPRINT = "ManagedAgentIdentityBlueprint"


    class azure.ai.projects.models.AgentCard(_Model):
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


    class azure.ai.projects.models.AgentCardSkill(_Model):
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


    class azure.ai.projects.models.AgentClusterInsightRequest(InsightRequest, discriminator='AgentClusterInsight'):
        agent_name: str
        model_configuration: Optional[InsightModelConfiguration]
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                model_configuration: Optional[InsightModelConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentClusterInsightResult(InsightResult, discriminator='AgentClusterInsight'):
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                cluster_insight: ClusterInsightResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDataGenerationJobSource(DataGenerationJobSource, discriminator='agent'):
        agent_name: str
        agent_version: Optional[str]
        description: str
        type: Literal[DataGenerationJobSourceType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDefinition(_Model):
        kind: str
        rai_config: Optional[RaiConfig]

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentDetails(_Model):
        agent_card: Optional[AgentCard]
        agent_endpoint: Optional[AgentEndpointConfig]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        digital_worker_type: Optional[Union[str, DigitalWorkerType]]
        id: str
        instance_identity: Optional[AgentIdentity]
        name: str
        object: Literal[AgentObjectType.AGENT]
        state: Union[str, AgentState]
        state_source: Optional[Union[str, AgentStateSource]]
        versions: AgentObjectVersions

        @overload
        def __init__(
                self, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                digital_worker_type: Optional[Union[str, DigitalWorkerType]] = ..., 
                id: str, 
                name: str, 
                object: Literal[AgentObjectType.AGENT], 
                versions: AgentObjectVersions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpointAuthorizationScheme(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentEndpointAuthorizationSchemeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT_SERVICE = "BotService"
        BOT_SERVICE_RBAC = "BotServiceRbac"
        BOT_SERVICE_TENANT = "BotServiceTenant"
        ENTRA = "Entra"


    class azure.ai.projects.models.AgentEndpointConfig(_Model):
        authorization_schemes: Optional[list[AgentEndpointAuthorizationScheme]]
        protocol_configuration: Optional[ProtocolConfiguration]
        publish_approval_status: Optional[Union[str, PublishApprovalStatus]]
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


    class azure.ai.projects.models.AgentEndpointProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A = "a2a"
        ACTIVITY = "activity"
        INVOCATIONS = "invocations"
        INVOCATIONS_WS = "invocations_ws"
        MCP = "mcp"
        RESPONSES = "responses"
        VOICE = "voice"


    class azure.ai.projects.models.AgentEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='agent'):
        agent_name: str
        agent_version: Optional[str]
        description: Optional[str]
        type: Literal[EvaluatorGenerationJobSourceType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentIdentity(_Model):
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


    class azure.ai.projects.models.AgentIdentityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        DISABLED = "disabled"


    class azure.ai.projects.models.AgentInsight(_Model):
        agent_name: str
        agent_version: str
        category: str
        created_at: datetime
        description: str
        details: Optional[AgentInsightDetails]
        id: str
        monitor_id: str
        severity: Union[str, AgentInsightSeverity]
        status: Union[str, AgentInsightStatus]
        title: str
        trace_count: int
        updated_at: datetime


    class azure.ai.projects.models.AgentInsightDetails(_Model):
        highlighted_traces: list[AgentInsightHighlightedTrace]
        linked_traces: list[AgentInsightLinkedTrace]
        recommended_actions: AgentInsightRecommendedAction

        @overload
        def __init__(
                self, 
                *, 
                highlighted_traces: list[AgentInsightHighlightedTrace], 
                linked_traces: list[AgentInsightLinkedTrace], 
                recommended_actions: AgentInsightRecommendedAction
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightEstimatedCost(_Model):
        amount: float
        currency: Literal["USD"]

        @overload
        def __init__(
                self, 
                *, 
                amount: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightHighlightedTrace(_Model):
        duration_ms: timedelta
        summary: str
        timestamp: datetime
        total_tokens: Optional[int]
        trace_id: str

        @overload
        def __init__(
                self, 
                *, 
                duration_ms: timedelta, 
                summary: str, 
                timestamp: datetime, 
                total_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightLinkedTrace(_Model):
        timestamp: datetime
        trace_id: str


    class azure.ai.projects.models.AgentInsightMonitor(_Model):
        agent_name: str
        enabled: bool
        estimated_cost: Optional[AgentInsightEstimatedCost]
        id: str
        model_deployment_name: str
        next_scheduled_run_at: Optional[datetime]
        overview: AgentInsightsOverview
        run_interval_hours: float
        suspension: AgentInsightSuspension
        updated_at: datetime


    class azure.ai.projects.models.AgentInsightMonitorCreate(_Model):
        agent_name: str
        enabled: Optional[bool]
        model_deployment_name: str
        run_interval_hours: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                enabled: Optional[bool] = ..., 
                model_deployment_name: str, 
                run_interval_hours: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightMonitorListItem(_Model):
        agent_name: str
        enabled: bool
        estimated_cost: Optional[AgentInsightEstimatedCost]
        id: str
        model_deployment_name: str
        next_scheduled_run_at: Optional[datetime]
        run_interval_hours: float
        suspension: AgentInsightSuspension
        updated_at: datetime


    class azure.ai.projects.models.AgentInsightMonitorUpdate(_Model):
        enabled: Optional[bool]
        model_deployment_name: Optional[str]
        overview_override: Optional[AgentInsightsOverviewOverride]
        run_interval_hours: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                model_deployment_name: Optional[str] = ..., 
                overview_override: Optional[AgentInsightsOverviewOverride] = ..., 
                run_interval_hours: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightOverviewSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERATED = "generated"
        USER_OVERRIDE = "user_override"


    class azure.ai.projects.models.AgentInsightPromptSurface(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTRUCTIONS = "instructions"
        TOOL = "tool"


    class azure.ai.projects.models.AgentInsightProposedFix(_Model):
        changes: Optional[list[AgentInsightProposedFixChange]]
        kind: Union[str, AgentInsightProposedFixKind]
        text: str

        @overload
        def __init__(
                self, 
                *, 
                changes: Optional[list[AgentInsightProposedFixChange]] = ..., 
                kind: Union[str, AgentInsightProposedFixKind], 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightProposedFixChange(_Model):
        diff: Optional[str]
        language: Optional[str]
        new_value: Optional[Any]
        old_value: Optional[Any]
        path: Optional[str]
        surface: Optional[Union[str, AgentInsightPromptSurface]]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                diff: Optional[str] = ..., 
                language: Optional[str] = ..., 
                new_value: Optional[Any] = ..., 
                old_value: Optional[Any] = ..., 
                path: Optional[str] = ..., 
                surface: Optional[Union[str, AgentInsightPromptSurface]] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightProposedFixKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_CHANGE = "code_change"
        PROMPT_CHANGE = "prompt_change"
        PROSE = "prose"


    class azure.ai.projects.models.AgentInsightRecommendedAction(_Model):
        proposed_fix: AgentInsightProposedFix

        @overload
        def __init__(
                self, 
                *, 
                proposed_fix: AgentInsightProposedFix
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightRun(_Model):
        agent_name: str
        completed_at: Optional[datetime]
        created_at: datetime
        error: Optional[ApiError]
        id: str
        inputs: Optional[AgentInsightRunCreate]
        model_deployment_name: str
        monitor_id: str
        result: Optional[AgentInsightRunResult]
        started_at: Optional[datetime]
        status: Union[str, JobStatus]
        trigger: Union[str, AgentInsightRunTrigger]
        updated_at: datetime
        window_end: datetime
        window_start: datetime

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[AgentInsightRunCreate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightRunCreate(_Model):
        lookback_hours: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                lookback_hours: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightRunResult(_Model):
        insights_created: int
        insights_reopened: int
        insights_updated: int
        token_usage: AgentInsightTokenUsage
        traces_analyzed: int
        traces_in_window: int

        @overload
        def __init__(
                self, 
                *, 
                insights_created: int, 
                insights_reopened: int, 
                insights_updated: int, 
                token_usage: AgentInsightTokenUsage, 
                traces_analyzed: int, 
                traces_in_window: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightRunTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ON_DEMAND = "on_demand"
        SCHEDULED = "scheduled"


    class azure.ai.projects.models.AgentInsightSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.projects.models.AgentInsightStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        IGNORED = "ignored"
        RESOLVED = "resolved"


    class azure.ai.projects.models.AgentInsightSuspension(_Model):
        code: str
        details: Optional[dict[str, Any]]
        message: str
        occurred_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[dict[str, Any]] = ..., 
                message: str, 
                occurred_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightTokenUsage(_Model):
        cached_tokens: Optional[int]
        input_tokens: int
        output_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                cached_tokens: Optional[int] = ..., 
                input_tokens: int, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightUpdate(_Model):
        status: Optional[Union[str, AgentInsightStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, AgentInsightStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightsOverview(_Model):
        content: str
        source: Union[str, AgentInsightOverviewSource]
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                source: Union[str, AgentInsightOverviewSource], 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentInsightsOverviewOverride(_Model):
        content: str

        @overload
        def __init__(
                self, 
                *, 
                content: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "external"
        HOSTED = "hosted"
        PROMPT = "prompt"
        VOICE = "voice"
        WORKFLOW = "workflow"


    class azure.ai.projects.models.AgentObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        AGENT_CONTAINER = "agent.container"
        AGENT_DELETED = "agent.deleted"
        AGENT_VERSION = "agent.version"
        AGENT_VERSION_DELETED = "agent.version.deleted"


    class azure.ai.projects.models.AgentObjectVersions(_Model):
        latest: AgentVersionDetails

        @overload
        def __init__(
                self, 
                *, 
                latest: AgentVersionDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationCandidate(_Model):
        avg_score: float
        avg_tokens: float
        candidate_id: Optional[str]
        eval_id: Optional[str]
        eval_run_id: Optional[str]
        mutations: Optional[dict[str, Any]]
        name: str
        promotion: Optional[PromotionInfo]

        @overload
        def __init__(
                self, 
                *, 
                avg_score: float, 
                avg_tokens: float, 
                candidate_id: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                eval_run_id: Optional[str] = ..., 
                mutations: Optional[dict[str, Any]] = ..., 
                name: str, 
                promotion: Optional[PromotionInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetCriterion(_Model):
        instruction: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                instruction: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetInput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationDatasetInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        REFERENCE = "reference"


    class azure.ai.projects.models.AgentOptimizationDatasetItem(_Model):
        criteria: Optional[list[AgentOptimizationDatasetCriterion]]
        desired_num_turns: Optional[int]
        ground_truth: Optional[str]
        query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                criteria: Optional[list[AgentOptimizationDatasetCriterion]] = ..., 
                desired_num_turns: Optional[int] = ..., 
                ground_truth: Optional[str] = ..., 
                query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationEvaluatorRef(_Model):
        name: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationInlineDatasetInput(AgentOptimizationDatasetInput, discriminator='inline'):
        dataset_items: list[AgentOptimizationDatasetItem]
        type: Literal[AgentOptimizationDatasetInputType.INLINE]

        @overload
        def __init__(
                self, 
                *, 
                dataset_items: list[AgentOptimizationDatasetItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        id: str
        inputs: Optional[AgentOptimizationJobInputs]
        progress: Optional[AgentOptimizationJobProgress]
        result: Optional[AgentOptimizationJobResult]
        status: Union[str, JobStatus]
        updated_at: datetime
        warnings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[AgentOptimizationJobInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobInputs(_Model):
        agent: OptimizedAgentIdentifier
        evaluators: list[AgentOptimizationEvaluatorRef]
        options: Optional[AgentOptimizationOptions]
        train_dataset: AgentOptimizationDatasetInput
        validation_dataset: Optional[AgentOptimizationDatasetInput]

        @overload
        def __init__(
                self, 
                *, 
                agent: OptimizedAgentIdentifier, 
                evaluators: list[AgentOptimizationEvaluatorRef], 
                options: Optional[AgentOptimizationOptions] = ..., 
                train_dataset: AgentOptimizationDatasetInput, 
                validation_dataset: Optional[AgentOptimizationDatasetInput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobListItem(_Model):
        agent: Optional[OptimizedAgentIdentifier]
        created_at: datetime
        error: Optional[ApiError]
        id: str
        progress: Optional[AgentOptimizationJobProgress]
        status: Union[str, JobStatus]
        updated_at: datetime


    class azure.ai.projects.models.AgentOptimizationJobProgress(_Model):
        best_score: float
        candidates_completed: int
        elapsed_seconds: float

        @overload
        def __init__(
                self, 
                *, 
                best_score: float, 
                candidates_completed: int, 
                elapsed_seconds: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationJobResult(_Model):
        baseline: Optional[str]
        best: Optional[str]
        candidates: Optional[list[AgentOptimizationCandidate]]

        @overload
        def __init__(
                self, 
                *, 
                baseline: Optional[str] = ..., 
                best: Optional[str] = ..., 
                candidates: Optional[list[AgentOptimizationCandidate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationLROPoller(LROPoller[AgentOptimizationJobResult]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[AgentOptimizationJobResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AgentOptimizationLROPoller: ...


    class azure.ai.projects.models.AgentOptimizationOptions(_Model):
        eval_model: Optional[str]
        evaluation_level: Optional[Union[str, EvaluationLevel]]
        max_candidates: Optional[int]
        max_stalls: Optional[int]
        optimization_config: Optional[dict[str, Any]]
        optimization_model: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                eval_model: Optional[str] = ..., 
                evaluation_level: Optional[Union[str, EvaluationLevel]] = ..., 
                max_candidates: Optional[int] = ..., 
                max_stalls: Optional[int] = ..., 
                optimization_config: Optional[dict[str, Any]] = ..., 
                optimization_model: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentOptimizationReferenceDatasetInput(AgentOptimizationDatasetInput, discriminator='reference'):
        name: str
        type: Literal[AgentOptimizationDatasetInputType.REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentSessionResource(_Model):
        agent_session_id: str
        created_at: datetime
        expires_at: datetime
        last_accessed_at: datetime
        status: Union[str, AgentSessionStatus]
        version_indicator: VersionIndicator

        @overload
        def __init__(
                self, 
                *, 
                agent_session_id: str, 
                status: Union[str, AgentSessionStatus], 
                version_indicator: VersionIndicator
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentSessionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETED = "deleted"
        DELETING = "deleting"
        EXPIRED = "expired"
        FAILED = "failed"
        IDLE = "idle"
        UPDATING = "updating"


    class azure.ai.projects.models.AgentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.ai.projects.models.AgentStateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_BLUEPRINT = "agent_blueprint"
        AGENT_INSTANCE_IDENTITY = "agent_instance_identity"


    class azure.ai.projects.models.AgentTaxonomyInput(EvaluationTaxonomyInput, discriminator='agent'):
        risk_categories: list[Union[str, RiskCategory]]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]

        @overload
        def __init__(
                self, 
                *, 
                risk_categories: list[Union[str, RiskCategory]], 
                target: EvaluationTarget
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AgentVersionDetails(_Model):
        agent_guid: Optional[str]
        blueprint: Optional[AgentIdentity]
        blueprint_reference: Optional[AgentBlueprintReference]
        created_at: datetime
        definition: AgentDefinition
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
                definition: AgentDefinition, 
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


    class azure.ai.projects.models.AgentVersionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        CREATING = "creating"
        DELETED = "deleted"
        DELETING = "deleting"
        FAILED = "failed"


    class azure.ai.projects.models.AgenticIdentityPreviewCredentials(BaseCredentials, discriminator='AgenticIdentityToken_Preview'):
        type: Literal[CredentialType.AGENTIC_IDENTITY_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiError(_Model):
        additional_info: Optional[dict[str, Any]]
        code: str
        debug_info: Optional[dict[str, Any]]
        details: Optional[list[ApiError]]
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
                details: Optional[list[ApiError]] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiErrorResponse(_Model):
        error: ApiError

        @overload
        def __init__(
                self, 
                *, 
                error: ApiError
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApiKeyCredentials(BaseCredentials, discriminator='ApiKey'):
        api_key: Optional[str]
        type: Literal[CredentialType.API_KEY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApplyPatchToolParam(Tool, discriminator='apply_patch'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        type: Literal[ToolType.APPLY_PATCH]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ApproximateLocation(_Model):
        city: Optional[str]
        country: Optional[str]
        region: Optional[str]
        timezone: Optional[str]
        type: Literal["approximate"]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                region: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ArtifactProfile(_Model):
        category: Union[str, FoundryModelArtifactProfileCategory]
        signals: Optional[list[Union[str, FoundryModelArtifactProfileSignal]]]

        @overload
        def __init__(
                self, 
                *, 
                category: Union[str, FoundryModelArtifactProfileCategory], 
                signals: Optional[list[Union[str, FoundryModelArtifactProfileSignal]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AsyncAgentOptimizationLROPoller(AsyncLROPoller[AgentOptimizationJobResult]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[AgentOptimizationJobResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncAgentOptimizationLROPoller: ...


    class azure.ai.projects.models.AsyncDatasetGenerationLROPoller(AsyncLROPoller[DataGenerationJobResult]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[DataGenerationJobResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncDatasetGenerationLROPoller: ...


    class azure.ai.projects.models.AsyncEvaluatorGenerationLROPoller(AsyncLROPoller[EvaluatorVersion]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[EvaluatorVersion], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncEvaluatorGenerationLROPoller: ...


    class azure.ai.projects.models.AsyncUpdateMemoriesLROPoller(AsyncLROPoller[MemoryStoreUpdateCompletedResult]):
        property superseded_by: Optional[str]    # Read-only
        property update_id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: AsyncPollingMethod[MemoryStoreUpdateCompletedResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> AsyncUpdateMemoriesLROPoller: ...


    class azure.ai.projects.models.AttackStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSI_ATTACK = "ansi_attack"
        ASCII_ART = "ascii_art"
        ASCII_SMUGGLER = "ascii_smuggler"
        ATBASH = "atbash"
        BASE64 = "base64"
        BASELINE = "baseline"
        BINARY = "binary"
        CAESAR = "caesar"
        CHARACTER_SPACE = "character_space"
        CHARACTER_SWAP = "character_swap"
        CRESCENDO = "crescendo"
        DIACRITIC = "diacritic"
        DIFFICULT = "difficult"
        EASY = "easy"
        FLIP = "flip"
        INDIRECT_JAILBREAK = "indirect_jailbreak"
        JAILBREAK = "jailbreak"
        LEETSPEAK = "leetspeak"
        MODERATE = "moderate"
        MORSE = "morse"
        MULTI_TURN = "multi_turn"
        ROT13 = "rot13"
        STRING_JOIN = "string_join"
        SUFFIX_APPEND = "suffix_append"
        TENSE = "tense"
        UNICODE_CONFUSABLE = "unicode_confusable"
        UNICODE_SUBSTITUTION = "unicode_substitution"
        URL = "url"


    class azure.ai.projects.models.AutoCodeInterpreterToolParam(_Model):
        file_ids: Optional[list[str]]
        memory_limit: Optional[Union[str, ContainerMemoryLimit]]
        network_policy: Optional[ContainerNetworkPolicyParam]
        type: Literal["auto"]

        @overload
        def __init__(
                self, 
                *, 
                file_ids: Optional[list[str]] = ..., 
                memory_limit: Optional[Union[str, ContainerMemoryLimit]] = ..., 
                network_policy: Optional[ContainerNetworkPolicyParam] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIAgentTarget(EvaluationTarget, discriminator='azure_ai_agent'):
        name: str
        tool_descriptions: Optional[list[ToolDescription]]
        tools: Optional[list[Tool]]
        type: Literal["azure_ai_agent"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                tool_descriptions: Optional[list[ToolDescription]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIAgentTargetParam(TypedDict, total=False):
        key "name": Required[str]
        key "tool_descriptions": List[ToolDescriptionParam]
        key "type": Required[Literal["azure_ai_agent"]]
        key "version": str


    class azure.ai.projects.models.AzureAIBenchmarkPreviewEvalRunDataSource(TypedDict, total=False):
        key "input_messages": InputMessagesItemReference
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_benchmark_preview"]]


    class azure.ai.projects.models.AzureAIDataSourceConfig(TypedDict, total=False):
        key "scenario": Required[str]
        key "type": Required[Literal["azure_ai_source"]]


    class azure.ai.projects.models.AzureAIModelTarget(EvaluationTarget, discriminator='azure_ai_model'):
        model: Optional[str]
        sampling_params: Optional[ModelSamplingParams]
        type: Literal["azure_ai_model"]

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[str] = ..., 
                sampling_params: Optional[ModelSamplingParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAIModelTargetParam(TypedDict, total=False):
        key "model": str
        key "sampling_params": ModelSamplingConfigParam
        key "type": Required[Literal["azure_ai_model"]]


    class azure.ai.projects.models.AzureAIResponsesEvalRunDataSource(TypedDict, total=False):
        key "event_configuration_id": str
        key "item_generation_params": Required[ResponseRetrievalItemGenerationParams]
        key "max_runs_hourly": int
        key "type": Required[Literal["azure_ai_responses"]]


    class azure.ai.projects.models.AzureAISearchIndex(Index, discriminator='AzureSearch'):
        connection_name: str
        description: str
        field_mapping: Optional[FieldMapping]
        id: str
        index_name: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.AZURE_SEARCH]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                description: Optional[str] = ..., 
                field_mapping: Optional[FieldMapping] = ..., 
                index_name: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchQueryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC = "semantic"
        SIMPLE = "simple"
        VECTOR = "vector"
        VECTOR_SEMANTIC_HYBRID = "vector_semantic_hybrid"
        VECTOR_SIMPLE_HYBRID = "vector_simple_hybrid"


    class azure.ai.projects.models.AzureAISearchTool(Tool, discriminator='azure_ai_search'):
        azure_ai_search: AzureAISearchToolResource
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchToolResource(_Model):
        indexes: list[AISearchIndexResource]

        @overload
        def __init__(
                self, 
                *, 
                indexes: list[AISearchIndexResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureAISearchToolboxTool(ToolboxTool, discriminator='azure_ai_search'):
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.AZURE_AI_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_search: AzureAISearchToolResource, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionBinding(_Model):
        storage_queue: AzureFunctionStorageQueue
        type: Literal["storage_queue"]

        @overload
        def __init__(
                self, 
                *, 
                storage_queue: AzureFunctionStorageQueue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionDefinition(_Model):
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding

        @overload
        def __init__(
                self, 
                *, 
                function: AzureFunctionDefinitionFunction, 
                input_binding: AzureFunctionBinding, 
                output_binding: AzureFunctionBinding
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionDefinitionFunction(_Model):
        description: Optional[str]
        name: str
        parameters: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionStorageQueue(_Model):
        queue_name: str
        queue_service_endpoint: str

        @overload
        def __init__(
                self, 
                *, 
                queue_name: str, 
                queue_service_endpoint: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureFunctionTool(Tool, discriminator='azure_function'):
        azure_function: AzureFunctionDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.AZURE_FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                azure_function: AzureFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.AzureOpenAIModelConfiguration(RedTeamTargetConfig, discriminator='AzureOpenAIModel'):
        model_deployment_name: str
        type: Literal["AzureOpenAIModel"]

        @overload
        def __init__(
                self, 
                *, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BaseCredentials(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchConfiguration(_Model):
        count: Optional[int]
        freshness: Optional[str]
        instance_name: str
        market: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                instance_name: str, 
                market: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchPreviewTool(Tool, discriminator='bing_custom_search_preview'):
        bing_custom_search_preview: BingCustomSearchToolParameters
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                bing_custom_search_preview: BingCustomSearchToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingCustomSearchToolParameters(_Model):
        search_configurations: list[BingCustomSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingCustomSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingSearchConfiguration(_Model):
        count: Optional[int]
        freshness: Optional[str]
        market: Optional[str]
        project_connection_id: str
        set_lang: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                freshness: Optional[str] = ..., 
                market: Optional[str] = ..., 
                project_connection_id: str, 
                set_lang: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingSearchToolParameters(_Model):
        search_configurations: list[BingGroundingSearchConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                search_configurations: list[BingGroundingSearchConfiguration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BingGroundingTool(Tool, discriminator='bing_grounding'):
        bing_grounding: BingGroundingSearchToolParameters
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.BING_GROUNDING]

        @overload
        def __init__(
                self, 
                *, 
                bing_grounding: BingGroundingSearchToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BlobReference(_Model):
        blob_uri: str
        credential: BlobReferenceSasCredential
        storage_account_arm_id: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str, 
                credential: BlobReferenceSasCredential, 
                storage_account_arm_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BlobReferenceSasCredential(_Model):
        sas_uri: str
        type: Literal["SAS"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.BotServiceAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotService'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BotServiceRbacAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceRbac'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BotServiceTenantAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='BotServiceTenant'):
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationPreviewTool(Tool, discriminator='browser_automation_preview'):
        browser_automation_preview: BrowserAutomationToolParameters
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation_preview: BrowserAutomationToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationPreviewToolboxTool(ToolboxTool, discriminator='browser_automation_preview'):
        browser_automation_preview: BrowserAutomationToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.BROWSER_AUTOMATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                browser_automation_preview: BrowserAutomationToolParameters, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationToolConnectionParameters(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.BrowserAutomationToolParameters(_Model):
        connection: BrowserAutomationToolConnectionParameters

        @overload
        def __init__(
                self, 
                *, 
                connection: BrowserAutomationToolConnectionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CallableToolAllowedCaller(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "direct"
        PROGRAMMATIC = "programmatic"


    class azure.ai.projects.models.CaptureStructuredOutputsTool(Tool, discriminator='capture_structured_outputs'):
        description: Optional[str]
        name: Optional[str]
        outputs: StructuredOutputDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                outputs: StructuredOutputDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ChartCoordinate(_Model):
        size: int
        x: int
        y: int

        @overload
        def __init__(
                self, 
                *, 
                size: int, 
                x: int, 
                y: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ChatSummaryMemoryItem(MemoryItem, discriminator='chat_summary'):
        content: str
        kind: Literal[MemoryItemKind.CHAT_SUMMARY]
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ClusterInsightResult(_Model):
        clusters: list[InsightCluster]
        coordinates: Optional[dict[str, ChartCoordinate]]
        summary: InsightSummary

        @overload
        def __init__(
                self, 
                *, 
                clusters: list[InsightCluster], 
                coordinates: Optional[dict[str, ChartCoordinate]] = ..., 
                summary: InsightSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ClusterTokenUsage(_Model):
        input_token_usage: int
        output_token_usage: int
        total_token_usage: int

        @overload
        def __init__(
                self, 
                *, 
                input_token_usage: int, 
                output_token_usage: int, 
                total_token_usage: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='code'):
        blob_uri: Optional[str]
        code_text: Optional[str]
        data_schema: dict[str, any]
        entry_point: Optional[str]
        image_tag: Optional[str]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.CODE]

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: Optional[str] = ..., 
                code_text: Optional[str] = ..., 
                data_schema: Optional[dict[str, Any]] = ..., 
                entry_point: Optional[str] = ..., 
                image_tag: Optional[str] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeConfiguration(_Model):
        content_hash: Optional[str]
        dependency_resolution: Union[str, CodeDependencyResolution]
        entry_point: list[str]
        runtime: str

        @overload
        def __init__(
                self, 
                *, 
                dependency_resolution: Union[str, CodeDependencyResolution], 
                entry_point: list[str], 
                runtime: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeDependencyResolution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUNDLED = "bundled"
        REMOTE_BUILD = "remote_build"


    class azure.ai.projects.models.CodeInterpreterTool(Tool, discriminator='code_interpreter'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CodeInterpreterToolboxTool(ToolboxTool, discriminator='code_interpreter'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        container: Optional[Union[str, AutoCodeInterpreterToolParam]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.CODE_INTERPRETER]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                container: Optional[Union[str, AutoCodeInterpreterToolParam]] = ..., 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ComparisonFilter(_Model):
        key: str
        type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]
        value: Union[str, float, bool, list[Union[str, float]]]

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                type: Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"], 
                value: Union[str, float, bool, list[Union[str, float]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CompoundFilter(_Model):
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal["and", "or"]

        @overload
        def __init__(
                self, 
                *, 
                filters: list[Union[ComparisonFilter, Any]], 
                type: Literal["and", "or"]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ComputerEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROWSER = "browser"
        LINUX = "linux"
        MAC = "mac"
        UBUNTU = "ubuntu"
        WINDOWS = "windows"


    class azure.ai.projects.models.ComputerTool(Tool, discriminator='computer'):
        type: Literal[ToolType.COMPUTER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ComputerUsePreviewTool(Tool, discriminator='computer_use_preview'):
        display_height: int
        display_width: int
        environment: Union[str, ComputerEnvironment]
        type: Literal[ToolType.COMPUTER_USE_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                display_height: int, 
                display_width: int, 
                environment: Union[str, ComputerEnvironment]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Connection(_Model):
        credentials: BaseCredentials
        id: str
        is_default: bool
        metadata: dict[str, str]
        name: str
        target: str
        type: Union[str, ConnectionType]


    class azure.ai.projects.models.ConnectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        API_KEY = "ApiKey"
        APPLICATION_CONFIGURATION = "AppConfig"
        APPLICATION_INSIGHTS = "AppInsights"
        AZURE_AI_SEARCH = "CognitiveSearch"
        AZURE_BLOB_STORAGE = "AzureBlob"
        AZURE_OPEN_AI = "AzureOpenAI"
        AZURE_STORAGE_ACCOUNT = "AzureStorageAccount"
        COSMOS_DB = "CosmosDB"
        CUSTOM = "CustomKeys"
        REMOTE_TOOL = "RemoteTool_Preview"


    class azure.ai.projects.models.ContainerAutoParam(FunctionShellToolParamEnvironment, discriminator='container_auto'):
        file_ids: Optional[list[str]]
        memory_limit: Optional[Union[str, ContainerMemoryLimit]]
        network_policy: Optional[ContainerNetworkPolicyParam]
        skills: Optional[list[ContainerSkill]]
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]

        @overload
        def __init__(
                self, 
                *, 
                file_ids: Optional[list[str]] = ..., 
                memory_limit: Optional[Union[str, ContainerMemoryLimit]] = ..., 
                network_policy: Optional[ContainerNetworkPolicyParam] = ..., 
                skills: Optional[list[ContainerSkill]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerConfiguration(_Model):
        image: str
        registry_connection_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                image: str, 
                registry_connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerMemoryLimit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMORY_16GB = "16g"
        MEMORY_1GB = "1g"
        MEMORY_4GB = "4g"
        MEMORY_64GB = "64g"


    class azure.ai.projects.models.ContainerNetworkPolicyAllowlistParam(ContainerNetworkPolicyParam, discriminator='allowlist'):
        allowed_domains: list[str]
        domain_secrets: Optional[list[ContainerNetworkPolicyDomainSecretParam]]
        type: Literal[ContainerNetworkPolicyParamType.ALLOWLIST]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: list[str], 
                domain_secrets: Optional[list[ContainerNetworkPolicyDomainSecretParam]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyDisabledParam(ContainerNetworkPolicyParam, discriminator='disabled'):
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyDomainSecretParam(_Model):
        domain: str
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                domain: str, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerNetworkPolicyParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWLIST = "allowlist"
        DISABLED = "disabled"


    class azure.ai.projects.models.ContainerSkill(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ContainerSkillType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INLINE = "inline"
        SKILL_REFERENCE = "skill_reference"


    class azure.ai.projects.models.ContinuousEvaluationRuleAction(EvaluationRuleAction, discriminator='continuousEvaluation'):
        eval_id: str
        max_hourly_runs: Optional[int]
        sampling_rate: Optional[float]
        type: Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                eval_id: str, 
                max_hourly_runs: Optional[int] = ..., 
                sampling_rate: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CosmosDBIndex(Index, discriminator='CosmosDBNoSqlVectorStore'):
        connection_name: str
        container_name: str
        database_name: str
        description: str
        embedding_configuration: EmbeddingConfiguration
        field_mapping: FieldMapping
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.COSMOS_DB]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                container_name: str, 
                database_name: str, 
                description: Optional[str] = ..., 
                embedding_configuration: EmbeddingConfiguration, 
                field_mapping: FieldMapping, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateAsyncResponse(_Model):
        location: Optional[str]
        operation_result: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                operation_result: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateSkillVersionFromFilesBody(_Model):
        default: Optional[bool]
        files: list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[bool] = ..., 
                files: list[FileType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTeamsPhoneExtensionTelephonyBindingRequest(CreateTelephonyBindingRequest, discriminator='teams_phone_extension'):
        connection: str
        label: str
        phone_number: Optional[str]
        provider: Literal[TelephonyProvider.TEAMS_PHONE_EXTENSION]
        resource_account_object_id: str

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                label: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                resource_account_object_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTelephonyBindingRequest(_Model):
        connection: str
        label: Optional[str]
        provider: str

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                label: Optional[str] = ..., 
                provider: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTranscriptionResponseJsonUsage(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CreateTranscriptionResponseJsonUsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DURATION = "duration"
        TOKENS = "tokens"


    class azure.ai.projects.models.CreateTwilioTelephonyBindingRequest(CreateTelephonyBindingRequest, discriminator='twilio'):
        connection: str
        label: str
        phone_number: str
        provider: Literal[TelephonyProvider.TWILIO]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                label: Optional[str] = ..., 
                phone_number: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CredentialType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC_IDENTITY_PREVIEW = "AgenticIdentityToken_Preview"
        API_KEY = "ApiKey"
        CUSTOM = "CustomKeys"
        ENTRA_ID = "AAD"
        NONE = "None"
        SAS = "SAS"


    class azure.ai.projects.models.CronTrigger(Trigger, discriminator='Cron'):
        end_time: Optional[datetime]
        expression: str
        start_time: Optional[datetime]
        time_zone: Optional[str]
        type: Literal[TriggerType.CRON]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                expression: str, 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomCredential(CustomCredentialGenerated, discriminator='CustomKeys'):
        credential_keys: Dict[str, str]
        type: Union[str, CredentialType]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.CustomGrammarFormatParam(CustomToolParamFormat, discriminator='grammar'):
        definition: str
        syntax: Union[str, GrammarSyntax1]
        type: Literal[CustomToolParamFormatType.GRAMMAR]

        @overload
        def __init__(
                self, 
                *, 
                definition: str, 
                syntax: Union[str, GrammarSyntax1]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomRoutineTrigger(RoutineTrigger, discriminator='custom'):
        event_name: Optional[str]
        parameters: dict[str, Any]
        provider: str
        type: Literal[RoutineTriggerType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                event_name: Optional[str] = ..., 
                parameters: dict[str, Any], 
                provider: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomTextFormatParam(CustomToolParamFormat, discriminator='text'):
        type: Literal[CustomToolParamFormatType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParam(Tool, discriminator='custom'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        format: Optional[CustomToolParamFormat]
        name: str
        type: Literal[ToolType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                format: Optional[CustomToolParamFormat] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParamFormat(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.CustomToolParamFormatType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRAMMAR = "grammar"
        TEXT = "text"


    class azure.ai.projects.models.DailyRecurrenceSchedule(RecurrenceSchedule, discriminator='Daily'):
        hours: list[int]
        type: Literal[RecurrenceType.DAILY]

        @overload
        def __init__(
                self, 
                *, 
                hours: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        finished_at: Optional[datetime]
        id: str
        inputs: Optional[DataGenerationJobInputs]
        result: Optional[DataGenerationJobResult]
        status: Union[str, JobStatus]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[DataGenerationJobInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobInputs(_Model):
        name: str
        options: DataGenerationJobOptions
        output_options: Optional[DataGenerationJobOutputOptions]
        scenario: Union[str, DataGenerationJobScenario]
        sources: list[DataGenerationJobSource]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                options: DataGenerationJobOptions, 
                output_options: Optional[DataGenerationJobOutputOptions] = ..., 
                scenario: Union[str, DataGenerationJobScenario], 
                sources: list[DataGenerationJobSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOptions(_Model):
        max_samples: int
        model_options: Optional[DataGenerationModelOptions]
        train_split: Optional[float]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutputOptions(_Model):
        description: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATASET = "dataset"
        FILE = "file"


    class azure.ai.projects.models.DataGenerationJobResult(_Model):
        generated_samples: int
        outputs: Optional[list[DataGenerationJobOutput]]
        token_usage: Optional[DataGenerationTokenUsage]

        @overload
        def __init__(
                self, 
                *, 
                generated_samples: int, 
                outputs: Optional[list[DataGenerationJobOutput]] = ..., 
                token_usage: Optional[DataGenerationTokenUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobScenario(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION = "evaluation"
        REINFORCEMENT_FINETUNING = "reinforcement_finetuning"
        SUPERVISED_FINETUNING = "supervised_finetuning"


    class azure.ai.projects.models.DataGenerationJobSource(_Model):
        description: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        FILE = "file"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.models.DataGenerationJobType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIMPLE_QNA = "simple_qna"
        SIMULATION_SEED = "simulation_seed"
        TOOL_USE = "tool_use"
        TRACES = "traces"


    class azure.ai.projects.models.DataGenerationModelOptions(_Model):
        model: str

        @overload
        def __init__(
                self, 
                *, 
                model: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DataGenerationTokenUsage(_Model):
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int


    class azure.ai.projects.models.DatasetCredential(_Model):
        blob_reference: BlobReference

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetDataGenerationJobOutput(DataGenerationJobOutput, discriminator='dataset'):
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        tags: Optional[dict[str, str]]
        type: Literal[DataGenerationJobOutputType.DATASET]
        version: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='dataset'):
        description: Optional[str]
        name: str
        type: Literal[EvaluatorGenerationJobSourceType.DATASET]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetGenerationLROPoller(LROPoller[DataGenerationJobResult]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[DataGenerationJobResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> DatasetGenerationLROPoller: ...


    class azure.ai.projects.models.DatasetReference(_Model):
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DatasetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        URI_FILE = "uri_file"
        URI_FOLDER = "uri_folder"


    class azure.ai.projects.models.DatasetVersion(_Model):
        connection_name: Optional[str]
        data_uri: str
        description: Optional[str]
        id: Optional[str]
        is_reference: Optional[bool]
        name: str
        tags: Optional[dict[str, str]]
        type: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.ai.projects.models.DeleteAgentResponse(_Model):
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


    class azure.ai.projects.models.DeleteAgentVersionResponse(_Model):
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


    class azure.ai.projects.models.DeleteMemoryResult(_Model):
        deleted: bool
        memory_id: str
        object: Literal[MemoryStoreObjectType.MEMORY_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                memory_id: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteMemoryStoreResult(_Model):
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE_DELETED]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteSkillResult(_Model):
        deleted: bool
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeleteSkillVersionResult(_Model):
        deleted: bool
        id: str
        name: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                id: str, 
                name: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Deployment(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODEL_DEPLOYMENT = "ModelDeployment"


    class azure.ai.projects.models.DigitalWorkerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        M365 = "m365"


    class azure.ai.projects.models.Dimension(_Model):
        always_applicable: Optional[bool]
        description: str
        id: str
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                always_applicable: Optional[bool] = ..., 
                description: str, 
                id: str, 
                weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.DispatchRoutineResult(_Model):
        action_correlation_id: Optional[str]
        dispatch_id: Optional[str]
        task_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_correlation_id: Optional[str] = ..., 
                dispatch_id: Optional[str] = ..., 
                task_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EmbeddingConfiguration(_Model):
        embedding_field: str
        model_deployment_name: str

        @overload
        def __init__(
                self, 
                *, 
                embedding_field: str, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EmptyModelParam(_Model):


    class azure.ai.projects.models.EndpointBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='endpoint'):
        connection_name: str
        data_schema: dict[str, any]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.ENDPOINT]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: str, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraAuthorizationScheme(AgentEndpointAuthorizationScheme, discriminator='Entra'):
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EntraIDCredentials(BaseCredentials, discriminator='AAD'):
        type: Literal[CredentialType.ENTRA_ID]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalCsvFileIdSource(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Literal["file_id"]]


    class azure.ai.projects.models.EvalCsvRunDataSource(TypedDict, total=False):
        key "source": Required[EvalCsvFileIdSource]
        key "type": Required[Literal["csv"]]


    class azure.ai.projects.models.EvalResult(_Model):
        name: str
        passed: bool
        score: float
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                passed: bool, 
                score: float, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultCompareItem(_Model):
        delta_estimate: float
        p_value: float
        treatment_effect: Union[str, TreatmentEffectType]
        treatment_run_id: str
        treatment_run_summary: EvalRunResultSummary

        @overload
        def __init__(
                self, 
                *, 
                delta_estimate: float, 
                p_value: float, 
                treatment_effect: Union[str, TreatmentEffectType], 
                treatment_run_id: str, 
                treatment_run_summary: EvalRunResultSummary
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultComparison(_Model):
        baseline_run_summary: EvalRunResultSummary
        compare_items: list[EvalRunResultCompareItem]
        evaluator: str
        metric: str
        testing_criteria: str

        @overload
        def __init__(
                self, 
                *, 
                baseline_run_summary: EvalRunResultSummary, 
                compare_items: list[EvalRunResultCompareItem], 
                evaluator: str, 
                metric: str, 
                testing_criteria: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvalRunResultSummary(_Model):
        average: float
        run_id: str
        sample_count: int
        standard_deviation: float

        @overload
        def __init__(
                self, 
                *, 
                average: float, 
                run_id: str, 
                sample_count: int, 
                standard_deviation: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationComparisonInsightRequest(InsightRequest, discriminator='EvaluationComparison'):
        baseline_run_id: str
        eval_id: str
        treatment_run_ids: list[str]
        type: Literal[InsightType.EVALUATION_COMPARISON]

        @overload
        def __init__(
                self, 
                *, 
                baseline_run_id: str, 
                eval_id: str, 
                treatment_run_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationComparisonInsightResult(InsightResult, discriminator='EvaluationComparison'):
        comparisons: list[EvalRunResultComparison]
        method: str
        type: Literal[InsightType.EVALUATION_COMPARISON]

        @overload
        def __init__(
                self, 
                *, 
                comparisons: list[EvalRunResultComparison], 
                method: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONVERSATION = "conversation"
        TURN = "turn"


    class azure.ai.projects.models.EvaluationResultSample(InsightSample, discriminator='EvaluationResultSample'):
        correlation_info: dict[str, any]
        evaluation_result: EvalResult
        features: dict[str, any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]

        @overload
        def __init__(
                self, 
                *, 
                correlation_info: dict[str, Any], 
                evaluation_result: EvalResult, 
                features: dict[str, Any], 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRule(_Model):
        action: EvaluationRuleAction
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        event_type: Union[str, EvaluationRuleEventType]
        filter: Optional[EvaluationRuleFilter]
        id: str
        system_data: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                action: EvaluationRuleAction, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: bool, 
                event_type: Union[str, EvaluationRuleEventType], 
                filter: Optional[EvaluationRuleFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRuleAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS_EVALUATION = "continuousEvaluation"
        HUMAN_EVALUATION_PREVIEW = "humanEvaluationPreview"


    class azure.ai.projects.models.EvaluationRuleEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "manual"
        RESPONSE_COMPLETED = "responseCompleted"


    class azure.ai.projects.models.EvaluationRuleFilter(_Model):
        agent_name: str

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRunClusterInsightRequest(InsightRequest, discriminator='EvaluationRunClusterInsight'):
        eval_id: str
        model_configuration: Optional[InsightModelConfiguration]
        run_ids: list[str]
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                eval_id: str, 
                model_configuration: Optional[InsightModelConfiguration] = ..., 
                run_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationRunClusterInsightResult(InsightResult, discriminator='EvaluationRunClusterInsight'):
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                cluster_insight: ClusterInsightResult
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationScheduleTask(ScheduleTask, discriminator='Evaluation'):
        configuration: dict[str, str]
        eval_id: str
        eval_run: dict[str, Any]
        type: Literal[ScheduleTaskType.EVALUATION]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                eval_id: str, 
                eval_run: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTarget(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomy(_Model):
        description: Optional[str]
        id: Optional[str]
        name: str
        properties: Optional[dict[str, str]]
        tags: Optional[dict[str, str]]
        taxonomy_categories: Optional[list[TaxonomyCategory]]
        taxonomy_input: EvaluationTaxonomyInput
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                taxonomy_categories: Optional[list[TaxonomyCategory]] = ..., 
                taxonomy_input: EvaluationTaxonomyInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomyInput(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluationTaxonomyInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        POLICY = "policy"


    class azure.ai.projects.models.EvaluatorCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTS = "agents"
        QUALITY = "quality"
        SAFETY = "safety"


    class azure.ai.projects.models.EvaluatorCredentialRequest(_Model):
        blob_uri: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorDefinition(_Model):
        data_schema: Optional[dict[str, Any]]
        init_parameters: Optional[dict[str, Any]]
        metrics: Optional[dict[str, EvaluatorMetric]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE = "code"
        ENDPOINT = "endpoint"
        OPENAI_GRADERS = "openai_graders"
        PROMPT = "prompt"
        PROMPT_AND_CODE = "prompt_and_code"
        RUBRIC = "rubric"
        SERVICE = "service"


    class azure.ai.projects.models.EvaluatorGenerationArtifacts(_Model):
        dataset: DatasetReference
        kinds: list[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset: DatasetReference, 
                kinds: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationInputs(_Model):
        evaluator_description: Optional[str]
        evaluator_display_name: Optional[str]
        evaluator_name: str
        model: str
        sources: list[EvaluatorGenerationJobSource]

        @overload
        def __init__(
                self, 
                *, 
                evaluator_description: Optional[str] = ..., 
                evaluator_display_name: Optional[str] = ..., 
                evaluator_name: str, 
                model: str, 
                sources: list[EvaluatorGenerationJobSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJob(_Model):
        created_at: datetime
        error: Optional[ApiError]
        finished_at: Optional[datetime]
        id: str
        input_quality_warnings: Optional[list[RubricGenerationInputQualityWarning]]
        inputs: Optional[EvaluatorGenerationInputs]
        result: Optional[EvaluatorVersion]
        status: Union[str, JobStatus]
        usage: Optional[EvaluatorGenerationTokenUsage]

        @overload
        def __init__(
                self, 
                *, 
                inputs: Optional[EvaluatorGenerationInputs] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJobSource(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorGenerationJobSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        DATASET = "dataset"
        PROMPT = "prompt"
        TRACES = "traces"


    class azure.ai.projects.models.EvaluatorGenerationLROPoller(LROPoller[EvaluatorVersion]):
        property details: Mapping[str, Any]    # Read-only

        def __init__(
                self, 
                client: Any, 
                initial_response: Any, 
                deserialization_callback: Any, 
                polling_method: Any
            ) -> None: ...

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[EvaluatorVersion], 
                continuation_token: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationLROPoller: ...


    class azure.ai.projects.models.EvaluatorGenerationTokenUsage(_Model):
        input_tokens: int
        output_tokens: int
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                input_tokens: int, 
                output_tokens: int, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorMetric(_Model):
        desirable_direction: Optional[Union[str, EvaluatorMetricDirection]]
        is_primary: Optional[bool]
        max_value: Optional[float]
        min_value: Optional[float]
        threshold: Optional[float]
        type: Optional[Union[str, EvaluatorMetricType]]

        @overload
        def __init__(
                self, 
                *, 
                desirable_direction: Optional[Union[str, EvaluatorMetricDirection]] = ..., 
                is_primary: Optional[bool] = ..., 
                max_value: Optional[float] = ..., 
                min_value: Optional[float] = ..., 
                threshold: Optional[float] = ..., 
                type: Optional[Union[str, EvaluatorMetricType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.EvaluatorMetricDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECREASE = "decrease"
        INCREASE = "increase"
        NEUTRAL = "neutral"


    class azure.ai.projects.models.EvaluatorMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        CONTINUOUS = "continuous"
        ORDINAL = "ordinal"


    class azure.ai.projects.models.EvaluatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILT_IN = "builtin"
        CUSTOM = "custom"


    class azure.ai.projects.models.EvaluatorVersion(_Model):
        categories: list[Union[str, EvaluatorCategory]]
        created_at: datetime
        created_by: str
        definition: EvaluatorDefinition
        description: Optional[str]
        display_name: Optional[str]
        evaluator_type: Union[str, EvaluatorType]
        generation_artifacts: Optional[EvaluatorGenerationArtifacts]
        generation_job_id: Optional[str]
        id: Optional[str]
        metadata: Optional[dict[str, str]]
        modified_at: datetime
        name: str
        supported_evaluation_levels: Optional[list[Union[str, EvaluationLevel]]]
        tags: Optional[dict[str, str]]
        version: str
        warnings: Optional[list[Union[str, GenerationWarningType]]]

        @overload
        def __init__(
                self, 
                *, 
                categories: list[Union[str, EvaluatorCategory]], 
                definition: EvaluatorDefinition, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluator_type: Union[str, EvaluatorType], 
                metadata: Optional[dict[str, str]] = ..., 
                supported_evaluation_levels: Optional[list[Union[str, EvaluationLevel]]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ExternalAgentDefinition(AgentDefinition, discriminator='external'):
        kind: Literal[AgentKind.EXTERNAL]
        otel_agent_id: Optional[str]
        rai_config: RaiConfig

        @overload
        def __init__(
                self, 
                *, 
                otel_agent_id: Optional[str] = ..., 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricDataAgentToolParameters(_Model):
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricIQPreviewTool(Tool, discriminator='fabric_iq_preview'):
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        server_url: Optional[str]
        type: Literal[ToolType.FABRIC_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ..., 
                server_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FabricIQPreviewToolboxTool(ToolboxTool, discriminator='fabric_iq_preview'):
        description: str
        name: str
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        server_url: Optional[str]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FABRIC_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ..., 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FieldMapping(_Model):
        content_fields: list[str]
        filepath_field: Optional[str]
        metadata_fields: Optional[list[str]]
        title_field: Optional[str]
        url_field: Optional[str]
        vector_fields: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                content_fields: list[str], 
                filepath_field: Optional[str] = ..., 
                metadata_fields: Optional[list[str]] = ..., 
                title_field: Optional[str] = ..., 
                url_field: Optional[str] = ..., 
                vector_fields: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDataGenerationJobOutput(DataGenerationJobOutput, discriminator='file'):
        filename: str
        id: str
        type: Literal[DataGenerationJobOutputType.FILE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDataGenerationJobSource(DataGenerationJobSource, discriminator='file'):
        description: str
        id: str
        type: Literal[DataGenerationJobSourceType.FILE]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileDatasetVersion(DatasetVersion, discriminator='uri_file'):
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FILE]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileSearchTool(Tool, discriminator='file_search'):
        description: Optional[str]
        filters: Optional[Filters]
        max_num_results: Optional[int]
        name: Optional[str]
        ranking_options: Optional[RankingOptions]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.FILE_SEARCH]
        vector_store_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                filters: Optional[Filters] = ..., 
                max_num_results: Optional[int] = ..., 
                name: Optional[str] = ..., 
                ranking_options: Optional[RankingOptions] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                vector_store_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FileSearchToolboxTool(ToolboxTool, discriminator='file_search'):
        description: str
        filters: Optional[Filters]
        max_num_results: Optional[int]
        name: str
        ranking_options: Optional[RankingOptions]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FILE_SEARCH]
        vector_store_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                filters: Optional[Filters] = ..., 
                max_num_results: Optional[int] = ..., 
                name: Optional[str] = ..., 
                ranking_options: Optional[RankingOptions] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                vector_store_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FixedRatioVersionSelectionRule(VersionSelectionRule, discriminator='FixedRatio'):
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


    class azure.ai.projects.models.FolderDatasetVersion(DatasetVersion, discriminator='uri_folder'):
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FOLDER]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                data_uri: str, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FoundryModelArtifactProfileCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_ONLY = "DataOnly"
        RUNTIME_DEPENDENT = "RuntimeDependent"
        UNKNOWN = "Unknown"


    class azure.ai.projects.models.FoundryModelArtifactProfileSignal(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_PYTHON_CODE = "CustomPythonCode"
        DYNAMIC_OPS = "DynamicOps"
        NATIVE_BINARY = "NativeBinary"
        PICKLE_DESERIALIZATION = "PickleDeserialization"
        UNKNOWN_FORMAT = "UnknownFormat"


    class azure.ai.projects.models.FoundryModelSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL_UPLOAD = "LocalUpload"
        TRAINING_JOB = "TrainingJob"


    class azure.ai.projects.models.FoundryModelWarning(_Model):
        code: Optional[Union[str, FoundryModelWarningCode]]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[Union[str, FoundryModelWarningCode]] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FoundryModelWarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNTIME_DEPENDENT_ARTIFACT = "RuntimeDependentArtifact"
        UNCLASSIFIED_ARTIFACT = "UnclassifiedArtifact"


    class azure.ai.projects.models.FoundryModelWeightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DRAFT_MODEL = "DraftModel"
        FULL_WEIGHT = "FullWeight"
        LO_RA = "LoRA"


    class azure.ai.projects.models.FunctionShellToolParam(Tool, discriminator='shell'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        description: Optional[str]
        environment: Optional[FunctionShellToolParamEnvironment]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.SHELL]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                description: Optional[str] = ..., 
                environment: Optional[FunctionShellToolParamEnvironment] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentContainerReferenceParam(FunctionShellToolParamEnvironment, discriminator='container_reference'):
        container_id: str
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentLocalEnvironmentParam(FunctionShellToolParamEnvironment, discriminator='local'):
        skills: Optional[list[LocalSkillParam]]
        type: Literal[FunctionShellToolParamEnvironmentType.LOCAL]

        @overload
        def __init__(
                self, 
                *, 
                skills: Optional[list[LocalSkillParam]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionShellToolParamEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_AUTO = "container_auto"
        CONTAINER_REFERENCE = "container_reference"
        LOCAL = "local"


    class azure.ai.projects.models.FunctionTool(Tool, discriminator='function'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        output_schema: Optional[dict[str, Any]]
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                output_schema: Optional[dict[str, Any]] = ..., 
                parameters: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.FunctionToolParam(_Model):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        defer_loading: Optional[bool]
        description: Optional[str]
        name: str
        output_schema: Optional[dict[str, Any]]
        parameters: Optional[EmptyModelParam]
        strict: Optional[bool]
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                output_schema: Optional[dict[str, Any]] = ..., 
                parameters: Optional[EmptyModelParam] = ..., 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.GenerateVoiceAgentRequest(_Model):
        description: Optional[str]
        draft: Optional[bool]
        goal: Optional[str]
        kind: Literal[AgentKind.VOICE]
        model: Optional[str]
        model_type: Optional[Union[str, VoiceModelType]]
        name: str
        tools: Optional[list[VoiceAgentTool]]
        use_case: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                goal: Optional[str] = ..., 
                kind: Literal[AgentKind.VOICE], 
                model: Optional[str] = ..., 
                model_type: Optional[Union[str, VoiceModelType]] = ..., 
                name: str, 
                tools: Optional[list[VoiceAgentTool]] = ..., 
                use_case: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.GenerationWarningType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INPUT_QUALITY = "input_quality"


    class azure.ai.projects.models.GitHubIssueEvent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSED = "closed"
        OPENED = "opened"


    class azure.ai.projects.models.GitHubIssueRoutineTrigger(RoutineTrigger, discriminator='github_issue'):
        connection_id: str
        issue_event: Union[str, GitHubIssueEvent]
        owner: str
        repository: str
        type: Literal[RoutineTriggerType.GITHUB_ISSUE]

        @overload
        def __init__(
                self, 
                *, 
                connection_id: str, 
                issue_event: Union[str, GitHubIssueEvent], 
                owner: str, 
                repository: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.GrammarSyntax1(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LARK = "lark"
        REGEX = "regex"


    class azure.ai.projects.models.HeaderTelemetryEndpointAuth(TelemetryEndpointAuth, discriminator='header'):
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]

        @overload
        def __init__(
                self, 
                *, 
                header_name: str, 
                secret_id: str, 
                secret_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HostedAgentDefinition(AgentDefinition, discriminator='hosted'):
        code_configuration: Optional[CodeConfiguration]
        container_configuration: Optional[ContainerConfiguration]
        cpu: str
        environment_variables: Optional[dict[str, str]]
        kind: Literal[AgentKind.HOSTED]
        memory: str
        protocol_versions: Optional[list[ProtocolVersionRecord]]
        rai_config: RaiConfig
        session_configuration: Optional[SessionConfiguration]
        telemetry_config: Optional[TelemetryConfig]

        @overload
        def __init__(
                self, 
                *, 
                code_configuration: Optional[CodeConfiguration] = ..., 
                container_configuration: Optional[ContainerConfiguration] = ..., 
                cpu: str, 
                environment_variables: Optional[dict[str, str]] = ..., 
                memory: str, 
                protocol_versions: Optional[list[ProtocolVersionRecord]] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                session_configuration: Optional[SessionConfiguration] = ..., 
                telemetry_config: Optional[TelemetryConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HourlyRecurrenceSchedule(RecurrenceSchedule, discriminator='Hourly'):
        type: Literal[RecurrenceType.HOURLY]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HumanEvaluationPreviewRuleAction(EvaluationRuleAction, discriminator='humanEvaluationPreview'):
        template_id: str
        type: Literal[EvaluationRuleActionType.HUMAN_EVALUATION_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                template_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.HybridSearchOptions(_Model):
        embedding_weight: float
        text_weight: float

        @overload
        def __init__(
                self, 
                *, 
                embedding_weight: float, 
                text_weight: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ImageGenAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        EDIT = "edit"
        GENERATE = "generate"


    class azure.ai.projects.models.ImageGenTool(Tool, discriminator='image_generation'):
        action: Optional[Union[str, ImageGenAction]]
        background: Optional[Literal["transparent", "opaque", "auto"]]
        description: Optional[str]
        input_fidelity: Optional[Union[str, InputFidelity]]
        input_image_mask: Optional[ImageGenToolInputImageMask]
        model: Optional[Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]]
        moderation: Optional[Literal["auto", "low"]]
        name: Optional[str]
        output_compression: Optional[int]
        output_format: Optional[Literal["png", "webp", "jpeg"]]
        partial_images: Optional[int]
        quality: Optional[Literal["low", "medium", "high", "auto"]]
        size: Optional[Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.IMAGE_GENERATION]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ImageGenAction]] = ..., 
                background: Optional[Literal[transparent, opaque, auto]] = ..., 
                description: Optional[str] = ..., 
                input_fidelity: Optional[Union[str, InputFidelity]] = ..., 
                input_image_mask: Optional[ImageGenToolInputImageMask] = ..., 
                model: Optional[Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]] = ..., 
                moderation: Optional[Literal[auto, low]] = ..., 
                name: Optional[str] = ..., 
                output_compression: Optional[int] = ..., 
                output_format: Optional[Literal[png, webp, jpeg]] = ..., 
                partial_images: Optional[int] = ..., 
                quality: Optional[Literal[low, medium, high, auto]] = ..., 
                size: Optional[Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ImageGenToolInputImageMask(_Model):
        file_id: Optional[str]
        image_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ..., 
                image_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Index(_Model):
        description: Optional[str]
        id: Optional[str]
        name: str
        tags: Optional[dict[str, str]]
        type: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.IndexType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEARCH = "AzureSearch"
        COSMOS_DB = "CosmosDBNoSqlVectorStore"
        MANAGED_AZURE_SEARCH = "ManagedAzureSearch"


    class azure.ai.projects.models.InlineSkillParam(ContainerSkill, discriminator='inline'):
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[ContainerSkillType.INLINE]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                source: InlineSkillSourceParam
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InlineSkillSourceParam(_Model):
        data: str
        media_type: Literal["application/zip"]
        type: Literal["base64"]

        @overload
        def __init__(
                self, 
                *, 
                data: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InputFidelity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"


    class azure.ai.projects.models.Insight(_Model):
        display_name: str
        insight_id: str
        metadata: InsightsMetadata
        request: InsightRequest
        result: Optional[InsightResult]
        state: Union[str, OperationState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: str, 
                request: InsightRequest
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightCluster(_Model):
        description: str
        id: str
        label: str
        samples: Optional[list[InsightSample]]
        sub_clusters: Optional[list[InsightCluster]]
        suggestion: str
        suggestion_title: str
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                id: str, 
                label: str, 
                samples: Optional[list[InsightSample]] = ..., 
                sub_clusters: Optional[list[InsightCluster]] = ..., 
                suggestion: str, 
                suggestion_title: str, 
                weight: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightModelConfiguration(_Model):
        model_deployment_name: str

        @overload
        def __init__(
                self, 
                *, 
                model_deployment_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightRequest(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightResult(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightSample(_Model):
        correlation_info: dict[str, Any]
        features: dict[str, Any]
        id: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                correlation_info: dict[str, Any], 
                features: dict[str, Any], 
                id: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightScheduleTask(ScheduleTask, discriminator='Insight'):
        configuration: dict[str, str]
        insight: Insight
        type: Literal[ScheduleTaskType.INSIGHT]

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                insight: Insight
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightSummary(_Model):
        method: str
        sample_count: int
        unique_cluster_count: int
        unique_subcluster_count: int
        usage: ClusterTokenUsage

        @overload
        def __init__(
                self, 
                *, 
                method: str, 
                sample_count: int, 
                unique_cluster_count: int, 
                unique_subcluster_count: int, 
                usage: ClusterTokenUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InsightType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_CLUSTER_INSIGHT = "AgentClusterInsight"
        EVALUATION_COMPARISON = "EvaluationComparison"
        EVALUATION_RUN_CLUSTER_INSIGHT = "EvaluationRunClusterInsight"


    class azure.ai.projects.models.InsightsMetadata(_Model):
        completed_at: Optional[datetime]
        created_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                completed_at: Optional[datetime] = ..., 
                created_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvocationsProtocolConfiguration(_Model):


    class azure.ai.projects.models.InvocationsWsProtocolConfiguration(_Model):


    class azure.ai.projects.models.InvokeAgentInvocationsApiDispatchPayload(RoutineDispatchPayload, discriminator='invoke_agent_invocations_api'):
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_INVOCATIONS_API]

        @overload
        def __init__(
                self, 
                *, 
                input: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentInvocationsApiRoutineAction(RoutineAction, discriminator='invoke_agent_invocations_api'):
        agent_endpoint_id: Optional[str]
        agent_name: Optional[str]
        input: Optional[Any]
        session_id: Optional[str]
        type: Literal[RoutineActionType.INVOKE_AGENT_INVOCATIONS_API]

        @overload
        def __init__(
                self, 
                *, 
                agent_endpoint_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                input: Optional[Any] = ..., 
                session_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentResponsesApiDispatchPayload(RoutineDispatchPayload, discriminator='invoke_agent_responses_api'):
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_RESPONSES_API]

        @overload
        def __init__(
                self, 
                *, 
                input: Any
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.InvokeAgentResponsesApiRoutineAction(RoutineAction, discriminator='invoke_agent_responses_api'):
        agent_endpoint_id: Optional[str]
        agent_name: Optional[str]
        conversation: Optional[str]
        input: Optional[Any]
        type: Literal[RoutineActionType.INVOKE_AGENT_RESPONSES_API]

        @overload
        def __init__(
                self, 
                *, 
                agent_endpoint_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                conversation: Optional[str] = ..., 
                input: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.JobStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        QUEUED = "queued"
        SUCCEEDED = "succeeded"


    class azure.ai.projects.models.LocalShellToolParam(Tool, discriminator='local_shell'):
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.LOCAL_SHELL]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.LocalSkillParam(_Model):
        description: str
        name: str
        path: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.LogProbProperties(_Model):
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


    class azure.ai.projects.models.LoraConfig(_Model):
        alpha: Optional[int]
        dropout: Optional[float]
        rank: Optional[int]
        target_modules: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                alpha: Optional[int] = ..., 
                dropout: Optional[float] = ..., 
                rank: Optional[int] = ..., 
                target_modules: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MCPListToolsTool(_Model):
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


    class azure.ai.projects.models.MCPListToolsToolAnnotations(_Model):


    class azure.ai.projects.models.MCPListToolsToolInputSchema(_Model):


    class azure.ai.projects.models.MCPTool(Tool, discriminator='mcp'):
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


    class azure.ai.projects.models.MCPToolFilter(_Model):
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


    class azure.ai.projects.models.MCPToolRequireApproval(_Model):
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


    class azure.ai.projects.models.MCPToolboxTool(ToolboxTool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        connector_id: Optional[Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]]
        defer_loading: Optional[bool]
        description: str
        headers: Optional[dict[str, str]]
        name: str
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: dict[str, ToolConfig]
        tunnel_id: Optional[str]
        type: Literal[ToolboxToolType.MCP]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                connector_id: Optional[Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams, connector_outlookcalendar, connector_outlookemail, connector_sharepoint]] = ..., 
                defer_loading: Optional[bool] = ..., 
                description: Optional[str] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                name: Optional[str] = ..., 
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


    class azure.ai.projects.models.ManagedAgentIdentityBlueprintReference(AgentBlueprintReference, discriminator='ManagedAgentIdentityBlueprint'):
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


    class azure.ai.projects.models.ManagedAzureAISearchIndex(Index, discriminator='ManagedAzureSearch'):
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.MANAGED_AZURE_SEARCH]
        vector_store_id: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                vector_store_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.McpProtocolConfiguration(_Model):


    class azure.ai.projects.models.MemoryItem(_Model):
        content: str
        kind: str
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                kind: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryItemKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHAT_SUMMARY = "chat_summary"
        PROCEDURAL = "procedural"
        USER_PROFILE = "user_profile"


    class azure.ai.projects.models.MemoryOperation(_Model):
        kind: Union[str, MemoryOperationKind]
        memory_item: MemoryItem

        @overload
        def __init__(
                self, 
                *, 
                kind: Union[str, MemoryOperationKind], 
                memory_item: MemoryItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "create"
        DELETE = "delete"
        UPDATE = "update"


    class azure.ai.projects.models.MemorySearchItem(_Model):
        memory_item: MemoryItem

        @overload
        def __init__(
                self, 
                *, 
                memory_item: MemoryItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemorySearchOptions(_Model):
        max_memories: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                max_memories: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemorySearchPreviewTool(Tool, discriminator='memory_search_preview'):
        memory_store_name: str
        scope: str
        search_options: Optional[MemorySearchOptions]
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                memory_store_name: str, 
                scope: str, 
                search_options: Optional[MemorySearchOptions] = ..., 
                update_delay: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefaultDefinition(MemoryStoreDefinition, discriminator='default'):
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: Optional[MemoryStoreDefaultOptions]

        @overload
        def __init__(
                self, 
                *, 
                chat_model: str, 
                embedding_model: str, 
                options: Optional[MemoryStoreDefaultOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefaultOptions(_Model):
        chat_summary_enabled: bool
        default_ttl_seconds: Optional[timedelta]
        procedural_memory_enabled: Optional[bool]
        user_profile_details: Optional[str]
        user_profile_enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                chat_summary_enabled: bool, 
                default_ttl_seconds: Optional[timedelta] = ..., 
                procedural_memory_enabled: Optional[bool] = ..., 
                user_profile_details: Optional[str] = ..., 
                user_profile_enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDefinition(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDeleteScopeResult(_Model):
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_SCOPE_DELETED]
        scope: str

        @overload
        def __init__(
                self, 
                *, 
                deleted: bool, 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE_SCOPE_DELETED], 
                scope: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreDetails(_Model):
        created_at: datetime
        definition: MemoryStoreDefinition
        description: Optional[str]
        id: str
        metadata: Optional[dict[str, str]]
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE]
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                object: Literal[MemoryStoreObjectType.MEMORY_STORE], 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"


    class azure.ai.projects.models.MemoryStoreObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MEMORY_DELETED = "memory_store.item.deleted"
        MEMORY_STORE = "memory_store"
        MEMORY_STORE_DELETED = "memory_store.deleted"
        MEMORY_STORE_SCOPE_DELETED = "memory_store.scope.deleted"


    class azure.ai.projects.models.MemoryStoreOperationUsage(_Model):
        embedding_tokens: int
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                embedding_tokens: int, 
                input_tokens: int, 
                input_tokens_details: ResponseUsageInputTokensDetails, 
                output_tokens: int, 
                output_tokens_details: ResponseUsageOutputTokensDetails, 
                total_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreSearchResult(_Model):
        memories: list[MemorySearchItem]
        search_id: str
        usage: MemoryStoreOperationUsage

        @overload
        def __init__(
                self, 
                *, 
                memories: list[MemorySearchItem], 
                search_id: str, 
                usage: MemoryStoreOperationUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateCompletedResult(_Model):
        memory_operations: list[MemoryOperation]
        usage: MemoryStoreOperationUsage

        @overload
        def __init__(
                self, 
                *, 
                memory_operations: list[MemoryOperation], 
                usage: MemoryStoreOperationUsage
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateResult(_Model):
        error: Optional[ApiError]
        result: Optional[MemoryStoreUpdateCompletedResult]
        status: Union[str, MemoryStoreUpdateStatus]
        superseded_by: Optional[str]
        update_id: str

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ApiError] = ..., 
                result: Optional[MemoryStoreUpdateCompletedResult] = ..., 
                status: Union[str, MemoryStoreUpdateStatus], 
                superseded_by: Optional[str] = ..., 
                update_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MemoryStoreUpdateStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        QUEUED = "queued"
        SUPERSEDED = "superseded"


    class azure.ai.projects.models.Metadata(_Model):


    class azure.ai.projects.models.Microsoft365PermissionScopes(_Model):
        resource_app_id: str
        scopes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_app_id: str, 
                scopes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Microsoft365PublishDefaults(_Model):
        agent_display_name: Optional[str]
        agent_name: Optional[str]
        app_publish_scope: Optional[Union[str, Microsoft365PublishScope]]
        app_registration_client_id: Optional[str]
        app_version: Optional[str]
        bot_service_arm_id: Optional[str]
        developer_name: Optional[str]
        developer_website_url: Optional[str]
        full_description: Optional[str]
        privacy_url: Optional[str]
        recommended_next_app_version: Optional[str]
        short_description: Optional[str]
        teams_app_id: Optional[str]
        terms_of_use_url: Optional[str]
        title_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_display_name: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                app_publish_scope: Optional[Union[str, Microsoft365PublishScope]] = ..., 
                app_registration_client_id: Optional[str] = ..., 
                app_version: Optional[str] = ..., 
                bot_service_arm_id: Optional[str] = ..., 
                developer_name: Optional[str] = ..., 
                developer_website_url: Optional[str] = ..., 
                full_description: Optional[str] = ..., 
                privacy_url: Optional[str] = ..., 
                recommended_next_app_version: Optional[str] = ..., 
                short_description: Optional[str] = ..., 
                teams_app_id: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                title_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Microsoft365PublishResult(_Model):
        teams_app_id: Optional[str]
        title_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                teams_app_id: Optional[str] = ..., 
                title_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Microsoft365PublishScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERSONAL = "Personal"
        SHARED = "Shared"
        TENANT = "Tenant"


    class azure.ai.projects.models.MicrosoftFabricPreviewTool(Tool, discriminator='fabric_dataagent_preview'):
        fabric_dataagent_preview: FabricDataAgentToolParameters
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                fabric_dataagent_preview: FabricDataAgentToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelCredentialRequest(_Model):
        blob_uri: str

        @overload
        def __init__(
                self, 
                *, 
                blob_uri: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelDeployment(Deployment, discriminator='ModelDeployment'):
        capabilities: dict[str, str]
        connection_name: Optional[str]
        model_name: str
        model_publisher: str
        model_version: str
        name: str
        sku: ModelDeploymentSku
        type: Literal[DeploymentType.MODEL_DEPLOYMENT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelDeploymentSku(_Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: str

        @overload
        def __init__(
                self, 
                *, 
                capacity: int, 
                family: str, 
                name: str, 
                size: str, 
                tier: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelPendingUploadRequest(_Model):
        connection_name: Optional[str]
        pending_upload_id: Optional[str]
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelPendingUploadResponse(_Model):
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference, 
                pending_upload_id: str, 
                pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelSamplingConfigParam(TypedDict, total=False):
        key "max_completion_tokens": int
        key "seed": int
        key "temperature": float
        key "top_p": float


    class azure.ai.projects.models.ModelSamplingParams(_Model):
        max_completion_tokens: Optional[int]
        seed: Optional[int]
        temperature: Optional[float]
        top_p: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                max_completion_tokens: Optional[int] = ..., 
                seed: Optional[int] = ..., 
                temperature: Optional[float] = ..., 
                top_p: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelSourceData(_Model):
        job_id: Optional[str]
        source_type: Optional[Union[str, FoundryModelSourceType]]

        @overload
        def __init__(
                self, 
                *, 
                job_id: Optional[str] = ..., 
                source_type: Optional[Union[str, FoundryModelSourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ModelVersion(_Model):
        artifact_profile: Optional[ArtifactProfile]
        base_model: Optional[str]
        blob_uri: str
        description: Optional[str]
        id: Optional[str]
        lora_config: Optional[LoraConfig]
        name: str
        source: Optional[ModelSourceData]
        tags: Optional[dict[str, str]]
        version: str
        warnings: Optional[list[FoundryModelWarning]]
        weight_type: Optional[Union[str, FoundryModelWeightType]]

        @overload
        def __init__(
                self, 
                *, 
                base_model: Optional[str] = ..., 
                blob_uri: str, 
                description: Optional[str] = ..., 
                lora_config: Optional[LoraConfig] = ..., 
                source: Optional[ModelSourceData] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                weight_type: Optional[Union[str, FoundryModelWeightType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.MonthlyRecurrenceSchedule(RecurrenceSchedule, discriminator='Monthly'):
        days_of_month: list[int]
        type: Literal[RecurrenceType.MONTHLY]

        @overload
        def __init__(
                self, 
                *, 
                days_of_month: list[int]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.NamespaceToolParam(Tool, discriminator='namespace'):
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[ToolType.NAMESPACE]

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                tools: list[Union[FunctionToolParam, CustomToolParam]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.NoAuthenticationCredentials(BaseCredentials, discriminator='None'):
        type: Literal[CredentialType.NONE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OneTimeTrigger(Trigger, discriminator='OneTime'):
        time_zone: Optional[str]
        trigger_at: datetime
        type: Literal[TriggerType.ONE_TIME]

        @overload
        def __init__(
                self, 
                *, 
                time_zone: Optional[str] = ..., 
                trigger_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAnonymousAuthDetails(OpenApiAuthDetails, discriminator='anonymous'):
        type: Literal[OpenApiAuthType.ANONYMOUS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAuthDetails(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "anonymous"
        MANAGED_IDENTITY = "managed_identity"
        PROJECT_CONNECTION = "project_connection"


    class azure.ai.projects.models.OpenApiFunctionDefinition(_Model):
        auth: OpenApiAuthDetails
        default_params: Optional[list[str]]
        description: Optional[str]
        functions: Optional[list[OpenApiFunctionDefinitionFunction]]
        name: str
        spec: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                auth: OpenApiAuthDetails, 
                default_params: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                spec: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiFunctionDefinitionFunction(_Model):
        description: Optional[str]
        name: str
        parameters: dict[str, Any]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: dict[str, Any]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiManagedAuthDetails(OpenApiAuthDetails, discriminator='managed_identity'):
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[OpenApiAuthType.MANAGED_IDENTITY]

        @overload
        def __init__(
                self, 
                *, 
                security_scheme: OpenApiManagedSecurityScheme
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiManagedSecurityScheme(_Model):
        audience: str

        @overload
        def __init__(
                self, 
                *, 
                audience: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiProjectConnectionAuthDetails(OpenApiAuthDetails, discriminator='project_connection'):
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[OpenApiAuthType.PROJECT_CONNECTION]

        @overload
        def __init__(
                self, 
                *, 
                security_scheme: OpenApiProjectConnectionSecurityScheme
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiProjectConnectionSecurityScheme(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiTool(Tool, discriminator='openapi'):
        openapi: OpenApiFunctionDefinition
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                openapi: OpenApiFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OpenApiToolboxTool(ToolboxTool, discriminator='openapi'):
        description: str
        name: str
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.OPENAPI]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                openapi: OpenApiFunctionDefinition, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OperationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.ai.projects.models.OptimizedAgentIdentifier(_Model):
        agent_name: str
        agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.OtlpTelemetryEndpoint(TelemetryEndpoint, discriminator='OTLP'):
        auth: TelemetryEndpointAuth
        data: Union[list[str, TelemetryDataKind]]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: Union[str, TelemetryTransportProtocol]

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[TelemetryEndpointAuth] = ..., 
                data: list[Union[str, TelemetryDataKind]], 
                endpoint: str, 
                protocol: Union[str, TelemetryTransportProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PSTNTelephonyTransferDestination(TelephonyTransferDestination, discriminator='pstn'):
        kind: Literal[TelephonyTransferDestinationKind.PSTN]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PageOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.ai.projects.models.PendingUploadRequest(_Model):
        connection_name: Optional[str]
        pending_upload_id: Optional[str]
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]

        @overload
        def __init__(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                pending_upload_id: Optional[str] = ..., 
                pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PendingUploadResponse(_Model):
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_reference: BlobReference, 
                pending_upload_id: str, 
                pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PendingUploadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_REFERENCE = "BlobReference"
        NONE = "None"
        TEMPORARY_BLOB_REFERENCE = "TemporaryBlobReference"


    class azure.ai.projects.models.PickPropertiesVoiceAgentAudioConfig(_Model):
        output: Optional[VoiceAgentAudioOutputConfig]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceAgentAudioOutputConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProceduralMemoryItem(MemoryItem, discriminator='procedural'):
        content: str
        kind: Literal[MemoryItemKind.PROCEDURAL]
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProgrammaticToolCallingParam(Tool, discriminator='programmatic_tool_calling'):
        type: Literal[ToolType.PROGRAMMATIC_TOOL_CALLING]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromotionInfo(_Model):
        agent_name: str
        agent_version: str
        promoted_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                agent_name: str, 
                agent_version: str, 
                promoted_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptAgentDefinition(AgentDefinition, discriminator='prompt'):
        instructions: Optional[str]
        kind: Literal[AgentKind.PROMPT]
        model: str
        rai_config: RaiConfig
        reasoning: Optional[Reasoning]
        structured_inputs: Optional[dict[str, StructuredInputDefinition]]
        temperature: Optional[float]
        text: Optional[PromptAgentDefinitionTextOptions]
        tool_choice: Optional[Union[str, ToolChoiceParam]]
        tools: Optional[list[Tool]]
        top_p: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                model: str, 
                rai_config: Optional[RaiConfig] = ..., 
                reasoning: Optional[Reasoning] = ..., 
                structured_inputs: Optional[dict[str, StructuredInputDefinition]] = ..., 
                temperature: Optional[float] = ..., 
                text: Optional[PromptAgentDefinitionTextOptions] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceParam]] = ..., 
                tools: Optional[list[Tool]] = ..., 
                top_p: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptAgentDefinitionTextOptions(_Model):
        format: Optional[TextResponseFormat]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[TextResponseFormat] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='prompt'):
        data_schema: dict[str, any]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        prompt_text: str
        type: Literal[EvaluatorDefinitionType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                prompt_text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptDataGenerationJobSource(DataGenerationJobSource, discriminator='prompt'):
        description: str
        prompt: str
        type: Literal[DataGenerationJobSourceType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                prompt: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PromptEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='prompt'):
        description: Optional[str]
        prompt: str
        type: Literal[EvaluatorGenerationJobSourceType.PROMPT]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                prompt: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProtocolConfiguration(_Model):
        a2a: Optional[A2AProtocolConfiguration]
        activity: Optional[ActivityProtocolConfiguration]
        invocations: Optional[InvocationsProtocolConfiguration]
        invocations_ws: Optional[InvocationsWsProtocolConfiguration]
        mcp: Optional[McpProtocolConfiguration]
        responses: Optional[ResponsesProtocolConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                a2a: Optional[A2AProtocolConfiguration] = ..., 
                activity: Optional[ActivityProtocolConfiguration] = ..., 
                invocations: Optional[InvocationsProtocolConfiguration] = ..., 
                invocations_ws: Optional[InvocationsWsProtocolConfiguration] = ..., 
                mcp: Optional[McpProtocolConfiguration] = ..., 
                responses: Optional[ResponsesProtocolConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ProtocolVersionRecord(_Model):
        protocol: Union[str, AgentEndpointProtocol]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                protocol: Union[str, AgentEndpointProtocol], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.PublishApprovalStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "approved"
        NOT_PUBLISHED = "not_published"
        NO_APPROVAL_NEEDED = "no_approval_needed"
        PENDING = "pending"
        REJECTED = "rejected"


    class azure.ai.projects.models.RaiConfig(_Model):
        rai_policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                rai_policy_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RankerVersionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        DEFAULT_2024_11_15 = "default-2024-11-15"


    class azure.ai.projects.models.RankingOptions(_Model):
        hybrid_search: Optional[HybridSearchOptions]
        ranker: Optional[Union[str, RankerVersionType]]
        score_threshold: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                hybrid_search: Optional[HybridSearchOptions] = ..., 
                ranker: Optional[Union[str, RankerVersionType]] = ..., 
                score_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormats(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcm(RealtimeAudioFormats, discriminator='audio/pcm'):
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


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcma(RealtimeAudioFormats, discriminator='audio/pcma'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMA]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsAudioPcmu(RealtimeAudioFormats, discriminator='audio/pcmu'):
        type: Literal[RealtimeAudioFormatsType.AUDIO_PCMU]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeAudioFormatsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIO_PCM = "audio/pcm"
        AUDIO_PCMA = "audio/pcma"
        AUDIO_PCMU = "audio/pcmu"


    class azure.ai.projects.models.RealtimeClientEvent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventConversationItemCreate(RealtimeClientEvent, discriminator='conversation.item.create'):
        event_id: Optional[str]
        item: RealtimeConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item: RealtimeConversationItem, 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventConversationItemDelete(RealtimeClientEvent, discriminator='conversation.item.delete'):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_DELETE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventConversationItemRetrieve(RealtimeClientEvent, discriminator='conversation.item.retrieve'):
        event_id: Optional[str]
        item_id: str
        type: Literal[RealtimeClientEventType.CONVERSATION_ITEM_RETRIEVE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventConversationItemTruncate(RealtimeClientEvent, discriminator='conversation.item.truncate'):
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
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventInputAudioBufferAppend(RealtimeClientEvent, discriminator='input_audio_buffer.append'):
        audio: str
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_APPEND]

        @overload
        def __init__(
                self, 
                *, 
                audio: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventInputAudioBufferClear(RealtimeClientEvent, discriminator='input_audio_buffer.clear'):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventInputAudioBufferCommit(RealtimeClientEvent, discriminator='input_audio_buffer.commit'):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.INPUT_AUDIO_BUFFER_COMMIT]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventOutputAudioBufferClear(RealtimeClientEvent, discriminator='output_audio_buffer.clear'):
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.OUTPUT_AUDIO_BUFFER_CLEAR]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventResponseCancel(RealtimeClientEvent, discriminator='response.cancel'):
        event_id: Optional[str]
        response_id: Optional[str]
        type: Literal[RealtimeClientEventType.RESPONSE_CANCEL]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventResponseCreate(RealtimeClientEvent, discriminator='response.create'):
        event_id: Optional[str]
        response: Optional[VoiceAgentResponseCreateParams]
        type: Literal[RealtimeClientEventType.RESPONSE_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                response: Optional[VoiceAgentResponseCreateParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeClientEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
        RTC_CALL_SDP_CREATE = "rtc.call.sdp.create"
        SESSION_AVATAR_CONNECT = "session.avatar.connect"
        SESSION_UPDATE = "session.update"


    class azure.ai.projects.models.RealtimeConversationItem(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemFunctionCall(RealtimeConversationItem, discriminator='function_call'):
        arguments: str
        call_id: Optional[str]
        created_at: Optional[datetime]
        id: Optional[str]
        name: str
        object: Optional[Literal["item"]]
        response_id: Optional[str]
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


    class azure.ai.projects.models.RealtimeConversationItemFunctionCallOutput(RealtimeConversationItem, discriminator='function_call_output'):
        call_id: str
        created_at: Optional[datetime]
        id: Optional[str]
        name: Optional[str]
        object: Optional[Literal["item"]]
        output: str
        response_id: Optional[str]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Literal[RealtimeConversationItemType.FUNCTION_CALL_OUTPUT]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                output: str, 
                status: Optional[Literal[completed, incomplete, in_progress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessage(RealtimeConversationItem, discriminator='message'):
        role: str
        type: Literal[RealtimeConversationItemType.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                role: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageAssistant(RealtimeConversationItemMessage, discriminator='assistant'):
        content: list[RealtimeConversationItemMessageAssistantContent]
        created_at: Optional[datetime]
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: Optional[str]
        role: Literal[RealtimeConversationItemMessageType.ASSISTANT]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageAssistantContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ..., 
                type: Literal[RealtimeConversationItemType.MESSAGE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageAssistantContent(_Model):
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


    class azure.ai.projects.models.RealtimeConversationItemMessageSystem(RealtimeConversationItemMessage, discriminator='system'):
        content: list[RealtimeConversationItemMessageSystemContent]
        created_at: Optional[datetime]
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: Optional[str]
        role: Literal[RealtimeConversationItemMessageType.SYSTEM]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageSystemContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ..., 
                type: Literal[RealtimeConversationItemType.MESSAGE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageSystemContent(_Model):
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


    class azure.ai.projects.models.RealtimeConversationItemMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSISTANT = "assistant"
        SYSTEM = "system"
        USER = "user"


    class azure.ai.projects.models.RealtimeConversationItemMessageUser(RealtimeConversationItemMessage, discriminator='user'):
        content: list[RealtimeConversationItemMessageUserContent]
        created_at: Optional[datetime]
        id: Optional[str]
        object: Optional[Literal["item"]]
        response_id: Optional[str]
        role: Literal[RealtimeConversationItemMessageType.USER]
        status: Optional[Literal["completed", "incomplete", "in_progress"]]
        type: Union[str, azure.ai.projects.models.MESSAGE]

        @overload
        def __init__(
                self, 
                *, 
                content: list[RealtimeConversationItemMessageUserContent], 
                id: Optional[str] = ..., 
                object: Optional[Literal[item]] = ..., 
                status: Optional[Literal[completed, incomplete, in_progress]] = ..., 
                type: Literal[RealtimeConversationItemType.MESSAGE]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeConversationItemMessageUserContent(_Model):
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


    class azure.ai.projects.models.RealtimeConversationItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION_CALL = "function_call"
        FUNCTION_CALL_OUTPUT = "function_call_output"
        MCP_APPROVAL_REQUEST = "mcp_approval_request"
        MCP_APPROVAL_RESPONSE = "mcp_approval_response"
        MCP_CALL = "mcp_call"
        MCP_LIST_TOOLS = "mcp_list_tools"
        MESSAGE = "message"


    class azure.ai.projects.models.RealtimeFunctionTool(_Model):
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


    class azure.ai.projects.models.RealtimeFunctionToolParameters(_Model):


    class azure.ai.projects.models.RealtimeMCPApprovalRequest(RealtimeConversationItem, discriminator='mcp_approval_request'):
        arguments: str
        created_at: Optional[datetime]
        id: str
        name: str
        response_id: Optional[str]
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


    class azure.ai.projects.models.RealtimeMCPApprovalResponse(RealtimeConversationItem, discriminator='mcp_approval_response'):
        approval_request_id: str
        approve: bool
        created_at: Optional[datetime]
        id: str
        reason: Optional[str]
        response_id: Optional[str]
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


    class azure.ai.projects.models.RealtimeMCPError(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeMCPHTTPError(RealtimeMCPError, discriminator='http_error'):
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


    class azure.ai.projects.models.RealtimeMCPListTools(RealtimeConversationItem, discriminator='mcp_list_tools'):
        created_at: Optional[datetime]
        id: Optional[str]
        response_id: Optional[str]
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


    class azure.ai.projects.models.RealtimeMCPProtocolError(RealtimeMCPError, discriminator='protocol_error'):
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


    class azure.ai.projects.models.RealtimeMCPToolCall(RealtimeConversationItem, discriminator='mcp_call'):
        approval_request_id: Optional[str]
        arguments: str
        created_at: Optional[datetime]
        error: Optional[RealtimeMCPError]
        id: str
        name: str
        output: Optional[str]
        response_id: Optional[str]
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


    class azure.ai.projects.models.RealtimeMCPToolExecutionError(RealtimeMCPError, discriminator='tool_execution_error'):
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


    class azure.ai.projects.models.RealtimeMcpErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP_ERROR = "http_error"
        PROTOCOL_ERROR = "protocol_error"
        TOOL_EXECUTION_ERROR = "tool_execution_error"


    class azure.ai.projects.models.RealtimeReasoning(_Model):
        effort: Optional[Union[str, RealtimeReasoningEffort]]

        @overload
        def __init__(
                self, 
                *, 
                effort: Optional[Union[str, RealtimeReasoningEffort]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        XHIGH = "xhigh"


    class azure.ai.projects.models.RealtimeResponseStatusDetails(_Model):
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


    class azure.ai.projects.models.RealtimeResponseStatusDetailsError(_Model):
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


    class azure.ai.projects.models.RealtimeResponseUsage(_Model):
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


    class azure.ai.projects.models.RealtimeResponseUsageInputTokenDetails(_Model):
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


    class azure.ai.projects.models.RealtimeResponseUsageInputTokenDetailsCachedTokensDetails(_Model):
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


    class azure.ai.projects.models.RealtimeResponseUsageOutputTokenDetails(_Model):
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


    class azure.ai.projects.models.RealtimeServerEvent(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemAdded(RealtimeServerEvent, discriminator='conversation.item.added'):
        event_id: str
        item: RealtimeConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem, 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemCreated(RealtimeServerEvent, discriminator='conversation.item.created'):
        event_id: str
        item: RealtimeConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem, 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemDeleted(RealtimeServerEvent, discriminator='conversation.item.deleted'):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DELETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemDone(RealtimeServerEvent, discriminator='conversation.item.done'):
        event_id: str
        item: RealtimeConversationItem
        previous_item_id: Optional[str]
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem, 
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionCompleted(RealtimeServerEvent, discriminator='conversation.item.input_audio_transcription.completed'):
        content_index: int
        event_id: str
        item_id: str
        languages: Optional[list[TranscriptionLanguage]]
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
                languages: Optional[list[TranscriptionLanguage]] = ..., 
                logprobs: Optional[list[LogProbProperties]] = ..., 
                phrases: Optional[list[VoiceAgentTranscriptionPhrase]] = ..., 
                transcript: str, 
                usage: Union[TranscriptTextUsageTokens, TranscriptTextUsageDuration]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionDelta(RealtimeServerEvent, discriminator='conversation.item.input_audio_transcription.delta'):
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
                logprobs: Optional[list[LogProbProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionFailed(RealtimeServerEvent, discriminator='conversation.item.input_audio_transcription.failed'):
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
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionFailedError(_Model):
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


    class azure.ai.projects.models.RealtimeServerEventConversationItemInputAudioTranscriptionSegment(RealtimeServerEvent, discriminator='conversation.item.input_audio_transcription.segment'):
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
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemRetrieved(RealtimeServerEvent, discriminator='conversation.item.retrieved'):
        event_id: str
        item: RealtimeConversationItem
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_RETRIEVED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventConversationItemTruncated(RealtimeServerEvent, discriminator='conversation.item.truncated'):
        audio_end_ms: int
        content_index: int
        event_id: str
        item: Optional[RealtimeConversationItem]
        item_id: str
        type: Literal[RealtimeServerEventType.CONVERSATION_ITEM_TRUNCATED]

        @overload
        def __init__(
                self, 
                *, 
                audio_end_ms: int, 
                content_index: int, 
                event_id: str, 
                item: Optional[RealtimeConversationItem] = ..., 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventError(_Model):
        error: RealtimeServerEventErrorError
        event_id: str
        type: Literal["error"]

        @overload
        def __init__(
                self, 
                *, 
                error: RealtimeServerEventErrorError, 
                event_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventErrorError(_Model):
        code: Optional[str]
        event_id: Optional[str]
        message: str
        param: Optional[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                event_id: Optional[str] = ..., 
                message: str, 
                param: Optional[str] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventInputAudioBufferCleared(RealtimeServerEvent, discriminator='input_audio_buffer.cleared'):
        event_id: str
        type: Literal[RealtimeServerEventType.INPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventInputAudioBufferCommitted(RealtimeServerEvent, discriminator='input_audio_buffer.committed'):
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
                previous_item_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventInputAudioBufferSpeechStarted(RealtimeServerEvent, discriminator='input_audio_buffer.speech_started'):
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
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventInputAudioBufferSpeechStopped(RealtimeServerEvent, discriminator='input_audio_buffer.speech_stopped'):
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
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventInputAudioBufferTimeoutTriggered(RealtimeServerEvent, discriminator='input_audio_buffer.timeout_triggered'):
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
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventMCPListToolsCompleted(RealtimeServerEvent, discriminator='mcp_list_tools.completed'):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventMCPListToolsFailed(RealtimeServerEvent, discriminator='mcp_list_tools.failed'):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_FAILED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventMCPListToolsInProgress(RealtimeServerEvent, discriminator='mcp_list_tools.in_progress'):
        event_id: str
        item_id: str
        type: Literal[RealtimeServerEventType.MCP_LIST_TOOLS_IN_PROGRESS]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventOutputAudioBufferCleared(RealtimeServerEvent, discriminator='output_audio_buffer.cleared'):
        event_id: str
        response_id: str
        type: Literal[RealtimeServerEventType.OUTPUT_AUDIO_BUFFER_CLEARED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventRateLimitsUpdated(RealtimeServerEvent, discriminator='rate_limits.updated'):
        event_id: str
        rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
        type: Literal[RealtimeServerEventType.RATE_LIMITS_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                rate_limits: list[RealtimeServerEventRateLimitsUpdatedRateLimits]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventRateLimitsUpdatedRateLimits(_Model):
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


    class azure.ai.projects.models.RealtimeServerEventResponseAudioDelta(RealtimeServerEvent, discriminator='response.output_audio.delta'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseAudioDone(RealtimeServerEvent, discriminator='response.output_audio.done'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseAudioTranscriptDelta(RealtimeServerEvent, discriminator='response.output_audio_transcript.delta'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseAudioTranscriptDone(RealtimeServerEvent, discriminator='response.output_audio_transcript.done'):
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
                transcript: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartAdded(RealtimeServerEvent, discriminator='response.content_part.added'):
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


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartAddedPart(_Model):
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


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartDone(RealtimeServerEvent, discriminator='response.content_part.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        part: RealtimeServerEventResponseContentPartDonePart
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
                part: RealtimeServerEventResponseContentPartDonePart, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseContentPartDonePart(_Model):
        audio: Optional[str]
        format: Optional[RealtimeAudioFormats]
        text: Optional[str]
        transcript: Optional[str]
        type: Optional[Literal["audio", "text"]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[str] = ..., 
                format: Optional[RealtimeAudioFormats] = ..., 
                text: Optional[str] = ..., 
                transcript: Optional[str] = ..., 
                type: Optional[Literal[audio, text]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseCreated(RealtimeServerEvent, discriminator='response.created'):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseDone(RealtimeServerEvent, discriminator='response.done'):
        event_id: str
        response: VoiceAgentRealtimeResponse
        type: Literal[RealtimeServerEventType.RESPONSE_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                response: VoiceAgentRealtimeResponse
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseFunctionCallArgumentsDelta(RealtimeServerEvent, discriminator='response.function_call_arguments.delta'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseFunctionCallArgumentsDone(RealtimeServerEvent, discriminator='response.function_call_arguments.done'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseMCPCallArgumentsDelta(RealtimeServerEvent, discriminator='response.mcp_call_arguments.delta'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseMCPCallArgumentsDone(RealtimeServerEvent, discriminator='response.mcp_call_arguments.done'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseMCPCallCompleted(RealtimeServerEvent, discriminator='response.mcp_call.completed'):
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
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseMCPCallFailed(RealtimeServerEvent, discriminator='response.mcp_call.failed'):
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
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseMCPCallInProgress(RealtimeServerEvent, discriminator='response.mcp_call.in_progress'):
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
                output_index: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseOutputItemAdded(RealtimeServerEvent, discriminator='response.output_item.added'):
        event_id: str
        item: RealtimeConversationItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_ADDED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseOutputItemDone(RealtimeServerEvent, discriminator='response.output_item.done'):
        event_id: str
        item: RealtimeConversationItem
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_OUTPUT_ITEM_DONE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                item: RealtimeConversationItem, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseTextDelta(RealtimeServerEvent, discriminator='response.output_text.delta'):
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
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventResponseTextDone(RealtimeServerEvent, discriminator='response.output_text.done'):
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
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventSessionCreated(RealtimeServerEvent, discriminator='session.created'):
        conversation_id: Optional[str]
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventSessionUpdated(RealtimeServerEvent, discriminator='session.updated'):
        event_id: str
        session: VoiceAgentSessionResponseConfig
        type: Literal[RealtimeServerEventType.SESSION_UPDATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                session: VoiceAgentSessionResponseConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RealtimeServerEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
        RESPONSE_ANIMATION_BLENDSHAPES_DELTA = "response.animation_blendshapes.delta"
        RESPONSE_ANIMATION_BLENDSHAPES_DONE = "response.animation_blendshapes.done"
        RESPONSE_ANIMATION_VISEME_DELTA = "response.animation_viseme.delta"
        RESPONSE_ANIMATION_VISEME_DONE = "response.animation_viseme.done"
        RESPONSE_AUDIO_TIMESTAMP_DELTA = "response.audio_timestamp.delta"
        RESPONSE_AUDIO_TIMESTAMP_DONE = "response.audio_timestamp.done"
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
        RESPONSE_VIDEO_DELTA = "response.video.delta"
        RTC_CALL_ERROR = "rtc.call.error"
        RTC_CALL_SDP_CREATED = "rtc.call.sdp.created"
        SESSION_AVATAR_CONNECTING = "session.avatar.connecting"
        SESSION_AVATAR_SWITCH_TO_IDLE = "session.avatar.switch_to_idle"
        SESSION_AVATAR_SWITCH_TO_SPEAKING = "session.avatar.switch_to_speaking"
        SESSION_CREATED = "session.created"
        SESSION_SUBAGENT_ABORTED = "session.subagent.aborted"
        SESSION_SUBAGENT_COMPLETED = "session.subagent.completed"
        SESSION_SUBAGENT_STARTED = "session.subagent.started"
        SESSION_UPDATED = "session.updated"
        WARNING = "warning"


    class azure.ai.projects.models.Reasoning(_Model):
        context: Optional[Literal["auto", "current_turn", "all_turns"]]
        effort: Optional[Union[str, ReasoningEffort]]
        generate_summary: Optional[Literal["auto", "concise", "detailed"]]
        mode: Optional[Union[str, ReasoningModeEnum]]
        summary: Optional[Literal["auto", "concise", "detailed"]]

        @overload
        def __init__(
                self, 
                *, 
                context: Optional[Literal[auto, current_turn, all_turns]] = ..., 
                effort: Optional[Union[str, ReasoningEffort]] = ..., 
                generate_summary: Optional[Literal[auto, concise, detailed]] = ..., 
                mode: Optional[Union[str, ReasoningModeEnum]] = ..., 
                summary: Optional[Literal[auto, concise, detailed]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ReasoningEffort(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MAX = "max"
        MEDIUM = "medium"
        MINIMAL = "minimal"
        NONE = "none"
        XHIGH = "xhigh"


    class azure.ai.projects.models.ReasoningModeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRO = "pro"
        STANDARD = "standard"


    class azure.ai.projects.models.RecurrenceSchedule(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RecurrenceTrigger(Trigger, discriminator='Recurrence'):
        end_time: Optional[datetime]
        interval: int
        schedule: RecurrenceSchedule
        start_time: Optional[datetime]
        time_zone: Optional[str]
        type: Literal[TriggerType.RECURRENCE]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                interval: int, 
                schedule: RecurrenceSchedule, 
                start_time: Optional[datetime] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        HOURLY = "Hourly"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.ai.projects.models.RedTeam(_Model):
        application_scenario: Optional[str]
        attack_strategies: Optional[list[Union[str, AttackStrategy]]]
        display_name: Optional[str]
        name: str
        num_turns: Optional[int]
        properties: Optional[dict[str, str]]
        risk_categories: Optional[list[Union[str, RiskCategory]]]
        simulation_only: Optional[bool]
        status: Optional[str]
        tags: Optional[dict[str, str]]
        target: RedTeamTargetConfig

        @overload
        def __init__(
                self, 
                *, 
                application_scenario: Optional[str] = ..., 
                attack_strategies: Optional[list[Union[str, AttackStrategy]]] = ..., 
                display_name: Optional[str] = ..., 
                num_turns: Optional[int] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                risk_categories: Optional[list[Union[str, RiskCategory]]] = ..., 
                simulation_only: Optional[bool] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                target: RedTeamTargetConfig
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RedTeamEvalRunDataSource(TypedDict, total=False):
        key "item_generation_params": Required[Any]
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_red_team"]]


    class azure.ai.projects.models.RedTeamTargetConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ReminderPreviewToolboxTool(ToolboxTool, discriminator='reminder_preview'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.REMINDER_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponseRetrievalItemGenerationParams(TypedDict, total=False):
        key "data_mapping": Required[Dict[str, str]]
        key "max_num_turns": int
        key "source": Required[Union[SourceFileContent, SourceFileID]]
        key "type": Required[Literal["response_retrieval"]]


    class azure.ai.projects.models.ResponseUsageInputTokensDetails(_Model):
        cache_write_tokens: int
        cached_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                cache_write_tokens: int, 
                cached_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponseUsageOutputTokensDetails(_Model):
        reasoning_tokens: int

        @overload
        def __init__(
                self, 
                *, 
                reasoning_tokens: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ResponsesProtocolConfiguration(_Model):


    class azure.ai.projects.models.RiskCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODE_VULNERABILITY = "CodeVulnerability"
        HATE_UNFAIRNESS = "HateUnfairness"
        PROHIBITED_ACTIONS = "ProhibitedActions"
        PROTECTED_MATERIAL = "ProtectedMaterial"
        SELF_HARM = "SelfHarm"
        SENSITIVE_DATA_LEAKAGE = "SensitiveDataLeakage"
        SEXUAL = "Sexual"
        TASK_ADHERENCE = "TaskAdherence"
        UNGROUNDED_ATTRIBUTES = "UngroundedAttributes"
        VIOLENCE = "Violence"


    class azure.ai.projects.models.Routine(_Model):
        action: Optional[RoutineAction]
        created_at: Optional[datetime]
        description: Optional[str]
        enabled: bool
        name: Optional[str]
        triggers: Optional[dict[str, RoutineTrigger]]
        updated_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[RoutineAction] = ..., 
                created_at: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                enabled: bool, 
                name: Optional[str] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                updated_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineAction(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.models.RoutineAttemptSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_FIRE = "event_fire"
        MANUAL_DISPATCH = "manual_dispatch"
        QUEUED_DISPATCH = "queued_dispatch"
        SCHEDULE_DELIVERY = "schedule_delivery"
        TIMER_DELIVERY = "timer_delivery"


    class azure.ai.projects.models.RoutineAuthorization(_Model):
        identity: Optional[Union[str, RoutineDispatchIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Union[str, RoutineDispatchIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineDispatchIdentity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        CREATOR = "creator"


    class azure.ai.projects.models.RoutineDispatchPayload(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineDispatchPayloadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVOKE_AGENT_INVOCATIONS_API = "invoke_agent_invocations_api"
        INVOKE_AGENT_RESPONSES_API = "invoke_agent_responses_api"


    class azure.ai.projects.models.RoutineRun(_Model):
        action_correlation_id: Optional[str]
        action_type: Optional[Union[str, RoutineActionType]]
        agent_endpoint_id: Optional[str]
        agent_id: Optional[str]
        attempt_source: Optional[Union[str, RoutineAttemptSource]]
        conversation_id: Optional[str]
        dispatch_id: Optional[str]
        ended_at: Optional[datetime]
        error_message: Optional[str]
        error_status_code: Optional[int]
        error_type: Optional[str]
        id: str
        phase: Optional[Union[str, RoutineRunPhase]]
        response_id: Optional[str]
        scheduled_fire_at: Optional[datetime]
        session_id: Optional[str]
        started_at: Optional[datetime]
        status: Optional[RoutineRunStatus]
        task_id: Optional[str]
        trigger_event_payload: Optional[dict[str, Any]]
        trigger_name: Optional[str]
        trigger_type: Optional[Union[str, RoutineTriggerType]]
        triggered_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                action_correlation_id: Optional[str] = ..., 
                action_type: Optional[Union[str, RoutineActionType]] = ..., 
                agent_endpoint_id: Optional[str] = ..., 
                agent_id: Optional[str] = ..., 
                attempt_source: Optional[Union[str, RoutineAttemptSource]] = ..., 
                conversation_id: Optional[str] = ..., 
                dispatch_id: Optional[str] = ..., 
                ended_at: Optional[datetime] = ..., 
                error_message: Optional[str] = ..., 
                error_status_code: Optional[int] = ..., 
                error_type: Optional[str] = ..., 
                phase: Optional[Union[str, RoutineRunPhase]] = ..., 
                response_id: Optional[str] = ..., 
                scheduled_fire_at: Optional[datetime] = ..., 
                session_id: Optional[str] = ..., 
                started_at: Optional[datetime] = ..., 
                status: Optional[RoutineRunStatus] = ..., 
                task_id: Optional[str] = ..., 
                trigger_event_payload: Optional[dict[str, Any]] = ..., 
                trigger_name: Optional[str] = ..., 
                trigger_type: Optional[Union[str, RoutineTriggerType]] = ..., 
                triggered_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineRunPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        DISPATCHING = "dispatching"
        FAILED = "failed"
        QUEUED = "queued"


    class azure.ai.projects.models.RoutineTrigger(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RoutineTriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "custom"
        GITHUB_ISSUE = "github_issue"
        SCHEDULE = "schedule"
        TIMER = "timer"


    class azure.ai.projects.models.RubricBasedEvaluatorDefinition(EvaluatorDefinition, discriminator='rubric'):
        data_schema: dict[str, any]
        dimensions: list[Dimension]
        init_parameters: dict[str, any]
        metrics: dict[str, EvaluatorMetric]
        pass_threshold: Optional[float]
        type: Literal[EvaluatorDefinitionType.RUBRIC]

        @overload
        def __init__(
                self, 
                *, 
                data_schema: Optional[dict[str, Any]] = ..., 
                dimensions: list[Dimension], 
                init_parameters: Optional[dict[str, Any]] = ..., 
                metrics: Optional[dict[str, EvaluatorMetric]] = ..., 
                pass_threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RubricGenerationInputQualityWarning(_Model):
        code: Union[str, RubricGenerationInputQualityWarningCode]
        message: str
        severity: Union[str, RubricGenerationInputQualityWarningSeverity]
        source: Union[str, RubricGenerationInputQualityWarningSource]
        source_index: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                code: Union[str, RubricGenerationInputQualityWarningCode], 
                message: str, 
                severity: Union[str, RubricGenerationInputQualityWarningSeverity], 
                source: Union[str, RubricGenerationInputQualityWarningSource], 
                source_index: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.RubricGenerationInputQualityWarningCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMPTY_AGENT_INSTRUCTIONS = "empty_agent_instructions"
        EMPTY_DATASET_CONTENT = "empty_dataset_content"
        EMPTY_PROMPT = "empty_prompt"
        INSUFFICIENT_TOTAL_INPUT = "insufficient_total_input"
        LOW_TRACE_COUNT = "low_trace_count"
        SHORT_AGENT_INSTRUCTIONS = "short_agent_instructions"
        SHORT_DATASET_CONTENT = "short_dataset_content"
        SHORT_PROMPT = "short_prompt"


    class azure.ai.projects.models.RubricGenerationInputQualityWarningSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WARNING = "warning"


    class azure.ai.projects.models.RubricGenerationInputQualityWarningSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        AGGREGATE = "aggregate"
        DATASET = "dataset"
        PROMPT = "prompt"


    class azure.ai.projects.models.SASCredentials(BaseCredentials, discriminator='SAS'):
        sas_token: Optional[str]
        type: Literal[CredentialType.SAS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SampleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION_RESULT_SAMPLE = "EvaluationResultSample"


    class azure.ai.projects.models.Schedule(_Model):
        description: Optional[str]
        display_name: Optional[str]
        enabled: bool
        properties: Optional[dict[str, str]]
        provisioning_status: Optional[Union[str, ScheduleProvisioningStatus]]
        schedule_id: str
        system_data: dict[str, str]
        tags: Optional[dict[str, str]]
        task: ScheduleTask
        trigger: Trigger

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enabled: bool, 
                properties: Optional[dict[str, str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                task: ScheduleTask, 
                trigger: Trigger
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleProvisioningStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.ai.projects.models.ScheduleRoutineTrigger(RoutineTrigger, discriminator='schedule'):
        cron_expression: str
        time_zone: str
        type: Literal[RoutineTriggerType.SCHEDULE]

        @overload
        def __init__(
                self, 
                *, 
                cron_expression: str, 
                time_zone: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleRun(_Model):
        error: Optional[str]
        properties: dict[str, str]
        run_id: str
        schedule_id: str
        success: bool
        trigger_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                schedule_id: str, 
                trigger_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleTask(_Model):
        configuration: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                configuration: Optional[dict[str, str]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ScheduleTaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVALUATION = "Evaluation"
        INSIGHT = "Insight"


    class azure.ai.projects.models.SearchContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMAGE = "image"
        TEXT = "text"


    class azure.ai.projects.models.SearchContextSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.projects.models.SessionConfiguration(_Model):
        idle_timeout_seconds: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                idle_timeout_seconds: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionDirectoryEntry(_Model):
        is_directory: bool
        modified_time: datetime
        name: str
        size: int

        @overload
        def __init__(
                self, 
                *, 
                is_directory: bool, 
                modified_time: datetime, 
                name: str, 
                size: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionFileWriteResult(_Model):
        bytes_written: int
        path: str

        @overload
        def __init__(
                self, 
                *, 
                bytes_written: int, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionLogEvent(_Model):
        data: str
        event: Union[str, SessionLogEventType]

        @overload
        def __init__(
                self, 
                *, 
                data: str, 
                event: Union[str, SessionLogEventType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SessionLogEventType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG = "log"


    class azure.ai.projects.models.SharepointGroundingToolParameters(_Model):
        project_connections: Optional[list[ToolProjectConnection]]

        @overload
        def __init__(
                self, 
                *, 
                project_connections: Optional[list[ToolProjectConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SharepointPreviewTool(Tool, discriminator='sharepoint_grounding_preview'):
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                sharepoint_grounding_preview: SharepointGroundingToolParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ShellToolboxTool(ToolboxTool, discriminator='shell'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        description: str
        environment: ToolboxShellEnvironment
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.SHELL]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                description: Optional[str] = ..., 
                environment: ToolboxShellEnvironment, 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SimpleQnADataGenerationJobOptions(DataGenerationJobOptions, discriminator='simple_qna'):
        max_samples: int
        model_options: DataGenerationModelOptions
        question_types: Optional[list[Union[str, SimpleQnAFineTuningQuestionType]]]
        train_split: float
        type: Literal[DataGenerationJobType.SIMPLE_QNA]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                question_types: Optional[list[Union[str, SimpleQnAFineTuningQuestionType]]] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SimpleQnAFineTuningQuestionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LONG_ANSWER = "long_answer"
        SHORT_ANSWER = "short_answer"


    class azure.ai.projects.models.SimulationSeedDataGenerationJobOptions(DataGenerationJobOptions, discriminator='simulation_seed'):
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.SIMULATION_SEED]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SipTelephonyTransferDestination(TelephonyTransferDestination, discriminator='sip'):
        kind: Literal[TelephonyTransferDestinationKind.SIP]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillDetails(_Model):
        created_at: datetime
        default_version: str
        description: str
        id: str
        latest_version: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                default_version: str, 
                description: str, 
                id: str, 
                latest_version: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillInlineContent(_Model):
        allowed_tools: Optional[list[str]]
        compatibility: Optional[str]
        description: str
        instructions: str
        license: Optional[str]
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_tools: Optional[list[str]] = ..., 
                compatibility: Optional[str] = ..., 
                description: str, 
                instructions: str, 
                license: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillReferenceParam(ContainerSkill, discriminator='skill_reference'):
        skill_id: str
        type: Literal[ContainerSkillType.SKILL_REFERENCE]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                skill_id: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SkillVersion(_Model):
        created_at: datetime
        description: str
        id: str
        name: str
        skill_id: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                description: str, 
                id: str, 
                name: str, 
                skill_id: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificApplyPatchParam(ToolChoiceParam, discriminator='apply_patch'):
        type: Literal[ToolChoiceParamType.APPLY_PATCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificFunctionShellParam(ToolChoiceParam, discriminator='shell'):
        type: Literal[ToolChoiceParamType.SHELL]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.SpecificProgrammaticToolCallingParam(ToolChoiceParam, discriminator='programmatic_tool_calling'):
        type: Literal[ToolChoiceParamType.PROGRAMMATIC_TOOL_CALLING]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.StructuredInputDefinition(_Model):
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


    class azure.ai.projects.models.StructuredOutputDefinition(_Model):
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                name: str, 
                schema: dict[str, Any], 
                strict: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TargetCompletionEvalRunDataSource(TypedDict, total=False):
        key "input_messages": Required[InputMessagesItemReference]
        key "source": Required[Union[SourceFileContent, SourceFileID]]
        key "target": Required[Union[AzureAIAgentTargetParam, AzureAIModelTargetParam, dict[str, Any]]]
        key "type": Required[Literal["azure_ai_target_completions"]]


    class azure.ai.projects.models.TaxonomyCategory(_Model):
        description: Optional[str]
        id: str
        name: str
        properties: Optional[dict[str, str]]
        risk_category: Union[str, RiskCategory]
        sub_categories: list[TaxonomySubCategory]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                id: str, 
                name: str, 
                properties: Optional[dict[str, str]] = ..., 
                risk_category: Union[str, RiskCategory], 
                sub_categories: list[TaxonomySubCategory]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TaxonomySubCategory(_Model):
        description: Optional[str]
        enabled: bool
        id: str
        name: str
        properties: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                enabled: bool, 
                id: str, 
                name: str, 
                properties: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TeamsPhoneExtensionTelephonyBinding(TelephonyBinding, discriminator='teams_phone_extension'):
        connection: str
        id: str
        incoming_call_url: str
        label: str
        phone_number: Optional[str]
        provider: Literal[TelephonyProvider.TEAMS_PHONE_EXTENSION]
        resource_account_object_id: str
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                resource_account_object_id: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TeamsPhoneExtensionTelephonyBindingListItem(TelephonyBindingListItem, discriminator='teams_phone_extension'):
        connection: str
        etag: str
        id: str
        incoming_call_url: str
        label: str
        phone_number: Optional[str]
        provider: Literal[TelephonyProvider.TEAMS_PHONE_EXTENSION]
        resource_account_object_id: str
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                resource_account_object_id: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TeamsTelephonyTransferDestination(TelephonyTransferDestination, discriminator='teams'):
        kind: Literal[TelephonyTransferDestinationKind.TEAMS]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryConfig(_Model):
        endpoints: list[TelemetryEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: list[TelemetryEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryDataKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINER_OTEL = "ContainerOtel"
        CONTAINER_STDOUT_STDERR = "ContainerStdoutStderr"
        METRICS = "Metrics"


    class azure.ai.projects.models.TelemetryEndpoint(_Model):
        auth: Optional[TelemetryEndpointAuth]
        data: list[Union[str, TelemetryDataKind]]
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                auth: Optional[TelemetryEndpointAuth] = ..., 
                data: list[Union[str, TelemetryDataKind]], 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryEndpointAuth(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelemetryEndpointAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEADER = "header"


    class azure.ai.projects.models.TelemetryEndpointKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTLP = "OTLP"


    class azure.ai.projects.models.TelemetryTransportProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GRPC = "Grpc"
        HTTP = "Http"


    class azure.ai.projects.models.TelephonyBinding(_Model):
        connection: str
        id: str
        incoming_call_url: str
        label: Optional[str]
        provider: str
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                provider: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyBindingListItem(_Model):
        connection: str
        etag: str
        id: str
        incoming_call_url: str
        label: Optional[str]
        provider: str
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                provider: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyBindingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "active"
        SUSPENDED = "suspended"


    class azure.ai.projects.models.TelephonyCallDurationBasis(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANSWERED = "answered"
        RECEIVED = "received"


    class azure.ai.projects.models.TelephonyCallLifecycleEvent(_Model):
        name: Union[str, TelephonyCallLifecycleEventName]
        observed_at: datetime
        occurred_at: Optional[datetime]
        outcome: Union[str, TelephonyCallLifecycleEventOutcome]
        provider_event_id: Optional[str]
        provider_sequence: Optional[int]
        provider_status_code: Optional[int]
        provider_sub_code: Optional[int]
        reason: Optional[str]
        sequence: int
        source: Union[str, TelephonyCallLifecycleEventSource]
        timestamp_source: Union[str, TelephonyCallTimestampSource]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, TelephonyCallLifecycleEventName], 
                observed_at: datetime, 
                occurred_at: Optional[datetime] = ..., 
                outcome: Union[str, TelephonyCallLifecycleEventOutcome], 
                provider_event_id: Optional[str] = ..., 
                provider_sequence: Optional[int] = ..., 
                provider_status_code: Optional[int] = ..., 
                provider_sub_code: Optional[int] = ..., 
                reason: Optional[str] = ..., 
                source: Union[str, TelephonyCallLifecycleEventSource], 
                timestamp_source: Union[str, TelephonyCallTimestampSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyCallLifecycleEventName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT_SESSION_CONNECT = "telephony.agent_session.connect"
        BINDING_RESOLVE = "telephony.binding.resolve"
        CALL_DISCONNECT = "telephony.call.disconnect"
        CALL_HANGUP = "telephony.call.hangup"
        CALL_TRANSFER = "telephony.call.transfer"
        FIRST_AGENT_AUDIO = "telephony.media.first_agent_audio"
        FIRST_CALLER_AUDIO = "telephony.media.first_caller_audio"
        MEDIA_CONNECT = "telephony.media.connect"
        PROVIDER_ANSWER = "telephony.provider.answer"
        WEBHOOK_RECEIVED = "telephony.webhook.received"
        WEBHOOK_VALIDATION = "telephony.webhook.validation"


    class azure.ai.projects.models.TelephonyCallLifecycleEventOutcome(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        FAILED = "failed"
        OBSERVED = "observed"
        REJECTED = "rejected"
        STARTED = "started"
        SUCCEEDED = "succeeded"


    class azure.ai.projects.models.TelephonyCallLifecycleEventSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GATEWAY = "gateway"
        TEAMS_PHONE_EXTENSION = "teams_phone_extension"
        TWILIO = "twilio"
        VOICE_AGENT = "voice_agent"


    class azure.ai.projects.models.TelephonyCallPhase(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMITTED = "admitted"
        AGENT_SESSION_READY = "agent_session_ready"
        ANSWERED = "answered"
        ANSWERING = "answering"
        BRIDGING = "bridging"
        COMPLETED = "completed"
        FAILED = "failed"
        MANAGING = "managing"
        MEDIA_CONNECTED = "media_connected"
        RECEIVED = "received"
        REJECTED = "rejected"
        VALIDATED = "validated"


    class azure.ai.projects.models.TelephonyCallRecord(_Model):
        agent_session_ready_at: Optional[datetime]
        answered_at: Optional[datetime]
        caller_number: Optional[str]
        duration_ms: Optional[timedelta]
        end_reason: Optional[str]
        ended_at: Optional[datetime]
        events: list[TelephonyCallLifecycleEvent]
        events_truncated: bool
        id: str
        media_connected_at: Optional[datetime]
        phase: Union[str, TelephonyCallPhase]
        provider: Union[str, TelephonyProvider]
        provider_call_id: Optional[str]
        provider_message: Optional[str]
        provider_number: Optional[str]
        provider_status_code: Optional[int]
        provider_sub_code: Optional[int]
        started_at: datetime
        status: Union[str, TelephonyCallStatus]
        timing: TelephonyCallTiming
        trace: Optional[TelephonyCallTrace]

        @overload
        def __init__(
                self, 
                *, 
                agent_session_ready_at: Optional[datetime] = ..., 
                answered_at: Optional[datetime] = ..., 
                caller_number: Optional[str] = ..., 
                duration_ms: Optional[timedelta] = ..., 
                end_reason: Optional[str] = ..., 
                ended_at: Optional[datetime] = ..., 
                events: list[TelephonyCallLifecycleEvent], 
                events_truncated: bool, 
                id: str, 
                media_connected_at: Optional[datetime] = ..., 
                phase: Union[str, TelephonyCallPhase], 
                provider: Union[str, TelephonyProvider], 
                provider_call_id: Optional[str] = ..., 
                provider_message: Optional[str] = ..., 
                provider_number: Optional[str] = ..., 
                provider_status_code: Optional[int] = ..., 
                provider_sub_code: Optional[int] = ..., 
                started_at: datetime, 
                status: Union[str, TelephonyCallStatus], 
                timing: TelephonyCallTiming, 
                trace: Optional[TelephonyCallTrace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyCallStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "failed"
        IN_PROGRESS = "in_progress"
        SUCCESS = "success"


    class azure.ai.projects.models.TelephonyCallSummary(_Model):
        agent_session_ready_at: Optional[datetime]
        answered_at: Optional[datetime]
        caller_number: Optional[str]
        duration_ms: Optional[timedelta]
        end_reason: Optional[str]
        ended_at: Optional[datetime]
        id: str
        media_connected_at: Optional[datetime]
        phase: Union[str, TelephonyCallPhase]
        provider: Union[str, TelephonyProvider]
        provider_call_id: Optional[str]
        provider_message: Optional[str]
        provider_number: Optional[str]
        provider_status_code: Optional[int]
        provider_sub_code: Optional[int]
        started_at: datetime
        status: Union[str, TelephonyCallStatus]

        @overload
        def __init__(
                self, 
                *, 
                agent_session_ready_at: Optional[datetime] = ..., 
                answered_at: Optional[datetime] = ..., 
                caller_number: Optional[str] = ..., 
                duration_ms: Optional[timedelta] = ..., 
                end_reason: Optional[str] = ..., 
                ended_at: Optional[datetime] = ..., 
                id: str, 
                media_connected_at: Optional[datetime] = ..., 
                phase: Union[str, TelephonyCallPhase], 
                provider: Union[str, TelephonyProvider], 
                provider_call_id: Optional[str] = ..., 
                provider_message: Optional[str] = ..., 
                provider_number: Optional[str] = ..., 
                provider_status_code: Optional[int] = ..., 
                provider_sub_code: Optional[int] = ..., 
                started_at: datetime, 
                status: Union[str, TelephonyCallStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyCallTimestampSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DERIVED = "derived"
        GATEWAY = "gateway"
        PROVIDER = "provider"


    class azure.ai.projects.models.TelephonyCallTiming(_Model):
        admitted_at: Optional[datetime]
        agent_session_ready_at: Optional[datetime]
        answer_requested_at: Optional[datetime]
        answered_at: Optional[datetime]
        duration_basis: Optional[Union[str, TelephonyCallDurationBasis]]
        ended_at: Optional[datetime]
        first_agent_audio_at: Optional[datetime]
        first_caller_audio_at: Optional[datetime]
        media_connected_at: Optional[datetime]
        received_at: Optional[datetime]
        timestamp_source: Union[str, TelephonyCallTimestampSource]
        validated_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                admitted_at: Optional[datetime] = ..., 
                agent_session_ready_at: Optional[datetime] = ..., 
                answer_requested_at: Optional[datetime] = ..., 
                answered_at: Optional[datetime] = ..., 
                duration_basis: Optional[Union[str, TelephonyCallDurationBasis]] = ..., 
                ended_at: Optional[datetime] = ..., 
                first_agent_audio_at: Optional[datetime] = ..., 
                first_caller_audio_at: Optional[datetime] = ..., 
                media_connected_at: Optional[datetime] = ..., 
                received_at: Optional[datetime] = ..., 
                timestamp_source: Union[str, TelephonyCallTimestampSource], 
                validated_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyCallTrace(_Model):
        conversation_id: Optional[str]
        mode: Optional[Union[str, TelephonyCallTraceMode]]
        root_span_id: Optional[str]
        status: Union[str, TelephonyCallTraceStatus]
        trace_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                mode: Optional[Union[str, TelephonyCallTraceMode]] = ..., 
                root_span_id: Optional[str] = ..., 
                status: Union[str, TelephonyCallTraceStatus], 
                trace_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyCallTraceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIVE = "live"
        POST_CALL = "post_call"


    class azure.ai.projects.models.TelephonyCallTraceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "available"
        EMITTING = "emitting"
        FAILED = "failed"
        NOT_APPLICABLE = "not_applicable"
        NOT_RECORDED = "not_recorded"
        PENDING = "pending"


    class azure.ai.projects.models.TelephonyProvider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TEAMS_PHONE_EXTENSION = "teams_phone_extension"
        TWILIO = "twilio"


    class azure.ai.projects.models.TelephonyTransferDestination(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyTransferDestinationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PSTN = "pstn"
        SIP = "sip"
        TEAMS = "teams"


    class azure.ai.projects.models.TelephonyTransferTarget(_Model):
        description: str
        destination: TelephonyTransferDestination
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                destination: TelephonyTransferDestination, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TelephonyTransferTargets(_Model):
        transfer_targets: list[TelephonyTransferTarget]

        @overload
        def __init__(
                self, 
                *, 
                transfer_targets: list[TelephonyTransferTarget]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TestingCriterionAzureAIEvaluator(TypedDict, total=False):
        key "data_mapping": Dict[str, str]
        key "evaluator_name": Required[str]
        key "evaluator_version": str
        key "initialization_parameters": Dict[str, Any]
        key "name": Required[str]
        key "type": Required[Literal["azure_ai_evaluator"]]


    class azure.ai.projects.models.TextResponseFormat(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON_OBJECT = "json_object"
        JSON_SCHEMA = "json_schema"
        TEXT = "text"


    class azure.ai.projects.models.TextResponseFormatJsonObject(TextResponseFormat, discriminator='json_object'):
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatJsonSchema(TextResponseFormat, discriminator='json_schema'):
        description: Optional[str]
        name: str
        schema: dict[str, Any]
        strict: Optional[bool]
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                schema: dict[str, Any], 
                strict: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TextResponseFormatText(TextResponseFormat, discriminator='text'):
        type: Literal[TextResponseFormatConfigurationType.TEXT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TimerRoutineTrigger(RoutineTrigger, discriminator='timer'):
        at: Optional[datetime]
        type: Literal[RoutineTriggerType.TIMER]

        @overload
        def __init__(
                self, 
                *, 
                at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.Tool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceAllowed(ToolChoiceParam, discriminator='allowed_tools'):
        mode: Literal["auto", "required"]
        tools: list[dict[str, Any]]
        type: Literal[ToolChoiceParamType.ALLOWED_TOOLS]

        @overload
        def __init__(
                self, 
                *, 
                mode: Literal["auto", "required"], 
                tools: list[dict[str, Any]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceCodeInterpreter(ToolChoiceParam, discriminator='code_interpreter'):
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputer(ToolChoiceParam, discriminator='computer'):
        type: Literal[ToolChoiceParamType.COMPUTER]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputerUse(ToolChoiceParam, discriminator='computer_use'):
        type: Literal[ToolChoiceParamType.COMPUTER_USE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceComputerUsePreview(ToolChoiceParam, discriminator='computer_use_preview'):
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceCustom(ToolChoiceParam, discriminator='custom'):
        name: str
        type: Literal[ToolChoiceParamType.CUSTOM]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceFileSearch(ToolChoiceParam, discriminator='file_search'):
        type: Literal[ToolChoiceParamType.FILE_SEARCH]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceFunction(ToolChoiceParam, discriminator='function'):
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


    class azure.ai.projects.models.ToolChoiceImageGeneration(ToolChoiceParam, discriminator='image_generation'):
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceMCP(ToolChoiceParam, discriminator='mcp'):
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


    class azure.ai.projects.models.ToolChoiceOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "auto"
        NONE = "none"
        REQUIRED = "required"


    class azure.ai.projects.models.ToolChoiceParam(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceParamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
        WEB_SEARCH_PREVIEW_2025_03_11 = "web_search_preview_2025_03_11"


    class azure.ai.projects.models.ToolChoiceWebSearchPreview(ToolChoiceParam, discriminator='web_search_preview'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolChoiceWebSearchPreview20250311(ToolChoiceParam, discriminator='web_search_preview_2025_03_11'):
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW_2025_03_11]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolConfig(_Model):
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


    class azure.ai.projects.models.ToolDescription(_Model):
        description: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolDescriptionParam(TypedDict, total=False):
        key "description": str
        key "name": str


    class azure.ai.projects.models.ToolProjectConnection(_Model):
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolSearchExecutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = "client"
        SERVER = "server"


    class azure.ai.projects.models.ToolSearchToolParam(Tool, discriminator='tool_search'):
        description: Optional[str]
        execution: Optional[Union[str, ToolSearchExecutionType]]
        parameters: Optional[EmptyModelParam]
        type: Literal[ToolType.TOOL_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                execution: Optional[Union[str, ToolSearchExecutionType]] = ..., 
                parameters: Optional[EmptyModelParam] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolSearchToolboxTool(ToolboxTool, discriminator='toolbox_search'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        A2_A = "a2a"
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
        WEB_IQ_PREVIEW = "web_iq_preview"
        WEB_SEARCH = "web_search"
        WEB_SEARCH_PREVIEW = "web_search_preview"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.models.ToolUseFineTuningDataGenerationJobOptions(DataGenerationJobOptions, discriminator='tool_use'):
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TOOL_USE]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxObject(_Model):
        default_version: str
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                default_version: str, 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxPolicies(_Model):
        rai_config: Optional[RaiConfig]

        @overload
        def __init__(
                self, 
                *, 
                rai_config: Optional[RaiConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSearchPreviewToolboxTool(ToolboxTool, discriminator='toolbox_search_preview'):
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxShellContainerAutoEnvironment(ToolboxShellEnvironment, discriminator='container_auto'):
        file_ids: Optional[list[str]]
        memory_limit: Optional[Union[str, ContainerMemoryLimit]]
        network_policy: Optional[ToolboxShellNetworkPolicy]
        skills: Optional[list[ContainerSkill]]
        type: Literal["container_auto"]

        @overload
        def __init__(
                self, 
                *, 
                file_ids: Optional[list[str]] = ..., 
                memory_limit: Optional[Union[str, ContainerMemoryLimit]] = ..., 
                network_policy: Optional[ToolboxShellNetworkPolicy] = ..., 
                skills: Optional[list[ContainerSkill]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxShellContainerReferenceEnvironment(ToolboxShellEnvironment, discriminator='container_reference'):
        container_id: str
        type: Literal["container_reference"]

        @overload
        def __init__(
                self, 
                *, 
                container_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxShellEnvironment(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxShellNetworkPolicy(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxShellNetworkPolicyDisabled(ToolboxShellNetworkPolicy, discriminator='disabled'):
        type: Literal["disabled"]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSkill(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxSkillReference(ToolboxSkill, discriminator='skill_reference'):
        name: str
        type: Literal["skill_reference"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxTool(_Model):
        description: Optional[str]
        name: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.ToolboxToolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2A_PREVIEW = "a2a_preview"
        A2_A = "a2a"
        AZURE_AI_SEARCH = "azure_ai_search"
        BROWSER_AUTOMATION_PREVIEW = "browser_automation_preview"
        CODE_INTERPRETER = "code_interpreter"
        FABRIC_IQ_PREVIEW = "fabric_iq_preview"
        FILE_SEARCH = "file_search"
        MCP = "mcp"
        OPENAPI = "openapi"
        REMINDER_PREVIEW = "reminder_preview"
        SHELL = "shell"
        TOOLBOX_SEARCH = "toolbox_search"
        TOOLBOX_SEARCH_PREVIEW = "toolbox_search_preview"
        WEB_IQ_PREVIEW = "web_iq_preview"
        WEB_SEARCH = "web_search"
        WORK_IQ_PREVIEW = "work_iq_preview"


    class azure.ai.projects.models.ToolboxVersionObject(_Model):
        created_at: datetime
        description: Optional[str]
        id: str
        metadata: dict[str, str]
        name: str
        policies: Optional[ToolboxPolicies]
        skills: Optional[list[ToolboxSkill]]
        tools: list[ToolboxTool]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                created_at: datetime, 
                description: Optional[str] = ..., 
                id: str, 
                metadata: dict[str, str], 
                name: str, 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[list[ToolboxSkill]] = ..., 
                tools: list[ToolboxTool], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesDataGenerationJobOptions(DataGenerationJobOptions, discriminator='traces'):
        max_samples: int
        model_options: DataGenerationModelOptions
        redact_private_content: Optional[bool]
        train_split: float
        type: Literal[DataGenerationJobType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                max_samples: int, 
                model_options: Optional[DataGenerationModelOptions] = ..., 
                redact_private_content: Optional[bool] = ..., 
                train_split: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesDataGenerationJobSource(DataGenerationJobSource, discriminator='traces'):
        agent_id: Optional[str]
        agent_name: Optional[str]
        agent_version: Optional[str]
        description: str
        end_time: Optional[datetime]
        start_time: datetime
        type: Literal[DataGenerationJobSourceType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesEvaluatorGenerationJobSource(EvaluatorGenerationJobSource, discriminator='traces'):
        agent_id: Optional[str]
        agent_name: Optional[str]
        agent_version: Optional[str]
        description: Optional[str]
        end_time: Optional[datetime]
        start_time: datetime
        type: Literal[EvaluatorGenerationJobSourceType.TRACES]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                agent_version: Optional[str] = ..., 
                description: Optional[str] = ..., 
                end_time: Optional[datetime] = ..., 
                start_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TracesPreviewEvalRunDataSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "end_time": datetime
        key "ingestion_delay_seconds": int
        key "lookback_hours": int
        key "max_traces": int
        key "trace_ids": List[str]
        key "type": Required[Literal["azure_ai_traces_preview"]]


    class azure.ai.projects.models.TranscriptTextUsageDuration(CreateTranscriptionResponseJsonUsage, discriminator='duration'):
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


    class azure.ai.projects.models.TranscriptTextUsageTokens(CreateTranscriptionResponseJsonUsage, discriminator='tokens'):
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


    class azure.ai.projects.models.TranscriptTextUsageTokensInputTokenDetails(_Model):
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


    class azure.ai.projects.models.TranscriptionLanguage(_Model):
        code: str

        @overload
        def __init__(
                self, 
                *, 
                code: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TreatmentEffectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANGED = "Changed"
        DEGRADED = "Degraded"
        IMPROVED = "Improved"
        INCONCLUSIVE = "Inconclusive"
        TOO_FEW_SAMPLES = "TooFewSamples"


    class azure.ai.projects.models.Trigger(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TriggerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CRON = "Cron"
        ONE_TIME = "OneTime"
        RECURRENCE = "Recurrence"


    class azure.ai.projects.models.TwilioTelephonyBinding(TelephonyBinding, discriminator='twilio'):
        connection: str
        id: str
        incoming_call_url: str
        label: str
        phone_number: str
        provider: Literal[TelephonyProvider.TWILIO]
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                phone_number: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.TwilioTelephonyBindingListItem(TelephonyBindingListItem, discriminator='twilio'):
        connection: str
        etag: str
        id: str
        incoming_call_url: str
        label: str
        phone_number: str
        provider: Literal[TelephonyProvider.TWILIO]
        status: Union[str, TelephonyBindingStatus]

        @overload
        def __init__(
                self, 
                *, 
                connection: str, 
                id: str, 
                incoming_call_url: str, 
                label: Optional[str] = ..., 
                phone_number: str, 
                status: Union[str, TelephonyBindingStatus]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UpdateMemoriesLROPoller(LROPoller[MemoryStoreUpdateCompletedResult]):
        property superseded_by: Optional[str]    # Read-only
        property update_id: str    # Read-only

        @classmethod
        def from_continuation_token(
                cls, 
                polling_method: PollingMethod[MemoryStoreUpdateCompletedResult], 
                continuation_token: str, 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...


    class azure.ai.projects.models.UpdateModelVersionRequest(_Model):
        description: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UpdateTelephonyBindingRequest(_Model):
        connection: Optional[str]
        label: Optional[str]
        phone_number: Optional[str]
        status: Optional[Union[str, TelephonyBindingStatus]]

        @overload
        def __init__(
                self, 
                *, 
                connection: Optional[str] = ..., 
                label: Optional[str] = ..., 
                phone_number: Optional[str] = ..., 
                status: Optional[Union[str, TelephonyBindingStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UpdateToolboxRequest(_Model):
        default_version: str

        @overload
        def __init__(
                self, 
                *, 
                default_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.UserProfileMemoryItem(MemoryItem, discriminator='user_profile'):
        content: str
        kind: Literal[MemoryItemKind.USER_PROFILE]
        memory_id: str
        scope: str
        updated_at: datetime

        @overload
        def __init__(
                self, 
                *, 
                content: str, 
                memory_id: str, 
                scope: str, 
                updated_at: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionIndicator(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionIndicatorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VERSION_REF = "version_ref"


    class azure.ai.projects.models.VersionRefIndicator(VersionIndicator, discriminator='version_ref'):
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]

        @overload
        def __init__(
                self, 
                *, 
                agent_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionSelectionRule(_Model):
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


    class azure.ai.projects.models.VersionSelector(_Model):
        version_selection_rules: list[VersionSelectionRule]

        @overload
        def __init__(
                self, 
                *, 
                version_selection_rules: list[VersionSelectionRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VersionSelectorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.ai.projects.models.VoiceAgentAnimationConfig(_Model):
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


    class azure.ai.projects.models.VoiceAgentAnimationOutputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLENDSHAPES = "blendshapes"
        VISEME_ID = "viseme_id"


    class azure.ai.projects.models.VoiceAgentAudioConfig(_Model):
        input: Optional[VoiceAgentAudioInputConfig]
        output: Optional[VoiceAgentAudioOutputConfig]

        @overload
        def __init__(
                self, 
                *, 
                input: Optional[VoiceAgentAudioInputConfig] = ..., 
                output: Optional[VoiceAgentAudioOutputConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAudioInputConfig(_Model):
        echo_cancellation: Optional[VoiceAgentEchoCancellation]
        format: Optional[RealtimeAudioFormats]
        noise_reduction: Optional[VoiceAgentNoiseReduction]
        transcription: Optional[VoiceAgentInputTranscription]
        turn_detection: Optional[VoiceAgentTurnDetectionConfig]

        @overload
        def __init__(
                self, 
                *, 
                echo_cancellation: Optional[VoiceAgentEchoCancellation] = ..., 
                format: Optional[RealtimeAudioFormats] = ..., 
                noise_reduction: Optional[VoiceAgentNoiseReduction] = ..., 
                transcription: Optional[VoiceAgentInputTranscription] = ..., 
                turn_detection: Optional[VoiceAgentTurnDetectionConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAudioOutputConfig(_Model):
        custom_lexicon_url: Optional[str]
        custom_text_normalization_url: Optional[str]
        custom_voice_endpoint_id: Optional[str]
        format: Optional[RealtimeAudioFormats]
        output_audio_timestamp_types: Optional[list[Union[str, VoiceAgentAudioTimestampType]]]
        personal_voice_model: Optional[str]
        pitch: Optional[str]
        prefer_locales: Optional[list[str]]
        speed: Optional[float]
        style: Optional[str]
        voice: Optional[str]
        voice_locale: Optional[str]
        voice_temperature: Optional[float]
        voice_type: Optional[Union[str, VoiceType]]
        volume: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_lexicon_url: Optional[str] = ..., 
                custom_text_normalization_url: Optional[str] = ..., 
                custom_voice_endpoint_id: Optional[str] = ..., 
                format: Optional[RealtimeAudioFormats] = ..., 
                output_audio_timestamp_types: Optional[list[Union[str, VoiceAgentAudioTimestampType]]] = ..., 
                personal_voice_model: Optional[str] = ..., 
                pitch: Optional[str] = ..., 
                prefer_locales: Optional[list[str]] = ..., 
                speed: Optional[float] = ..., 
                style: Optional[str] = ..., 
                voice: Optional[str] = ..., 
                voice_locale: Optional[str] = ..., 
                voice_temperature: Optional[float] = ..., 
                voice_type: Optional[Union[str, VoiceType]] = ..., 
                volume: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAudioTimestampType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WORD = "word"


    class azure.ai.projects.models.VoiceAgentAvatarConfig(_Model):
        character: str
        customized: Optional[bool]
        model: Optional[str]
        output_audit_audio: Optional[bool]
        output_protocol: Optional[Union[str, VoiceAgentAvatarOutputProtocol]]
        scene: Optional[VoiceAgentAvatarScene]
        style: Optional[str]
        type: Union[str, VoiceAgentAvatarType]
        video: Optional[VoiceAgentAvatarVideoParams]

        @overload
        def __init__(
                self, 
                *, 
                character: str, 
                customized: Optional[bool] = ..., 
                model: Optional[str] = ..., 
                output_audit_audio: Optional[bool] = ..., 
                output_protocol: Optional[Union[str, VoiceAgentAvatarOutputProtocol]] = ..., 
                scene: Optional[VoiceAgentAvatarScene] = ..., 
                style: Optional[str] = ..., 
                type: Union[str, VoiceAgentAvatarType], 
                video: Optional[VoiceAgentAvatarVideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarIceServer(_Model):
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


    class azure.ai.projects.models.VoiceAgentAvatarOutputProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"
        WEBSOCKET_BINARY = "websocket-binary"


    class azure.ai.projects.models.VoiceAgentAvatarScene(_Model):
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


    class azure.ai.projects.models.VoiceAgentAvatarType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PHOTO_AVATAR = "photo_avatar"
        VIDEO_AVATAR = "video_avatar"


    class azure.ai.projects.models.VoiceAgentAvatarVideoBackground(_Model):
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


    class azure.ai.projects.models.VoiceAgentAvatarVideoCrop(_Model):
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


    class azure.ai.projects.models.VoiceAgentAvatarVideoParams(_Model):
        background: Optional[VoiceAgentAvatarVideoBackground]
        bitrate: Optional[int]
        crop: Optional[VoiceAgentAvatarVideoCrop]
        gop_size: Optional[int]
        resolution: Optional[VoiceAgentAvatarVideoResolution]

        @overload
        def __init__(
                self, 
                *, 
                background: Optional[VoiceAgentAvatarVideoBackground] = ..., 
                bitrate: Optional[int] = ..., 
                crop: Optional[VoiceAgentAvatarVideoCrop] = ..., 
                gop_size: Optional[int] = ..., 
                resolution: Optional[VoiceAgentAvatarVideoResolution] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAvatarVideoResolution(_Model):
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


    class azure.ai.projects.models.VoiceAgentAzureSemanticVadEnTurnDetection(VoiceAgentTurnDetectionConfig, discriminator='azure_semantic_vad_en'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceAgentTurnDetectionType.AZURE_SEMANTIC_VAD_EN]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAzureSemanticVadMultilingualTurnDetection(VoiceAgentTurnDetectionConfig, discriminator='azure_semantic_vad_multilingual'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceAgentTurnDetectionType.AZURE_SEMANTIC_VAD_MULTILINGUAL]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentAzureSemanticVadTurnDetection(VoiceAgentTurnDetectionConfig, discriminator='azure_semantic_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[timedelta]
        interrupt_response: Optional[bool]
        languages: Optional[list[str]]
        prefix_padding_ms: Optional[timedelta]
        remove_filler_words: Optional[bool]
        silence_duration_ms: Optional[timedelta]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceAgentTurnDetectionType.AZURE_SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection] = ..., 
                idle_timeout_ms: Optional[timedelta] = ..., 
                interrupt_response: Optional[bool] = ..., 
                languages: Optional[list[str]] = ..., 
                prefix_padding_ms: Optional[timedelta] = ..., 
                remove_filler_words: Optional[bool] = ..., 
                silence_duration_ms: Optional[timedelta] = ..., 
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventRtcCallSdpCreate(RealtimeClientEvent, discriminator='rtc.call.sdp.create'):
        event_id: Optional[str]
        sdp_offer: str
        session: Optional[VoiceAgentSessionUpdateConfig]
        type: Literal[RealtimeClientEventType.RTC_CALL_SDP_CREATE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: Optional[str] = ..., 
                sdp_offer: str, 
                session: Optional[VoiceAgentSessionUpdateConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventSessionAvatarConnect(RealtimeClientEvent, discriminator='session.avatar.connect'):
        client_sdp: str
        event_id: Optional[str]
        type: Literal[RealtimeClientEventType.SESSION_AVATAR_CONNECT]

        @overload
        def __init__(
                self, 
                *, 
                client_sdp: str, 
                event_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentClientEventSessionUpdate(_Model):
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


    class azure.ai.projects.models.VoiceAgentDefinition(AgentDefinition, discriminator='voice'):
        audio: Optional[VoiceAgentAudioConfig]
        avatar: Optional[VoiceAgentAvatarConfig]
        conversation_engine: Optional[VoiceConversationEngine]
        greeting: Optional[VoiceAgentGreetingConfig]
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponseConfig]
        kind: Literal[AgentKind.VOICE]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        model: Optional[str]
        model_type: Optional[Union[str, VoiceModelType]]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        rai_config: RaiConfig
        store: Optional[bool]
        structured_inputs: Optional[dict[str, StructuredInputDefinition]]
        subagent_config: Optional[VoiceAgentSubAgentConfig]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceAgentAudioConfig] = ..., 
                avatar: Optional[VoiceAgentAvatarConfig] = ..., 
                conversation_engine: Optional[VoiceConversationEngine] = ..., 
                greeting: Optional[VoiceAgentGreetingConfig] = ..., 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponseConfig] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                model: Optional[str] = ..., 
                model_type: Optional[Union[str, VoiceModelType]] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                rai_config: Optional[RaiConfig] = ..., 
                store: Optional[bool] = ..., 
                structured_inputs: Optional[dict[str, StructuredInputDefinition]] = ..., 
                subagent_config: Optional[VoiceAgentSubAgentConfig] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentEchoCancellation(_Model):
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


    class azure.ai.projects.models.VoiceAgentEchoCancellationReferenceSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT = "client"
        SERVER = "server"


    class azure.ai.projects.models.VoiceAgentEndOfUtteranceDetection(_Model):
        model: Union[str, VoiceAgentEndOfUtteranceDetectionModel]
        threshold_level: Optional[Union[str, VoiceAgentEndOfUtteranceThresholdLevel]]
        timeout_ms: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                model: Union[str, VoiceAgentEndOfUtteranceDetectionModel], 
                threshold_level: Optional[Union[str, VoiceAgentEndOfUtteranceThresholdLevel]] = ..., 
                timeout_ms: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentEndOfUtteranceDetectionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEMANTIC_DETECTION_V1 = "semantic_detection_v1"
        SEMANTIC_DETECTION_V1_EN = "semantic_detection_v1_en"
        SEMANTIC_DETECTION_V1_MULTILINGUAL = "semantic_detection_v1_multilingual"
        SMART_END_OF_TURN_DETECTION = "smart_end_of_turn_detection"


    class azure.ai.projects.models.VoiceAgentEndOfUtteranceThresholdLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        HIGH = "high"
        LOW = "low"
        MEDIUM = "medium"


    class azure.ai.projects.models.VoiceAgentFunctionTool(VoiceAgentTool, discriminator='function'):
        description: Optional[str]
        name: str
        parameters: Optional[RealtimeFunctionToolParameters]
        type: Literal["function"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                parameters: Optional[RealtimeFunctionToolParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentGreetingConfig(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentInputTranscription(_Model):
        custom_speech: Optional[dict[str, str]]
        delay: Optional[Literal["minimal", "low", "medium", "high", "xhigh"]]
        keywords: Optional[list[str]]
        language: Optional[str]
        languages: Optional[list[str]]
        model: Union[str, VoiceAgentInputTranscriptionModel]
        phrase_list: Optional[list[str]]
        prompt: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_speech: Optional[dict[str, str]] = ..., 
                delay: Optional[Literal[minimal, low, medium, high, xhigh]] = ..., 
                keywords: Optional[list[str]] = ..., 
                language: Optional[str] = ..., 
                languages: Optional[list[str]] = ..., 
                model: Union[str, VoiceAgentInputTranscriptionModel], 
                phrase_list: Optional[list[str]] = ..., 
                prompt: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentInputTranscriptionModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SPEECH = "azure-speech"
        GPT4_O_MINI_TRANSCRIBE = "gpt-4o-mini-transcribe"
        GPT4_O_TRANSCRIBE = "gpt-4o-transcribe"
        GPT4_O_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"
        GPT_LIVE_TRANSCRIBE = "gpt-live-transcribe"
        GPT_REALTIME_WHISPER = "gpt-realtime-whisper"
        GPT_TRANSCRIBE = "gpt-transcribe"
        MAI_TRANSCRIBE = "mai-transcribe"
        WHISPER1 = "whisper-1"


    class azure.ai.projects.models.VoiceAgentInterimResponseConfig(_Model):
        latency_threshold_ms: Optional[timedelta]
        triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[timedelta] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentInterimResponseTrigger(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LATENCY = "latency"
        TOOL = "tool"


    class azure.ai.projects.models.VoiceAgentLlmGeneratedGreetingConfig(VoiceAgentGreetingConfig, discriminator='llm_generated'):
        prompt: str
        tool_choice: Optional[VoiceAgentToolChoice]
        type: Literal["llm_generated"]

        @overload
        def __init__(
                self, 
                *, 
                prompt: str, 
                tool_choice: Optional[VoiceAgentToolChoice] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentLlmInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='llm_interim_response'):
        instructions: Optional[str]
        latency_threshold_ms: timedelta
        max_completion_tokens: Optional[int]
        model: Optional[str]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["llm_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                instructions: Optional[str] = ..., 
                latency_threshold_ms: Optional[timedelta] = ..., 
                max_completion_tokens: Optional[int] = ..., 
                model: Optional[str] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentMcpTool(VoiceAgentTool, discriminator='mcp'):
        allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]]
        allowed_tools: Optional[Union[list[str], MCPToolFilter]]
        authorization: Optional[str]
        defer_loading: Optional[bool]
        headers: Optional[dict[str, str]]
        project_connection_id: Optional[str]
        require_approval: Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]]
        server_description: Optional[str]
        server_label: str
        server_url: Optional[str]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal["mcp"]

        @overload
        def __init__(
                self, 
                *, 
                allowed_callers: Optional[list[Union[str, CallableToolAllowedCaller]]] = ..., 
                allowed_tools: Optional[Union[list[str], MCPToolFilter]] = ..., 
                authorization: Optional[str] = ..., 
                defer_loading: Optional[bool] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                project_connection_id: Optional[str] = ..., 
                require_approval: Optional[Union[MCPToolRequireApproval, Literal[always], Literal[never]]] = ..., 
                response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]] = ..., 
                server_description: Optional[str] = ..., 
                server_label: str, 
                server_url: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentNoiseReduction(_Model):
        type: Union[str, VoiceAgentNoiseReductionType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, VoiceAgentNoiseReductionType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentNoiseReductionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DEEP_NOISE_SUPPRESSION = "azure_deep_noise_suppression"
        FAR_FIELD = "far_field"
        NEAR_FIELD = "near_field"


    class azure.ai.projects.models.VoiceAgentRealtimeResponse(VoiceAgentRealtimeResponseBase):
        audio: Optional[VoiceResponseAudio]
        conversation_id: str
        id: str
        max_output_tokens: Union[int, str]
        metadata: Metadata
        object: str
        output: Optional[list[RealtimeConversationItem]]
        output_modalities: Union[list[str, str]]
        status: Union[str, str, str, str, str]
        status_details: RealtimeResponseStatusDetails
        usage: RealtimeResponseUsage

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[VoiceResponseAudio] = ..., 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                object: Optional[Literal[response]] = ..., 
                output: Optional[list[RealtimeConversationItem]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentRealtimeResponseBase(_Model):
        conversation_id: Optional[str]
        id: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[Metadata]
        object: Optional[Literal["response"]]
        output_modalities: Optional[list[Literal["text", "audio"]]]
        status: Optional[Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]]
        status_details: Optional[RealtimeResponseStatusDetails]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                object: Optional[Literal[response]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentResponseCreateParams(_Model):
        audio: Optional[PickPropertiesVoiceAgentAudioConfig]
        conversation: Optional[Union[Literal["auto"], Literal["none"], str]]
        input: Optional[list[RealtimeConversationItem]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponseConfig]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        metadata: Optional[Metadata]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        pre_generated_assistant_message: Optional[RealtimeConversationItem]
        reasoning: Optional[RealtimeReasoning]
        tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]]
        tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]]

        @overload
        def __init__(
                self, 
                *, 
                audio: Optional[PickPropertiesVoiceAgentAudioConfig] = ..., 
                conversation: Optional[Union[Literal[auto], Literal[none], str]] = ..., 
                input: Optional[list[RealtimeConversationItem]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponseConfig] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                metadata: Optional[Metadata] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                pre_generated_assistant_message: Optional[RealtimeConversationItem] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                tool_choice: Optional[Union[str, ToolChoiceOptions, ToolChoiceFunction, ToolChoiceMCP]] = ..., 
                tools: Optional[list[Union[RealtimeFunctionTool, MCPTool]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentRtcCallErrorDetails(_Model):
        code: Optional[str]
        message: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSemanticVadTurnDetection(VoiceAgentTurnDetectionConfig, discriminator='semantic_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        eagerness: Optional[Literal["low", "medium", "high", "auto"]]
        interrupt_response: Optional[bool]
        type: Literal[VoiceAgentTurnDetectionType.SEMANTIC_VAD]

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                create_response: Optional[bool] = ..., 
                eagerness: Optional[Literal[low, medium, high, auto]] = ..., 
                interrupt_response: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationBlendshapesDelta(RealtimeServerEvent, discriminator='response.animation_blendshapes.delta'):
        content_index: int
        event_id: str
        frame_index: int
        frames: list[list[float]]
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_ANIMATION_BLENDSHAPES_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                content_index: int, 
                event_id: str, 
                frame_index: int, 
                frames: list[list[float]], 
                item_id: str, 
                output_index: int, 
                response_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationBlendshapesDone(RealtimeServerEvent, discriminator='response.animation_blendshapes.done'):
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_ANIMATION_BLENDSHAPES_DONE]

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


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationVisemeDelta(RealtimeServerEvent, discriminator='response.animation_viseme.delta'):
        audio_offset_ms: timedelta
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_ANIMATION_VISEME_DELTA]
        viseme_id: int

        @overload
        def __init__(
                self, 
                *, 
                audio_offset_ms: timedelta, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                viseme_id: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAnimationVisemeDone(RealtimeServerEvent, discriminator='response.animation_viseme.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_ANIMATION_VISEME_DONE]

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


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTimestampDelta(RealtimeServerEvent, discriminator='response.audio_timestamp.delta'):
        audio_duration_ms: timedelta
        audio_offset_ms: timedelta
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        text: str
        timestamp_type: Literal["word"]
        type: Literal[RealtimeServerEventType.RESPONSE_AUDIO_TIMESTAMP_DELTA]

        @overload
        def __init__(
                self, 
                *, 
                audio_duration_ms: timedelta, 
                audio_offset_ms: timedelta, 
                content_index: int, 
                event_id: str, 
                item_id: str, 
                output_index: int, 
                response_id: str, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventResponseAudioTimestampDone(RealtimeServerEvent, discriminator='response.audio_timestamp.done'):
        content_index: int
        event_id: str
        item_id: str
        output_index: int
        response_id: str
        type: Literal[RealtimeServerEventType.RESPONSE_AUDIO_TIMESTAMP_DONE]

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


    class azure.ai.projects.models.VoiceAgentServerEventResponseVideoDelta(RealtimeServerEvent, discriminator='response.video.delta'):
        codec: str
        delta: str
        event_id: str
        output_index: int
        type: Literal[RealtimeServerEventType.RESPONSE_VIDEO_DELTA]

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


    class azure.ai.projects.models.VoiceAgentServerEventRtcCallError(RealtimeServerEvent, discriminator='rtc.call.error'):
        error: VoiceAgentRtcCallErrorDetails
        event_id: Optional[str]
        operation: Optional[str]
        rtc_call_id: Optional[str]
        type: Literal[RealtimeServerEventType.RTC_CALL_ERROR]

        @overload
        def __init__(
                self, 
                *, 
                error: VoiceAgentRtcCallErrorDetails, 
                event_id: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                rtc_call_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventRtcCallSdpCreated(RealtimeServerEvent, discriminator='rtc.call.sdp.created'):
        event_id: str
        rtc_call_id: str
        sdp_answer: str
        type: Literal[RealtimeServerEventType.RTC_CALL_SDP_CREATED]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                rtc_call_id: str, 
                sdp_answer: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarConnecting(RealtimeServerEvent, discriminator='session.avatar.connecting'):
        event_id: str
        server_sdp: str
        type: Literal[RealtimeServerEventType.SESSION_AVATAR_CONNECTING]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                server_sdp: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarSwitchToIdle(RealtimeServerEvent, discriminator='session.avatar.switch_to_idle'):
        event_id: str
        turn_id: Optional[str]
        type: Literal[RealtimeServerEventType.SESSION_AVATAR_SWITCH_TO_IDLE]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking(RealtimeServerEvent, discriminator='session.avatar.switch_to_speaking'):
        event_id: str
        turn_id: Optional[str]
        type: Literal[RealtimeServerEventType.SESSION_AVATAR_SWITCH_TO_SPEAKING]

        @overload
        def __init__(
                self, 
                *, 
                event_id: str, 
                turn_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionSubagentAborted(RealtimeServerEvent, discriminator='session.subagent.aborted'):
        call_id: str
        consultation_id: str
        event_id: str
        reason: Union[str, VoiceAgentSubagentAbortReason]
        subagent_name: str
        type: Literal[RealtimeServerEventType.SESSION_SUBAGENT_ABORTED]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                consultation_id: str, 
                event_id: str, 
                reason: Union[str, VoiceAgentSubagentAbortReason], 
                subagent_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionSubagentCompleted(RealtimeServerEvent, discriminator='session.subagent.completed'):
        call_id: str
        consultation_id: str
        event_id: str
        subagent_name: str
        type: Literal[RealtimeServerEventType.SESSION_SUBAGENT_COMPLETED]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                consultation_id: str, 
                event_id: str, 
                subagent_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventSessionSubagentStarted(RealtimeServerEvent, discriminator='session.subagent.started'):
        call_id: str
        consultation_id: str
        event_id: str
        subagent_name: str
        type: Literal[RealtimeServerEventType.SESSION_SUBAGENT_STARTED]

        @overload
        def __init__(
                self, 
                *, 
                call_id: str, 
                consultation_id: str, 
                event_id: str, 
                subagent_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentServerEventWarning(RealtimeServerEvent, discriminator='warning'):
        event_id: str
        type: Literal[RealtimeServerEventType.WARNING]
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


    class azure.ai.projects.models.VoiceAgentServerEventWarningDetails(_Model):
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


    class azure.ai.projects.models.VoiceAgentServerVadTurnDetection(VoiceAgentTurnDetectionConfig, discriminator='server_vad'):
        auto_truncate: bool
        create_response: Optional[bool]
        end_of_utterance_detection: Optional[VoiceAgentEndOfUtteranceDetection]
        idle_timeout_ms: Optional[int]
        interrupt_response: Optional[bool]
        prefix_padding_ms: Optional[int]
        silence_duration_ms: Optional[int]
        speech_duration_ms: Optional[timedelta]
        threshold: Optional[float]
        type: Literal[VoiceAgentTurnDetectionType.SERVER_VAD]

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
                speech_duration_ms: Optional[timedelta] = ..., 
                threshold: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionAvatarConfig(VoiceAgentAvatarConfig):
        character: str
        customized: bool
        ice_servers: Optional[list[VoiceAgentAvatarIceServer]]
        model: str
        output_audit_audio: bool
        output_protocol: Union[str, VoiceAgentAvatarOutputProtocol]
        scene: VoiceAgentAvatarScene
        style: str
        type: Union[str, VoiceAgentAvatarType]
        video: VoiceAgentAvatarVideoParams

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
                type: Union[str, VoiceAgentAvatarType], 
                video: Optional[VoiceAgentAvatarVideoParams] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionIncludeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILE_SEARCH_CALL_RESULTS = "file_search_call.results"
        INPUT_AUDIO_TRANSCRIPTION_LOGPROBS = "item.input_audio_transcription.logprobs"
        INPUT_AUDIO_TRANSCRIPTION_PHRASES = "item.input_audio_transcription.phrases"


    class azure.ai.projects.models.VoiceAgentSessionResponseConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAgentAudioConfig]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        expires_at: Optional[datetime]
        greeting: Optional[VoiceAgentGreetingConfig]
        id: str
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponseConfig]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        model: str
        object: Literal["session"]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]
        type: Literal["realtime"]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAgentAudioConfig] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                expires_at: Optional[datetime] = ..., 
                greeting: Optional[VoiceAgentGreetingConfig] = ..., 
                id: str, 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponseConfig] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                model: str, 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSessionUpdateConfig(_Model):
        animation: Optional[VoiceAgentAnimationConfig]
        audio: Optional[VoiceAgentAudioConfig]
        avatar: Optional[VoiceAgentSessionAvatarConfig]
        greeting: Optional[VoiceAgentGreetingConfig]
        include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]]
        instructions: Optional[str]
        interim_response: Optional[VoiceAgentInterimResponseConfig]
        max_output_tokens: Optional[VoiceAgentMaxOutputTokens]
        metadata: Optional[dict[str, str]]
        output_modalities: Optional[list[Union[str, VoiceOutputModality]]]
        parallel_tool_calls: Optional[bool]
        reasoning: Optional[RealtimeReasoning]
        temperature: Optional[float]
        tool_choice: Optional[VoiceAgentToolChoice]
        tools: Optional[list[VoiceAgentTool]]
        type: Literal["realtime"]

        @overload
        def __init__(
                self, 
                *, 
                animation: Optional[VoiceAgentAnimationConfig] = ..., 
                audio: Optional[VoiceAgentAudioConfig] = ..., 
                avatar: Optional[VoiceAgentSessionAvatarConfig] = ..., 
                greeting: Optional[VoiceAgentGreetingConfig] = ..., 
                include: Optional[list[Union[str, VoiceAgentSessionIncludeOption]]] = ..., 
                instructions: Optional[str] = ..., 
                interim_response: Optional[VoiceAgentInterimResponseConfig] = ..., 
                max_output_tokens: Optional[VoiceAgentMaxOutputTokens] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                output_modalities: Optional[list[Union[str, VoiceOutputModality]]] = ..., 
                parallel_tool_calls: Optional[bool] = ..., 
                reasoning: Optional[RealtimeReasoning] = ..., 
                temperature: Optional[float] = ..., 
                tool_choice: Optional[VoiceAgentToolChoice] = ..., 
                tools: Optional[list[VoiceAgentTool]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentStaticInterimResponseConfig(VoiceAgentInterimResponseConfig, discriminator='static_interim_response'):
        latency_threshold_ms: timedelta
        texts: Optional[list[str]]
        triggers: Union[list[str, VoiceAgentInterimResponseTrigger]]
        type: Literal["static_interim_response"]

        @overload
        def __init__(
                self, 
                *, 
                latency_threshold_ms: Optional[timedelta] = ..., 
                texts: Optional[list[str]] = ..., 
                triggers: Optional[list[Union[str, VoiceAgentInterimResponseTrigger]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSubAgent(_Model):
        agent_capabilities: str
        agent_name: str
        agent_version: Optional[str]
        invoke_timeout_seconds: Optional[timedelta]
        response_policy: Optional[VoiceAgentSubagentResponsePolicy]

        @overload
        def __init__(
                self, 
                *, 
                agent_capabilities: str, 
                agent_name: str, 
                agent_version: Optional[str] = ..., 
                invoke_timeout_seconds: Optional[timedelta] = ..., 
                response_policy: Optional[VoiceAgentSubagentResponsePolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSubAgentConfig(_Model):
        subagents: list[VoiceAgentSubAgent]

        @overload
        def __init__(
                self, 
                *, 
                subagents: list[VoiceAgentSubAgent]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSubagentAbortReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "cancelled"
        FAILED = "failed"
        STOPPED_BY_USER = "stopped_by_user"
        SUPERSEDED = "superseded"
        TIMEOUT = "timeout"
        UNKNOWN_TARGET = "unknown_target"


    class azure.ai.projects.models.VoiceAgentSubagentResponsePolicy(_Model):
        ack_instructions: Optional[str]
        enable_delta_progress: Optional[bool]
        gap_filling_instructions: Optional[str]
        gap_filling_interval: Optional[timedelta]
        immediate_ack: Optional[bool]
        progress_instructions: Optional[str]
        progress_update_interval: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                ack_instructions: Optional[str] = ..., 
                enable_delta_progress: Optional[bool] = ..., 
                gap_filling_instructions: Optional[str] = ..., 
                gap_filling_interval: Optional[timedelta] = ..., 
                immediate_ack: Optional[bool] = ..., 
                progress_instructions: Optional[str] = ..., 
                progress_update_interval: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSystemTool(VoiceAgentTool, discriminator='system'):
        description: Optional[str]
        name: Union[str, VoiceAgentSystemToolName]
        type: Literal["system"]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Union[str, VoiceAgentSystemToolName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentSystemToolName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        END_CONVERSATION = "end_conversation"


    class azure.ai.projects.models.VoiceAgentTemplateGreetingConfig(VoiceAgentGreetingConfig, discriminator='template'):
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


    class azure.ai.projects.models.VoiceAgentTool(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentToolResponseScheduling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERRUPT = "interrupt"
        SILENT = "silent"
        SKIP_IF_BUSY = "skip_if_busy"
        WHEN_IDLE = "when_idle"


    class azure.ai.projects.models.VoiceAgentToolboxTool(VoiceAgentTool, discriminator='toolbox'):
        response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]]
        toolbox_name: str
        toolbox_version: str
        type: Literal["toolbox"]

        @overload
        def __init__(
                self, 
                *, 
                response_scheduling: Optional[Union[str, VoiceAgentToolResponseScheduling]] = ..., 
                toolbox_name: str, 
                toolbox_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTranscriptionPhrase(_Model):
        confidence: Optional[float]
        duration_milliseconds: timedelta
        locale: Optional[str]
        offset_milliseconds: timedelta
        text: str
        words: Optional[list[VoiceAgentTranscriptionWord]]

        @overload
        def __init__(
                self, 
                *, 
                confidence: Optional[float] = ..., 
                duration_milliseconds: timedelta, 
                locale: Optional[str] = ..., 
                offset_milliseconds: timedelta, 
                text: str, 
                words: Optional[list[VoiceAgentTranscriptionWord]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTranscriptionWord(_Model):
        duration_milliseconds: timedelta
        offset_milliseconds: timedelta
        text: str

        @overload
        def __init__(
                self, 
                *, 
                duration_milliseconds: timedelta, 
                offset_milliseconds: timedelta, 
                text: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTransport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEBRTC = "webrtc"
        WEBSOCKET = "websocket"


    class azure.ai.projects.models.VoiceAgentTurnDetectionConfig(_Model):
        auto_truncate: Optional[bool]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                auto_truncate: Optional[bool] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceAgentTurnDetectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SEMANTIC_VAD = "azure_semantic_vad"
        AZURE_SEMANTIC_VAD_EN = "azure_semantic_vad_en"
        AZURE_SEMANTIC_VAD_MULTILINGUAL = "azure_semantic_vad_multilingual"
        SEMANTIC_VAD = "semantic_vad"
        SERVER_VAD = "server_vad"


    class azure.ai.projects.models.VoiceAgentWebSocketSubprotocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REALTIME = "realtime"


    class azure.ai.projects.models.VoiceAudioCodec(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PCM16 = "pcm16"
        PCMA = "pcma"
        PCMU = "pcmu"


    class azure.ai.projects.models.VoiceAudioContainerFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAV = "wav"


    class azure.ai.projects.models.VoiceAudioRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        USER = "user"


    class azure.ai.projects.models.VoiceConversation(_Model):
        completed_at: Optional[datetime]
        created_at: datetime
        id: str
        last_error: Optional[ApiError]
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
                last_error: Optional[ApiError] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                status: Union[str, VoiceConversationStatus], 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceConversationEngine(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceConversationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "completed"
        FAILED = "failed"
        IN_PROGRESS = "in_progress"


    class azure.ai.projects.models.VoiceGeneratedItemAudioResponse(_Model):
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


    class azure.ai.projects.models.VoiceHostedAgentConversationEngine(VoiceConversationEngine, discriminator='hosted_agent'):
        name: str
        type: Literal["hosted_agent"]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceItemAudioResponse(_Model):
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


    class azure.ai.projects.models.VoiceModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "managed"
        SELF_DEPLOYED = "self_deployed"


    class azure.ai.projects.models.VoiceOutputModality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANIMATION = "animation"
        AUDIO = "audio"
        AVATAR = "avatar"
        TEXT = "text"


    class azure.ai.projects.models.VoiceRecordingChannelLayout(_Model):
        left: Literal["user"]
        right: Literal["agent"]

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.models.VoiceRecordingResponse(_Model):
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


    class azure.ai.projects.models.VoiceResponse(VoiceResponseBase):
        audio: Optional[VoiceResponseAudio]
        completed_at: Optional[datetime]
        conversation_id: str
        created_at: Optional[datetime]
        id: str
        max_output_tokens: Union[int, str]
        metadata: Optional[dict[str, str]]
        object: str
        output: Optional[list[RealtimeConversationItem]]
        output_modalities: Union[list[str, str]]
        status: Union[str, str, str, str, str]
        status_details: RealtimeResponseStatusDetails
        temperature: Optional[float]
        usage: RealtimeResponseUsage

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
                metadata: Optional[dict[str, str]] = ..., 
                object: Optional[Literal[response]] = ..., 
                output: Optional[list[RealtimeConversationItem]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                temperature: Optional[float] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponseAudio(_Model):
        output: Optional[VoiceResponseAudioOutput]

        @overload
        def __init__(
                self, 
                *, 
                output: Optional[VoiceResponseAudioOutput] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponseAudioOutput(_Model):
        format: Optional[RealtimeAudioFormats]
        voice: Optional[str]
        voice_locale: Optional[str]
        voice_type: Optional[Union[str, VoiceType]]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[RealtimeAudioFormats] = ..., 
                voice: Optional[str] = ..., 
                voice_locale: Optional[str] = ..., 
                voice_type: Optional[Union[str, VoiceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceResponseBase(_Model):
        conversation_id: Optional[str]
        id: Optional[str]
        max_output_tokens: Optional[Union[int, Literal["inf"]]]
        object: Optional[Literal["response"]]
        output_modalities: Optional[list[Literal["text", "audio"]]]
        status: Optional[Literal["completed", "cancelled", "failed", "incomplete", "in_progress"]]
        status_details: Optional[RealtimeResponseStatusDetails]
        usage: Optional[RealtimeResponseUsage]

        @overload
        def __init__(
                self, 
                *, 
                conversation_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                max_output_tokens: Optional[Union[int, Literal[inf]]] = ..., 
                object: Optional[Literal[response]] = ..., 
                output_modalities: Optional[list[Literal[text, audio]]] = ..., 
                status: Optional[Literal[completed, cancelled, failed, incomplete, in_progress]] = ..., 
                status_details: Optional[RealtimeResponseStatusDetails] = ..., 
                usage: Optional[RealtimeResponseUsage] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.VoiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVATAR_VOICE_SYNC = "avatar-voice-sync"
        AZURE_CUSTOM = "azure-custom"
        AZURE_PERSONAL = "azure-personal"
        AZURE_REALTIME_NATIVE = "azure-realtime-native"
        AZURE_STANDARD = "azure-standard"
        OPENAI = "openai"


    class azure.ai.projects.models.WebIQPreviewTool(Tool, discriminator='web_iq_preview'):
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        type: Literal[ToolType.WEB_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebIQPreviewToolboxTool(ToolboxTool, discriminator='web_iq_preview'):
        description: str
        name: str
        project_connection_id: str
        require_approval: Optional[Union[MCPToolRequireApproval, str]]
        server_label: Optional[str]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WEB_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                require_approval: Optional[Union[MCPToolRequireApproval, str]] = ..., 
                server_label: Optional[str] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchApproximateLocation(_Model):
        city: Optional[str]
        country: Optional[str]
        region: Optional[str]
        timezone: Optional[str]
        type: Literal["approximate"]

        @overload
        def __init__(
                self, 
                *, 
                city: Optional[str] = ..., 
                country: Optional[str] = ..., 
                region: Optional[str] = ..., 
                timezone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchConfiguration(_Model):
        instance_name: str
        project_connection_id: str

        @overload
        def __init__(
                self, 
                *, 
                instance_name: str, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchPreviewTool(Tool, discriminator='web_search_preview'):
        search_content_types: Optional[list[Union[str, SearchContentType]]]
        search_context_size: Optional[Union[str, SearchContextSize]]
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: Optional[ApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                search_content_types: Optional[list[Union[str, SearchContentType]]] = ..., 
                search_context_size: Optional[Union[str, SearchContextSize]] = ..., 
                user_location: Optional[ApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchTool(Tool, discriminator='web_search'):
        custom_search_configuration: Optional[WebSearchConfiguration]
        description: Optional[str]
        external_web_access: Optional[bool]
        filters: Optional[WebSearchToolFilters]
        name: Optional[str]
        search_context_size: Optional[Literal["low", "medium", "high"]]
        tool_configs: Optional[dict[str, ToolConfig]]
        type: Literal[ToolType.WEB_SEARCH]
        user_location: Optional[WebSearchApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                custom_search_configuration: Optional[WebSearchConfiguration] = ..., 
                description: Optional[str] = ..., 
                external_web_access: Optional[bool] = ..., 
                filters: Optional[WebSearchToolFilters] = ..., 
                name: Optional[str] = ..., 
                search_context_size: Optional[Literal[low, medium, high]] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                user_location: Optional[WebSearchApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchToolFilters(_Model):
        allowed_domains: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WebSearchToolboxTool(ToolboxTool, discriminator='web_search'):
        custom_search_configuration: Optional[WebSearchConfiguration]
        description: str
        external_web_access: Optional[bool]
        filters: Optional[WebSearchToolFilters]
        name: str
        search_context_size: Optional[Literal["low", "medium", "high"]]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WEB_SEARCH]
        user_location: Optional[WebSearchApproximateLocation]

        @overload
        def __init__(
                self, 
                *, 
                custom_search_configuration: Optional[WebSearchConfiguration] = ..., 
                description: Optional[str] = ..., 
                external_web_access: Optional[bool] = ..., 
                filters: Optional[WebSearchToolFilters] = ..., 
                name: Optional[str] = ..., 
                search_context_size: Optional[Literal[low, medium, high]] = ..., 
                tool_configs: Optional[dict[str, ToolConfig]] = ..., 
                user_location: Optional[WebSearchApproximateLocation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WeeklyRecurrenceSchedule(RecurrenceSchedule, discriminator='Weekly'):
        days_of_week: list[Union[str, DayOfWeek]]
        type: Literal[RecurrenceType.WEEKLY]

        @overload
        def __init__(
                self, 
                *, 
                days_of_week: list[Union[str, DayOfWeek]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkIQPreviewTool(Tool, discriminator='work_iq_preview'):
        project_connection_id: str
        type: Literal[ToolType.WORK_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                project_connection_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkIQPreviewToolboxTool(ToolboxTool, discriminator='work_iq_preview'):
        description: str
        name: str
        project_connection_id: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WORK_IQ_PREVIEW]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: Optional[str] = ..., 
                project_connection_id: str, 
                tool_configs: Optional[dict[str, ToolConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.ai.projects.models.WorkflowAgentDefinition(AgentDefinition, discriminator='workflow'):
        kind: Literal[AgentKind.WORKFLOW]
        rai_config: RaiConfig
        workflow: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                rai_config: Optional[RaiConfig] = ..., 
                workflow: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.ai.projects.operations

    class azure.ai.projects.operations.AgentEndpointConversationsOperations(GeneratedAgentEndpointConversationsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_agent_conversation_item_generated_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceGeneratedItemAudioResponse: ...

        @distributed_trace
        def get_agent_conversation_item_generated_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...


    class azure.ai.projects.operations.AgentsOperations(GeneratedAgentsOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                *, 
                agent_session_id: Optional[str] = ..., 
                content_type: str = "application/json", 
                version_indicator: VersionIndicator, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_session(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @overload
        def create_telephony_binding(
                self, 
                agent_name: str, 
                body: CreateTelephonyBindingRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def create_telephony_binding(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def create_telephony_binding(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                *, 
                blueprint_reference: Optional[AgentBlueprintReference] = ..., 
                content_type: str = "application/json", 
                definition: AgentDefinition, 
                description: Optional[str] = ..., 
                draft: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def create_version_from_code(
                self, 
                agent_name: str, 
                *, 
                code: IO[bytes], 
                code_zip_sha256: Optional[str] = ..., 
                definition: HostedAgentDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                manifest_id: str, 
                metadata: Optional[dict[str, str]] = ..., 
                parameter_values: dict[str, Any], 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @overload
        def create_version_from_manifest(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def delete(
                self, 
                agent_name: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentResponse: ...

        @distributed_trace
        def delete_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                recursive: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                *, 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                *, 
                force: Optional[bool] = ..., 
                **kwargs: Any
            ) -> DeleteAgentVersionResponse: ...

        @distributed_trace
        def disable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def download_code(
                self, 
                agent_name: str, 
                *, 
                agent_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def download_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                path: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def enable(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def end_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @distributed_trace
        def generate_agent(
                self, 
                body: GenerateVoiceAgentRequest, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @distributed_trace
        def get(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def get_microsoft365_package(
                self, 
                agent_name: str, 
                *, 
                access_boundaries: Optional[List[Union[str, ActivityProtocolAccessBoundary]]] = ..., 
                agent_display_name: Optional[str] = ..., 
                app_version: Optional[str] = ..., 
                bot_service_arm_id: Optional[str] = ..., 
                can_respond_without_mention: Optional[bool] = ..., 
                color_icon_base64: Optional[str] = ..., 
                content_type: str = "application/json", 
                developer_name: Optional[str] = ..., 
                developer_website_url: Optional[str] = ..., 
                full_description: Optional[str] = ..., 
                optional_permission_scopes: Optional[List[Microsoft365PermissionScopes]] = ..., 
                outline_icon_base64: Optional[str] = ..., 
                privacy_url: Optional[str] = ..., 
                publish_as_autopilot: Optional[bool] = ..., 
                publish_scope: Union[str, Microsoft365PublishScope], 
                short_description: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def get_microsoft365_package(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def get_microsoft365_package(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_microsoft365_publish_defaults(
                self, 
                agent_name: str, 
                *, 
                publish_as_digital_worker: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Microsoft365PublishDefaults: ...

        @distributed_trace
        def get_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> AgentSessionResource: ...

        @distributed_trace
        def get_session_log_stream(
                self, 
                agent_name: str, 
                agent_version: str, 
                session_id: str, 
                **kwargs: Any
            ) -> SessionLogEvent: ...

        @distributed_trace
        def get_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @distributed_trace
        def get_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @distributed_trace
        def get_telephony_transfer_targets(
                self, 
                agent_name: str, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @distributed_trace
        def get_version(
                self, 
                agent_name: str, 
                agent_version: str, 
                **kwargs: Any
            ) -> AgentVersionDetails: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                kind: Optional[Union[str, AgentKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentDetails]: ...

        @distributed_trace
        def list_session_files(
                self, 
                agent_name: str, 
                session_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                path: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SessionDirectoryEntry]: ...

        @distributed_trace
        def list_sessions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentSessionResource]: ...

        @distributed_trace
        def list_telephony_bindings(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                provider: Optional[Union[str, TelephonyProvider]] = ..., 
                status: Optional[Union[str, TelephonyBindingStatus]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TelephonyBindingListItem]: ...

        @distributed_trace
        def list_telephony_calls(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                provider: Optional[Union[str, TelephonyProvider]] = ..., 
                started_after: Optional[datetime] = ..., 
                started_before: Optional[datetime] = ..., 
                status: Optional[Union[str, TelephonyCallStatus]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TelephonyCallSummary]: ...

        @distributed_trace
        def list_versions(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                include_drafts: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentVersionDetails]: ...

        @overload
        def publish_to_microsoft365(
                self, 
                agent_name: str, 
                *, 
                access_boundaries: Optional[List[Union[str, ActivityProtocolAccessBoundary]]] = ..., 
                agent_display_name: Optional[str] = ..., 
                app_version: Optional[str] = ..., 
                bot_service_arm_id: Optional[str] = ..., 
                can_respond_without_mention: Optional[bool] = ..., 
                color_icon_base64: Optional[str] = ..., 
                content_type: str = "application/json", 
                developer_name: Optional[str] = ..., 
                developer_website_url: Optional[str] = ..., 
                full_description: Optional[str] = ..., 
                optional_permission_scopes: Optional[List[Microsoft365PermissionScopes]] = ..., 
                outline_icon_base64: Optional[str] = ..., 
                privacy_url: Optional[str] = ..., 
                publish_as_autopilot: Optional[bool] = ..., 
                publish_scope: Union[str, Microsoft365PublishScope], 
                short_description: Optional[str] = ..., 
                terms_of_use_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        def publish_to_microsoft365(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        def publish_to_microsoft365(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Microsoft365PublishResult: ...

        @overload
        def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                transfer_targets: List[TelephonyTransferTarget], 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @overload
        def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @overload
        def replace_telephony_transfer_targets(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyTransferTargets: ...

        @distributed_trace
        def stop_session(
                self, 
                agent_name: str, 
                session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                *, 
                content_type: str = "application/json", 
                target: str, 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        def transfer_telephony_call(
                self, 
                agent_name: str, 
                call_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TelephonyCallRecord: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                *, 
                agent_card: Optional[AgentCard] = ..., 
                agent_endpoint: Optional[AgentEndpointConfig] = ..., 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def update_details(
                self, 
                agent_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentDetails: ...

        @overload
        def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: UpdateTelephonyBindingRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def update_telephony_binding(
                self, 
                agent_name: str, 
                binding_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> TelephonyBinding: ...

        @overload
        def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: bytes, 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...

        @overload
        def upload_session_file(
                self, 
                agent_name: str, 
                session_id: str, 
                content: IO[bytes], 
                *, 
                content_type: str = "application/octet-stream", 
                path: str, 
                **kwargs: Any
            ) -> SessionFileWriteResult: ...


    class azure.ai.projects.operations.BetaAgentEndpointConversationsOperations:

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
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_agent_conversation(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceConversation: ...

        @distributed_trace
        def get_agent_conversation_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> VoiceRecordingResponse: ...

        @distributed_trace
        def get_agent_conversation_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_item(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> RealtimeConversationItem: ...

        @distributed_trace
        def get_agent_conversation_item_audio(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> VoiceItemAudioResponse: ...

        @distributed_trace
        def get_agent_conversation_item_audio_content(
                self, 
                agent_name: str, 
                conversation_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_agent_conversation_response(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                **kwargs: Any
            ) -> VoiceResponse: ...

        @distributed_trace
        def list_agent_conversation_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RealtimeConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_response_items(
                self, 
                agent_name: str, 
                conversation_id: str, 
                response_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RealtimeConversationItem]: ...

        @distributed_trace
        def list_agent_conversation_responses(
                self, 
                agent_name: str, 
                conversation_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceResponse]: ...

        @distributed_trace
        def list_agent_conversations(
                self, 
                agent_name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[VoiceConversation]: ...


    class azure.ai.projects.operations.BetaAgentInsightMonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_run(
                self, 
                monitor_id: str, 
                run: AgentInsightRunCreate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentInsightRunResult]: ...

        @overload
        def begin_create_run(
                self, 
                monitor_id: str, 
                run: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentInsightRunResult]: ...

        @overload
        def begin_create_run(
                self, 
                monitor_id: str, 
                run: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentInsightRunResult]: ...

        @distributed_trace
        def cancel_run(
                self, 
                monitor_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> AgentInsightRun: ...

        @overload
        def create(
                self, 
                monitor: AgentInsightMonitorCreate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        def create(
                self, 
                monitor: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        def create(
                self, 
                monitor: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @distributed_trace
        def delete(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @distributed_trace
        def get_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                *, 
                include_details: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AgentInsight: ...

        @distributed_trace
        def get_run(
                self, 
                monitor_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> AgentInsightRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentInsightMonitorListItem]: ...

        @distributed_trace
        def list_insights(
                self, 
                monitor_id: str, 
                *, 
                before: Optional[str] = ..., 
                category: Optional[str] = ..., 
                include_details: Optional[bool] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                severity: Optional[Union[str, AgentInsightSeverity]] = ..., 
                status: Optional[Union[str, AgentInsightStatus]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentInsight]: ...

        @distributed_trace
        def list_runs(
                self, 
                monitor_id: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                trigger: Optional[Union[str, AgentInsightRunTrigger]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentInsightRun]: ...

        @distributed_trace
        def reset(
                self, 
                monitor_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                monitor_id: str, 
                monitor: AgentInsightMonitorUpdate, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        def update(
                self, 
                monitor_id: str, 
                monitor: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        def update(
                self, 
                monitor_id: str, 
                monitor: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsightMonitor: ...

        @overload
        def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: AgentInsightUpdate, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...

        @overload
        def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...

        @overload
        def update_insight(
                self, 
                monitor_id: str, 
                insight_id: str, 
                update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AgentInsight: ...


    class azure.ai.projects.operations.BetaAgentsOperations(BetaAgentsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: AgentOptimizationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AgentOptimizationLROPoller: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AgentOptimizationLROPoller: ...

        @overload
        def begin_create_optimization_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> AgentOptimizationLROPoller: ...

        @distributed_trace
        def cancel_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def delete_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_optimization_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> AgentOptimizationJob: ...

        @distributed_trace
        def list_optimization_jobs(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                status: Optional[Union[str, JobStatus]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentOptimizationJobListItem]: ...


    class azure.ai.projects.operations.BetaDatasetsOperations(BetaDatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: DataGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DatasetGenerationLROPoller: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DatasetGenerationLROPoller: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> DatasetGenerationLROPoller: ...

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> DataGenerationJob: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DataGenerationJob]: ...


    class azure.ai.projects.operations.BetaEvaluationTaxonomiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def create(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @distributed_trace
        def list(
                self, 
                *, 
                input_name: Optional[str] = ..., 
                input_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluationTaxonomy]: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: EvaluationTaxonomy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...

        @overload
        def update(
                self, 
                name: str, 
                taxonomy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationTaxonomy: ...


    class azure.ai.projects.operations.BetaEvaluatorsOperations(BetaEvaluatorsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: EvaluatorGenerationJob, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationLROPoller: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: JSON, 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationLROPoller: ...

        @overload
        def begin_create_generation_job(
                self, 
                job: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> EvaluatorGenerationLROPoller: ...

        @distributed_trace
        def cancel_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def create_version(
                self, 
                name: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def delete_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: EvaluatorCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def get_generation_job(
                self, 
                job_id: str, 
                **kwargs: Any
            ) -> EvaluatorGenerationJob: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorVersion]: ...

        @distributed_trace
        def list_generation_jobs(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorGenerationJob]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                limit: Optional[int] = ..., 
                type: Optional[Union[Literal[builtin], Literal[custom], Literal[all], str]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluatorVersion]: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: EvaluatorVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...

        @overload
        def update_version(
                self, 
                name: str, 
                version: str, 
                evaluator_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluatorVersion: ...


    class azure.ai.projects.operations.BetaInsightsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def generate(
                self, 
                insight: Insight, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def generate(
                self, 
                insight: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @overload
        def generate(
                self, 
                insight: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def get(
                self, 
                insight_id: str, 
                *, 
                include_coordinates: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Insight: ...

        @distributed_trace
        def list(
                self, 
                *, 
                agent_name: Optional[str] = ..., 
                eval_id: Optional[str] = ..., 
                include_coordinates: Optional[bool] = ..., 
                run_id: Optional[str] = ..., 
                type: Optional[Union[str, InsightType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Insight]: ...


    class azure.ai.projects.operations.BetaMemoryStoresOperations(GenerateBetaMemoryStoresOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                previous_update_id: Optional[str] = ..., 
                scope: str, 
                update_delay: Optional[int] = ..., 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def begin_update_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpdateMemoriesLROPoller: ...

        @overload
        def create(
                self, 
                *, 
                content_type: str = "application/json", 
                definition: MemoryStoreDefinition, 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                kind: Union[str, MemoryItemKind], 
                scope: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def create_memory(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteMemoryStoreResult: ...

        @distributed_trace
        def delete_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> DeleteMemoryResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @overload
        def delete_scope(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDeleteScopeResult: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @distributed_trace
        def get_memory(
                self, 
                name: str, 
                memory_id: str, 
                **kwargs: Any
            ) -> MemoryItem: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryStoreDetails]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def list_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                before: Optional[str] = ..., 
                content_type: str = "application/json", 
                kind: Optional[Union[str, MemoryItemKind]] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MemoryItem]: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                items: Optional[Union[str, ResponseInputParam]] = ..., 
                options: Optional[MemorySearchOptions] = ..., 
                previous_search_id: Optional[str] = ..., 
                scope: str, 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def search_memories(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreSearchResult: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryStoreDetails: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                *, 
                content: str, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...

        @overload
        def update_memory(
                self, 
                name: str, 
                memory_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MemoryItem: ...


    class azure.ai.projects.operations.BetaModelsOperations(BetaModelsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                *, 
                azcopy_path: Optional[str] = ..., 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[True] = True, 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def create(
                self, 
                *, 
                azcopy_path: Optional[str] = ..., 
                base_model: Optional[str] = ..., 
                description: Optional[str] = ..., 
                name: str, 
                polling_interval: float = 2.0, 
                polling_timeout: float = 300.0, 
                source: Union[str, PathLike[str]], 
                tags: Optional[dict[str, str]] = ..., 
                version: str, 
                wait_for_commit: Literal[False], 
                weight_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: ModelCredentialRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @overload
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                credential_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ModelVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelVersion]: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: ModelVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_create_version(
                self, 
                name: str, 
                version: str, 
                model_version: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CreateAsyncResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: ModelPendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ModelPendingUploadResponse: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: UpdateModelVersionRequest, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...

        @overload
        def update(
                self, 
                name: str, 
                version: str, 
                model_version_update: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> ModelVersion: ...


    class azure.ai.projects.operations.BetaOperations(GeneratedBetaOperations):
        agent_endpoint_conversations: BetaAgentEndpointConversationsOperations
        agent_insight_monitors: BetaAgentInsightMonitorsOperations
        agents: BetaAgentsOperations
        datasets: BetaDatasetsOperations
        evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
        evaluators: BetaEvaluatorsOperations
        insights: BetaInsightsOperations
        memory_stores: BetaMemoryStoresOperations
        models: BetaModelsOperations
        red_teams: BetaRedTeamsOperations
        routines: BetaRoutinesOperations
        schedules: BetaSchedulesOperations
        skills: BetaSkillsOperations

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.ai.projects.operations.BetaRedTeamsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                red_team: RedTeam, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        def create(
                self, 
                red_team: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @overload
        def create(
                self, 
                red_team: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> RedTeam: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[RedTeam]: ...


    class azure.ai.projects.operations.BetaRoutinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                *, 
                action: Optional[RoutineAction] = ..., 
                authorization: Optional[RoutineAuthorization] = ..., 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                triggers: Optional[dict[str, RoutineTrigger]] = ..., 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def create_or_update(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def delete(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                *, 
                content_type: str = "application/json", 
                payload: Optional[RoutineDispatchPayload] = ..., 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @overload
        def dispatch(
                self, 
                routine_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DispatchRoutineResult: ...

        @distributed_trace
        def enable(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def get(
                self, 
                routine_name: str, 
                **kwargs: Any
            ) -> Routine: ...

        @distributed_trace
        def list(
                self, 
                *, 
                after: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Routine]: ...

        @distributed_trace
        def list_runs(
                self, 
                routine_name: str, 
                *, 
                after: Optional[str] = ..., 
                filter: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[RoutineRun]: ...


    class azure.ai.projects.operations.BetaSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: Schedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @overload
        def create_or_update(
                self, 
                schedule_id: str, 
                schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def delete(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                schedule_id: str, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def get_run(
                self, 
                schedule_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> ScheduleRun: ...

        @distributed_trace
        def list(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Schedule]: ...

        @distributed_trace
        def list_runs(
                self, 
                schedule_id: str, 
                *, 
                enabled: Optional[bool] = ..., 
                type: Optional[Union[str, ScheduleTaskType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ScheduleRun]: ...


    class azure.ai.projects.operations.BetaSkillsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default: Optional[bool] = ..., 
                inline_content: Optional[SkillInlineContent] = ..., 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create_from_files(
                self, 
                name: str, 
                content: CreateSkillVersionFromFilesBody, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @overload
        def create_from_files(
                self, 
                name: str, 
                content: JSON, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> DeleteSkillResult: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DeleteSkillVersionResult: ...

        @distributed_trace
        def download(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def download_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> SkillVersion: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkillDetails]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkillVersion]: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkillDetails: ...


    class azure.ai.projects.operations.ConnectionsOperations(ConnectionsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def get_default(
                self, 
                connection_type: Union[str, ConnectionType], 
                *, 
                include_credentials: Optional[bool] = False, 
                **kwargs: Any
            ) -> Connection: ...

        @distributed_trace
        def list(
                self, 
                *, 
                connection_type: Optional[Union[str, ConnectionType]] = ..., 
                default_connection: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Connection]: ...


    class azure.ai.projects.operations.DatasetsOperations(DatasetsOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: DatasetVersion, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                dataset_version: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetVersion: ...

        @distributed_trace
        def get_credentials(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> DatasetCredential: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DatasetVersion]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatasetVersion]: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: PendingUploadRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @overload
        def pending_upload(
                self, 
                name: str, 
                version: str, 
                pending_upload_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PendingUploadResponse: ...

        @distributed_trace
        def upload_file(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_path: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FileDatasetVersion: ...

        @distributed_trace
        def upload_folder(
                self, 
                *, 
                connection_name: Optional[str] = ..., 
                file_pattern: Optional[Pattern] = ..., 
                folder: str, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> FolderDatasetVersion: ...


    class azure.ai.projects.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                *, 
                deployment_type: Optional[Union[str, DeploymentType]] = ..., 
                model_name: Optional[str] = ..., 
                model_publisher: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...


    class azure.ai.projects.operations.EvaluationRulesOperations(GeneratedEvaluationRulesOperations):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: EvaluationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @overload
        def create_or_update(
                self, 
                id: str, 
                evaluation_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def delete(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                id: str, 
                **kwargs: Any
            ) -> EvaluationRule: ...

        @distributed_trace
        def list(
                self, 
                *, 
                action_type: Optional[Union[str, EvaluationRuleActionType]] = ..., 
                agent_name: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EvaluationRule]: ...


    class azure.ai.projects.operations.IndexesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: Index, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @overload
        def create_or_update(
                self, 
                name: str, 
                version: str, 
                index: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> Index: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Index]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[Index]: ...


    class azure.ai.projects.operations.TelemetryOperations:

        def __init__(self, outer_instance: AIProjectClient) -> None: ...

        @distributed_trace
        def get_application_insights_connection_string(self) -> str: ...


    class azure.ai.projects.operations.ToolboxesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_version(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                description: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                policies: Optional[ToolboxPolicies] = ..., 
                skills: Optional[List[ToolboxSkill]] = ..., 
                tools: List[ToolboxTool], 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        def create_version(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @overload
        def create_version(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def delete(
                self, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                name: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @distributed_trace
        def get_version(
                self, 
                name: str, 
                version: str, 
                **kwargs: Any
            ) -> ToolboxVersionObject: ...

        @distributed_trace
        def list(
                self, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ToolboxObject]: ...

        @distributed_trace
        def list_versions(
                self, 
                name: str, 
                *, 
                before: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                order: Optional[Union[str, PageOrder]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ToolboxVersionObject]: ...

        @overload
        def update(
                self, 
                name: str, 
                *, 
                content_type: str = "application/json", 
                default_version: str, 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...

        @overload
        def update(
                self, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ToolboxObject: ...


namespace azure.ai.projects.telemetry

    def azure.ai.projects.telemetry.trace_function(span_name: Optional[str] = None) -> Callable: ...


    class azure.ai.projects.telemetry.AIProjectInstrumentor:

        def __init__(self) -> None: ...

        def instrument(
                self, 
                enable_content_recording: Optional[bool] = None, 
                enable_trace_context_propagation: Optional[bool] = None, 
                enable_baggage_propagation: Optional[bool] = None
            ) -> None: ...

        def is_content_recording_enabled(self) -> bool: ...

        def is_instrumented(self) -> bool: ...

        def uninstrument(self) -> None: ...


```