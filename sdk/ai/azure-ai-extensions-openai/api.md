```py
namespace azure.ai.extensions.openai

    def azure.ai.extensions.openai.enum_value(value: Any) -> Any: ...


    def azure.ai.extensions.openai.get_field(
            payload: Any,
            field: str,
            default: Any = None
        ) -> Any: ...


    def azure.ai.extensions.openai.is_type(payload: Any, type_value: str) -> bool: ...


    def azure.ai.extensions.openai.set_field(
            payload: Any,
            field: str,
            value: Any
        ) -> None: ...


    def azure.ai.extensions.openai.to_wire_dict(value: Any) -> dict[str, Any]: ...


namespace azure.ai.extensions.openai.projects

    class azure.ai.extensions.openai.projects.A2APreviewTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "project_connection_id": str
        key "send_credentials_for_agent_card": bool
        key "type": Required[Literal[a2a_preview]]
        agent_card_path: str
        base_url: str
        project_connection_id: str
        send_credentials_for_agent_card: bool
        type: Literal[ToolType.A2A_PREVIEW]


    class azure.ai.extensions.openai.projects.A2APreviewToolboxTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "description": str
        key "name": str
        key "project_connection_id": str
        key "send_credentials_for_agent_card": bool
        key "type": Required[Literal[a2a_preview]]
        agent_card_path: str
        base_url: str
        description: str
        name: str
        project_connection_id: str
        send_credentials_for_agent_card: bool
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.A2A_PREVIEW]


    class azure.ai.extensions.openai.projects.A2AProtocolConfiguration(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.AISearchIndexResource(TypedDict, total=False):
        key "filter": str
        key "index_asset_id": str
        key "index_name": str
        key "project_connection_id": str
        key "query_type": Literal["simple", "semantic", "vector", "vector_simple_hybrid", "vector_semantic_hybrid"]
        key "top_k": int
        filter: str
        index_asset_id: str
        index_name: str
        project_connection_id: str
        query_type: AzureAISearchQueryType
        top_k: int


    class azure.ai.extensions.openai.projects.ActivityProtocolConfiguration(TypedDict, total=False):
        key "enable_m365_public_endpoint": bool
        enable_m365_public_endpoint: bool


    class azure.ai.extensions.openai.projects.AgentBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[managed_agent_identity_blueprint]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.extensions.openai.projects.AgentBlueprintReferenceType(TypedDict):


    class azure.ai.extensions.openai.projects.AgentCard(TypedDict, total=False):
        key "description": str
        key "skills": Required[list[AgentCardSkill]]
        key "version": Required[str]
        description: str
        skills: list[AgentCardSkill]
        version: str


    class azure.ai.extensions.openai.projects.AgentCardSkill(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        description: str
        examples: list[str]
        id: str
        name: str
        tags: list[str]


    class azure.ai.extensions.openai.projects.AgentClusterInsightRequest(TypedDict, total=False):
        key "agentName": Required[str]
        key "modelConfiguration": ForwardRef('InsightModelConfiguration', module='types')
        key "type": Required[Literal[agent_cluster_insight]]
        agent_name: str
        model_configuration: InsightModelConfiguration
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]


    class azure.ai.extensions.openai.projects.AgentClusterInsightResult(TypedDict, total=False):
        key "clusterInsight": Required[ClusterInsightResult]
        key "type": Required[Literal[agent_cluster_insight]]
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.AGENT_CLUSTER_INSIGHT]


    class azure.ai.extensions.openai.projects.AgentDataGenerationJobSource(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        key "description": str
        key "type": Required[Literal[agent]]
        agent_name: str
        agent_version: str
        description: str
        type: Literal[DataGenerationJobSourceType.AGENT]


    class azure.ai.extensions.openai.projects.AgentDetails(TypedDict, total=False):
        key "agent_card": ForwardRef('AgentCard', module='types')
        key "agent_endpoint": ForwardRef('AgentEndpointConfig', module='types')
        key "blueprint": ForwardRef('AgentIdentity', module='types')
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "id": Required[str]
        key "instance_identity": ForwardRef('AgentIdentity', module='types')
        key "name": Required[str]
        key "object": Required[Literal[agent]]
        key "state": Required[Literal["enabled", "disabled"]]
        key "versions": Required[AgentObjectVersions]
        agent_card: AgentCard
        agent_endpoint: AgentEndpointConfig
        blueprint: AgentIdentity
        blueprint_reference: AgentBlueprintReference
        id: str
        instance_identity: AgentIdentity
        name: str
        object: Literal[AgentObjectType.AGENT]
        state: AgentState
        versions: AgentObjectVersions


    class azure.ai.extensions.openai.projects.AgentEndpointAuthorizationSchemeType(TypedDict):


    class azure.ai.extensions.openai.projects.AgentEndpointConfig(TypedDict, total=False):
        key "protocol_configuration": ForwardRef('ProtocolConfiguration', module='types')
        key "version_selector": ForwardRef('VersionSelector', module='types')
        authorization_schemes: list[AgentEndpointAuthorizationScheme]
        protocol_configuration: ProtocolConfiguration
        version_selector: VersionSelector


    class azure.ai.extensions.openai.projects.AgentEvaluatorGenerationJobSource(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        key "description": str
        key "type": Required[Literal[agent]]
        agent_name: str
        agent_version: str
        description: str
        type: Literal[EvaluatorGenerationJobSourceType.AGENT]


    class azure.ai.extensions.openai.projects.AgentIdentity(TypedDict, total=False):
        key "client_id": Required[str]
        key "principal_id": Required[str]
        client_id: str
        principal_id: str


    class azure.ai.extensions.openai.projects.AgentKind(TypedDict):


    class azure.ai.extensions.openai.projects.AgentObjectType(TypedDict):


    class azure.ai.extensions.openai.projects.AgentObjectVersions(TypedDict, total=False):
        key "latest": Required[AgentVersionDetails]
        latest: AgentVersionDetails


    class azure.ai.extensions.openai.projects.AgentSessionResource(TypedDict, total=False):
        key "agent_session_id": Required[str]
        key "created_at": Required[int]
        key "expires_at": Required[int]
        key "last_accessed_at": Required[int]
        key "status": Required[Literal["creating", "active", "idle", "updating", "failed", "deleting", "deleted", "expired"]]
        key "version_indicator": Required[VersionIndicator]
        agent_session_id: str
        created_at: int
        expires_at: int
        last_accessed_at: int
        status: AgentSessionStatus
        version_indicator: VersionIndicator


    class azure.ai.extensions.openai.projects.AgentTaxonomyInput(TypedDict, total=False):
        key "riskCategories": Required[list[Literal["HateUnfairness", "Violence", "Sexual", "SelfHarm", "ProtectedMaterial", "CodeVulnerability", "UngroundedAttributes", "ProhibitedActions", "SensitiveDataLeakage", "TaskAdherence"]]]
        key "target": Required[EvaluationTarget]
        key "type": Required[Literal[agent]]
        risk_categories: list[RiskCategory]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]


    class azure.ai.extensions.openai.projects.AgentVersionDetails(TypedDict, total=False):
        key "agent_guid": str
        key "blueprint": ForwardRef('AgentIdentity', module='types')
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "created_at": Required[int]
        key "definition": Required[AgentDefinition]
        key "description": str
        key "draft": bool
        key "id": Required[str]
        key "instance_identity": ForwardRef('AgentIdentity', module='types')
        key "metadata": Required[Optional[dict[str, str]]]
        key "name": Required[str]
        key "object": Required[Literal[agent_version]]
        key "status": Literal["creating", "active", "failed", "deleting", "deleted"]
        key "version": Required[str]
        agent_guid: str
        blueprint: AgentIdentity
        blueprint_reference: AgentBlueprintReference
        created_at: int
        definition: AgentDefinition
        description: str
        draft: bool
        id: str
        instance_identity: AgentIdentity
        metadata: dict[str, str]
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION]
        status: AgentVersionStatus
        version: str


    class azure.ai.extensions.openai.projects.AgenticIdentityPreviewCredentials(TypedDict, total=False):
        key "type": Required[Literal[agentic_identity_preview]]
        type: Literal[CredentialType.AGENTIC_IDENTITY_PREVIEW]


    class azure.ai.extensions.openai.projects.ApiError(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": str
        additionalInfo: dict[str, Any]
        additional_info: dict[str, Any]
        code: str
        debugInfo: dict[str, Any]
        debug_info: dict[str, Any]
        details: list[ApiError]
        message: str
        param: str
        type: str


    class azure.ai.extensions.openai.projects.ApiErrorResponse(TypedDict, total=False):
        key "error": Required[ApiError]
        error: ApiError


    class azure.ai.extensions.openai.projects.ApiKeyCredentials(TypedDict, total=False):
        key "key": str
        key "type": Required[Literal[api_key]]
        api_key: str
        type: Literal[CredentialType.API_KEY]


    class azure.ai.extensions.openai.projects.ApplyPatchToolParam(TypedDict, total=False):
        key "type": Required[Literal[apply_patch]]
        type: Literal[ToolType.APPLY_PATCH]


    class azure.ai.extensions.openai.projects.ApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.extensions.openai.projects.ArtifactProfile(TypedDict, total=False):
        key "category": Required[Literal["DataOnly", "RuntimeDependent", "Unknown"]]
        category: FoundryModelArtifactProfileCategory
        signals: list[Literal["PickleDeserialization", "CustomPythonCode", "DynamicOps", "NativeBinary", "UnknownFormat"]]


    class azure.ai.extensions.openai.projects.AutoCodeInterpreterToolParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal["auto"]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        type: Literal[auto]


    class azure.ai.extensions.openai.projects.AzureAIAgentTarget(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["azure_ai_agent"]]
        key "version": str
        name: str
        tool_descriptions: list[ToolDescription]
        tools: list[Tool]
        type: Literal[azure_ai_agent]
        version: str


    class azure.ai.extensions.openai.projects.AzureAIModelTarget(TypedDict, total=False):
        key "model": str
        key "sampling_params": ForwardRef('ModelSamplingParams', module='types')
        key "type": Required[Literal["azure_ai_model"]]
        model: str
        sampling_params: ModelSamplingParams
        type: Literal[azure_ai_model]


    class azure.ai.extensions.openai.projects.AzureAISearchIndex(TypedDict, total=False):
        key "connectionName": Required[str]
        key "description": str
        key "fieldMapping": ForwardRef('FieldMapping', module='types')
        key "id": str
        key "indexName": Required[str]
        key "name": Required[str]
        key "type": Required[Literal[azure_search]]
        key "version": Required[str]
        connection_name: str
        description: str
        field_mapping: FieldMapping
        id: str
        index_name: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.AZURE_SEARCH]
        version: str


    class azure.ai.extensions.openai.projects.AzureAISearchTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "description": str
        key "name": str
        key "type": Required[Literal[azure_ai_search]]
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.AZURE_AI_SEARCH]


    class azure.ai.extensions.openai.projects.AzureAISearchToolResource(TypedDict, total=False):
        key "indexes": Required[list[AISearchIndexResource]]
        indexes: list[AISearchIndexResource]


    class azure.ai.extensions.openai.projects.AzureAISearchToolboxTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "description": str
        key "name": str
        key "type": Required[Literal[azure_ai_search]]
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.AZURE_AI_SEARCH]


    class azure.ai.extensions.openai.projects.AzureFunctionBinding(TypedDict, total=False):
        key "storage_queue": Required[AzureFunctionStorageQueue]
        key "type": Required[Literal["storage_queue"]]
        storage_queue: AzureFunctionStorageQueue
        type: Literal[storage_queue]


    class azure.ai.extensions.openai.projects.AzureFunctionDefinition(TypedDict, total=False):
        key "function": Required[AzureFunctionDefinitionFunction]
        key "input_binding": Required[AzureFunctionBinding]
        key "output_binding": Required[AzureFunctionBinding]
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding


    class azure.ai.extensions.openai.projects.AzureFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.extensions.openai.projects.AzureFunctionStorageQueue(TypedDict, total=False):
        key "queue_name": Required[str]
        key "queue_service_endpoint": Required[str]
        queue_name: str
        queue_service_endpoint: str


    class azure.ai.extensions.openai.projects.AzureFunctionTool(TypedDict, total=False):
        key "azure_function": Required[AzureFunctionDefinition]
        key "type": Required[Literal[azure_function]]
        azure_function: AzureFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.AZURE_FUNCTION]


    class azure.ai.extensions.openai.projects.AzureOpenAIModelConfiguration(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        key "type": Required[Literal["AzureOpenAIModel"]]
        model_deployment_name: str
        type: Literal[AzureOpenAIModel]


    class azure.ai.extensions.openai.projects.BingCustomSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "freshness": str
        key "instance_name": Required[str]
        key "market": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        freshness: str
        instance_name: str
        market: str
        project_connection_id: str
        set_lang: str


    class azure.ai.extensions.openai.projects.BingCustomSearchPreviewTool(TypedDict, total=False):
        key "bing_custom_search_preview": Required[BingCustomSearchToolParameters]
        key "type": Required[Literal[bing_custom_search_preview]]
        bing_custom_search_preview: BingCustomSearchToolParameters
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]


    class azure.ai.extensions.openai.projects.BingCustomSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingCustomSearchConfiguration]]
        search_configurations: list[BingCustomSearchConfiguration]


    class azure.ai.extensions.openai.projects.BingGroundingSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "freshness": str
        key "market": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        freshness: str
        market: str
        project_connection_id: str
        set_lang: str


    class azure.ai.extensions.openai.projects.BingGroundingSearchToolParameters(TypedDict, total=False):
        key "search_configurations": Required[list[BingGroundingSearchConfiguration]]
        search_configurations: list[BingGroundingSearchConfiguration]


    class azure.ai.extensions.openai.projects.BingGroundingTool(TypedDict, total=False):
        key "bing_grounding": Required[BingGroundingSearchToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[bing_grounding]]
        bing_grounding: BingGroundingSearchToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.BING_GROUNDING]


    class azure.ai.extensions.openai.projects.BlobReference(TypedDict, total=False):
        key "blobUri": Required[str]
        key "credential": Required[BlobReferenceSasCredential]
        key "storageAccountArmId": Required[str]
        blob_uri: str
        credential: BlobReferenceSasCredential
        storage_account_arm_id: str


    class azure.ai.extensions.openai.projects.BlobReferenceSasCredential(TypedDict, total=False):
        key "sasUri": Required[str]
        key "type": Required[Literal["SAS"]]
        sas_uri: str
        type: Literal[SAS]


    class azure.ai.extensions.openai.projects.BotServiceAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[bot_service]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE]


    class azure.ai.extensions.openai.projects.BotServiceRbacAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[bot_service_rbac]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_RBAC]


    class azure.ai.extensions.openai.projects.BotServiceTenantAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[bot_service_tenant]]
        type: Literal[AgentEndpointAuthorizationSchemeType.BOT_SERVICE_TENANT]


    class azure.ai.extensions.openai.projects.BrowserAutomationPreviewTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "type": Required[Literal[browser_automation_preview]]
        browser_automation_preview: BrowserAutomationToolParameters
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]


    class azure.ai.extensions.openai.projects.BrowserAutomationPreviewToolboxTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[browser_automation_preview]]
        browser_automation_preview: BrowserAutomationToolParameters
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.BROWSER_AUTOMATION_PREVIEW]


    class azure.ai.extensions.openai.projects.BrowserAutomationToolConnectionParameters(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.extensions.openai.projects.BrowserAutomationToolParameters(TypedDict, total=False):
        key "connection": Required[BrowserAutomationToolConnectionParameters]
        connection: BrowserAutomationToolConnectionParameters


    class azure.ai.extensions.openai.projects.CaptureStructuredOutputsTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "outputs": Required[StructuredOutputDefinition]
        key "type": Required[Literal[capture_structured_outputs]]
        description: str
        name: str
        outputs: StructuredOutputDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]


    class azure.ai.extensions.openai.projects.ChartCoordinate(TypedDict, total=False):
        key "size": Required[int]
        key "x": Required[int]
        key "y": Required[int]
        size: int
        x: int
        y: int


    class azure.ai.extensions.openai.projects.ChatSummaryMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal[chat_summary]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[MemoryItemKind.CHAT_SUMMARY]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.extensions.openai.projects.ClusterInsightResult(TypedDict, total=False):
        key "clusters": Required[list[InsightCluster]]
        key "summary": Required[InsightSummary]
        clusters: list[InsightCluster]
        coordinates: dict[str, ChartCoordinate]
        summary: InsightSummary


    class azure.ai.extensions.openai.projects.ClusterTokenUsage(TypedDict, total=False):
        key "inputTokenUsage": Required[int]
        key "outputTokenUsage": Required[int]
        key "totalTokenUsage": Required[int]
        input_token_usage: int
        output_token_usage: int
        total_token_usage: int


    class azure.ai.extensions.openai.projects.CodeBasedEvaluatorDefinition(TypedDict, total=False):
        key "blob_uri": str
        key "code_text": str
        key "entry_point": str
        key "image_tag": str
        key "type": Required[Literal[code]]
        blob_uri: str
        code_text: str
        data_schema: dict[str, Any]
        entry_point: str
        image_tag: str
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.CODE]


    class azure.ai.extensions.openai.projects.CodeConfiguration(TypedDict, total=False):
        key "content_hash": str
        key "dependency_resolution": Required[Literal["bundled", "remote_build"]]
        key "entry_point": Required[list[str]]
        key "runtime": Required[str]
        content_hash: str
        dependency_resolution: CodeDependencyResolution
        entry_point: list[str]
        runtime: str


    class azure.ai.extensions.openai.projects.CodeInterpreterTool(TypedDict, total=False):
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "description": str
        key "name": str
        key "type": Required[Literal[code_interpreter]]
        container: Union[str, AutoCodeInterpreterToolParam]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.CODE_INTERPRETER]


    class azure.ai.extensions.openai.projects.CodeInterpreterToolboxTool(TypedDict, total=False):
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "description": str
        key "name": str
        key "type": Required[Literal[code_interpreter]]
        container: Union[str, AutoCodeInterpreterToolParam]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.CODE_INTERPRETER]


    class azure.ai.extensions.openai.projects.ComparisonFilter(TypedDict, total=False):
        key "key": Required[str]
        key "type": Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
        key "value": Required[Union[str, float, bool, list[Union[str, float]]]]
        key: str
        type: Literal[eq, ne, gt, gte, lt, lte, in, nin]
        value: Union[str, float, bool, list[Union[str, float]]]


    class azure.ai.extensions.openai.projects.CompoundFilter(TypedDict, total=False):
        key "filters": Required[list[Union[ComparisonFilter, Any]]]
        key "type": Required[Literal["and", "or"]]
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal[and, or]


    class azure.ai.extensions.openai.projects.ComputerTool(TypedDict, total=False):
        key "type": Required[Literal[computer]]
        type: Literal[ToolType.COMPUTER]


    class azure.ai.extensions.openai.projects.ComputerUsePreviewTool(TypedDict, total=False):
        key "display_height": Required[int]
        key "display_width": Required[int]
        key "environment": Required[Literal["windows", "mac", "linux", "ubuntu", "browser"]]
        key "type": Required[Literal[computer_use_preview]]
        display_height: int
        display_width: int
        environment: ComputerEnvironment
        type: Literal[ToolType.COMPUTER_USE_PREVIEW]


    class azure.ai.extensions.openai.projects.Connection(TypedDict, total=False):
        key "credentials": Required[BaseCredentials]
        key "id": Required[str]
        key "isDefault": Required[bool]
        key "metadata": Required[dict[str, str]]
        key "name": Required[str]
        key "target": Required[str]
        key "type": Required[Literal["AzureOpenAI", "AzureBlob", "AzureStorageAccount", "CognitiveSearch", "CosmosDB", "ApiKey", "AppConfig", "AppInsights", "CustomKeys", "RemoteTool_Preview"]]
        credentials: BaseCredentials
        id: str
        is_default: bool
        metadata: dict[str, str]
        name: str
        target: str
        type: ConnectionType


    class azure.ai.extensions.openai.projects.ContainerAutoParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal[container_auto]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        skills: list[ContainerSkill]
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]


    class azure.ai.extensions.openai.projects.ContainerConfiguration(TypedDict, total=False):
        key "image": Required[str]
        image: str


    class azure.ai.extensions.openai.projects.ContainerNetworkPolicyAllowlistParam(TypedDict, total=False):
        key "allowed_domains": Required[list[str]]
        key "type": Required[Literal[allowlist]]
        allowed_domains: list[str]
        domain_secrets: list[ContainerNetworkPolicyDomainSecretParam]
        type: Literal[ContainerNetworkPolicyParamType.ALLOWLIST]


    class azure.ai.extensions.openai.projects.ContainerNetworkPolicyDisabledParam(TypedDict, total=False):
        key "type": Required[Literal[disabled]]
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]


    class azure.ai.extensions.openai.projects.ContainerNetworkPolicyDomainSecretParam(TypedDict, total=False):
        key "domain": Required[str]
        key "name": Required[str]
        key "value": Required[str]
        domain: str
        name: str
        value: str


    class azure.ai.extensions.openai.projects.ContainerNetworkPolicyParamType(TypedDict):


    class azure.ai.extensions.openai.projects.ContainerSkillType(TypedDict):


    class azure.ai.extensions.openai.projects.ContinuousEvaluationRuleAction(TypedDict, total=False):
        key "evalId": Required[str]
        key "maxHourlyRuns": int
        key "samplingRate": float
        key "type": Required[Literal[continuous_evaluation]]
        eval_id: str
        max_hourly_runs: int
        sampling_rate: float
        type: Literal[EvaluationRuleActionType.CONTINUOUS_EVALUATION]


    class azure.ai.extensions.openai.projects.CosmosDBIndex(TypedDict, total=False):
        key "connectionName": Required[str]
        key "containerName": Required[str]
        key "databaseName": Required[str]
        key "description": str
        key "embeddingConfiguration": Required[EmbeddingConfiguration]
        key "fieldMapping": Required[FieldMapping]
        key "id": str
        key "name": Required[str]
        key "type": Required[Literal[cosmos_db]]
        key "version": Required[str]
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


    class azure.ai.extensions.openai.projects.CreateAgentVersionFromManifestRequest(TypedDict, total=False):
        key "description": str
        key "manifest_id": Required[str]
        key "parameter_values": Required[dict[str, Any]]
        description: str
        manifest_id: str
        metadata: dict[str, str]
        parameter_values: dict[str, Any]


    class azure.ai.extensions.openai.projects.CreateAgentVersionRequest(TypedDict, total=False):
        key "blueprint_reference": ForwardRef('AgentBlueprintReference', module='types')
        key "definition": Required[AgentDefinition]
        key "description": str
        key "draft": bool
        blueprint_reference: AgentBlueprintReference
        definition: AgentDefinition
        description: str
        draft: bool
        metadata: dict[str, str]


    class azure.ai.extensions.openai.projects.CreateAsyncResponse(TypedDict, total=False):
        key "location": str
        key "operationResult": Optional[str]
        location: str
        operation_result: str


    class azure.ai.extensions.openai.projects.CreateMemoryRequest(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[MemoryItemKind[_, _, a, r, g, s, _, _]]
        key "scope": Required[str]
        content: str
        kind: MemoryItemKind
        scope: str


    class azure.ai.extensions.openai.projects.CreateMemoryStoreRequest(TypedDict, total=False):
        key "definition": Required[MemoryStoreDefinition]
        key "description": str
        key "name": Required[str]
        definition: MemoryStoreDefinition
        description: str
        metadata: dict[str, str]
        name: str


    class azure.ai.extensions.openai.projects.CreateOrUpdateRoutineRequest(TypedDict, total=False):
        key "action": ForwardRef('RoutineAction', module='types')
        key "description": str
        key "enabled": bool
        action: RoutineAction
        description: str
        enabled: bool
        triggers: dict[str, RoutineTrigger]


    class azure.ai.extensions.openai.projects.CreateSessionRequest(TypedDict, total=False):
        key "agent_session_id": str
        key "version_indicator": Required[VersionIndicator]
        agent_session_id: str
        version_indicator: VersionIndicator


    class azure.ai.extensions.openai.projects.CreateSkillVersionFromFilesBody(TypedDict, total=False):
        key "default": bool
        key "files": Required[list[Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]]]
        default: bool
        files: list[FileType]


    class azure.ai.extensions.openai.projects.CreateSkillVersionRequest(TypedDict, total=False):
        key "default": bool
        key "inline_content": ForwardRef('SkillInlineContent', module='types')
        default: bool
        inline_content: SkillInlineContent


    class azure.ai.extensions.openai.projects.CreateToolboxVersionRequest(TypedDict, total=False):
        key "description": str
        key "policies": ForwardRef('ToolboxPolicies', module='types')
        key "tools": Required[list[ToolboxTool]]
        description: str
        metadata: dict[str, str]
        policies: ToolboxPolicies
        skills: list[ToolboxSkill]
        tools: list[ToolboxTool]


    class azure.ai.extensions.openai.projects.CredentialType(TypedDict):


    class azure.ai.extensions.openai.projects.CronTrigger(TypedDict, total=False):
        key "endTime": str
        key "expression": Required[str]
        key "startTime": str
        key "timeZone": str
        key "type": Required[Literal[cron]]
        end_time: str
        expression: str
        start_time: str
        time_zone: str
        type: Literal[TriggerType.CRON]


    class azure.ai.extensions.openai.projects.CustomCredential(TypedDict, total=False):
        key "type": Required[Literal[custom]]
        type: Literal[CredentialType.CUSTOM]


    class azure.ai.extensions.openai.projects.CustomGrammarFormatParam(TypedDict, total=False):
        key "definition": Required[str]
        key "syntax": Required[Literal["lark", "regex"]]
        key "type": Required[Literal[grammar]]
        definition: str
        syntax: GrammarSyntax1
        type: Literal[CustomToolParamFormatType.GRAMMAR]


    class azure.ai.extensions.openai.projects.CustomRoutineTrigger(TypedDict, total=False):
        key "event_name": str
        key "parameters": Required[dict[str, Any]]
        key "provider": Required[str]
        key "type": Required[Literal[custom]]
        event_name: str
        parameters: dict[str, Any]
        provider: str
        type: Literal[RoutineTriggerType.CUSTOM]


    class azure.ai.extensions.openai.projects.CustomTextFormatParam(TypedDict, total=False):
        key "type": Required[Literal[text]]
        type: Literal[CustomToolParamFormatType.TEXT]


    class azure.ai.extensions.openai.projects.CustomToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": str
        key "format": ForwardRef('CustomToolParamFormat', module='types')
        key "name": Required[str]
        key "type": Required[Literal[custom]]
        defer_loading: bool
        description: str
        format: CustomToolParamFormat
        name: str
        type: Literal[ToolType.CUSTOM]


    class azure.ai.extensions.openai.projects.CustomToolParamFormatType(TypedDict):


    class azure.ai.extensions.openai.projects.DailyRecurrenceSchedule(TypedDict, total=False):
        key "hours": Required[list[int]]
        key "type": Required[Literal[daily]]
        hours: list[int]
        type: Literal[RecurrenceType.DAILY]


    class azure.ai.extensions.openai.projects.DataGenerationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "finished_at": int
        key "id": Required[str]
        key "inputs": ForwardRef('DataGenerationJobInputs', module='types')
        key "result": ForwardRef('DataGenerationJobResult', module='types')
        key "status": Required[Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]]
        created_at: int
        error: ApiError
        finished_at: int
        id: str
        inputs: DataGenerationJobInputs
        result: DataGenerationJobResult
        status: JobStatus


    class azure.ai.extensions.openai.projects.DataGenerationJobInputs(TypedDict, total=False):
        key "name": Required[str]
        key "options": Required[DataGenerationJobOptions]
        key "output_options": ForwardRef('DataGenerationJobOutputOptions', module='types')
        key "scenario": Required[Literal["supervised_finetuning", "reinforcement_finetuning", "evaluation"]]
        key "sources": Required[list[DataGenerationJobSource]]
        name: str
        options: DataGenerationJobOptions
        output_options: DataGenerationJobOutputOptions
        scenario: DataGenerationJobScenario
        sources: list[DataGenerationJobSource]


    class azure.ai.extensions.openai.projects.DataGenerationJobOutputOptions(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str
        tags: dict[str, str]


    class azure.ai.extensions.openai.projects.DataGenerationJobOutputType(TypedDict):


    class azure.ai.extensions.openai.projects.DataGenerationJobResult(TypedDict, total=False):
        key "generated_samples": Required[int]
        key "token_usage": ForwardRef('DataGenerationTokenUsage', module='types')
        generated_samples: int
        outputs: list[DataGenerationJobOutput]
        token_usage: DataGenerationTokenUsage


    class azure.ai.extensions.openai.projects.DataGenerationJobSourceType(TypedDict):


    class azure.ai.extensions.openai.projects.DataGenerationJobType(TypedDict):


    class azure.ai.extensions.openai.projects.DataGenerationModelOptions(TypedDict, total=False):
        key "model": Required[str]
        model: str


    class azure.ai.extensions.openai.projects.DataGenerationTokenUsage(TypedDict, total=False):
        key "completion_tokens": Required[int]
        key "prompt_tokens": Required[int]
        key "total_tokens": Required[int]
        completion_tokens: int
        prompt_tokens: int
        total_tokens: int


    class azure.ai.extensions.openai.projects.DatasetCredential(TypedDict, total=False):
        key "blobReference": Required[BlobReference]
        blob_reference: BlobReference


    class azure.ai.extensions.openai.projects.DatasetDataGenerationJobOutput(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": str
        key "type": Required[Literal[dataset]]
        key "version": str
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[DataGenerationJobOutputType.DATASET]
        version: str


    class azure.ai.extensions.openai.projects.DatasetEvaluatorGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "type": Required[Literal[dataset]]
        key "version": str
        description: str
        name: str
        type: Literal[EvaluatorGenerationJobSourceType.DATASET]
        version: str


    class azure.ai.extensions.openai.projects.DatasetReference(TypedDict, total=False):
        key "name": Required[str]
        key "version": Required[str]
        name: str
        version: str


    class azure.ai.extensions.openai.projects.DatasetType(TypedDict):


    class azure.ai.extensions.openai.projects.DeleteAgentResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal[agent_deleted]]
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_DELETED]


    class azure.ai.extensions.openai.projects.DeleteAgentVersionResponse(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal[agent_version_deleted]]
        key "version": Required[str]
        deleted: bool
        name: str
        object: Literal[AgentObjectType.AGENT_VERSION_DELETED]
        version: str


    class azure.ai.extensions.openai.projects.DeleteMemoryResult(TypedDict, total=False):
        key "deleted": Required[bool]
        key "memory_id": Required[str]
        key "object": Required[Literal[memory_deleted]]
        deleted: bool
        memory_id: str
        object: Literal[MemoryStoreObjectType.MEMORY_DELETED]


    class azure.ai.extensions.openai.projects.DeleteMemoryStoreResult(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal[memory_store_deleted]]
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_DELETED]


    class azure.ai.extensions.openai.projects.DeleteScopeRequest(TypedDict, total=False):
        key "scope": Required[str]
        scope: str


    class azure.ai.extensions.openai.projects.DeleteSkillResult(TypedDict, total=False):
        key "deleted": Required[bool]
        key "id": Required[str]
        key "name": Required[str]
        deleted: bool
        id: str
        name: str


    class azure.ai.extensions.openai.projects.DeleteSkillVersionResult(TypedDict, total=False):
        key "deleted": Required[bool]
        key "id": Required[str]
        key "name": Required[str]
        key "version": Required[str]
        deleted: bool
        id: str
        name: str
        version: str


    class azure.ai.extensions.openai.projects.Deployment(TypedDict, total=False):
        key "capabilities": Required[dict[str, str]]
        key "connectionName": str
        key "modelName": Required[str]
        key "modelPublisher": Required[str]
        key "modelVersion": Required[str]
        key "name": Required[str]
        key "sku": Required[ModelDeploymentSku]
        key "type": Required[Literal[model_deployment]]
        capabilities: dict[str, str]
        connection_name: str
        model_name: str
        model_publisher: str
        model_version: str
        name: str
        sku: ModelDeploymentSku
        type: Literal[DeploymentType.MODEL_DEPLOYMENT]


    class azure.ai.extensions.openai.projects.DeploymentType(TypedDict):


    class azure.ai.extensions.openai.projects.Dimension(TypedDict, total=False):
        key "always_applicable": bool
        key "description": Required[str]
        key "id": Required[str]
        key "weight": Required[int]
        always_applicable: bool
        description: str
        id: str
        weight: int


    class azure.ai.extensions.openai.projects.DispatchRoutineAsyncRequest(TypedDict, total=False):
        key "payload": ForwardRef('RoutineDispatchPayload', module='types')
        payload: RoutineDispatchPayload


    class azure.ai.extensions.openai.projects.DispatchRoutineResult(TypedDict, total=False):
        key "action_correlation_id": str
        key "dispatch_id": str
        key "task_id": str
        action_correlation_id: str
        dispatch_id: str
        task_id: str


    class azure.ai.extensions.openai.projects.EmbeddingConfiguration(TypedDict, total=False):
        key "embeddingField": Required[str]
        key "modelDeploymentName": Required[str]
        embedding_field: str
        model_deployment_name: str


    class azure.ai.extensions.openai.projects.EmptyModelParam(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.EndpointBasedEvaluatorDefinition(TypedDict, total=False):
        key "connection_name": Required[str]
        key "type": Required[Literal[endpoint]]
        connection_name: str
        data_schema: dict[str, Any]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        type: Literal[EvaluatorDefinitionType.ENDPOINT]


    class azure.ai.extensions.openai.projects.EntraAuthorizationScheme(TypedDict, total=False):
        key "type": Required[Literal[entra]]
        type: Literal[AgentEndpointAuthorizationSchemeType.ENTRA]


    class azure.ai.extensions.openai.projects.EntraIDCredentials(TypedDict, total=False):
        key "type": Required[Literal[entra_id]]
        type: Literal[CredentialType.ENTRA_ID]


    class azure.ai.extensions.openai.projects.EvalResult(TypedDict, total=False):
        key "name": Required[str]
        key "passed": Required[bool]
        key "score": Required[float]
        key "type": Required[str]
        name: str
        passed: bool
        score: float
        type: str


    class azure.ai.extensions.openai.projects.EvalRunResultCompareItem(TypedDict, total=False):
        key "deltaEstimate": Required[float]
        key "pValue": Required[float]
        key "treatmentEffect": Required[Literal["TooFewSamples", "Inconclusive", "Changed", "Improved", "Degraded"]]
        key "treatmentRunId": Required[str]
        key "treatmentRunSummary": Required[EvalRunResultSummary]
        delta_estimate: float
        p_value: float
        treatment_effect: TreatmentEffectType
        treatment_run_id: str
        treatment_run_summary: EvalRunResultSummary


    class azure.ai.extensions.openai.projects.EvalRunResultComparison(TypedDict, total=False):
        key "baselineRunSummary": Required[EvalRunResultSummary]
        key "compareItems": Required[list[EvalRunResultCompareItem]]
        key "evaluator": Required[str]
        key "metric": Required[str]
        key "testingCriteria": Required[str]
        baseline_run_summary: EvalRunResultSummary
        compare_items: list[EvalRunResultCompareItem]
        evaluator: str
        metric: str
        testing_criteria: str


    class azure.ai.extensions.openai.projects.EvalRunResultSummary(TypedDict, total=False):
        key "average": Required[float]
        key "runId": Required[str]
        key "sampleCount": Required[int]
        key "standardDeviation": Required[float]
        average: float
        run_id: str
        sample_count: int
        standard_deviation: float


    class azure.ai.extensions.openai.projects.EvaluationComparisonInsightRequest(TypedDict, total=False):
        key "baselineRunId": Required[str]
        key "evalId": Required[str]
        key "treatmentRunIds": Required[list[str]]
        key "type": Required[Literal[evaluation_comparison]]
        baseline_run_id: str
        eval_id: str
        treatment_run_ids: list[str]
        type: Literal[InsightType.EVALUATION_COMPARISON]


    class azure.ai.extensions.openai.projects.EvaluationComparisonInsightResult(TypedDict, total=False):
        key "comparisons": Required[list[EvalRunResultComparison]]
        key "method": Required[str]
        key "type": Required[Literal[evaluation_comparison]]
        comparisons: list[EvalRunResultComparison]
        method: str
        type: Literal[InsightType.EVALUATION_COMPARISON]


    class azure.ai.extensions.openai.projects.EvaluationResultSample(TypedDict, total=False):
        key "correlationInfo": Required[dict[str, Any]]
        key "evaluationResult": Required[EvalResult]
        key "features": Required[dict[str, Any]]
        key "id": Required[str]
        key "type": Required[Literal[evaluation_result_sample]]
        correlation_info: dict[str, Any]
        evaluation_result: EvalResult
        features: dict[str, Any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]


    class azure.ai.extensions.openai.projects.EvaluationRule(TypedDict, total=False):
        key "action": Required[EvaluationRuleAction]
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "eventType": Required[Literal["responseCompleted", "manual"]]
        key "filter": ForwardRef('EvaluationRuleFilter', module='types')
        key "id": Required[str]
        key "systemData": Required[dict[str, str]]
        action: EvaluationRuleAction
        description: str
        display_name: str
        enabled: bool
        event_type: EvaluationRuleEventType
        filter: EvaluationRuleFilter
        id: str
        system_data: dict[str, str]


    class azure.ai.extensions.openai.projects.EvaluationRuleActionType(TypedDict):


    class azure.ai.extensions.openai.projects.EvaluationRuleFilter(TypedDict, total=False):
        key "agentName": Required[str]
        agent_name: str


    class azure.ai.extensions.openai.projects.EvaluationRunClusterInsightRequest(TypedDict, total=False):
        key "evalId": Required[str]
        key "modelConfiguration": ForwardRef('InsightModelConfiguration', module='types')
        key "runIds": Required[list[str]]
        key "type": Required[Literal[evaluation_run_cluster_insight]]
        eval_id: str
        model_configuration: InsightModelConfiguration
        run_ids: list[str]
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]


    class azure.ai.extensions.openai.projects.EvaluationRunClusterInsightResult(TypedDict, total=False):
        key "clusterInsight": Required[ClusterInsightResult]
        key "type": Required[Literal[evaluation_run_cluster_insight]]
        cluster_insight: ClusterInsightResult
        type: Literal[InsightType.EVALUATION_RUN_CLUSTER_INSIGHT]


    class azure.ai.extensions.openai.projects.EvaluationScheduleTask(TypedDict, total=False):
        key "evalId": Required[str]
        key "evalRun": Required[dict[str, Any]]
        key "type": Required[Literal[evaluation]]
        configuration: dict[str, str]
        eval_id: str
        eval_run: dict[str, Any]
        type: Literal[ScheduleTaskType.EVALUATION]


    class azure.ai.extensions.openai.projects.EvaluationTaxonomy(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": Required[str]
        key "taxonomyInput": Required[EvaluationTaxonomyInput]
        key "version": Required[str]
        description: str
        id: str
        name: str
        properties: dict[str, str]
        tags: dict[str, str]
        taxonomyCategories: list[TaxonomyCategory]
        taxonomy_categories: list[TaxonomyCategory]
        taxonomy_input: EvaluationTaxonomyInput
        version: str


    class azure.ai.extensions.openai.projects.EvaluationTaxonomyInput(TypedDict, total=False):
        key "riskCategories": Required[list[Literal["HateUnfairness", "Violence", "Sexual", "SelfHarm", "ProtectedMaterial", "CodeVulnerability", "UngroundedAttributes", "ProhibitedActions", "SensitiveDataLeakage", "TaskAdherence"]]]
        key "target": Required[EvaluationTarget]
        key "type": Required[Literal[agent]]
        risk_categories: list[RiskCategory]
        target: EvaluationTarget
        type: Literal[EvaluationTaxonomyInputType.AGENT]


    class azure.ai.extensions.openai.projects.EvaluationTaxonomyInputType(TypedDict):


    class azure.ai.extensions.openai.projects.EvaluatorCredentialRequest(TypedDict, total=False):
        key "blob_uri": Required[str]
        blob_uri: str


    class azure.ai.extensions.openai.projects.EvaluatorDefinitionType(TypedDict):


    class azure.ai.extensions.openai.projects.EvaluatorGenerationArtifacts(TypedDict, total=False):
        key "dataset": Required[DatasetReference]
        key "kinds": Required[list[str]]
        dataset: DatasetReference
        kinds: list[str]


    class azure.ai.extensions.openai.projects.EvaluatorGenerationInputs(TypedDict, total=False):
        key "evaluator_description": str
        key "evaluator_display_name": str
        key "evaluator_name": Required[str]
        key "model": Required[str]
        key "sources": Required[list[EvaluatorGenerationJobSource]]
        evaluator_description: str
        evaluator_display_name: str
        evaluator_name: str
        model: str
        sources: list[EvaluatorGenerationJobSource]


    class azure.ai.extensions.openai.projects.EvaluatorGenerationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "finished_at": int
        key "id": Required[str]
        key "inputs": ForwardRef('EvaluatorGenerationInputs', module='types')
        key "result": ForwardRef('EvaluatorVersion', module='types')
        key "status": Required[Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]]
        key "usage": ForwardRef('EvaluatorGenerationTokenUsage', module='types')
        created_at: int
        error: ApiError
        finished_at: int
        id: str
        inputs: EvaluatorGenerationInputs
        result: EvaluatorVersion
        status: JobStatus
        usage: EvaluatorGenerationTokenUsage


    class azure.ai.extensions.openai.projects.EvaluatorGenerationJobSourceType(TypedDict):


    class azure.ai.extensions.openai.projects.EvaluatorGenerationTokenUsage(TypedDict, total=False):
        key "input_tokens": Required[int]
        key "output_tokens": Required[int]
        key "total_tokens": Required[int]
        input_tokens: int
        output_tokens: int
        total_tokens: int


    class azure.ai.extensions.openai.projects.EvaluatorMetric(TypedDict, total=False):
        key "desirable_direction": Literal["increase", "decrease", "neutral"]
        key "is_primary": bool
        key "max_value": float
        key "min_value": float
        key "threshold": float
        key "type": Literal["ordinal", "continuous", "boolean"]
        desirable_direction: EvaluatorMetricDirection
        is_primary: bool
        max_value: float
        min_value: float
        threshold: float
        type: EvaluatorMetricType


    class azure.ai.extensions.openai.projects.EvaluatorVersion(TypedDict, total=False):
        key "categories": Required[list[Literal["quality", "safety", "agents"]]]
        key "created_at": Required[str]
        key "created_by": Required[str]
        key "definition": Required[EvaluatorDefinition]
        key "description": str
        key "display_name": str
        key "evaluator_type": Required[Literal["builtin", "custom"]]
        key "generation_artifacts": ForwardRef('EvaluatorGenerationArtifacts', module='types')
        key "id": str
        key "modified_at": Required[str]
        key "name": Required[str]
        key "version": Required[str]
        categories: list[EvaluatorCategory]
        created_at: str
        created_by: str
        definition: EvaluatorDefinition
        description: str
        display_name: str
        evaluator_type: EvaluatorType
        generation_artifacts: EvaluatorGenerationArtifacts
        id: str
        metadata: dict[str, str]
        modified_at: str
        name: str
        supported_evaluation_levels: list[Literal["turn", "conversation"]]
        tags: dict[str, str]
        version: str


    class azure.ai.extensions.openai.projects.ExternalAgentDefinition(TypedDict, total=False):
        key "kind": Required[Literal[external]]
        key "otel_agent_id": str
        key "rai_config": ForwardRef('RaiConfig', module='types')
        kind: Literal[AgentKind.EXTERNAL]
        otel_agent_id: str
        rai_config: RaiConfig


    class azure.ai.extensions.openai.projects.FabricDataAgentToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.extensions.openai.projects.FabricIQPreviewTool(TypedDict, total=False):
        key "project_connection_id": Required[str]
        key "require_approval": Optional[Union[MCPToolRequireApproval, str]]
        key "server_label": str
        key "server_url": str
        key "type": Required[Literal[fabric_iq_preview]]
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, str]
        server_label: str
        server_url: str
        type: Literal[ToolType.FABRIC_IQ_PREVIEW]


    class azure.ai.extensions.openai.projects.FabricIQPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        key "require_approval": Optional[Union[MCPToolRequireApproval, str]]
        key "server_label": str
        key "server_url": str
        key "type": Required[Literal[fabric_iq_preview]]
        description: str
        name: str
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, str]
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FABRIC_IQ_PREVIEW]


    class azure.ai.extensions.openai.projects.FieldMapping(TypedDict, total=False):
        key "contentFields": Required[list[str]]
        key "filepathField": str
        key "titleField": str
        key "urlField": str
        content_fields: list[str]
        filepath_field: str
        metadataFields: list[str]
        metadata_fields: list[str]
        title_field: str
        url_field: str
        vectorFields: list[str]
        vector_fields: list[str]


    class azure.ai.extensions.openai.projects.FileDataGenerationJobOutput(TypedDict, total=False):
        key "filename": Required[str]
        key "id": Required[str]
        key "type": Required[Literal[file]]
        filename: str
        id: str
        type: Literal[DataGenerationJobOutputType.FILE]


    class azure.ai.extensions.openai.projects.FileDataGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "type": Required[Literal[file]]
        description: str
        id: str
        type: Literal[DataGenerationJobSourceType.FILE]


    class azure.ai.extensions.openai.projects.FileDatasetVersion(TypedDict, total=False):
        key "connectionName": str
        key "dataUri": Required[str]
        key "description": str
        key "id": str
        key "isReference": bool
        key "name": Required[str]
        key "type": Required[Literal[uri_file]]
        key "version": Required[str]
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FILE]
        version: str


    class azure.ai.extensions.openai.projects.FileSearchTool(TypedDict, total=False):
        key "description": str
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "name": str
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal[file_search]]
        key "vector_store_ids": Required[list[str]]
        description: str
        filters: Filters
        max_num_results: int
        name: str
        ranking_options: RankingOptions
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.FILE_SEARCH]
        vector_store_ids: list[str]


    class azure.ai.extensions.openai.projects.FileSearchToolboxTool(TypedDict, total=False):
        key "description": str
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "name": str
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal[file_search]]
        description: str
        filters: Filters
        max_num_results: int
        name: str
        ranking_options: RankingOptions
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.FILE_SEARCH]
        vector_store_ids: list[str]


    class azure.ai.extensions.openai.projects.FixedRatioVersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[fixed_ratio]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.extensions.openai.projects.FolderDatasetVersion(TypedDict, total=False):
        key "connectionName": str
        key "dataUri": Required[str]
        key "description": str
        key "id": str
        key "isReference": bool
        key "name": Required[str]
        key "type": Required[Literal[uri_folder]]
        key "version": Required[str]
        connection_name: str
        data_uri: str
        description: str
        id: str
        is_reference: bool
        name: str
        tags: dict[str, str]
        type: Literal[DatasetType.URI_FOLDER]
        version: str


    class azure.ai.extensions.openai.projects.FoundryModelWarning(TypedDict, total=False):
        key "code": Literal["RuntimeDependentArtifact", "UnclassifiedArtifact"]
        key "message": str
        code: FoundryModelWarningCode
        message: str


    class azure.ai.extensions.openai.projects.FunctionShellToolParam(TypedDict, total=False):
        key "description": str
        key "environment": Optional[FunctionShellToolParamEnvironment]
        key "name": str
        key "type": Required[Literal[shell]]
        description: str
        environment: FunctionShellToolParamEnvironment
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.SHELL]


    class azure.ai.extensions.openai.projects.FunctionShellToolParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal[container_reference]]
        container_id: str
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]


    class azure.ai.extensions.openai.projects.FunctionShellToolParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal[local]]
        skills: list[LocalSkillParam]
        type: Literal[FunctionShellToolParamEnvironmentType.LOCAL]


    class azure.ai.extensions.openai.projects.FunctionShellToolParamEnvironmentType(TypedDict):


    class azure.ai.extensions.openai.projects.FunctionTool(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Required[Optional[dict[str, Any]]]
        key "strict": Required[Optional[bool]]
        key "type": Required[Literal[function]]
        defer_loading: bool
        description: str
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]


    class azure.ai.extensions.openai.projects.FunctionToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Optional[EmptyModelParam]
        key "strict": Optional[bool]
        key "type": Required[Literal["function"]]
        defer_loading: bool
        description: str
        name: str
        parameters: EmptyModelParam
        strict: bool
        type: Literal[function]


    class azure.ai.extensions.openai.projects.GitHubIssueRoutineTrigger(TypedDict, total=False):
        key "connection_id": Required[str]
        key "issue_event": Required[Literal["opened", "closed"]]
        key "owner": Required[str]
        key "repository": Required[str]
        key "type": Required[Literal[github_issue]]
        connection_id: str
        issue_event: GitHubIssueEvent
        owner: str
        repository: str
        type: Literal[RoutineTriggerType.GITHUB_ISSUE]


    class azure.ai.extensions.openai.projects.HeaderTelemetryEndpointAuth(TypedDict, total=False):
        key "header_name": Required[str]
        key "secret_id": Required[str]
        key "secret_key": Required[str]
        key "type": Required[Literal[header]]
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]


    class azure.ai.extensions.openai.projects.HostedAgentDefinition(TypedDict, total=False):
        key "code_configuration": ForwardRef('CodeConfiguration', module='types')
        key "container_configuration": ForwardRef('ContainerConfiguration', module='types')
        key "cpu": Required[str]
        key "kind": Required[Literal[hosted]]
        key "memory": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "telemetry_config": ForwardRef('TelemetryConfig', module='types')
        code_configuration: CodeConfiguration
        container_configuration: ContainerConfiguration
        cpu: str
        environment_variables: dict[str, str]
        kind: Literal[AgentKind.HOSTED]
        memory: str
        protocol_versions: list[ProtocolVersionRecord]
        rai_config: RaiConfig
        telemetry_config: TelemetryConfig


    class azure.ai.extensions.openai.projects.HourlyRecurrenceSchedule(TypedDict, total=False):
        key "type": Required[Literal[hourly]]
        type: Literal[RecurrenceType.HOURLY]


    class azure.ai.extensions.openai.projects.HumanEvaluationPreviewRuleAction(TypedDict, total=False):
        key "templateId": Required[str]
        key "type": Required[Literal[human_evaluation_preview]]
        template_id: str
        type: Literal[EvaluationRuleActionType.HUMAN_EVALUATION_PREVIEW]


    class azure.ai.extensions.openai.projects.HybridSearchOptions(TypedDict, total=False):
        key "embedding_weight": Required[float]
        key "text_weight": Required[float]
        embedding_weight: float
        text_weight: float


    class azure.ai.extensions.openai.projects.ImageGenTool(TypedDict, total=False):
        key "action": Literal["generate", "edit", "auto"]
        key "background": Literal["transparent", "opaque", "auto"]
        key "description": str
        key "input_fidelity": Optional[Literal["high", "low"]]
        key "input_image_mask": ForwardRef('ImageGenToolInputImageMask', module='types')
        key "model": Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]
        key "moderation": Literal["auto", "low"]
        key "name": str
        key "output_compression": int
        key "output_format": Literal["png", "webp", "jpeg"]
        key "partial_images": int
        key "quality": Literal["low", "medium", "high", "auto"]
        key "size": Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]
        key "type": Required[Literal[image_generation]]
        action: ImageGenAction
        background: Literal[transparent, opaque, auto]
        description: str
        input_fidelity: InputFidelity
        input_image_mask: ImageGenToolInputImageMask
        model: Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]
        moderation: Literal[auto, low]
        name: str
        output_compression: int
        output_format: Literal[png, webp, jpeg]
        partial_images: int
        quality: Literal[low, medium, high, auto]
        size: Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.IMAGE_GENERATION]


    class azure.ai.extensions.openai.projects.ImageGenToolInputImageMask(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        file_id: str
        image_url: str


    class azure.ai.extensions.openai.projects.IndexType(TypedDict):


    class azure.ai.extensions.openai.projects.InlineSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "source": Required[InlineSkillSourceParam]
        key "type": Required[Literal[inline]]
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[ContainerSkillType.INLINE]


    class azure.ai.extensions.openai.projects.InlineSkillSourceParam(TypedDict, total=False):
        key "data": Required[str]
        key "media_type": Required[Literal["application/zip"]]
        key "type": Required[Literal["base64"]]
        data: str
        media_type: Literal[application/zip]
        type: Literal[base64]


    class azure.ai.extensions.openai.projects.Insight(TypedDict, total=False):
        key "displayName": Required[str]
        key "id": Required[str]
        key "metadata": Required[InsightsMetadata]
        key "request": Required[InsightRequest]
        key "result": ForwardRef('InsightResult', module='types')
        key "state": Required[Literal["NotStarted", "Running", "Succeeded", "Failed", "Canceled"]]
        display_name: str
        insight_id: str
        metadata: InsightsMetadata
        request: InsightRequest
        result: InsightResult
        state: OperationState


    class azure.ai.extensions.openai.projects.InsightCluster(TypedDict, total=False):
        key "description": Required[str]
        key "id": Required[str]
        key "label": Required[str]
        key "suggestion": Required[str]
        key "suggestionTitle": Required[str]
        key "weight": Required[int]
        description: str
        id: str
        label: str
        samples: list[InsightSample]
        subClusters: list[InsightCluster]
        sub_clusters: list[InsightCluster]
        suggestion: str
        suggestion_title: str
        weight: int


    class azure.ai.extensions.openai.projects.InsightModelConfiguration(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        model_deployment_name: str


    class azure.ai.extensions.openai.projects.InsightSample(TypedDict, total=False):
        key "correlationInfo": Required[dict[str, Any]]
        key "evaluationResult": Required[EvalResult]
        key "features": Required[dict[str, Any]]
        key "id": Required[str]
        key "type": Required[Literal[evaluation_result_sample]]
        correlation_info: dict[str, Any]
        evaluation_result: EvalResult
        features: dict[str, Any]
        id: str
        type: Literal[SampleType.EVALUATION_RESULT_SAMPLE]


    class azure.ai.extensions.openai.projects.InsightScheduleTask(TypedDict, total=False):
        key "insight": Required[Insight]
        key "type": Required[Literal[insight]]
        configuration: dict[str, str]
        insight: Insight
        type: Literal[ScheduleTaskType.INSIGHT]


    class azure.ai.extensions.openai.projects.InsightSummary(TypedDict, total=False):
        key "method": Required[str]
        key "sampleCount": Required[int]
        key "uniqueClusterCount": Required[int]
        key "uniqueSubclusterCount": Required[int]
        key "usage": Required[ClusterTokenUsage]
        method: str
        sample_count: int
        unique_cluster_count: int
        unique_subcluster_count: int
        usage: ClusterTokenUsage


    class azure.ai.extensions.openai.projects.InsightType(TypedDict):


    class azure.ai.extensions.openai.projects.InsightsMetadata(TypedDict, total=False):
        key "completedAt": str
        key "createdAt": Required[str]
        completed_at: str
        created_at: str


    class azure.ai.extensions.openai.projects.InvocationsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.InvocationsWsProtocolConfiguration(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.InvokeAgentInvocationsApiDispatchPayload(TypedDict, total=False):
        key "input": Required[Any]
        key "type": Required[Literal[invoke_agent_invocations_api]]
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_INVOCATIONS_API]


    class azure.ai.extensions.openai.projects.InvokeAgentInvocationsApiRoutineAction(TypedDict, total=False):
        key "agent_endpoint_id": str
        key "agent_name": str
        key "input": Any
        key "session_id": str
        key "type": Required[Literal[invoke_agent_invocations_api]]
        agent_endpoint_id: str
        agent_name: str
        input: Any
        session_id: str
        type: Literal[RoutineActionType.INVOKE_AGENT_INVOCATIONS_API]


    class azure.ai.extensions.openai.projects.InvokeAgentResponsesApiDispatchPayload(TypedDict, total=False):
        key "input": Required[Any]
        key "type": Required[Literal[invoke_agent_responses_api]]
        input: Any
        type: Literal[RoutineDispatchPayloadType.INVOKE_AGENT_RESPONSES_API]


    class azure.ai.extensions.openai.projects.InvokeAgentResponsesApiRoutineAction(TypedDict, total=False):
        key "agent_endpoint_id": str
        key "agent_name": str
        key "conversation": str
        key "input": Any
        key "type": Required[Literal[invoke_agent_responses_api]]
        agent_endpoint_id: str
        agent_name: str
        conversation: str
        input: Any
        type: Literal[RoutineActionType.INVOKE_AGENT_RESPONSES_API]


    class azure.ai.extensions.openai.projects.ListMemoriesRequest(TypedDict, total=False):
        key "scope": Required[str]
        scope: str


    class azure.ai.extensions.openai.projects.LocalShellToolParam(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[local_shell]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.LOCAL_SHELL]


    class azure.ai.extensions.openai.projects.LocalSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "path": Required[str]
        description: str
        name: str
        path: str


    class azure.ai.extensions.openai.projects.LoraConfig(TypedDict, total=False):
        key "alpha": int
        key "dropout": float
        key "rank": int
        alpha: int
        dropout: float
        rank: int
        targetModules: list[str]
        target_modules: list[str]


    class azure.ai.extensions.openai.projects.MCPTool(TypedDict, total=False):
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
        key "type": Required[Literal[mcp]]
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


    class azure.ai.extensions.openai.projects.MCPToolFilter(TypedDict, total=False):
        key "read_only": bool
        read_only: bool
        tool_names: list[str]


    class azure.ai.extensions.openai.projects.MCPToolRequireApproval(TypedDict, total=False):
        key "always": ForwardRef('MCPToolFilter', module='types')
        key "never": ForwardRef('MCPToolFilter', module='types')
        always: MCPToolFilter
        never: MCPToolFilter


    class azure.ai.extensions.openai.projects.MCPToolboxTool(TypedDict, total=False):
        key "allowed_tools": Optional[Union[list[str], MCPToolFilter]]
        key "authorization": str
        key "connector_id": Literal["connector_dropbox", "connector_gmail", "connector_googlecalendar", "connector_googledrive", "connector_microsoftteams", "connector_outlookcalendar", "connector_outlookemail", "connector_sharepoint"]
        key "defer_loading": bool
        key "description": str
        key "headers": Optional[dict[str, str]]
        key "name": str
        key "project_connection_id": str
        key "require_approval": Optional[Union[MCPToolRequireApproval, Literal["always"], Literal["never"]]]
        key "server_description": str
        key "server_label": Required[str]
        key "server_url": str
        key "tunnel_id": str
        key "type": Required[Literal[mcp]]
        allowed_tools: Union[list[str], MCPToolFilter]
        authorization: str
        connector_id: Literal[connector_dropbox, connector_gmail, connector_googlecalendar, connector_googledrive, connector_microsoftteams,
        defer_loading: bool
        description: str
        headers: dict[str, str]
        name: str
        project_connection_id: str
        require_approval: Union[MCPToolRequireApproval, Literal[always], Literal[never]]
        server_description: str
        server_label: str
        server_url: str
        tool_configs: dict[str, ToolConfig]
        tunnel_id: str
        type: Literal[ToolboxToolType.MCP]


    class azure.ai.extensions.openai.projects.ManagedAgentIdentityBlueprintReference(TypedDict, total=False):
        key "blueprint_id": Required[str]
        key "type": Required[Literal[managed_agent_identity_blueprint]]
        blueprint_id: str
        type: Literal[AgentBlueprintReferenceType.MANAGED_AGENT_IDENTITY_BLUEPRINT]


    class azure.ai.extensions.openai.projects.ManagedAzureAISearchIndex(TypedDict, total=False):
        key "description": str
        key "id": str
        key "name": Required[str]
        key "type": Required[Literal[managed_azure_search]]
        key "vectorStoreId": Required[str]
        key "version": Required[str]
        description: str
        id: str
        name: str
        tags: dict[str, str]
        type: Literal[IndexType.MANAGED_AZURE_SEARCH]
        vector_store_id: str
        version: str


    class azure.ai.extensions.openai.projects.McpProtocolConfiguration(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.MemoryItemKind(TypedDict):


    class azure.ai.extensions.openai.projects.MemoryOperation(TypedDict, total=False):
        key "kind": Required[Literal["create", "update", "delete"]]
        key "memory_item": Required[MemoryItem]
        kind: MemoryOperationKind
        memory_item: MemoryItem


    class azure.ai.extensions.openai.projects.MemorySearchItem(TypedDict, total=False):
        key "memory_item": Required[MemoryItem]
        memory_item: MemoryItem


    class azure.ai.extensions.openai.projects.MemorySearchOptions(TypedDict, total=False):
        key "max_memories": int
        max_memories: int


    class azure.ai.extensions.openai.projects.MemorySearchPreviewTool(TypedDict, total=False):
        key "memory_store_name": Required[str]
        key "scope": Required[str]
        key "search_options": ForwardRef('MemorySearchOptions', module='types')
        key "type": Required[Literal[memory_search_preview]]
        key "update_delay": int
        memory_store_name: str
        scope: str
        search_options: MemorySearchOptions
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: int


    class azure.ai.extensions.openai.projects.MemoryStoreDefaultDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal[default]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: MemoryStoreDefaultOptions


    class azure.ai.extensions.openai.projects.MemoryStoreDefaultOptions(TypedDict, total=False):
        key "chat_summary_enabled": Required[bool]
        key "default_ttl_seconds": str
        key "procedural_memory_enabled": bool
        key "user_profile_details": str
        key "user_profile_enabled": Required[bool]
        chat_summary_enabled: bool
        default_ttl_seconds: str
        procedural_memory_enabled: bool
        user_profile_details: str
        user_profile_enabled: bool


    class azure.ai.extensions.openai.projects.MemoryStoreDefinition(TypedDict, total=False):
        key "chat_model": Required[str]
        key "embedding_model": Required[str]
        key "kind": Required[Literal[default]]
        key "options": ForwardRef('MemoryStoreDefaultOptions', module='types')
        chat_model: str
        embedding_model: str
        kind: Literal[MemoryStoreKind.DEFAULT]
        options: MemoryStoreDefaultOptions


    class azure.ai.extensions.openai.projects.MemoryStoreDeleteScopeResult(TypedDict, total=False):
        key "deleted": Required[bool]
        key "name": Required[str]
        key "object": Required[Literal[memory_store_scope_deleted]]
        key "scope": Required[str]
        deleted: bool
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE_SCOPE_DELETED]
        scope: str


    class azure.ai.extensions.openai.projects.MemoryStoreDetails(TypedDict, total=False):
        key "created_at": Required[int]
        key "definition": Required[MemoryStoreDefinition]
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        key "object": Required[Literal[memory_store]]
        key "updated_at": Required[int]
        created_at: int
        definition: MemoryStoreDefinition
        description: str
        id: str
        metadata: dict[str, str]
        name: str
        object: Literal[MemoryStoreObjectType.MEMORY_STORE]
        updated_at: int


    class azure.ai.extensions.openai.projects.MemoryStoreKind(TypedDict):


    class azure.ai.extensions.openai.projects.MemoryStoreObjectType(TypedDict):


    class azure.ai.extensions.openai.projects.MemoryStoreOperationUsage(TypedDict, total=False):
        key "embedding_tokens": Required[int]
        key "input_tokens": Required[int]
        key "input_tokens_details": Required[ResponseUsageInputTokensDetails]
        key "output_tokens": Required[int]
        key "output_tokens_details": Required[ResponseUsageOutputTokensDetails]
        key "total_tokens": Required[int]
        embedding_tokens: int
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int


    class azure.ai.extensions.openai.projects.MemoryStoreSearchResult(TypedDict, total=False):
        key "memories": Required[list[MemorySearchItem]]
        key "search_id": Required[str]
        key "usage": Required[MemoryStoreOperationUsage]
        memories: list[MemorySearchItem]
        search_id: str
        usage: MemoryStoreOperationUsage


    class azure.ai.extensions.openai.projects.MemoryStoreUpdateCompletedResult(TypedDict, total=False):
        key "memory_operations": Required[list[MemoryOperation]]
        key "usage": Required[MemoryStoreOperationUsage]
        memory_operations: list[MemoryOperation]
        usage: MemoryStoreOperationUsage


    class azure.ai.extensions.openai.projects.MemoryStoreUpdateResult(TypedDict, total=False):
        key "error": ForwardRef('ApiError', module='types')
        key "result": ForwardRef('MemoryStoreUpdateCompletedResult', module='types')
        key "status": Required[Literal["queued", "in_progress", "completed", "failed", "superseded"]]
        key "superseded_by": str
        key "update_id": Required[str]
        error: ApiError
        result: MemoryStoreUpdateCompletedResult
        status: MemoryStoreUpdateStatus
        superseded_by: str
        update_id: str


    class azure.ai.extensions.openai.projects.MicrosoftFabricPreviewTool(TypedDict, total=False):
        key "fabric_dataagent_preview": Required[FabricDataAgentToolParameters]
        key "type": Required[Literal[fabric_dataagent_preview]]
        fabric_dataagent_preview: FabricDataAgentToolParameters
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]


    class azure.ai.extensions.openai.projects.ModelCredentialRequest(TypedDict, total=False):
        key "blobUri": Required[str]
        blob_uri: str


    class azure.ai.extensions.openai.projects.ModelDeployment(TypedDict, total=False):
        key "capabilities": Required[dict[str, str]]
        key "connectionName": str
        key "modelName": Required[str]
        key "modelPublisher": Required[str]
        key "modelVersion": Required[str]
        key "name": Required[str]
        key "sku": Required[ModelDeploymentSku]
        key "type": Required[Literal[model_deployment]]
        capabilities: dict[str, str]
        connection_name: str
        model_name: str
        model_publisher: str
        model_version: str
        name: str
        sku: ModelDeploymentSku
        type: Literal[DeploymentType.MODEL_DEPLOYMENT]


    class azure.ai.extensions.openai.projects.ModelDeploymentSku(TypedDict, total=False):
        key "capacity": Required[int]
        key "family": Required[str]
        key "name": Required[str]
        key "size": Required[str]
        key "tier": Required[str]
        capacity: int
        family: str
        name: str
        size: str
        tier: str


    class azure.ai.extensions.openai.projects.ModelPendingUploadRequest(TypedDict, total=False):
        key "connectionName": str
        key "pendingUploadId": str
        key "pendingUploadType": Required[Literal[temporary_blob_reference]]
        connection_name: str
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]


    class azure.ai.extensions.openai.projects.ModelPendingUploadResponse(TypedDict, total=False):
        key "blobReference": Required[BlobReference]
        key "pendingUploadId": Required[str]
        key "pendingUploadType": Required[Literal[temporary_blob_reference]]
        key "version": str
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.TEMPORARY_BLOB_REFERENCE]
        version: str


    class azure.ai.extensions.openai.projects.ModelSamplingParams(TypedDict, total=False):
        key "max_completion_tokens": int
        key "seed": int
        key "temperature": float
        key "top_p": float
        max_completion_tokens: int
        seed: int
        temperature: float
        top_p: float


    class azure.ai.extensions.openai.projects.ModelSourceData(TypedDict, total=False):
        key "jobId": str
        key "sourceType": Literal["LocalUpload", "TrainingJob"]
        job_id: str
        source_type: FoundryModelSourceType


    class azure.ai.extensions.openai.projects.ModelVersion(TypedDict, total=False):
        key "artifactProfile": ForwardRef('ArtifactProfile', module='types')
        key "baseModel": str
        key "blobUri": Required[str]
        key "description": str
        key "id": str
        key "loraConfig": ForwardRef('LoraConfig', module='types')
        key "name": Required[str]
        key "source": ForwardRef('ModelSourceData', module='types')
        key "version": Required[str]
        key "weightType": Literal["FullWeight", "LoRA", "DraftModel"]
        artifact_profile: ArtifactProfile
        base_model: str
        blob_uri: str
        description: str
        id: str
        lora_config: LoraConfig
        name: str
        source: ModelSourceData
        tags: dict[str, str]
        version: str
        warnings: list[FoundryModelWarning]
        weight_type: FoundryModelWeightType


    class azure.ai.extensions.openai.projects.MonthlyRecurrenceSchedule(TypedDict, total=False):
        key "daysOfMonth": Required[list[int]]
        key "type": Required[Literal[monthly]]
        days_of_month: list[int]
        type: Literal[RecurrenceType.MONTHLY]


    class azure.ai.extensions.openai.projects.NamespaceToolParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "tools": Required[list[Union[FunctionToolParam, CustomToolParam]]]
        key "type": Required[Literal[namespace]]
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[ToolType.NAMESPACE]


    class azure.ai.extensions.openai.projects.NoAuthenticationCredentials(TypedDict, total=False):
        key "type": Required[Literal[none]]
        type: Literal[CredentialType.NONE]


    class azure.ai.extensions.openai.projects.OneTimeTrigger(TypedDict, total=False):
        key "timeZone": str
        key "triggerAt": Required[str]
        key "type": Required[Literal[one_time]]
        time_zone: str
        trigger_at: str
        type: Literal[TriggerType.ONE_TIME]


    class azure.ai.extensions.openai.projects.OpenApiAnonymousAuthDetails(TypedDict, total=False):
        key "type": Required[Literal[anonymous]]
        type: Literal[OpenApiAuthType.ANONYMOUS]


    class azure.ai.extensions.openai.projects.OpenApiAuthType(TypedDict):


    class azure.ai.extensions.openai.projects.OpenApiFunctionDefinition(TypedDict, total=False):
        key "auth": Required[OpenApiAuthDetails]
        key "description": str
        key "name": Required[str]
        key "spec": Required[dict[str, Any]]
        auth: OpenApiAuthDetails
        default_params: list[str]
        description: str
        functions: list[OpenApiFunctionDefinitionFunction]
        name: str
        spec: dict[str, Any]


    class azure.ai.extensions.openai.projects.OpenApiFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.extensions.openai.projects.OpenApiManagedAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiManagedSecurityScheme]
        key "type": Required[Literal[managed_identity]]
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[OpenApiAuthType.MANAGED_IDENTITY]


    class azure.ai.extensions.openai.projects.OpenApiManagedSecurityScheme(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.ai.extensions.openai.projects.OpenApiProjectConnectionAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiProjectConnectionSecurityScheme]
        key "type": Required[Literal[project_connection]]
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[OpenApiAuthType.PROJECT_CONNECTION]


    class azure.ai.extensions.openai.projects.OpenApiProjectConnectionSecurityScheme(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.extensions.openai.projects.OpenApiTool(TypedDict, total=False):
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal[openapi]]
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.OPENAPI]


    class azure.ai.extensions.openai.projects.OpenApiToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal[openapi]]
        description: str
        name: str
        openapi: OpenApiFunctionDefinition
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.OPENAPI]


    class azure.ai.extensions.openai.projects.OptimizationAgentIdentifier(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": str
        agent_name: str
        agent_version: str


    class azure.ai.extensions.openai.projects.OptimizationCandidate(TypedDict, total=False):
        key "avg_score": Required[float]
        key "avg_tokens": Required[float]
        key "candidate_id": str
        key "eval_id": str
        key "eval_run_id": str
        key "name": Required[str]
        key "promotion": ForwardRef('PromotionInfo', module='types')
        avg_score: float
        avg_tokens: float
        candidate_id: str
        eval_id: str
        eval_run_id: str
        mutations: dict[str, Any]
        name: str
        promotion: PromotionInfo


    class azure.ai.extensions.openai.projects.OptimizationDatasetCriterion(TypedDict, total=False):
        key "instruction": Required[str]
        key "name": Required[str]
        instruction: str
        name: str


    class azure.ai.extensions.openai.projects.OptimizationDatasetInputType(TypedDict):


    class azure.ai.extensions.openai.projects.OptimizationDatasetItem(TypedDict, total=False):
        key "desired_num_turns": int
        key "ground_truth": str
        key "query": str
        criteria: list[OptimizationDatasetCriterion]
        desired_num_turns: int
        ground_truth: str
        query: str


    class azure.ai.extensions.openai.projects.OptimizationEvaluatorRef(TypedDict, total=False):
        key "name": Required[str]
        key "version": str
        name: str
        version: str


    class azure.ai.extensions.openai.projects.OptimizationInlineDatasetInput(TypedDict, total=False):
        key "items": Required[list[OptimizationDatasetItem]]
        key "type": Required[Literal[inline]]
        dataset_items: list[OptimizationDatasetItem]
        type: Literal[OptimizationDatasetInputType.INLINE]


    class azure.ai.extensions.openai.projects.OptimizationJob(TypedDict, total=False):
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "id": Required[str]
        key "inputs": ForwardRef('OptimizationJobInputs', module='types')
        key "progress": ForwardRef('OptimizationJobProgress', module='types')
        key "result": ForwardRef('OptimizationJobResult', module='types')
        key "status": Required[Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]]
        key "updated_at": Required[int]
        created_at: int
        error: ApiError
        id: str
        inputs: OptimizationJobInputs
        progress: OptimizationJobProgress
        result: OptimizationJobResult
        status: JobStatus
        updated_at: int
        warnings: list[str]


    class azure.ai.extensions.openai.projects.OptimizationJobInputs(TypedDict, total=False):
        key "agent": Required[OptimizationAgentIdentifier]
        key "evaluators": Required[list[OptimizationEvaluatorRef]]
        key "options": ForwardRef('OptimizationOptions', module='types')
        key "train_dataset": Required[OptimizationDatasetInput]
        key "validation_dataset": ForwardRef('OptimizationDatasetInput', module='types')
        agent: OptimizationAgentIdentifier
        evaluators: list[OptimizationEvaluatorRef]
        options: OptimizationOptions
        train_dataset: OptimizationDatasetInput
        validation_dataset: OptimizationDatasetInput


    class azure.ai.extensions.openai.projects.OptimizationJobListItem(TypedDict, total=False):
        key "agent": ForwardRef('OptimizationAgentIdentifier', module='types')
        key "created_at": Required[int]
        key "error": ForwardRef('ApiError', module='types')
        key "id": Required[str]
        key "progress": ForwardRef('OptimizationJobProgress', module='types')
        key "status": Required[Literal["queued", "in_progress", "succeeded", "failed", "cancelled"]]
        key "updated_at": Required[int]
        agent: OptimizationAgentIdentifier
        created_at: int
        error: ApiError
        id: str
        progress: OptimizationJobProgress
        status: JobStatus
        updated_at: int


    class azure.ai.extensions.openai.projects.OptimizationJobProgress(TypedDict, total=False):
        key "best_score": Required[float]
        key "candidates_completed": Required[int]
        key "elapsed_seconds": Required[float]
        best_score: float
        candidates_completed: int
        elapsed_seconds: float


    class azure.ai.extensions.openai.projects.OptimizationJobResult(TypedDict, total=False):
        key "baseline": str
        key "best": str
        baseline: str
        best: str
        candidates: list[OptimizationCandidate]


    class azure.ai.extensions.openai.projects.OptimizationOptions(TypedDict, total=False):
        key "eval_model": str
        key "evaluation_level": Literal["turn", "conversation"]
        key "max_candidates": int
        key "optimization_model": str
        eval_model: str
        evaluation_level: EvaluationLevel
        max_candidates: int
        optimization_config: dict[str, Any]
        optimization_model: str


    class azure.ai.extensions.openai.projects.OptimizationReferenceDatasetInput(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[reference]]
        key "version": str
        name: str
        type: Literal[OptimizationDatasetInputType.REFERENCE]
        version: str


    class azure.ai.extensions.openai.projects.OtlpTelemetryEndpoint(TypedDict, total=False):
        key "auth": ForwardRef('TelemetryEndpointAuth', module='types')
        key "data": Required[list[Literal["ContainerStdoutStderr", "ContainerOtel", "Metrics"]]]
        key "endpoint": Required[str]
        key "kind": Required[Literal[otlp]]
        key "protocol": Required[Literal["Http", "Grpc"]]
        auth: TelemetryEndpointAuth
        data: list[TelemetryDataKind]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: TelemetryTransportProtocol


    class azure.ai.extensions.openai.projects.PatchAgentObjectRequest(TypedDict, total=False):
        key "agent_card": ForwardRef('AgentCard', module='types')
        key "agent_endpoint": ForwardRef('AgentEndpointConfig', module='types')
        agent_card: AgentCard
        agent_endpoint: AgentEndpointConfig


    class azure.ai.extensions.openai.projects.PendingUploadRequest(TypedDict, total=False):
        key "connectionName": str
        key "pendingUploadId": str
        key "pendingUploadType": Required[Literal[blob_reference]]
        connection_name: str
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]


    class azure.ai.extensions.openai.projects.PendingUploadResponse(TypedDict, total=False):
        key "blobReference": Required[BlobReference]
        key "pendingUploadId": Required[str]
        key "pendingUploadType": Required[Literal[blob_reference]]
        key "version": str
        blob_reference: BlobReference
        pending_upload_id: str
        pending_upload_type: Literal[PendingUploadType.BLOB_REFERENCE]
        version: str


    class azure.ai.extensions.openai.projects.PendingUploadType(TypedDict):


    class azure.ai.extensions.openai.projects.ProceduralMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal[procedural]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[MemoryItemKind.PROCEDURAL]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.extensions.openai.projects.PromotionInfo(TypedDict, total=False):
        key "agent_name": Required[str]
        key "agent_version": Required[str]
        key "promoted_at": Required[int]
        agent_name: str
        agent_version: str
        promoted_at: int


    class azure.ai.extensions.openai.projects.PromptAgentDefinition(TypedDict, total=False):
        key "instructions": Optional[str]
        key "kind": Required[Literal[prompt]]
        key "model": Required[str]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "reasoning": Optional[Reasoning]
        key "temperature": Optional[float]
        key "text": ForwardRef('PromptAgentDefinitionTextOptions', module='types')
        key "tool_choice": Union[str, ToolChoiceParam]
        key "top_p": Optional[float]
        instructions: str
        kind: Literal[AgentKind.PROMPT]
        model: str
        rai_config: RaiConfig
        reasoning: Reasoning
        structured_inputs: dict[str, StructuredInputDefinition]
        temperature: float
        text: PromptAgentDefinitionTextOptions
        tool_choice: Union[str, ToolChoiceParam]
        tools: list[Tool]
        top_p: float


    class azure.ai.extensions.openai.projects.PromptAgentDefinitionTextOptions(TypedDict, total=False):
        key "format": ForwardRef('TextResponseFormat', module='types')
        format: TextResponseFormat


    class azure.ai.extensions.openai.projects.PromptBasedEvaluatorDefinition(TypedDict, total=False):
        key "prompt_text": Required[str]
        key "type": Required[Literal[prompt]]
        data_schema: dict[str, Any]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        prompt_text: str
        type: Literal[EvaluatorDefinitionType.PROMPT]


    class azure.ai.extensions.openai.projects.PromptDataGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "prompt": Required[str]
        key "type": Required[Literal[prompt]]
        description: str
        prompt: str
        type: Literal[DataGenerationJobSourceType.PROMPT]


    class azure.ai.extensions.openai.projects.PromptEvaluatorGenerationJobSource(TypedDict, total=False):
        key "description": str
        key "prompt": Required[str]
        key "type": Required[Literal[prompt]]
        description: str
        prompt: str
        type: Literal[EvaluatorGenerationJobSourceType.PROMPT]


    class azure.ai.extensions.openai.projects.ProtocolConfiguration(TypedDict, total=False):
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


    class azure.ai.extensions.openai.projects.ProtocolVersionRecord(TypedDict, total=False):
        key "protocol": Required[Literal["activity", "responses", "a2a", "mcp", "invocations", "invocations_ws"]]
        key "version": Required[str]
        protocol: AgentEndpointProtocol
        version: str


    class azure.ai.extensions.openai.projects.RaiConfig(TypedDict, total=False):
        key "rai_policy_name": Required[str]
        rai_policy_name: str


    class azure.ai.extensions.openai.projects.RankingOptions(TypedDict, total=False):
        key "hybrid_search": ForwardRef('HybridSearchOptions', module='types')
        key "ranker": Literal["auto", "default-2024-11-15"]
        key "score_threshold": float
        hybrid_search: HybridSearchOptions
        ranker: RankerVersionType
        score_threshold: float


    class azure.ai.extensions.openai.projects.Reasoning(TypedDict, total=False):
        key "context": Optional[Literal["auto", "current_turn", "all_turns"]]
        key "effort": Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh"]]
        key "generate_summary": Optional[Literal["auto", "concise", "detailed"]]
        key "summary": Optional[Literal["auto", "concise", "detailed"]]
        context: Literal[auto, current_turn, all_turns]
        effort: Literal[none, minimal, low, medium, high, xhigh]
        generate_summary: Literal[auto, concise, detailed]
        summary: Literal[auto, concise, detailed]


    class azure.ai.extensions.openai.projects.RecurrenceTrigger(TypedDict, total=False):
        key "endTime": str
        key "interval": Required[int]
        key "schedule": Required[RecurrenceSchedule]
        key "startTime": str
        key "timeZone": str
        key "type": Required[Literal[recurrence]]
        end_time: str
        interval: int
        schedule: RecurrenceSchedule
        start_time: str
        time_zone: str
        type: Literal[TriggerType.RECURRENCE]


    class azure.ai.extensions.openai.projects.RecurrenceType(TypedDict):


    class azure.ai.extensions.openai.projects.RedTeam(TypedDict, total=False):
        key "applicationScenario": str
        key "displayName": str
        key "id": Required[str]
        key "numTurns": int
        key "simulationOnly": bool
        key "status": str
        key "target": Required[RedTeamTargetConfig]
        application_scenario: str
        attackStrategies: list[Literal["easy", "moderate", "difficult", "ascii_art", "ascii_smuggler", "atbash", "base64", "binary", "caesar", "character_space", "jailbreak", "ansi_attack", "character_swap", "suffix_append", "string_join", "unicode_confusable", "unicode_substitution", "diacritic", "flip", "leetspeak", "rot13", "morse", "url", "baseline", "indirect_jailbreak", "tense", "multi_turn", "crescendo"]]
        attack_strategies: list[AttackStrategy]
        display_name: str
        name: str
        num_turns: int
        properties: dict[str, str]
        riskCategories: list[Literal["HateUnfairness", "Violence", "Sexual", "SelfHarm", "ProtectedMaterial", "CodeVulnerability", "UngroundedAttributes", "ProhibitedActions", "SensitiveDataLeakage", "TaskAdherence"]]
        risk_categories: list[RiskCategory]
        simulation_only: bool
        status: str
        tags: dict[str, str]
        target: RedTeamTargetConfig


    class azure.ai.extensions.openai.projects.RedTeamTargetConfig(TypedDict, total=False):
        key "modelDeploymentName": Required[str]
        key "type": Required[Literal["AzureOpenAIModel"]]
        model_deployment_name: str
        type: Literal[AzureOpenAIModel]


    class azure.ai.extensions.openai.projects.ReminderPreviewTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[reminder_preview]]
        description: str
        name: str
        type: Literal[ToolType.REMINDER_PREVIEW]


    class azure.ai.extensions.openai.projects.ReminderPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[reminder_preview]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.REMINDER_PREVIEW]


    class azure.ai.extensions.openai.projects.ResponseUsageInputTokensDetails(TypedDict, total=False):
        key "cached_tokens": Required[int]
        cached_tokens: int


    class azure.ai.extensions.openai.projects.ResponseUsageOutputTokensDetails(TypedDict, total=False):
        key "reasoning_tokens": Required[int]
        reasoning_tokens: int


    class azure.ai.extensions.openai.projects.ResponsesProtocolConfiguration(TypedDict, total=False):


    class azure.ai.extensions.openai.projects.Routine(TypedDict, total=False):
        key "action": ForwardRef('RoutineAction', module='types')
        key "created_at": int
        key "description": str
        key "enabled": Required[bool]
        key "name": str
        key "updated_at": int
        action: RoutineAction
        created_at: int
        description: str
        enabled: bool
        name: str
        triggers: dict[str, RoutineTrigger]
        updated_at: int


    class azure.ai.extensions.openai.projects.RoutineActionType(TypedDict):


    class azure.ai.extensions.openai.projects.RoutineDispatchPayloadType(TypedDict):


    class azure.ai.extensions.openai.projects.RoutineRun(TypedDict, total=False):
        key "action_correlation_id": str
        key "action_type": RoutineActionType[_, _, a, r, g, s, _, _]
        key "agent_endpoint_id": str
        key "agent_id": str
        key "attempt_source": Literal["event_fire", "manual_dispatch", "queued_dispatch", "schedule_delivery", "timer_delivery"]
        key "conversation_id": str
        key "dispatch_id": str
        key "ended_at": int
        key "error_message": str
        key "error_status_code": int
        key "error_type": str
        key "id": Required[str]
        key "phase": Literal["queued", "dispatching", "completed", "failed"]
        key "response_id": str
        key "scheduled_fire_at": int
        key "session_id": str
        key "started_at": int
        key "status": ForwardRef('RoutineRunStatus', module='types')
        key "task_id": str
        key "trigger_name": str
        key "trigger_type": RoutineTriggerType[_, _, a, r, g, s, _, _]
        key "triggered_at": int
        action_correlation_id: str
        action_type: RoutineActionType
        agent_endpoint_id: str
        agent_id: str
        attempt_source: RoutineAttemptSource
        conversation_id: str
        dispatch_id: str
        ended_at: int
        error_message: str
        error_status_code: int
        error_type: str
        id: str
        phase: RoutineRunPhase
        response_id: str
        scheduled_fire_at: int
        session_id: str
        started_at: int
        status: RoutineRunStatus
        task_id: str
        trigger_event_payload: dict[str, Any]
        trigger_name: str
        trigger_type: RoutineTriggerType
        triggered_at: int


    class azure.ai.extensions.openai.projects.RoutineTriggerType(TypedDict):


    class azure.ai.extensions.openai.projects.RubricBasedEvaluatorDefinition(TypedDict, total=False):
        key "dimensions": Required[list[Dimension]]
        key "pass_threshold": float
        key "type": Required[Literal[rubric]]
        data_schema: dict[str, Any]
        dimensions: list[Dimension]
        init_parameters: dict[str, Any]
        metrics: dict[str, EvaluatorMetric]
        pass_threshold: float
        type: Literal[EvaluatorDefinitionType.RUBRIC]


    class azure.ai.extensions.openai.projects.SASCredentials(TypedDict, total=False):
        key "SAS": str
        key "type": Required[Literal[sas]]
        sas_token: str
        type: Literal[CredentialType.SAS]


    class azure.ai.extensions.openai.projects.SampleType(TypedDict):


    class azure.ai.extensions.openai.projects.Schedule(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "enabled": Required[bool]
        key "id": Required[str]
        key "provisioningStatus": Literal["Creating", "Updating", "Deleting", "Succeeded", "Failed"]
        key "systemData": Required[dict[str, str]]
        key "task": Required[ScheduleTask]
        key "trigger": Required[Trigger]
        description: str
        display_name: str
        enabled: bool
        properties: dict[str, str]
        provisioning_status: ScheduleProvisioningStatus
        schedule_id: str
        system_data: dict[str, str]
        tags: dict[str, str]
        task: ScheduleTask
        trigger: Trigger


    class azure.ai.extensions.openai.projects.ScheduleRoutineTrigger(TypedDict, total=False):
        key "cron_expression": Required[str]
        key "time_zone": Required[str]
        key "type": Required[Literal[schedule]]
        cron_expression: str
        time_zone: str
        type: Literal[RoutineTriggerType.SCHEDULE]


    class azure.ai.extensions.openai.projects.ScheduleRun(TypedDict, total=False):
        key "error": str
        key "id": Required[str]
        key "properties": Required[dict[str, str]]
        key "scheduleId": Required[str]
        key "success": Required[bool]
        key "triggerTime": str
        error: str
        properties: dict[str, str]
        run_id: str
        schedule_id: str
        success: bool
        trigger_time: str


    class azure.ai.extensions.openai.projects.ScheduleTaskType(TypedDict):


    class azure.ai.extensions.openai.projects.SearchMemoriesRequest(TypedDict, total=False):
        key "options": ForwardRef('MemorySearchOptions', module='types')
        key "previous_search_id": str
        key "scope": Required[str]
        items: list[dict[str, Any]]
        options: MemorySearchOptions
        previous_search_id: str
        scope: str


    class azure.ai.extensions.openai.projects.SessionDirectoryEntry(TypedDict, total=False):
        key "is_directory": Required[bool]
        key "modified_time": Required[int]
        key "name": Required[str]
        key "size": Required[int]
        is_directory: bool
        modified_time: int
        name: str
        size: int


    class azure.ai.extensions.openai.projects.SessionFileWriteResult(TypedDict, total=False):
        key "bytes_written": Required[int]
        key "path": Required[str]
        bytes_written: int
        path: str


    class azure.ai.extensions.openai.projects.SessionLogEvent(TypedDict, total=False):
        key "data": Required[str]
        key "event": Required[Literal["log"]]
        data: str
        event: SessionLogEventType


    class azure.ai.extensions.openai.projects.SharepointGroundingToolParameters(TypedDict, total=False):
        project_connections: list[ToolProjectConnection]


    class azure.ai.extensions.openai.projects.SharepointPreviewTool(TypedDict, total=False):
        key "sharepoint_grounding_preview": Required[SharepointGroundingToolParameters]
        key "type": Required[Literal[sharepoint_grounding_preview]]
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]


    class azure.ai.extensions.openai.projects.SimpleQnADataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[simple_qna]]
        max_samples: int
        model_options: DataGenerationModelOptions
        question_types: list[Literal["short_answer", "long_answer"]]
        train_split: float
        type: Literal[DataGenerationJobType.SIMPLE_QNA]


    class azure.ai.extensions.openai.projects.SkillDetails(TypedDict, total=False):
        key "created_at": Required[int]
        key "default_version": Required[str]
        key "description": Required[str]
        key "id": Required[str]
        key "latest_version": Required[str]
        key "name": Required[str]
        created_at: int
        default_version: str
        description: str
        id: str
        latest_version: str
        name: str


    class azure.ai.extensions.openai.projects.SkillInlineContent(TypedDict, total=False):
        key "compatibility": str
        key "description": Required[str]
        key "instructions": Required[str]
        key "license": str
        allowed_tools: list[str]
        compatibility: str
        description: str
        instructions: str
        license: str
        metadata: dict[str, str]


    class azure.ai.extensions.openai.projects.SkillReferenceParam(TypedDict, total=False):
        key "skill_id": Required[str]
        key "type": Required[Literal[skill_reference]]
        key "version": str
        skill_id: str
        type: Literal[ContainerSkillType.SKILL_REFERENCE]
        version: str


    class azure.ai.extensions.openai.projects.SkillVersion(TypedDict, total=False):
        key "created_at": Required[int]
        key "description": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "skill_id": Required[str]
        key "version": Required[str]
        created_at: int
        description: str
        id: str
        name: str
        skill_id: str
        version: str


    class azure.ai.extensions.openai.projects.SpecificApplyPatchParam(TypedDict, total=False):
        key "type": Required[Literal[apply_patch]]
        type: Literal[ToolChoiceParamType.APPLY_PATCH]


    class azure.ai.extensions.openai.projects.SpecificFunctionShellParam(TypedDict, total=False):
        key "type": Required[Literal[shell]]
        type: Literal[ToolChoiceParamType.SHELL]


    class azure.ai.extensions.openai.projects.StructuredInputDefinition(TypedDict, total=False):
        key "default_value": Any
        key "description": str
        key "required": bool
        default_value: Any
        description: str
        required: bool
        schema: dict[str, Any]


    class azure.ai.extensions.openai.projects.StructuredOutputDefinition(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Required[Optional[bool]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool


    class azure.ai.extensions.openai.projects.TaxonomyCategory(TypedDict, total=False):
        key "description": str
        key "id": Required[str]
        key "name": Required[str]
        key "riskCategory": Required[Literal["HateUnfairness", "Violence", "Sexual", "SelfHarm", "ProtectedMaterial", "CodeVulnerability", "UngroundedAttributes", "ProhibitedActions", "SensitiveDataLeakage", "TaskAdherence"]]
        key "subCategories": Required[list[TaxonomySubCategory]]
        description: str
        id: str
        name: str
        properties: dict[str, str]
        risk_category: RiskCategory
        sub_categories: list[TaxonomySubCategory]


    class azure.ai.extensions.openai.projects.TaxonomySubCategory(TypedDict, total=False):
        key "description": str
        key "enabled": Required[bool]
        key "id": Required[str]
        key "name": Required[str]
        description: str
        enabled: bool
        id: str
        name: str
        properties: dict[str, str]


    class azure.ai.extensions.openai.projects.TelemetryConfig(TypedDict, total=False):
        key "endpoints": Required[list[TelemetryEndpoint]]
        endpoints: list[TelemetryEndpoint]


    class azure.ai.extensions.openai.projects.TelemetryEndpoint(TypedDict, total=False):
        key "auth": ForwardRef('TelemetryEndpointAuth', module='types')
        key "data": Required[list[Literal["ContainerStdoutStderr", "ContainerOtel", "Metrics"]]]
        key "endpoint": Required[str]
        key "kind": Required[Literal[otlp]]
        key "protocol": Required[Literal["Http", "Grpc"]]
        auth: TelemetryEndpointAuth
        data: list[TelemetryDataKind]
        endpoint: str
        kind: Literal[TelemetryEndpointKind.OTLP]
        protocol: TelemetryTransportProtocol


    class azure.ai.extensions.openai.projects.TelemetryEndpointAuth(TypedDict, total=False):
        key "header_name": Required[str]
        key "secret_id": Required[str]
        key "secret_key": Required[str]
        key "type": Required[Literal[header]]
        header_name: str
        secret_id: str
        secret_key: str
        type: Literal[TelemetryEndpointAuthType.HEADER]


    class azure.ai.extensions.openai.projects.TelemetryEndpointAuthType(TypedDict):


    class azure.ai.extensions.openai.projects.TelemetryEndpointKind(TypedDict):


    class azure.ai.extensions.openai.projects.TextResponseFormatConfigurationType(TypedDict):


    class azure.ai.extensions.openai.projects.TextResponseFormatJsonObject(TypedDict, total=False):
        key "type": Required[Literal[json_object]]
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]


    class azure.ai.extensions.openai.projects.TextResponseFormatJsonSchema(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Optional[bool]
        key "type": Required[Literal[json_schema]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]


    class azure.ai.extensions.openai.projects.TextResponseFormatText(TypedDict, total=False):
        key "type": Required[Literal[text]]
        type: Literal[TextResponseFormatConfigurationType.TEXT]


    class azure.ai.extensions.openai.projects.TimerRoutineTrigger(TypedDict, total=False):
        key "at": int
        key "type": Required[Literal[timer]]
        at: int
        type: Literal[RoutineTriggerType.TIMER]


    class azure.ai.extensions.openai.projects.ToolChoiceAllowed(TypedDict, total=False):
        key "mode": Required[Literal["auto", "required"]]
        key "tools": Required[list[dict[str, Any]]]
        key "type": Required[Literal[allowed_tools]]
        mode: Literal[auto, required]
        tools: list[dict[str, Any]]
        type: Literal[ToolChoiceParamType.ALLOWED_TOOLS]


    class azure.ai.extensions.openai.projects.ToolChoiceCodeInterpreter(TypedDict, total=False):
        key "type": Required[Literal[code_interpreter]]
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]


    class azure.ai.extensions.openai.projects.ToolChoiceComputer(TypedDict, total=False):
        key "type": Required[Literal[computer]]
        type: Literal[ToolChoiceParamType.COMPUTER]


    class azure.ai.extensions.openai.projects.ToolChoiceComputerUse(TypedDict, total=False):
        key "type": Required[Literal[computer_use]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE]


    class azure.ai.extensions.openai.projects.ToolChoiceComputerUsePreview(TypedDict, total=False):
        key "type": Required[Literal[computer_use_preview]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]


    class azure.ai.extensions.openai.projects.ToolChoiceCustom(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[custom]]
        name: str
        type: Literal[ToolChoiceParamType.CUSTOM]


    class azure.ai.extensions.openai.projects.ToolChoiceFileSearch(TypedDict, total=False):
        key "type": Required[Literal[file_search]]
        type: Literal[ToolChoiceParamType.FILE_SEARCH]


    class azure.ai.extensions.openai.projects.ToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[function]]
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]


    class azure.ai.extensions.openai.projects.ToolChoiceImageGeneration(TypedDict, total=False):
        key "type": Required[Literal[image_generation]]
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]


    class azure.ai.extensions.openai.projects.ToolChoiceMCP(TypedDict, total=False):
        key "name": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[mcp]]
        name: str
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]


    class azure.ai.extensions.openai.projects.ToolChoiceParamType(TypedDict):


    class azure.ai.extensions.openai.projects.ToolChoiceWebSearchPreview(TypedDict, total=False):
        key "type": Required[Literal[web_search_preview]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]


    class azure.ai.extensions.openai.projects.ToolChoiceWebSearchPreview20250311(TypedDict, total=False):
        key "type": Required[Literal[web_search_preview_2025_03_11]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW_2025_03_11]


    class azure.ai.extensions.openai.projects.ToolConfig(TypedDict, total=False):
        key "additional_search_text": str
        key "pin": bool
        additional_search_text: str
        pin: bool


    class azure.ai.extensions.openai.projects.ToolDescription(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str


    class azure.ai.extensions.openai.projects.ToolProjectConnection(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.extensions.openai.projects.ToolSearchToolParam(TypedDict, total=False):
        key "description": Optional[str]
        key "execution": Literal["server", "client"]
        key "parameters": Optional[EmptyModelParam]
        key "type": Required[Literal[tool_search]]
        description: str
        execution: ToolSearchExecutionType
        parameters: EmptyModelParam
        type: Literal[ToolType.TOOL_SEARCH]


    class azure.ai.extensions.openai.projects.ToolType(TypedDict):


    class azure.ai.extensions.openai.projects.ToolUseFineTuningDataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[tool_use]]
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TOOL_USE]


    class azure.ai.extensions.openai.projects.ToolboxObject(TypedDict, total=False):
        key "default_version": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        default_version: str
        id: str
        name: str


    class azure.ai.extensions.openai.projects.ToolboxPolicies(TypedDict, total=False):
        key "rai_config": ForwardRef('RaiConfig', module='types')
        rai_config: RaiConfig


    class azure.ai.extensions.openai.projects.ToolboxSearchPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[toolbox_search_preview]]
        description: str
        name: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.TOOLBOX_SEARCH_PREVIEW]


    class azure.ai.extensions.openai.projects.ToolboxSkill(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["skill_reference"]]
        key "version": str
        name: str
        type: Literal[skill_reference]
        version: str


    class azure.ai.extensions.openai.projects.ToolboxSkillReference(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["skill_reference"]]
        key "version": str
        name: str
        type: Literal[skill_reference]
        version: str


    class azure.ai.extensions.openai.projects.ToolboxToolType(TypedDict):


    class azure.ai.extensions.openai.projects.ToolboxVersionObject(TypedDict, total=False):
        key "created_at": Required[int]
        key "description": str
        key "id": Required[str]
        key "metadata": Required[Optional[dict[str, str]]]
        key "name": Required[str]
        key "policies": ForwardRef('ToolboxPolicies', module='types')
        key "tools": Required[list[ToolboxTool]]
        key "version": Required[str]
        created_at: int
        description: str
        id: str
        metadata: dict[str, str]
        name: str
        policies: ToolboxPolicies
        skills: list[ToolboxSkill]
        tools: list[ToolboxTool]
        version: str


    class azure.ai.extensions.openai.projects.TracesDataGenerationJobOptions(TypedDict, total=False):
        key "max_samples": Required[int]
        key "model_options": ForwardRef('DataGenerationModelOptions', module='types')
        key "train_split": float
        key "type": Required[Literal[traces]]
        max_samples: int
        model_options: DataGenerationModelOptions
        train_split: float
        type: Literal[DataGenerationJobType.TRACES]


    class azure.ai.extensions.openai.projects.TracesDataGenerationJobSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "agent_version": str
        key "description": str
        key "end_time": int
        key "start_time": Required[int]
        key "type": Required[Literal[traces]]
        agent_id: str
        agent_name: str
        agent_version: str
        description: str
        end_time: int
        start_time: int
        type: Literal[DataGenerationJobSourceType.TRACES]


    class azure.ai.extensions.openai.projects.TracesEvaluatorGenerationJobSource(TypedDict, total=False):
        key "agent_id": str
        key "agent_name": str
        key "agent_version": str
        key "description": str
        key "end_time": int
        key "start_time": Required[int]
        key "type": Required[Literal[traces]]
        agent_id: str
        agent_name: str
        agent_version: str
        description: str
        end_time: int
        start_time: int
        type: Literal[EvaluatorGenerationJobSourceType.TRACES]


    class azure.ai.extensions.openai.projects.TriggerType(TypedDict):


    class azure.ai.extensions.openai.projects.UpdateMemoriesRequest(TypedDict, total=False):
        key "previous_update_id": str
        key "scope": Required[str]
        key "update_delay": int
        items: list[dict[str, Any]]
        items_property: list[dict[str, Any]]
        previous_update_id: str
        scope: str
        update_delay: int


    class azure.ai.extensions.openai.projects.UpdateMemoryRequest(TypedDict, total=False):
        key "content": Required[str]
        content: str


    class azure.ai.extensions.openai.projects.UpdateMemoryStoreRequest(TypedDict, total=False):
        key "description": str
        description: str
        metadata: dict[str, str]


    class azure.ai.extensions.openai.projects.UpdateModelVersionRequest(TypedDict, total=False):
        key "description": str
        description: str
        tags: dict[str, str]


    class azure.ai.extensions.openai.projects.UpdateSkillRequest(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.extensions.openai.projects.UpdateToolboxRequest(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.extensions.openai.projects.UpdateToolboxRequest1(TypedDict, total=False):
        key "default_version": Required[str]
        default_version: str


    class azure.ai.extensions.openai.projects.UserProfileMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal[user_profile]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[MemoryItemKind.USER_PROFILE]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.extensions.openai.projects.VersionIndicator(TypedDict, total=False):
        key "agent_version": Required[str]
        key "type": Required[Literal[version_ref]]
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]


    class azure.ai.extensions.openai.projects.VersionIndicatorType(TypedDict):


    class azure.ai.extensions.openai.projects.VersionRefIndicator(TypedDict, total=False):
        key "agent_version": Required[str]
        key "type": Required[Literal[version_ref]]
        agent_version: str
        type: Literal[VersionIndicatorType.VERSION_REF]


    class azure.ai.extensions.openai.projects.VersionSelectionRule(TypedDict, total=False):
        key "agent_version": Required[str]
        key "traffic_percentage": Required[int]
        key "type": Required[Literal[fixed_ratio]]
        agent_version: str
        traffic_percentage: int
        type: Literal[VersionSelectorType.FIXED_RATIO]


    class azure.ai.extensions.openai.projects.VersionSelector(TypedDict, total=False):
        key "version_selection_rules": Required[list[VersionSelectionRule]]
        version_selection_rules: list[VersionSelectionRule]


    class azure.ai.extensions.openai.projects.VersionSelectorType(TypedDict):


    class azure.ai.extensions.openai.projects.WebSearchApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.extensions.openai.projects.WebSearchConfiguration(TypedDict, total=False):
        key "instance_name": Required[str]
        key "project_connection_id": Required[str]
        instance_name: str
        project_connection_id: str


    class azure.ai.extensions.openai.projects.WebSearchPreviewTool(TypedDict, total=False):
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[web_search_preview]]
        key "user_location": Optional[ApproximateLocation]
        search_content_types: list[Literal["text", "image"]]
        search_context_size: SearchContextSize
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: ApproximateLocation


    class azure.ai.extensions.openai.projects.WebSearchTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "description": str
        key "filters": Optional[WebSearchToolFilters]
        key "name": str
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[web_search]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        description: str
        filters: WebSearchToolFilters
        name: str
        search_context_size: Literal[low, medium, high]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolType.WEB_SEARCH]
        user_location: WebSearchApproximateLocation


    class azure.ai.extensions.openai.projects.WebSearchToolFilters(TypedDict, total=False):
        key "allowed_domains": Optional[list[str]]
        allowed_domains: list[str]


    class azure.ai.extensions.openai.projects.WebSearchToolboxTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "description": str
        key "filters": Optional[WebSearchToolFilters]
        key "name": str
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[web_search]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        description: str
        filters: WebSearchToolFilters
        name: str
        search_context_size: Literal[low, medium, high]
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WEB_SEARCH]
        user_location: WebSearchApproximateLocation


    class azure.ai.extensions.openai.projects.WeeklyRecurrenceSchedule(TypedDict, total=False):
        key "daysOfWeek": Required[list[Literal["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]]]
        key "type": Required[Literal[weekly]]
        days_of_week: list[DayOfWeek]
        type: Literal[RecurrenceType.WEEKLY]


    class azure.ai.extensions.openai.projects.WorkIQPreviewTool(TypedDict, total=False):
        key "project_connection_id": Required[str]
        key "type": Required[Literal[work_iq_preview]]
        project_connection_id: str
        type: Literal[ToolType.WORK_IQ_PREVIEW]


    class azure.ai.extensions.openai.projects.WorkIQPreviewToolboxTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        key "type": Required[Literal[work_iq_preview]]
        description: str
        name: str
        project_connection_id: str
        tool_configs: dict[str, ToolConfig]
        type: Literal[ToolboxToolType.WORK_IQ_PREVIEW]


    class azure.ai.extensions.openai.projects.WorkflowAgentDefinition(TypedDict, total=False):
        key "kind": Required[Literal[workflow]]
        key "rai_config": ForwardRef('RaiConfig', module='types')
        key "workflow": str
        kind: Literal[AgentKind.WORKFLOW]
        rai_config: RaiConfig
        workflow: str


namespace azure.ai.extensions.openai.resources

    def azure.ai.extensions.openai.resources.async_conversation_items_class() -> type[Any]: ...


    def azure.ai.extensions.openai.resources.async_conversations_class() -> type[Any]: ...


    def azure.ai.extensions.openai.resources.conversation_items_class() -> type[Any]: ...


    def azure.ai.extensions.openai.resources.conversations_class() -> type[Any]: ...


    def azure.ai.extensions.openai.resources.responses_module() -> Any: ...


namespace azure.ai.extensions.openai.responses

    class azure.ai.extensions.openai.responses.A2APreviewTool(TypedDict, total=False):
        key "agent_card_path": str
        key "base_url": str
        key "description": str
        key "name": str
        key "project_connection_id": str
        key "type": Required[Literal[a2_a_preview]]
        agent_card_path: str
        base_url: str
        description: str
        name: str
        project_connection_id: str
        type: Literal[ToolType.A2_A_PREVIEW]


    class azure.ai.extensions.openai.responses.A2AToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[a2_a_preview_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.A2_A_PREVIEW_CALL]


    class azure.ai.extensions.openai.responses.A2AToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[a2_a_preview_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.A2_A_PREVIEW_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.AISearchIndexResource(TypedDict, total=False):
        key "description": str
        key "filter": str
        key "index_asset_id": str
        key "index_name": str
        key "name": str
        key "project_connection_id": str
        key "query_type": Literal["simple", "semantic", "vector", "vector_simple_hybrid", "vector_semantic_hybrid"]
        key "top_k": int
        description: str
        filter: str
        index_asset_id: str
        index_name: str
        name: str
        project_connection_id: str
        query_type: AzureAISearchQueryType
        top_k: int


    class azure.ai.extensions.openai.responses.AdditionalToolsItemParam(TypedDict, total=False):
        key "id": Optional[str]
        key "role": Required[Literal["developer"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[additional_tools]]
        id: str
        role: Literal[developer]
        tools: list[Tool]
        type: Literal[ItemType.ADDITIONAL_TOOLS]


    class azure.ai.extensions.openai.responses.AgentReference(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["agent_reference"]]
        key "version": str
        name: str
        type: Literal[agent_reference]
        version: str


    class azure.ai.extensions.openai.responses.AnnotationType(TypedDict):


    class azure.ai.extensions.openai.responses.ApiErrorResponse(TypedDict, total=False):
        key "error": Required[Error]
        error: Error


    class azure.ai.extensions.openai.responses.ApplyPatchCreateFileOperation(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal[create_file]]
        diff: str
        path: str
        type: Literal[ApplyPatchFileOperationType.CREATE_FILE]


    class azure.ai.extensions.openai.responses.ApplyPatchCreateFileOperationParam(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal[create_file]]
        diff: str
        path: str
        type: Literal[ApplyPatchOperationParamType.CREATE_FILE]


    class azure.ai.extensions.openai.responses.ApplyPatchDeleteFileOperation(TypedDict, total=False):
        key "path": Required[str]
        key "type": Required[Literal[delete_file]]
        path: str
        type: Literal[ApplyPatchFileOperationType.DELETE_FILE]


    class azure.ai.extensions.openai.responses.ApplyPatchDeleteFileOperationParam(TypedDict, total=False):
        key "path": Required[str]
        key "type": Required[Literal[delete_file]]
        path: str
        type: Literal[ApplyPatchOperationParamType.DELETE_FILE]


    class azure.ai.extensions.openai.responses.ApplyPatchFileOperationType(TypedDict):


    class azure.ai.extensions.openai.responses.ApplyPatchOperationParamType(TypedDict):


    class azure.ai.extensions.openai.responses.ApplyPatchToolCallItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "operation": Required[ApplyPatchOperationParam]
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal[apply_patch_call]]
        call_id: str
        id: str
        operation: ApplyPatchOperationParam
        status: ApplyPatchCallStatusParam
        type: Literal[ItemType.APPLY_PATCH_CALL]


    class azure.ai.extensions.openai.responses.ApplyPatchToolCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Optional[str]
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal[apply_patch_call_output]]
        call_id: str
        id: str
        output: str
        status: ApplyPatchCallOutputStatusParam
        type: Literal[ItemType.APPLY_PATCH_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ApplyPatchToolParam(TypedDict, total=False):
        key "type": Required[Literal[apply_patch]]
        type: Literal[ToolType.APPLY_PATCH]


    class azure.ai.extensions.openai.responses.ApplyPatchUpdateFileOperation(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal[update_file]]
        diff: str
        path: str
        type: Literal[ApplyPatchFileOperationType.UPDATE_FILE]


    class azure.ai.extensions.openai.responses.ApplyPatchUpdateFileOperationParam(TypedDict, total=False):
        key "diff": Required[str]
        key "path": Required[str]
        key "type": Required[Literal[update_file]]
        diff: str
        path: str
        type: Literal[ApplyPatchOperationParamType.UPDATE_FILE]


    class azure.ai.extensions.openai.responses.ApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.extensions.openai.responses.AutoCodeInterpreterToolParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal["auto"]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        type: Literal[auto]


    class azure.ai.extensions.openai.responses.AzureAISearchTool(TypedDict, total=False):
        key "azure_ai_search": Required[AzureAISearchToolResource]
        key "description": str
        key "name": str
        key "type": Required[Literal[azure_ai_search]]
        azure_ai_search: AzureAISearchToolResource
        description: str
        name: str
        type: Literal[ToolType.AZURE_AI_SEARCH]


    class azure.ai.extensions.openai.responses.AzureAISearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[azure_ai_search_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.AZURE_AI_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.AzureAISearchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[azure_ai_search_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.AZURE_AI_SEARCH_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.AzureAISearchToolResource(TypedDict, total=False):
        key "description": str
        key "indexes": Required[list[AISearchIndexResource]]
        key "name": str
        description: str
        indexes: list[AISearchIndexResource]
        name: str


    class azure.ai.extensions.openai.responses.AzureFunctionBinding(TypedDict, total=False):
        key "storage_queue": Required[AzureFunctionStorageQueue]
        key "type": Required[Literal["storage_queue"]]
        storage_queue: AzureFunctionStorageQueue
        type: Literal[storage_queue]


    class azure.ai.extensions.openai.responses.AzureFunctionDefinition(TypedDict, total=False):
        key "function": Required[AzureFunctionDefinitionFunction]
        key "input_binding": Required[AzureFunctionBinding]
        key "output_binding": Required[AzureFunctionBinding]
        function: AzureFunctionDefinitionFunction
        input_binding: AzureFunctionBinding
        output_binding: AzureFunctionBinding


    class azure.ai.extensions.openai.responses.AzureFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.extensions.openai.responses.AzureFunctionStorageQueue(TypedDict, total=False):
        key "queue_name": Required[str]
        key "queue_service_endpoint": Required[str]
        queue_name: str
        queue_service_endpoint: str


    class azure.ai.extensions.openai.responses.AzureFunctionTool(TypedDict, total=False):
        key "azure_function": Required[AzureFunctionDefinition]
        key "type": Required[Literal[azure_function]]
        azure_function: AzureFunctionDefinition
        type: Literal[ToolType.AZURE_FUNCTION]


    class azure.ai.extensions.openai.responses.AzureFunctionToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[azure_function_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.AZURE_FUNCTION_CALL]


    class azure.ai.extensions.openai.responses.AzureFunctionToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[azure_function_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.AZURE_FUNCTION_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.BingCustomSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "description": str
        key "freshness": str
        key "instance_name": Required[str]
        key "market": str
        key "name": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        description: str
        freshness: str
        instance_name: str
        market: str
        name: str
        project_connection_id: str
        set_lang: str


    class azure.ai.extensions.openai.responses.BingCustomSearchPreviewTool(TypedDict, total=False):
        key "bing_custom_search_preview": Required[BingCustomSearchToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[bing_custom_search_preview]]
        bing_custom_search_preview: BingCustomSearchToolParameters
        description: str
        name: str
        type: Literal[ToolType.BING_CUSTOM_SEARCH_PREVIEW]


    class azure.ai.extensions.openai.responses.BingCustomSearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[bing_custom_search_preview_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BING_CUSTOM_SEARCH_PREVIEW_CALL]


    class azure.ai.extensions.openai.responses.BingCustomSearchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[bing_custom_search_preview_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BING_CUSTOM_SEARCH_PREVIEW_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.BingCustomSearchToolParameters(TypedDict, total=False):
        key "description": str
        key "name": str
        key "search_configurations": Required[list[BingCustomSearchConfiguration]]
        description: str
        name: str
        search_configurations: list[BingCustomSearchConfiguration]


    class azure.ai.extensions.openai.responses.BingGroundingSearchConfiguration(TypedDict, total=False):
        key "count": int
        key "description": str
        key "freshness": str
        key "market": str
        key "name": str
        key "project_connection_id": Required[str]
        key "set_lang": str
        count: int
        description: str
        freshness: str
        market: str
        name: str
        project_connection_id: str
        set_lang: str


    class azure.ai.extensions.openai.responses.BingGroundingSearchToolParameters(TypedDict, total=False):
        key "description": str
        key "name": str
        key "search_configurations": Required[list[BingGroundingSearchConfiguration]]
        description: str
        name: str
        search_configurations: list[BingGroundingSearchConfiguration]


    class azure.ai.extensions.openai.responses.BingGroundingTool(TypedDict, total=False):
        key "bing_grounding": Required[BingGroundingSearchToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[bing_grounding]]
        bing_grounding: BingGroundingSearchToolParameters
        description: str
        name: str
        type: Literal[ToolType.BING_GROUNDING]


    class azure.ai.extensions.openai.responses.BingGroundingToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[bing_grounding_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BING_GROUNDING_CALL]


    class azure.ai.extensions.openai.responses.BingGroundingToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[bing_grounding_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BING_GROUNDING_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.BrowserAutomationPreviewTool(TypedDict, total=False):
        key "browser_automation_preview": Required[BrowserAutomationToolParameters]
        key "description": str
        key "name": str
        key "type": Required[Literal[browser_automation_preview]]
        browser_automation_preview: BrowserAutomationToolParameters
        description: str
        name: str
        type: Literal[ToolType.BROWSER_AUTOMATION_PREVIEW]


    class azure.ai.extensions.openai.responses.BrowserAutomationToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[browser_automation_preview_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BROWSER_AUTOMATION_PREVIEW_CALL]


    class azure.ai.extensions.openai.responses.BrowserAutomationToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[browser_automation_preview_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.BROWSER_AUTOMATION_PREVIEW_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.BrowserAutomationToolConnectionParameters(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        description: str
        name: str
        project_connection_id: str


    class azure.ai.extensions.openai.responses.BrowserAutomationToolParameters(TypedDict, total=False):
        key "connection": Required[BrowserAutomationToolConnectionParameters]
        key "description": str
        key "name": str
        connection: BrowserAutomationToolConnectionParameters
        description: str
        name: str


    class azure.ai.extensions.openai.responses.CaptureStructuredOutputsTool(TypedDict, total=False):
        key "outputs": Required[StructuredOutputDefinition]
        key "type": Required[Literal[capture_structured_outputs]]
        outputs: StructuredOutputDefinition
        type: Literal[ToolType.CAPTURE_STRUCTURED_OUTPUTS]


    class azure.ai.extensions.openai.responses.ChatSummaryMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal[chat_summary]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[MemoryItemKind.CHAT_SUMMARY]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.extensions.openai.responses.ClickParam(TypedDict, total=False):
        key "button": Required[Literal["left", "right", "wheel", "back", "forward"]]
        key "keys": Optional[list[str]]
        key "type": Required[Literal[click]]
        key "x": Required[int]
        key "y": Required[int]
        button: ClickButtonType
        keys_property: list[str]
        type: Literal[ComputerActionType.CLICK]
        x: int
        y: int


    class azure.ai.extensions.openai.responses.CodeInterpreterOutputImage(TypedDict, total=False):
        key "type": Required[Literal["image"]]
        key "url": Required[str]
        type: Literal[image]
        url: str


    class azure.ai.extensions.openai.responses.CodeInterpreterOutputLogs(TypedDict, total=False):
        key "logs": Required[str]
        key "type": Required[Literal["logs"]]
        logs: str
        type: Literal[logs]


    class azure.ai.extensions.openai.responses.CodeInterpreterTool(TypedDict, total=False):
        key "container": Union[str, AutoCodeInterpreterToolParam]
        key "description": str
        key "name": str
        key "type": Required[Literal[code_interpreter]]
        container: Union[str, AutoCodeInterpreterToolParam]
        description: str
        name: str
        type: Literal[ToolType.CODE_INTERPRETER]


    class azure.ai.extensions.openai.responses.CompactResource(TypedDict, total=False):
        key "created_at": Required[int]
        key "id": Required[str]
        key "object": Required[Literal["compaction"]]
        key "output": Required[list[ItemField]]
        key "usage": Required[ResponseUsage]
        created_at: int
        id: str
        object: Literal[compaction]
        output: list[ItemField]
        usage: ResponseUsage


    class azure.ai.extensions.openai.responses.CompactResponseMethodPublicBody(TypedDict, total=False):
        key "input": Optional[Union[str, list[Item]]]
        key "instructions": Optional[str]
        key "model": Required[Optional[Literal["gpt-4", "gpt-4-mini", "gpt-4-nano", "gpt-4-mini-2026-03-17", "gpt-4-nano-2026-03-17", "gpt-3-chat-latest", "gpt-2", "gpt-2-2025-12-11", "gpt-2-chat-latest", "gpt-2-pro", "gpt-2-pro-2025-12-11", "gpt-1", "gpt-1-2025-11-13", "gpt-1-codex", "gpt-1-mini", "gpt-1-chat-latest", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-2025-08-07", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-5-chat-latest", "gpt-1", "gpt-1-mini", "gpt-1-nano", "gpt-1-2025-04-14", "gpt-1-mini-2025-04-14", "gpt-1-nano-2025-04-14", "o4-mini", "o4-mini-2025-04-16", "o3", "o3-2025-04-16", "o3-mini", "o3-mini-2025-01-31", "o1", "o1-2024-12-17", "o1-preview", "o1-preview-2024-09-12", "o1-mini", "o1-mini-2024-09-12", "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4o-audio-preview", "gpt-4o-audio-preview-2024-10-01", "gpt-4o-audio-preview-2024-12-17", "gpt-4o-audio-preview-2025-06-03", "gpt-4o-mini-audio-preview", "gpt-4o-mini-audio-preview-2024-12-17", "gpt-4o-search-preview", "gpt-4o-mini-search-preview", "gpt-4o-search-preview-2025-03-11", "gpt-4o-mini-search-preview-2025-03-11", "chatgpt-4o-latest", "codex-mini-latest", "gpt-4o-mini", "gpt-4o-mini-2024-07-18", "gpt-4-turbo", "gpt-4-turbo-2024-04-09", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-1106-preview", "gpt-4-vision-preview", "gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613", "gpt-5-turbo", "gpt-5-turbo-16k", "gpt-5-turbo-0301", "gpt-5-turbo-0613", "gpt-5-turbo-1106", "gpt-5-turbo-0125", "gpt-5-turbo-16k-0613", "o1-pro", "o1-pro-2025-03-19", "o3-pro", "o3-pro-2025-06-10", "o3-deep-research", "o3-deep-research-2025-06-26", "o4-mini-deep-research", "o4-mini-deep-research-2025-06-26", "computer-use-preview", "computer-use-preview-2025-03-11", "gpt-5-codex", "gpt-5-pro", "gpt-5-pro-2025-10-06", "gpt-1-codex-max"]]]
        key "previous_response_id": Optional[str]
        key "prompt_cache_key": Optional[str]
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "service_tier": Optional[Literal["auto", "default", "flex", "priority"]]
        input: Union[str, list[Item]]
        instructions: str
        model: ModelIdsCompaction
        previous_response_id: str
        prompt_cache_key: str
        prompt_cache_retention: PromptCacheRetentionEnum
        service_tier: ServiceTierEnum


    class azure.ai.extensions.openai.responses.CompactionSummaryItemParam(TypedDict, total=False):
        key "encrypted_content": Required[str]
        key "id": Optional[str]
        key "type": Required[Literal[compaction]]
        encrypted_content: str
        id: str
        type: Literal[ItemType.COMPACTION]


    class azure.ai.extensions.openai.responses.ComparisonFilter(TypedDict, total=False):
        key "key": Required[str]
        key "type": Required[Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin"]]
        key "value": Required[Union[str, float, bool, list[Union[str, float]]]]
        key: str
        type: Literal[eq, ne, gt, gte, lt, lte, in, nin]
        value: Union[str, float, bool, list[Union[str, float]]]


    class azure.ai.extensions.openai.responses.CompoundFilter(TypedDict, total=False):
        key "filters": Required[list[Union[ComparisonFilter, Any]]]
        key "type": Required[Literal["and", "or"]]
        filters: list[Union[ComparisonFilter, Any]]
        type: Literal[and, or]


    class azure.ai.extensions.openai.responses.ComputerActionType(TypedDict):


    class azure.ai.extensions.openai.responses.ComputerCallOutputItemParam(TypedDict, total=False):
        key "acknowledged_safety_checks": Optional[list[ComputerCallSafetyCheckParam]]
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Required[ComputerScreenshotImage]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[computer_call_output]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        call_id: str
        id: str
        output: ComputerScreenshotImage
        status: FunctionCallItemStatus
        type: Literal[ItemType.COMPUTER_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ComputerCallSafetyCheckParam(TypedDict, total=False):
        key "code": Optional[str]
        key "id": Required[str]
        key "message": Optional[str]
        code: str
        id: str
        message: str


    class azure.ai.extensions.openai.responses.ComputerScreenshotContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Required[Optional[str]]
        key "image_url": Required[Optional[str]]
        key "type": Required[Literal[computer_screenshot]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[MessageContentType.COMPUTER_SCREENSHOT]


    class azure.ai.extensions.openai.responses.ComputerScreenshotImage(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        key "type": Required[Literal["computer_screenshot"]]
        file_id: str
        image_url: str
        type: Literal[computer_screenshot]


    class azure.ai.extensions.openai.responses.ComputerTool(TypedDict, total=False):
        key "type": Required[Literal[computer]]
        type: Literal[ToolType.COMPUTER]


    class azure.ai.extensions.openai.responses.ComputerUsePreviewTool(TypedDict, total=False):
        key "display_height": Required[int]
        key "display_width": Required[int]
        key "environment": Required[Literal["windows", "mac", "linux", "ubuntu", "browser"]]
        key "type": Required[Literal[computer_use_preview]]
        display_height: int
        display_width: int
        environment: ComputerEnvironment
        type: Literal[ToolType.COMPUTER_USE_PREVIEW]


    class azure.ai.extensions.openai.responses.ContainerAutoParam(TypedDict, total=False):
        key "memory_limit": Optional[Literal["1g", "4g", "16g", "64g"]]
        key "network_policy": ForwardRef('ContainerNetworkPolicyParam', module='types')
        key "type": Required[Literal[container_auto]]
        file_ids: list[str]
        memory_limit: ContainerMemoryLimit
        network_policy: ContainerNetworkPolicyParam
        skills: list[ContainerSkill]
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_AUTO]


    class azure.ai.extensions.openai.responses.ContainerFileCitationBody(TypedDict, total=False):
        key "container_id": Required[str]
        key "end_index": Required[int]
        key "file_id": Required[str]
        key "filename": Required[str]
        key "start_index": Required[int]
        key "type": Required[Literal[container_file_citation]]
        container_id: str
        end_index: int
        file_id: str
        filename: str
        start_index: int
        type: Literal[AnnotationType.CONTAINER_FILE_CITATION]


    class azure.ai.extensions.openai.responses.ContainerNetworkPolicyAllowlistParam(TypedDict, total=False):
        key "allowed_domains": Required[list[str]]
        key "type": Required[Literal[allowlist]]
        allowed_domains: list[str]
        domain_secrets: list[ContainerNetworkPolicyDomainSecretParam]
        type: Literal[ContainerNetworkPolicyParamType.ALLOWLIST]


    class azure.ai.extensions.openai.responses.ContainerNetworkPolicyDisabledParam(TypedDict, total=False):
        key "type": Required[Literal[disabled]]
        type: Literal[ContainerNetworkPolicyParamType.DISABLED]


    class azure.ai.extensions.openai.responses.ContainerNetworkPolicyDomainSecretParam(TypedDict, total=False):
        key "domain": Required[str]
        key "name": Required[str]
        key "value": Required[str]
        domain: str
        name: str
        value: str


    class azure.ai.extensions.openai.responses.ContainerNetworkPolicyParamType(TypedDict):


    class azure.ai.extensions.openai.responses.ContainerReferenceResource(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal[container_reference]]
        container_id: str
        type: Literal[FunctionShellCallEnvironmentType.CONTAINER_REFERENCE]


    class azure.ai.extensions.openai.responses.ContainerSkillType(TypedDict):


    class azure.ai.extensions.openai.responses.ContextManagementParam(TypedDict, total=False):
        key "compact_threshold": Optional[int]
        key "type": Required[str]
        compact_threshold: int
        type: str


    class azure.ai.extensions.openai.responses.ConversationParam_2(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.ai.extensions.openai.responses.ConversationReference(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.ai.extensions.openai.responses.CoordParam(TypedDict, total=False):
        key "x": Required[int]
        key "y": Required[int]
        x: int
        y: int


    class azure.ai.extensions.openai.responses.CreateResponse(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "background": Optional[bool]
        key "context_management": Optional[list[ContextManagementParam]]
        key "conversation": Optional[ConversationParam]
        key "include": Optional[list[Literal["results", "results", "sources", "image_url", "image_url", "outputs", "encrypted_content", "logprobs", "results"]]]
        key "input": ForwardRef('InputParam', module='types')
        key "instructions": Optional[str]
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[ModerationParam]
        key "parallel_tool_calls": Optional[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "reasoning": Optional[Reasoning]
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "store": Optional[bool]
        key "stream": Optional[bool]
        key "stream_options": Optional[ResponseStreamOptions]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "user": str
        agent_reference: AgentReference
        background: bool
        context_management: list[ContextManagementParam]
        conversation: ConversationParam
        include: list[IncludeEnum]
        input: InputParam
        instructions: str
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: ModerationParam
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        reasoning: Reasoning
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        store: bool
        stream: bool
        stream_options: ResponseStreamOptions
        structured_inputs: dict[str, Any]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        user: str


    class azure.ai.extensions.openai.responses.CustomGrammarFormatParam(TypedDict, total=False):
        key "definition": Required[str]
        key "syntax": Required[Literal["lark", "regex"]]
        key "type": Required[Literal[grammar]]
        definition: str
        syntax: GrammarSyntax1
        type: Literal[CustomToolParamFormatType.GRAMMAR]


    class azure.ai.extensions.openai.responses.CustomTextFormatParam(TypedDict, total=False):
        key "type": Required[Literal[text]]
        type: Literal[CustomToolParamFormatType.TEXT]


    class azure.ai.extensions.openai.responses.CustomToolCallOutputResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "created_by": str
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[custom_tool_call_output]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        status: FunctionCallOutputStatusEnum
        type: Literal[OutputItemType.CUSTOM_TOOL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.CustomToolCallResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "created_by": str
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[custom_tool_call]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        id: str
        input: str
        name: str
        namespace: str
        response_id: str
        status: FunctionCallStatus
        type: Literal[OutputItemType.CUSTOM_TOOL_CALL]


    class azure.ai.extensions.openai.responses.CustomToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": str
        key "format": ForwardRef('CustomToolParamFormat', module='types')
        key "name": Required[str]
        key "type": Required[Literal[custom]]
        defer_loading: bool
        description: str
        format: CustomToolParamFormat
        name: str
        type: Literal[ToolType.CUSTOM]


    class azure.ai.extensions.openai.responses.CustomToolParamFormatType(TypedDict):


    class azure.ai.extensions.openai.responses.DeleteResponseResult(TypedDict, total=False):
        key "deleted": Required[Literal[True]]
        key "id": Required[str]
        key "object": Required[Literal["response"]]
        deleted: Literal[True]
        id: str
        object: Literal[response]


    class azure.ai.extensions.openai.responses.DoubleClickAction(TypedDict, total=False):
        key "keys": Required[Optional[list[str]]]
        key "type": Required[Literal[double_click]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        type: Literal[ComputerActionType.DOUBLE_CLICK]
        x: int
        y: int


    class azure.ai.extensions.openai.responses.DragParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "path": Required[list[CoordParam]]
        key "type": Required[Literal[drag]]
        keys_property: list[str]
        path: list[CoordParam]
        type: Literal[ComputerActionType.DRAG]


    class azure.ai.extensions.openai.responses.EmptyModelParam(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.Error(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Optional[str]
        key "type": str
        additionalInfo: dict[str, Any]
        additional_info: dict[str, Any]
        code: str
        debugInfo: dict[str, Any]
        debug_info: dict[str, Any]
        details: list[Error]
        message: str
        param: str
        type: str


    class azure.ai.extensions.openai.responses.FabricDataAgentToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[fabric_dataagent_preview_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.FABRIC_DATAAGENT_PREVIEW_CALL]


    class azure.ai.extensions.openai.responses.FabricDataAgentToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[fabric_dataagent_preview_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.FABRIC_DATAAGENT_PREVIEW_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.FabricDataAgentToolParameters(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str
        project_connections: list[ToolProjectConnection]


    class azure.ai.extensions.openai.responses.FileCitationBody(TypedDict, total=False):
        key "file_id": Required[str]
        key "filename": Required[str]
        key "index": Required[int]
        key "type": Required[Literal[file_citation]]
        file_id: str
        filename: str
        index: int
        type: Literal[AnnotationType.FILE_CITATION]


    class azure.ai.extensions.openai.responses.FilePath(TypedDict, total=False):
        key "file_id": Required[str]
        key "index": Required[int]
        key "type": Required[Literal[file_path]]
        file_id: str
        index: int
        type: Literal[AnnotationType.FILE_PATH]


    class azure.ai.extensions.openai.responses.FileSearchTool(TypedDict, total=False):
        key "description": str
        key "filters": Optional[Filters]
        key "max_num_results": int
        key "name": str
        key "ranking_options": ForwardRef('RankingOptions', module='types')
        key "type": Required[Literal[file_search]]
        key "vector_store_ids": Required[list[str]]
        description: str
        filters: Filters
        max_num_results: int
        name: str
        ranking_options: RankingOptions
        type: Literal[ToolType.FILE_SEARCH]
        vector_store_ids: list[str]


    class azure.ai.extensions.openai.responses.FileSearchToolCallResults(TypedDict, total=False):
        key "attributes": Optional[VectorStoreFileAttributes]
        key "file_id": str
        key "filename": str
        key "score": float
        key "text": str
        attributes: VectorStoreFileAttributes
        file_id: str
        filename: str
        score: float
        text: str


    class azure.ai.extensions.openai.responses.FunctionAndCustomToolCallOutputInputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal[input_file]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_FILE]


    class azure.ai.extensions.openai.responses.FunctionAndCustomToolCallOutputInputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal[input_image]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_IMAGE]


    class azure.ai.extensions.openai.responses.FunctionAndCustomToolCallOutputInputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[input_text]]
        text: str
        type: Literal[FunctionAndCustomToolCallOutputType.INPUT_TEXT]


    class azure.ai.extensions.openai.responses.FunctionAndCustomToolCallOutputType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "output": Required[Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]]]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[function_call_output]]
        call_id: str
        id: str
        output: Union[str, list[Union[InputTextContentParam, InputImageContentParamAutoParam, InputFileContentParam]]]
        status: FunctionCallItemStatus
        type: Literal[ItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.FunctionShellAction(TypedDict, total=False):
        key "commands": Required[list[str]]
        key "max_output_length": Required[Optional[int]]
        key "timeout_ms": Required[Optional[int]]
        commands: list[str]
        max_output_length: int
        timeout_ms: int


    class azure.ai.extensions.openai.responses.FunctionShellActionParam(TypedDict, total=False):
        key "commands": Required[list[str]]
        key "max_output_length": Optional[int]
        key "timeout_ms": Optional[int]
        commands: list[str]
        max_output_length: int
        timeout_ms: int


    class azure.ai.extensions.openai.responses.FunctionShellCallEnvironmentType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionShellCallItemParam(TypedDict, total=False):
        key "action": Required[FunctionShellActionParam]
        key "call_id": Required[str]
        key "environment": Optional[FunctionShellCallItemParamEnvironment]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call]]
        action: FunctionShellActionParam
        call_id: str
        environment: FunctionShellCallItemParamEnvironment
        id: str
        status: FunctionShellCallItemStatus
        type: Literal[ItemType.SHELL_CALL]


    class azure.ai.extensions.openai.responses.FunctionShellCallItemParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal[container_reference]]
        container_id: str
        type: Literal[FunctionShellCallItemParamEnvironmentType.CONTAINER_REFERENCE]


    class azure.ai.extensions.openai.responses.FunctionShellCallItemParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal[local]]
        skills: list[LocalSkillParam]
        type: Literal[FunctionShellCallItemParamEnvironmentType.LOCAL]


    class azure.ai.extensions.openai.responses.FunctionShellCallItemParamEnvironmentType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputContent(TypedDict, total=False):
        key "created_by": str
        key "outcome": Required[FunctionShellCallOutputOutcome]
        key "stderr": Required[str]
        key "stdout": Required[str]
        created_by: str
        outcome: FunctionShellCallOutputOutcome
        stderr: str
        stdout: str


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputContentParam(TypedDict, total=False):
        key "outcome": Required[FunctionShellCallOutputOutcomeParam]
        key "stderr": Required[str]
        key "stdout": Required[str]
        outcome: FunctionShellCallOutputOutcomeParam
        stderr: str
        stdout: str


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputExitOutcome(TypedDict, total=False):
        key "exit_code": Required[int]
        key "type": Required[Literal[exit]]
        exit_code: int
        type: Literal[FunctionShellCallOutputOutcomeType.EXIT]


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputExitOutcomeParam(TypedDict, total=False):
        key "exit_code": Required[int]
        key "type": Required[Literal[exit]]
        exit_code: int
        type: Literal[FunctionShellCallOutputOutcomeParamType.EXIT]


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputItemParam(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Optional[str]
        key "max_output_length": Optional[int]
        key "output": Required[list[FunctionShellCallOutputContentParam]]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call_output]]
        call_id: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContentParam]
        status: FunctionShellCallItemStatus
        type: Literal[ItemType.SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputOutcomeParamType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputOutcomeType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputTimeoutOutcome(TypedDict, total=False):
        key "type": Required[Literal[timeout]]
        type: Literal[FunctionShellCallOutputOutcomeType.TIMEOUT]


    class azure.ai.extensions.openai.responses.FunctionShellCallOutputTimeoutOutcomeParam(TypedDict, total=False):
        key "type": Required[Literal[timeout]]
        type: Literal[FunctionShellCallOutputOutcomeParamType.TIMEOUT]


    class azure.ai.extensions.openai.responses.FunctionShellToolParam(TypedDict, total=False):
        key "description": str
        key "environment": Optional[FunctionShellToolParamEnvironment]
        key "name": str
        key "type": Required[Literal[shell]]
        description: str
        environment: FunctionShellToolParamEnvironment
        name: str
        type: Literal[ToolType.SHELL]


    class azure.ai.extensions.openai.responses.FunctionShellToolParamEnvironmentContainerReferenceParam(TypedDict, total=False):
        key "container_id": Required[str]
        key "type": Required[Literal[container_reference]]
        container_id: str
        type: Literal[FunctionShellToolParamEnvironmentType.CONTAINER_REFERENCE]


    class azure.ai.extensions.openai.responses.FunctionShellToolParamEnvironmentLocalEnvironmentParam(TypedDict, total=False):
        key "type": Required[Literal[local]]
        skills: list[LocalSkillParam]
        type: Literal[FunctionShellToolParamEnvironmentType.LOCAL]


    class azure.ai.extensions.openai.responses.FunctionShellToolParamEnvironmentType(TypedDict):


    class azure.ai.extensions.openai.responses.FunctionTool(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Required[Optional[dict[str, Any]]]
        key "strict": Required[Optional[bool]]
        key "type": Required[Literal[function]]
        defer_loading: bool
        description: str
        name: str
        parameters: dict[str, Any]
        strict: bool
        type: Literal[ToolType.FUNCTION]


    class azure.ai.extensions.openai.responses.FunctionToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal["function_call_output"]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[function_call_output]


    class azure.ai.extensions.openai.responses.FunctionToolParam(TypedDict, total=False):
        key "defer_loading": bool
        key "description": Optional[str]
        key "name": Required[str]
        key "parameters": Optional[EmptyModelParam]
        key "strict": Optional[bool]
        key "type": Required[Literal["function"]]
        defer_loading: bool
        description: str
        name: str
        parameters: EmptyModelParam
        strict: bool
        type: Literal[function]


    class azure.ai.extensions.openai.responses.HybridSearchOptions(TypedDict, total=False):
        key "embedding_weight": Required[float]
        key "text_weight": Required[float]
        embedding_weight: float
        text_weight: float


    class azure.ai.extensions.openai.responses.ImageGenTool(TypedDict, total=False):
        key "action": Literal["generate", "edit", "auto"]
        key "background": Literal["transparent", "opaque", "auto"]
        key "description": str
        key "input_fidelity": Optional[Literal["high", "low"]]
        key "input_image_mask": ForwardRef('ImageGenToolInputImageMask', module='types')
        key "model": Union[Literal["gpt-image-1"], Literal["gpt-image-1-mini"], Literal["gpt-image-5"], str]
        key "moderation": Literal["auto", "low"]
        key "name": str
        key "output_compression": int
        key "output_format": Literal["png", "webp", "jpeg"]
        key "partial_images": int
        key "quality": Literal["low", "medium", "high", "auto"]
        key "size": Union[Literal["1024x1024"], Literal["1024x1536"], Literal["1536x1024"], Literal["auto"], str]
        key "type": Required[Literal[image_generation]]
        action: ImageGenActionEnum
        background: Literal[transparent, opaque, auto]
        description: str
        input_fidelity: InputFidelity
        input_image_mask: ImageGenToolInputImageMask
        model: Union[Literal[gpt-image-1], Literal[gpt-image-1-mini], Literal[gpt-image-5], str]
        moderation: Literal[auto, low]
        name: str
        output_compression: int
        output_format: Literal[png, webp, jpeg]
        partial_images: int
        quality: Literal[low, medium, high, auto]
        size: Union[Literal[1024x1024], Literal[1024x1536], Literal[1536x1024], Literal[auto], str]
        type: Literal[ToolType.IMAGE_GENERATION]


    class azure.ai.extensions.openai.responses.ImageGenToolInputImageMask(TypedDict, total=False):
        key "file_id": str
        key "image_url": str
        file_id: str
        image_url: str


    class azure.ai.extensions.openai.responses.InlineSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "source": Required[InlineSkillSourceParam]
        key "type": Required[Literal[inline]]
        description: str
        name: str
        source: InlineSkillSourceParam
        type: Literal[ContainerSkillType.INLINE]


    class azure.ai.extensions.openai.responses.InlineSkillSourceParam(TypedDict, total=False):
        key "data": Required[str]
        key "media_type": Required[Literal["application/zip"]]
        key "type": Required[Literal["base64"]]
        data: str
        media_type: Literal[application/zip]
        type: Literal[base64]


    class azure.ai.extensions.openai.responses.InputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.extensions.openai.responses.InputFileContentParam(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": Optional[str]
        key "file_id": Optional[str]
        key "file_url": Optional[str]
        key "filename": Optional[str]
        key "type": Required[Literal["input_file"]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[input_file]


    class azure.ai.extensions.openai.responses.InputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.extensions.openai.responses.InputImageContentParamAutoParam(TypedDict, total=False):
        key "detail": Optional[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal["input_image"]]
        detail: DetailEnum
        file_id: str
        image_url: str
        type: Literal[input_image]


    class azure.ai.extensions.openai.responses.InputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.extensions.openai.responses.InputTextContentParam(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["input_text"]]
        text: str
        type: Literal[input_text]


    class azure.ai.extensions.openai.responses.ItemCodeInterpreterToolCall(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal[code_interpreter_call]]
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[ItemType.CODE_INTERPRETER_CALL]


    class azure.ai.extensions.openai.responses.ItemComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[computer_call]]
        action: ComputerAction
        actions: list[ComputerAction]
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemType.COMPUTER_CALL]


    class azure.ai.extensions.openai.responses.ItemCustomToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "type": Required[Literal[custom_tool_call]]
        call_id: str
        id: str
        input: str
        name: str
        namespace: str
        type: Literal[ItemType.CUSTOM_TOOL_CALL]


    class azure.ai.extensions.openai.responses.ItemCustomToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "type": Required[Literal[custom_tool_call_output]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[ItemType.CUSTOM_TOOL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldAdditionalTools(TypedDict, total=False):
        key "id": Required[str]
        key "role": Required[MessageRole[_, _, a, r, g, s, _, _]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[additional_tools]]
        id: str
        role: MessageRole
        tools: list[Tool]
        type: Literal[ItemFieldType.ADDITIONAL_TOOLS]


    class azure.ai.extensions.openai.responses.ItemFieldApplyPatchToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "operation": Required[ApplyPatchFileOperation]
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal[apply_patch_call]]
        call_id: str
        created_by: str
        id: str
        operation: ApplyPatchFileOperation
        status: ApplyPatchCallStatus
        type: Literal[ItemFieldType.APPLY_PATCH_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldApplyPatchToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "output": Optional[str]
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal[apply_patch_call_output]]
        call_id: str
        created_by: str
        id: str
        output: str
        status: ApplyPatchCallOutputStatus
        type: Literal[ItemFieldType.APPLY_PATCH_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldCodeInterpreterToolCall(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal[code_interpreter_call]]
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[ItemFieldType.CODE_INTERPRETER_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldCompactionBody(TypedDict, total=False):
        key "created_by": str
        key "encrypted_content": Required[str]
        key "id": Required[str]
        key "type": Required[Literal[compaction]]
        created_by: str
        encrypted_content: str
        id: str
        type: Literal[ItemFieldType.COMPACTION]


    class azure.ai.extensions.openai.responses.ItemFieldComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[computer_call]]
        action: ComputerAction
        actions: list[ComputerAction]
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.COMPUTER_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldComputerToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[ComputerScreenshotImage]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[computer_call_output]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        call_id: str
        id: str
        output: ComputerScreenshotImage
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.COMPUTER_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldCustomToolCall(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "input": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "type": Required[Literal[custom_tool_call]]
        call_id: str
        id: str
        input: str
        name: str
        namespace: str
        type: Literal[ItemFieldType.CUSTOM_TOOL_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldCustomToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": str
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "type": Required[Literal[custom_tool_call_output]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        type: Literal[ItemFieldType.CUSTOM_TOOL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldFileSearchToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[file_search_call]]
        id: str
        queries: list[str]
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[ItemFieldType.FILE_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldFunctionShellCall(TypedDict, total=False):
        key "action": Required[FunctionShellAction]
        key "call_id": Required[str]
        key "created_by": str
        key "environment": Required[Optional[FunctionShellCallEnvironment]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call]]
        action: FunctionShellAction
        call_id: str
        created_by: str
        environment: FunctionShellCallEnvironment
        id: str
        status: FunctionShellCallStatus
        type: Literal[ItemFieldType.SHELL_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldFunctionShellCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "created_by": str
        key "id": Required[str]
        key "max_output_length": Required[Optional[int]]
        key "output": Required[list[FunctionShellCallOutputContent]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call_output]]
        call_id: str
        created_by: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        status: FunctionShellCallOutputStatusEnum
        type: Literal[ItemFieldType.SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldFunctionToolCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[function_call]]
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.FUNCTION_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldFunctionToolCallOutput(TypedDict, total=False):
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[function_call_output]]
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.FUNCTION_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldImageGenToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal[image_generation_call]]
        id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[ItemFieldType.IMAGE_GENERATION_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "call_id": Required[str]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call]]
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.LOCAL_SHELL_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldLocalShellToolCallOutput(TypedDict, total=False):
        key "id": Required[str]
        key "output": Required[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call_output]]
        id: str
        output: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemFieldType.LOCAL_SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldMcpApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal[mcp_approval_request]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[ItemFieldType.MCP_APPROVAL_REQUEST]


    class azure.ai.extensions.openai.responses.ItemFieldMcpApprovalResponseResource(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "type": Required[Literal[mcp_approval_response]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[ItemFieldType.MCP_APPROVAL_RESPONSE]


    class azure.ai.extensions.openai.responses.ItemFieldMcpListTools(TypedDict, total=False):
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[mcp_list_tools]]
        error: RealtimeMCPError
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[ItemFieldType.MCP_LIST_TOOLS]


    class azure.ai.extensions.openai.responses.ItemFieldMcpToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal[mcp_call]]
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[ItemFieldType.MCP_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldMessage(TypedDict, total=False):
        key "content": Required[list[MessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[MessageRole[_, _, a, r, g, s, _, _]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[message]]
        content: list[MessageContent]
        id: str
        phase: MessagePhase
        role: MessageRole
        status: MessageStatus
        type: Literal[ItemFieldType.MESSAGE]


    class azure.ai.extensions.openai.responses.ItemFieldReasoningItem(TypedDict, total=False):
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal[reasoning]]
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[ItemFieldType.REASONING]


    class azure.ai.extensions.openai.responses.ItemFieldToolSearchCall(TypedDict, total=False):
        key "arguments": Required[Any]
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[tool_search_call]]
        arguments: Any
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallStatus
        type: Literal[ItemFieldType.TOOL_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.ItemFieldToolSearchOutput(TypedDict, total=False):
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[tool_search_output]]
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallOutputStatusEnum
        tools: list[Tool]
        type: Literal[ItemFieldType.TOOL_SEARCH_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemFieldType(TypedDict):


    class azure.ai.extensions.openai.responses.ItemFieldWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "searching", "completed", "failed"]]
        key "type": Required[Literal[web_search_call]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal[in_progress, searching, completed, failed]
        type: Literal[ItemFieldType.WEB_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.ItemFileSearchToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[file_search_call]]
        id: str
        queries: list[str]
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[ItemType.FILE_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.ItemFunctionToolCall(TypedDict, total=False):
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[function_call]]
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemType.FUNCTION_CALL]


    class azure.ai.extensions.openai.responses.ItemImageGenToolCall(TypedDict, total=False):
        key "id": Required[str]
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal[image_generation_call]]
        id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[ItemType.IMAGE_GENERATION_CALL]


    class azure.ai.extensions.openai.responses.ItemLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "call_id": Required[str]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call]]
        action: LocalShellExecAction
        call_id: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemType.LOCAL_SHELL_CALL]


    class azure.ai.extensions.openai.responses.ItemLocalShellToolCallOutput(TypedDict, total=False):
        key "id": Required[str]
        key "output": Required[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call_output]]
        id: str
        output: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemType.LOCAL_SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.ItemMcpApprovalRequest(TypedDict, total=False):
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "server_label": Required[str]
        key "type": Required[Literal[mcp_approval_request]]
        arguments: str
        id: str
        name: str
        server_label: str
        type: Literal[ItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.extensions.openai.responses.ItemMcpListTools(TypedDict, total=False):
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[mcp_list_tools]]
        error: RealtimeMCPError
        id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[ItemType.MCP_LIST_TOOLS]


    class azure.ai.extensions.openai.responses.ItemMcpToolCall(TypedDict, total=False):
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal[mcp_call]]
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[ItemType.MCP_CALL]


    class azure.ai.extensions.openai.responses.ItemMessage(TypedDict, total=False):
        key "content": Required[Union[str, list[MessageContent]]]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[MessageRole[_, _, a, r, g, s, _, _]]
        key "type": Required[Literal[message]]
        content: Union[str, list[MessageContent]]
        phase: MessagePhase
        role: MessageRole
        type: Literal[ItemType.MESSAGE]


    class azure.ai.extensions.openai.responses.ItemOutputMessage(TypedDict, total=False):
        key "content": Required[list[OutputMessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "role": Required[Literal["assistant"]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[output_message]]
        content: list[OutputMessageContent]
        id: str
        phase: MessagePhase
        role: Literal[assistant]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[ItemType.OUTPUT_MESSAGE]


    class azure.ai.extensions.openai.responses.ItemReasoningItem(TypedDict, total=False):
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal[reasoning]]
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[ItemType.REASONING]


    class azure.ai.extensions.openai.responses.ItemReferenceParam(TypedDict, total=False):
        key "id": Required[str]
        key "type": Required[Literal[item_reference]]
        id: str
        type: Literal[ItemType.ITEM_REFERENCE]


    class azure.ai.extensions.openai.responses.ItemType(TypedDict):


    class azure.ai.extensions.openai.responses.ItemWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "id": Required[str]
        key "status": Required[Literal["in_progress", "searching", "completed", "failed"]]
        key "type": Required[Literal[web_search_call]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        id: str
        status: Literal[in_progress, searching, completed, failed]
        type: Literal[ItemType.WEB_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.KeyPressAction(TypedDict, total=False):
        key "keys": Required[list[str]]
        key "type": Required[Literal[keypress]]
        keys_property: list[str]
        type: Literal[ComputerActionType.KEYPRESS]


    class azure.ai.extensions.openai.responses.LocalEnvironmentResource(TypedDict, total=False):
        key "type": Required[Literal[local]]
        type: Literal[FunctionShellCallEnvironmentType.LOCAL]


    class azure.ai.extensions.openai.responses.LocalShellExecAction(TypedDict, total=False):
        key "command": Required[list[str]]
        key "env": Required[dict[str, str]]
        key "timeout_ms": Optional[int]
        key "type": Required[Literal["exec"]]
        key "user": Optional[str]
        key "working_directory": Optional[str]
        command: list[str]
        env: dict[str, str]
        timeout_ms: int
        type: Literal[exec]
        user: str
        working_directory: str


    class azure.ai.extensions.openai.responses.LocalShellToolParam(TypedDict, total=False):
        key "description": str
        key "name": str
        key "type": Required[Literal[local_shell]]
        description: str
        name: str
        type: Literal[ToolType.LOCAL_SHELL]


    class azure.ai.extensions.openai.responses.LocalSkillParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "path": Required[str]
        description: str
        name: str
        path: str


    class azure.ai.extensions.openai.responses.LogProb(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        key "top_logprobs": Required[list[TopLogProb]]
        bytes: list[int]
        logprob: float
        token: str
        top_logprobs: list[TopLogProb]


    class azure.ai.extensions.openai.responses.MCPApprovalResponse(TypedDict, total=False):
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Optional[str]
        key "reason": Optional[str]
        key "type": Required[Literal[mcp_approval_response]]
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        type: Literal[ItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.extensions.openai.responses.MCPListToolsTool(TypedDict, total=False):
        key "annotations": Optional[MCPListToolsToolAnnotations]
        key "description": Optional[str]
        key "input_schema": Required[MCPListToolsToolInputSchema]
        key "name": Required[str]
        annotations: MCPListToolsToolAnnotations
        description: str
        input_schema: MCPListToolsToolInputSchema
        name: str


    class azure.ai.extensions.openai.responses.MCPListToolsToolAnnotations(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.MCPListToolsToolInputSchema(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.MCPTool(TypedDict, total=False):
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
        key "type": Required[Literal[mcp]]
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
        tunnel_id: str
        type: Literal[ToolType.MCP]


    class azure.ai.extensions.openai.responses.MCPToolFilter(TypedDict, total=False):
        key "read_only": bool
        read_only: bool
        tool_names: list[str]


    class azure.ai.extensions.openai.responses.MCPToolRequireApproval(TypedDict, total=False):
        key "always": ForwardRef('MCPToolFilter', module='types')
        key "never": ForwardRef('MCPToolFilter', module='types')
        always: MCPToolFilter
        never: MCPToolFilter


    class azure.ai.extensions.openai.responses.MemoryItemKind(TypedDict):


    class azure.ai.extensions.openai.responses.MemorySearchItem(TypedDict, total=False):
        key "memory_item": Required[MemoryItem]
        memory_item: MemoryItem


    class azure.ai.extensions.openai.responses.MemorySearchOptions(TypedDict, total=False):
        key "max_memories": int
        max_memories: int


    class azure.ai.extensions.openai.responses.MemorySearchPreviewTool(TypedDict, total=False):
        key "description": str
        key "memory_store_name": Required[str]
        key "name": str
        key "scope": Required[str]
        key "search_options": ForwardRef('MemorySearchOptions', module='types')
        key "type": Required[Literal[memory_search_preview]]
        key "update_delay": int
        description: str
        memory_store_name: str
        name: str
        scope: str
        search_options: MemorySearchOptions
        type: Literal[ToolType.MEMORY_SEARCH_PREVIEW]
        update_delay: int


    class azure.ai.extensions.openai.responses.MemorySearchToolCallItemParam(TypedDict, total=False):
        key "results": Optional[list[MemorySearchItem]]
        key "type": Required[Literal[memory_search_call]]
        results: list[MemorySearchItem]
        type: Literal[ItemType.MEMORY_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.MemorySearchToolCallItemResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "results": Optional[list[MemorySearchItem]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[memory_search_call]]
        agent_reference: AgentReference
        id: str
        response_id: str
        results: list[MemorySearchItem]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[OutputItemType.MEMORY_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.MessageContentInputFileContent(TypedDict, total=False):
        key "detail": Literal["low", "high"]
        key "file_data": str
        key "file_id": Optional[str]
        key "file_url": str
        key "filename": str
        key "type": Required[Literal[input_file]]
        detail: FileInputDetail
        file_data: str
        file_id: str
        file_url: str
        filename: str
        type: Literal[MessageContentType.INPUT_FILE]


    class azure.ai.extensions.openai.responses.MessageContentInputImageContent(TypedDict, total=False):
        key "detail": Required[Literal["low", "high", "auto", "original"]]
        key "file_id": Optional[str]
        key "image_url": Optional[str]
        key "type": Required[Literal[input_image]]
        detail: ImageDetail
        file_id: str
        image_url: str
        type: Literal[MessageContentType.INPUT_IMAGE]


    class azure.ai.extensions.openai.responses.MessageContentInputTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[input_text]]
        text: str
        type: Literal[MessageContentType.INPUT_TEXT]


    class azure.ai.extensions.openai.responses.MessageContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal[output_text]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[MessageContentType.OUTPUT_TEXT]


    class azure.ai.extensions.openai.responses.MessageContentReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[reasoning_text]]
        text: str
        type: Literal[MessageContentType.REASONING_TEXT]


    class azure.ai.extensions.openai.responses.MessageContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal[refusal]]
        refusal: str
        type: Literal[MessageContentType.REFUSAL]


    class azure.ai.extensions.openai.responses.MessageContentType(TypedDict):


    class azure.ai.extensions.openai.responses.MessageRole(TypedDict):


    class azure.ai.extensions.openai.responses.Metadata(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.MicrosoftFabricPreviewTool(TypedDict, total=False):
        key "description": str
        key "fabric_dataagent_preview": Required[FabricDataAgentToolParameters]
        key "name": str
        key "type": Required[Literal[fabric_dataagent_preview]]
        description: str
        fabric_dataagent_preview: FabricDataAgentToolParameters
        name: str
        type: Literal[ToolType.FABRIC_DATAAGENT_PREVIEW]


    class azure.ai.extensions.openai.responses.Moderation(TypedDict, total=False):
        key "input": Required[ModerationEntry]
        key "output": Required[ModerationEntry]
        input: ModerationEntry
        output: ModerationEntry


    class azure.ai.extensions.openai.responses.ModerationEntryType(TypedDict):


    class azure.ai.extensions.openai.responses.ModerationErrorBody(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        key "type": Required[Literal[error]]
        code: str
        message: str
        type: Literal[ModerationEntryType.ERROR]


    class azure.ai.extensions.openai.responses.ModerationParam(TypedDict, total=False):
        key "model": Required[str]
        model: str


    class azure.ai.extensions.openai.responses.ModerationResultBody(TypedDict, total=False):
        key "categories": Required[dict[str, bool]]
        key "category_applied_input_types": Required[dict[str, list[Literal["text", "image"]]]]
        key "category_scores": Required[dict[str, float]]
        key "flagged": Required[bool]
        key "model": Required[str]
        key "type": Required[Literal[moderation_result]]
        categories: dict[str, bool]
        category_applied_input_types: dict[str, list[ModerationInputType]]
        category_scores: dict[str, float]
        flagged: bool
        model: str
        type: Literal[ModerationEntryType.MODERATION_RESULT]


    class azure.ai.extensions.openai.responses.MoveParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "type": Required[Literal[move]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        type: Literal[ComputerActionType.MOVE]
        x: int
        y: int


    class azure.ai.extensions.openai.responses.NamespaceToolParam(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "tools": Required[list[Union[FunctionToolParam, CustomToolParam]]]
        key "type": Required[Literal[namespace]]
        description: str
        name: str
        tools: list[Union[FunctionToolParam, CustomToolParam]]
        type: Literal[ToolType.NAMESPACE]


    class azure.ai.extensions.openai.responses.OAuthConsentRequestOutputItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "consent_link": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[oauth_consent_request]]
        agent_reference: AgentReference
        consent_link: str
        id: str
        response_id: str
        server_label: str
        type: Literal[OutputItemType.OAUTH_CONSENT_REQUEST]


    class azure.ai.extensions.openai.responses.OpenApiAnonymousAuthDetails(TypedDict, total=False):
        key "type": Required[Literal[anonymous]]
        type: Literal[OpenApiAuthType.ANONYMOUS]


    class azure.ai.extensions.openai.responses.OpenApiAuthType(TypedDict):


    class azure.ai.extensions.openai.responses.OpenApiFunctionDefinition(TypedDict, total=False):
        key "auth": Required[OpenApiAuthDetails]
        key "description": str
        key "name": Required[str]
        key "spec": Required[dict[str, Any]]
        auth: OpenApiAuthDetails
        default_params: list[str]
        description: str
        functions: list[OpenApiFunctionDefinitionFunction]
        name: str
        spec: dict[str, Any]


    class azure.ai.extensions.openai.responses.OpenApiFunctionDefinitionFunction(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "parameters": Required[dict[str, Any]]
        description: str
        name: str
        parameters: dict[str, Any]


    class azure.ai.extensions.openai.responses.OpenApiManagedAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiManagedSecurityScheme]
        key "type": Required[Literal[managed_identity]]
        security_scheme: OpenApiManagedSecurityScheme
        type: Literal[OpenApiAuthType.MANAGED_IDENTITY]


    class azure.ai.extensions.openai.responses.OpenApiManagedSecurityScheme(TypedDict, total=False):
        key "audience": Required[str]
        audience: str


    class azure.ai.extensions.openai.responses.OpenApiProjectConnectionAuthDetails(TypedDict, total=False):
        key "security_scheme": Required[OpenApiProjectConnectionSecurityScheme]
        key "type": Required[Literal[project_connection]]
        security_scheme: OpenApiProjectConnectionSecurityScheme
        type: Literal[OpenApiAuthType.PROJECT_CONNECTION]


    class azure.ai.extensions.openai.responses.OpenApiProjectConnectionSecurityScheme(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.extensions.openai.responses.OpenApiTool(TypedDict, total=False):
        key "openapi": Required[OpenApiFunctionDefinition]
        key "type": Required[Literal[openapi]]
        openapi: OpenApiFunctionDefinition
        type: Literal[ToolType.OPENAPI]


    class azure.ai.extensions.openai.responses.OpenApiToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[openapi_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.OPENAPI_CALL]


    class azure.ai.extensions.openai.responses.OpenApiToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[openapi_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        name: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.OPENAPI_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal[output_text]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[OutputContentType.OUTPUT_TEXT]


    class azure.ai.extensions.openai.responses.OutputContentReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[reasoning_text]]
        text: str
        type: Literal[OutputContentType.REASONING_TEXT]


    class azure.ai.extensions.openai.responses.OutputContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal[refusal]]
        refusal: str
        type: Literal[OutputContentType.REFUSAL]


    class azure.ai.extensions.openai.responses.OutputContentType(TypedDict):


    class azure.ai.extensions.openai.responses.OutputItemAdditionalTools(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "role": Required[MessageRole[_, _, a, r, g, s, _, _]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[additional_tools]]
        agent_reference: AgentReference
        id: str
        response_id: str
        role: MessageRole
        tools: list[Tool]
        type: Literal[OutputItemType.ADDITIONAL_TOOLS]


    class azure.ai.extensions.openai.responses.OutputItemApplyPatchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "operation": Required[ApplyPatchFileOperation]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed"]]
        key "type": Required[Literal[apply_patch_call]]
        agent_reference: AgentReference
        call_id: str
        id: str
        operation: ApplyPatchFileOperation
        response_id: str
        status: ApplyPatchCallStatus
        type: Literal[OutputItemType.APPLY_PATCH_CALL]


    class azure.ai.extensions.openai.responses.OutputItemApplyPatchToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "status": Required[Literal["completed", "failed"]]
        key "type": Required[Literal[apply_patch_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: str
        response_id: str
        status: ApplyPatchCallOutputStatus
        type: Literal[OutputItemType.APPLY_PATCH_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemCodeInterpreterToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "code": Required[Optional[str]]
        key "container_id": Required[str]
        key "id": Required[str]
        key "outputs": Required[Optional[list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "interpreting", "failed"]]
        key "type": Required[Literal[code_interpreter_call]]
        agent_reference: AgentReference
        code: str
        container_id: str
        id: str
        outputs: list[Union[CodeInterpreterOutputLogs, CodeInterpreterOutputImage]]
        response_id: str
        status: Literal[in_progress, completed, incomplete, interpreting, failed]
        type: Literal[OutputItemType.CODE_INTERPRETER_CALL]


    class azure.ai.extensions.openai.responses.OutputItemCompactionBody(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "encrypted_content": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "type": Required[Literal[compaction]]
        agent_reference: AgentReference
        encrypted_content: str
        id: str
        response_id: str
        type: Literal[OutputItemType.COMPACTION]


    class azure.ai.extensions.openai.responses.OutputItemComputerToolCall(TypedDict, total=False):
        key "action": ForwardRef('ComputerAction', module='types')
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "pending_safety_checks": Required[list[ComputerCallSafetyCheckParam]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[computer_call]]
        action: ComputerAction
        actions: list[ComputerAction]
        agent_reference: AgentReference
        call_id: str
        id: str
        pending_safety_checks: list[ComputerCallSafetyCheckParam]
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.COMPUTER_CALL]


    class azure.ai.extensions.openai.responses.OutputItemComputerToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[ComputerScreenshotImage]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[computer_call_output]]
        acknowledged_safety_checks: list[ComputerCallSafetyCheckParam]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ComputerScreenshotImage
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.COMPUTER_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemFileSearchToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "queries": Required[list[str]]
        key "response_id": str
        key "results": Optional[list[FileSearchToolCallResults]]
        key "status": Required[Literal["in_progress", "searching", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[file_search_call]]
        agent_reference: AgentReference
        id: str
        queries: list[str]
        response_id: str
        results: list[FileSearchToolCallResults]
        status: Literal[in_progress, searching, completed, incomplete, failed]
        type: Literal[OutputItemType.FILE_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.OutputItemFunctionShellCall(TypedDict, total=False):
        key "action": Required[FunctionShellAction]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "environment": Required[Optional[FunctionShellCallEnvironment]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call]]
        action: FunctionShellAction
        agent_reference: AgentReference
        call_id: str
        environment: FunctionShellCallEnvironment
        id: str
        response_id: str
        status: FunctionShellCallStatus
        type: Literal[OutputItemType.SHELL_CALL]


    class azure.ai.extensions.openai.responses.OutputItemFunctionShellCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "max_output_length": Required[Optional[int]]
        key "output": Required[list[FunctionShellCallOutputContent]]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[shell_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        max_output_length: int
        output: list[FunctionShellCallOutputContent]
        response_id: str
        status: FunctionShellCallOutputStatusEnum
        type: Literal[OutputItemType.SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemFunctionToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "namespace": str
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[function_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        name: str
        namespace: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.FUNCTION_CALL]


    class azure.ai.extensions.openai.responses.OutputItemFunctionToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": Required[Union[str, list[FunctionAndCustomToolCallOutput]]]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "type": Required[Literal[function_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: Union[str, list[FunctionAndCustomToolCallOutput]]
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.FUNCTION_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemImageGenToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "result": Required[Optional[str]]
        key "status": Required[Literal["in_progress", "completed", "generating", "failed"]]
        key "type": Required[Literal[image_generation_call]]
        agent_reference: AgentReference
        id: str
        response_id: str
        result: str
        status: Literal[in_progress, completed, generating, failed]
        type: Literal[OutputItemType.IMAGE_GENERATION_CALL]


    class azure.ai.extensions.openai.responses.OutputItemLocalShellToolCall(TypedDict, total=False):
        key "action": Required[LocalShellExecAction]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call]]
        action: LocalShellExecAction
        agent_reference: AgentReference
        call_id: str
        id: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.LOCAL_SHELL_CALL]


    class azure.ai.extensions.openai.responses.OutputItemLocalShellToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "output": Required[str]
        key "response_id": str
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[local_shell_call_output]]
        agent_reference: AgentReference
        id: str
        output: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.LOCAL_SHELL_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemMcpApprovalRequest(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "type": Required[Literal[mcp_approval_request]]
        agent_reference: AgentReference
        arguments: str
        id: str
        name: str
        response_id: str
        server_label: str
        type: Literal[OutputItemType.MCP_APPROVAL_REQUEST]


    class azure.ai.extensions.openai.responses.OutputItemMcpApprovalResponseResource(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "approval_request_id": Required[str]
        key "approve": Required[bool]
        key "id": Required[str]
        key "reason": Optional[str]
        key "response_id": str
        key "type": Required[Literal[mcp_approval_response]]
        agent_reference: AgentReference
        approval_request_id: str
        approve: bool
        id: str
        reason: str
        response_id: str
        type: Literal[OutputItemType.MCP_APPROVAL_RESPONSE]


    class azure.ai.extensions.openai.responses.OutputItemMcpListTools(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "error": ForwardRef('RealtimeMCPError', module='types')
        key "id": Required[str]
        key "response_id": str
        key "server_label": Required[str]
        key "tools": Required[list[MCPListToolsTool]]
        key "type": Required[Literal[mcp_list_tools]]
        agent_reference: AgentReference
        error: RealtimeMCPError
        id: str
        response_id: str
        server_label: str
        tools: list[MCPListToolsTool]
        type: Literal[OutputItemType.MCP_LIST_TOOLS]


    class azure.ai.extensions.openai.responses.OutputItemMcpToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "approval_request_id": Optional[str]
        key "arguments": Required[str]
        key "id": Required[str]
        key "name": Required[str]
        key "output": Optional[str]
        key "response_id": str
        key "server_label": Required[str]
        key "status": Literal["in_progress", "completed", "incomplete", "calling", "failed"]
        key "type": Required[Literal[mcp_call]]
        agent_reference: AgentReference
        approval_request_id: str
        arguments: str
        error: dict[str, Any]
        id: str
        name: str
        output: str
        response_id: str
        server_label: str
        status: MCPToolCallStatus
        type: Literal[OutputItemType.MCP_CALL]


    class azure.ai.extensions.openai.responses.OutputItemMessage(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "content": Required[list[MessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "response_id": str
        key "role": Required[MessageRole[_, _, a, r, g, s, _, _]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[message]]
        agent_reference: AgentReference
        content: list[MessageContent]
        id: str
        phase: MessagePhase
        response_id: str
        role: MessageRole
        status: MessageStatus
        type: Literal[OutputItemType.MESSAGE]


    class azure.ai.extensions.openai.responses.OutputItemOutputMessage(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "content": Required[list[OutputMessageContent]]
        key "id": Required[str]
        key "phase": Optional[Literal["commentary", "final_answer"]]
        key "response_id": str
        key "role": Required[Literal["assistant"]]
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[output_message]]
        agent_reference: AgentReference
        content: list[OutputMessageContent]
        id: str
        phase: MessagePhase
        response_id: str
        role: Literal[assistant]
        status: Literal[in_progress, completed, incomplete]
        type: Literal[OutputItemType.OUTPUT_MESSAGE]


    class azure.ai.extensions.openai.responses.OutputItemReasoningItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "encrypted_content": Optional[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Literal["in_progress", "completed", "incomplete"]
        key "summary": Required[list[SummaryTextContent]]
        key "type": Required[Literal[reasoning]]
        agent_reference: AgentReference
        content: list[ReasoningTextContent]
        encrypted_content: str
        id: str
        response_id: str
        status: Literal[in_progress, completed, incomplete]
        summary: list[SummaryTextContent]
        type: Literal[OutputItemType.REASONING]


    class azure.ai.extensions.openai.responses.OutputItemToolSearchCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[Any]
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[tool_search_call]]
        agent_reference: AgentReference
        arguments: Any
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        response_id: str
        status: FunctionCallStatus
        type: Literal[OutputItemType.TOOL_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.OutputItemToolSearchOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[Optional[str]]
        key "created_by": str
        key "execution": Required[Literal["server", "client"]]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[tool_search_output]]
        agent_reference: AgentReference
        call_id: str
        created_by: str
        execution: ToolSearchExecutionType
        id: str
        response_id: str
        status: FunctionCallOutputStatusEnum
        tools: list[Tool]
        type: Literal[OutputItemType.TOOL_SEARCH_OUTPUT]


    class azure.ai.extensions.openai.responses.OutputItemType(TypedDict):


    class azure.ai.extensions.openai.responses.OutputItemWebSearchToolCall(TypedDict, total=False):
        key "action": Required[Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "searching", "completed", "failed"]]
        key "type": Required[Literal[web_search_call]]
        action: Union[WebSearchActionSearch, WebSearchActionOpenPage, WebSearchActionFind]
        agent_reference: AgentReference
        id: str
        response_id: str
        status: Literal[in_progress, searching, completed, failed]
        type: Literal[OutputItemType.WEB_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.OutputMessageContentOutputTextContent(TypedDict, total=False):
        key "annotations": Required[list[Annotation]]
        key "logprobs": Required[list[LogProb]]
        key "text": Required[str]
        key "type": Required[Literal[output_text]]
        annotations: list[Annotation]
        logprobs: list[LogProb]
        text: str
        type: Literal[OutputMessageContentType.OUTPUT_TEXT]


    class azure.ai.extensions.openai.responses.OutputMessageContentRefusalContent(TypedDict, total=False):
        key "refusal": Required[str]
        key "type": Required[Literal[refusal]]
        refusal: str
        type: Literal[OutputMessageContentType.REFUSAL]


    class azure.ai.extensions.openai.responses.OutputMessageContentType(TypedDict):


    class azure.ai.extensions.openai.responses.Prompt(TypedDict, total=False):
        key "id": Required[str]
        key "variables": Optional[ResponsePromptVariables]
        key "version": Optional[str]
        id: str
        variables: ResponsePromptVariables
        version: str


    class azure.ai.extensions.openai.responses.RankingOptions(TypedDict, total=False):
        key "hybrid_search": ForwardRef('HybridSearchOptions', module='types')
        key "ranker": Literal["auto", "default-2024-11-15"]
        key "score_threshold": float
        hybrid_search: HybridSearchOptions
        ranker: RankerVersionType
        score_threshold: float


    class azure.ai.extensions.openai.responses.RealtimeMCPHTTPError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[http_error]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.HTTP_ERROR]


    class azure.ai.extensions.openai.responses.RealtimeMCPProtocolError(TypedDict, total=False):
        key "code": Required[int]
        key "message": Required[str]
        key "type": Required[Literal[protocol_error]]
        code: int
        message: str
        type: Literal[RealtimeMcpErrorType.PROTOCOL_ERROR]


    class azure.ai.extensions.openai.responses.RealtimeMCPToolExecutionError(TypedDict, total=False):
        key "message": Required[str]
        key "type": Required[Literal[tool_execution_error]]
        message: str
        type: Literal[RealtimeMcpErrorType.TOOL_EXECUTION_ERROR]


    class azure.ai.extensions.openai.responses.RealtimeMcpErrorType(TypedDict):


    class azure.ai.extensions.openai.responses.Reasoning(TypedDict, total=False):
        key "context": Optional[Literal["auto", "current_turn", "all_turns"]]
        key "effort": Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh"]]
        key "generate_summary": Optional[Literal["auto", "concise", "detailed"]]
        key "summary": Optional[Literal["auto", "concise", "detailed"]]
        context: Literal[auto, current_turn, all_turns]
        effort: Literal[none, minimal, low, medium, high, xhigh]
        generate_summary: Literal[auto, concise, detailed]
        summary: Literal[auto, concise, detailed]


    class azure.ai.extensions.openai.responses.ReasoningTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["reasoning_text"]]
        text: str
        type: Literal[reasoning_text]


    class azure.ai.extensions.openai.responses.ResponseAudioDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_DELTA]


    class azure.ai.extensions.openai.responses.ResponseAudioDoneEvent(TypedDict, total=False):
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_DONE]


    class azure.ai.extensions.openai.responses.ResponseAudioTranscriptDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA]


    class azure.ai.extensions.openai.responses.ResponseAudioTranscriptDoneEvent(TypedDict, total=False):
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE]


    class azure.ai.extensions.openai.responses.ResponseCodeInterpreterCallCodeDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA]


    class azure.ai.extensions.openai.responses.ResponseCodeInterpreterCallCodeDoneEvent(TypedDict, total=False):
        key "code": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        code: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE]


    class azure.ai.extensions.openai.responses.ResponseCodeInterpreterCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseCodeInterpreterCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseCodeInterpreterCallInterpretingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[interpreting]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING]


    class azure.ai.extensions.openai.responses.ResponseCompletedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseContentPartAddedEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[OutputContent]
        key "sequence_number": Required[int]
        key "type": Required[Literal[added]]
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CONTENT_PART_ADDED]


    class azure.ai.extensions.openai.responses.ResponseContentPartDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[OutputContent]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        content_index: int
        item_id: str
        output_index: int
        part: OutputContent
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CONTENT_PART_DONE]


    class azure.ai.extensions.openai.responses.ResponseCreatedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[created]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CREATED]


    class azure.ai.extensions.openai.responses.ResponseCustomToolCallInputDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA]


    class azure.ai.extensions.openai.responses.ResponseCustomToolCallInputDoneEvent(TypedDict, total=False):
        key "input": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        input: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE]


    class azure.ai.extensions.openai.responses.ResponseErrorEvent(TypedDict, total=False):
        key "code": Required[Optional[str]]
        key "message": Required[str]
        key "param": Required[Optional[str]]
        key "sequence_number": Required[int]
        key "type": Required[Literal[error]]
        code: str
        message: str
        param: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.ERROR]


    class azure.ai.extensions.openai.responses.ResponseErrorInfo(TypedDict, total=False):
        key "code": Required[Literal["server_error", "rate_limit_exceeded", "invalid_prompt", "vector_store_timeout", "invalid_image", "invalid_image_format", "invalid_base64_image", "invalid_image_url", "image_too_large", "image_too_small", "image_parse_error", "image_content_policy_violation", "invalid_image_mode", "image_file_too_large", "unsupported_image_media_type", "empty_image_file", "failed_to_download_image", "image_file_not_found"]]
        key "message": Required[str]
        code: ResponseErrorCode
        message: str


    class azure.ai.extensions.openai.responses.ResponseFailedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[failed]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FAILED]


    class azure.ai.extensions.openai.responses.ResponseFileSearchCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseFileSearchCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseFileSearchCallSearchingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[searching]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FILE_SEARCH_CALL_SEARCHING]


    class azure.ai.extensions.openai.responses.ResponseFormatJsonSchemaSchema(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.ResponseFunctionCallArgumentsDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA]


    class azure.ai.extensions.openai.responses.ResponseFunctionCallArgumentsDoneEvent(TypedDict, total=False):
        key "arguments": Required[str]
        key "item_id": Required[str]
        key "name": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        arguments: str
        item_id: str
        name: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE]


    class azure.ai.extensions.openai.responses.ResponseImageGenCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseImageGenCallGeneratingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[generating]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_GENERATING]


    class azure.ai.extensions.openai.responses.ResponseImageGenCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseImageGenCallPartialImageEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "partial_image_b64": Required[str]
        key "partial_image_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[partial_image]]
        item_id: str
        output_index: int
        partial_image_b64: str
        partial_image_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE]


    class azure.ai.extensions.openai.responses.ResponseInProgressEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseIncompleteDetails(TypedDict, total=False):
        key "reason": Literal["max_output_tokens", "content_filter"]
        reason: Literal[max_output_tokens, content_filter]


    class azure.ai.extensions.openai.responses.ResponseIncompleteEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[incomplete]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_INCOMPLETE]


    class azure.ai.extensions.openai.responses.ResponseIncompleteReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTENT_FILTER = "content_filter"
        MAX_OUTPUT_TOKENS = "max_output_tokens"


    class azure.ai.extensions.openai.responses.ResponseLogProb(TypedDict, total=False):
        key "logprob": Required[float]
        key "token": Required[str]
        logprob: float
        token: str
        top_logprobs: list[ResponseLogProbTopLogprobs]


    class azure.ai.extensions.openai.responses.ResponseLogProbTopLogprobs(TypedDict, total=False):
        key "logprob": float
        key "token": str
        logprob: float
        token: str


    class azure.ai.extensions.openai.responses.ResponseMCPCallArgumentsDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DELTA]


    class azure.ai.extensions.openai.responses.ResponseMCPCallArgumentsDoneEvent(TypedDict, total=False):
        key "arguments": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        arguments: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_ARGUMENTS_DONE]


    class azure.ai.extensions.openai.responses.ResponseMCPCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseMCPCallFailedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[failed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_FAILED]


    class azure.ai.extensions.openai.responses.ResponseMCPCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_CALL_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseMCPListToolsCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseMCPListToolsFailedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[failed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_FAILED]


    class azure.ai.extensions.openai.responses.ResponseMCPListToolsInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseObject(TypedDict, total=False):
        key "agent_reference": Required[Optional[AgentReference]]
        key "background": Optional[bool]
        key "completed_at": Optional[int]
        key "conversation": Optional[ConversationReference]
        key "created_at": Required[int]
        key "error": Required[Optional[ResponseErrorInfo]]
        key "id": Required[str]
        key "incomplete_details": Required[Optional[ResponseIncompleteDetails]]
        key "instructions": Required[Optional[Union[str, list[Item]]]]
        key "max_output_tokens": Optional[int]
        key "max_tool_calls": Optional[int]
        key "metadata": Optional[Metadata]
        key "model": str
        key "moderation": Optional[Moderation]
        key "object": Required[Literal["response"]]
        key "output": Required[list[OutputItem]]
        key "output_text": Optional[str]
        key "parallel_tool_calls": Required[bool]
        key "previous_response_id": Optional[str]
        key "prompt": ForwardRef('Prompt', module='types')
        key "prompt_cache_key": str
        key "prompt_cache_retention": Optional[Literal["in_memory", "24h"]]
        key "reasoning": Optional[Reasoning]
        key "safety_identifier": str
        key "service_tier": Optional[Literal["auto", "default", "flex", "scale", "priority"]]
        key "status": Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"]
        key "temperature": Optional[float]
        key "text": ForwardRef('ResponseTextParam', module='types')
        key "tool_choice": Union[Literal["none", "auto", "required"], ToolChoiceParam]
        key "top_logprobs": Optional[int]
        key "top_p": Optional[float]
        key "truncation": Optional[Literal["auto", "disabled"]]
        key "usage": ForwardRef('ResponseUsage', module='types')
        key "user": str
        agent_reference: AgentReference
        background: bool
        completed_at: int
        conversation: ConversationReference
        created_at: int
        error: ResponseErrorInfo
        id: str
        incomplete_details: ResponseIncompleteDetails
        instructions: Union[str, list[Item]]
        max_output_tokens: int
        max_tool_calls: int
        metadata: Metadata
        model: str
        moderation: Moderation
        object: Literal[response]
        output: list[OutputItem]
        output_text: str
        parallel_tool_calls: bool
        previous_response_id: str
        prompt: Prompt
        prompt_cache_key: str
        prompt_cache_retention: Literal[in_memory, 24h]
        reasoning: Reasoning
        safety_identifier: str
        service_tier: Literal[auto, default, flex, scale, priority]
        status: Literal[completed, failed, in_progress, cancelled, queued, incomplete]
        temperature: float
        text: ResponseTextParam
        tool_choice: Union[ToolChoiceOptions, ToolChoiceParam]
        tools: list[Tool]
        top_logprobs: int
        top_p: float
        truncation: Literal[auto, disabled]
        usage: ResponseUsage
        user: str


    class azure.ai.extensions.openai.responses.ResponseOutputItemAddedEvent(TypedDict, total=False):
        key "item": Required[OutputItem]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[added]]
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED]


    class azure.ai.extensions.openai.responses.ResponseOutputItemDoneEvent(TypedDict, total=False):
        key "item": Required[OutputItem]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        item: OutputItem
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE]


    class azure.ai.extensions.openai.responses.ResponseOutputTextAnnotationAddedEvent(TypedDict, total=False):
        key "annotation": Required[Annotation]
        key "annotation_index": Required[int]
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[added]]
        annotation: Annotation
        annotation_index: int
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED]


    class azure.ai.extensions.openai.responses.ResponsePromptVariables(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.ResponseQueuedEvent(TypedDict, total=False):
        key "response": Required[ResponseObject]
        key "sequence_number": Required[int]
        key "type": Required[Literal[queued]]
        response: ResponseObject
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_QUEUED]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryPartAddedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[ResponseReasoningSummaryPartAddedEventPart]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal[added]]
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartAddedEventPart
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_ADDED]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryPartAddedEventPart(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["summary_text"]]
        text: str
        type: Literal[summary_text]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryPartDoneEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "part": Required[ResponseReasoningSummaryPartDoneEventPart]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal[done]]
        item_id: str
        output_index: int
        part: ResponseReasoningSummaryPartDoneEventPart
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_PART_DONE]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryPartDoneEventPart(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal["summary_text"]]
        text: str
        type: Literal[summary_text]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryTextDeltaEvent(TypedDict, total=False):
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "type": Required[Literal[delta]]
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DELTA]


    class azure.ai.extensions.openai.responses.ResponseReasoningSummaryTextDoneEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "summary_index": Required[int]
        key "text": Required[str]
        key "type": Required[Literal[done]]
        item_id: str
        output_index: int
        sequence_number: int
        summary_index: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_SUMMARY_TEXT_DONE]


    class azure.ai.extensions.openai.responses.ResponseReasoningTextDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_TEXT_DELTA]


    class azure.ai.extensions.openai.responses.ResponseReasoningTextDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "text": Required[str]
        key "type": Required[Literal[done]]
        content_index: int
        item_id: str
        output_index: int
        sequence_number: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_REASONING_TEXT_DONE]


    class azure.ai.extensions.openai.responses.ResponseRefusalDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        content_index: int
        delta: str
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REFUSAL_DELTA]


    class azure.ai.extensions.openai.responses.ResponseRefusalDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "refusal": Required[str]
        key "sequence_number": Required[int]
        key "type": Required[Literal[done]]
        content_index: int
        item_id: str
        output_index: int
        refusal: str
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_REFUSAL_DONE]


    class azure.ai.extensions.openai.responses.ResponseStreamEventType(TypedDict):


    class azure.ai.extensions.openai.responses.ResponseStreamOptions(TypedDict, total=False):
        key "include_obfuscation": bool
        include_obfuscation: bool


    class azure.ai.extensions.openai.responses.ResponseTextDeltaEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "delta": Required[str]
        key "item_id": Required[str]
        key "logprobs": Required[list[ResponseLogProb]]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[delta]]
        content_index: int
        delta: str
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA]


    class azure.ai.extensions.openai.responses.ResponseTextDoneEvent(TypedDict, total=False):
        key "content_index": Required[int]
        key "item_id": Required[str]
        key "logprobs": Required[list[ResponseLogProb]]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "text": Required[str]
        key "type": Required[Literal[done]]
        content_index: int
        item_id: str
        logprobs: list[ResponseLogProb]
        output_index: int
        sequence_number: int
        text: str
        type: Literal[ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE]


    class azure.ai.extensions.openai.responses.ResponseTextParam(TypedDict, total=False):
        key "format": ForwardRef('TextResponseFormatConfiguration', module='types')
        key "verbosity": Optional[Literal["low", "medium", "high"]]
        format: TextResponseFormatConfiguration
        verbosity: Literal[low, medium, high]


    class azure.ai.extensions.openai.responses.ResponseUsage(TypedDict, total=False):
        key "input_tokens": Required[int]
        key "input_tokens_details": Required[ResponseUsageInputTokensDetails]
        key "output_tokens": Required[int]
        key "output_tokens_details": Required[ResponseUsageOutputTokensDetails]
        key "total_tokens": Required[int]
        input_tokens: int
        input_tokens_details: ResponseUsageInputTokensDetails
        output_tokens: int
        output_tokens_details: ResponseUsageOutputTokensDetails
        total_tokens: int


    class azure.ai.extensions.openai.responses.ResponseUsageInputTokensDetails(TypedDict, total=False):
        key "cached_tokens": Required[int]
        cached_tokens: int


    class azure.ai.extensions.openai.responses.ResponseUsageOutputTokensDetails(TypedDict, total=False):
        key "reasoning_tokens": Required[int]
        reasoning_tokens: int


    class azure.ai.extensions.openai.responses.ResponseWebSearchCallCompletedEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[completed]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_COMPLETED]


    class azure.ai.extensions.openai.responses.ResponseWebSearchCallInProgressEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[in_progress]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS]


    class azure.ai.extensions.openai.responses.ResponseWebSearchCallSearchingEvent(TypedDict, total=False):
        key "item_id": Required[str]
        key "output_index": Required[int]
        key "sequence_number": Required[int]
        key "type": Required[Literal[searching]]
        item_id: str
        output_index: int
        sequence_number: int
        type: Literal[ResponseStreamEventType.RESPONSE_WEB_SEARCH_CALL_SEARCHING]


    class azure.ai.extensions.openai.responses.ScreenshotParam(TypedDict, total=False):
        key "type": Required[Literal[screenshot]]
        type: Literal[ComputerActionType.SCREENSHOT]


    class azure.ai.extensions.openai.responses.ScrollParam(TypedDict, total=False):
        key "keys": Optional[list[str]]
        key "scroll_x": Required[int]
        key "scroll_y": Required[int]
        key "type": Required[Literal[scroll]]
        key "x": Required[int]
        key "y": Required[int]
        keys_property: list[str]
        scroll_x: int
        scroll_y: int
        type: Literal[ComputerActionType.SCROLL]
        x: int
        y: int


    class azure.ai.extensions.openai.responses.SharepointGroundingToolCall(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "arguments": Required[str]
        key "call_id": Required[str]
        key "id": Required[str]
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[sharepoint_grounding_preview_call]]
        agent_reference: AgentReference
        arguments: str
        call_id: str
        id: str
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.SHAREPOINT_GROUNDING_PREVIEW_CALL]


    class azure.ai.extensions.openai.responses.SharepointGroundingToolCallOutput(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "call_id": Required[str]
        key "id": Required[str]
        key "output": ForwardRef('ToolCallOutputContent', module='types')
        key "response_id": str
        key "status": Required[Literal["in_progress", "completed", "incomplete", "failed"]]
        key "type": Required[Literal[sharepoint_grounding_preview_call_output]]
        agent_reference: AgentReference
        call_id: str
        id: str
        output: ToolCallOutputContent
        response_id: str
        status: ToolCallStatus
        type: Literal[OutputItemType.SHAREPOINT_GROUNDING_PREVIEW_CALL_OUTPUT]


    class azure.ai.extensions.openai.responses.SharepointGroundingToolParameters(TypedDict, total=False):
        key "description": str
        key "name": str
        description: str
        name: str
        project_connections: list[ToolProjectConnection]


    class azure.ai.extensions.openai.responses.SharepointPreviewTool(TypedDict, total=False):
        key "description": str
        key "name": str
        key "sharepoint_grounding_preview": Required[SharepointGroundingToolParameters]
        key "type": Required[Literal[sharepoint_grounding_preview]]
        description: str
        name: str
        sharepoint_grounding_preview: SharepointGroundingToolParameters
        type: Literal[ToolType.SHAREPOINT_GROUNDING_PREVIEW]


    class azure.ai.extensions.openai.responses.SkillReferenceParam(TypedDict, total=False):
        key "skill_id": Required[str]
        key "type": Required[Literal[skill_reference]]
        key "version": str
        skill_id: str
        type: Literal[ContainerSkillType.SKILL_REFERENCE]
        version: str


    class azure.ai.extensions.openai.responses.SpecificApplyPatchParam(TypedDict, total=False):
        key "type": Required[Literal[apply_patch]]
        type: Literal[ToolChoiceParamType.APPLY_PATCH]


    class azure.ai.extensions.openai.responses.SpecificFunctionShellParam(TypedDict, total=False):
        key "type": Required[Literal[shell]]
        type: Literal[ToolChoiceParamType.SHELL]


    class azure.ai.extensions.openai.responses.StructuredOutputDefinition(TypedDict, total=False):
        key "description": Required[str]
        key "name": Required[str]
        key "schema": Required[dict[str, Any]]
        key "strict": Required[Optional[bool]]
        description: str
        name: str
        schema: dict[str, Any]
        strict: bool


    class azure.ai.extensions.openai.responses.StructuredOutputsOutputItem(TypedDict, total=False):
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "output": Required[Any]
        key "response_id": str
        key "type": Required[Literal[structured_outputs]]
        agent_reference: AgentReference
        id: str
        output: Any
        response_id: str
        type: Literal[OutputItemType.STRUCTURED_OUTPUTS]


    class azure.ai.extensions.openai.responses.SummaryTextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[summary_text]]
        text: str
        type: Literal[MessageContentType.SUMMARY_TEXT]


    class azure.ai.extensions.openai.responses.TextContent(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[text]]
        text: str
        type: Literal[MessageContentType.TEXT]


    class azure.ai.extensions.openai.responses.TextResponseFormatConfigurationResponseFormatJsonObject(TypedDict, total=False):
        key "type": Required[Literal[json_object]]
        type: Literal[TextResponseFormatConfigurationType.JSON_OBJECT]


    class azure.ai.extensions.openai.responses.TextResponseFormatConfigurationResponseFormatText(TypedDict, total=False):
        key "type": Required[Literal[text]]
        type: Literal[TextResponseFormatConfigurationType.TEXT]


    class azure.ai.extensions.openai.responses.TextResponseFormatConfigurationType(TypedDict):


    class azure.ai.extensions.openai.responses.TextResponseFormatJsonSchema(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        key "schema": Required[ResponseFormatJsonSchemaSchema]
        key "strict": Optional[bool]
        key "type": Required[Literal[json_schema]]
        description: str
        name: str
        schema: ResponseFormatJsonSchemaSchema
        strict: bool
        type: Literal[TextResponseFormatConfigurationType.JSON_SCHEMA]


    class azure.ai.extensions.openai.responses.ToolChoiceAllowed(TypedDict, total=False):
        key "mode": Required[Literal["auto", "required"]]
        key "tools": Required[list[dict[str, Any]]]
        key "type": Required[Literal[allowed_tools]]
        mode: Literal[auto, required]
        tools: list[dict[str, Any]]
        type: Literal[ToolChoiceParamType.ALLOWED_TOOLS]


    class azure.ai.extensions.openai.responses.ToolChoiceCodeInterpreter(TypedDict, total=False):
        key "type": Required[Literal[code_interpreter]]
        type: Literal[ToolChoiceParamType.CODE_INTERPRETER]


    class azure.ai.extensions.openai.responses.ToolChoiceComputer(TypedDict, total=False):
        key "type": Required[Literal[computer]]
        type: Literal[ToolChoiceParamType.COMPUTER]


    class azure.ai.extensions.openai.responses.ToolChoiceComputerUse(TypedDict, total=False):
        key "type": Required[Literal[computer_use]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE]


    class azure.ai.extensions.openai.responses.ToolChoiceComputerUsePreview(TypedDict, total=False):
        key "type": Required[Literal[computer_use_preview]]
        type: Literal[ToolChoiceParamType.COMPUTER_USE_PREVIEW]


    class azure.ai.extensions.openai.responses.ToolChoiceCustom(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[custom]]
        name: str
        type: Literal[ToolChoiceParamType.CUSTOM]


    class azure.ai.extensions.openai.responses.ToolChoiceFileSearch(TypedDict, total=False):
        key "type": Required[Literal[file_search]]
        type: Literal[ToolChoiceParamType.FILE_SEARCH]


    class azure.ai.extensions.openai.responses.ToolChoiceFunction(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal[function]]
        name: str
        type: Literal[ToolChoiceParamType.FUNCTION]


    class azure.ai.extensions.openai.responses.ToolChoiceImageGeneration(TypedDict, total=False):
        key "type": Required[Literal[image_generation]]
        type: Literal[ToolChoiceParamType.IMAGE_GENERATION]


    class azure.ai.extensions.openai.responses.ToolChoiceMCP(TypedDict, total=False):
        key "name": Optional[str]
        key "server_label": Required[str]
        key "type": Required[Literal[mcp]]
        name: str
        server_label: str
        type: Literal[ToolChoiceParamType.MCP]


    class azure.ai.extensions.openai.responses.ToolChoiceParamType(TypedDict):


    class azure.ai.extensions.openai.responses.ToolChoiceWebSearchPreview(TypedDict, total=False):
        key "type": Required[Literal[web_search_preview]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW]


    class azure.ai.extensions.openai.responses.ToolChoiceWebSearchPreview20250311(TypedDict, total=False):
        key "type": Required[Literal[web_search_preview2025_03_11]]
        type: Literal[ToolChoiceParamType.WEB_SEARCH_PREVIEW2025_03_11]


    class azure.ai.extensions.openai.responses.ToolProjectConnection(TypedDict, total=False):
        key "description": str
        key "name": str
        key "project_connection_id": Required[str]
        description: str
        name: str
        project_connection_id: str


    class azure.ai.extensions.openai.responses.ToolSearchCallItemParam(TypedDict, total=False):
        key "arguments": Required[EmptyModelParam]
        key "call_id": Optional[str]
        key "execution": Literal["server", "client"]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "type": Required[Literal[tool_search_call]]
        arguments: EmptyModelParam
        call_id: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallItemStatus
        type: Literal[ItemType.TOOL_SEARCH_CALL]


    class azure.ai.extensions.openai.responses.ToolSearchOutputItemParam(TypedDict, total=False):
        key "call_id": Optional[str]
        key "execution": Literal["server", "client"]
        key "id": Optional[str]
        key "status": Optional[Literal["in_progress", "completed", "incomplete"]]
        key "tools": Required[list[Tool]]
        key "type": Required[Literal[tool_search_output]]
        call_id: str
        execution: ToolSearchExecutionType
        id: str
        status: FunctionCallItemStatus
        tools: list[Tool]
        type: Literal[ItemType.TOOL_SEARCH_OUTPUT]


    class azure.ai.extensions.openai.responses.ToolSearchToolParam(TypedDict, total=False):
        key "description": Optional[str]
        key "execution": Literal["server", "client"]
        key "parameters": Optional[EmptyModelParam]
        key "type": Required[Literal[tool_search]]
        description: str
        execution: ToolSearchExecutionType
        parameters: EmptyModelParam
        type: Literal[ToolType.TOOL_SEARCH]


    class azure.ai.extensions.openai.responses.ToolType(TypedDict):


    class azure.ai.extensions.openai.responses.TopLogProb(TypedDict, total=False):
        key "bytes": Required[list[int]]
        key "logprob": Required[float]
        key "token": Required[str]
        bytes: list[int]
        logprob: float
        token: str


    class azure.ai.extensions.openai.responses.TypeParam(TypedDict, total=False):
        key "text": Required[str]
        key "type": Required[Literal[type]]
        text: str
        type: Literal[ComputerActionType.TYPE]


    class azure.ai.extensions.openai.responses.UrlCitationBody(TypedDict, total=False):
        key "end_index": Required[int]
        key "start_index": Required[int]
        key "title": Required[str]
        key "type": Required[Literal[url_citation]]
        key "url": Required[str]
        end_index: int
        start_index: int
        title: str
        type: Literal[AnnotationType.URL_CITATION]
        url: str


    class azure.ai.extensions.openai.responses.UserProfileMemoryItem(TypedDict, total=False):
        key "content": Required[str]
        key "kind": Required[Literal[user_profile]]
        key "memory_id": Required[str]
        key "scope": Required[str]
        key "updated_at": Required[int]
        content: str
        kind: Literal[MemoryItemKind.USER_PROFILE]
        memory_id: str
        scope: str
        updated_at: int


    class azure.ai.extensions.openai.responses.VectorStoreFileAttributes(TypedDict, total=False):


    class azure.ai.extensions.openai.responses.WaitParam(TypedDict, total=False):
        key "type": Required[Literal[wait]]
        type: Literal[ComputerActionType.WAIT]


    class azure.ai.extensions.openai.responses.WebSearchActionFind(TypedDict, total=False):
        key "pattern": Required[str]
        key "type": Required[Literal["find_in_page"]]
        key "url": Required[str]
        pattern: str
        type: Literal[find_in_page]
        url: str


    class azure.ai.extensions.openai.responses.WebSearchActionOpenPage(TypedDict, total=False):
        key "type": Required[Literal["open_page"]]
        key "url": Optional[str]
        type: Literal[open_page]
        url: str


    class azure.ai.extensions.openai.responses.WebSearchActionSearch(TypedDict, total=False):
        key "query": str
        key "type": Required[Literal["search"]]
        queries: list[str]
        query: str
        sources: list[WebSearchActionSearchSources]
        type: Literal[search]


    class azure.ai.extensions.openai.responses.WebSearchActionSearchSources(TypedDict, total=False):
        key "type": Required[Literal["url"]]
        key "url": Required[str]
        type: Literal[url]
        url: str


    class azure.ai.extensions.openai.responses.WebSearchApproximateLocation(TypedDict, total=False):
        key "city": Optional[str]
        key "country": Optional[str]
        key "region": Optional[str]
        key "timezone": Optional[str]
        key "type": Required[Literal["approximate"]]
        city: str
        country: str
        region: str
        timezone: str
        type: Literal[approximate]


    class azure.ai.extensions.openai.responses.WebSearchConfiguration(TypedDict, total=False):
        key "description": str
        key "instance_name": Required[str]
        key "name": str
        key "project_connection_id": Required[str]
        description: str
        instance_name: str
        name: str
        project_connection_id: str


    class azure.ai.extensions.openai.responses.WebSearchPreviewTool(TypedDict, total=False):
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[web_search_preview]]
        key "user_location": Optional[ApproximateLocation]
        search_content_types: list[Literal["text", "image"]]
        search_context_size: SearchContextSize
        type: Literal[ToolType.WEB_SEARCH_PREVIEW]
        user_location: ApproximateLocation


    class azure.ai.extensions.openai.responses.WebSearchTool(TypedDict, total=False):
        key "custom_search_configuration": ForwardRef('WebSearchConfiguration', module='types')
        key "description": str
        key "filters": Optional[WebSearchToolFilters]
        key "name": str
        key "search_context_size": Literal["low", "medium", "high"]
        key "type": Required[Literal[web_search]]
        key "user_location": Optional[WebSearchApproximateLocation]
        custom_search_configuration: WebSearchConfiguration
        description: str
        filters: WebSearchToolFilters
        name: str
        search_context_size: Literal[low, medium, high]
        type: Literal[ToolType.WEB_SEARCH]
        user_location: WebSearchApproximateLocation


    class azure.ai.extensions.openai.responses.WebSearchToolFilters(TypedDict, total=False):
        key "allowed_domains": Optional[list[str]]
        allowed_domains: list[str]


    class azure.ai.extensions.openai.responses.WorkIQPreviewTool(TypedDict, total=False):
        key "type": Required[Literal[work_iq_preview]]
        key "work_iq_preview": Required[WorkIQPreviewToolParameters]
        type: Literal[ToolType.WORK_IQ_PREVIEW]
        work_iq_preview: WorkIQPreviewToolParameters


    class azure.ai.extensions.openai.responses.WorkIQPreviewToolParameters(TypedDict, total=False):
        key "project_connection_id": Required[str]
        project_connection_id: str


    class azure.ai.extensions.openai.responses.WorkflowActionOutputItem(TypedDict, total=False):
        key "action_id": Required[str]
        key "agent_reference": ForwardRef('AgentReference', module='types')
        key "id": Required[str]
        key "kind": Required[str]
        key "parent_action_id": str
        key "previous_action_id": str
        key "response_id": str
        key "status": Required[Literal["completed", "failed", "in_progress", "cancelled"]]
        key "type": Required[Literal[workflow_action]]
        action_id: str
        agent_reference: AgentReference
        id: str
        kind: str
        parent_action_id: str
        previous_action_id: str
        response_id: str
        status: Literal[completed, failed, in_progress, cancelled]
        type: Literal[OutputItemType.WORKFLOW_ACTION]


```