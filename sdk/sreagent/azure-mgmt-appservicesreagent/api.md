```py
namespace azure.mgmt.appservicesreagent

    class azure.mgmt.appservicesreagent.AppClient: implements ContextManager 
        agent_spaces: AgentSpacesOperations
        agent_spaces_connectors: AgentSpacesConnectorsOperations
        agents: AgentsOperations
        agents_connectors: AgentsConnectorsOperations
        supported_agent_models: SupportedAgentModelsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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


namespace azure.mgmt.appservicesreagent.aio

    class azure.mgmt.appservicesreagent.aio.AppClient: implements AsyncContextManager 
        agent_spaces: AgentSpacesOperations
        agent_spaces_connectors: AgentSpacesConnectorsOperations
        agents: AgentsOperations
        agents_connectors: AgentsConnectorsOperations
        supported_agent_models: SupportedAgentModelsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                polling_interval: Optional[int] = ..., 
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


namespace azure.mgmt.appservicesreagent.aio.operations

    class azure.mgmt.appservicesreagent.aio.operations.AgentSpacesConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: AgentSpaceConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpaceConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: AgentSpaceConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpaceConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpaceConnector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnector: ...

        @distributed_trace_async
        async def list_all_secrets(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnectorCollection: ...

        @distributed_trace
        def list_by_agent_space(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentSpaceConnector]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnector: ...


    class azure.mgmt.appservicesreagent.aio.operations.AgentSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: AgentSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: AgentSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: AgentSpacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: AgentSpacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentSpace]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AgentSpace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentSpace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AgentSpace]: ...


    class azure.mgmt.appservicesreagent.aio.operations.AgentsConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: AgentConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: AgentConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentConnector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentConnector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentConnector: ...

        @distributed_trace
        def list_by_agent(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentConnector]: ...

        @distributed_trace_async
        async def list_secrets(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentConnector: ...

        @distributed_trace_async
        async def list_with_secrets_by_agent(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentConnectorCollection: ...


    class azure.mgmt.appservicesreagent.aio.operations.AgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: AgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: AgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Agent]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Agent]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Agent]: ...


    class azure.mgmt.appservicesreagent.aio.operations.SupportedAgentModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SupportedAgentModel]: ...


namespace azure.mgmt.appservicesreagent.models

    class azure.mgmt.appservicesreagent.models.ActionConfiguration(_Model):
        access_level: Optional[Union[str, AgentAccessLevel]]
        identity: Optional[str]
        mode: Optional[Union[str, AgentMode]]

        @overload
        def __init__(
                self, 
                *, 
                access_level: Optional[Union[str, AgentAccessLevel]] = ..., 
                identity: Optional[str] = ..., 
                mode: Optional[Union[str, AgentMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.Agent(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AgentProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AgentProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentAccessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"


    class azure.mgmt.appservicesreagent.models.AgentConnector(ProxyResource):
        id: str
        name: str
        properties: Optional[AgentConnectorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentConnectorCollection(_Model):
        next_link: Optional[str]
        value: list[AgentConnector]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[AgentConnector]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentConnectorProperties(_Model):
        data_connector_type: Optional[str]
        data_source: Optional[str]
        deployment_error: Optional[str]
        endpoint: Optional[str]
        extended_properties: Optional[dict[str, Any]]
        identity: Optional[str]
        provisioning_state: Optional[Union[str, ConnectorProvisioningState]]
        source: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_connector_type: Optional[str] = ..., 
                data_source: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                extended_properties: Optional[dict[str, Any]] = ..., 
                identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentIdentity(_Model):
        client_id: Optional[str]
        enabled: Optional[bool]
        initial_sponsor_group_id: str

        @overload
        def __init__(
                self, 
                *, 
                initial_sponsor_group_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentIdentityPatch(_Model):
        initial_sponsor_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initial_sponsor_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTONOMOUS = "Autonomous"
        READ_ONLY = "ReadOnly"
        REVIEW = "Review"


    class azure.mgmt.appservicesreagent.models.AgentPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AgentPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AgentPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentPatchProperties(_Model):
        action_configuration: Optional[ActionConfiguration]
        agent_identity: Optional[AgentIdentityPatch]
        agent_space_id: Optional[str]
        default_model: Optional[DefaultModel]
        incident_management_configuration: Optional[IncidentManagementConfiguration]
        knowledge_graph_configuration: Optional[KnowledgeGraphConfiguration]
        log_configuration: Optional[LogConfiguration]
        upgrade_channel: Optional[Union[str, UpgradeChannel]]

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[ActionConfiguration] = ..., 
                agent_identity: Optional[AgentIdentityPatch] = ..., 
                agent_space_id: Optional[str] = ..., 
                default_model: Optional[DefaultModel] = ..., 
                incident_management_configuration: Optional[IncidentManagementConfiguration] = ..., 
                knowledge_graph_configuration: Optional[KnowledgeGraphConfiguration] = ..., 
                log_configuration: Optional[LogConfiguration] = ..., 
                upgrade_channel: Optional[Union[str, UpgradeChannel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentPowerState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RUNNING = "Running"
        STOPPED = "Stopped"


    class azure.mgmt.appservicesreagent.models.AgentProperties(_Model):
        action_configuration: Optional[ActionConfiguration]
        agent_endpoint: Optional[str]
        agent_identity: Optional[AgentIdentity]
        agent_space_id: Optional[str]
        default_model: Optional[DefaultModel]
        incident_management_configuration: Optional[IncidentManagementConfiguration]
        knowledge_graph_configuration: Optional[KnowledgeGraphConfiguration]
        log_configuration: Optional[LogConfiguration]
        power_state: Optional[Union[str, AgentPowerState]]
        provisioning_state: Optional[Union[str, AgentProvisioningState]]
        running_state: Optional[str]
        upgrade_channel: Optional[Union[str, UpgradeChannel]]

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[ActionConfiguration] = ..., 
                agent_identity: Optional[AgentIdentity] = ..., 
                agent_space_id: Optional[str] = ..., 
                default_model: Optional[DefaultModel] = ..., 
                incident_management_configuration: Optional[IncidentManagementConfiguration] = ..., 
                knowledge_graph_configuration: Optional[KnowledgeGraphConfiguration] = ..., 
                log_configuration: Optional[LogConfiguration] = ..., 
                upgrade_channel: Optional[Union[str, UpgradeChannel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appservicesreagent.models.AgentSpace(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AgentSpaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AgentSpaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpaceComplianceStatus(_Model):
        compliance_issues: Optional[list[str]]
        is_compliant: bool
        last_compliance_check: Optional[datetime]


    class azure.mgmt.appservicesreagent.models.AgentSpaceConnector(ProxyResource):
        id: str
        name: str
        properties: Optional[AgentSpaceConnectorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AgentSpaceConnectorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpaceConnectorCollection(_Model):
        next_link: Optional[str]
        value: list[AgentSpaceConnector]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[AgentSpaceConnector]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpaceConnectorProperties(_Model):
        data_connector_type: Optional[str]
        data_source: Optional[str]
        deployment_error: Optional[str]
        endpoint: Optional[str]
        extended_properties: Optional[dict[str, Any]]
        identity: Optional[str]
        provisioning_state: Optional[Union[str, ConnectorProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_connector_type: Optional[str] = ..., 
                data_source: Optional[str] = ..., 
                endpoint: Optional[str] = ..., 
                extended_properties: Optional[dict[str, Any]] = ..., 
                identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpacePatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[AgentSpacePatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[AgentSpacePatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpacePatchProperties(_Model):
        description: Optional[str]
        max_agent_count: Optional[int]
        policies: Optional[AgentSpacePoliciesPatch]
        service_tree_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                max_agent_count: Optional[int] = ..., 
                policies: Optional[AgentSpacePoliciesPatch] = ..., 
                service_tree_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpacePolicies(_Model):
        geneva_actions_configuration: Optional[GenevaActionsPolicy]

        @overload
        def __init__(
                self, 
                *, 
                geneva_actions_configuration: Optional[GenevaActionsPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpacePoliciesPatch(_Model):
        geneva_actions_configuration: Optional[GenevaActionsPolicyPatch]

        @overload
        def __init__(
                self, 
                *, 
                geneva_actions_configuration: Optional[GenevaActionsPolicyPatch] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpaceProperties(_Model):
        compliance_status: Optional[AgentSpaceComplianceStatus]
        current_agent_count: Optional[int]
        description: Optional[str]
        last_policy_propagation: Optional[datetime]
        max_agent_count: Optional[int]
        member_agents: Optional[list[str]]
        policies: Optional[AgentSpacePolicies]
        provisioning_state: Optional[Union[str, AgentSpaceProvisioningState]]
        service_tree_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                max_agent_count: Optional[int] = ..., 
                policies: Optional[AgentSpacePolicies] = ..., 
                service_tree_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.AgentSpaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appservicesreagent.models.ApplicationInsightsConfiguration(_Model):
        app_id: Optional[str]
        connection_string: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                connection_string: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.ConnectorProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.appservicesreagent.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.appservicesreagent.models.DefaultModel(_Model):
        name: Optional[str]
        provider: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                provider: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.appservicesreagent.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.appservicesreagent.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.GenevaActionAuthenticationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        O_AUTH = "OAuth"
        WS_TRUST = "WS-Trust"


    class azure.mgmt.appservicesreagent.models.GenevaActionConfig(_Model):
        action_name: Optional[str]
        action_parameters: Optional[list[GenevaActionParameter]]
        approval_required: Optional[bool]
        extension: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_name: Optional[str] = ..., 
                action_parameters: Optional[list[GenevaActionParameter]] = ..., 
                approval_required: Optional[bool] = ..., 
                extension: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.GenevaActionParameter(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.GenevaActionsPolicy(_Model):
        acis_endpoint: Optional[str]
        allowed_actions: Optional[list[GenevaActionConfig]]
        authentication_mode: Optional[Union[str, GenevaActionAuthenticationMode]]
        certificate_subject_alternative_name: Optional[str]
        certificate_subject_name: Optional[str]
        client_id: Optional[str]
        extension_name: str

        @overload
        def __init__(
                self, 
                *, 
                acis_endpoint: Optional[str] = ..., 
                allowed_actions: Optional[list[GenevaActionConfig]] = ..., 
                authentication_mode: Optional[Union[str, GenevaActionAuthenticationMode]] = ..., 
                certificate_subject_name: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                extension_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.GenevaActionsPolicyPatch(_Model):
        acis_endpoint: Optional[str]
        allowed_actions: Optional[list[GenevaActionConfig]]
        authentication_mode: Optional[Union[str, GenevaActionAuthenticationMode]]
        certificate_subject_name: Optional[str]
        client_id: Optional[str]
        extension_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                acis_endpoint: Optional[str] = ..., 
                allowed_actions: Optional[list[GenevaActionConfig]] = ..., 
                authentication_mode: Optional[Union[str, GenevaActionAuthenticationMode]] = ..., 
                certificate_subject_name: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                extension_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.IncidentManagementConfiguration(_Model):
        connection_key: Optional[str]
        connection_name: Optional[str]
        connection_url: Optional[str]
        obo_user: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                connection_key: Optional[str] = ..., 
                connection_name: Optional[str] = ..., 
                connection_url: Optional[str] = ..., 
                obo_user: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.KnowledgeGraphConfiguration(_Model):
        identity: Optional[str]
        managed_resources: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[str] = ..., 
                managed_resources: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.LogConfiguration(_Model):
        application_insights_configuration: Optional[ApplicationInsightsConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                application_insights_configuration: Optional[ApplicationInsightsConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.appservicesreagent.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.appservicesreagent.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.appservicesreagent.models.SupportedAgentModel(ProxyResource):
        id: str
        name: str
        properties: Optional[SupportedAgentModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SupportedAgentModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.SupportedAgentModelProperties(_Model):
        default: bool
        model: str
        model_display_name: Optional[str]
        multiplier: Optional[str]
        provider: str
        provider_display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default: bool, 
                model: str, 
                model_display_name: Optional[str] = ..., 
                multiplier: Optional[str] = ..., 
                provider: str, 
                provider_display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appservicesreagent.models.UpgradeChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.appservicesreagent.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.appservicesreagent.operations

    class azure.mgmt.appservicesreagent.operations.AgentSpacesConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: AgentSpaceConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpaceConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: AgentSpaceConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpaceConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpaceConnector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnector: ...

        @distributed_trace
        def list_all_secrets(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnectorCollection: ...

        @distributed_trace
        def list_by_agent_space(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentSpaceConnector]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentSpaceConnector: ...


    class azure.mgmt.appservicesreagent.operations.AgentSpacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: AgentSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: AgentSpace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: AgentSpacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: AgentSpacePatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentSpace]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_space_name: str, 
                **kwargs: Any
            ) -> AgentSpace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentSpace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AgentSpace]: ...


    class azure.mgmt.appservicesreagent.operations.AgentsConnectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: AgentConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: AgentConnector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentConnector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentConnector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentConnector: ...

        @distributed_trace
        def list_by_agent(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AgentConnector]: ...

        @distributed_trace
        def list_secrets(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                connector_name: str, 
                **kwargs: Any
            ) -> AgentConnector: ...

        @distributed_trace
        def list_with_secrets_by_agent(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> AgentConnectorCollection: ...


    class azure.mgmt.appservicesreagent.operations.AgentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: Agent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: AgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: AgentPatch, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Agent]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                agent_name: str, 
                **kwargs: Any
            ) -> Agent: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Agent]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Agent]: ...


    class azure.mgmt.appservicesreagent.operations.SupportedAgentModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[SupportedAgentModel]: ...


namespace azure.mgmt.appservicesreagent.types

    class azure.mgmt.appservicesreagent.types.ActionConfiguration(TypedDict, total=False):
        key "accessLevel": Union[str, AgentAccessLevel]
        key "identity": str
        key "mode": Union[str, AgentMode]
        accessLevel: Union[str, AgentAccessLevel]
        identity: str
        mode: Union[str, AgentMode]


    class azure.mgmt.appservicesreagent.types.Agent(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AgentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AgentProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appservicesreagent.types.AgentConnector(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AgentConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgentConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appservicesreagent.types.AgentConnectorProperties(TypedDict, total=False):
        key "dataConnectorType": str
        key "dataSource": str
        key "deploymentError": str
        key "endpoint": str
        key "identity": str
        key "provisioningState": Union[str, ConnectorProvisioningState]
        key "source": str
        dataConnectorType: str
        dataSource: str
        deploymentError: str
        endpoint: str
        extendedProperties: dict[str, Any]
        identity: str
        provisioningState: Union[str, ConnectorProvisioningState]
        source: str


    class azure.mgmt.appservicesreagent.types.AgentIdentity(TypedDict, total=False):
        key "clientId": str
        key "enabled": bool
        key "initialSponsorGroupId": Required[str]
        clientId: str
        enabled: bool
        initialSponsorGroupId: str


    class azure.mgmt.appservicesreagent.types.AgentIdentityPatch(TypedDict, total=False):
        key "initialSponsorGroupId": str
        initialSponsorGroupId: str


    class azure.mgmt.appservicesreagent.types.AgentPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('AgentPatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: AgentPatchProperties
        tags: dict[str, str]


    class azure.mgmt.appservicesreagent.types.AgentPatchProperties(TypedDict, total=False):
        key "actionConfiguration": ForwardRef('ActionConfiguration', module='types')
        key "agentIdentity": ForwardRef('AgentIdentityPatch', module='types')
        key "agentSpaceId": str
        key "defaultModel": ForwardRef('DefaultModel', module='types')
        key "incidentManagementConfiguration": ForwardRef('IncidentManagementConfiguration', module='types')
        key "knowledgeGraphConfiguration": ForwardRef('KnowledgeGraphConfiguration', module='types')
        key "logConfiguration": ForwardRef('LogConfiguration', module='types')
        key "upgradeChannel": Union[str, UpgradeChannel]
        actionConfiguration: ActionConfiguration
        agentIdentity: AgentIdentityPatch
        agentSpaceId: str
        defaultModel: DefaultModel
        incidentManagementConfiguration: IncidentManagementConfiguration
        knowledgeGraphConfiguration: KnowledgeGraphConfiguration
        logConfiguration: LogConfiguration
        upgradeChannel: Union[str, UpgradeChannel]


    class azure.mgmt.appservicesreagent.types.AgentProperties(TypedDict, total=False):
        key "actionConfiguration": ForwardRef('ActionConfiguration', module='types')
        key "agentEndpoint": str
        key "agentIdentity": ForwardRef('AgentIdentity', module='types')
        key "agentSpaceId": str
        key "defaultModel": ForwardRef('DefaultModel', module='types')
        key "incidentManagementConfiguration": ForwardRef('IncidentManagementConfiguration', module='types')
        key "knowledgeGraphConfiguration": ForwardRef('KnowledgeGraphConfiguration', module='types')
        key "logConfiguration": ForwardRef('LogConfiguration', module='types')
        key "powerState": Union[str, AgentPowerState]
        key "provisioningState": Union[str, AgentProvisioningState]
        key "runningState": str
        key "upgradeChannel": Union[str, UpgradeChannel]
        actionConfiguration: ActionConfiguration
        agentEndpoint: str
        agentIdentity: AgentIdentity
        agentSpaceId: str
        defaultModel: DefaultModel
        incidentManagementConfiguration: IncidentManagementConfiguration
        knowledgeGraphConfiguration: KnowledgeGraphConfiguration
        logConfiguration: LogConfiguration
        powerState: Union[str, AgentPowerState]
        provisioningState: Union[str, AgentProvisioningState]
        runningState: str
        upgradeChannel: Union[str, UpgradeChannel]


    class azure.mgmt.appservicesreagent.types.AgentSpace(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AgentSpaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AgentSpaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appservicesreagent.types.AgentSpaceComplianceStatus(TypedDict, total=False):
        key "isCompliant": Required[bool]
        key "lastComplianceCheck": str
        complianceIssues: list[str]
        isCompliant: bool
        lastComplianceCheck: str


    class azure.mgmt.appservicesreagent.types.AgentSpaceConnector(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AgentSpaceConnectorProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgentSpaceConnectorProperties
        systemData: SystemData
        type: str


    class azure.mgmt.appservicesreagent.types.AgentSpaceConnectorProperties(TypedDict, total=False):
        key "dataConnectorType": str
        key "dataSource": str
        key "deploymentError": str
        key "endpoint": str
        key "identity": str
        key "provisioningState": Union[str, ConnectorProvisioningState]
        dataConnectorType: str
        dataSource: str
        deploymentError: str
        endpoint: str
        extendedProperties: dict[str, Any]
        identity: str
        provisioningState: Union[str, ConnectorProvisioningState]


    class azure.mgmt.appservicesreagent.types.AgentSpacePatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('AgentSpacePatchProperties', module='types')
        identity: ManagedServiceIdentity
        properties: AgentSpacePatchProperties
        tags: dict[str, str]


    class azure.mgmt.appservicesreagent.types.AgentSpacePatchProperties(TypedDict, total=False):
        key "description": str
        key "maxAgentCount": int
        key "policies": ForwardRef('AgentSpacePoliciesPatch', module='types')
        key "serviceTreeId": str
        description: str
        maxAgentCount: int
        policies: AgentSpacePoliciesPatch
        serviceTreeId: str


    class azure.mgmt.appservicesreagent.types.AgentSpacePolicies(TypedDict, total=False):
        key "genevaActionsConfiguration": ForwardRef('GenevaActionsPolicy', module='types')
        genevaActionsConfiguration: GenevaActionsPolicy


    class azure.mgmt.appservicesreagent.types.AgentSpacePoliciesPatch(TypedDict, total=False):
        key "genevaActionsConfiguration": ForwardRef('GenevaActionsPolicyPatch', module='types')
        genevaActionsConfiguration: GenevaActionsPolicyPatch


    class azure.mgmt.appservicesreagent.types.AgentSpaceProperties(TypedDict, total=False):
        key "complianceStatus": ForwardRef('AgentSpaceComplianceStatus', module='types')
        key "currentAgentCount": int
        key "description": str
        key "lastPolicyPropagation": str
        key "maxAgentCount": int
        key "policies": ForwardRef('AgentSpacePolicies', module='types')
        key "provisioningState": Union[str, AgentSpaceProvisioningState]
        key "serviceTreeId": str
        complianceStatus: AgentSpaceComplianceStatus
        currentAgentCount: int
        description: str
        lastPolicyPropagation: str
        maxAgentCount: int
        memberAgents: list[str]
        policies: AgentSpacePolicies
        provisioningState: Union[str, AgentSpaceProvisioningState]
        serviceTreeId: str


    class azure.mgmt.appservicesreagent.types.ApplicationInsightsConfiguration(TypedDict, total=False):
        key "appId": str
        key "connectionString": str
        appId: str
        connectionString: str


    class azure.mgmt.appservicesreagent.types.DefaultModel(TypedDict, total=False):
        key "name": str
        key "provider": str
        name: str
        provider: str


    class azure.mgmt.appservicesreagent.types.GenevaActionConfig(TypedDict, total=False):
        key "actionName": str
        key "approvalRequired": bool
        key "extension": str
        actionName: str
        actionParameters: list[GenevaActionParameter]
        approvalRequired: bool
        extension: str


    class azure.mgmt.appservicesreagent.types.GenevaActionParameter(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.appservicesreagent.types.GenevaActionsPolicy(TypedDict, total=False):
        key "acisEndpoint": str
        key "authenticationMode": Union[str, GenevaActionAuthenticationMode]
        key "certificateSubjectAlternativeName": str
        key "certificateSubjectName": str
        key "clientId": str
        key "extensionName": Required[str]
        acisEndpoint: str
        allowedActions: list[GenevaActionConfig]
        authenticationMode: Union[str, GenevaActionAuthenticationMode]
        certificateSubjectAlternativeName: str
        certificateSubjectName: str
        clientId: str
        extensionName: str


    class azure.mgmt.appservicesreagent.types.GenevaActionsPolicyPatch(TypedDict, total=False):
        key "acisEndpoint": str
        key "authenticationMode": Union[str, GenevaActionAuthenticationMode]
        key "certificateSubjectName": str
        key "clientId": str
        key "extensionName": str
        acisEndpoint: str
        allowedActions: list[GenevaActionConfig]
        authenticationMode: Union[str, GenevaActionAuthenticationMode]
        certificateSubjectName: str
        clientId: str
        extensionName: str


    class azure.mgmt.appservicesreagent.types.IncidentManagementConfiguration(TypedDict, total=False):
        key "connectionKey": str
        key "connectionName": str
        key "connectionUrl": str
        key "oboUser": str
        key "type": str
        connectionKey: str
        connectionName: str
        connectionUrl: str
        oboUser: str
        type: str


    class azure.mgmt.appservicesreagent.types.KnowledgeGraphConfiguration(TypedDict, total=False):
        key "identity": str
        identity: str
        managedResources: list[str]


    class azure.mgmt.appservicesreagent.types.LogConfiguration(TypedDict, total=False):
        key "applicationInsightsConfiguration": ForwardRef('ApplicationInsightsConfiguration', module='types')
        applicationInsightsConfiguration: ApplicationInsightsConfiguration


    class azure.mgmt.appservicesreagent.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.appservicesreagent.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appservicesreagent.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appservicesreagent.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.appservicesreagent.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appservicesreagent.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```