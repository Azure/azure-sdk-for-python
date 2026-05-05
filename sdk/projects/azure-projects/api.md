```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.projects

    def azure.projects.deploy(deployment: AzureInfrastructure) -> None: ...


    def azure.projects.deprovision(
            deployment: Union[str, AzureInfrastructure, AzureApp], 
            /, 
            *, 
            purge: bool = False
        ) -> None: ...


    def azure.projects.export(
            deployment: AzureInfrastructure, 
            /, 
            infra_dir: str = "infra", 
            main_bicep: str = "main", 
            output_dir: str = ".", 
            user_access: bool = True, 
            location: Optional[str] = None, 
            parameters: Optional[Mapping[str, Any]] = None
        ) -> None: ...


    def azure.projects.field(
            *, 
            alias = ..., 
            default = MISSING, 
            default_factory = MISSING, 
            init = True, 
            repr = True, 
            **kwargs
        ): ...


    def azure.projects.provision(
            deployment: AzureInfrastructure, 
            /, 
            infra_dir: str = "infra", 
            main_bicep: str = "main", 
            output_dir: str = ".", 
            user_access: bool = True, 
            location: Optional[str] = None, 
            parameters: Optional[Mapping[str, Any]] = None
        ) -> Mapping[str, Any]: ...


    class azure.projects.AzureApp(Generic[InfrastructureType], metaclass=AzureAppComponent): implements ContextManager , AsyncContextManager 
        config_store: Mapping[str, Any] = {}

        def __delattr__(self, name): ...

        def __init__(self, **kwargs): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                name, 
                _
            ): ...

        @classmethod
        def load(
                cls, 
                attr_map: Optional[Mapping[str, str]] = None, 
                *, 
                config_store: Optional[Mapping[str, Any]] = ..., 
                **kwargs
            ) -> Self: ...

        @classmethod
        def provision(
                cls, 
                infra: Optional[InfrastructureType] = None, 
                *, 
                attr_map: Optional[Mapping[str, str]] = ..., 
                parameters: Optional[Mapping[str, Any]] = ..., 
                **kwargs
            ) -> Self: ...

        async def aclose(self) -> None: ...

        def close(self) -> None: ...


    class azure.projects.AzureInfrastructure(metaclass=AzureInfraComponent):
        config_store: Optional[ConfigStore[Any]]
        host: Optional[AppSite]
        identity: Optional[UserAssignedIdentity]
        resource_group: ResourceGroup

        def __delattr__(self, name): ...

        def __getattribute__(self, name): ...

        def __init__(self, **kwargs): ...

        def __repr__(self) -> str: ...

        def __setattr__(
                self, 
                name, 
                value
            ): ...

        def down(
                self, 
                *, 
                purge: bool = False
            ) -> None: ...


    class azure.projects.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.Resource:
        property resource: str    # Read-only
        property version: str    # Read-only
        DEFAULTS: MutableMapping[str, Any] = {}
        DEFAULT_EXTENSIONS: ExtensionResources = {}
        extensions: ExtensionResources
        identifier: ResourceIdentifiers
        parent: Optional[Resource]
        properties: Mapping[str, Any]

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[Mapping[str, Any]] = None, 
                /, 
                **kwargs
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Optional[Union[str, Parameter]] = ..., 
                parent: Optional[Resource] = ..., 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ..., 
                subscription: Optional[Union[str, Parameter]] = ...
            ) -> Self: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources

    class azure.projects.resources.ResourceIdentifiers(Enum):
        ai_chat_deployment = "ai:deployment:chat"
        ai_connection = "ai:connection"
        ai_deployment = "ai:deployment"
        ai_embeddings_deployment = "ai:deployment:embeddings"
        ai_hub = "ai:hub"
        ai_project = "ai:project"
        ai_services = "ai"
        app_service_plan = "appservice:plan"
        app_service_site = "appservice:site"
        app_service_site_config = "appservice:site:config"
        blob_container = "storage:blobs:container"
        blob_storage = "storage:blobs"
        cognitive_services = "cognitive_services"
        config_setting = "appconfig.setting"
        config_store = "appconfig"
        datalake_storage = "storage:datalake"
        file_share = "storage:files:share"
        file_storage = "storage:files"
        file_system = "storage:datalake:filesystem"
        keyvault = "keyvault"
        keyvault_key = "keyvault:key"
        keyvault_secret = "keyvault:secret"
        ml_workspace = "ml_workspace"
        queue = "storage:queues:queue"
        queue_storage = "storage:queues"
        resource_group = "resourcegroup"
        role_assignment = "roleassignment"
        search = "search"
        storage_account = "storage"
        system_topic = "events:systemtopic"
        system_topic_subscription = "events:systemtopic:subscription"
        table = "storage:tables:table"
        table_storage = "storage:tables"
        user_assigned_identity = "userassignedidentity"


namespace azure.projects.resources.ai

    class azure.projects.resources.ai.AIServices(CognitiveServicesAccount[CognitiveServicesAccountResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["CognitiveServices/accounts"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: CognitiveServicesAccountResource = {'name': '${defaultName}-aiservices', 'location': parameter(location), 'tags': var(azdTags), 'kind': 'AIServices', 'sku': {'name': 'S0'}, 'properties': {'publicNetworkAccess': 'Enabled', 'disableLocalAuth': True, 'customSubDomainName': '${defaultName}-aiservices', 'networkAcls': {'defaultAction': 'Allow'}}, 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Cognitive Services OpenAI Contributor', 'Cognitive Services Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services User'], 'user_roles': ['Cognitive Services OpenAI Contributor', 'Cognitive Services Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services User']}

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[CognitiveServicesAccountResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[AIServicesKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIServices[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.ai.deployment

    class azure.projects.resources.ai.deployment.AIChat(AIDeployment[AIDeploymentResourceType]):
        property api_version: str
        property audience: str
        property model_format: str
        property model_name: str
        property model_version: str
        property resource: Literal["CognitiveServices/accounts/deployments"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: DeploymentResource = {'name': parameter(aiChatModel=o1-mini), 'properties': {'model': {'name': parameter(aiChatModel=o1-mini), 'format': parameter(aiChatModelFormat=OpenAI), 'version': parameter(aiChatModelVersion=2024-09-12)}}, 'sku': {'name': parameter(aiChatModelSku=GlobalStandard), 'capacity': parameter(aiChatModelCapacity=1)}}
        DEFAULT_EXTENSIONS = {'managed_identity_roles': [], 'user_roles': []}

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[DeploymentResource] = None, 
                /, 
                account: Optional[Union[str, AIServices]] = None, 
                *, 
                deployment_name: Optional[Union[str, Parameter]] = ..., 
                **kwargs: Unpack[DeploymentKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Union[str, Parameter, AIServices[ResourceReference]], 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIChat[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> ChatCompletionsClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncChatCompletionsClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ChatClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ChatClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ChatClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ChatClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


    class azure.projects.resources.ai.deployment.AIDeployment(_ClientResource, Generic[AIDeploymentResourceType]):
        property api_version: str
        property audience: str
        property model_format: str
        property model_name: str
        property model_version: str
        property resource: Literal["CognitiveServices/accounts/deployments"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: DeploymentResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)})}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': [], 'user_roles': []}
        parent: AIServices
        properties: AIDeploymentResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[DeploymentResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                account: Optional[Union[str, Parameter, AIServices]] = None, 
                **kwargs: Unpack[DeploymentKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Union[str, Parameter, AIServices[ResourceReference]], 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIDeployment[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


    class azure.projects.resources.ai.deployment.AIEmbeddings(AIDeployment[AIDeploymentResourceType]):
        property api_version: str
        property audience: str
        property model_format: str
        property model_name: str
        property model_version: str
        property resource: Literal["CognitiveServices/accounts/deployments"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: DeploymentResource = {'name': '${defaultName}-embeddings-deployment', 'properties': {'model': {'name': parameter(aiEmbeddingsModel=text-embedding-ada-002), 'format': parameter(aiEmbeddingsModelFormat=OpenAI), 'version': parameter(aiEmbeddingsModelVersion=2)}}, 'sku': {'name': parameter(aiEmbeddingsModelSku=Standard), 'capacity': parameter(aiEmbeddingsModelCapacity=30)}}
        DEFAULT_EXTENSIONS = {'managed_identity_roles': [], 'user_roles': []}

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[DeploymentResource] = None, 
                /, 
                account: Optional[Union[str, AIServices]] = None, 
                *, 
                deployment_name: Optional[Union[str, Parameter]] = ..., 
                **kwargs: Unpack[DeploymentKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Union[str, Parameter, AIServices[ResourceReference]], 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIEmbeddings[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> EmbeddingsClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncEmbeddingsClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[EmbeddingsClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> EmbeddingsClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[EmbeddingsClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[EmbeddingsClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.ai.deployment.types

    class azure.projects.resources.ai.deployment.types.DeploymentCapacitySettings(TypedDict, total=False):
        key "designatedCapacity": Union[int, Parameter]
        key "priority": Union[int, Parameter]


    class azure.projects.resources.ai.deployment.types.DeploymentModel(TypedDict, total=False):
        key "format": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "publisher": Union[str, Parameter]
        key "source": Union[str, Parameter]
        key "sourceAccount": Union[str, Parameter]
        key "version": Union[str, Parameter]


    class azure.projects.resources.ai.deployment.types.DeploymentProperties(TypedDict, total=False):
        key "capacitySettings": Union[DeploymentCapacitySettings, Parameter]
        key "currentCapacity": Union[int, Parameter]
        key "model": Union[DeploymentModel, Parameter]
        key "parentDeploymentName": Union[str, Parameter]
        key "raiPolicyName": Union[str, Parameter]
        key "scaleSettings": Union[DeploymentScaleSettings, Parameter]
        key "versionUpgradeOption": Union[Parameter, Literal["NoAutoUpgrade", "OnceCurrentVersionExpired", "OnceNewDefaultVersionAvailable"]]


    class azure.projects.resources.ai.deployment.types.DeploymentResource(TypedDict, total=False):
        key "dependsOn": List[ResourceSymbol]
        key "name": Union[str, Parameter]
        key "parent": ResourceSymbol
        key "properties": ForwardRef('DeploymentProperties', module='types')
        key "sku": Union[DeploymentSku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.ai.deployment.types.DeploymentScaleSettings(TypedDict, total=False):
        key "capacity": Union[int, Parameter]
        key "scaleType": Union[Parameter, Literal["Manual", "Standard"]]


    class azure.projects.resources.ai.deployment.types.DeploymentSku(TypedDict, total=False):
        key "capacity": Union[int, Parameter]
        key "family": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "size": Union[str, Parameter]
        key "tier": Union[Parameter, Literal["Basic", "Enterprise", "Free", "Premium", "Standard"]]


    class azure.projects.resources.ai.deployment.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.ai.deployment.types.ResourceSymbol(Expression):
        property id: Output    # Read-only
        property name: Output    # Read-only
        property principal_id: Output    # Read-only
        property value: str    # Read-only

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                value: str, 
                *, 
                principal_id: bool = False
            ) -> None: ...

        def __ne__(self, value: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


namespace azure.projects.resources.ai.types

    class azure.projects.resources.ai.types.ApiProperties(TypedDict, total=False):
        key "aadClientId": Union[str, Parameter]
        key "aadTenantId": Union[str, Parameter]
        key "eventHubConnectionString": Union[str, Parameter]
        key "qnaAzureSearchEndpointId": Union[str, Parameter]
        key "qnaAzureSearchEndpointKey": Union[str, Parameter]
        key "qnaRuntimeEndpoint": Union[str, Parameter]
        key "statisticsEnabled": Union[bool, Parameter]
        key "storageAccountConnectionString": Union[str, Parameter]
        key "superUser": Union[str, Parameter]
        key "websiteName": Union[str, Parameter]


    class azure.projects.resources.ai.types.CognitiveServicesAccountProperties(TypedDict, total=False):
        key "allowedFqdnList": Union[List[Union[str, Parameter]], Parameter]
        key "amlWorkspace": Union[UserOwnedAmlWorkspace, Parameter]
        key "apiProperties": Union[ApiProperties, Parameter]
        key "customSubDomainName": Union[str, Parameter]
        key "disableLocalAuth": Union[bool, Parameter]
        key "dynamicThrottlingEnabled": Union[bool, Parameter]
        key "encryption": Union[CognitiveServicesEncryption, Parameter]
        key "locations": Union[MultiRegionSettings, Parameter]
        key "migrationToken": Union[str, Parameter]
        key "networkAcls": Union[CognitiveServicesNetworkRuleSet, Parameter]
        key "publicNetworkAccess": Union[Literal["Disabled", "Enabled"], Parameter]
        key "raiMonitorConfig": Union[RaiMonitorConfig, Parameter]
        key "restore": Union[bool, Parameter]
        key "restrictOutboundNetworkAccess": Union[bool, Parameter]
        key "userOwnedStorage": Union[List[Union[UserOwnedStorage, Parameter]], Parameter]


    class azure.projects.resources.ai.types.CognitiveServicesAccountResource(TypedDict, total=False):
        key "identity": ForwardRef('CognitiveServicesIdentity', module='types')
        key "kind": Union[Literal["AIServices", "AnomalyDetector", "CognitiveServices", "ComputerVision", "ContentModerator", "ContentSafety", "ConversationalLanguageUnderstanding", "Prediction", "Training", "Face", "FormRecognizer", "HealthInsights", "ImmersiveReader", "AllInOne", "LanguageAuthoring", "LUIS", "Authoring", "MetricsAdvisor", "OpenAI", "Personalizer", "v2", "SpeechServices", "TextAnalytics", "TextTranslation"], Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('CognitiveServicesAccountProperties', module='types')
        key "sku": Union[CognitiveServicesSku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.ai.types.CognitiveServicesEncryption(TypedDict, total=False):
        key "keySource": Union[Parameter, Literal["CognitiveServices", "KeyVault"]]
        key "keyVaultProperties": Union[Parameter, KeyVaultProperties]


    class azure.projects.resources.ai.types.CognitiveServicesIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


    class azure.projects.resources.ai.types.CognitiveServicesIpRule(TypedDict, total=False):
        key "value": Required[Union[str, Parameter]]


    class azure.projects.resources.ai.types.CognitiveServicesNetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[Parameter, Literal["AzureServices", "None"]]
        key "defaultAction": Union[Parameter, Literal["Allow", "Deny"]]
        key "ipRules": Union[Parameter, List[Union[CognitiveServicesIpRule, Parameter]]]
        key "virtualNetworkRules": Union[Parameter, List[Union[VirtualNetworkRule, Parameter]]]


    class azure.projects.resources.ai.types.CognitiveServicesSku(TypedDict, total=False):
        key "capacity": Union[int, Parameter]
        key "family": Union[str, Parameter]
        key "name": Required[Union[str, Parameter]]
        key "size": Union[str, Parameter]
        key "tier": Union[Parameter, Literal["Basic", "Enterprise", "Free", "Premium", "Standard"]]


    class azure.projects.resources.ai.types.KeyVaultProperties(TypedDict, total=False):
        key "identityClientId": Union[str, Parameter]
        key "keyName": Union[str, Parameter]
        key "keyVaultUri": Union[str, Parameter]
        key "keyVersion": Union[str, Parameter]


    class azure.projects.resources.ai.types.MultiRegionSettings(TypedDict, total=False):
        key "regions": Union[Parameter, List[Union[Parameter, RegionSetting]]]
        key "routingMethod": Union[Parameter, Literal["Performance", "Priority", "Weighted"]]


    class azure.projects.resources.ai.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.ai.types.RaiMonitorConfig(TypedDict, total=False):
        key "adxStorageResourceId": Union[str, Parameter]
        key "identityClientId": Union[str, Parameter]


    class azure.projects.resources.ai.types.RegionSetting(TypedDict, total=False):
        key "customsubdomain": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "value": Union[int, Parameter]


    class azure.projects.resources.ai.types.UserOwnedAmlWorkspace(TypedDict, total=False):
        key "identityClientId": Union[str, Parameter]
        key "resourceId": Union[str, Parameter]


    class azure.projects.resources.ai.types.UserOwnedStorage(TypedDict, total=False):
        key "identityClientId": Union[str, Parameter]
        key "resourceId": Union[str, Parameter]


    class azure.projects.resources.ai.types.VirtualNetworkRule(TypedDict, total=False):
        key "id": Required[Union[str, Parameter]]
        key "ignoreMissingVnetServiceEndpoint": Union[bool, Parameter]


namespace azure.projects.resources.appconfig

    class azure.projects.resources.appconfig.ConfigStore(_ClientResource, Generic[ConfigStoreResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["AppConfiguration/configurationStores"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: ConfigStoreResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'sku': {'name': 'Standard'}, 'properties': {'disableLocalAuth': True, 'createMode': 'Default', 'dataPlaneProxy': {'authenticationMode': 'Pass-through', 'privateLinkDelegation': 'Disabled'}, 'publicNetworkAccess': 'Enabled'}, 'location': parameter(location), 'tags': var(azdTags), 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['App Configuration Data Reader'], 'user_roles': ['App Configuration Data Owner']}
        parent: None
        properties: ConfigStoreResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[ConfigStoreResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[ConfigStoreKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> ConfigStore[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> AzureAppConfigurationClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncAzureAppConfigurationClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.appconfig.setting

    class azure.projects.resources.appconfig.setting.ConfigSetting(Resource, Generic[ConfigSettingResourceType]):
        property resource: Literal["AppConfiguration/configurationStores/keyValues"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: ConfigSettingResource = {}
        DEFAULT_EXTENSIONS: ExtensionResources = {}
        parent: ConfigStore
        properties: ConfigSettingResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[ConfigSettingResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                value: Optional[Union[str, Parameter]] = None, 
                store: Optional[Union[str, Parameter, ConfigStore]] = None, 
                **kwargs: Unpack[ConfigSettingKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ..., 
                store: Optional[Union[str, Parameter, ConfigStore[ResourceReference]]] = ...
            ) -> ConfigSetting[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.appconfig.setting.types

    class azure.projects.resources.appconfig.setting.types.ConfigSettingProperties(TypedDict, total=False):
        key "contentType": Union[str, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]
        key "value": Union[str, Parameter]


    class azure.projects.resources.appconfig.setting.types.ConfigSettingResource(TypedDict, total=False):
        key "name": Union[str, Parameter]
        key "parent": ResourceSymbol
        key "properties": ConfigSettingProperties


    class azure.projects.resources.appconfig.setting.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.appconfig.setting.types.ResourceSymbol(Expression):
        property id: Output    # Read-only
        property name: Output    # Read-only
        property principal_id: Output    # Read-only
        property value: str    # Read-only

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                value: str, 
                *, 
                principal_id: bool = False
            ) -> None: ...

        def __ne__(self, value: Any) -> bool: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


namespace azure.projects.resources.appconfig.types

    class azure.projects.resources.appconfig.types.ConfigStoreIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


    class azure.projects.resources.appconfig.types.ConfigStoreProperties(TypedDict, total=False):
        key "createMode": Union[Literal["Default", "Recover"], Parameter]
        key "dataPlaneProxy": Union[DataPlaneProxyProperties, Parameter]
        key "disableLocalAuth": Union[bool, Parameter]
        key "enablePurgeProtection": Union[bool, Parameter]
        key "encryption": Union[EncryptionProperties, Parameter]
        key "publicNetworkAccess": Union[Literal["Disabled", "Enabled"], Parameter]
        key "softDeleteRetentionInDays": Union[int, Parameter]


    class azure.projects.resources.appconfig.types.ConfigStoreResource(TypedDict, total=False):
        key "identity": Union[ConfigStoreIdentity, Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('ConfigStoreProperties', module='types')
        key "sku": Union[ConfigStoreSku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.appconfig.types.ConfigStoreSku(TypedDict, total=False):
        key "name": Union[Literal["Free", "Standard"], Parameter]


    class azure.projects.resources.appconfig.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


namespace azure.projects.resources.appservice

    class azure.projects.resources.appservice.AppServicePlan(Resource, Generic[AppServicePlanResourceType]):
        property resource: Literal["Web/serverfarms"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: AppServicePlanResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'location': parameter(location), 'tags': var(azdTags), 'kind': 'linux', 'properties': {'reserved': True}, 'sku': {'name': 'P1v3', 'capacity': 3}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': [], 'user_roles': []}
        parent: None
        properties: AppServicePlanResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[AppServicePlanResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[AppServicePlanKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AppServicePlan[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.appservice.site

    class azure.projects.resources.appservice.site.AppSite(Resource, Generic[AppSiteResourceType]):
        property resource: Literal["Web/sites"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: AppSiteResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'location': parameter(location), 'tags': {'azd-service-name': parameter(environmentName)}, 'kind': 'app,linux', 'properties': {'httpsOnly': True, 'clientAffinityEnabled': False, 'siteConfig': {'minTlsVersion': '1.2', 'use32BitWorkerProcess': False, 'alwaysOn': True, 'ftpsState': 'FtpsOnly', 'linuxFxVersion': 'python|3.12', 'cors': {'allowedOrigins': ['https://portal.azure.com', 'https://ms.portal.azure.com']}}}, 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': [], 'user_roles': []}
        parent: None
        properties: AppSiteResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[AppSiteResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                plan: Optional[Union[str, Parameter, AppServicePlan]] = None, 
                **kwargs: Unpack[AppSiteKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                plan: Union[str, Parameter, AppServicePlan[ResourceReference]], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AppSite[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.appservice.site.types

    class azure.projects.resources.appservice.site.types.AppSiteResource(TypedDict, total=False):
        key "extendedLocation": Union[ExtendedLocation, Parameter]
        key "identity": Union[SiteIdentity, Parameter]
        key "kind": Union[str, Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('AppSiteProperties', module='types')
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.appservice.site.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.appservice.site.types.SiteIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


namespace azure.projects.resources.appservice.types

    class azure.projects.resources.appservice.types.AppServicePlanResource(TypedDict, total=False):
        key "extendedLocation": Union[ExtendedLocation, Parameter]
        key "kind": Union[str, Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('AppServicePlanProperties', module='types')
        key "sku": Union[SkuDescription, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.appservice.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.appservice.types.SkuDescription(TypedDict, total=False):
        key "capabilities": Union[List[Union[Capability, Parameter]], Parameter]
        key "capacity": Union[int, Parameter]
        key "family": Union[str, Parameter]
        key "locations": Union[List[Union[str, Parameter]], Parameter]
        key "name": Union[str, Parameter]
        key "size": Union[str, Parameter]
        key "skuCapacity": Union[SkuCapacity, Parameter]
        key "tier": Union[str, Parameter]


namespace azure.projects.resources.foundry

    class azure.projects.resources.foundry.AIHub(MLWorkspace[MachineLearningWorkspaceResourceType]):
        property resource: Literal["MachineLearningServices/workspaces"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: MachineLearningWorkspaceResource = {'kind': 'Hub', 'name': '${defaultName}-hub', 'location': parameter(location), 'tags': var(azdTags), 'properties': {'primaryUserAssignedIdentity': parameter(managedIdentityId), 'publicNetworkAccess': 'Enabled', 'enableDataIsolation': True, 'v1LegacyMode': False, 'hbiWorkspace': False, 'managedNetwork': {'isolationMode': 'Disabled'}}, 'sku': {'name': 'Basic', 'tier': 'Basic'}, 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': [], 'user_roles': []}
        properties: MachineLearningWorkspaceResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[MachineLearningWorkspaceResource] = None, 
                /, 
                name: Optional[str] = None, 
                **kwargs: Unpack[MachineLearningWorkspaceKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIHub[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


    class azure.projects.resources.foundry.AIProject(MLWorkspace[MachineLearningWorkspaceResourceType]):
        property resource: Literal["MachineLearningServices/workspaces"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: MachineLearningWorkspaceResource = {'kind': 'Project', 'name': '${defaultName}-project', 'location': parameter(location), 'tags': var(azdTags), 'properties': {'primaryUserAssignedIdentity': parameter(managedIdentityId), 'publicNetworkAccess': 'Enabled', 'enableDataIsolation': True, 'v1LegacyMode': False, 'hbiWorkspace': False}, 'sku': {'name': 'Basic', 'tier': 'Basic'}, 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Contributor'], 'user_roles': ['Contributor']}
        properties: MachineLearningWorkspaceResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[MachineLearningWorkspaceResource] = None, 
                /, 
                name: Optional[str] = None, 
                **kwargs: Unpack[MachineLearningWorkspaceKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> AIProject[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> AIProjectClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncAIProjectClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.foundry.types

    class azure.projects.resources.foundry.types.MLIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


    class azure.projects.resources.foundry.types.MachineLearningWorkspaceResource(TypedDict, total=False):
        key "identity": Union[MLIdentity, Parameter]
        key "kind": Union[Literal["Default", "FeatureStore", "Hub", "Project"], Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('WorkspaceProperties', module='types')
        key "sku": Union[Sku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.foundry.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


namespace azure.projects.resources.keyvault

    class azure.projects.resources.keyvault.KeyVault(_ClientResource, Generic[KeyVaultResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["KeyVault/vaults"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: KeyVaultResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'properties': {'sku': {'family': 'A', 'name': 'standard'}, 'publicNetworkAccess': 'Enabled', 'tenantId': parameter(tenantId=subscription().tenantId), 'accessPolicies': [], 'enableRbacAuthorization': True}, 'location': parameter(location), 'tags': var(azdTags)}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Key Vault Administrator'], 'user_roles': ['Key Vault Administrator']}
        parent: None
        properties: KeyVaultResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[KeyVaultResource] = None, 
                /, 
                name: Optional[str] = None, 
                **kwargs: Unpack[KeyVaultKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> KeyVault[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.keyvault.types

    class azure.projects.resources.keyvault.types.KeyVaultIpRule(TypedDict, total=False):
        key "value": Required[Union[str, Parameter]]


    class azure.projects.resources.keyvault.types.KeyVaultNetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[Parameter, Literal["AzureServices", "None"]]
        key "defaultAction": Union[Parameter, Literal["Allow", "Deny"]]
        key "ipRules": Union[Parameter, List[Union[KeyVaultIpRule, Parameter]]]
        key "virtualNetworkRules": Union[Parameter, List[Union[VirtualNetworkRule, Parameter]]]


    class azure.projects.resources.keyvault.types.KeyVaultResource(TypedDict, total=False):
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('VaultProperties', module='types')
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.keyvault.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.keyvault.types.VirtualNetworkRule(TypedDict, total=False):
        key "id": Required[Union[str, Parameter]]
        key "ignoreMissingVnetServiceEndpoint": Union[bool, Parameter]


namespace azure.projects.resources.managedidentity

    class azure.projects.resources.managedidentity.UserAssignedIdentity(Resource, Generic[UserAssignedIdentityResourceType]):
        property resource: Literal["ManagedIdentity/userAssignedIdentities"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: UserAssignedIdentityResource = {'location': parameter(location), 'tags': var(azdTags), 'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)})}
        DEFAULT_EXTENSIONS = {}
        parent: None
        properties: UserAssignedIdentityResourceType

        def __bicep__(
                self, 
                fields, 
                *, 
                infra_component = ..., 
                parameters, 
                **kwargs
            ): ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[UserAssignedIdentityResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[UserAssignedIdentityKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> UserAssignedIdentity[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.managedidentity.types

    class azure.projects.resources.managedidentity.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.managedidentity.types.UserAssignedIdentityResource(TypedDict, total=False):
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


namespace azure.projects.resources.resourcegroup

    class azure.projects.resources.resourcegroup.ResourceGroup(Resource, Generic[ResourceGroupResourceType]):
        property resource: Literal["Resources/resourceGroups"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: ResourceGroupResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'location': parameter(location), 'tags': var(azdTags)}
        DEFAULT_EXTENSIONS = {}
        parent: None
        properties: ResourceGroupResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter], 
                **kwargs
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[ResourceGroupResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[ResourceGroupKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                subscription: Optional[Union[str, Parameter]] = ...
            ) -> ResourceGroup[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.resourcegroup.types

    class azure.projects.resources.resourcegroup.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.resourcegroup.types.ResourceGroupResource(TypedDict, total=False):
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


namespace azure.projects.resources.search

    class azure.projects.resources.search.SearchService(_ClientResource, Generic[SearchServiceResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["Search/searchServices"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: SearchServiceResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'sku': {'name': 'basic'}, 'properties': {'publicNetworkAccess': 'Disabled'}, 'location': parameter(location), 'tags': var(azdTags), 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Search Index Data Contributor', 'Search Index Data Reader', 'Search Service Contributor'], 'user_roles': ['Search Index Data Contributor', 'Search Index Data Reader', 'Search Service Contributor']}
        parent: None
        properties: SearchServiceResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[SearchServiceResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[SearchServiceKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> SearchService[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> SearchIndexClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncSearchIndexClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.search.types

    class azure.projects.resources.search.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.search.types.SearchIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


    class azure.projects.resources.search.types.SearchIpRule(TypedDict, total=False):
        key "value": Required[Union[str, Parameter]]


    class azure.projects.resources.search.types.SearchNetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[Parameter, Literal["AzurePortal", "AzureServices", "None"]]
        key "ipRules": Union[Parameter, List[Union[SearchIpRule, Parameter]]]


    class azure.projects.resources.search.types.SearchServiceResource(TypedDict, total=False):
        key "identity": Union[SearchIdentity, Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": ForwardRef('SearchServiceProperties', module='types')
        key "sku": Union[SearchSku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.search.types.SearchSku(TypedDict, total=False):
        key "name": Union[Literal["basic", "free", "standard", "standard2", "standard3", "storage_optimized_l1", "storage_optimized_l2"], Parameter]


namespace azure.projects.resources.storage

    class azure.projects.resources.storage.StorageAccount(Resource, Generic[StorageAccountResourceType]):
        property resource: Literal["Storage/storageAccounts"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: StorageAccountResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}), 'location': parameter(location), 'tags': var(azdTags), 'kind': 'StorageV2', 'sku': {'name': 'Standard_GRS'}, 'properties': {'accessTier': 'Hot', 'allowCrossTenantReplication': False, 'allowSharedKeyAccess': False}, 'identity': {'type': 'UserAssigned', 'userAssignedIdentities': {parameter(managedIdentityId): {}}}}
        DEFAULT_EXTENSIONS = {}
        parent: None
        properties: StorageAccountResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[StorageAccountResource] = None, 
                /, 
                name: Optional[Union[str, Parameter]] = None, 
                **kwargs: Unpack[StorageAccountKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> StorageAccount[ResourceReference]: ...

        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                **kwargs
            ) -> ClientType: ...


namespace azure.projects.resources.storage.blobs

    class azure.projects.resources.storage.blobs.BlobStorage(_ClientResource, Generic[BlobServiceResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["Storage/storageAccounts/blobServices"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: BlobServiceResource = {'name': 'default'}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Storage Blob Data Contributor'], 'user_roles': ['Storage Blob Data Contributor']}
        parent: StorageAccount
        properties: BlobServiceResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[BlobServiceResource] = None, 
                /, 
                account: Optional[Union[str, Parameter, ComponentField, StorageAccount]] = None, 
                **kwargs: Unpack[BlobStorageKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Union[str, Parameter, StorageAccount[ResourceReference]], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> BlobStorage[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> BlobServiceClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncBlobServiceClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.storage.blobs.container

    class azure.projects.resources.storage.blobs.container.BlobContainer(_ClientResource, Generic[ContainerResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["Storage/storageAccounts/blobServices/containers"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: ContainerResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)})}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Storage Blob Data Contributor'], 'user_roles': ['Storage Blob Data Contributor']}
        parent: BlobStorage
        properties: ContainerResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[ContainerResource] = None, 
                /, 
                name: Optional[str] = None, 
                account: Optional[Union[str, Parameter, BlobStorage]] = None, 
                **kwargs: Unpack[ContainerKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Optional[Union[str, Parameter, BlobStorage[ResourceReference]]] = ..., 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> BlobContainer[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> ContainerClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncContainerClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.storage.blobs.container.types

    class azure.projects.resources.storage.blobs.container.types.ContainerProperties(TypedDict, total=False):
        key "defaultEncryptionScope": Union[str, Parameter]
        key "denyEncryptionScopeOverride": Union[bool, Parameter]
        key "enableNfsV3AllSquash": Union[bool, Parameter]
        key "enableNfsV3RootSquash": Union[bool, Parameter]
        key "immutabilityPolicyName": Union[bool, Parameter]
        key "immutableStorageWithVersioning": Union[ImmutableStorageWithVersioning, Parameter]
        key "metadata": Dict[str, str]
        key "publicAccess": Union[Literal["Blob", "Container", "None"], Parameter]


    class azure.projects.resources.storage.blobs.container.types.ContainerResource(TypedDict, total=False):
        key "name": Union[str, Parameter]
        key "properties": ContainerProperties


    class azure.projects.resources.storage.blobs.container.types.ImmutableStorageWithVersioning(TypedDict, total=False):
        key "enabled": Union[bool, Parameter]


    class azure.projects.resources.storage.blobs.container.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


namespace azure.projects.resources.storage.blobs.types

    class azure.projects.resources.storage.blobs.types.BlobServiceProperties(TypedDict, total=False):
        key "automaticSnapshotPolicyEnabled": Union[bool, Parameter]
        key "changeFeed": Union[ChangeFeed, Parameter]
        key "containerDeleteRetentionPolicy": Union[DeleteRetentionPolicy, Parameter]
        key "cors": Union[BlobsCorsRules, Parameter]
        key "defaultServiceVersion": Union[str, Parameter]
        key "deleteRetentionPolicy": Union[DeleteRetentionPolicy, Parameter]
        key "isVersioningEnabled": Union[bool, Parameter]
        key "lastAccessTimeTrackingPolicy": Union[LastAccessTimeTrackingPolicy, Parameter]
        key "restorePolicy": Union[RestorePolicyProperties, Parameter]


    class azure.projects.resources.storage.blobs.types.BlobServiceResource(TypedDict, total=False):
        key "name": Union[Literal["default"], Parameter]
        key "properties": BlobServiceProperties


    class azure.projects.resources.storage.blobs.types.BlobsCorsRule(TypedDict, total=False):
        key "allowedHeaders": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "allowedMethods": Required[Union[Parameter, List[Union[Literal["CONNECT", "DELETE", "GET", "HEAD", "MERGE", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"], Parameter]]]]
        key "allowedOrigins": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "exposedHeaders": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "maxAgeInSeconds": Required[Union[int, Parameter]]


    class azure.projects.resources.storage.blobs.types.BlobsCorsRules(TypedDict, total=False):
        key "corsRules": Union[Parameter, List[Union[BlobsCorsRule, Parameter]]]


    class azure.projects.resources.storage.blobs.types.ChangeFeed(TypedDict, total=False):
        key "enabled": Union[bool, Parameter]
        key "retentionInDays": Union[int, Parameter]


    class azure.projects.resources.storage.blobs.types.DeleteRetentionPolicy(TypedDict, total=False):
        key "allowPermanentDelete": Union[bool, Parameter]
        key "days": Union[int, Parameter]
        key "enabled": Union[bool, Parameter]


    class azure.projects.resources.storage.blobs.types.LastAccessTimeTrackingPolicy(TypedDict, total=False):
        key "enable": Required[Union[bool, Parameter]]


    class azure.projects.resources.storage.blobs.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.storage.blobs.types.RestorePolicyProperties(TypedDict, total=False):
        key "days": Union[int, Parameter]
        key "enabled": Required[Union[bool, Parameter]]


namespace azure.projects.resources.storage.tables

    class azure.projects.resources.storage.tables.TableStorage(_ClientResource, Generic[TableServiceResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["Storage/storageAccounts/tableServices"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: TableServiceResource = {'name': 'default'}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Storage Table Data Contributor'], 'user_roles': ['Storage Table Data Contributor']}
        parent: StorageAccount
        properties: TableServiceResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[TableServiceResource] = None, 
                /, 
                account: Optional[Union[str, StorageAccount, Parameter]] = None, 
                **kwargs: Unpack[TableStorageKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Union[str, Parameter, StorageAccount[ResourceReference]], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> TableStorage[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> TableServiceClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncTableServiceClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Optional[Union[SupportsTokenInfo, AsyncSupportsTokenInfo]] = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.storage.tables.table

    class azure.projects.resources.storage.tables.table.Table(_ClientResource, Generic[TableResourceType]):
        property api_version: str
        property audience: str
        property resource: Literal["Storage/storageAccounts/tableServices/tables"]    # Read-only
        property version: str    # Read-only
        DEFAULTS: TableResource = {'name': parameter(defaultName=${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)})}
        DEFAULT_EXTENSIONS: ExtensionResources = {'managed_identity_roles': ['Storage Blob Data Contributor'], 'user_roles': ['Storage Blob Data Contributor']}
        parent: TableStorage
        properties: TableResourceType

        def __bicep__(
                self, 
                fields: FieldsType, 
                *, 
                attrname: Optional[str] = ..., 
                depends_on: Optional[List[ResourceSymbol]] = ..., 
                infra_component: Optional[AzureInfrastructure] = ..., 
                parameters: Dict[str, Parameter]
            ) -> Tuple[ResourceSymbol, ]: ...

        def __eq__(self, value: Any) -> bool: ...

        def __init__(
                self, 
                properties: Optional[TableResource] = None, 
                /, 
                name: Optional[str] = None, 
                account: Optional[Union[str, Parameter, TableStorage]] = None, 
                **kwargs: Unpack[TableKwargs]
            ) -> None: ...

        def __repr__(self) -> str: ...

        @classmethod
        def reference(
                cls, 
                *, 
                account: Optional[Union[str, Parameter, TableStorage[ResourceReference]]] = ..., 
                name: Union[str, Parameter], 
                resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = ...
            ) -> Table[ResourceReference]: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Optional[Literal[False]] = ..., 
                **client_options
            ) -> TableClient: ...

        @overload
        def get_client(
                self, 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                transport: Any = ..., 
                use_async: Literal[True], 
                **client_options
            ) -> AsyncTableClient: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[False] = False, 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> ClientType: ...

        @overload
        def get_client(
                self, 
                cls: Type[ClientType], 
                /, 
                *, 
                api_version: Optional[str] = ..., 
                audience: Optional[str] = ..., 
                config_store: Optional[Mapping[str, Any]] = ..., 
                credential: Any = ..., 
                return_credential: Literal[True], 
                transport: Any = ..., 
                use_async: Optional[bool] = ..., 
                **client_options
            ) -> Tuple[ClientType, Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]: ...


namespace azure.projects.resources.storage.tables.table.types

    class azure.projects.resources.storage.tables.table.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.storage.tables.table.types.TableAccessPolicy(TypedDict, total=False):
        key "expiryTime": Union[str, Parameter]
        key "permission": Required[Union[str, Parameter]]
        key "startTime": Union[str, Parameter]


    class azure.projects.resources.storage.tables.table.types.TableProperties(TypedDict, total=False):
        key "signedIdentifiers": Union[List[Union[TableSignedIdentifier, Parameter]], Parameter]


    class azure.projects.resources.storage.tables.table.types.TableResource(TypedDict, total=False):
        key "name": Union[str, Parameter]
        key "properties": TableProperties


    class azure.projects.resources.storage.tables.table.types.TableSignedIdentifier(TypedDict, total=False):
        key "accessPolicy": Union[TableAccessPolicy, Parameter]
        key "id": Required[Union[str, Parameter]]


namespace azure.projects.resources.storage.tables.types

    class azure.projects.resources.storage.tables.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.storage.tables.types.TableServiceProperties(TypedDict, total=False):
        key "cors": Union[TablesCorsRules, Parameter]


    class azure.projects.resources.storage.tables.types.TableServiceResource(TypedDict, total=False):
        key "name": Union[Literal["default"], Parameter]
        key "properties": TableServiceProperties


    class azure.projects.resources.storage.tables.types.TablesCorsRule(TypedDict, total=False):
        key "allowedHeaders": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "allowedMethods": Required[Union[Parameter, List[Union[Literal["CONNECT", "DELETE", "GET", "HEAD", "MERGE", "OPTIONS", "PATCH", "POST", "PUT", "TRACE"], Parameter]]]]
        key "allowedOrigins": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "exposedHeaders": Required[Union[Parameter, List[Union[str, Parameter]]]]
        key "maxAgeInSeconds": Required[Union[int, Parameter]]


    class azure.projects.resources.storage.tables.types.TablesCorsRules(TypedDict, total=False):
        key "corsRules": Union[Parameter, List[Union[TablesCorsRule, Parameter]]]


namespace azure.projects.resources.storage.types

    class azure.projects.resources.storage.types.AccountImmutabilityPolicyProperties(TypedDict, total=False):
        key "allowProtectedAppendWrites": Union[bool, Parameter]
        key "immutabilityPeriodSinceCreationInDays": Union[int, Parameter]
        key "state": Union[Literal["Disabled", "Locked", "Unlocked"], Parameter]


    class azure.projects.resources.storage.types.ActiveDirectoryProperties(TypedDict, total=False):
        key "accountType": Union[Literal["Computer", "User"], Parameter]
        key "azureStorageSid": Union[str, Parameter]
        key "domainGuid": Required[Union[str, Parameter]]
        key "domainName": Required[Union[str, Parameter]]
        key "domainSid": Union[str, Parameter]
        key "forestName": Union[str, Parameter]
        key "netBiosDomainName": Union[str, Parameter]
        key "samAccountName": Union[str, Parameter]


    class azure.projects.resources.storage.types.AzureFilesIdentityBasedAuthentication(TypedDict, total=False):
        key "activeDirectoryProperties": Union[ActiveDirectoryProperties, Parameter]
        key "defaultSharePermission": Union[Literal["None", "StorageFileDataSmbShareContributor", "StorageFileDataSmbShareElevatedContributor", "StorageFileDataSmbShareReader"], Parameter]
        key "directoryServiceOptions": Required[Union[Literal["AADDS", "AADKERB", "AD", "None"], Parameter]]


    class azure.projects.resources.storage.types.CustomDomain(TypedDict, total=False):
        key "name": Required[Union[str, Parameter]]
        key "useSubDomainName": Union[bool, Parameter]


    class azure.projects.resources.storage.types.EncryptionIdentity(TypedDict, total=False):
        key "federatedIdentityClientId": Union[str, Parameter]
        key "userAssignedIdentity": Union[str, Parameter]


    class azure.projects.resources.storage.types.EncryptionService(TypedDict, total=False):
        key "enabled": Union[bool, Parameter]
        key "keyType": Union[Literal["Account", "Service"], Parameter]


    class azure.projects.resources.storage.types.EncryptionServices(TypedDict, total=False):
        key "blob": Union[EncryptionService, Parameter]
        key "file": Union[EncryptionService, Parameter]
        key "queue": Union[EncryptionService, Parameter]
        key "table": Union[EncryptionService, Parameter]


    class azure.projects.resources.storage.types.ExtendedLocation(TypedDict):
        key "name": Union[str, Parameter]
        key "type": Required[Union[Literal["EdgeZone"], Parameter]]


    class azure.projects.resources.storage.types.IPRule(TypedDict):
        key "action": Union[Literal["Allow"], Parameter]
        key "value": Required[Union[str, Parameter]]


    class azure.projects.resources.storage.types.ImmutableStorageAccount(TypedDict, total=False):
        key "enabled": Union[bool, Parameter]
        key "immutabilityPolicy": Union[AccountImmutabilityPolicyProperties, Parameter]


    class azure.projects.resources.storage.types.KeyPolicy(TypedDict):
        key "keyExpirationPeriodInDays": Required[Union[int, Parameter]]


    class azure.projects.resources.storage.types.KeyVaultProperties(TypedDict, total=False):
        key "keyname": Union[str, Parameter]
        key "keyvaulturi": Union[str, Parameter]
        key "keyversion": Union[str, Parameter]


    class azure.projects.resources.storage.types.Parameter(Expression):
        property name: str    # Read-only
        property type: str    # Read-only
        property value: str    # Read-only
        default: Any
        env_var: Optional[str]

        def __bicep__(
                self, 
                default: Any = MISSING, 
                /, 
            ) -> str: ...

        def __eq__(self, value: Any) -> bool: ...

        def __hash__(self): ...

        def __init__(
                self, 
                name: str, 
                *, 
                allowed: Optional[List[int]] = ..., 
                default: Any = MISSING, 
                description: Optional[str] = ..., 
                env_var: Optional[str] = ..., 
                max_length: Optional[int] = ..., 
                max_value: Optional[int] = ..., 
                min_length: Optional[int] = ..., 
                min_value: Optional[int] = ..., 
                secure: bool = False, 
                type: Optional[Literal[string, int, boolean, array, object]] = ...
            ): ...

        def __ne__(self, value: Any) -> bool: ...

        def __obj__(self) -> Dict[str, Dict[str, str]]: ...

        def __repr__(self) -> str: ...

        def format(
                self, 
                format_str: Optional[str] = None, 
                /, 
            ) -> str: ...


    class azure.projects.resources.storage.types.ResourceAccessRule(TypedDict):
        key "resourceId": Required[Union[str, Parameter]]
        key "tenantId": Required[Union[str, Parameter]]


    class azure.projects.resources.storage.types.RoutingPreference(TypedDict, total=False):
        key "publishInternetEndpoints": Union[bool, Parameter]
        key "publishMicrosoftEndpoints": Union[bool, Parameter]
        key "routingChoice": Union[Literal["InternetRouting", "MicrosoftRouting"], Parameter]


    class azure.projects.resources.storage.types.SasPolicy(TypedDict):
        key "expirationAction": Required[Union[Literal["Block", "Log"], Parameter]]
        key "sasExpirationPeriod": Required[Union[str, Parameter]]


    class azure.projects.resources.storage.types.StorageAccountProperties(TypedDict, total=False):
        key "accessTier": Union[Literal["Hot", "Cold", "Cool", "Premium"], Parameter]
        key "allowBlobPublicAccess": Union[bool, Parameter]
        key "allowCrossTenantReplication": Union[bool, Parameter]
        key "allowSharedKeyAccess": Union[bool, Parameter]
        key "allowedCopyScope": Union[Literal["AAD", "PrivateLink"], Parameter]
        key "azureFilesIdentityBasedAuthentication": Union[AzureFilesIdentityBasedAuthentication, Parameter]
        key "customDomain": Union[CustomDomain, Parameter]
        key "defaultToOAuthAuthentication": Union[bool, Parameter]
        key "dnsEndpointType": Union[Literal["AzureDnsZone", "Standard"], Parameter]
        key "enableExtendedGroups": Union[bool, Parameter]
        key "encryption": Union[StorageEncryption, Parameter]
        key "immutableStorageWithVersioning": Union[ImmutableStorageAccount, Parameter]
        key "isHnsEnabled": Union[bool, Parameter]
        key "isLocalUserEnabled": Union[bool, Parameter]
        key "isNfsV3Enabled": Union[bool, Parameter]
        key "isSftpEnabled": Union[bool, Parameter]
        key "keyPolicy": Union[KeyPolicy, Parameter]
        key "largeFileSharesState": Union[Literal["Disabled", "Enabled"], Parameter]
        key "minimumTlsVersion": Union[Literal["TLS1_0", "TLS1_1", "TLS1_2", "TLS1_3"], Parameter]
        key "networkAcls": Union[StorageNetworkRuleSet, Parameter]
        key "publicNetworkAccess": Union[Literal["Disabled", "Enabled", "SecuredByPerimeter"], Parameter]
        key "routingPreference": Union[RoutingPreference, Parameter]
        key "sasPolicy": Union[SasPolicy, Parameter]
        key "supportsHttpsTrafficOnly": Union[bool, Parameter]


    class azure.projects.resources.storage.types.StorageAccountResource(TypedDict, total=False):
        key "extendedLocation": Union[ExtendedLocation, Parameter]
        key "identity": Union[StorageIdentity, Parameter]
        key "kind": Union[Literal["BlobStorage", "BlockBlobStorage", "FileStorage", "Storage", "StorageV2"], Parameter]
        key "location": Union[str, Parameter]
        key "name": Union[str, Parameter]
        key "properties": StorageAccountProperties
        key "sku": Union[StorageSku, Parameter]
        key "tags": Union[Dict[str, Union[str, Parameter]], Parameter]


    class azure.projects.resources.storage.types.StorageEncryption(TypedDict, total=False):
        key "identity": Union[EncryptionIdentity, Parameter]
        key "keySource": Union[Literal["Keyvault", "Storage"], Parameter]
        key "keyvaultProperties": Union[KeyVaultProperties, Parameter]
        key "requireInfrastructureEncryption": Union[bool, Parameter]
        key "services": Union[EncryptionServices, Parameter]


    class azure.projects.resources.storage.types.StorageIdentity(TypedDict, total=False):
        key "type": Required[Union[Literal["None", "SystemAssigned", "SystemAssigned,UserAssigned", "UserAssigned"], Parameter]]
        key "userAssignedIdentities": Dict[Union[str, Parameter], Dict]


    class azure.projects.resources.storage.types.StorageNetworkRuleSet(TypedDict, total=False):
        key "bypass": Literal["AzureServices", "Logging", "Metrics", "None"]
        key "defaultAction": Required[Union[Literal["Allow", "Deny"], Parameter]]
        key "ipRules": List[Union[IPRule, Parameter]]
        key "resourceAccessRules": List[Union[ResourceAccessRule, Parameter]]
        key "virtualNetworkRules": List[Union[VirtualNetworkRule, Parameter]]


    class azure.projects.resources.storage.types.StorageSku(TypedDict, total=False):
        key "name": Required[Union[Literal["Premium_LRS", "Premium_ZRS", "Standard_GRS", "Standard_GZRS", "Standard_LRS", "Standard_RAGRS", "Standard_RAGZRS", "Standard_ZRS"], Parameter]]


    class azure.projects.resources.storage.types.VirtualNetworkRule(TypedDict):
        key "action": Required[Union[Literal["Allow"], Parameter]]
        key "id": Required[Union[str, Parameter]]


```