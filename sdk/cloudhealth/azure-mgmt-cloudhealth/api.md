```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.cloudhealth

    class azure.mgmt.cloudhealth.CloudHealthMgmtClient: implements ContextManager 
        authentication_settings: AuthenticationSettingsOperations
        discovery_rules: DiscoveryRulesOperations
        entities: EntitiesOperations
        health_models: HealthModelsOperations
        operations: Operations
        relationships: RelationshipsOperations
        signal_definitions: SignalDefinitionsOperations

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


namespace azure.mgmt.cloudhealth.aio

    class azure.mgmt.cloudhealth.aio.CloudHealthMgmtClient: implements AsyncContextManager 
        authentication_settings: AuthenticationSettingsOperations
        discovery_rules: DiscoveryRulesOperations
        entities: EntitiesOperations
        health_models: HealthModelsOperations
        operations: Operations
        relationships: RelationshipsOperations
        signal_definitions: SignalDefinitionsOperations

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


namespace azure.mgmt.cloudhealth.aio.operations

    class azure.mgmt.cloudhealth.aio.operations.AuthenticationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: AuthenticationSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthenticationSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthenticationSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthenticationSetting]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'authentication_setting_name']}, api_versions_list=['2026-01-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                **kwargs: Any
            ) -> AuthenticationSetting: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthenticationSetting]: ...


    class azure.mgmt.cloudhealth.aio.operations.DiscoveryRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: DiscoveryRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoveryRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoveryRule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoveryRule]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'discovery_rule_name']}, api_versions_list=['2026-01-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                **kwargs: Any
            ) -> DiscoveryRule: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DiscoveryRule]: ...


    class azure.mgmt.cloudhealth.aio.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: Entity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Entity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Entity]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Entity]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'entity_name']}, api_versions_list=['2026-01-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                **kwargs: Any
            ) -> Entity: ...

        @overload
        async def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: EntityHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        async def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        async def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        async def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: SignalHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        async def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        async def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        async def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: HealthReportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Entity]: ...


    class azure.mgmt.cloudhealth.aio.operations.HealthModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: HealthModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: HealthModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthModel]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> HealthModel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HealthModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[HealthModel]: ...


    class azure.mgmt.cloudhealth.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.cloudhealth.aio.operations.RelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: Relationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Relationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Relationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Relationship]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'relationship_name']}, api_versions_list=['2026-01-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                **kwargs: Any
            ) -> Relationship: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Relationship]: ...


    class azure.mgmt.cloudhealth.aio.operations.SignalDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: SignalDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SignalDefinition]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'signal_definition_name']}, api_versions_list=['2026-01-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                **kwargs: Any
            ) -> SignalDefinition: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SignalDefinition]: ...


namespace azure.mgmt.cloudhealth.models

    class azure.mgmt.cloudhealth.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.cloudhealth.models.AlertConfiguration(_Model):
        action_group_ids: Optional[list[str]]
        description: Optional[str]
        severity: Union[str, AlertSeverity]

        @overload
        def __init__(
                self, 
                *, 
                action_group_ids: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                severity: Union[str, AlertSeverity]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AlertSeverity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SEV0 = "Sev0"
        SEV1 = "Sev1"
        SEV2 = "Sev2"
        SEV3 = "Sev3"
        SEV4 = "Sev4"


    class azure.mgmt.cloudhealth.models.ApplicationInsightsTopologySpecification(DiscoveryRuleSpecification, discriminator='ApplicationInsightsTopology'):
        application_insights_resource_id: str
        kind: Literal[DiscoveryRuleKind.APPLICATION_INSIGHTS_TOPOLOGY]

        @overload
        def __init__(
                self, 
                *, 
                application_insights_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AuthenticationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "ManagedIdentity"


    class azure.mgmt.cloudhealth.models.AuthenticationSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[AuthenticationSettingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AuthenticationSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AuthenticationSettingProperties(_Model):
        authentication_kind: str
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_kind: str, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AzureMonitorWorkspaceSignals(_Model):
        authentication_setting: str
        azure_monitor_workspace_resource_id: str
        signals: Optional[list[PrometheusMetricsSignal]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_setting: str, 
                azure_monitor_workspace_resource_id: str, 
                signals: Optional[list[PrometheusMetricsSignal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AzureResourceSignal(SignalInstanceProperties, discriminator='AzureResourceMetric'):
        aggregation_type: Optional[Union[str, MetricAggregationType]]
        data_unit: Optional[str]
        dimension: Optional[str]
        dimension_filter: Optional[str]
        display_name: Optional[str]
        evaluation_rules: Optional[EvaluationRule]
        metric_name: Optional[str]
        metric_namespace: Optional[str]
        name: str
        refresh_interval: Optional[Union[str, RefreshInterval]]
        signal_definition_name: str
        signal_kind: Literal[SignalKind.AZURE_RESOURCE_METRIC]
        status: SignalStatus
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[Union[str, MetricAggregationType]] = ..., 
                data_unit: Optional[str] = ..., 
                dimension: Optional[str] = ..., 
                dimension_filter: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: Optional[EvaluationRule] = ..., 
                metric_name: Optional[str] = ..., 
                metric_namespace: Optional[str] = ..., 
                name: str, 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                signal_definition_name: Optional[str] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.AzureResourceSignals(_Model):
        authentication_setting: str
        azure_resource_id: str
        azure_resource_kind: Optional[str]
        signals: Optional[list[AzureResourceSignal]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_setting: str, 
                azure_resource_id: str, 
                azure_resource_kind: Optional[str] = ..., 
                signals: Optional[list[AzureResourceSignal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cloudhealth.models.DependenciesAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAX_NOT_HEALTHY = "MaxNotHealthy"
        MIN_HEALTHY = "MinHealthy"
        WORST_OF = "WorstOf"


    class azure.mgmt.cloudhealth.models.DependenciesAggregationUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABSOLUTE = "Absolute"
        PERCENTAGE = "Percentage"


    class azure.mgmt.cloudhealth.models.DependenciesSignalGroupV2(_Model):
        aggregation_type: Union[str, DependenciesAggregationType]
        degraded_threshold: Optional[float]
        ignore_unknown: Optional[bool]
        unhealthy_threshold: Optional[float]
        unit: Optional[Union[str, DependenciesAggregationUnit]]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Union[str, DependenciesAggregationType], 
                degraded_threshold: Optional[float] = ..., 
                ignore_unknown: Optional[bool] = ..., 
                unhealthy_threshold: Optional[float] = ..., 
                unit: Optional[Union[str, DependenciesAggregationUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.DiscoveryError(_Model):
        context: Optional[list[str]]
        message: str


    class azure.mgmt.cloudhealth.models.DiscoveryRule(ProxyResource):
        id: str
        name: str
        properties: Optional[DiscoveryRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DiscoveryRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.DiscoveryRuleKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_INSIGHTS_TOPOLOGY = "ApplicationInsightsTopology"
        RESOURCE_GRAPH_QUERY = "ResourceGraphQuery"


    class azure.mgmt.cloudhealth.models.DiscoveryRuleProperties(_Model):
        add_recommended_signals: Union[str, DiscoveryRuleRecommendedSignalsBehavior]
        authentication_setting: str
        discover_relationships: Union[str, DiscoveryRuleRelationshipDiscoveryBehavior]
        display_name: Optional[str]
        entity_name: str
        error: Optional[DiscoveryError]
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]
        specification: DiscoveryRuleSpecification

        @overload
        def __init__(
                self, 
                *, 
                add_recommended_signals: Union[str, DiscoveryRuleRecommendedSignalsBehavior], 
                authentication_setting: str, 
                discover_relationships: Union[str, DiscoveryRuleRelationshipDiscoveryBehavior], 
                display_name: Optional[str] = ..., 
                specification: DiscoveryRuleSpecification
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.DiscoveryRuleRecommendedSignalsBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cloudhealth.models.DiscoveryRuleRelationshipDiscoveryBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cloudhealth.models.DiscoveryRuleSpecification(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.Entity(ProxyResource):
        id: str
        name: str
        properties: Optional[EntityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EntityAlerts(_Model):
        degraded: Optional[AlertConfiguration]
        unhealthy: Optional[AlertConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                degraded: Optional[AlertConfiguration] = ..., 
                unhealthy: Optional[AlertConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EntityCoordinates(_Model):
        x: float
        y: float

        @overload
        def __init__(
                self, 
                *, 
                x: float, 
                y: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EntityHistoryRequest(_Model):
        end_at: Optional[datetime]
        start_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_at: Optional[datetime] = ..., 
                start_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EntityHistoryResponse(_Model):
        entity_name: str
        history: list[HealthStateTransition]

        @overload
        def __init__(
                self, 
                *, 
                entity_name: str, 
                history: list[HealthStateTransition]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EntityImpact(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIMITED = "Limited"
        STANDARD = "Standard"
        SUPPRESSED = "Suppressed"


    class azure.mgmt.cloudhealth.models.EntityProperties(_Model):
        alerts: Optional[EntityAlerts]
        canvas_position: Optional[EntityCoordinates]
        discovered_by: Optional[str]
        display_name: Optional[str]
        health_objective: Optional[float]
        health_state: Optional[Union[str, HealthState]]
        icon: Optional[IconDefinition]
        impact: Optional[Union[str, EntityImpact]]
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]
        signal_groups: Optional[SignalGroups]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                alerts: Optional[EntityAlerts] = ..., 
                canvas_position: Optional[EntityCoordinates] = ..., 
                display_name: Optional[str] = ..., 
                health_objective: Optional[float] = ..., 
                icon: Optional[IconDefinition] = ..., 
                impact: Optional[Union[str, EntityImpact]] = ..., 
                signal_groups: Optional[SignalGroups] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.cloudhealth.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.cloudhealth.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.EvaluationRule(_Model):
        degraded_rule: Optional[ThresholdRuleV2]
        unhealthy_rule: ThresholdRuleV2

        @overload
        def __init__(
                self, 
                *, 
                degraded_rule: Optional[ThresholdRuleV2] = ..., 
                unhealthy_rule: ThresholdRuleV2
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ExternalSignal(SignalInstanceProperties, discriminator='External'):
        evaluation_rules: Optional[EvaluationRule]
        name: str
        signal_definition_name: str
        signal_kind: Literal[SignalKind.EXTERNAL_SIGNAL]
        status: SignalStatus

        @overload
        def __init__(
                self, 
                *, 
                evaluation_rules: Optional[EvaluationRule] = ..., 
                name: str, 
                signal_definition_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ExternalSignalGroup(_Model):
        signals: Optional[list[ExternalSignal]]


    class azure.mgmt.cloudhealth.models.HealthModel(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[HealthModelProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[HealthModelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.HealthModelProperties(_Model):
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]


    class azure.mgmt.cloudhealth.models.HealthModelProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cloudhealth.models.HealthModelUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.HealthReportEvaluationRule(_Model):
        degraded_rule: Optional[ThresholdRuleV2]
        unhealthy_rule: ThresholdRuleV2

        @overload
        def __init__(
                self, 
                *, 
                degraded_rule: Optional[ThresholdRuleV2] = ..., 
                unhealthy_rule: ThresholdRuleV2
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.HealthReportRequest(_Model):
        additional_context: Optional[str]
        evaluation_rules: Optional[HealthReportEvaluationRule]
        expires_in_minutes: Optional[int]
        health_state: Union[str, HealthState]
        signal_name: str
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                additional_context: Optional[str] = ..., 
                evaluation_rules: Optional[HealthReportEvaluationRule] = ..., 
                expires_in_minutes: Optional[int] = ..., 
                health_state: Union[str, HealthState], 
                signal_name: str, 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.HealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DELETED = "Deleted"
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.cloudhealth.models.HealthStateTransition(_Model):
        new_state: Union[str, HealthState]
        occurred_at: datetime
        previous_state: Union[str, HealthState]
        reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                new_state: Union[str, HealthState], 
                occurred_at: datetime, 
                previous_state: Union[str, HealthState], 
                reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.IconDefinition(_Model):
        custom_data: Optional[str]
        icon_name: str

        @overload
        def __init__(
                self, 
                *, 
                custom_data: Optional[str] = ..., 
                icon_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.LogAnalyticsQuerySignalDefinitionProperties(SignalDefinitionProperties, discriminator='LogAnalyticsQuery'):
        data_unit: str
        display_name: str
        evaluation_rules: EvaluationRule
        provisioning_state: Union[str, HealthModelProvisioningState]
        query_text: str
        refresh_interval: Union[str, RefreshInterval]
        signal_kind: Literal[SignalKind.LOG_ANALYTICS_QUERY]
        tags: dict[str, str]
        time_grain: Optional[str]
        value_column_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_unit: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: EvaluationRule, 
                query_text: str, 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                time_grain: Optional[str] = ..., 
                value_column_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.LogAnalyticsSignal(SignalInstanceProperties, discriminator='LogAnalyticsQuery'):
        data_unit: Optional[str]
        display_name: Optional[str]
        evaluation_rules: Optional[EvaluationRule]
        name: str
        query_text: Optional[str]
        refresh_interval: Optional[Union[str, RefreshInterval]]
        signal_definition_name: str
        signal_kind: Literal[SignalKind.LOG_ANALYTICS_QUERY]
        status: SignalStatus
        time_grain: Optional[str]
        value_column_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_unit: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: Optional[EvaluationRule] = ..., 
                name: str, 
                query_text: Optional[str] = ..., 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                signal_definition_name: Optional[str] = ..., 
                time_grain: Optional[str] = ..., 
                value_column_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.LogAnalyticsSignals(_Model):
        authentication_setting: str
        log_analytics_workspace_resource_id: str
        signals: Optional[list[LogAnalyticsSignal]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_setting: str, 
                log_analytics_workspace_resource_id: str, 
                signals: Optional[list[LogAnalyticsSignal]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ManagedIdentityAuthenticationSettingProperties(AuthenticationSettingProperties, discriminator='ManagedIdentity'):
        authentication_kind: Literal[AuthenticationKind.MANAGED_IDENTITY]
        display_name: str
        managed_identity_name: str
        provisioning_state: Union[str, HealthModelProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                managed_identity_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.cloudhealth.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cloudhealth.models.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.mgmt.cloudhealth.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.cloudhealth.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.cloudhealth.models.PrometheusMetricsSignal(SignalInstanceProperties, discriminator='PrometheusMetricsQuery'):
        data_unit: Optional[str]
        display_name: Optional[str]
        evaluation_rules: Optional[EvaluationRule]
        name: str
        query_text: Optional[str]
        refresh_interval: Optional[Union[str, RefreshInterval]]
        signal_definition_name: str
        signal_kind: Literal[SignalKind.PROMETHEUS_METRICS_QUERY]
        status: SignalStatus
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_unit: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: Optional[EvaluationRule] = ..., 
                name: str, 
                query_text: Optional[str] = ..., 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                signal_definition_name: Optional[str] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.PrometheusMetricsSignalDefinitionProperties(SignalDefinitionProperties, discriminator='PrometheusMetricsQuery'):
        data_unit: str
        display_name: str
        evaluation_rules: EvaluationRule
        provisioning_state: Union[str, HealthModelProvisioningState]
        query_text: str
        refresh_interval: Union[str, RefreshInterval]
        signal_kind: Literal[SignalKind.PROMETHEUS_METRICS_QUERY]
        tags: dict[str, str]
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_unit: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: EvaluationRule, 
                query_text: str, 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cloudhealth.models.RefreshInterval(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PT10M = "PT10M"
        PT1H = "PT1H"
        PT1M = "PT1M"
        PT2H = "PT2H"
        PT30M = "PT30M"
        PT5M = "PT5M"


    class azure.mgmt.cloudhealth.models.Relationship(ProxyResource):
        id: str
        name: str
        properties: Optional[RelationshipProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RelationshipProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.RelationshipProperties(_Model):
        child_entity_name: str
        discovered_by: Optional[str]
        display_name: Optional[str]
        parent_entity_name: str
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                child_entity_name: str, 
                display_name: Optional[str] = ..., 
                parent_entity_name: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.cloudhealth.models.ResourceGraphQuerySpecification(DiscoveryRuleSpecification, discriminator='ResourceGraphQuery'):
        kind: Literal[DiscoveryRuleKind.RESOURCE_GRAPH_QUERY]
        resource_graph_query: str

        @overload
        def __init__(
                self, 
                *, 
                resource_graph_query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.ResourceMetricSignalDefinitionProperties(SignalDefinitionProperties, discriminator='AzureResourceMetric'):
        aggregation_type: Union[str, MetricAggregationType]
        data_unit: str
        dimension: Optional[str]
        dimension_filter: Optional[str]
        display_name: str
        evaluation_rules: EvaluationRule
        metric_name: str
        metric_namespace: str
        provisioning_state: Union[str, HealthModelProvisioningState]
        refresh_interval: Union[str, RefreshInterval]
        signal_kind: Literal[SignalKind.AZURE_RESOURCE_METRIC]
        tags: dict[str, str]
        time_grain: str

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Union[str, MetricAggregationType], 
                data_unit: Optional[str] = ..., 
                dimension: Optional[str] = ..., 
                dimension_filter: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: EvaluationRule, 
                metric_name: str, 
                metric_namespace: str, 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                time_grain: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[SignalDefinitionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SignalDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalDefinitionProperties(_Model):
        data_unit: Optional[str]
        display_name: Optional[str]
        evaluation_rules: EvaluationRule
        provisioning_state: Optional[Union[str, HealthModelProvisioningState]]
        refresh_interval: Optional[Union[str, RefreshInterval]]
        signal_kind: str
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                data_unit: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                evaluation_rules: EvaluationRule, 
                refresh_interval: Optional[Union[str, RefreshInterval]] = ..., 
                signal_kind: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalGroups(_Model):
        azure_log_analytics: Optional[LogAnalyticsSignals]
        azure_monitor_workspace: Optional[AzureMonitorWorkspaceSignals]
        azure_resource: Optional[AzureResourceSignals]
        dependencies: Optional[DependenciesSignalGroupV2]
        external: Optional[ExternalSignalGroup]

        @overload
        def __init__(
                self, 
                *, 
                azure_log_analytics: Optional[LogAnalyticsSignals] = ..., 
                azure_monitor_workspace: Optional[AzureMonitorWorkspaceSignals] = ..., 
                azure_resource: Optional[AzureResourceSignals] = ..., 
                dependencies: Optional[DependenciesSignalGroupV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalHistoryDataPoint(_Model):
        additional_context: Optional[str]
        health_state: Union[str, HealthState]
        occurred_at: datetime
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                additional_context: Optional[str] = ..., 
                health_state: Union[str, HealthState], 
                occurred_at: datetime, 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalHistoryRequest(_Model):
        end_at: Optional[datetime]
        signal_name: str
        start_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_at: Optional[datetime] = ..., 
                signal_name: str, 
                start_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalHistoryResponse(_Model):
        entity_name: str
        history: list[SignalHistoryDataPoint]
        signal_name: str

        @overload
        def __init__(
                self, 
                *, 
                entity_name: str, 
                history: list[SignalHistoryDataPoint], 
                signal_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalInstanceProperties(_Model):
        name: str
        signal_definition_name: Optional[str]
        signal_kind: str
        status: Optional[SignalStatus]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                signal_definition_name: Optional[str] = ..., 
                signal_kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.SignalKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_RESOURCE_METRIC = "AzureResourceMetric"
        EXTERNAL_SIGNAL = "External"
        LOG_ANALYTICS_QUERY = "LogAnalyticsQuery"
        PROMETHEUS_METRICS_QUERY = "PrometheusMetricsQuery"


    class azure.mgmt.cloudhealth.models.SignalOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        NOT_EQUAL = "NotEqual"


    class azure.mgmt.cloudhealth.models.SignalStatus(_Model):
        error: Optional[str]
        health_state: Optional[Union[str, HealthState]]
        reported_at: Optional[datetime]
        value: Optional[float]


    class azure.mgmt.cloudhealth.models.SystemData(_Model):
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


    class azure.mgmt.cloudhealth.models.ThresholdRuleV2(_Model):
        operator: Union[str, SignalOperator]
        threshold: float

        @overload
        def __init__(
                self, 
                *, 
                operator: Union[str, SignalOperator], 
                threshold: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cloudhealth.models.TrackedResource(Resource):
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


    class azure.mgmt.cloudhealth.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.cloudhealth.operations

    class azure.mgmt.cloudhealth.operations.AuthenticationSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: AuthenticationSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthenticationSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthenticationSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthenticationSetting]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'authentication_setting_name']}, api_versions_list=['2026-01-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                authentication_setting_name: str, 
                **kwargs: Any
            ) -> AuthenticationSetting: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthenticationSetting]: ...


    class azure.mgmt.cloudhealth.operations.DiscoveryRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: DiscoveryRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoveryRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoveryRule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoveryRule]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'discovery_rule_name']}, api_versions_list=['2026-01-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                discovery_rule_name: str, 
                **kwargs: Any
            ) -> DiscoveryRule: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DiscoveryRule]: ...


    class azure.mgmt.cloudhealth.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: Entity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Entity]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Entity]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Entity]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'entity_name']}, api_versions_list=['2026-01-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                **kwargs: Any
            ) -> Entity: ...

        @overload
        def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: EntityHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        def get_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EntityHistoryResponse: ...

        @overload
        def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: SignalHistoryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        def get_signal_history(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SignalHistoryResponse: ...

        @overload
        def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: HealthReportRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def ingest_health_report(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                entity_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Entity]: ...


    class azure.mgmt.cloudhealth.operations.HealthModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: HealthModel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: HealthModelUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HealthModel]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                **kwargs: Any
            ) -> HealthModel: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HealthModel]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[HealthModel]: ...


    class azure.mgmt.cloudhealth.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.cloudhealth.operations.RelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: Relationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Relationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Relationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Relationship]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'relationship_name']}, api_versions_list=['2026-01-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                relationship_name: str, 
                **kwargs: Any
            ) -> Relationship: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Relationship]: ...


    class azure.mgmt.cloudhealth.operations.SignalDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: SignalDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SignalDefinition]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-01-preview', params_added_on={'2026-01-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'health_model_name', 'signal_definition_name']}, api_versions_list=['2026-01-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                signal_definition_name: str, 
                **kwargs: Any
            ) -> SignalDefinition: ...

        @distributed_trace
        def list_by_health_model(
                self, 
                resource_group_name: str, 
                health_model_name: str, 
                *, 
                timestamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SignalDefinition]: ...


```